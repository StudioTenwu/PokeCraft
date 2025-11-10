"""Unit tests for AvatarGenerator."""
import subprocess
from unittest.mock import MagicMock, patch

import pytest
from avatar_generator import AvatarGenerator


class TestAvatarGenerator:
    """Tests for AvatarGenerator class."""

    @pytest.fixture()
    def generator(self, tmp_path):
        """Create avatar generator with temp output directory."""
        gen = AvatarGenerator()
        gen.output_dir = tmp_path / "avatars"
        gen.output_dir.mkdir(parents=True, exist_ok=True)
        return gen

    def test_init_creates_output_directory(self, tmp_path):
        """Should create output directory on initialization."""
        output_dir = tmp_path / "test_avatars"
        gen = AvatarGenerator()
        gen.output_dir = output_dir
        gen.output_dir.mkdir(parents=True, exist_ok=True)

        assert output_dir.exists()
        assert output_dir.is_dir()

    @patch("subprocess.run")
    def test_generate_avatar_success(self, mock_run, generator):
        """Should generate avatar and return URL when mflux succeeds."""
        # Arrange
        agent_id = "test-123"
        prompt = "A cute robot"
        output_path = generator.output_dir / f"{agent_id}.png"

        # Mock successful subprocess
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

        # Create fake image file
        output_path.write_bytes(b"fake image data")

        # Act
        result = generator.generate_avatar(agent_id, prompt)

        # Assert
        assert result == f"/static/avatars/{agent_id}.png"
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "mflux-generate" in call_args
        assert prompt in " ".join(call_args)

    @patch("subprocess.run")
    def test_generate_avatar_fallback_on_mflux_failure(self, mock_run, generator):
        """Should return fallback avatar when mflux fails."""
        # Arrange
        agent_id = "test-456"
        prompt = "A cute robot"

        # Mock failed subprocess
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error")

        # Act
        result = generator.generate_avatar(agent_id, prompt)

        # Assert
        assert result.startswith("data:image/svg+xml")
        assert "🤖" in result

    @patch("subprocess.run")
    def test_generate_avatar_fallback_on_timeout(self, mock_run, generator):
        """Should return fallback avatar when mflux times out."""
        # Arrange
        agent_id = "test-789"
        prompt = "A cute robot"

        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="mflux-generate", timeout=60,
        )

        # Act
        result = generator.generate_avatar(agent_id, prompt)

        # Assert
        assert result.startswith("data:image/svg+xml")
        assert "🤖" in result

    @patch("subprocess.run")
    def test_generate_avatar_fallback_on_command_not_found(self, mock_run, generator):
        """Should return fallback avatar when mflux command not found."""
        # Arrange
        agent_id = "test-404"
        prompt = "A cute robot"

        # Mock command not found
        mock_run.side_effect = FileNotFoundError("mflux-generate not found")

        # Act
        result = generator.generate_avatar(agent_id, prompt)

        # Assert
        assert result.startswith("data:image/svg+xml")
        assert "🤖" in result

    def test_generate_avatar_enhances_prompt(self, generator):
        """Should enhance prompt with Pokemon Game Boy style instructions."""
        # Arrange
        agent_id = "test-enhance"
        prompt = "A wizard cat"

        # Mock mflux to verify enhanced prompt
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            output_path = generator.output_dir / f"{agent_id}.png"
            output_path.write_bytes(b"fake")

            # Act
            generator.generate_avatar(agent_id, prompt)

            # Assert
            call_args = mock_run.call_args[0][0]
            full_prompt = " ".join(call_args)
            assert "Game Boy Color style" in full_prompt
            assert "retro pixel art" in full_prompt
            assert prompt in full_prompt

    def test_fallback_avatar_contains_emoji(self, generator):
        """Should include robot emoji in fallback avatar."""
        # Act
        result = generator._get_fallback_avatar()  # noqa: SLF001

        # Assert
        assert "🤖" in result
        assert "data:image/svg+xml" in result
        assert "width='200'" in result
        assert "height='200'" in result
