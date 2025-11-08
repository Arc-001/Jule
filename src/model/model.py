"""
Database models for Jule bot using SQLite
Provides persistent storage for all bot data
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional, Dict
import os

class Database:
    def __init__(self, db_path: str = "data/jule.db"):
        """Initialize database connection and create tables"""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else "data", exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create all necessary tables"""
        # User points table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_points (
                user_id INTEGER PRIMARY KEY,
                points INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Reminders table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                remind_time TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Birthdays table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS birthdays (
                user_id INTEGER PRIMARY KEY,
                birth_month INTEGER NOT NULL,
                birth_day INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Spam tracking table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS spam_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                message_count INTEGER NOT NULL,
                timeframe_seconds REAL NOT NULL,
                action_taken TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Message tracking for spam detection (temporary table, cleared periodically)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Server settings table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS server_settings (
                guild_id INTEGER PRIMARY KEY,
                spam_threshold INTEGER DEFAULT 5,
                spam_timeframe INTEGER DEFAULT 20,
                welcome_channel_id INTEGER,
                default_role_id INTEGER,
                settings_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    # ============= USER POINTS =============

    def get_user_points(self, user_id: int) -> int:
        """Get points for a user"""
        self.cursor.execute("SELECT points FROM user_points WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result['points'] if result else 0

    def add_points(self, user_id: int, points: int = 1):
        """Add points to a user"""
        self.cursor.execute("""
            INSERT INTO user_points (user_id, points, message_count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                points = points + ?,
                last_updated = CURRENT_TIMESTAMP
        """, (user_id, points, points))
        self.conn.commit()

    def increment_message_count(self, user_id: int):
        """Increment message count for a user"""
        self.cursor.execute("""
            INSERT INTO user_points (user_id, message_count)
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                message_count = message_count + 1,
                last_updated = CURRENT_TIMESTAMP
        """, (user_id,))
        self.conn.commit()

    def get_message_count(self, user_id: int) -> int:
        """Get message count for a user"""
        self.cursor.execute("SELECT message_count FROM user_points WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result['message_count'] if result else 0

    def get_leaderboard(self, limit: int = 10) -> List[Tuple[int, int]]:
        """Get top users by points"""
        self.cursor.execute("""
            SELECT user_id, points
            FROM user_points
            ORDER BY points DESC
            LIMIT ?
        """, (limit,))
        return [(row['user_id'], row['points']) for row in self.cursor.fetchall()]

    # ============= REMINDERS =============

    def add_reminder(self, user_id: int, channel_id: int, message: str, remind_time: datetime):
        """Add a new reminder"""
        self.cursor.execute("""
            INSERT INTO reminders (user_id, channel_id, message, remind_time)
            VALUES (?, ?, ?, ?)
        """, (user_id, channel_id, message, remind_time))
        self.conn.commit()

    def get_due_reminders(self) -> List[Dict]:
        """Get all reminders that are due"""
        now = datetime.now()
        self.cursor.execute("""
            SELECT id, user_id, channel_id, message, remind_time
            FROM reminders
            WHERE remind_time <= ?
        """, (now,))

        reminders = []
        for row in self.cursor.fetchall():
            reminders.append({
                'id': row['id'],
                'user': row['user_id'],
                'channel': row['channel_id'],
                'message': row['message'],
                'time': datetime.fromisoformat(row['remind_time'])
            })
        return reminders

    def delete_reminder(self, reminder_id: int):
        """Delete a reminder after it's been sent"""
        self.cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        self.conn.commit()

    # ============= BIRTHDAYS =============

    def add_birthday(self, user_id: int, month: int, day: int):
        """Add or update user's birthday"""
        self.cursor.execute("""
            INSERT INTO birthdays (user_id, birth_month, birth_day)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                birth_month = ?,
                birth_day = ?
        """, (user_id, month, day, month, day))
        self.conn.commit()

    def get_birthday(self, user_id: int) -> Optional[Tuple[int, int]]:
        """Get user's birthday"""
        self.cursor.execute("""
            SELECT birth_month, birth_day
            FROM birthdays
            WHERE user_id = ?
        """, (user_id,))
        result = self.cursor.fetchone()
        return (result['birth_month'], result['birth_day']) if result else None

    def get_todays_birthdays(self) -> List[int]:
        """Get all users with birthdays today"""
        now = datetime.now()
        self.cursor.execute("""
            SELECT user_id
            FROM birthdays
            WHERE birth_month = ? AND birth_day = ?
        """, (now.month, now.day))
        return [row['user_id'] for row in self.cursor.fetchall()]

    # ============= SPAM DETECTION =============

    def track_message(self, user_id: int, message_id: int, channel_id: int, guild_id: int):
        """Track a message for spam detection"""
        self.cursor.execute("""
            INSERT INTO message_tracking (user_id, message_id, channel_id, guild_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, message_id, channel_id, guild_id))
        self.conn.commit()

    def get_recent_messages(self, user_id: int, seconds: int = 20) -> List[Dict]:
        """Get recent messages from a user within timeframe"""
        cutoff_time = datetime.now().timestamp() - seconds

        self.cursor.execute("""
            SELECT message_id, channel_id, timestamp
            FROM message_tracking
            WHERE user_id = ? 
            AND datetime(timestamp) >= datetime(?, 'unixepoch')
            ORDER BY timestamp DESC
        """, (user_id, cutoff_time))

        messages = []
        for row in self.cursor.fetchall():
            messages.append({
                'message_id': row['message_id'],
                'channel_id': row['channel_id'],
                'timestamp': row['timestamp']
            })
        return messages

    def log_spam_detection(self, user_id: int, guild_id: int, message_count: int,
                          timeframe: float, action: str):
        """Log a spam detection event"""
        self.cursor.execute("""
            INSERT INTO spam_logs (user_id, guild_id, message_count, timeframe_seconds, action_taken)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, guild_id, message_count, timeframe, action))
        self.conn.commit()

    def cleanup_old_message_tracking(self, hours: int = 1):
        """Clean up old message tracking data"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        self.cursor.execute("""
            DELETE FROM message_tracking
            WHERE datetime(timestamp) < datetime(?, 'unixepoch')
        """, (cutoff_time,))
        self.conn.commit()

    def delete_tracked_messages(self, message_ids: List[int]):
        """Delete tracked messages after they've been removed"""
        if not message_ids:
            return
        placeholders = ','.join('?' * len(message_ids))
        self.cursor.execute(f"""
            DELETE FROM message_tracking
            WHERE message_id IN ({placeholders})
        """, message_ids)
        self.conn.commit()

    # ============= SERVER SETTINGS =============

    def get_server_settings(self, guild_id: int) -> Dict:
        """Get server settings"""
        self.cursor.execute("""
            SELECT spam_threshold, spam_timeframe, welcome_channel_id, default_role_id
            FROM server_settings
            WHERE guild_id = ?
        """, (guild_id,))
        result = self.cursor.fetchone()

        if result:
            return {
                'spam_threshold': result['spam_threshold'],
                'spam_timeframe': result['spam_timeframe'],
                'welcome_channel_id': result['welcome_channel_id'],
                'default_role_id': result['default_role_id']
            }
        return {
            'spam_threshold': 5,
            'spam_timeframe': 20,
            'welcome_channel_id': None,
            'default_role_id': None
        }

    def update_server_settings(self, guild_id: int, **settings):
        """Update server settings"""
        valid_keys = ['spam_threshold', 'spam_timeframe', 'welcome_channel_id', 'default_role_id']
        updates = {k: v for k, v in settings.items() if k in valid_keys}

        if not updates:
            return

        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [guild_id]

        self.cursor.execute(f"""
            INSERT INTO server_settings (guild_id, {', '.join(updates.keys())})
            VALUES (?, {', '.join(['?'] * len(updates))})
            ON CONFLICT(guild_id) DO UPDATE SET
                {set_clause},
                settings_updated = CURRENT_TIMESTAMP
        """, [guild_id] + list(updates.values()) + list(updates.values()))
        self.conn.commit()

    # ============= UTILITY =============

    def close(self):
        """Close database connection"""
        self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

