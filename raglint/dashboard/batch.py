"""
Batch API for analyzing large datasets
"""

import uuid
from datetime import datetime
from typing import Any

from fastapi import BackgroundTasks, HTTPException

# In-memory job tracker (in production, use Redis or DB)
batch_jobs = {}


class BatchJob:
    def __init__(self, job_id: str, total_items: int):
        self.job_id = job_id
        self.total_items = total_items
        self.processed_items = 0
        self.status = "running"  # running, completed, failed
        self.started_at = datetime.utcnow()
        self.completed_at = None
        self.results = []
        self.errors = []


async def process_batch_job(job_id: str, data: list[dict[str, Any]], config: dict[str, Any]):
    """Background task to process a batch job"""
    job = batch_jobs.get(job_id)
    if not job:
        return

    try:
        from raglint.config import Config
        from raglint.core import RAGPipelineAnalyzer

        # Create analyzer
        cfg = Config.from_dict(config) if config else Config()
        analyzer = RAGPipelineAnalyzer(cfg)

        # Process items in batches of 10
        batch_size = 10
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]

            # Analyze batch
            results = await analyzer.analyze_async(batch)

            # Update job
            job.results.extend(results)
            job.processed_items += len(batch)

        # Mark as completed
        job.status = "completed"
        job.completed_at = datetime.utcnow()

    except Exception as e:
        job.status = "failed"
        job.errors.append(str(e))
        job.completed_at = datetime.utcnow()


def create_batch_job(
    data: list[dict[str, Any]], config: dict[str, Any], background_tasks: BackgroundTasks
) -> str:
    """Create a new batch processing job"""
    job_id = str(uuid.uuid4())

    # Create job tracker
    job = BatchJob(job_id=job_id, total_items=len(data))
    batch_jobs[job_id] = job

    # Start background processing
    background_tasks.add_task(process_batch_job, job_id, data, config)

    return job_id


def get_batch_job_status(job_id: str) -> dict[str, Any]:
    """Get the status of a batch job"""
    job = batch_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.job_id,
        "status": job.status,
        "total_items": job.total_items,
        "processed_items": job.processed_items,
        "progress": (job.processed_items / job.total_items * 100) if job.total_items > 0 else 0,
        "started_at": job.started_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "errors": job.errors,
    }


def get_batch_job_results(job_id: str) -> list[dict[str, Any]]:
    """Get the results of a completed batch job"""
    job = batch_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not yet completed")

    return job.results
