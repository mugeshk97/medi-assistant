"""Application settings and configuration."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    MODEL_NAME: str = Field(default="gpt-4o-mini", description="OpenAI model name")

    # Server Configuration
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(
        default="*", description="Comma-separated list of allowed CORS origins"
    )

    # Google Cloud SQL Configuration
    CLOUD_SQL_CONNECTION_NAME: str | None = Field(
        default=None,
        description="Cloud SQL Instance Connection Name (project:region:instance)",
    )
    DB_USER: str | None = Field(default=None, description="Cloud SQL Database User")
    DB_PASS: str | None = Field(default=None, description="Cloud SQL Database Password")
    DB_NAME: str | None = Field(default=None, description="Cloud SQL Database Name")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate OpenAI API key is set."""
        if not v or v == "your_openai_api_key_here":
            raise ValueError(
                "OPENAI_API_KEY must be set in .env file. "
                "Get your key from https://platform.openai.com/api-keys"
            )
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
        return v

    def get_allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into a list."""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        extra = "ignore"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
