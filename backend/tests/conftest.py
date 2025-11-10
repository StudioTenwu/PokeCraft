"""Pytest configuration for AICraft backend tests."""
import sys
from pathlib import Path
import asyncio

# Add src directory to Python path so tests can import modules
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Initialize test database at module import time (before any tests run)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models.db_models import Base
import database

# Create test database file - always start fresh
test_db_path = Path(__file__).parent / "test_database.db"
# Delete any existing test database to ensure clean state
if test_db_path.exists():
    test_db_path.unlink()

# Create test engine
test_engine = create_async_engine(
    f"sqlite+aiosqlite:///{test_db_path}",
    echo=False,
)

# Create tables
async def _create_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Run table creation synchronously at import time
loop = asyncio.new_event_loop()
try:
    loop.run_until_complete(_create_tables())
finally:
    loop.close()

# Replace global session factory with test factory
database.async_session_factory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
