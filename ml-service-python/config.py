"""
Configuration module for the ML Prediction Engine.

Loads settings from environment variables with sensible defaults
for database connections, ML model paths, and training schedules.
"""

import os
from pathlib import Path


# Base directory of the project
BASE_DIR: Path = Path(__file__).resolve().parent


class Config:
    """Application configuration loaded from environment variables.

    Attributes:
        MYSQL_HOST: MySQL database host address.
        MYSQL_PORT: MySQL database port number.
        MYSQL_USER: MySQL database username.
        MYSQL_PASSWORD: MySQL database password.
        MYSQL_DB: MySQL database name.
        SQLALCHEMY_DATABASE_URI: SQLAlchemy connection string (auto-generated).
        MODEL_DIR: Directory path for saving/loading trained ML models.
        RETRAIN_INTERVAL: Interval in hours between automatic model retraining.
    """

    # ── Database Connection Settings ────────────────────────────────────
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "restaurant_ai")

    # Constructed SQLAlchemy connection URI
    SQLALCHEMY_DATABASE_URI: str = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # ── ML Model Settings ───────────────────────────────────────────────
    MODEL_DIR: str = os.getenv("MODEL_DIR", str(BASE_DIR / "models"))
    RETRAIN_INTERVAL: int = int(os.getenv("RETRAIN_INTERVAL", "24"))  # hours

    # ── Flask Settings ──────────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
