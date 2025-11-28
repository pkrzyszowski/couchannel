from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOOKING_", env_file=".env", extra="ignore")

    kafka_bootstrap: str = Field(default="redpanda:9092")
    kafka_topic: str = Field(default="booking.events")
    kafka_enabled: bool = Field(default=True)


settings = Settings()
