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
        "/Users/wz/Desktop/zPersonalProjects/AICraft/models/schnell-3bit"
    )
