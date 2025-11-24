import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from raglint.dashboard.app import app
from raglint.dashboard.database import Base, get_db
from raglint.dashboard import database

# Use in-memory SQLite for testing
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(name="test_db")
async def fixture_test_db():
    # Create test engine
    test_engine = create_async_engine(
        TEST_DB_URL, 
        connect_args={"check_same_thread": False},
        poolclass=None # distinct connections for in-memory
    )
    
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Override get_db dependency
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session
            
    app.dependency_overrides[get_db] = override_get_db
    
    # Also patch the global engine/SessionLocal in database module 
    # so that background tasks (which might import SessionLocal directly) work
    # This is a bit hacky but necessary since background tasks don't use dependency injection
    original_engine = database.engine
    original_session = database.SessionLocal
    
    database.engine = test_engine
    database.SessionLocal = TestSessionLocal
    
    yield
    
    # Cleanup
    app.dependency_overrides.clear()
    database.engine = original_engine
    database.SessionLocal = original_session
    await test_engine.dispose()

@pytest.mark.asyncio
async def test_health_check(test_db):
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "raglint"


@pytest.mark.asyncio
async def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200
        assert b"RAGLint" in response.content  # Landing page content

@pytest.mark.asyncio
async def test_trigger_analysis(test_db):
    from unittest.mock import patch
    
    # Patch the background task runner to do nothing
    with patch("raglint.dashboard.app.run_analysis_task") as mock_task:
        with TestClient(app) as client:
            payload = {
                "data": [{"query": "test", "response": "test", "retrieved_contexts": ["ctx"], "metrics": {"faithfulness": 0.5}}],
                "config": {"provider": "mock"}
            }
            response = client.post("/analyze", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["config"]["provider"] == "mock"
            
            mock_task.assert_called_once()

@pytest.mark.asyncio
async def test_get_runs(test_db):
    # Create a dummy run
    from raglint.dashboard import models
    from raglint.dashboard.database import SessionLocal
    import uuid
    
    run_id = str(uuid.uuid4())
    async with SessionLocal() as session:
        run = models.AnalysisRun(id=run_id, config={}, metrics_summary={})
        session.add(run)
        await session.commit()
        
    with TestClient(app) as client:
        response = client.get("/runs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["id"] == run_id
        
        # Test get specific run
        response = client.get(f"/runs/{run_id}")
        assert response.status_code == 200
        assert response.json()["id"] == run_id
        
        # Test get items (empty)
        response = client.get(f"/runs/{run_id}/items")
        assert response.status_code == 200
        assert response.json() == []
        
        # Test 404
        response = client.get("/runs/nonexistent")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_run_details_ui(test_db):
    # Create a dummy run with items
    from raglint.dashboard import models
    from raglint.dashboard.database import SessionLocal
    import uuid
    
    run_id = str(uuid.uuid4())
    async with SessionLocal() as session:
        run = models.AnalysisRun(
            id=run_id, 
            config={"provider": "test"}, 
            metrics_summary={"faithfulness": 0.8}
        )
        session.add(run)
        
        item = models.ResultItem(
            run_id=run_id,
            query="test query",
            response="test response",
            retrieved_contexts=["ctx1"],
            metrics={"faithfulness": 0.9}
        )
        session.add(item)
        await session.commit()
        
    with TestClient(app) as client:
        # Test UI endpoint
        response = client.get(f"/runs/{run_id}/ui")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert f"Run {run_id[:8]}" in response.text
        assert "test query" in response.text
        
        # Test 404
        response = client.get("/runs/nonexistent/ui")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_compare_ui(test_db):
    # Create two dummy runs
    from raglint.dashboard import models
    from raglint.dashboard.database import SessionLocal
    import uuid
    
    id1 = str(uuid.uuid4())
    id2 = str(uuid.uuid4())
    
    async with SessionLocal() as session:
        run1 = models.AnalysisRun(
            id=id1, 
            config={"provider": "test"}, 
            metrics_summary={"faithfulness": 0.8}
        )
        run2 = models.AnalysisRun(
            id=id2, 
            config={"provider": "test"}, 
            metrics_summary={"faithfulness": 0.9}
        )
        session.add(run1)
        session.add(run2)
        await session.commit()
        
    with TestClient(app) as client:
        # Test Compare endpoint
        response = client.get(f"/compare?base_id={id1}&target_id={id2}")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Run Comparison" in response.text
        
        # Test 404
        response = client.get(f"/compare?base_id={id1}&target_id=nonexistent")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_versions_ui(test_db):
    # Create a dummy version
    from raglint.dashboard import models
    from raglint.dashboard.database import SessionLocal
    import uuid
    
    async with SessionLocal() as session:
        version = models.PipelineVersion(
            hash="testhash",
            config={"provider": "test"},
            description="Initial commit"
        )
        session.add(version)
        await session.commit()
        
    with TestClient(app) as client:
        response = client.get("/versions")
        assert response.status_code == 200
        assert "Pipeline Versions" in response.text
        response = client.get("/versions")
        assert response.status_code == 200
        assert "Pipeline Versions" in response.text
        assert "Initial commit" in response.text

@pytest.mark.asyncio
async def test_auth_flow(test_db):
    """Test registration, login, and protected route."""
    from raglint.dashboard import models
    from raglint.dashboard.database import SessionLocal
    
    with TestClient(app) as client:
        # 1. Access Home -> Shows Landing Page
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200  # Landing page
        
        # 2. Register
        response = client.post(
            "/auth/register", 
            data={"email": "test@example.com", "password": "password123"},
            follow_redirects=False
        )
        assert response.status_code == 303
        assert "/login" in response.headers["location"]
        
        # Verify user in DB
        async with SessionLocal() as session:
            from sqlalchemy import select
            result = await session.execute(select(models.User).where(models.User.email == "test@example.com"))
            user = result.scalar_one_or_none()
            assert user is not None
            
        # 3. Login UI
        response = client.post(
            "/auth/login-ui",
            data={"email": "test@example.com", "password": "password123"},
            follow_redirects=False
        )
        assert response.status_code == 303
        assert "/dashboard" in response.headers["location"]
        assert "access_token" in response.cookies
        
        # 4. Access Dashboard with Cookie
        client.cookies = response.cookies # Set cookie for subsequent requests
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "test@example.com" in response.text
