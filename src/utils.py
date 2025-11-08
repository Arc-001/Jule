"""
Utility functions for Jule bot
"""

import json
from typing import Dict, Optional
import discord
from constants import MONTH_NAMES


def load_json_config(file_path: str) -> Dict:
    """
    Load a JSON configuration file

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON as dictionary, empty dict on error
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load config from {file_path}: {e}")
        return {}


def format_birthday(month: int, day: int) -> str:
    """
    Format birthday as string

    Args:
        month: Month number (1-12)
        day: Day number (1-31)

    Returns:
        Formatted birthday string
    """
    if not (1 <= month <= 12):
        return "Invalid month"
    return f"{MONTH_NAMES[month-1]} {day}"


def get_avatar_url(user: discord.Member) -> str:
    """
    Get user's avatar URL, falling back to default

    Args:
        user: Discord member

    Returns:
        Avatar URL string
    """
    if user.avatar:
        return user.avatar.url
    return user.default_avatar.url


def create_embed(
    title: str,
    description: str = "",
    color: discord.Color = discord.Color.blue(),
    thumbnail_url: Optional[str] = None,
    footer_text: Optional[str] = None
) -> discord.Embed:
    """
    Create a Discord embed with common settings

    Args:
        title: Embed title
        description: Embed description
        color: Embed color
        thumbnail_url: Optional thumbnail URL
        footer_text: Optional footer text

    Returns:
        Configured Discord embed
    """
    embed = discord.Embed(title=title, description=description, color=color)
    
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    if footer_text:
        embed.set_footer(text=footer_text)
    
    return embed


def validate_birthday(month: int, day: int) -> tuple[bool, Optional[str]]:
    """
    Validate birthday input

    Args:
        month: Month number
        day: Day number

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (1 <= month <= 12):
        return False, "❌ Month must be between 1 and 12!"
    
    if not (1 <= day <= 31):
        return False, "❌ Day must be between 1 and 31!"
    
    return True, None

