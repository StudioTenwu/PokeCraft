import subprocess
from pathlib import Path

DEFAULT_MODEL_PATH = "/Users/wz/.AICraft/models/schnell-3bit"


class AvatarGenerator:
    def __init__(
        self,
        model_path: str = DEFAULT_MODEL_PATH,
    ) -> None:
        self.model_path: str = model_path
        self.output_dir: Path = Path(__file__).parent.parent / "static" / "avatars"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_avatar(self, agent_id: str, prompt: str) -> str:
        """Generate avatar using mflux and return URL path."""
        output_path = self.output_dir / f"{agent_id}.png"

        # Enhance prompt for Pokemon Trading Card hand-drawn aesthetic
        enhanced_prompt = (
            f"{prompt}, Pokemon trading card illustration, hand-drawn digital art, "
            "glossy finish, vibrant saturated colors, cute character design, "
            "centered composition, professional game art"
        )

        try:
            # Run mflux-generate command
            cmd = [
                "mflux-generate",
                "--model",
                "schnell",
                "--path",
                self.model_path,
                "--prompt",
                enhanced_prompt,
                "--steps",
                "2",
                "--output",
                str(output_path),
            ]

            print(f"Running mflux: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60, check=False,
            )

            print(f"mflux returncode: {result.returncode}")
            if result.stdout:
                print(f"mflux stdout: {result.stdout}")
            if result.stderr:
                print(f"mflux stderr: {result.stderr}")

            if result.returncode != 0:
                print(f"❌ mflux failed with return code {result.returncode}")
                return self._get_fallback_avatar()

            if output_path.exists():
                print(f"✅ Avatar created: {output_path}")
                return f"/static/avatars/{agent_id}.png"

            print(f"❌ Output file not created: {output_path}")
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
        return (
            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
            "width='200' height='200'%3E%3Crect fill='%23FFD700' width='200' "
            "height='200'/%3E%3Ctext x='50%25' y='50%25' font-size='100' "
            "text-anchor='middle' dy='.3em'%3E🤖%3C/text%3E%3C/svg%3E"
        )
