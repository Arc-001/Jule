"""Shared utility helpers for Jule bot."""

from __future__ import annotations

import json
from typing import Dict, Optional, Tuple

import discord

from constants import MONTH_NAMES
from logger import get_logger

log = get_logger(__name__)


def load_json_config(file_path: str) -> Dict:
    """Load a JSON config file. Returns {} on missing or invalid file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log.warning("Could not load config from %s: %s", file_path, e)
        return {}


def format_birthday(month: int, day: int) -> str:
    """Format a birthday as e.g. 'Jan 15'. Returns 'Invalid month' for bad input."""
    if not 1 <= month <= 12:
        return "Invalid month"
    return f"{MONTH_NAMES[month - 1]} {day}"


def validate_birthday(month: int, day: int) -> Tuple[bool, Optional[str]]:
    """Return (is_valid, error_message)."""
    if not 1 <= month <= 12:
        return False, "❌ Month must be between 1 and 12!"
    if not 1 <= day <= 31:
        return False, "❌ Day must be between 1 and 31!"
    return True, None


def get_avatar_url(user: discord.abc.User) -> str:
    """Get a user's avatar URL, falling back to the default Discord avatar."""
    if getattr(user, "avatar", None):
        return user.avatar.url
    return user.default_avatar.url
