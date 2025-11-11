"""Unit tests for LLMClient."""
import json
from unittest.mock import patch

import pytest
from llm_client import LLMClient
from models.agent import AgentData


class MockMessage:
    """Mock message from Agent SDK."""

    def __init__(self, result=None):
        self.result = result


class TestLLMClient:
    """Tests for LLMClient class."""

    @pytest.fixture()
    def client(self):
        """Create LLM client instance."""
        return LLMClient()

    @pytest.mark.asyncio()
    async def test_generate_agent_with_valid_description(self, client):
        """Should generate agent data with valid description."""
        # Arrange
        description = "A brave knight who protects the kingdom"
        mock_response = {
            "name": "Sir Valor",
            "backstory": "A legendary knight with unwavering courage.",
            "personality_traits": ["brave", "loyal", "protective"],
            "avatar_prompt": "A knight in shining armor, Game Boy Color style",
        }

        # Mock the Agent SDK query function with XML format
        async def mock_query(prompt):
            xml_response = f"<output>{json.dumps(mock_response)}</output>"
            yield MockMessage(result=xml_response)

        with patch("llm_client.query", side_effect=mock_query):
            # Act
            result = await client.generate_agent(description)

            # Assert - result is now AgentData object
            assert isinstance(result, AgentData)
            assert result.name == "Sir Valor"
            assert len(result.personality_traits) == 3  # noqa: PLR2004
            assert "brave" in result.personality_traits
            expected_prompt = "A knight in shining armor, Game Boy Color style"
            assert result.avatar_prompt == expected_prompt

    @pytest.mark.asyncio()
    async def test_generate_agent_with_markdown_json_response(self, client):
        """Should parse JSON from XML output tags."""
        # Arrange
        description = "A wise owl"
        mock_agent_data = {
            "name": "Professor Hoot",
            "backstory": "A scholarly owl who teaches magic.",
            "personality_traits": ["wise", "patient"],
            "avatar_prompt": "An owl with glasses, pixel art style",
        }
        # Wrap JSON in XML output tags
        xml_response = f"<output>{json.dumps(mock_agent_data)}</output>"

        async def mock_query(prompt):
            yield MockMessage(result=xml_response)

        with patch("llm_client.query", side_effect=mock_query):
            # Act
            result = await client.generate_agent(description)

            # Assert - result is AgentData object
            assert isinstance(result, AgentData)
            assert result.name == "Professor Hoot"
            assert result.personality_traits == ["wise", "patient"]

    @pytest.mark.asyncio()
    async def test_generate_agent_fallback_on_json_parse_error(self, client):
        """Should return fallback data when JSON parsing fails."""
        # Arrange
        description = "A playful cat"

        async def mock_query(prompt):
            yield MockMessage(result="Invalid JSON response {not valid}")

        with patch("llm_client.query", side_effect=mock_query):
            # Act
            result = await client.generate_agent(description)

            # Assert - fallback returns AgentData object
            assert isinstance(result, AgentData)
            assert result.name == "Pixelmon"
            assert "friendly" in result.personality_traits
            assert description[:50] in result.backstory

    @pytest.mark.asyncio()
    async def test_generate_agent_fallback_on_sdk_error(self, client):
        """Should return fallback data when Agent SDK raises exception."""
        # Arrange
        description = "A dragon"

        async def mock_query(prompt):
            raise RuntimeError("Agent SDK error")
            yield  # Make it a generator

        with patch("llm_client.query", side_effect=mock_query):
            # Act
            result = await client.generate_agent(description)

            # Assert - fallback returns AgentData object
            assert isinstance(result, AgentData)
            assert result.name == "Pixelmon"
            assert result.avatar_prompt is not None

    @pytest.mark.asyncio()
    async def test_generate_agent_consumes_full_generator(self, client):
        """Should fully consume Agent SDK generator to avoid async scope issues."""
        # Arrange
        description = "A robot"
        mock_response = {
            "name": "RoboBot",
            "backstory": "A helpful robot pokemon.",
            "personality_traits": ["helpful", "curious"],
            "avatar_prompt": "A cute robot, pixel art",
        }

        message_count = 0

        async def mock_query(prompt):
            nonlocal message_count
            # Simulate multiple messages
            yield MockMessage(result=None)  # SystemMessage
            xml_response = f"<output>{json.dumps(mock_response)}</output>"
            yield MockMessage(result=xml_response)  # ResultMessage
            message_count += 1
            yield MockMessage(result=None)  # Final message
            message_count += 1

        with patch("llm_client.query", side_effect=mock_query):
            # Act
            result = await client.generate_agent(description)

            # Assert - result is AgentData object
            assert isinstance(result, AgentData)
            assert result.name == "RoboBot"
            # Verify generator was fully consumed
            assert message_count == 2  # noqa: PLR2004

    @pytest.mark.asyncio()
    async def test_generate_agent_strips_whitespace_from_json(self, client):
        """Should strip whitespace from JSON response."""
        # Arrange
        description = "A wizard"
        mock_data = {
            "name": "Merlin",
            "backstory": "A powerful wizard.",
            "personality_traits": ["wise"],
            "avatar_prompt": "A wizard with a long beard, pixel art style",
        }

        async def mock_query(prompt):
            # Add extra whitespace and wrap in XML
            xml_response = f"<output>\n\n  {json.dumps(mock_data)}  \n\n</output>"
            yield MockMessage(result=xml_response)

        with patch("llm_client.query", side_effect=mock_query):
            # Act
            result = await client.generate_agent(description)

            # Assert - result is AgentData object
            assert isinstance(result, AgentData)
            assert result.name == "Merlin"

    @pytest.mark.asyncio()
    async def test_generate_agent_includes_avatar_prompt_in_fallback(self, client):
        """Should include basic avatar prompt in fallback data."""
        # Arrange
        description = "A unicorn"

        async def mock_query(prompt):
            yield MockMessage(result="")  # Empty response

        with patch("llm_client.query", side_effect=mock_query):
            # Act
            result = await client.generate_agent(description)

            # Assert - fallback returns AgentData object
            assert isinstance(result, AgentData)
            assert result.avatar_prompt is not None
            assert "pokemon-style" in result.avatar_prompt.lower()
