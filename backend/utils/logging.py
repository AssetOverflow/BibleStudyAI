"""
Centralized logging configuration for the application using Loguru.
Provides a standardized, powerful, and simple way to log messages.
"""

import sys
from loguru import logger


def setup_logging(level="INFO", serialize=False):
    """
    Configures the Loguru logger for the application.

    Args:
        level (str): The minimum logging level (e.g., "INFO", "DEBUG").
        serialize (bool): If True, logs will be formatted as JSON.
    """
    logger.remove()  # Remove the default handler
    logger.add(
        sys.stdout,
        level=level.upper(),
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
        serialize=serialize,
        backtrace=True,
        diagnose=True,
    )
    logger.info("Loguru logger configured.")
