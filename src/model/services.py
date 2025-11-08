"""
Service layer for bot operations
Handles spam detection and other business logic
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .model import Database
import discord


class SpamDetector:
    """Spam detection service using message tracking"""

    def __init__(self, db: Database, threshold: int = 10, timeframe: int = 20):
        """
        Initialize spam detector

        Args:
            db: Database instance
            threshold: Number of messages to trigger spam detection
            timeframe: Time window in seconds to check for spam
        """
        self.db = db
        self.threshold = threshold
        self.timeframe = timeframe
        # Track message history: {user_id: [(message_id, timestamp), ...]}
        self.message_history: Dict[int, List[tuple]] = {}

    async def track_message(self, message: discord.Message) -> bool:
        """
        Track a message and check if it's spam

        Returns:
            True if spam detected, False otherwise
        """
        user_id = message.author.id
        message_id = message.id
        timestamp = datetime.now()

        # Add to database
        self.db.track_message(
            user_id=user_id,
            message_id=message_id,
            channel_id=message.channel.id,
            guild_id=message.guild.id if message.guild else 0
        )

        # Add to in-memory tracking
        if user_id not in self.message_history:
            self.message_history[user_id] = []

        self.message_history[user_id].append((message_id, timestamp))

        # Clean old messages from memory
        self._cleanup_old_messages(user_id)

        # Check if spam threshold reached
        recent_count = len(self.message_history[user_id])

        if recent_count >= self.threshold:
            return True

        return False

    def _cleanup_old_messages(self, user_id: int):
        """Remove messages older than timeframe from memory"""
        if user_id not in self.message_history:
            return

        cutoff_time = datetime.now() - timedelta(seconds=self.timeframe)
        self.message_history[user_id] = [
            (msg_id, ts) for msg_id, ts in self.message_history[user_id]
            if ts > cutoff_time
        ]

        # Remove user entry if no recent messages
        if not self.message_history[user_id]:
            del self.message_history[user_id]

    async def handle_spam(self, message: discord.Message) -> List[int]:
        """
        Handle detected spam - delete recent messages

        Returns:
            List of deleted message IDs
        """
        user_id = message.author.id

        if user_id not in self.message_history:
            return []

        # Get message IDs to delete
        message_ids = [msg_id for msg_id, _ in self.message_history[user_id]]

        # Log spam detection
        self.db.log_spam_detection(
            user_id=user_id,
            guild_id=message.guild.id if message.guild else 0,
            message_count=len(message_ids),
            timeframe=self.timeframe,
            action="messages_deleted"
        )

        # Delete messages from Discord
        deleted_ids = []
        for msg_id in message_ids:
            try:
                msg = await message.channel.fetch_message(msg_id)
                await msg.delete()
                deleted_ids.append(msg_id)
            except discord.NotFound:
                # Message already deleted
                pass
            except discord.Forbidden:
                # No permission to delete
                pass
            except Exception as e:
                print(f"Error deleting message {msg_id}: {e}")

        # Clean up from tracking
        self.db.delete_tracked_messages(deleted_ids)
        if user_id in self.message_history:
            del self.message_history[user_id]

        return deleted_ids

    def get_user_message_count(self, user_id: int) -> int:
        """Get current message count for user in timeframe"""
        if user_id not in self.message_history:
            return 0
        return len(self.message_history[user_id])

    def is_user_tracked(self, user_id: int) -> bool:
        """Check if user is currently being tracked"""
        return user_id in self.message_history

    async def cleanup_database(self):
        """Periodic cleanup of old tracking data"""
        self.db.cleanup_old_message_tracking(hours=1)


class ReminderService:
    """Service for handling reminders"""

    def __init__(self, db: Database):
        self.db = db

    def add_reminder(self, user_id: int, channel_id: int, message: str, minutes: int):
        """Add a new reminder"""
        remind_time = datetime.now() + timedelta(minutes=minutes)
        self.db.add_reminder(user_id, channel_id, message, remind_time)

    def get_due_reminders(self) -> List[Dict]:
        """Get all due reminders"""
        return self.db.get_due_reminders()

    def complete_reminder(self, reminder_id: int):
        """Mark reminder as completed"""
        self.db.delete_reminder(reminder_id)


class PointsService:
    """Service for managing user points"""

    def __init__(self, db: Database):
        self.db = db

    def add_points(self, user_id: int, points: int = 1):
        """Add points to user"""
        self.db.add_points(user_id, points)

    def get_points(self, user_id: int) -> int:
        """Get user's points"""
        return self.db.get_user_points(user_id)

    def increment_message(self, user_id: int) -> bool:
        """
        Increment message count and award points if threshold reached

        Returns:
            True if points were awarded
        """
        self.db.increment_message_count(user_id)
        count = self.db.get_message_count(user_id)

        # Award 1 point per 10 messages
        if count % 10 == 0:
            self.db.add_points(user_id, 1)
            return True
        return False

    def get_leaderboard(self, limit: int = 10) -> List[tuple]:
        """Get top users by points"""
        return self.db.get_leaderboard(limit)


class BirthdayService:
    """Service for managing birthdays"""

    def __init__(self, db: Database):
        self.db = db

    def add_birthday(self, user_id: int, month: int, day: int):
        """Add user's birthday"""
        self.db.add_birthday(user_id, month, day)

    def get_birthday(self, user_id: int) -> Optional[tuple]:
        """Get user's birthday"""
        return self.db.get_birthday(user_id)

    def get_todays_birthdays(self) -> List[int]:
        """Get users with birthdays today"""
        return self.db.get_todays_birthdays()

