"""
Comprehensive tests for dashboard database models and operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime


@pytest.mark.asyncio
async def test_dashboard_database_init():
    """Test dashboard database initialization."""
    from raglint.dashboard.database import init_db
    # Should complete without error
    await init_db()


@pytest.mark.asyncio
async def test_run_model_create():
    """Test Run model creation."""
    from raglint.dashboard.database import Run
    
    run = Run(
        id="test-run-123",
        timestamp=datetime.now(),
        config={"provider": "mock"},
        results={"score": 0.85}
    )
    assert run.id == "test-run-123"
    assert run.results["score"] == 0.85


@pytest.mark.asyncio
async def test_dataset_model():
    """Test Dataset model."""
    from raglint.dashboard.database import Dataset
    
    dataset = Dataset(
        name="test_dataset",
        description="Test dataset",
        data=[{"query": "test"}]
    )
    assert dataset.name == "test_dataset"
    assert len(dataset.data) == 1


def test_get_db_session():
    """Test getting database session."""
    from raglint.dashboard.database import get_db
    
    # Should return an async generator
    db_gen = get_db()
    assert db_gen is not None
