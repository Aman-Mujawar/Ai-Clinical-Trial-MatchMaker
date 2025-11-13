from pydantic_settings import BaseSettings
from typing import ClassVar


class DatabaseConfig(BaseSettings):
    """
    Database configuration for the Clinical Trial Matchmaker app.
    """

    APP_DB_URL: ClassVar[str] = (
        "postgresql+psycopg2://neondb_owner:"
        "npg_vAI5WPi4MjUw@ep-crimson-base-afv02jvq.c-2.us-west-2.aws.neon.tech/"
        "neondb?sslmode=require&options=endpoint%3Dep-crimson-base-afv02jvq"
    )
    """Primary database connection URL."""

    COMMON_DB_URL: str | None = None
    """Optional secondary/common database URL."""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def database_url(self) -> str:
        """Return Neon DB URL, preferring COMMON_DB_URL if provided."""
        return self.COMMON_DB_URL or self.APP_DB_URL


db_config = DatabaseConfig()
