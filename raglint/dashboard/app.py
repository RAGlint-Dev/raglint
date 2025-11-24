import csv
import io
import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    WebSocket,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from raglint.config import Config
from raglint.core import RAGPipelineAnalyzer
from raglint.dashboard.analytics import CohortAnalyzer, DriftDetector
from raglint.plugins.loader import PluginLoader, PluginRegistry

from . import auth, models, schemas
from .database import get_db, init_db

logger = logging.getLogger(__name__)

# Setup templates and static files paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Dependency to get user from cookie for UI
async def get_current_user_from_cookie(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    # Remove 'Bearer ' prefix if present (though usually just the token in cookie)
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    try:
        return await auth.get_current_user(token, db)
    except HTTPException:
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="RAGLint Dashboard",
    description="API for RAGLint Observability Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount documentation
DOCS_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../docs/_build/html"))
if os.path.exists(DOCS_DIR):
    app.mount("/docs", StaticFiles(directory=DOCS_DIR, html=True), name="docs")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple rate limiting for export endpoint
from collections import defaultdict
from datetime import datetime, timedelta

# Track export requests: {user_id: [timestamps]}
export_rate_limits = defaultdict(list)


def check_export_rate_limit(user_id: str, max_requests: int = 10, window_minutes: int = 5) -> bool:
    """Check if user has exceeded export rate limit."""
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=window_minutes)

    # Clean old requests
    export_rate_limits[user_id] = [ts for ts in export_rate_limits[user_id] if ts > cutoff]

    # Check limit
    if len(export_rate_limits[user_id]) >= max_requests:
        return False

    # Record this request
    export_rate_limits[user_id].append(now)
    return True


# --- Auth Routes ---


@app.post("/auth/register")
async def register(
    email: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select

    # Check existing
    result = await db.execute(select(models.User).where(models.User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_pw = auth.get_password_hash(password)
    user = models.User(email=email, hashed_password=hashed_pw)
    db.add(user)
    await db.commit()

    return RedirectResponse(url="/login?registered=true", status_code=303)


@app.post("/auth/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select

    # Find user
    result = await db.execute(select(models.User).where(models.User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token
    access_token = auth.create_access_token(data={"sub": user.email})

    # Return token (for API) or set cookie (for UI)
    # For simplicity, we'll assume this is called by UI form mostly, but return JSON standard
    response = {"access_token": access_token, "token_type": "bearer"}
    return response


@app.post("/auth/login-ui")
async def login_ui(
    email: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select

    # Find user
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalar_one_or_none()

    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html", {"request": {}, "error": "Invalid credentials"}, status_code=401
        )

    # Create token
    access_token = auth.create_access_token(data={"sub": user.email})

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/playground", response_class=HTMLResponse)
async def playground_page(
    request: Request, user: Optional[models.User] = Depends(get_current_user_from_cookie)
):
    """Render the playground page."""
    # Allow access without login for testing
    # if not user:
    #     return RedirectResponse(url="/login")

    # Get pre-fill data from query params
    prefill = {
        "query": request.query_params.get("query", ""),
        "response": request.query_params.get("response", ""),
        "contexts": request.query_params.get("contexts", ""),
    }

    return templates.TemplateResponse(
        "playground.html", {"request": request, "user": user, "prefill": prefill}
    )


@app.post("/playground/analyze", response_class=HTMLResponse)
async def playground_analyze(
    request: Request,
    query: str = Form(...),
    contexts: str = Form(...),
    response: str = Form(...),
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
):
    """Analyze a single item from the playground."""
    if not user:
        return "<div>Please login</div>"

    # Parse contexts (split by newline)
    context_list = [c.strip() for c in contexts.split("\n") if c.strip()]

    # Create a temporary analyzer instance (using mock or configured provider)
    # For playground, we want fast feedback, maybe use the configured one.
    from raglint.config import Config
    from raglint.core import RAGPipelineAnalyzer

    # Load config but force smart metrics if possible, or just basic
    # For this demo, let's assume we want to run the full suite including plugins
    cfg = Config.load().as_dict()
    RAGPipelineAnalyzer(use_smart_metrics=True, config=cfg)

    # Analyze single item
    item = {
        "query": query,
        "retrieved_contexts": context_list,
        "ground_truth_contexts": [],  # No GT in playground usually
        "response": response,
    }

    # Use async analysis for the single item
    # For real-time updates, we return a shell that triggers individual metric calculations
    return templates.TemplateResponse(
        "partials/playground_result_shell.html", {"request": request, "item": item}
    )


@app.post("/playground/generate", response_class=HTMLResponse)
async def playground_generate(
    request: Request,
    system_prompt: str = Form(...),
    user_prompt_template: str = Form(...),
    context: str = Form(""),
    query: str = Form(""),
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
):
    """Generate a response using the configured LLM."""
    if not user:
        return "<div>Please login</div>"

    # 1. Construct Prompt
    try:
        user_prompt = user_prompt_template.format(context=context, query=query)
    except KeyError as e:
        return f"<div class='text-red-500'>Error in prompt template: Missing variable {e}</div>"

    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    # 2. Generate Response
    from raglint.config import Config
    from raglint.llm import LLMFactory

    cfg = Config.load().as_dict()
    llm = LLMFactory.create(cfg)

    try:
        response_text = await llm.agenerate(full_prompt)
    except Exception as e:
        return f"<div class='text-red-500'>Generation failed: {e}</div>"

    # 3. Return Result Shell (same as analyze, but with generated response)
    item = {
        "query": query,
        "retrieved_contexts": [context] if context else [],
        "response": response_text,
        "ground_truth_contexts": [],
    }

    return templates.TemplateResponse(
        "partials/playground_result_shell.html",
        {"request": request, "item": item, "generated": True},
    )


@app.post("/playground/analyze/metric/{metric_name}", response_class=HTMLResponse)
async def playground_analyze_metric(
    request: Request,
    metric_name: str,
    query: str = Form(...),
    contexts: str = Form(...),
    response: str = Form(...),
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
):
    """Calculate a single metric."""
    if not user:
        return ""

    from raglint.config import Config
    from raglint.core import RAGPipelineAnalyzer

    cfg = Config.load().as_dict()
    # Initialize analyzer (this might be heavy to do per request, but for playground it's okay)
    # Optimization: Cache analyzer or use a lightweight version
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=cfg)

    context_list = [c.strip() for c in contexts.split("\n") if c.strip()]

    score = 0.0
    reasoning = ""

    try:
        if metric_name == "faithfulness":
            if analyzer.faithfulness_scorer and response:
                score, reasoning = await analyzer.faithfulness_scorer.ascore(
                    query, context_list, response
                )
        elif metric_name == "answer_relevance":
            if analyzer.answer_relevance_scorer and response:
                score, reasoning = await analyzer.answer_relevance_scorer.ascore(query, response)
        elif metric_name == "toxicity":
            if analyzer.toxicity_scorer and response:
                score, reasoning = await analyzer.toxicity_scorer.ascore(response)
        elif metric_name == "semantic":
            if analyzer.semantic_matcher and context_list:
                # Semantic usually needs ground truth, but here maybe we check coherence?
                # Or if we had GT. For now, let's skip or use coherence.
                pass
    except Exception as e:
        logger.error(f"Error calculating {metric_name}: {e}")

    return templates.TemplateResponse(
        "partials/metric_card.html",
        {
            "request": request,
            "name": metric_name.replace("_", " ").title(),
            "score": score,
            "reasoning": reasoning,
        },
    )


@app.get("/auth/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {"status": "healthy", "service": "raglint"}


@app.get("/runs/{run_id}/export")
async def export_run(
    run_id: str,
    format: str = "json",
    db: AsyncSession = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
):
    """Export run results as CSV or JSON."""
    if not user:
        return RedirectResponse(url="/login")

    # Rate limiting check
    if not check_export_rate_limit(str(user.id)):
        raise HTTPException(
            status_code=429,
            detail="Too many export requests. Please wait a few minutes and try again.",
        )

    from sqlalchemy import select

    # Get run
    result = await db.execute(select(models.AnalysisRun).where(models.AnalysisRun.id == run_id))
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Get items
    result = await db.execute(select(models.ResultItem).where(models.ResultItem.run_id == run_id))
    items = result.scalars().all()

    if format == "csv":
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "Query",
                "Response",
                "Retrieved Contexts",
                "Faithfulness",
                "Semantic Score",
                "Context Precision",
                "Context Recall",
            ]
        )

        # Data
        for item in items:
            writer.writerow(
                [
                    item.query or "",
                    item.response or "",
                    " | ".join(item.retrieved_contexts or []),
                    item.metrics.get("faithfulness_score", ""),
                    item.metrics.get("semantic_score", ""),
                    item.metrics.get("context_precision", ""),
                    item.metrics.get("context_recall", ""),
                ]
            )

        csv_content = output.getvalue()

        from fastapi.responses import StreamingResponse

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=raglint_run_{run_id[:8]}.csv"},
        )

    else:  # JSON format
        export_data = {
            "run_id": run.id,
            "timestamp": run.timestamp.isoformat() if run.timestamp else None,
            "config": run.config,
            "summary_metrics": run.metrics_summary,  # Changed from run.summary_metrics to run.metrics_summary
            "items": [
                {
                    "query": item.query,
                    "response": item.response,
                    "retrieved_contexts": item.retrieved_contexts,
                    "ground_truth_contexts": item.ground_truth_contexts,
                    "metrics": item.metrics,
                }
                for item in items
            ],
        }

        from fastapi.responses import JSONResponse

        return JSONResponse(
            content=export_data,
            headers={"Content-Disposition": f"attachment; filename=raglint_run_{run_id[:8]}.json"},
        )


# ============================================================================
# Dashboard Routes
# ============================================================================


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# --- Protected Routes ---


async def run_analysis_task(run_id: str, request: schemas.AnalyzeRequest, db: AsyncSession):
    """Background task to run analysis and save results."""
    try:
        # 1. Setup Config
        config_dict = request.config or {}
        # Ensure we have a valid config object, might need to load defaults
        # For now, we assume the core analyzer handles dict or we create a Config object
        # We'll mock the config loading for simplicity here or use Config.from_dict if available
        # But Config.load takes a path. Let's just pass the dict to Analyzer if it supported it,
        # or create a temporary config.

        # Actually RAGPipelineAnalyzer takes a Config object.
        # We need to instantiate it.
        # Use Config.from_dict for clean instantiation

        cfg = Config.from_dict(config_dict) if config_dict else Config()

        analyzer = RAGPipelineAnalyzer(cfg)

        # 2. Run Analysis
        # We need to adapt the input data format
        # request.data is List[Dict]
        results = await analyzer.analyze_async(request.data)

        # 3. Save Results to DB
        # We need a new session since the one passed might be closed?
        # BackgroundTasks runs after response, so we should manage session carefully.
        # Better to create a new session here.
        from .database import SessionLocal

        async with SessionLocal() as session:
            # Update Run status (if we had a status field)
            # Save items

            # Calculate summary metrics
            total_items = len(results)
            avg_faithfulness = (
                sum(r["metrics"]["faithfulness"] or 0 for r in results) / total_items
                if total_items
                else 0
            )
            # ... other metrics

            summary = {"faithfulness": avg_faithfulness, "total_items": total_items}

            # Update the run with summary
            stmt = (
                models.AnalysisRun.__table__.update()
                .where(models.AnalysisRun.id == run_id)
                .values(metrics_summary=summary, status="completed")
            )
            await session.execute(stmt)

            # Insert items
            for res in results:
                item = models.ResultItem(
                    run_id=run_id,
                    query=res["detailed"]["query"],
                    response=res["detailed"]["response"],
                    retrieved_contexts=res["chunks"],
                    ground_truth_contexts=res["detailed"].get("ground_truth_contexts"),
                    metrics=res["metrics"],
                )
                session.add(item)

            await session.commit()
            logger.info(f"Analysis {run_id} completed and saved.")

    except Exception as e:
        logger.error(f"Analysis {run_id} failed: {e}")
        # Update run status to FAILED
        from .database import SessionLocal

        async with SessionLocal() as session:
            stmt = (
                models.AnalysisRun.__table__.update()
                .where(models.AnalysisRun.id == run_id)
                .values(status="failed", error_message=str(e))
            )
            await session.execute(stmt)
            await session.commit()


@app.post("/analyze", response_model=schemas.AnalysisRun)
async def trigger_analysis(
    request: schemas.AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger a new analysis run."""
    import hashlib
    import json

    from sqlalchemy import select

    run_id = str(uuid.uuid4())

    # Calculate config hash
    config_json = json.dumps(request.config, sort_keys=True)
    config_hash = hashlib.sha256(config_json.encode()).hexdigest()

    # Find matching version
    result = await db.execute(
        select(models.PipelineVersion).where(models.PipelineVersion.hash == config_hash)
    )
    version = result.scalar_one_or_none()

    # Create initial run record
    new_run = models.AnalysisRun(
        id=run_id,
        config=request.config,
        metrics_summary={},  # Empty initially
        status="running",
        version_id=version.id if version else None,
    )
    db.add(new_run)
    await db.commit()
    await db.refresh(new_run)

    # Start background task
    # We pass the ID and request data.
    # Note: We don't pass 'db' session to background task as it closes after request.
    background_tasks.add_task(run_analysis_task, run_id, request, None)

    return new_run

    return new_run


@app.get("/runs", response_model=list[schemas.AnalysisRun])
async def list_runs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all analysis runs."""
    from sqlalchemy import select

    result = await db.execute(
        select(models.AnalysisRun)
        .order_by(models.AnalysisRun.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@app.get("/runs/{run_id}", response_model=schemas.AnalysisRun)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific analysis run."""
    from sqlalchemy import select

    result = await db.execute(select(models.AnalysisRun).where(models.AnalysisRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/runs/{run_id}/items", response_model=list[schemas.ResultItem])
async def get_run_items(run_id: str, db: AsyncSession = Depends(get_db)):
    """Get items for a specific run."""
    from sqlalchemy import select

    # Verify run exists first
    result = await db.execute(select(models.AnalysisRun).where(models.AnalysisRun.id == run_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Run not found")

    result = await db.execute(select(models.ResultItem).where(models.ResultItem.run_id == run_id))
    return result.scalars().all()

    return result.scalars().all()


@app.websocket("/ws/status/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await websocket.accept()
    try:
        while True:
            # Placeholder: In a real app, we would subscribe to a message queue
            # or poll the DB status. For now, just echo or wait.
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        # Log websocket errors instead of silently ignoring
        logger.warning(f"WebSocket error: {e}")


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Render the public landing page."""
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/docs", response_class=HTMLResponse)
async def docs_page(request: Request):
    """Render the documentation page."""
    return templates.TemplateResponse("docs.html", {"request": request})


@app.get("/license", response_class=HTMLResponse)
async def license_page(request: Request):
    """Render the license page."""
    return templates.TemplateResponse("license.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_home(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
):
    """Render the dashboard home page."""
    if not user:
        return RedirectResponse(url="/login?next=/dashboard")

    from sqlalchemy import select

    # Fetch recent runs (optionally filter by user)
    query = select(models.AnalysisRun).order_by(
        models.AnalysisRun.timestamp.asc()
    )  # Get all for chart, sorted by time
    if user:
        query = query.where(models.AnalysisRun.user_id == user.id)

    result = await db.execute(query)
    all_runs = result.scalars().all()

    # Prepare Chart Data
    dates = []
    faithfulness_scores = []
    relevance_scores = []

    for run in all_runs:
        if run.status == "completed":
            dates.append(run.timestamp.strftime("%Y-%m-%d %H:%M"))
            # Extract metrics safely
            metrics = run.summary_metrics or {}
            faithfulness_scores.append(metrics.get("avg_faithfulness", 0))
            # Assuming relevance is stored or we use retrieval precision as a proxy for now
            # In a real app, we'd have a specific relevance score.
            # Let's use retrieval precision as a proxy for "Relevance" in this demo chart.
            retrieval = metrics.get("retrieval_stats", {})
            relevance_scores.append(
                retrieval.get("precision", 0) if isinstance(retrieval, dict) else 0
            )

    # Recent runs for table (reverse order)
    runs = sorted(all_runs, key=lambda x: x.timestamp, reverse=True)[:20]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "runs": runs,
            "user": user,
            "dates": dates,
            "faithfulness_scores": faithfulness_scores,
            "relevance_scores": relevance_scores,
        },
    )


@app.get("/runs/{run_id}/ui", response_class=HTMLResponse)
async def run_details_ui(request: Request, run_id: str, db: AsyncSession = Depends(get_db)):
    """Render the run details page."""
    from sqlalchemy import select

    # Fetch run
    result = await db.execute(select(models.AnalysisRun).where(models.AnalysisRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Fetch items
    result_items = await db.execute(
        select(models.ResultItem).where(models.ResultItem.run_id == run_id)
    )
    items = result_items.scalars().all()

    return templates.TemplateResponse(
        "run_details.html", {"request": request, "run": run, "items": items}
    )


@app.get("/compare", response_class=HTMLResponse)
async def compare_runs_ui(
    request: Request, base_id: str, target_id: str, db: AsyncSession = Depends(get_db)
):
    """Render the comparison view between two runs."""
    from sqlalchemy import select

    # Fetch both runs
    result_base = await db.execute(
        select(models.AnalysisRun).where(models.AnalysisRun.id == base_id)
    )
    run_base = result_base.scalar_one_or_none()

    result_target = await db.execute(
        select(models.AnalysisRun).where(models.AnalysisRun.id == target_id)
    )
    run_target = result_target.scalar_one_or_none()

    if not run_base or not run_target:
        raise HTTPException(status_code=404, detail="One or both runs not found")

    # Calculate metric diffs
    metrics_diff = {}
    base_metrics = run_base.metrics_summary or {}
    target_metrics = run_target.metrics_summary or {}

    all_keys = set(base_metrics.keys()) | set(target_metrics.keys())
    for k in all_keys:
        val_base = base_metrics.get(k, 0)
        val_target = target_metrics.get(k, 0)
        metrics_diff[k] = {
            "base": val_base,
            "target": val_target,
            "diff": val_target - val_base,
            "pct_change": ((val_target - val_base) / val_base * 100) if val_base != 0 else 0,
        }

    return templates.TemplateResponse(
        "compare.html",
        {
            "request": request,
            "run_base": run_base,
            "run_target": run_target,
            "metrics_diff": metrics_diff,
        },
    )


@app.get("/versions", response_class=HTMLResponse)
async def versions_ui(request: Request, db: AsyncSession = Depends(get_db)):
    """Render the versions list page."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    # Fetch versions with run counts
    # Note: selectinload is needed if we access version.runs in template
    result = await db.execute(
        select(models.PipelineVersion)
        .options(selectinload(models.PipelineVersion.runs))
        .order_by(models.PipelineVersion.created_at.desc())
    )
    versions = result.scalars().all()

    return templates.TemplateResponse("versions.html", {"request": request, "versions": versions})


# === Real-time Metrics WebSocket ===
@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    from .realtime import stream_metrics

    await stream_metrics(websocket)


# === Webhook Management Routes ===
@app.post("/api/webhooks/register")
async def register_webhook(
    url: str, events: list[str], user: Optional[models.User] = Depends(get_current_user_from_cookie)
):
    """Register a new webhook"""
    from raglint.webhooks import WebhookEvent, webhook_manager

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    webhook_events = [WebhookEvent(e) for e in events]
    webhook_manager.register_webhook(url, webhook_events)

    return {"status": "registered", "url": url}


@app.get("/api/webhooks/list")
async def list_webhooks(user: Optional[models.User] = Depends(get_current_user_from_cookie)):
    """List registered webhooks"""
    from raglint.webhooks import webhook_manager

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    return {"webhooks": webhook_manager.webhooks}


# === OAuth Routes ===
@app.get("/auth/google/login")
async def google_login_route(request: Request):
    """Initiate Google OAuth login"""
    from .oauth import google_login

    return await google_login(request)


@app.get("/auth/google/callback")
async def google_callback_route(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback"""
    from sqlalchemy import select

    from . import auth
    from .oauth import google_callback

    user_info = await google_callback(request)
    email = user_info.get("email")

    # Find or create user
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        # Create new user from OAuth
        user = models.User(email=email, hashed_password="")  # No password for OAuth users
        db.add(user)
        await db.commit()

    # Create session
    access_token = auth.create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/auth/github/login")
async def github_login_route(request: Request):
    """Initiate GitHub OAuth login"""
    from .oauth import github_login

    return await github_login(request)


@app.get("/auth/github/callback")
async def github_callback_route(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle GitHub OAuth callback"""
    from sqlalchemy import select

    from . import auth
    from .oauth import github_callback

    user_info = await github_callback(request)
    email = user_info.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by GitHub")

    # Find or create user
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = models.User(email=email, hashed_password="")
        db.add(user)
        await db.commit()

    # Create session
    access_token = auth.create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


# === Batch API Routes ===
@app.post("/api/batch/analyze")
async def batch_analyze(
    request: schemas.AnalyzeRequest,
    background_tasks: BackgroundTasks,
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
):
    """Start a batch analysis job for large datasets"""
    from .batch import create_batch_job

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    job_id = create_batch_job(request.data, request.config, background_tasks)

    return {"job_id": job_id, "status": "started"}


@app.get("/api/batch/status/{job_id}")
async def batch_status(
    job_id: str, user: Optional[models.User] = Depends(get_current_user_from_cookie)
):
    """Get the status of a batch job"""
    from .batch import get_batch_job_status

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    return get_batch_job_status(job_id)


@app.get("/api/batch/results/{job_id}")
async def batch_results(
    job_id: str, user: Optional[models.User] = Depends(get_current_user_from_cookie)
):
    """Get the results of a completed batch job"""
    from .batch import get_batch_job_results

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    return get_batch_job_results(job_id)


# === PDF Export Route ===
@app.get("/runs/{run_id}/export/pdf")
async def export_run_pdf(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
):
    """Export run as PDF"""
    if not user:
        return RedirectResponse(url="/login")

    from sqlalchemy import select

    from .pdf_export import generate_pdf_report

    # Get run
    result = await db.execute(select(models.AnalysisRun).where(models.AnalysisRun.id == run_id))
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Get items
    result = await db.execute(select(models.ResultItem).where(models.ResultItem.run_id == run_id))
    items = result.scalars().all()

    # Convert to dicts
    run_dict = {"id": run.id, "metrics_summary": run.metrics_summary, "timestamp": run.timestamp}
    items_list = [
        {"query": item.query, "response": item.response, "metrics": item.metrics} for item in items
    ]

    # Generate PDF
    pdf_bytes = generate_pdf_report(run_dict, items_list)

    from fastapi.responses import Response

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=raglint_run_{run_id[:8]}.pdf"},
    )


@app.get("/datasets", response_class=HTMLResponse)
async def datasets_list(
    request: Request,
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db),
):
    """List all datasets."""
    if not user:
        return RedirectResponse(url="/login")

    result = await db.execute(
        select(models.Dataset)
        .where(models.Dataset.user_id == user.id)
        .order_by(models.Dataset.created_at.desc())
    )
    datasets = result.scalars().all()

    return templates.TemplateResponse(
        "datasets.html", {"request": request, "datasets": datasets, "user": user}
    )


@app.post("/datasets", response_class=HTMLResponse)
async def datasets_create(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Create a new dataset from CSV/JSON."""
    if not user:
        return RedirectResponse(url="/login")

    # Create Dataset
    dataset = models.Dataset(name=name, description=description, user_id=user.id)
    db.add(dataset)
    await db.flush()  # Get ID

    # Parse File
    content = await file.read()
    items = []

    try:
        if file.filename.endswith(".csv"):
            # Parse CSV
            text = content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text))
            for row in reader:
                items.append(row)
        elif file.filename.endswith(".json"):
            # Parse JSON
            import json

            items = json.loads(content)
            if not isinstance(items, list):
                raise ValueError("JSON must be a list of objects")
    except Exception as e:
        logger.error(f"Error parsing dataset file: {e}")
        # TODO: Show error to user
        pass

    # Create Items
    for item_data in items:
        db_item = models.DatasetItem(dataset_id=dataset.id, data=item_data)
        db.add(db_item)

    await db.commit()

    return RedirectResponse(url="/datasets", status_code=303)


@app.get("/datasets/{dataset_id}", response_class=HTMLResponse)
async def datasets_detail(
    request: Request,
    dataset_id: str,
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db),
):
    """View dataset details."""
    if not user:
        return RedirectResponse(url="/login")

    # Get Dataset
    result = await db.execute(
        select(models.Dataset).where(
            models.Dataset.id == dataset_id, models.Dataset.user_id == user.id
        )
    )
    dataset = result.scalar_one_or_none()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Get Items
    result = await db.execute(
        select(models.DatasetItem).where(models.DatasetItem.dataset_id == dataset_id)
    )
    items = result.scalars().all()

    return templates.TemplateResponse(
        "dataset_detail.html",
        {"request": request, "dataset": dataset, "items": items, "user": user},
    )


@app.get("/traces", response_class=HTMLResponse)
async def traces_ui(
    request: Request, user: Optional[models.User] = Depends(get_current_user_from_cookie)
):
    """Render the traces page with tree visualization."""
    if not user:
        return RedirectResponse(url="/login")

    # Read traces from jsonl file
    events = []
    trace_file = "raglint_events.jsonl"

    if os.path.exists(trace_file):
        import json

        try:
            with open(trace_file) as f:
                # Read all lines
                lines = f.readlines()
                for line in lines:
                    if line.strip():
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Error reading traces: {e}")

    # Build Tree Structure
    events_by_id = {e.get("trace_id"): e for e in events if e.get("trace_id")}
    children_by_parent = {}
    roots = []

    # Organize parent/child relationships
    for e in events:
        tid = e.get("trace_id")
        pid = e.get("parent_id")

        if not tid:
            continue

        if pid and pid in events_by_id:
            if pid not in children_by_parent:
                children_by_parent[pid] = []
            children_by_parent[pid].append(e)
        else:
            # No parent, or parent not found in current set -> treat as root
            roots.append(e)

    # Sort roots by timestamp (newest first)
    roots.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Recursive function to build tree with depth
    def build_tree(event):
        children = children_by_parent.get(event.get("trace_id"), [])
        # Sort children by timestamp
        children.sort(key=lambda x: x.get("timestamp", ""))

        event["children"] = [build_tree(c) for c in children]
        return event

    # Build full trees for roots
    trace_trees = [build_tree(r) for r in roots]

    # Limit to last 50 root traces for performance
    trace_trees = trace_trees[:50]

    return templates.TemplateResponse(
        "traces.html", {"request": request, "traces": trace_trees, "user": user}
    )


@app.get("/marketplace", response_class=HTMLResponse)
async def marketplace_ui(
    request: Request, user: Optional[models.User] = Depends(get_current_user_from_cookie)
):
    """Render the plugin marketplace."""
    if not user:
        return RedirectResponse(url="/login")

    registry = PluginRegistry()
    available_plugins = registry.list_available_plugins()

    # Check installed status
    loader = PluginLoader.get_instance()
    installed_names = set(loader.plugins.keys())

    for p in available_plugins:
        p["installed"] = p["name"] in installed_names

    return templates.TemplateResponse(
        "marketplace.html", {"request": request, "plugins": available_plugins, "user": user}
    )


@app.post("/marketplace/install", response_class=HTMLResponse)
async def marketplace_install(
    request: Request,
    plugin_name: str = Form(...),
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
):
    """Install a plugin."""
    if not user:
        return RedirectResponse(url="/login")

    registry = PluginRegistry()
    try:
        registry.install_plugin(plugin_name)
        # Reload plugins
        PluginLoader.get_instance().load_plugins()
    except Exception as e:
        logger.error(f"Failed to install plugin {plugin_name}: {e}")
        # TODO: Show error
        pass

    return RedirectResponse(url="/marketplace", status_code=303)


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(
    request: Request, user: Optional[models.User] = Depends(get_current_user_from_cookie)
):
    # Placeholder page for now
    return templates.TemplateResponse("analytics.html", {"request": request, "user": user})


@app.get("/api/analytics/drift")
async def get_drift_analysis(
    metric_name: str,
    threshold: float = 0.15,
    db: AsyncSession = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
):
    """Get drift analysis for a specific metric."""
    try:
        # Fetch historical runs
        result = await db.execute(
            select(models.Run).order_by(models.Run.timestamp.desc()).limit(100)
        )
        runs = result.scalars().all()

        # Convert to dict format
        historical_data = []
        for run in runs:
            historical_data.append({"timestamp": run.timestamp, "metrics": run.metrics or {}})

        # Perform drift detection
        detector = DriftDetector()
        drift_analysis = detector.detect_drift(historical_data, metric_name, threshold)

        return drift_analysis
    except Exception as e:
        logger.error(f"Error in drift analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/cohorts")
async def get_cohort_analysis(
    group_by: str = "config_hash",
    db: AsyncSession = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user_from_cookie),
):
    """Get cohort analysis."""
    try:
        # Fetch runs
        result = await db.execute(
            select(models.Run).order_by(models.Run.timestamp.desc()).limit(100)
        )
        runs = result.scalars().all()

        # Convert to dict format
        runs_data = []
        for run in runs:
            runs_data.append(
                {
                    "config_hash": run.config_hash,
                    "tags": run.tags or [],
                    "metrics": run.metrics or {},
                }
            )

        # Perform cohort analysis
        analyzer = CohortAnalyzer()
        cohort_analysis = analyzer.analyze_cohorts(runs_data, group_by)

        return cohort_analysis
    except Exception as e:
        logger.error(f"Error in cohort analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("raglint.dashboard.app:app", host="0.0.0.0", port=8000, reload=True)
