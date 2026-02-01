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

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./chat_history.db", description="Database connection URL"
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")

    # Authentication (JWT)
    SECRET_KEY: str = Field(
        default="dev-secret-key-CHANGE-IN-PRODUCTION-" + "x" * 32,
        description="Secret key for JWT signing - MUST be changed in production",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=43200, description="JWT token expiry in minutes (default: 30 days)"
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate SECRET_KEY is set and secure."""
        if not v:
            raise ValueError(
                "SECRET_KEY must be set. Generate one with: "
                "python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        # Warn if using development default
        if v.startswith("dev-secret-key-CHANGE-IN-PRODUCTION"):
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                "Using development SECRET_KEY! Generate a secure key for production: "
                "python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        # Require minimum length for security
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long for security. "
                "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return v

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
