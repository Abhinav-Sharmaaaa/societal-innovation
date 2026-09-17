from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv

# ============================================================
# Project Root
# ============================================================
# config.py is at: backend/app/core/config.py
# BASE_DIR resolves to: backend/
BASE_DIR = Path(__file__).resolve().parents[2]

# Explicitly load backend/.env — avoids picking up app/.env by mistake
load_dotenv(BASE_DIR / ".env", override=True)


class Settings(BaseSettings):
    # ========================================================
    # Application
    # ========================================================

    APP_NAME: str = "Societal Innovation Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # ========================================================
    # API
    # ========================================================

    API_V1_PREFIX: str = "/api/v1"

    # ========================================================
    # Database
    # ========================================================

    # Loaded from the root .env file
    DATABASE_URL: str

    # ========================================================
    # Security
    # ========================================================

    SECRET_KEY: str = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ALGORITHM: str = "HS256"

    # ========================================================
    # CORS
    # ========================================================

    FRONTEND_URL: str = "http://localhost:5173"

    # ========================================================
    # AI Service
    # ========================================================

    AI_SERVICE_URL: str = "http://localhost:8001"

    # ========================================================
    # File Uploads
    # ========================================================

    MAX_UPLOAD_SIZE_MB: int = 50

    # ========================================================
    # Pydantic Settings Configuration
    # ========================================================

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# ============================================================
# Settings Instance
# ============================================================

settings = Settings()