import json
import logging
import xml.etree.ElementTree as ET

from claude_agent_sdk import query
from models.agent import AgentData
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        # Agent SDK doesn't require API key - it works through Claude Code CLI
        pass

    async def generate_agent(self, description: str) -> AgentData:
        """Generate agent data using Claude via Agent SDK."""
        logger.debug(f"Generating agent from description: {description[:50]}...")

        prompt = f"""Create an AI pokemon based on this description: {description}

You must return your response wrapped in XML <output> tags with CDATA containing a valid JSON object.

Return your response in this exact format:
<output><![CDATA[
{{
    "name": "agent name",
    "backstory": "2-3 sentence backstory",
    "personality_traits": ["trait1", "trait2", "trait3"],
    "avatar_prompt": "detailed prompt for image generation in Pokemon retro Game Boy style"
}}
]]></output>

Requirements:
- The avatar_prompt should describe a Pokemon-style character in retro Game Boy Color aesthetic
- The name should have a cute, Pokemon-like feel
- Keep the backstory child-friendly and engaging
- Make personality traits single words or short phrases
- The JSON must be valid and properly formatted
- You must wrap the entire JSON object in <output><![CDATA[...]]></output> tags"""

        try:
            # Collect the response from the Agent SDK
            # Use ResultMessage.result which contains the final response
            # IMPORTANT: Must fully consume the generator to avoid asyncio scope issues
            response_text = ""

            async for message in query(prompt=prompt):
                # Only use ResultMessage which has the final result
                if hasattr(message, "result") and message.result:
                    response_text = message.result
                    # Continue to let generator finish naturally, don't break

            logger.debug(f"Agent SDK response: {response_text[:200]}...")

            # Parse XML to extract JSON from <output> CDATA tags
            root = ET.fromstring(response_text)
            json_str = root.text.strip()
            logger.debug("Extracted JSON from <output> CDATA tags")

            # Parse the JSON string
            data_dict = json.loads(json_str)

            # Validate with Pydantic - raises ValidationError if invalid
            agent_data = AgentData(**data_dict)
            logger.info(f"Successfully generated agent: {agent_data.name}")
            return agent_data

        except ValidationError as ve:
            # Log validation errors and re-raise for debugging
            logger.error(f"LLM returned invalid data: {ve}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Failed to generate agent with Agent SDK: {e}", exc_info=True)
            logger.warning("Returning fallback agent data due to generation failure")
            # Return validated fallback data
            return AgentData(
                name="Pixelmon",
                backstory=(
                    f"A pokemon inspired by: {description[:50]}... "
                    "Ready for adventure in the digital world!"
                ),
                personality_traits=["friendly", "curious", "helpful"],
                avatar_prompt=(
                    "cute pokemon-style character, Game Boy Color "
                    "aesthetic, pixel art, colorful"
                ),
            )
