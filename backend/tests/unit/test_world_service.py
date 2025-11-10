"""Unit tests for world service."""
import pytest
import aiosqlite
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from world_service import WorldService
from models.world import WorldData


@pytest.fixture
async def world_service(tmp_path):
    """Create a world service with temporary database."""
    db_path = tmp_path / "test_worlds.db"
    service = WorldService(db_path=str(db_path))
    await service.init_db()
    return service


@pytest.fixture
def mock_world_data():
    """Create mock world data for testing."""
    return WorldData(
        name="Test World",
        description="A test world for unit tests",
        grid=[["grass"] * 10 for _ in range(10)],
        agent_start=[5, 5]
    )


@pytest.mark.asyncio
async def test_init_db_creates_table(world_service):
    """Test that init_db creates the worlds table."""
    # Check table exists by querying it
    async with aiosqlite.connect(world_service.db_path) as db:
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='worlds'"
        ) as cursor:
            result = await cursor.fetchone()
            assert result is not None


@pytest.mark.asyncio
async def test_create_world_success(world_service, mock_world_data):
    """Test successful world creation."""
    agent_id = "test-agent-123"
    description = "a peaceful meadow"

    # Mock the world generator
    with patch.object(world_service.world_generator, 'generate_world',
                     return_value=mock_world_data):
        world = await world_service.create_world(agent_id, description)

    # Assertions
    assert world["id"] is not None
    assert world["agent_id"] == agent_id
    assert world["name"] == "Test World"
    assert world["description"] == "A test world for unit tests"
    assert world["grid"] == [["grass"] * 10 for _ in range(10)]
    assert world["width"] == 10
    assert world["height"] == 10
    assert world["agent_position"] == [5, 5]
    assert "created_at" in world


@pytest.mark.asyncio
async def test_create_world_stores_in_database(world_service, mock_world_data):
    """Test that create_world stores data in database."""
    agent_id = "test-agent-456"
    description = "a forest"

    with patch.object(world_service.world_generator, 'generate_world',
                     return_value=mock_world_data):
        world = await world_service.create_world(agent_id, description)

    # Verify stored in database
    async with aiosqlite.connect(world_service.db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM worlds WHERE id = ?", (world["id"],)
        ) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row["agent_id"] == agent_id
            assert row["name"] == "Test World"


@pytest.mark.asyncio
async def test_get_world_success(world_service, mock_world_data):
    """Test successful world retrieval."""
    agent_id = "test-agent-789"
    description = "test world"

    # Create a world first
    with patch.object(world_service.world_generator, 'generate_world',
                     return_value=mock_world_data):
        created_world = await world_service.create_world(agent_id, description)

    # Retrieve it
    retrieved_world = await world_service.get_world(created_world["id"])

    assert retrieved_world is not None
    assert retrieved_world["id"] == created_world["id"]
    assert retrieved_world["agent_id"] == agent_id
    assert retrieved_world["name"] == "Test World"


@pytest.mark.asyncio
async def test_get_world_not_found(world_service):
    """Test get_world returns None for non-existent world."""
    world = await world_service.get_world("non-existent-id")
    assert world is None


@pytest.mark.asyncio
async def test_create_world_generates_unique_ids(world_service, mock_world_data):
    """Test that multiple worlds get unique IDs."""
    agent_id = "test-agent"
    description = "test"

    with patch.object(world_service.world_generator, 'generate_world',
                     return_value=mock_world_data):
        world1 = await world_service.create_world(agent_id, description)
        world2 = await world_service.create_world(agent_id, description)

    assert world1["id"] != world2["id"]


@pytest.mark.asyncio
async def test_create_world_stores_grid_as_json(world_service, mock_world_data):
    """Test that grid is stored as JSON string in database."""
    agent_id = "test-agent"
    description = "test"

    # Create world with specific grid pattern
    test_grid = [
        ["grass", "wall", "grass"] + ["grass"] * 7,
        ["water", "path", "goal"] + ["grass"] * 7,
    ] + [["grass"] * 10 for _ in range(8)]

    custom_world_data = WorldData(
        name="Custom Grid",
        description="Test grid storage",
        grid=test_grid,
        agent_start=[0, 0]
    )

    with patch.object(world_service.world_generator, 'generate_world',
                     return_value=custom_world_data):
        world = await world_service.create_world(agent_id, description)

    # Verify grid is correctly stored and retrieved
    retrieved = await world_service.get_world(world["id"])
    assert retrieved["grid"] == test_grid
    assert retrieved["grid"][0][0] == "grass"
    assert retrieved["grid"][0][1] == "wall"
    assert retrieved["grid"][1][0] == "water"


@pytest.mark.asyncio
async def test_get_worlds_by_agent_id(world_service, mock_world_data):
    """Test retrieving all worlds for a specific agent."""
    agent_id = "test-agent-multi"
    other_agent_id = "other-agent"

    # Create multiple worlds for the same agent
    with patch.object(world_service.world_generator, 'generate_world',
                     return_value=mock_world_data):
        world1 = await world_service.create_world(agent_id, "world 1")
        world2 = await world_service.create_world(agent_id, "world 2")
        world3 = await world_service.create_world(other_agent_id, "world 3")

    # Get worlds for specific agent
    agent_worlds = await world_service.get_worlds_by_agent_id(agent_id)

    assert len(agent_worlds) == 2
    assert all(w["agent_id"] == agent_id for w in agent_worlds)
    assert {w["id"] for w in agent_worlds} == {world1["id"], world2["id"]}
