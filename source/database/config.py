import os
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """
    Database configuration for the Clinical Trial Matchmaker app.
    Loads from .env or system environment variables.
    """

    DATABASE_URL: str | None = None  # ✅ Matches your .env variable

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def database_url(self) -> str:
        """Return the effective database connection string."""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in environment.")
        return self.DATABASE_URL


# ✅ Instance
db_config = DatabaseConfig()
