"""
Pytest configuration and shared fixtures
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

# === Pytest Configuration ===
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# === Temporary Directory Fixtures ===
@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)

@pytest.fixture
def sample_data():
    """Sample RAG pipeline data for testing"""
    return [
        {
            "query": "What is RAG?",
            "response": "RAG stands for Retrieval Augmented Generation. It combines retrieval with generation.",
            "retrieved_contexts": [
                "RAG is a technique that enhances LLMs with external knowledge.",
                "Retrieval Augmented Generation was introduced by Facebook AI."
            ],
            "ground_truth": "RAG combines retrieval with LLM generation"
        },
        {
            "query": "How does RAG work?",
            "response": "RAG retrieves relevant documents and uses them to generate better answers.",
            "retrieved_contexts": [
                "RAG first retrieves documents from a knowledge base.",
                "Then it uses these documents as context for the LLM."
            ],
            "ground_truth": "RAG retrieves documents then generates answers"
        }
    ]

@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    from raglint.config import Config
    
    config = Config()
    config.openai_api_key = "test-key"
    config.model_name = "gpt-3.5-turbo"
    config.metrics = {
        "chunking": True,
        "faithfulness": False,  # Disable LLM-based for tests
        "semantic": False,
        "retrieval": True
    }
    return config

@pytest.fixture
async def test_db():
    """Create test database"""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from raglint.dashboard.models import Base
    
    # Use in-memory SQLite for tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def mock_openai(monkeypatch):
    """Mock OpenAI API calls"""
    class MockCompletion:
        def __init__(self, content):
            self.content = content
    
    class MockChoice:
        def __init__(self, content):
            self.message = MockCompletion(content)
    
    class MockResponse:
        def __init__(self, content="0.95"):
            self.choices = [MockChoice(content)]
    
    def mock_create(*args, **kwargs):
        return MockResponse()
    
    # Mock openai module
    from unittest.mock import MagicMock
    mock_openai_module = MagicMock()
    mock_openai_module.ChatCompletion.create = mock_create
    monkeypatch.setitem(__import__('sys').modules, 'openai', mock_openai_module)
    
    return mock_openai_module
