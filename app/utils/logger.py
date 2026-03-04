"""

Structured logging using loguru.
Import `logger` everywhere instead of using print().
"""

import sys
from loguru import logger
from app.config.config import settings

logger.remove()  # Remove default handler

logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> — <level>{message}</level>",
    colorize=True,
)

logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
    format="{time} | {level} | {name}:{function} — {message}",
)

__all__ = ["logger"]
