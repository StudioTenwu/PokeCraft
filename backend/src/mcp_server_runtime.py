"""Runtime MCP server using MCP SDK directly.

Dynamically loads tools from tools.py and creates an MCP server
that can be launched via stdio transport for the Claude Agent SDK.

This replaces the buggy SDK create_sdk_mcp_server() approach with a
simpler, more reliable solution using the MCP SDK's stdio server.
"""
import asyncio
import importlib.util
import logging
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import ImageContent, TextContent, Tool

logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("user_tools")


def _load_tools_from_file(tools_file_path: str | None = None) -> list[tuple[str, str, dict[str, Any], Any]]:
    """Dynamically load SDK tools from tools.py file.

    Returns:
        List of (tool_name, tool_description, tool_schema, tool_handler) tuples
    """
    from claude_agent_sdk import SdkMcpTool

    if tools_file_path is None:
        tools_file_path = str(Path(__file__).parent / "tools.py")

    logger.info(f"Loading tools from {tools_file_path}")

    try:
        spec = importlib.util.spec_from_file_location("custom_tools", tools_file_path)
        if spec is None or spec.loader is None:
            logger.warning(f"Could not load tools from {tools_file_path}")
            return []

        module = importlib.util.module_from_spec(spec)
        sys.modules["custom_tools"] = module
        spec.loader.exec_module(module)

        # Collect all SdkMcpTool instances from module
        tools_dict = {}  # Deduplicate by tool name
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, SdkMcpTool):
                # Keep last definition of each tool
                tools_dict[obj.name] = (
                    obj.name,
                    obj.description or "",
                    obj.input_schema or {},
                    obj.handler,
                )
                logger.info(f"Loaded tool: {obj.name}")

        tools = list(tools_dict.values())
        logger.info(f"Successfully loaded {len(tools)} unique tools")
        return tools

    except Exception as e:
        logger.error(f"Failed to load tools: {e}", exc_info=True)
        return []


# Load tools and store handlers
tools_data = _load_tools_from_file()
tool_handlers = {name: handler for name, _, _, handler in tools_data}

# Log loaded tools at startup
logger.info(f"🚀 MCP Server initialized with {len(tools_data)} tools:")
for name, desc, schema, _ in tools_data:
    logger.info(f"   - {name}: {desc[:60]}...")
logger.info(f"   Tool names: {list(tool_handlers.keys())}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name=name,
            description=description,
            inputSchema=schema,
        )
        for name, description, schema, _ in tools_data
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent | ImageContent]:
    """Execute a tool by name."""
    logger.info(f"🔧 MCP Server: Calling tool: {name} with args: {arguments}")

    if name not in tool_handlers:
        error_msg = f"Tool {name} not found"
        logger.error(f"   ❌ {error_msg}")
        return [TextContent(type="text", text=error_msg)]

    try:
        handler = tool_handlers[name]
        result = await handler(arguments)
        logger.info(f"   📦 Tool handler returned: {result}")
        logger.info(f"   📦 Result type: {type(result)}")

        # Convert SDK tool result format to MCP content format
        if isinstance(result, dict) and "content" in result:
            content_list = result["content"]
            logger.info(f"   📋 Extracting content list with {len(content_list)} items")
            mcp_content = []
            for item in content_list:
                if item.get("type") == "text":
                    text_content = TextContent(type="text", text=item["text"])
                    mcp_content.append(text_content)
                    logger.info(f"      ✅ Added text content: {item['text'][:100]}...")
                elif item.get("type") == "image":
                    mcp_content.append(
                        ImageContent(
                            type="image",
                            data=item["data"],
                            mimeType=item.get("mimeType", "image/png"),
                        )
                    )
                    logger.info(f"      ✅ Added image content")

            final_result = mcp_content if mcp_content else [TextContent(type="text", text=str(result))]
            logger.info(f"   🎯 Returning {len(final_result)} MCP content items")
            return final_result

        fallback = [TextContent(type="text", text=str(result))]
        logger.info(f"   ⚠️ Result didn't have 'content' field, returning fallback: {fallback}")
        return fallback

    except Exception as e:
        logger.error(f"   ❌ Tool execution failed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main() -> None:
    """Run the MCP server via stdio transport."""
    import sys
    # Log to stderr so it's visible (stdout is used for MCP protocol)
    print("🚀 MCP Server starting via stdio transport...", file=sys.stderr)
    print(f"🚀 Loaded {len(tools_data)} tools: {list(tool_handlers.keys())}", file=sys.stderr)
    logger.info("Starting MCP server via stdio transport")
    async with stdio_server() as (read_stream, write_stream):
        print("🚀 MCP Server stdio streams established", file=sys.stderr)
        await server.run(read_stream, write_stream, server.create_initialization_options())
        print("🚀 MCP Server shutting down", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
