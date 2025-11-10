import subprocess
import os
import re
from pathlib import Path
from typing import Generator

class AvatarGenerator:
    def __init__(self, model_path: str = "/Users/wz/.AICraft/models/schnell-3bit"):
        self.model_path = model_path
        self.output_dir = Path(__file__).parent.parent / "static" / "avatars"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_avatar(self, agent_id: str, prompt: str) -> str:
        """Generate avatar using mflux and return URL path."""
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

            print(f"Running mflux: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"mflux error: {result.stderr}")
                return self._get_fallback_avatar()

            if output_path.exists():
                return f"/static/avatars/{agent_id}.png"
            else:
                print(f"Output file not created: {output_path}")
                return self._get_fallback_avatar()

        except subprocess.TimeoutExpired:
            print("mflux generation timeout")
            return self._get_fallback_avatar()
        except FileNotFoundError:
            print("mflux-generate command not found")
            return self._get_fallback_avatar()
        except Exception as e:
            print(f"Avatar generation error: {e}")
            return self._get_fallback_avatar()

    def _get_fallback_avatar(self) -> str:
        """Return fallback avatar URL (emoji or placeholder)."""
        return "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23FFD700' width='200' height='200'/%3E%3Ctext x='50%25' y='50%25' font-size='100' text-anchor='middle' dy='.3em'%3E🤖%3C/text%3E%3C/svg%3E"

    def generate_avatar_stream(self, agent_id: str, prompt: str) -> Generator[dict, None, None]:
        """
        Generate avatar with real-time progress streaming.

        Yields progress updates as dicts:
        - {"type": "progress", "step": int, "total": int, "percent": int, "message": str}
        - {"type": "complete", "avatar_url": str}  # Final yield with avatar URL
        """
        output_path = self.output_dir / f"{agent_id}.png"
        enhanced_prompt = f"{prompt}, Game Boy Color style, retro pixel art, colorful, nostalgic 90s gaming aesthetic"

        try:
            cmd = [
                "mflux-generate",
                "--model", "schnell",
                "--path", self.model_path,
                "--prompt", enhanced_prompt,
                "--steps", "2",
                "--output", str(output_path)
            ]

            print(f"Running mflux: {' '.join(cmd)}")

            # Use Popen for real-time output streaming
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1  # Line-buffered
            )

            # Regex to parse tqdm progress: "50%|█████     | 1/2 [00:14<00:14, 14.45s/it]"
            progress_pattern = re.compile(r'(\d+)%\|[^|]*\|\s*(\d+)/(\d+)')

            try:
                # Read output line by line
                for line in process.stdout:
                    print(f"mflux output: {line.strip()}")

                    # Try to parse progress
                    match = progress_pattern.search(line)
                    if match:
                        percent = int(match.group(1))
                        current_step = int(match.group(2))
                        total_steps = int(match.group(3))

                        yield {
                            "type": "progress",
                            "step": current_step,
                            "total": total_steps,
                            "percent": percent,
                            "message": f"Generating avatar... Step {current_step}/{total_steps}"
                        }

                # Wait for process to complete
                process.wait(timeout=60)

                if process.returncode != 0:
                    print(f"mflux failed with return code {process.returncode}")
                    yield {"type": "complete", "avatar_url": self._get_fallback_avatar()}
                    return

                if output_path.exists():
                    yield {"type": "complete", "avatar_url": f"/static/avatars/{agent_id}.png"}
                else:
                    print(f"Output file not created: {output_path}")
                    yield {"type": "complete", "avatar_url": self._get_fallback_avatar()}

            except subprocess.TimeoutExpired:
                process.kill()
                print("mflux generation timeout")
                yield {"type": "complete", "avatar_url": self._get_fallback_avatar()}
                return

        except FileNotFoundError:
            print("mflux-generate command not found")
            yield {"type": "complete", "avatar_url": self._get_fallback_avatar()}
        except Exception as e:
            print(f"Avatar generation error: {e}")
            yield {"type": "complete", "avatar_url": self._get_fallback_avatar()}
