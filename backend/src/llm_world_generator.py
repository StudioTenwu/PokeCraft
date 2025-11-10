"""LLM-based world generator using Claude Agent SDK."""
import json
import logging
import xml.etree.ElementTree as ET

from claude_agent_sdk import query
from models.world import WorldData
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class LLMWorldGenerator:
    """Generates 2D grid worlds using Claude LLM via Agent SDK."""

    def __init__(self) -> None:
        # Agent SDK doesn't require API key - it works through Claude Code CLI
        pass

    async def generate_world(self, description: str) -> WorldData:
        """Generate a 10x10 world grid based on natural language description.

        Args:
            description: Natural language description of the desired world

        Returns:
            WorldData: Validated world data with 10x10 grid

        Raises:
            ValidationError: If LLM returns invalid data structure
        """
        prompt = self._build_world_prompt(description)

        try:
            # Collect the response from the Agent SDK
            response_text = ""

            async for message in query(prompt=prompt):
                # Only use ResultMessage which has the final result
                if hasattr(message, "result") and message.result:
                    response_text = message.result
                    # Continue to let generator finish naturally

            logger.debug(f"World generation response: {response_text[:200]}...")

            # Parse and validate response
            world_data = self._parse_world_response(response_text)
            logger.info(f"Successfully generated world: {world_data.name}")
            return world_data

        except ValidationError as ve:
            # Log validation errors and re-raise for debugging
            logger.error(f"LLM returned invalid world data: {ve}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Failed to generate world with Agent SDK: {e}", exc_info=True)
            # Return validated fallback data
            return self._get_fallback_world(description)

    def _build_world_prompt(self, description: str) -> str:
        """Build the prompt for world generation."""
        return f"""Create a 2D grid world based on this description: {description}

You must return your response wrapped in XML <output> tags with CDATA
containing a valid JSON object.

Return your response in this exact format:
<output><![CDATA[
{{
    "name": "world name",
    "description": "brief description of the world",
    "grid": [
        ["grass", "grass", "path", ...],
        ["grass", "water", "path", ...],
        ... (10 rows total)
    ],
    "agent_start": [x, y]
}}
]]></output>

REQUIREMENTS:
- Grid must be EXACTLY 10x10 (10 rows, 10 columns)
- Use ONLY these tile types: "grass", "wall", "water", "path", "goal"
- agent_start must be [x, y] coordinates within bounds (0-9)
- Place exactly ONE "goal" tile somewhere in the world
- Create a logical layout that matches the description
- Make sure there's a path from agent_start to the goal
- Wrap the entire JSON in <output><![CDATA[...]]></output> tags

Keep it child-friendly and fun!"""

    def _parse_world_response(self, response_text: str) -> WorldData:
        """Parse and validate LLM response into WorldData using XML parsing.

        This method matches the approach in llm_client.py for consistency.
        """
        try:
            # Try XML parsing with CDATA first (preferred method)
            root = ET.fromstring(response_text)
            json_str = root.text.strip()
            logger.debug("Extracted JSON from <output> CDATA tags")
        except ET.ParseError:
            # Fallback: Manual tag extraction (backward compatibility)
            logger.debug("XML parse failed, trying manual tag extraction")
            start_tag = "<output>"
            end_tag = "</output>"

            start_idx = response_text.find(start_tag)
            end_idx = response_text.find(end_tag)

            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx + len(start_tag):end_idx].strip()
                # Remove CDATA markers if present
                json_str = (
                    json_str.replace("<![CDATA[", "").replace("]]>", "").strip()
                )
            else:
                msg = f"No <output> tags found in response: {response_text[:100]}"
                raise ValueError(msg) from None

        # Parse the JSON string
        data_dict = json.loads(json_str)

        # Validate with Pydantic - raises ValidationError if invalid
        return WorldData(**data_dict)

    def _get_fallback_world(self, description: str) -> WorldData:
        """Return a valid fallback world when generation fails."""
        return WorldData(
            name="Starter World",
            description=f"A simple world inspired by: {description[:50]}",
            grid=[
                ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
                ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
                ["grass", "grass", "path", "path", "path", "path", "path", "grass", "grass", "grass"],
                ["grass", "grass", "path", "grass", "grass", "grass", "path", "grass", "grass", "grass"],
                ["grass", "grass", "path", "grass", "water", "grass", "path", "grass", "grass", "grass"],
                ["grass", "grass", "path", "grass", "water", "grass", "path", "grass", "grass", "grass"],
                ["grass", "grass", "path", "grass", "grass", "grass", "path", "grass", "grass", "grass"],
                ["grass", "grass", "path", "path", "path", "path", "path", "grass", "grass", "grass"],
                ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "goal"],
                ["grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass", "grass"],
            ],
            agent_start=[2, 2],
        )
