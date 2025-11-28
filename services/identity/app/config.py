from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the identity service."""

    model_config = SettingsConfigDict(env_prefix="IDENTITY_", env_file=".env", extra="ignore")

    redis_url: str = Field(default="redis://redis:6379/0")
    oidc_issuer: str = Field(default="http://identity:8000")
    oidc_audience: str = Field(default="couchannel-api")
    token_ttl_seconds: int = Field(default=3600)


settings = Settings()
