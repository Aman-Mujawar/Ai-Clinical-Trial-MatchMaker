import os
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """
    Database configuration for the Clinical Trial Matchmaker app.
    Loads from system environment variables.
    """

    APP_DB_URL: str
    COMMON_DB_URL: str | None = None  # Optional

    class Config:
        # Only used for local development; Render uses system env vars
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def database_url(self) -> str:
        """Return the effective database connection string."""
        if not self.APP_DB_URL:
            raise ValueError(
                "APP_DB_URL is not set in environment. "
                "Set it in Render dashboard or local .env file."
            )
        return self.APP_DB_URL

    @property
    def common_database_url(self) -> str | None:
        """Return the common database connection string if set."""
        return self.COMMON_DB_URL


#  Instance
db_config = DatabaseConfig()
