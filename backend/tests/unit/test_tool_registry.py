"""Unit tests for tool_registry module."""
import tempfile
from pathlib import Path
from typing import Any

import pytest

from src.tool_registry import create_user_tool_server, get_available_tools


class TestToolRegistry:
    """Test suite for tool registry functions."""

    @pytest.fixture
    def empty_tools_file(self) -> Path:
        """Create a temporary empty tools.py file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('"""Auto-generated tool storage."""\n')
            f.write("from typing import Any\n\n")
            return Path(f.name)

    @pytest.fixture
    def tools_file_with_one_tool(self) -> Path:
        """Create a temporary tools.py file with one tool."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('"""Auto-generated tool storage."""\n')
            f.write("from typing import Any\n\n")
            f.write("# Mock tool decorator for testing\n")
            f.write("def tool(name, desc, params):\n")
            f.write("    def decorator(func):\n")
            f.write("        return func\n")
            f.write("    return decorator\n\n")
            f.write('@tool("test_tool", "Test tool", {"param": "str"})\n')
            f.write("async def test_tool(args: dict[str, Any]) -> dict[str, Any]:\n")
            f.write('    return {"content": [{"type": "text", "text": "Test"}]}\n')
            return Path(f.name)

    @pytest.fixture
    def tools_file_with_multiple_tools(self) -> Path:
        """Create a temporary tools.py file with multiple tools."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('"""Auto-generated tool storage."""\n')
            f.write("from typing import Any\n\n")
            f.write("# Mock tool decorator for testing\n")
            f.write("def tool(name, desc, params):\n")
            f.write("    def decorator(func):\n")
            f.write("        return func\n")
            f.write("    return decorator\n\n")
            f.write('@tool("tool_one", "First tool", {})\n')
            f.write("async def tool_one(args: dict[str, Any]) -> dict[str, Any]:\n")
            f.write('    return {"content": [{"type": "text", "text": "One"}]}\n\n')
            f.write('@tool("tool_two", "Second tool", {"x": "int"})\n')
            f.write("async def tool_two(args: dict[str, Any]) -> dict[str, Any]:\n")
            f.write('    return {"content": [{"type": "text", "text": "Two"}]}\n')
            return Path(f.name)

    def test_get_available_tools_empty_file(self, empty_tools_file: Path) -> None:
        """Test discovering tools from empty file returns empty list."""
        tools = get_available_tools("test-agent", str(empty_tools_file))
        assert tools == []

    def test_get_available_tools_with_one_tool(self, tools_file_with_one_tool: Path) -> None:
        """Test discovering a single tool."""
        tools = get_available_tools("test-agent", str(tools_file_with_one_tool))
        assert len(tools) == 1
        assert tools[0].__name__ == "test_tool"

    def test_get_available_tools_with_multiple_tools(
        self, tools_file_with_multiple_tools: Path
    ) -> None:
        """Test discovering multiple tools."""
        tools = get_available_tools("test-agent", str(tools_file_with_multiple_tools))
        assert len(tools) == 2
        tool_names = [tool.__name__ for tool in tools]
        assert "tool_one" in tool_names
        assert "tool_two" in tool_names

    def test_get_available_tools_default_path(self) -> None:
        """Test using default tools.py path."""
        # Should not raise an error even if file doesn't exist
        # Should return empty list or handle gracefully
        tools = get_available_tools("test-agent")
        assert isinstance(tools, list)

    def test_create_user_tool_server(self) -> None:
        """Test creating MCP server config."""
        server_config = create_user_tool_server()
        # McpSdkServerConfig is a TypedDict, so check structure instead of isinstance
        assert isinstance(server_config, dict)
        assert "command" in server_config
        assert "args" in server_config
        assert server_config["command"] == "python"

    def test_get_available_tools_invalid_file(self) -> None:
        """Test handling of invalid Python file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("this is not valid python code!\n")
            invalid_file = Path(f.name)

        # Should handle gracefully and return empty list or raise informative error
        with pytest.raises(Exception):  # Exact exception type depends on implementation
            get_available_tools("test-agent", str(invalid_file))

    def test_append_tool_to_file(self) -> None:
        """Test appending tool code to tools file."""
        from src.tool_registry import append_tool_to_file

        # Create a temporary tools file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('"""Auto-generated tool storage."""\n')
            f.write("from typing import Any\n")
            tools_file = Path(f.name)

        # Append a tool
        tool_code = """@tool("new_tool", "A new tool", {})
async def new_tool(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": "New tool"}]}"""

        append_tool_to_file(tool_code, str(tools_file))

        # Verify the tool was appended
        with open(tools_file, "r") as f:
            content = f.read()
            assert "new_tool" in content
            assert "@tool" in content
            assert 'return {"content"' in content

        # Clean up
        tools_file.unlink()
