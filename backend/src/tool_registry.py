"""Dynamic tool discovery and MCP server creation."""
import importlib.util
import logging
from pathlib import Path
from typing import Any, Callable

from claude_agent_sdk import McpSdkServerConfig

logger = logging.getLogger(__name__)


def get_available_tools(agent_id: str, tools_file_path: str | None = None) -> list[Callable]:
    """
    Discover and return all @tool-decorated functions for an agent.

    Args:
        agent_id: ID of the agent to get tools for
        tools_file_path: Optional path to tools.py file (defaults to src/tools.py)

    Returns:
        List of callable tool functions

    Raises:
        Exception: If tools file cannot be loaded or parsed
    """
    if tools_file_path is None:
        # Default to src/tools.py in the same directory as this file
        tools_file_path = str(Path(__file__).parent / "tools.py")

    logger.info(f"Loading tools for agent {agent_id} from {tools_file_path}")

    try:
        # Dynamically import the tools module
        spec = importlib.util.spec_from_file_location("tools", tools_file_path)
        if spec is None or spec.loader is None:
            logger.warning(f"Could not load spec from {tools_file_path}")
            return []

        tools_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tools_module)

        # Extract all async functions (tools) from the module
        tools = []
        for attr_name in dir(tools_module):
            attr = getattr(tools_module, attr_name)
            # Check if it's a callable async function (not a built-in or import)
            # Exclude the 'tool' decorator function itself
            if callable(attr) and not attr_name.startswith("_") and attr_name != "tool":
                # Additional check: it should be defined in the tools module
                if hasattr(attr, "__module__") and attr.__module__ == "tools":
                    tools.append(attr)
                    logger.debug(f"Discovered tool: {attr_name}")

        logger.info(f"Found {len(tools)} tools for agent {agent_id}")
        return tools

    except FileNotFoundError:
        logger.warning(f"Tools file not found: {tools_file_path}")
        return []
    except Exception as e:
        logger.error(f"Error loading tools from {tools_file_path}: {e}", exc_info=True)
        raise


def create_user_tool_server(tools_file_path: str | None = None) -> McpSdkServerConfig:
    """
    Create an MCP server configuration with discovered tools.

    Args:
        tools_file_path: Optional path to tools.py file

    Returns:
        McpSdkServerConfig for the tool server
    """
    logger.info("Creating user tool MCP server")

    # For now, we create a basic server config
    # The actual tools will be loaded dynamically when the agent is deployed
    server_config = McpSdkServerConfig(
        command="python",
        args=["-m", "src.tools"],
        env=None,
    )

    logger.info("User tool MCP server created")
    return server_config


def append_tool_to_file(tool_code: str, tools_file_path: str | None = None) -> None:
    """
    Append a new tool to the tools.py file.

    Args:
        tool_code: Complete Python code for the tool (with @tool decorator)
        tools_file_path: Optional path to tools.py file

    Raises:
        IOError: If file cannot be written
    """
    if tools_file_path is None:
        tools_file_path = str(Path(__file__).parent / "tools.py")

    logger.info(f"Appending tool to {tools_file_path}")

    try:
        with open(tools_file_path, "a") as f:
            f.write("\n\n")
            f.write(tool_code)
            f.write("\n")

        logger.info("Tool successfully appended to file")

    except Exception as e:
        logger.error(f"Failed to append tool to file: {e}", exc_info=True)
        raise IOError(f"Could not write to tools file: {e}")
