import os
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """
    Database configuration for the Clinical Trial Matchmaker app.
    Loads from .env or system environment variables.
    """

    APP_DB_URL: str | None = None  # ✅ Changed from DATABASE_URL to APP_DB_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def database_url(self) -> str:
        """Return the effective database connection string."""
        if not self.APP_DB_URL:
            raise ValueError("APP_DB_URL is not set in environment.")
        return self.APP_DB_URL


# ✅ Instance
db_config = DatabaseConfig()