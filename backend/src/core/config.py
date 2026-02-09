"""Environment configuration using pydantic-settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database configuration
    database_url: str

    # JWT authentication configuration
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # OpenAI configuration for AI agent
    openai_api_key: str
    openai_model: str = "gpt-4"
    agent_timeout: int = 30  # seconds
    context_window_size: int = 20  # number of messages

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
