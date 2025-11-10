import json
import re
from claude_agent_sdk import query

class LLMClient:
    def __init__(self):
        # Agent SDK doesn't require API key - it works through Claude Code CLI
        pass

    async def generate_agent(self, description: str) -> dict:
        """Generate agent data using Claude via Agent SDK."""
        prompt = f"""Create an AI companion based on this description: {description}

Return ONLY a valid JSON object with this exact structure (no markdown, no extra text):
{{
    "name": "agent name",
    "backstory": "2-3 sentence backstory",
    "personality_traits": ["trait1", "trait2", "trait3"],
    "avatar_prompt": "detailed prompt for image generation in Pokémon retro Game Boy style"
}}

The avatar_prompt should describe a Pokémon-style character in retro Game Boy Color aesthetic.
Keep the backstory child-friendly and engaging.
Make personality traits single words or short phrases.

Return ONLY the JSON object, nothing else."""

        try:
            # Collect the response from the Agent SDK
            # Use ResultMessage.result which contains the final response
            # IMPORTANT: Must fully consume the generator to avoid asyncio scope issues
            response_text = ""

            async for message in query(prompt=prompt):
                # Only use ResultMessage which has the final result
                if hasattr(message, 'result') and message.result:
                    response_text = message.result
                    # Continue to let generator finish naturally, don't break

            print(f"[INFO] Agent SDK response: {response_text[:200]}...")

            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*$', '', response_text)
            response_text = response_text.strip()

            # Parse JSON from response
            # Look for JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                print(f"[SUCCESS] Generated agent: {data['name']}")
                return data
            else:
                raise ValueError(f"No JSON found in response: {response_text}")

        except Exception as e:
            print(f"[ERROR] Failed to generate agent with Agent SDK: {e}")
            # Return fallback data
            return {
                "name": "Pixelmon",
                "backstory": f"A companion inspired by: {description[:50]}... Ready for adventure in the digital world!",
                "personality_traits": ["friendly", "curious", "helpful"],
                "avatar_prompt": "cute pokemon-style character, Game Boy Color aesthetic, pixel art, colorful"
            }
