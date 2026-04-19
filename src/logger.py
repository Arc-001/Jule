"""Centralized logging for Jule bot and dashboard."""

import logging
import sys
from typing import Optional


_CONFIGURED = False

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"


def configure(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Configure root logger once. Safe to call multiple times."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format=_FORMAT,
        datefmt=_DATEFMT,
        handlers=handlers,
    )

    # Quiet noisy libs
    for noisy in ("discord", "discord.http", "discord.gateway", "werkzeug", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Auto-configures root on first call."""
    if not _CONFIGURED:
        configure()
    return logging.getLogger(name)
