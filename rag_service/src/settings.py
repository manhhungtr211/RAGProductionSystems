from pydantic_settings import BaseSettings
from pydantic import SecretStr
from dotenv import load_dotenv
from typing import Optional


load_dotenv()


class Settings(BaseSettings):
    """Settings for the application."""

    # OpenAI API key
    API_KEY: SecretStr
    DEBUG_MODE: bool = False
    LANGFUSE_SECRET_KEY: SecretStr
    LANGFUSE_PUBLIC_KEY: SecretStr
    LANGFUSE_BASE_URL: str

    # Redis cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[SecretStr] = None
    REDIS_CACHE_THRESHOLD: float = 0.70  # cosine similarity threshold

    class Config:
        """Pydantic config."""

        env_file = "../.env"
        env_file_encoding = "utf-8"


SETTINGS = Settings()  # type: ignore
