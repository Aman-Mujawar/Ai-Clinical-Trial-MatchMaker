from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """
    Database configuration
    """

    APP_DB_URL: str = "postgresql://postgres:12345@localhost:5432/clinical_matchmaking"
    """Database URL / connection string"""

    COMMON_DB_URL: str = ""
    """Common database URL / connection string - defaults to APP_DB_URL"""