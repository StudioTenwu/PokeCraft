"""Tool generation service using Claude Agent SDK."""
import ast
import json
import logging
import re
import xml.etree.ElementTree as ET
from typing import Any

from claude_agent_sdk import query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ToolCode(BaseModel):
    """Generated tool code and metadata."""

    tool_name: str = Field(..., description="Name of the generated tool")
    code: str = Field(..., description="Complete Python code with @tool decorator")
    explanation: str = Field(..., description="Kid-friendly explanation of what the tool does")
    action_id: str | None = Field(default=None, description="Which action this tool uses")


class ToolGenerator:
    """Service for generating custom tools using Claude Agent SDK."""

    # List of forbidden imports for security
    FORBIDDEN_IMPORTS = {"os", "subprocess", "sys", "importlib", "eval", "exec", "__import__"}

    def __init__(self) -> None:
        """Initialize the ToolGenerator."""
        pass

    async def generate_tool(
        self, description: str, agent_id: str, game_action_set: Any | None = None, world_context: dict[str, Any] | None = None
    ) -> ToolCode:
        """
        Generate a custom tool from natural language description.

        Args:
            description: Natural language description of what the tool should do
            agent_id: ID of the agent this tool is for
            game_action_set: Optional GameActionSet defining available game actions

        Returns:
            ToolCode object with tool_name, code, and explanation

        Raises:
            ValueError: If generated code is unsafe or invalid
        """
        logger.info(f"Generating tool for agent {agent_id} from description: {description}...")

        forbidden_list = ", ".join(sorted(self.FORBIDDEN_IMPORTS))

        # Include world context if provided
        world_info = ""
        if world_context:
            world_info = f"""

    World Context:
    - Size: {world_context.get('width', '?')}x{world_context.get('height', '?')}
    - Game Type: {world_context.get('game_type', 'unknown')}
"""

        # Include action information if provided
        action_info = ""
        if game_action_set:
            action_info = f"""

    IMPORTANT: This tool must emit a game action. Available actions in this game:
{self._format_actions_for_prompt(game_action_set)}

    Your tool MUST return an "action" field along with "content":
    Return format: {{"content": [{{"type": "text", "text": "message"}}], "action": {{"action_id": "action_id", "parameters": {{...}}}}}}"""

        prompt = f"""Create a custom tool for an AI agent based on this description: {description}

    The tool will be used in a children's educational game where agents explore 2D grid worlds.
{world_info}{action_info}

    You must return your response wrapped in XML <output> tags with CDATA containing a valid JSON object.

    Return your response in this exact format:
    <output><![CDATA[
    {{
        "tool_name": "function_name_here",
        "code": "COMPLETE Python code here with @tool decorator",
        "explanation": "Kid-friendly explanation (1-2 sentences)"
    }}
    ]]></output>

    Requirements for the generated code:
    1. Must include @tool decorator: @tool("tool_name", "description", {{"param": "type"}})
    2. Function signature: async def tool_name(args: dict[str, Any]) -> dict[str, Any]:
    3. Extract parameters from args dict: param = args.get('param_name', default_value)
    4. Return format: {{"content": [{{"type": "text", "text": "result message"}}]}}{', "action": {{"action_id": "...", "parameters": {{...}}}}' if game_action_set else ''}
    5. NO forbidden imports: {forbidden_list}
    6. The function name must match the tool_name in the @tool decorator
    7. The description should have enough information for an agent to use it effectively

    Example:
    @tool("move_forward", "Move agent forward", {{"steps": "int"}})
    async def move_forward(args: dict[str, Any]) -> dict[str, Any]:
        steps = args.get('steps', 1)
        return {{"content": [{{"type": "text", "text": f"Moved forward {{steps}} steps"}}]}}{', "action": {{"action_id": "move", "parameters": {{"direction": "north", "steps": steps}}}}' if game_action_set else ''}

    Make the tool appropriate for: {description}"""

        try:
            # Collect response from Claude Agent SDK
            response_text = ""

            async for message in query(prompt=prompt):
                if hasattr(message, "result") and message.result:
                    response_text = message.result
                    # Continue to let generator finish naturally

            logger.debug(f"Agent SDK response: {response_text[:200]}...")

            # Parse XML to extract JSON from <output> CDATA tags
            root = ET.fromstring(response_text)
            json_str = root.text.strip()
            logger.debug("Extracted JSON from <output> CDATA tags")

            # Parse JSON
            data_dict = json.loads(json_str)

            # Validate with Pydantic
            tool_code = ToolCode(**data_dict)

            # Validate code safety
            self._validate_code_safety(tool_code.code, tool_code.tool_name)

            logger.info(f"Successfully generated tool: {tool_code.tool_name}")
            return tool_code

        except Exception as e:
            logger.error(f"Failed to generate tool: {e}", exc_info=True)
            raise

    def _validate_code_safety(self, code: str, expected_tool_name: str) -> None:
        """
        Validate that generated code is safe and well-formed.

        Args:
            code: Python code to validate
            expected_tool_name: Expected function name

        Raises:
            ValueError: If code is unsafe or invalid
        """
        # 1. Check syntax validity
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e}")

        # 2. Check for forbidden imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(forbidden in alias.name for forbidden in self.FORBIDDEN_IMPORTS):
                        raise ValueError(f"Forbidden import detected: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(forbidden in node.module for forbidden in self.FORBIDDEN_IMPORTS):
                    raise ValueError(f"Forbidden import detected: {node.module}")

        # 3. Check for @tool decorator
        if "@tool" not in code:
            raise ValueError("Generated code must have @tool decorator")

        # 4. Check function name matches expected tool name
        func_def = None
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                func_def = node
                break

        if not func_def:
            raise ValueError("No async function definition found")

        if func_def.name != expected_tool_name:
            raise ValueError(
                f"Function name '{func_def.name}' does not match expected tool name '{expected_tool_name}'"
            )

        # 5. Check return statement exists (basic check)
        has_return = any(isinstance(node, ast.Return) for node in ast.walk(tree))
        if not has_return:
            logger.warning(f"Tool {expected_tool_name} may not have a return statement")

        logger.debug(f"Code validation passed for tool: {expected_tool_name}")

    def _format_actions_for_prompt(self, action_set: Any) -> str:
        """Format action set information for LLM prompt.

        Args:
            action_set: GameActionSet with available actions

        Returns:
            Formatted string describing available actions
        """
        if not action_set or not hasattr(action_set, "actions"):
            return "No actions available"

        lines = []
        for action in action_set.actions:
            params_str = ""
            if action.parameters:
                param_list = []
                for param in action.parameters:
                    req = "required" if param.required else "optional"
                    default = f", default={param.default}" if not param.required else ""
                    param_list.append(
                        f"{param.name} ({param.type.value}, {req}{default}): {param.description}"
                    )
                params_str = "\n      " + "\n      ".join(param_list)

            lines.append(
                f"    - {action.action_id}: {action.description}{params_str}"
            )

        return "\n".join(lines)
