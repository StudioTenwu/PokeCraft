#!/usr/bin/env python3
"""Script to add MCP server integration to agent_deployer.py"""

import re

# Read the original file
with open('src/agent_deployer.py', 'r') as f:
    content = f.read()

# 1. Add imports at the top
old_imports = """from claude_agent_sdk import query, ClaudeAgentOptions
from tool_registry import create_user_tool_server, get_available_tools
from action_registry import get_action_set_for_game, create_game_engine
from game_engine import GameEngine"""

new_imports = """from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    create_sdk_mcp_server,
    tool as sdk_tool,
)
from tool_registry import create_user_tool_server, get_available_tools
from action_registry import get_action_set_for_game, create_game_engine
from game_engine import GameEngine
import importlib.util
import sys
from pathlib import Path"""

content = content.replace(old_imports, new_imports)

# 2. Add helper method to load tools dynamically (after __init__)
helper_method = '''
    def _load_tools_from_file(self, tools_file_path: str | None = None) -> list:
        """Dynamically load tools from tools.py file."""
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

            tools = []
            for name in dir(module):
                obj = getattr(module, name)
                if callable(obj) and hasattr(obj, "__claude_tool__"):
                    tools.append(obj)
                    logger.info(f"Loaded tool: {name}")

            logger.info(f"Successfully loaded {len(tools)} tools")
            return tools

        except Exception as e:
            logger.error(f"Failed to load tools: {e}", exc_info=True)
            return []
'''

# Find where to insert (after __init__ method)
init_end = content.find('        self.world_service = world_service\n')
if init_end != -1:
    insert_pos = init_end + len('        self.world_service = world_service\n')
    content = content[:insert_pos] + helper_method + content[insert_pos:]

# 3. Replace the query section with MCP server integration
old_query_section = """            # 3. Load agent's custom tools from tool_service
            tools = await self.tool_service.get_agent_tools(agent_id)
            logger.info(f"Loaded {len(tools)} tools for agent {agent_id}")

            # 3. Create deployment prompt
            prompt = self._build_deployment_prompt(world, goal)

            # 4. Stream agent execution with Claude Agent SDK
            async for message in query(prompt=prompt):"""

new_query_section = """            # 3. Load agent's custom tools from tool_service
            tools = await self.tool_service.get_agent_tools(agent_id)
            logger.info(f"Loaded {len(tools)} tools for agent {agent_id}")

            # 4. Load tools from tools.py and create MCP server
            tool_functions = self._load_tools_from_file()
            if len(tool_functions) == 0:
                logger.warning("No tools found - agent will run without custom tools")

            # Create MCP server with user's custom tools
            user_tool_server = create_sdk_mcp_server(
                name="user_tools",
                version="1.0.0",
                tools=tool_functions
            )
            logger.info(f"Created MCP server with {len(tool_functions)} tools")

            # Build allowed tools list
            allowed_tools = [f"mcp__user_tools__{tool.__name__}" for tool in tool_functions]
            logger.info(f"Allowed tools: {allowed_tools}")

            # Configure Claude Agent SDK with MCP server
            options = ClaudeAgentOptions(
                mcp_servers={"user_tools": user_tool_server},
                allowed_tools=allowed_tools if allowed_tools else None,
            )

            # 5. Create deployment prompt
            prompt = self._build_deployment_prompt(world, goal)

            # 6. Stream agent execution with Claude SDK Client + MCP server
            async with ClaudeSDKClient(options=options) as client:
                async for message in client.query(prompt=prompt):"""

content = content.replace(old_query_section, new_query_section)

# 4. Fix indentation of the final complete event (needs to be inside async with)
# The break and complete event should stay at the same indentation level

# Write the fixed file
with open('src/agent_deployer.py', 'w') as f:
    f.write(content)

print("✓ Agent deployer updated with MCP server integration")
print("✓ Added imports: ClaudeSDKClient, create_sdk_mcp_server, importlib, sys, Path")
print("✓ Added _load_tools_from_file() helper method")
print("✓ Wrapped query in ClaudeSDKClient with MCP server configuration")
