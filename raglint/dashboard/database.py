"""
Database connection and session management.
"""

import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default to a local SQLite file in the user's home directory or current dir
DB_PATH = os.getenv("RAGLINT_DB_URL") or os.getenv(
    "RAGLINT_DB_PATH", "sqlite+aiosqlite:///raglint.db"
)

# Configure engine arguments based on database type
engine_args = {"echo": False}
if "sqlite" in DB_PATH:
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(DB_PATH, **engine_args)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
