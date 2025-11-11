import logging
import subprocess
import os
import re
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Any

logger = logging.getLogger(__name__)


def parse_mflux_progress(stderr_line: str) -> int | None:
    """Parse mflux progress percentage from stderr line.

    Args:
        stderr_line: A line from mflux stderr output

    Returns:
        Progress percentage (0-100) or None if no progress found

    Examples:
        >>> parse_mflux_progress("0%|          | 0/2 [00:00<?, ?it/s]")
        0
        >>> parse_mflux_progress("50%|█████     | 1/2 [00:14<00:14, 14.32s/it]")
        50
        >>> parse_mflux_progress("no progress here")
        None
    """
    match = re.search(r'(\d+)%\|', stderr_line)
    return int(match.group(1)) if match else None


def map_mflux_to_overall(mflux_progress: int) -> int:
    """Map mflux progress (0-100%) to overall progress (25-100%).

    Args:
        mflux_progress: Progress from mflux (0-100)

    Returns:
        Overall progress percentage where mflux maps to 25-100% range

    Examples:
        >>> map_mflux_to_overall(0)
        25
        >>> map_mflux_to_overall(50)
        62
        >>> map_mflux_to_overall(100)
        100
    """
    # Map 0-100% mflux to 25-100% overall
    # Formula: 25 + (mflux * 0.75)
    return int(25 + (mflux_progress * 0.75))

class AvatarGenerator:
    def __init__(
        self,
        model_path: str | None = None,
        base_url: str | None = None
    ):
        from config import Config
        self.model_path = model_path or Config.AVATAR_MODEL_PATH
        self.base_url = base_url or Config.API_BASE_URL
        self.output_dir = Path(__file__).parent.parent / "static" / "avatars"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"AvatarGenerator initialized with model at {self.model_path}")

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

    def _generate_fallback_avatar(self, agent_id: str, prompt: str) -> str:
        """Generate a fallback avatar URL when mflux fails.

        Args:
            agent_id: The agent ID (for future enhancements)
            prompt: The original prompt (for future enhancements)

        Returns:
            Data URL for a simple SVG placeholder
        """
        logger.debug(f"Generating fallback avatar for agent {agent_id}")
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23FFD700' width='200' height='200'/%3E%3Ctext x='50%25' y='50%25' font-size='100' text-anchor='middle' dy='.3em'%3E🤖%3C/text%3E%3C/svg%3E"

    def _get_fallback_avatar(self) -> str:
        """Return fallback avatar URL (emoji or placeholder)."""
        logger.debug("Using fallback avatar")
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23FFD700' width='200' height='200'/%3E%3Ctext x='50%25' y='50%25' font-size='100' text-anchor='middle' dy='.3em'%3E🤖%3C/text%3E%3C/svg%3E"

    async def generate_avatar_stream(
        self,
        agent_id: str,
        prompt: str
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Generate avatar with real-time progress from mflux stderr.

        Yields progress events as mflux executes, mapping mflux's 0-100%
        progress to overall 25-100% progress range.

        Args:
            agent_id: Unique agent identifier for output filename
            prompt: Image generation prompt

        Yields:
            Progress events with type, progress %, and message:
            - {"type": "avatar_progress", "progress": 25-100, "message": "..."}
            - {"type": "avatar_complete", "progress": 100, "avatar_url": "..."}

        Example:
            async for event in generator.generate_avatar_stream("123", "cute robot"):
                print(f"{event['progress']}%: {event['message']}")
        """
        logger.info(f"Streaming avatar generation for agent {agent_id}")

        output_path = self.output_dir / f"{agent_id}.png"
        enhanced_prompt = f"{prompt}, Game Boy Color style, retro pixel art, colorful, nostalgic 90s gaming aesthetic"

        # Construct mflux command
        cmd = [
            "mflux-generate",
            "--model", "schnell",
            "--path", str(self.model_path),
            "--prompt", enhanced_prompt,
            "--steps", "2",
            "--output", str(output_path)
        ]

        try:
            # Create async subprocess
            logger.debug(f"Starting mflux subprocess: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stderr=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE
            )

            # Track last progress to prevent regression
            last_progress = 0

            # Parse stderr for progress
            if process.stderr:
                async for line_bytes in process.stderr:
                    line = line_bytes.decode('utf-8', errors='ignore')

                    # Parse progress from line
                    mflux_pct = parse_mflux_progress(line)

                    if mflux_pct is not None:
                        # Map to overall progress
                        overall_pct = map_mflux_to_overall(mflux_pct)

                        # Prevent progress regression
                        if overall_pct > last_progress:
                            last_progress = overall_pct

                            yield {
                                "type": "avatar_progress",
                                "progress": overall_pct,
                                "message": f"Drawing ({mflux_pct}%)"
                            }

            # Wait for completion
            await process.wait()

            if process.returncode == 0 and output_path.exists():
                # Success - return the generated avatar
                avatar_url = f"{self.base_url}/static/avatars/{agent_id}.png"
                logger.info(f"Avatar generated successfully: {avatar_url}")

                yield {
                    "type": "avatar_complete",
                    "progress": 100,
                    "avatar_url": avatar_url
                }
            else:
                # mflux failed, use fallback
                logger.warning(f"mflux failed (returncode={process.returncode}), using fallback")
                fallback_url = self._generate_fallback_avatar(agent_id, prompt)
                yield {
                    "type": "avatar_complete",
                    "progress": 100,
                    "avatar_url": fallback_url
                }

        except Exception as e:
            logger.error(f"Avatar streaming error: {e}", exc_info=True)
            fallback_url = self._generate_fallback_avatar(agent_id, prompt)
            yield {
                "type": "avatar_complete",
                "progress": 100,
                "avatar_url": fallback_url
            }
