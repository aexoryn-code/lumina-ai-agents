import structlog
import logging
import sys
from typing import Any
from app.config import get_settings

settings = get_settings()


def setup_logging():
    """Configure structured logging"""

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.APP_ENV == "development"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.INFO if settings.APP_ENV == "production" else logging.DEBUG
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO if settings.APP_ENV == "production" else logging.DEBUG,
    )


def get_logger(name: str = None) -> Any:
    """Get a structured logger instance"""
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


# Initialize logging on import
setup_logging()
