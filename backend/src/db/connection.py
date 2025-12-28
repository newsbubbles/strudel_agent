"""Database connection management."""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Load environment variables from backend/.env
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('STRUDEL_DB_URL')

if not DATABASE_URL:
    raise ValueError("STRUDEL_DB_URL environment variable is required")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging in development
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "command_timeout": 30,
        "statement_cache_size": 512,
    }
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # CRITICAL for async
)

async def init_db():
    """Initialize database tables.
    
    Creates all tables if they don't exist. Safe to call multiple times.
    """
    # Import all models to register them
    from .models import Session, Message, MemoryFile
    
    async with engine.begin() as conn:
        # Use run_sync for non-async metadata operations
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logger.info("Database tables initialized")

async def get_session() -> AsyncSession:
    """Get database session (FastAPI dependency)."""
    async with async_session() as session:
        yield session

async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")
