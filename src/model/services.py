"""Service layer: wraps the Database with bot-facing business logic."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import discord

from logger import get_logger

from .model import Database

log = get_logger(__name__)


# ============================================================================
# Spam detection
# ============================================================================

class SpamDetector:
    """In-memory + persistent spam tracker for Discord messages."""

    def __init__(self, db: Database, threshold: int = 15, timeframe: int = 1200) -> None:
        self.db = db
        self.threshold = threshold
        self.timeframe = timeframe
        # {user_id: [(message_id, timestamp), ...]}
        self.message_history: Dict[int, List[Tuple[int, datetime]]] = {}

    async def track_message(self, message: discord.Message) -> bool:
        """Record a message. Returns True if user crossed the spam threshold."""
        user_id = message.author.id
        guild_id = message.guild.id if message.guild else 0

        self.db.track_message(
            user_id=user_id,
            message_id=message.id,
            channel_id=message.channel.id,
            guild_id=guild_id,
        )

        history = self.message_history.setdefault(user_id, [])
        history.append((message.id, datetime.now()))
        self._prune(user_id)

        return len(self.message_history.get(user_id, [])) >= self.threshold

    def _prune(self, user_id: int) -> None:
        """Drop in-memory entries older than `timeframe` for one user."""
        history = self.message_history.get(user_id)
        if not history:
            return

        cutoff = datetime.now() - timedelta(seconds=self.timeframe)
        fresh = [(mid, ts) for mid, ts in history if ts > cutoff]
        if fresh:
            self.message_history[user_id] = fresh
        else:
            self.message_history.pop(user_id, None)

    async def handle_spam(self, message: discord.Message) -> List[int]:
        """Delete tracked spam messages. Returns IDs of messages actually removed."""
        user_id = message.author.id
        history = self.message_history.get(user_id)
        if not history:
            return []

        message_ids = [mid for mid, _ in history]
        guild_id = message.guild.id if message.guild else 0

        self.db.log_spam_detection(
            user_id=user_id,
            guild_id=guild_id,
            message_count=len(message_ids),
            timeframe=self.timeframe,
            action="messages_deleted",
        )

        deleted_ids = await self._bulk_delete(message, message_ids)

        self.db.delete_tracked_messages(deleted_ids)
        self.message_history.pop(user_id, None)
        return deleted_ids

    async def _bulk_delete(
        self,
        message: discord.Message,
        message_ids: List[int],
    ) -> List[int]:
        """Try purge() first, then fall back to individual deletes."""
        target = set(message_ids)

        try:
            deleted = await message.channel.purge(
                limit=20,
                check=lambda m: m.id in target,
                bulk=True,
            )
            return [m.id for m in deleted]
        except discord.Forbidden:
            log.warning("No permission to bulk delete in channel %s", message.channel.id)
        except Exception as e:
            log.error("Bulk delete failed: %s", e)

        return await self._delete_individually(message, message_ids)

    @staticmethod
    async def _delete_individually(
        message: discord.Message,
        message_ids: List[int],
    ) -> List[int]:
        deleted: List[int] = []
        for mid in message_ids:
            try:
                msg = await message.channel.fetch_message(mid)
                await msg.delete()
                deleted.append(mid)
            except (discord.NotFound, discord.Forbidden):
                pass
            except Exception as e:
                log.error("Error deleting message %s: %s", mid, e)
        return deleted

    def get_user_message_count(self, user_id: int) -> int:
        return len(self.message_history.get(user_id, []))

    def is_user_tracked(self, user_id: int) -> bool:
        return user_id in self.message_history

    async def cleanup_database(self) -> None:
        self.db.cleanup_old_message_tracking(hours=1)


# ============================================================================
# Reminders
# ============================================================================

class ReminderService:
    """Thin reminder scheduler on top of the database."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def add_reminder(self, user_id: int, channel_id: int, message: str, minutes: int) -> None:
        remind_time = datetime.now() + timedelta(minutes=minutes)
        self.db.add_reminder(user_id, channel_id, message, remind_time)

    def get_due_reminders(self) -> List[Dict]:
        return self.db.get_due_reminders()

    def complete_reminder(self, reminder_id: int) -> None:
        self.db.delete_reminder(reminder_id)


# ============================================================================
# Points
# ============================================================================

class PointsService:
    """Message-count driven points system."""

    MESSAGES_PER_POINT = 10

    def __init__(self, db: Database) -> None:
        self.db = db

    def add_points(self, user_id: int, points: int = 1) -> None:
        self.db.add_points(user_id, points)

    def get_points(self, user_id: int) -> int:
        return self.db.get_user_points(user_id)

    def increment_message(self, user_id: int) -> bool:
        """Increment count, awarding a point every N messages. Returns True if awarded."""
        self.db.increment_message_count(user_id)
        count = self.db.get_message_count(user_id)
        if count and count % self.MESSAGES_PER_POINT == 0:
            self.db.add_points(user_id, 1)
            return True
        return False

    def get_leaderboard(self, limit: int = 10) -> List[Tuple[int, int]]:
        return self.db.get_leaderboard(limit)


# ============================================================================
# Birthdays
# ============================================================================

class BirthdayService:
    """Birthday storage and lookup."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def set_birthday(self, user_id: int, month: int, day: int) -> None:
        self.db.add_birthday(user_id, month, day)

    def get_birthday(self, user_id: int) -> Optional[Tuple[int, int]]:
        return self.db.get_birthday(user_id)

    def get_todays_birthdays(self) -> List[int]:
        return self.db.get_todays_birthdays()


# ============================================================================
# Music
# ============================================================================

class MusicService:
    """Music-play logging and stats."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def log_play(
        self,
        user_id: int,
        song_title: str,
        song_url: str,
        artist: Optional[str] = None,
        duration: Optional[int] = None,
        guild_id: Optional[int] = None,
    ) -> None:
        self.db.log_music_play(user_id, song_title, song_url, artist, duration, guild_id)

    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        return self.db.get_user_music_stats(user_id)

    def get_top_songs(self, user_id: int, limit: int = 10) -> List[Dict]:
        return self.db.get_user_top_songs(user_id, limit)

    def get_leaderboard(self, limit: int = 10) -> List[Tuple[int, int]]:
        return self.db.get_music_leaderboard(limit)

    def set_favorite_song(self, user_id: int, song_title: str) -> None:
        self.db.update_favorite_song(user_id, song_title)


# ============================================================================
# Games & trivia
# ============================================================================

class GameStatsService:
    """Generic game-result logging plus trivia-specific helpers."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def log_game(
        self,
        user_id: int,
        game_type: str,
        result: str,
        points_earned: int = 0,
        difficulty: Optional[str] = None,
        genre: Optional[str] = None,
        score: Optional[int] = None,
        details: Optional[str] = None,
        guild_id: Optional[int] = None,
    ) -> None:
        self.db.log_game_result(
            user_id=user_id,
            game_type=game_type,
            result=result,
            points_earned=points_earned,
            difficulty=difficulty,
            genre=genre,
            score=score,
            details=details,
            guild_id=guild_id,
        )

    def get_user_stats(self, user_id: int, game_type: Optional[str] = None) -> Dict:
        return self.db.get_user_game_stats(user_id, game_type)

    def get_leaderboard(
        self,
        game_type: str,
        stat_type: str = "wins",
        limit: int = 10,
    ) -> List[Tuple[int, int]]:
        return self.db.get_game_leaderboard(game_type, stat_type, limit)

    def log_trivia_answer(self, user_id: int, correct: bool, difficulty: str, points: int = 0) -> None:
        self.db.log_trivia_answer(user_id, correct, difficulty, points)

    def log_trivia_competition(
        self,
        user_id: int,
        correct: int,
        total: int,
        points: int,
        difficulty: str,
    ) -> None:
        self.db.log_trivia_competition(user_id, correct, total, points, difficulty)

    def get_trivia_stats(self, user_id: int) -> Optional[Dict]:
        return self.db.get_trivia_stats(user_id)

    def get_trivia_leaderboard(
        self,
        stat_type: str = "accuracy",
        limit: int = 10,
    ) -> List[Tuple[int, float]]:
        return self.db.get_trivia_leaderboard(stat_type, limit)
