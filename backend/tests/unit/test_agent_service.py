"""Unit tests for AgentService."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agent_service import AgentService
from models.agent import AgentData
from models.db_models import AgentDB


class TestAgentService:
    """Tests for AgentService class."""

    @pytest.fixture()
    def service(self):
        """Create agent service instance."""
        return AgentService()

    @pytest.mark.asyncio()
    async def test_create_agent_with_valid_description(self, service):
        """Should create agent with all required fields."""
        # Arrange
        description = "A brave knight"
        mock_agent_data = AgentData(
            name="Sir Valor",
            backstory="A legendary knight.",
            personality_traits=["brave", "loyal"],
            avatar_prompt="A knight in armor",
        )

        service.llm_client.generate_agent = AsyncMock(return_value=mock_agent_data)
        service.avatar_generator.generate_avatar = MagicMock(
            return_value="/static/avatars/test-123.png",
        )

        # Act
        test_uuid = uuid.UUID("12345678-1234-1234-1234-123456789abc")
        with patch("uuid.uuid4", return_value=test_uuid):
            result = await service.create_agent(description)

        # Assert
        assert result["name"] == "Sir Valor"
        assert result["backstory"] == "A legendary knight."
        assert result["personality_traits"] == ["brave", "loyal"]
        assert result["avatar_url"] == "/static/avatars/test-123.png"
        assert "id" in result

        # Verify LLM client was called
        service.llm_client.generate_agent.assert_called_once_with(description)

        # Verify avatar generator was called
        service.avatar_generator.generate_avatar.assert_called_once()

    @pytest.mark.asyncio()
    async def test_create_agent_generates_unique_id(self, service):
        """Should generate unique UUID for each agent."""
        # Arrange
        description = "A wizard"
        mock_agent_data = AgentData(
            name="Merlin",
            backstory="A wise wizard.",
            personality_traits=["wise"],
            avatar_prompt="A wizard with a long beard, pixel art style",
        )

        service.llm_client.generate_agent = AsyncMock(return_value=mock_agent_data)
        service.avatar_generator.generate_avatar = MagicMock(
            return_value="/static/avatars/test.png",
        )

        # Act
        result1 = await service.create_agent(description)
        result2 = await service.create_agent(description)

        # Assert
        assert result1["id"] != result2["id"]
        assert isinstance(uuid.UUID(result1["id"]), uuid.UUID)
        assert isinstance(uuid.UUID(result2["id"]), uuid.UUID)

    @pytest.mark.asyncio()
    async def test_create_agent_saves_to_database(self, service):
        """Should persist agent to database with correct fields."""
        # Arrange
        description = "A robot"
        mock_agent_data = AgentData(
            name="RoboBot",
            backstory="A helpful robot.",
            personality_traits=["helpful", "curious"],
            avatar_prompt="A robot pixel art",
        )

        service.llm_client.generate_agent = AsyncMock(return_value=mock_agent_data)
        service.avatar_generator.generate_avatar = MagicMock(
            return_value="/static/avatars/test.png",
        )

        # Act
        result = await service.create_agent(description)

        # Assert - Verify agent was saved by retrieving it
        saved_agent = await service.get_agent(result["id"])
        assert saved_agent is not None
        assert saved_agent["name"] == "RoboBot"
        assert saved_agent["backstory"] == "A helpful robot."
        assert saved_agent["personality_traits"] == ["helpful", "curious"]

    @pytest.mark.asyncio()
    async def test_create_agent_converts_personality_to_json(self, service):
        """Should convert personality_traits list to JSON string for database."""
        # Arrange
        description = "A cat"
        mock_agent_data = AgentData(
            name="Whiskers",
            backstory="A playful cat.",
            personality_traits=["playful", "curious", "friendly"],
            avatar_prompt="A cat pixel art style",
        )

        service.llm_client.generate_agent = AsyncMock(return_value=mock_agent_data)
        service.avatar_generator.generate_avatar = MagicMock(
            return_value="/static/avatars/cat.png",
        )

        # Act
        result = await service.create_agent(description)

        # Assert
        # Verify the service stores traits as a list in response
        assert isinstance(result["personality_traits"], list)
        assert result["personality_traits"] == ["playful", "curious", "friendly"]

    @pytest.mark.asyncio()
    async def test_get_agent_by_id_returns_agent(self, service):
        """Should retrieve agent by ID from database."""
        # Arrange - First create an agent
        description = "A brave knight"
        mock_agent_data = AgentData(
            name="Sir Valor",
            backstory="A brave knight.",
            personality_traits=["brave", "loyal"],
            avatar_prompt="A knight in armor",
        )

        service.llm_client.generate_agent = AsyncMock(return_value=mock_agent_data)
        service.avatar_generator.generate_avatar = MagicMock(
            return_value="/static/avatars/test-123.png",
        )

        created_agent = await service.create_agent(description)
        agent_id = created_agent["id"]

        # Act
        result = await service.get_agent(agent_id)

        # Assert
        assert result["id"] == agent_id
        assert result["name"] == "Sir Valor"
        assert result["personality_traits"] == ["brave", "loyal"]

    @pytest.mark.asyncio()
    async def test_get_agent_by_id_returns_none_when_not_found(self, service):
        """Should return None when agent ID not found."""
        # Arrange
        agent_id = "nonexistent"

        # Act
        result = await service.get_agent(agent_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio()
    async def test_create_agent_uses_avatar_prompt_from_llm(self, service):
        """Should use avatar_prompt from LLM for image generation."""
        # Arrange
        description = "A dragon"
        avatar_prompt = "A fierce dragon with red scales, Game Boy Color style"
        mock_agent_data = AgentData(
            name="Drakon",
            backstory="A mighty dragon.",
            personality_traits=["fierce", "brave"],
            avatar_prompt=avatar_prompt,
        )

        service.llm_client.generate_agent = AsyncMock(return_value=mock_agent_data)
        service.avatar_generator.generate_avatar = MagicMock(
            return_value="/static/avatars/dragon.png",
        )

        # Act
        with patch("uuid.uuid4", return_value=uuid.UUID(int=999)):
            await service.create_agent(description)

        # Assert
        # Verify avatar generator was called with the LLM-generated prompt
        call_args = service.avatar_generator.generate_avatar.call_args[0]
        assert call_args[1] == avatar_prompt
