from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the API gateway."""

    model_config = SettingsConfigDict(env_prefix="API_", env_file=".env", extra="ignore")

    inventory_url: str = Field(default="http://inventory:8000")
    identity_url: str = Field(default="http://identity:8000")
    auth_enabled: bool = Field(default=True)
    oidc_jwks_url: str = Field(default="http://identity:8000/.well-known/jwks.json")
    oidc_issuer: str = Field(default="http://identity:8000")
    oidc_audience: str = Field(default="couchannel-api")
    oidc_algorithm: str = Field(default="RS256")


settings = Settings()
