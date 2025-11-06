from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """
    Database configuration for the Clinical Trial Matchmaker app.
    """

    APP_DB_URL: str = "postgresql+psycopg2://postgres:1234@localhost:5432/clinical_db"
    """Primary database connection URL."""

    COMMON_DB_URL: str | None = None
    """Optional secondary/common database URL."""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def database_url(self) -> str:
        """
        Returns the effective database connection string.
        Defaults to APP_DB_URL if COMMON_DB_URL is not provided.
        """
        return self.COMMON_DB_URL or self.APP_DB_URL


#  Instantiate config for global import
db_config = DatabaseConfig()
