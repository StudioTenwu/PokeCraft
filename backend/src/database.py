"""Database configuration and session management."""
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)

# Database URL - SQLite with aiosqlite driver
DB_PATH = Path(__file__).parent.parent / "agents.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database schema by creating all tables."""
    logger.info(f"Initializing database at {DB_PATH}")
    try:
        # Import models to register them with Base
        from models.db_models import Base

        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise


async def get_session() -> AsyncSession:
    """Get a database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
