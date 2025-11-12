"""Unit tests for default world creation without LLM generation.

Similar to how default agents (starter Pokemon) can be created without LLM,
this tests creating pre-defined starter worlds instantly.
"""

import pytest
from src.world_service import WorldService


@pytest.mark.asyncio
async def test_create_default_world_directly():
    """Test creating a pre-defined default world without LLM generation."""
    service = WorldService(db_path="sqlite+aiosqlite:///:memory:")
    await service.init_db()

    # Pre-defined default world data (no LLM needed)
    default_world = {
        "name": "Pallet Town",
        "description": "A peaceful starter town with grassy fields and friendly neighbors",
        "width": 10,
        "height": 10,
        "game_type": "grid",
        "grid": [
            ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
            ["G", "T", "T", "G", "G", "G", "G", "T", "T", "G"],
            ["G", "T", "T", "G", "G", "G", "G", "T", "T", "G"],
            ["G", "G", "G", "G", "P", "P", "G", "G", "G", "G"],
            ["G", "G", "G", "G", "P", "P", "G", "G", "G", "G"],
            ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
            ["G", "W", "W", "G", "G", "G", "G", "W", "W", "G"],
            ["G", "W", "W", "G", "G", "G", "G", "W", "W", "G"],
            ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"],
            ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G"]
        ],
        "agent_position": [4, 4]
    }

    # Create world with pre-defined data
    agent_id = "test-agent-123"
    world = await service.create_world_from_data(
        agent_id=agent_id,
        world_data=default_world
    )

    # Verify world was created with exact data
    assert world["name"] == "Pallet Town"
    assert world["width"] == 10
    assert world["height"] == 10
    assert world["game_type"] == "grid"
    assert len(world["grid"]) == 10
    assert len(world["grid"][0]) == 10
    assert world["agent_position"] == [4, 4]
    assert world["agent_id"] == agent_id


@pytest.mark.asyncio
async def test_multiple_default_worlds():
    """Test that different default worlds can be created."""
    service = WorldService(db_path="sqlite+aiosqlite:///:memory:")
    await service.init_db()

    default_worlds = [
        {
            "name": "Pallet Town",
            "description": "A peaceful starter town",
            "width": 10,
            "height": 10,
            "game_type": "grid",
            "grid": [["G"] * 10 for _ in range(10)],
            "agent_position": [5, 5]
        },
        {
            "name": "Viridian Forest",
            "description": "A dense forest with tall trees",
            "width": 8,
            "height": 8,
            "game_type": "grid",
            "grid": [["T"] * 8 for _ in range(8)],
            "agent_position": [0, 0]
        }
    ]

    agent_id = "test-agent-456"

    for default_data in default_worlds:
        world = await service.create_world_from_data(
            agent_id=agent_id,
            world_data=default_data
        )
        assert world["name"] == default_data["name"]
        assert world["width"] == default_data["width"]
        assert world["height"] == default_data["height"]
