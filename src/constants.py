"""
Constants and configuration for Jule bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============= ENVIRONMENT VARIABLES =============
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ============= CHANNEL IDS =============
GREET_CHANNEL_ID = 1436379982015365251

# ============= ROLE IDS =============
DEFAULT_ROLE_ID = 1316483824854634586

# ============= FILE PATHS =============
DATABASE_PATH = "data/jule.db"
CHANNELS_CONFIG_PATH = "config/channels.json"
ROLES_CONFIG_PATH = "config/roles.json"

# ============= SPAM DETECTION =============
SPAM_THRESHOLD = 15
SPAM_TIMEFRAME = 20

# ============= POINTS SYSTEM =============
MESSAGES_PER_POINT = 10  # Award 1 point per 10 messages
RANDOM_REACTION_CHANCE = 0.05  # 5% chance of random reaction

# ============= REMINDER LIMITS =============
MIN_REMINDER_MINUTES = 1
MAX_REMINDER_MINUTES = 1440  # 24 hours

# ============= POLL LIMITS =============
MIN_POLL_OPTIONS = 2
MAX_POLL_OPTIONS = 10

# ============= ADMIN LIMITS =============
MIN_CLEAR_MESSAGES = 1
MAX_CLEAR_MESSAGES = 100

# ============= INTRO CHANNEL =============
MIN_INTRO_LENGTH = 50  # Minimum characters for intro to trigger role assignment

# ============= FUN RESPONSES =============
GREETINGS = [
    "Hey there!  What's up?",
    "Hello! How can I make your day better?",
    "Hi! Great to see you!",
    "Heya! Ready for some fun?",
    "Greetings! How are you doing today?"
]

ENCOURAGEMENTS = [
    "You're doing amazing! ",
    "Keep being awesome! ",
    "You're a star! ",
    "Love your energy! ",
    "You're the best! "
]

RANDOM_FACTS = [
    "Honey never spoils! Archaeologists have found 3000-year-old honey that's still edible.",
    "Octopuses have three hearts! Two pump blood to the gills, one to the rest of the body.",
    "Bananas are berries, but strawberries aren't! ",
    "A group of flamingos is called a 'flamboyance'! ",
    "The inventor of the Pringles can is now buried in one!",
    "Sea otters hold hands while sleeping so they don't drift apart! ",
    "A bolt of lightning is five times hotter than the surface of the sun! "
]

COMPLIMENTS = [
    "is absolutely wonderful! ",
    "lights up the server! ",
    "is incredibly kind! ",
    "has amazing energy! ",
    "is a true gem! ",
    "makes everyone smile! ",
    "is super awesome! "
]

EIGHT_BALL_RESPONSES = [
    "Yes, absolutely! ",
    "No doubt about it! ",
    "Definitely yes! ",
    "Maybe... ",
    "Ask again later... ",
    "Cannot predict now... ",
    "No way! ",
    "Don't count on it... ",
    "Very doubtful... "
]

RANDOM_REACTIONS = ["👍", "❤️", "✨", "🎉", "😊", "👏", "🌟"]

POLL_REACTIONS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ============= GAME SETTINGS =============
RPS_CHOICES = ["rock", "paper", "scissors"]
RPS_EMOJI_MAP = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
RPS_WIN_POINTS = 2

GUESS_MIN = 1
GUESS_MAX = 100
GUESS_ATTEMPTS = 6
GUESS_TIMEOUT = 30.0  # seconds
GUESS_WIN_POINTS = 5

