"""
Logger configuration
"""

from pydantic_settings import BaseSettings


class LoggerConfig(BaseSettings):
    """
    Logger configuration
    """

    LOG_LEVEL: str = "INFO"
    """Default log level"""

    LOG_FORMAT: str = "%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s"
    """Log format"""

    APP_LOG_LEVEL: str = "INFO"
    """Application log level"""

    APP_LOG_NAME: str = "agri-svc"
    """Application logger name"""