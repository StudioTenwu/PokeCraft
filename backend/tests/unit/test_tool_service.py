"""Unit tests for ToolService."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.tool_service import ToolService


class TestToolService:
    """Test suite for ToolService."""

    @pytest.fixture
    async def service(self) -> ToolService:
        """Create a ToolService instance for testing."""
        svc = ToolService(db_path="sqlite+aiosqlite:///:memory:")
        await svc.init_db()
        return svc

    @pytest.mark.asyncio
    async def test_create_tool(self, service: ToolService) -> None:
        """Test creating a new tool."""
        from src.tool_generator import ToolCode

        # Mock the tool_generator.generate_tool method directly on the service instance
        mock_tool_code = ToolCode(
            tool_name="test_tool",
            code="@tool(...)\nasync def test_tool(args): pass",
            explanation="A test tool",
        )

        service.tool_generator.generate_tool = AsyncMock(return_value=mock_tool_code)

        # Mock append_tool_to_file
        with patch("src.tool_service.append_tool_to_file"):
            result = await service.create_tool("agent-123", "Make a test tool")

            assert result["tool_name"] == "test_tool"
            assert result["code"] == "@tool(...)\nasync def test_tool(args): pass"
            assert result["explanation"] == "A test tool"
            assert "tool_id" in result

    @pytest.mark.asyncio
    async def test_get_agent_tools(self, service: ToolService) -> None:
        """Test getting all tools for an agent."""
        from src.tool_generator import ToolCode

        # First create a tool
        mock_tool_code = ToolCode(
            tool_name="agent_tool",
            code="code",
            explanation="explanation",
        )
        service.tool_generator.generate_tool = AsyncMock(return_value=mock_tool_code)

        with patch("src.tool_service.append_tool_to_file"):
            await service.create_tool("agent-456", "Create a tool")

        # Now get tools for the agent
        tools = await service.get_agent_tools("agent-456")

        assert isinstance(tools, list)
        assert len(tools) > 0
        assert tools[0]["agent_id"] == "agent-456"
        assert tools[0]["name"] == "agent_tool"

    @pytest.mark.asyncio
    async def test_delete_tool(self, service: ToolService) -> None:
        """Test deleting a tool."""
        from src.tool_generator import ToolCode

        # First create a tool
        mock_tool_code = ToolCode(
            tool_name="deletable_tool",
            code="code",
            explanation="explanation",
        )
        service.tool_generator.generate_tool = AsyncMock(return_value=mock_tool_code)

        with patch("src.tool_service.append_tool_to_file"):
            result = await service.create_tool("agent-789", "Create a deletable tool")
            tool_id = result["tool_id"]

        # Delete the tool
        success = await service.delete_tool("deletable_tool")
        assert success is True

        # Verify it's gone
        tools = await service.get_agent_tools("agent-789")
        assert len(tools) == 0

    @pytest.mark.asyncio
    async def test_get_nonexistent_agent_tools(self, service: ToolService) -> None:
        """Test getting tools for an agent with no tools."""
        tools = await service.get_agent_tools("nonexistent-agent")
        assert isinstance(tools, list)
        assert len(tools) == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tool(self, service: ToolService) -> None:
        """Test deleting a tool that doesn't exist."""
        success = await service.delete_tool("nonexistent_tool")
        assert success is False
