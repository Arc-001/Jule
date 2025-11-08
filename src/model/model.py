"""
Database models for Jule bot using SQLAlchemy
Provides persistent storage for all bot data
"""

from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from typing import List, Tuple, Optional, Dict
import os

Base = declarative_base()


# ============= MODELS =============

class UserPoints(Base):
    __tablename__ = 'user_points'

    user_id = Column(BigInteger, primary_key=True)
    points = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Reminder(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    remind_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Birthday(Base):
    __tablename__ = 'birthdays'

    user_id = Column(BigInteger, primary_key=True)
    birth_month = Column(Integer, nullable=False)
    birth_day = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)


class SpamLog(Base):
    __tablename__ = 'spam_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    message_count = Column(Integer, nullable=False)
    timeframe_seconds = Column(Float, nullable=False)
    action_taken = Column(String(100))
    detected_at = Column(DateTime, default=datetime.utcnow)


class MessageTracking(Base):
    __tablename__ = 'message_tracking'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class UserCache(Base):
    __tablename__ = 'user_cache'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ServerSettings(Base):
    __tablename__ = 'server_settings'

    guild_id = Column(BigInteger, primary_key=True)
    spam_threshold = Column(Integer, default=5)
    spam_timeframe = Column(Integer, default=20)
    welcome_channel_id = Column(BigInteger, nullable=True)
    default_role_id = Column(BigInteger, nullable=True)
    settings_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============= DATABASE CLASS =============

class Database:
    def __init__(self, db_path: str = "data/jule.db"):
        """Initialize database connection and create tables"""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else "data", exist_ok=True)

        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)

        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    # ============= USER POINTS =============

    def get_user_points(self, user_id: int) -> int:
        """Get points for a user"""
        session = self.get_session()
        try:
            user = session.query(UserPoints).filter_by(user_id=user_id).first()
            return user.points if user else 0
        finally:
            session.close()

    def add_points(self, user_id: int, points: int = 1):
        """Add points to a user"""
        session = self.get_session()
        try:
            user = session.query(UserPoints).filter_by(user_id=user_id).first()
            if user:
                user.points += points
                user.last_updated = datetime.utcnow()
            else:
                user = UserPoints(user_id=user_id, points=points, message_count=1)
                session.add(user)
            session.commit()
        finally:
            session.close()

    def increment_message_count(self, user_id: int):
        """Increment message count for a user"""
        session = self.get_session()
        try:
            user = session.query(UserPoints).filter_by(user_id=user_id).first()
            if user:
                user.message_count += 1
                user.last_updated = datetime.utcnow()
            else:
                user = UserPoints(user_id=user_id, message_count=1, points=0)
                session.add(user)
            session.commit()
        finally:
            session.close()

    def get_message_count(self, user_id: int) -> int:
        """Get message count for a user"""
        session = self.get_session()
        try:
            user = session.query(UserPoints).filter_by(user_id=user_id).first()
            return user.message_count if user else 0
        finally:
            session.close()

    def get_leaderboard(self, limit: int = 10) -> List[Tuple[int, int]]:
        """Get top users by points"""
        session = self.get_session()
        try:
            users = session.query(UserPoints).order_by(UserPoints.points.desc()).limit(limit).all()
            return [(user.user_id, user.points) for user in users]
        finally:
            session.close()

    # ============= REMINDERS =============

    def add_reminder(self, user_id: int, channel_id: int, message: str, remind_time: datetime):
        """Add a new reminder"""
        session = self.get_session()
        try:
            reminder = Reminder(
                user_id=user_id,
                channel_id=channel_id,
                message=message,
                remind_time=remind_time
            )
            session.add(reminder)
            session.commit()
        finally:
            session.close()

    def get_due_reminders(self) -> List[Dict]:
        """Get all reminders that are due"""
        session = self.get_session()
        try:
            now = datetime.utcnow()
            reminders = session.query(Reminder).filter(Reminder.remind_time <= now).all()
            return [{
                'id': r.id,
                'user': r.user_id,
                'channel': r.channel_id,
                'message': r.message,
                'time': r.remind_time
            } for r in reminders]
        finally:
            session.close()

    def delete_reminder(self, reminder_id: int):
        """Delete a reminder after it's been sent"""
        session = self.get_session()
        try:
            session.query(Reminder).filter_by(id=reminder_id).delete()
            session.commit()
        finally:
            session.close()

    # ============= BIRTHDAYS =============

    def add_birthday(self, user_id: int, month: int, day: int):
        """Add or update user's birthday"""
        session = self.get_session()
        try:
            birthday = session.query(Birthday).filter_by(user_id=user_id).first()
            if birthday:
                birthday.birth_month = month
                birthday.birth_day = day
            else:
                birthday = Birthday(user_id=user_id, birth_month=month, birth_day=day)
                session.add(birthday)
            session.commit()
        finally:
            session.close()

    def get_birthday(self, user_id: int) -> Optional[Tuple[int, int]]:
        """Get user's birthday"""
        session = self.get_session()
        try:
            birthday = session.query(Birthday).filter_by(user_id=user_id).first()
            return (birthday.birth_month, birthday.birth_day) if birthday else None
        finally:
            session.close()

    def get_todays_birthdays(self) -> List[int]:
        """Get all users with birthdays today"""
        session = self.get_session()
        try:
            now = datetime.now()
            birthdays = session.query(Birthday).filter_by(
                birth_month=now.month,
                birth_day=now.day
            ).all()
            return [b.user_id for b in birthdays]
        finally:
            session.close()

    # ============= SPAM DETECTION =============

    def track_message(self, user_id: int, message_id: int, channel_id: int, guild_id: int):
        """Track a message for spam detection"""
        session = self.get_session()
        try:
            msg = MessageTracking(
                user_id=user_id,
                message_id=message_id,
                channel_id=channel_id,
                guild_id=guild_id
            )
            session.add(msg)
            session.commit()
        finally:
            session.close()

    def get_recent_messages(self, user_id: int, seconds: int = 20) -> List[Dict]:
        """Get recent messages from a user within timeframe"""
        session = self.get_session()
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(seconds=seconds)

            messages = session.query(MessageTracking).filter(
                MessageTracking.user_id == user_id,
                MessageTracking.timestamp >= cutoff_time
            ).order_by(MessageTracking.timestamp.desc()).all()

            return [{
                'message_id': msg.message_id,
                'channel_id': msg.channel_id,
                'timestamp': msg.timestamp
            } for msg in messages]
        finally:
            session.close()

    def log_spam_detection(self, user_id: int, guild_id: int, message_count: int,
                          timeframe: float, action: str):
        """Log a spam detection event"""
        session = self.get_session()
        try:
            log = SpamLog(
                user_id=user_id,
                guild_id=guild_id,
                message_count=message_count,
                timeframe_seconds=timeframe,
                action_taken=action
            )
            session.add(log)
            session.commit()
        finally:
            session.close()

    def cleanup_old_message_tracking(self, hours: int = 1):
        """Clean up old message tracking data"""
        session = self.get_session()
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            session.query(MessageTracking).filter(
                MessageTracking.timestamp < cutoff_time
            ).delete()
            session.commit()
        finally:
            session.close()

    def delete_tracked_messages(self, message_ids: List[int]):
        """Delete tracked messages after they've been removed"""
        if not message_ids:
            return
        session = self.get_session()
        try:
            session.query(MessageTracking).filter(
                MessageTracking.message_id.in_(message_ids)
            ).delete(synchronize_session=False)
            session.commit()
        finally:
            session.close()

    # ============= SERVER SETTINGS =============

    def get_server_settings(self, guild_id: int) -> Dict:
        """Get server settings"""
        session = self.get_session()
        try:
            settings = session.query(ServerSettings).filter_by(guild_id=guild_id).first()

            if settings:
                return {
                    'spam_threshold': settings.spam_threshold,
                    'spam_timeframe': settings.spam_timeframe,
                    'welcome_channel_id': settings.welcome_channel_id,
                    'default_role_id': settings.default_role_id
                }
            return {
                'spam_threshold': 5,
                'spam_timeframe': 20,
                'welcome_channel_id': None,
                'default_role_id': None
            }
        finally:
            session.close()

    def update_server_settings(self, guild_id: int, **settings):
        """Update server settings"""
        valid_keys = ['spam_threshold', 'spam_timeframe', 'welcome_channel_id', 'default_role_id']
        updates = {k: v for k, v in settings.items() if k in valid_keys}

        if not updates:
            return

        session = self.get_session()
        try:
            server_settings = session.query(ServerSettings).filter_by(guild_id=guild_id).first()
            if server_settings:
                for key, value in updates.items():
                    setattr(server_settings, key, value)
                server_settings.settings_updated = datetime.utcnow()
            else:
                server_settings = ServerSettings(guild_id=guild_id, **updates)
                session.add(server_settings)
            session.commit()
        finally:
            session.close()

    # ============= USER CACHE =============

    def update_user_cache(self, user_id: int, username: str, display_name: str = None, avatar_url: str = None):
        """Update or add user to cache"""
        session = self.get_session()
        try:
            user = session.query(UserCache).filter_by(user_id=user_id).first()
            if user:
                user.username = username
                user.display_name = display_name
                user.avatar_url = avatar_url
                user.last_updated = datetime.utcnow()
            else:
                user = UserCache(
                    user_id=user_id,
                    username=username,
                    display_name=display_name,
                    avatar_url=avatar_url
                )
                session.add(user)
            session.commit()
        finally:
            session.close()

    def get_user_from_cache(self, user_id: int) -> Optional[Dict]:
        """Get user from cache"""
        session = self.get_session()
        try:
            user = session.query(UserCache).filter_by(user_id=user_id).first()
            if user:
                return {
                    'user_id': user.user_id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'avatar_url': user.avatar_url,
                    'last_updated': user.last_updated
                }
            return None
        finally:
            session.close()

    def get_users_from_cache(self, user_ids: List[int]) -> Dict[int, Dict]:
        """Get multiple users from cache"""
        session = self.get_session()
        try:
            users = session.query(UserCache).filter(UserCache.user_id.in_(user_ids)).all()
            return {
                user.user_id: {
                    'username': user.username,
                    'display_name': user.display_name,
                    'avatar_url': user.avatar_url
                }
                for user in users
            }
        finally:
            session.close()

    # ============= UTILITY =============

    def close(self):
        """Close database connection"""
        self.Session.remove()
        self.engine.dispose()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

