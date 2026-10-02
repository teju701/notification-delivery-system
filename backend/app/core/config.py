from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration management using Pydantic Settings.
    Reads environment variables from environment or .env file.
    """
    PROJECT_NAME: str = "Distributed Notification Delivery System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "notification_db"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            # Ensure asyncpg scheme
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: Optional[str] = None

    @property
    def get_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # Email Provider
    RESEND_API_KEY: str = "mock_key"
    DEFAULT_FROM_EMAIL: str = "onboarding@resend.dev"
    ENABLE_MOCK_EMAIL: bool = True

    # Rate Limiting Defaults
    TENANT_DEFAULT_RPS: int = 10
    PROVIDER_GLOBAL_RPS: int = 5

    # Redis Stream Names & Channels
    NOTIFICATION_STREAM: str = "notifications_stream"
    NOTIFICATION_GROUP: str = "worker_group"
    DLQ_STREAM: str = "dlq_stream"
    DELAYED_JOBS_KEY: str = "delayed_jobs"
    PUBSUB_CHANNEL: str = "notification_updates"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
