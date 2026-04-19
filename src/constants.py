"""Constants and environment configuration for Jule bot."""

from __future__ import annotations

import os
from typing import Dict, Final, List

from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# Environment
# ============================================================================

DISCORD_TOKEN: Final[str | None] = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY: Final[str | None] = os.getenv("GEMINI_API_KEY")


# ============================================================================
# File paths
# ============================================================================

DATABASE_PATH: Final[str] = "data/jule.db"
CHANNELS_CONFIG_PATH: Final[str] = "config/channels.json"
ROLES_CONFIG_PATH: Final[str] = "config/roles.json"


# ============================================================================
# Spam detection
# ============================================================================

SPAM_THRESHOLD: Final[int] = 15
SPAM_TIMEFRAME: Final[int] = 20


# ============================================================================
# Points & engagement
# ============================================================================

MESSAGES_PER_POINT: Final[int] = 10
RANDOM_REACTION_CHANCE: Final[float] = 0.05


# ============================================================================
# Limits
# ============================================================================

MIN_REMINDER_MINUTES: Final[int] = 1
MAX_REMINDER_MINUTES: Final[int] = 1440  # 24 hours

MIN_POLL_OPTIONS: Final[int] = 2
MAX_POLL_OPTIONS: Final[int] = 10

MIN_CLEAR_MESSAGES: Final[int] = 1
MAX_CLEAR_MESSAGES: Final[int] = 100

MIN_INTRO_LENGTH: Final[int] = 50


# ============================================================================
# Music
# ============================================================================

MAX_QUEUE_SIZE: Final[int] = 50
MAX_SEARCH_RESULTS: Final[int] = 5
MUSIC_INACTIVITY_TIMEOUT: Final[int] = 300  # seconds


# ============================================================================
# Fun responses
# ============================================================================

GREETINGS: Final[List[str]] = [
    "Hey there! What's up?",
    "Hello! How can I make your day better?",
    "Hi! Great to see you!",
    "Heya! Ready for some fun?",
    "Greetings! How are you doing today?",
]

ENCOURAGEMENTS: Final[List[str]] = [
    "You're doing amazing!",
    "Keep being awesome!",
    "You're a star!",
    "Love your energy!",
    "You're the best!",
]

RANDOM_FACTS: Final[List[str]] = [
    "Honey never spoils! Archaeologists have found 3000-year-old honey that's still edible.",
    "Octopuses have three hearts! Two pump blood to the gills, one to the rest of the body.",
    "Bananas are berries, but strawberries aren't!",
    "A group of flamingos is called a 'flamboyance'!",
    "The inventor of the Pringles can is now buried in one!",
    "Sea otters hold hands while sleeping so they don't drift apart!",
    "A bolt of lightning is five times hotter than the surface of the sun!",
]

COMPLIMENTS: Final[List[str]] = [
    "is absolutely wonderful!",
    "lights up the server!",
    "is incredibly kind!",
    "has amazing energy!",
    "is a true gem!",
    "makes everyone smile!",
    "is super awesome!",
]

EIGHT_BALL_RESPONSES: Final[List[str]] = [
    "Yes, absolutely!",
    "No doubt about it!",
    "Definitely yes!",
    "Maybe...",
    "Ask again later...",
    "Cannot predict now...",
    "No way!",
    "Don't count on it...",
    "Very doubtful...",
]

RANDOM_REACTIONS: Final[List[str]] = ["👍", "❤️", "✨", "🎉", "😊", "👏", "🌟"]

POLL_REACTIONS: Final[List[str]] = [
    "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣",
    "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟",
]

MONTH_NAMES: Final[List[str]] = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


# ============================================================================
# Games
# ============================================================================

RPS_CHOICES: Final[List[str]] = ["rock", "paper", "scissors"]
RPS_EMOJI_MAP: Final[Dict[str, str]] = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
RPS_WIN_POINTS: Final[int] = 2

GUESS_MIN: Final[int] = 1
GUESS_MAX: Final[int] = 100
GUESS_ATTEMPTS: Final[int] = 6
GUESS_TIMEOUT: Final[float] = 30.0  # seconds
GUESS_WIN_POINTS: Final[int] = 5
