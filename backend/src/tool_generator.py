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


class ToolGenerator:
    """Service for generating custom tools using Claude Agent SDK."""

    # List of forbidden imports for security
    FORBIDDEN_IMPORTS = {"os", "subprocess", "sys", "importlib", "eval", "exec", "__import__"}

    def __init__(self) -> None:
        """Initialize the ToolGenerator."""
        pass

    async def generate_tool(self, description: str, agent_id: str) -> ToolCode:
        """
        Generate a custom tool from natural language description.

        Args:
            description: Natural language description of what the tool should do
            agent_id: ID of the agent this tool is for

        Returns:
            ToolCode object with tool_name, code, and explanation

        Raises:
            ValueError: If generated code is unsafe or invalid
        """
        logger.info(f"Generating tool for agent {agent_id} from description: {description}...")

        forbidden_list = ", ".join(sorted(self.FORBIDDEN_IMPORTS))
        prompt = f"""Create a custom tool for an AI agent based on this description: {description}

    The tool will be used in a children's educational game where agents explore 2D grid worlds.

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
    4. Return format: {{"content": [{{"type": "text", "text": "result message"}}]}}
    5. NO forbidden imports: {forbidden_list}
    6. The function name must match the tool_name in the @tool decorator
    7. The description should have enough information for an agent to use it effectively

    Example:
    @tool("move_forward", "Move agent forward", {{"steps": "int"}})
    async def move_forward(args: dict[str, Any]) -> dict[str, Any]:
        steps = args.get('steps', 1)
        return {{"content": [{{"type": "text", "text": f"Moved forward {{steps}} steps"}}]}}

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
