"""Application configuration using Pydantic settings."""

"""Application configuration using Pydantic settings."""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None

    # External APIs
    FRED_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_KEY: Optional[str] = None

    # Redis (for Celery)
    REDIS_URL: Optional[str] = None

    # ML Models
    MODEL_PATH: Optional[str] = None
    SHAP_BACKGROUND_SAMPLES: Optional[int] = None

    # App
    APP_ENV: Optional[str] = "development"
    APP_HOST: Optional[str] = "0.0.0.0"
    APP_PORT: Optional[int] = 8000
    ALLOWED_ORIGINS: List[str]

    class Config:
        env_file = ".env"
        extra = "allow"  # accept extra keys without breaking



settings = Settings()
