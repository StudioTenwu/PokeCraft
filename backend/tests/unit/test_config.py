"""Tests for configuration management."""
import os
import pytest
from pathlib import Path
from unittest.mock import patch


class TestConfig:
    """Test configuration loading from environment variables."""

    def test_cors_origins_from_env(self):
        """Config should load CORS origins from environment variable."""
        with patch.dict(os.environ, {"CORS_ORIGINS": "http://example.com,http://test.com"}):
            # Re-import to get fresh config
            import importlib
            from src import config
            importlib.reload(config)

            assert hasattr(config.Config, "CORS_ORIGINS")
            assert config.Config.CORS_ORIGINS == ["http://example.com", "http://test.com"]

    def test_cors_origins_default(self):
        """Config should provide default CORS origins."""
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            from src import config
            importlib.reload(config)

            assert hasattr(config.Config, "CORS_ORIGINS")
            assert "http://localhost:5173" in config.Config.CORS_ORIGINS

    def test_api_host_from_env(self):
        """Config should load API host from environment variable."""
        with patch.dict(os.environ, {"API_HOST": "127.0.0.1"}):
            import importlib
            from src import config
            importlib.reload(config)

            assert hasattr(config.Config, "API_HOST")
            assert config.Config.API_HOST == "127.0.0.1"

    def test_api_port_from_env(self):
        """Config should load API port from environment variable."""
        with patch.dict(os.environ, {"API_PORT": "9000"}):
            import importlib
            from src import config
            importlib.reload(config)

            assert hasattr(config.Config, "API_PORT")
            assert config.Config.API_PORT == 9000
            assert isinstance(config.Config.API_PORT, int)

    def test_api_base_url_from_env(self):
        """Config should load API base URL from environment variable."""
        with patch.dict(os.environ, {"API_BASE_URL": "http://api.example.com"}):
            import importlib
            from src import config
            importlib.reload(config)

            assert hasattr(config.Config, "API_BASE_URL")
            assert config.Config.API_BASE_URL == "http://api.example.com"

    def test_avatar_model_path_uses_relative_path(self):
        """Avatar model path should use relative path from project root."""
        from src.config import Config

        # Should use Path(__file__) relative resolution, not hardcoded absolute path
        # The default should end with models/schnell-3bit
        assert Config.AVATAR_MODEL_PATH.endswith("models/schnell-3bit")

    def test_avatar_model_path_respects_env_var(self):
        """Avatar model path should respect AVATAR_MODEL_PATH env var."""
        with patch.dict(os.environ, {"AVATAR_MODEL_PATH": "/custom/model/path"}):
            import importlib
            from src import config
            importlib.reload(config)

            assert config.Config.AVATAR_MODEL_PATH == "/custom/model/path"
