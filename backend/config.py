"""Configuration management for FIN-DASH backend."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # Server settings
    APP_PORT = int(os.getenv("APP_PORT", 8777))
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_SECRET = os.getenv("APP_SECRET", "change-me")

    # Localization
    CURRENCY = os.getenv("CURRENCY", "ZAR")
    LOCALE = os.getenv("LOCALE", "en-ZA")

    # Data directory
    # Default to "data" (works when running from root) or "../data" (works when running from backend)
    DATA_DIR = Path(os.getenv("DATA_DIR", "data"))

    # CORS - Allow common development ports
    # In production, set CORS_ORIGINS environment variable to specific origins
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:8080,http://localhost:8081,http://localhost:8082,http://localhost:3000",
    ).split(",")

    # Backup settings
    BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
    BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", 90))

    @classmethod
    def get_data_path(cls, filename: str) -> Path:
        """Get full path to a data file."""
        return cls.DATA_DIR / filename

    @classmethod
    def ensure_data_dir(cls):
        """Ensure data directory exists."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        (cls.DATA_DIR / "backups").mkdir(exist_ok=True)


config = Config()
