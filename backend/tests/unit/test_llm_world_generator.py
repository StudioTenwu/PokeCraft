"""Unit tests for LLMWorldGenerator."""
import json
from unittest.mock import patch, MagicMock

import pytest
from llm_world_generator import LLMWorldGenerator
from models.world import WorldData
from pydantic import ValidationError


class MockMessage:
    """Mock message from Agent SDK."""
    def __init__(self, result=None):
        self.result = result


class TestLLMWorldGenerator:
    """Tests for LLMWorldGenerator class."""

    @pytest.fixture()
    def generator(self):
        """Create world generator instance."""
        return LLMWorldGenerator()

    @pytest.mark.asyncio()
    async def test_generate_world_with_xml_cdata_response(self, generator):
        """Should parse world data from XML CDATA output tags."""
        # Arrange
        description = "A forest maze with a goal"
        mock_world = {
            "name": "Forest Maze",
            "description": "A dense forest with winding paths",
            "grid": [
                ["grass"] * 10 for _ in range(9)
            ] + [["grass"] * 9 + ["goal"]],
            "agent_start": [0, 0]
        }

        # XML response with CDATA
        xml_response = f"<output><![CDATA[{json.dumps(mock_world)}]]></output>"

        async def mock_query(prompt):
            yield MockMessage(result=xml_response)

        with patch("llm_world_generator.query", side_effect=mock_query):
            # Act
            result = await generator.generate_world(description)

            # Assert
            assert isinstance(result, WorldData)
            assert result.name == "Forest Maze"
            assert len(result.grid) == 10
            assert len(result.grid[0]) == 10

    @pytest.mark.asyncio()
    async def test_generate_world_without_cdata_fallback(self, generator):
        """Should handle XML without CDATA (backward compatibility)."""
        # Arrange
        description = "A simple world"
        mock_world = {
            "name": "Simple World",
            "description": "A basic world",
            "grid": [["grass"] * 10 for _ in range(10)],
            "agent_start": [5, 5]
        }

        # XML without CDATA
        xml_response = f"<output>{json.dumps(mock_world)}</output>"

        async def mock_query(prompt):
            yield MockMessage(result=xml_response)

        with patch("llm_world_generator.query", side_effect=mock_query):
            # Act
            result = await generator.generate_world(description)

            # Assert
            assert isinstance(result, WorldData)
            assert result.name == "Simple World"

    @pytest.mark.asyncio()
    async def test_generate_world_validates_grid_size(self, generator):
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

        xml_response = f"<output><![CDATA[{json.dumps(invalid_response)}]]></output>"

        async def mock_query(prompt):
            yield MockMessage(result=xml_response)

        with patch('llm_world_generator.query', side_effect=mock_query):
            with pytest.raises(ValidationError):
                await generator.generate_world(description)

    @pytest.mark.asyncio()
    async def test_generate_world_validates_tile_types(self, generator):
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

        xml_response = f"<output><![CDATA[{json.dumps(invalid_response)}]]></output>"

        async def mock_query(prompt):
            yield MockMessage(result=xml_response)

        with patch('llm_world_generator.query', side_effect=mock_query):
            with pytest.raises(ValidationError):
                await generator.generate_world(description)

    @pytest.mark.asyncio()
    async def test_generate_world_validates_agent_start_position(self, generator):
        """Test that agent start position is within grid bounds."""
        description = "a world"

        # Mock response with invalid agent start position
        invalid_response = {
            "name": "Bad Start",
            "description": "Agent starts outside grid",
            "grid": [["grass"] * 10 for _ in range(10)],
            "agent_start": [15, 15]  # Out of bounds
        }

        xml_response = f"<output><![CDATA[{json.dumps(invalid_response)}]]></output>"

        async def mock_query(prompt):
            yield MockMessage(result=xml_response)

        with patch('llm_world_generator.query', side_effect=mock_query):
            with pytest.raises(ValidationError):
                await generator.generate_world(description)

    @pytest.mark.asyncio()
    async def test_generate_world_fallback_on_error(self, generator):
        """Test that generator returns fallback world on error."""
        description = "a test world"

        # Mock SDK to raise exception
        async def mock_query_error(*args, **kwargs):
            raise Exception("SDK Error")

        with patch('llm_world_generator.query', side_effect=mock_query_error):
            world_data = await generator.generate_world(description)

        # Should return valid fallback world
        assert isinstance(world_data, WorldData)
        assert len(world_data.grid) == 10
        assert len(world_data.grid[0]) == 10

    @pytest.mark.asyncio()
    async def test_generate_world_prompt_includes_xml_instructions(self, generator):
        """Test that the prompt includes XML CDATA format instructions."""
        description = "a magical forest"

        mock_response = {
            "name": "Test World",
            "description": "A test world",
            "grid": [["grass"] * 10 for _ in range(10)],
            "agent_start": [0, 0]
        }

        captured_prompt = None

        async def mock_query_capture(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            xml_response = f"<output><![CDATA[{json.dumps(mock_response)}]]></output>"
            yield MockMessage(result=xml_response)

        with patch('llm_world_generator.query', side_effect=mock_query_capture):
            await generator.generate_world(description)

        assert captured_prompt is not None
        assert "<output><![CDATA[" in captured_prompt
        assert "magical forest" in captured_prompt
