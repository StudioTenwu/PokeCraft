import logging
import subprocess
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class AvatarGenerator:
    def __init__(
        self,
        model_path: str = "/Users/wz/Desktop/zPersonalProjects/AICraft/models/schnell-3bit",
        base_url: str = "http://localhost:8000"
    ):
        self.model_path = model_path
        self.base_url = base_url
        self.output_dir = Path(__file__).parent.parent / "static" / "avatars"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"AvatarGenerator initialized with model at {model_path}")

    def generate_avatar(self, agent_id: str, prompt: str) -> str:
        """Generate avatar using mflux and return URL path."""
        logger.info(f"Generating avatar for agent {agent_id}")
        output_path = self.output_dir / f"{agent_id}.png"

        # Enhance prompt for Pokémon retro aesthetic
        enhanced_prompt = f"{prompt}, Game Boy Color style, retro pixel art, colorful, nostalgic 90s gaming aesthetic"

        try:
            # Run mflux-generate command
            cmd = [
                "mflux-generate",
                "--model", "schnell",
                "--path", self.model_path,
                "--prompt", enhanced_prompt,
                "--steps", "2",
                "--output", str(output_path)
            ]

            logger.debug(f"Running mflux: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"mflux failed with return code {result.returncode}: {result.stderr}")
                return self._get_fallback_avatar()

            if output_path.exists():
                avatar_url = f"{self.base_url}/static/avatars/{agent_id}.png"
                logger.info(f"Avatar generated successfully: {avatar_url}")
                return avatar_url
            else:
                logger.warning(f"Output file not created: {output_path}")
                return self._get_fallback_avatar()

        except subprocess.TimeoutExpired:
            logger.warning("mflux generation timeout")
            return self._get_fallback_avatar()
        except FileNotFoundError:
            logger.error("mflux-generate command not found", exc_info=True)
            return self._get_fallback_avatar()
        except Exception as e:
            logger.error(f"Avatar generation error: {e}", exc_info=True)
            return self._get_fallback_avatar()

    def _get_fallback_avatar(self) -> str:
        """Return fallback avatar URL (emoji or placeholder)."""
        logger.debug("Using fallback avatar")
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23FFD700' width='200' height='200'/%3E%3Ctext x='50%25' y='50%25' font-size='100' text-anchor='middle' dy='.3em'%3E🤖%3C/text%3E%3C/svg%3E"
