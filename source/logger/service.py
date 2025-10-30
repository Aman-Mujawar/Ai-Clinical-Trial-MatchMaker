"""
Logger utility module
"""

import logging

from logger.config import LoggerConfig

logger_settings = LoggerConfig()

APP_LOGGER = None


def configure_logger():
    """
    Configure the logger
    """
    global APP_LOGGER
    if APP_LOGGER is not None:
        return

    def_log_level = logger_settings.LOG_LEVEL
    numeric_level = getattr(logging, def_log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    logging.basicConfig(
        level=numeric_level,
        format=logger_settings.LOG_FORMAT,
    )

    app_log_level = logger_settings.APP_LOG_LEVEL
    numeric_level = getattr(logging, app_log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    # set the log level for the app logger
    APP_LOGGER = logging.getLogger(logger_settings.APP_LOG_NAME)
    APP_LOGGER.setLevel(numeric_level)


def get_logger(name: str | None = None):
    """
    Get a (named) logger

    If a name is provided, a child logger will be returned
    else the app logger will be returned

    Args:
        name (str): The name of the logger to get

    Returns:
        logger: A logger instance
    """

    if name is None or len(name) == 0:
        return APP_LOGGER

    return APP_LOGGER.getChild(name)


configure_logger()
