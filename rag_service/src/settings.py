from pydantic_settings import BaseSettings
from pydantic import SecretStr
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    """Settings for the application."""

    # OpenAI API key
    API_KEY: SecretStr
    DEBUG_MODE: bool = False
    LANGFUSE_SECRET_KEY: SecretStr
    LANGFUSE_PUBLIC_KEY: SecretStr
    LANGFUSE_BASE_URL: str 

    class Config:
        """Pydantic config."""

        env_file = "../.env"
        env_file_encoding = "utf-8"


SETTINGS = Settings()  # type: ignore
