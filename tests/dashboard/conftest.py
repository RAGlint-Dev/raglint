import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from raglint.dashboard.app import app
from raglint.dashboard.database import Base, get_db
from raglint.dashboard import database

# Use file-based SQLite for testing to avoid memory sharing issues
import os
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

from sqlalchemy.pool import StaticPool

@pytest_asyncio.fixture(name="test_db")
async def fixture_test_db():
    # Create test engine
    test_engine = create_async_engine(
        TEST_DB_URL, 
        connect_args={"check_same_thread": False},
        poolclass=None
    )
    
    # Create tables
    # Import models to ensure they are registered with Base
    from raglint.dashboard import models
    from sqlalchemy import inspect
    print(f"DEBUG: Tables in metadata: {Base.metadata.tables.keys()}")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with test_engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        print(f"DEBUG: Tables in DB: {tables}")
    
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
    
    if os.path.exists("./test.db"):
        os.remove("./test.db")
