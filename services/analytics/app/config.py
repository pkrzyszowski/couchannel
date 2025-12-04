from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ANALYTICS_", env_file=".env", extra="ignore")

    kafka_bootstrap: str = Field(default="redpanda:9092")
    kafka_topic: str = Field(default="booking.events")
    kafka_group_id: str = Field(default="analytics-service")
    kafka_enabled: bool = Field(default=True)
    database_url: str = Field(default="postgresql+psycopg://couchchannel:couchchannel@db:5432/couchchannel")


settings = Settings()
