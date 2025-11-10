"""Unit tests for LLM world generation."""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from llm_world_generator import LLMWorldGenerator
from models.world import WorldData
from pydantic import ValidationError


@pytest.fixture
def world_generator():
    """Create a world generator instance for testing."""
    return LLMWorldGenerator()


@pytest.mark.asyncio
async def test_generate_world_success(world_generator):
    """Test successful world generation with valid LLM response."""
    description = "a peaceful meadow with a small pond"

    # Mock Agent SDK response
    mock_response = {
        "name": "Peaceful Meadow",
        "description": "A tranquil meadow with soft grass and a sparkling pond",
        "grid": [
            ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
            ["grass", "grass", "grass", "water", "water", "grass", "grass", "grass", "grass", "grass"],
            ["grass", "path", "grass", "water", "water", "grass", "grass", "grass", "grass", "grass"],
            ["grass", "path", "grass", "grass", "grass", "grass", "wall", "wall", "grass", "grass"],
            ["grass", "path", "path", "path", "grass", "grass", "wall", "wall", "grass", "grass"],
            ["grass", "grass", "grass", "path", "grass", "grass", "grass", "grass", "grass", "grass"],
            ["grass", "grass", "grass", "path", "grass", "grass", "grass", "grass", "grass", "grass"],
            ["grass", "grass", "grass", "path", "path", "grass", "grass", "grass", "grass", "grass"],
            ["grass", "grass", "grass", "grass", "path", "grass", "grass", "grass", "grass", "goal"],
            ["grass", "grass", "grass", "grass", "path", "path", "path", "path", "path", "path"]
        ],
        "agent_start": [1, 1]
    }

    # Mock the query function from Agent SDK
    async def mock_query_generator(*args, **kwargs):
        mock_message = MagicMock()
        json_str = json.dumps(mock_response)
        mock_message.result = f"```json\n{json_str}\n```"
        yield mock_message

    with patch('llm_world_generator.query', side_effect=mock_query_generator):
        world_data = await world_generator.generate_world(description)

    # Assertions
    assert isinstance(world_data, WorldData)
    assert world_data.name == "Peaceful Meadow"
    assert len(world_data.grid) == 10
    assert len(world_data.grid[0]) == 10
    assert world_data.agent_start == [1, 1]
    assert all(tile in ["grass", "wall", "water", "path", "goal"] for row in world_data.grid for tile in row)


@pytest.mark.asyncio
async def test_generate_world_validates_grid_size(world_generator):
    """Test that world generator validates 10x10 grid requirement."""
    description = "a small world"

    # Mock invalid response with wrong grid size
    invalid_response = {
        "name": "Too Small",
        "description": "A world that's too small",
        "grid": [
            ["grass", "grass"],
            ["grass", "grass"]
        ],
        "agent_start": [0, 0]
    }

    async def mock_query_generator(*args, **kwargs):
        mock_message = MagicMock()
        json_str = json.dumps(invalid_response)
        mock_message.result = f"```json\n{json_str}\n```"
        yield mock_message

    with patch('llm_world_generator.query', side_effect=mock_query_generator):
        with pytest.raises(ValidationError):
            await world_generator.generate_world(description)


@pytest.mark.asyncio
async def test_generate_world_validates_tile_types(world_generator):
    """Test that world generator validates tile types."""
    description = "a world with invalid tiles"

    # Mock response with invalid tile type
    invalid_response = {
        "name": "Invalid World",
        "description": "A world with wrong tiles",
        "grid": [
            ["invalid_tile"] * 10 for _ in range(10)
        ],
        "agent_start": [0, 0]
    }

    async def mock_query_generator(*args, **kwargs):
        mock_message = MagicMock()
        json_str = json.dumps(invalid_response)
        mock_message.result = f"```json\n{json_str}\n```"
        yield mock_message

    with patch('llm_world_generator.query', side_effect=mock_query_generator):
        with pytest.raises(ValidationError):
            await world_generator.generate_world(description)


@pytest.mark.asyncio
async def test_generate_world_validates_agent_start_position(world_generator):
    """Test that agent start position is within grid bounds."""
    description = "a world"

    # Mock response with invalid agent start position
    invalid_response = {
        "name": "Bad Start",
        "description": "Agent starts outside grid",
        "grid": [["grass"] * 10 for _ in range(10)],
        "agent_start": [15, 15]  # Out of bounds
    }

    async def mock_query_generator(*args, **kwargs):
        mock_message = MagicMock()
        json_str = json.dumps(invalid_response)
        mock_message.result = f"```json\n{json_str}\n```"
        yield mock_message

    with patch('llm_world_generator.query', side_effect=mock_query_generator):
        with pytest.raises(ValidationError):
            await world_generator.generate_world(description)


@pytest.mark.asyncio
async def test_generate_world_fallback_on_error(world_generator):
    """Test that generator returns fallback world on error."""
    description = "a test world"

    # Mock SDK to raise exception
    async def mock_query_error(*args, **kwargs):
        raise Exception("SDK Error")

    with patch('llm_world_generator.query', side_effect=mock_query_error):
        world_data = await world_generator.generate_world(description)

    # Should return valid fallback world
    assert isinstance(world_data, WorldData)
    assert len(world_data.grid) == 10
    assert len(world_data.grid[0]) == 10


@pytest.mark.asyncio
async def test_generate_world_prompt_includes_description(world_generator):
    """Test that the prompt includes user's description."""
    description = "a magical forest with ancient trees"

    mock_response = {
        "name": "Test World",
        "description": "A test world for prompt validation",
        "grid": [["grass"] * 10 for _ in range(10)],
        "agent_start": [0, 0]
    }

    captured_prompt = None

    async def mock_query_capture(*args, **kwargs):
        nonlocal captured_prompt
        captured_prompt = kwargs.get('prompt', args[0] if args else None)
        mock_message = MagicMock()
        json_str = json.dumps(mock_response)
        mock_message.result = f"```json\n{json_str}\n```"
        yield mock_message

    with patch('llm_world_generator.query', side_effect=mock_query_capture):
        await world_generator.generate_world(description)

    assert captured_prompt is not None
    assert "magical forest with ancient trees" in captured_prompt
