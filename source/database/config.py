from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """
    Database configuration
    """

    # APP_DB_URL: str = "postgresql+psycopg://postgres:postgres@localhost/agri"
    """Database URL / connection string"""

    COMMON_DB_URL: str = ""
    """Common database URL / connection string - defaults to APP_DB_URL"""