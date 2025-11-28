from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the inventory service."""

    model_config = SettingsConfigDict(env_prefix="INVENTORY_", env_file=".env", extra="ignore")

    database_url: str = Field(default="postgresql+psycopg://couchchannel:couchchannel@db:5432/couchchannel")


settings = Settings()
