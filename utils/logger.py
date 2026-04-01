"""Structured logging for tests and CI. Use for step logging and AI-consumable output."""

import logging
import sys
from datetime import datetime

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger with standard format, suitable for CI and local runs."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


def get_interaction_logger(name: str) -> logging.Logger:
    """
    Logger that prints one line per message (no duplicate timestamp from parent format).
    Used for [TIMESTAMP] [INFO] Performed ... lines.
    """
    logger = logging.getLogger(f"orangehrm.interaction.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def log_interaction(logger: logging.Logger, action: str, element: str) -> None:
    """Log: [TIMESTAMP] [INFO] Performed {action} on {element}."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("[%s] [INFO] Performed %s on %s.", ts, action, element)
