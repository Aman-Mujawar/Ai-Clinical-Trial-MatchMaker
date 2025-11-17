from pydantic_settings import BaseSettings

class DatabaseConfig(BaseSettings):
    """
    Database configuration for the Clinical Trial Matchmaker app.
    Reads from environment variables (Render or .env for local development).
    """

    APP_DB_URL: str
    COMMON_DB_URL: str | None = None  # Optional

    class Config:
        env_file = ".env"  # only for local dev
        env_file_encoding = "utf-8"

    @property
    def database_url(self) -> str:
        if not self.APP_DB_URL:
            raise ValueError(
                "APP_DB_URL is not set. "
                "Set it in Render Dashboard or in your local .env file."
            )
        return self.APP_DB_URL

    @property
    def common_database_url(self) -> str | None:
        return self.COMMON_DB_URL


# ✅ Single instance
db_config = DatabaseConfig()
