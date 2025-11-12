"""Configuration management for AICraft."""
import os
from pathlib import Path


class Config:
    """Application configuration loaded from environment variables."""

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = Path(os.getenv("LOG_DIR", str(Path(__file__).parent.parent / "logs")))
    LOG_FORMAT = os.getenv("LOG_FORMAT", "text")  # 'text' or 'json'

    # Database
    DB_PATH = Path(os.getenv("DB_PATH", str(Path(__file__).parent.parent / "agents.db")))

    # Avatar Generation
    AVATAR_MODEL_PATH = os.getenv(
        "AVATAR_MODEL_PATH",
        str(Path.home() / ".AICraft" / "models" / "schnell-3bit")
    )

    # CORS Configuration
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # Server Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

    # Claude API Key (Required for agent deployment)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
