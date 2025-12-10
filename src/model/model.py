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
    intro_channel_id = Column(BigInteger, nullable=True)
    settings_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MusicStats(Base):
    __tablename__ = 'music_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    song_title = Column(String(500), nullable=False)
    song_url = Column(Text, nullable=False)
    artist = Column(String(255), nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    played_at = Column(DateTime, default=datetime.utcnow)
    guild_id = Column(BigInteger, nullable=True)


class UserMusicStats(Base):
    __tablename__ = 'user_music_stats'

    user_id = Column(BigInteger, primary_key=True)
    total_songs_played = Column(Integer, default=0)
    total_listening_time = Column(BigInteger, default=0)  # Total time in seconds
    favorite_song = Column(String(500), nullable=True)
    last_played_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GameStats(Base):
    __tablename__ = 'game_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    game_type = Column(String(50), nullable=False)  # 'trivia', 'rps', 'guess', 'scramble', etc.
    result = Column(String(20), nullable=False)  # 'win', 'loss', 'tie'
    points_earned = Column(Integer, default=0)
    difficulty = Column(String(20), nullable=True)  # For games with difficulty levels
    genre = Column(String(100), nullable=True)  # For trivia genre
    score = Column(Integer, nullable=True)  # For games with numeric scores
    details = Column(Text, nullable=True)  # JSON string for additional data
    played_at = Column(DateTime, default=datetime.utcnow)
    guild_id = Column(BigInteger, nullable=True)


class UserGameStats(Base):
    __tablename__ = 'user_game_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    game_type = Column(String(50), nullable=False)

    # Overall stats
    total_played = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)
    total_ties = Column(Integer, default=0)
    total_points_earned = Column(Integer, default=0)

    # Streaks
    current_win_streak = Column(Integer, default=0)
    best_win_streak = Column(Integer, default=0)

    # Averages
    average_score = Column(Float, nullable=True)

    # Best performance
    highest_score = Column(Integer, nullable=True)

    # Timestamps
    first_played = Column(DateTime, default=datetime.utcnow)
    last_played = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TriviaStats(Base):
    __tablename__ = 'trivia_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)

    # Overall trivia stats
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    total_points = Column(Integer, default=0)

    # By difficulty
    easy_correct = Column(Integer, default=0)
    easy_total = Column(Integer, default=0)
    medium_correct = Column(Integer, default=0)
    medium_total = Column(Integer, default=0)
    hard_correct = Column(Integer, default=0)
    hard_total = Column(Integer, default=0)
    expert_correct = Column(Integer, default=0)
    expert_total = Column(Integer, default=0)

    # Competition stats
    competitions_completed = Column(Integer, default=0)
    competitions_perfect = Column(Integer, default=0)
    best_competition_score = Column(Integer, default=0)

    # Streaks
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)

    # Timestamps
    last_played = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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
                    'default_role_id': settings.default_role_id,
                    'intro_channel_id': settings.intro_channel_id
                }
            return {
                'spam_threshold': 5,
                'spam_timeframe': 20,
                'welcome_channel_id': None,
                'default_role_id': None,
                'intro_channel_id': None
            }
        finally:
            session.close()

    def update_server_settings(self, guild_id: int, **settings):
        """Update server settings"""
        valid_keys = ['spam_threshold', 'spam_timeframe', 'welcome_channel_id', 'default_role_id', 'intro_channel_id']
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

    def update_user_cache(self, user_id: int, username: str, display_name: str, avatar_url: Optional[str]):
        """Update or create user cache entry"""
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

    def get_user_cache(self, user_id: int) -> Optional[Dict]:
        """Get cached user info"""
        session = self.get_session()
        try:
            user = session.query(UserCache).filter_by(user_id=user_id).first()
            if user:
                return {
                    'username': user.username,
                    'display_name': user.display_name,
                    'avatar_url': user.avatar_url,
                    'last_updated': user.last_updated
                }
            return None
        finally:
            session.close()

    # ============= MUSIC STATS =============

    def log_music_play(self, user_id: int, song_title: str, song_url: str,
                       artist: Optional[str] = None, duration: Optional[int] = None,
                       guild_id: Optional[int] = None):
        """Log a song play event"""
        session = self.get_session()
        try:
            # Add to music stats
            stat = MusicStats(
                user_id=user_id,
                song_title=song_title,
                song_url=song_url,
                artist=artist,
                duration=duration,
                guild_id=guild_id
            )
            session.add(stat)

            # Update user music stats
            user_stat = session.query(UserMusicStats).filter_by(user_id=user_id).first()
            if user_stat:
                user_stat.total_songs_played += 1
                if duration:
                    user_stat.total_listening_time += duration
                user_stat.last_played_at = datetime.utcnow()
                user_stat.last_updated = datetime.utcnow()
            else:
                user_stat = UserMusicStats(
                    user_id=user_id,
                    total_songs_played=1,
                    total_listening_time=duration if duration else 0,
                    last_played_at=datetime.utcnow()
                )
                session.add(user_stat)

            session.commit()
        finally:
            session.close()

    def get_user_music_stats(self, user_id: int) -> Optional[Dict]:
        """Get music statistics for a user"""
        session = self.get_session()
        try:
            stats = session.query(UserMusicStats).filter_by(user_id=user_id).first()
            if stats:
                return {
                    'total_songs': stats.total_songs_played,
                    'total_time': stats.total_listening_time,
                    'favorite_song': stats.favorite_song,
                    'last_played': stats.last_played_at
                }
            return None
        finally:
            session.close()

    def get_user_top_songs(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's most played songs"""
        session = self.get_session()
        try:
            from sqlalchemy import func
            results = session.query(
                MusicStats.song_title,
                MusicStats.artist,
                func.count(MusicStats.id).label('play_count')
            ).filter(
                MusicStats.user_id == user_id
            ).group_by(
                MusicStats.song_title, MusicStats.artist
            ).order_by(
                func.count(MusicStats.id).desc()
            ).limit(limit).all()

            return [{
                'title': r.song_title,
                'artist': r.artist,
                'plays': r.play_count
            } for r in results]
        finally:
            session.close()

    def get_music_leaderboard(self, limit: int = 10) -> List[Tuple[int, int]]:
        """Get top users by total songs played"""
        session = self.get_session()
        try:
            users = session.query(UserMusicStats).order_by(
                UserMusicStats.total_songs_played.desc()
            ).limit(limit).all()
            return [(user.user_id, user.total_songs_played) for user in users]
        finally:
            session.close()

    def update_favorite_song(self, user_id: int, song_title: str):
        """Update user's favorite song"""
        session = self.get_session()
        try:
            user_stat = session.query(UserMusicStats).filter_by(user_id=user_id).first()
            if user_stat:
                user_stat.favorite_song = song_title
                user_stat.last_updated = datetime.utcnow()
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

    # ============= GAME STATS =============

    def log_game_result(self, user_id: int, game_type: str, result: str,
                       points_earned: int = 0, difficulty: Optional[str] = None,
                       genre: Optional[str] = None, score: Optional[int] = None,
                       details: Optional[str] = None, guild_id: Optional[int] = None):
        """Log a game result"""
        session = self.get_session()
        try:
            # Add to game stats log
            game_stat = GameStats(
                user_id=user_id,
                game_type=game_type,
                result=result,
                points_earned=points_earned,
                difficulty=difficulty,
                genre=genre,
                score=score,
                details=details,
                guild_id=guild_id
            )
            session.add(game_stat)

            # Update user game stats
            user_game_stat = session.query(UserGameStats).filter_by(
                user_id=user_id,
                game_type=game_type
            ).first()

            if user_game_stat:
                user_game_stat.total_played += 1
                if result == 'win':
                    user_game_stat.total_wins += 1
                    user_game_stat.current_win_streak += 1
                    if user_game_stat.current_win_streak > user_game_stat.best_win_streak:
                        user_game_stat.best_win_streak = user_game_stat.current_win_streak
                elif result == 'loss':
                    user_game_stat.total_losses += 1
                    user_game_stat.current_win_streak = 0
                elif result == 'tie':
                    user_game_stat.total_ties += 1

                user_game_stat.total_points_earned += points_earned
                user_game_stat.last_played = datetime.utcnow()

                # Update score stats if provided
                if score is not None:
                    # Update average
                    total_scores = (user_game_stat.average_score or 0) * (user_game_stat.total_played - 1) + score
                    user_game_stat.average_score = total_scores / user_game_stat.total_played

                    # Update highest score
                    if user_game_stat.highest_score is None or score > user_game_stat.highest_score:
                        user_game_stat.highest_score = score
            else:
                user_game_stat = UserGameStats(
                    user_id=user_id,
                    game_type=game_type,
                    total_played=1,
                    total_wins=1 if result == 'win' else 0,
                    total_losses=1 if result == 'loss' else 0,
                    total_ties=1 if result == 'tie' else 0,
                    total_points_earned=points_earned,
                    current_win_streak=1 if result == 'win' else 0,
                    best_win_streak=1 if result == 'win' else 0,
                    average_score=float(score) if score is not None else None,
                    highest_score=score,
                    last_played=datetime.utcnow()
                )
                session.add(user_game_stat)

            session.commit()
        finally:
            session.close()

    def get_user_game_stats(self, user_id: int, game_type: Optional[str] = None) -> Dict:
        """Get game statistics for a user"""
        session = self.get_session()
        try:
            if game_type:
                stats = session.query(UserGameStats).filter_by(
                    user_id=user_id,
                    game_type=game_type
                ).first()

                if stats:
                    return {
                        'game_type': stats.game_type,
                        'total_played': stats.total_played,
                        'total_wins': stats.total_wins,
                        'total_losses': stats.total_losses,
                        'total_ties': stats.total_ties,
                        'total_points': stats.total_points_earned,
                        'win_rate': (stats.total_wins / stats.total_played * 100) if stats.total_played > 0 else 0,
                        'current_streak': stats.current_win_streak,
                        'best_streak': stats.best_win_streak,
                        'average_score': stats.average_score,
                        'highest_score': stats.highest_score,
                        'first_played': stats.first_played,
                        'last_played': stats.last_played
                    }
                return {}
            else:
                # Get all game stats for user
                all_stats = session.query(UserGameStats).filter_by(user_id=user_id).all()
                return {
                    stat.game_type: {
                        'total_played': stat.total_played,
                        'total_wins': stat.total_wins,
                        'total_losses': stat.total_losses,
                        'total_ties': stat.total_ties,
                        'total_points': stat.total_points_earned,
                        'win_rate': (stat.total_wins / stat.total_played * 100) if stat.total_played > 0 else 0,
                        'current_streak': stat.current_win_streak,
                        'best_streak': stat.best_win_streak,
                        'average_score': stat.average_score,
                        'highest_score': stat.highest_score,
                        'last_played': stat.last_played
                    }
                    for stat in all_stats
                }
        finally:
            session.close()

    def get_game_leaderboard(self, game_type: str, stat_type: str = 'wins', limit: int = 10) -> List[Tuple[int, int]]:
        """Get game leaderboard by stat type"""
        session = self.get_session()
        try:
            query = session.query(UserGameStats).filter_by(game_type=game_type)

            if stat_type == 'wins':
                query = query.order_by(UserGameStats.total_wins.desc())
            elif stat_type == 'played':
                query = query.order_by(UserGameStats.total_played.desc())
            elif stat_type == 'points':
                query = query.order_by(UserGameStats.total_points_earned.desc())
            elif stat_type == 'streak':
                query = query.order_by(UserGameStats.best_win_streak.desc())
            elif stat_type == 'score':
                query = query.order_by(UserGameStats.highest_score.desc())

            stats = query.limit(limit).all()

            if stat_type == 'wins':
                return [(stat.user_id, stat.total_wins) for stat in stats]
            elif stat_type == 'played':
                return [(stat.user_id, stat.total_played) for stat in stats]
            elif stat_type == 'points':
                return [(stat.user_id, stat.total_points_earned) for stat in stats]
            elif stat_type == 'streak':
                return [(stat.user_id, stat.best_win_streak) for stat in stats]
            elif stat_type == 'score':
                return [(stat.user_id, stat.highest_score or 0) for stat in stats]

            return []
        finally:
            session.close()

    # ============= TRIVIA STATS =============

    def log_trivia_answer(self, user_id: int, correct: bool, difficulty: str, points: int = 0):
        """Log a trivia answer"""
        session = self.get_session()
        try:
            stats = session.query(TriviaStats).filter_by(user_id=user_id).first()

            if stats:
                stats.total_questions += 1
                if correct:
                    stats.correct_answers += 1
                    stats.current_streak += 1
                    if stats.current_streak > stats.best_streak:
                        stats.best_streak = stats.current_streak
                else:
                    stats.wrong_answers += 1
                    stats.current_streak = 0

                stats.total_points += points

                # Update difficulty-specific stats
                if difficulty == 'easy':
                    stats.easy_total += 1
                    if correct:
                        stats.easy_correct += 1
                elif difficulty == 'medium':
                    stats.medium_total += 1
                    if correct:
                        stats.medium_correct += 1
                elif difficulty == 'hard':
                    stats.hard_total += 1
                    if correct:
                        stats.hard_correct += 1
                elif difficulty == 'expert':
                    stats.expert_total += 1
                    if correct:
                        stats.expert_correct += 1

                stats.last_played = datetime.utcnow()
                stats.last_updated = datetime.utcnow()
            else:
                stats = TriviaStats(
                    user_id=user_id,
                    total_questions=1,
                    correct_answers=1 if correct else 0,
                    wrong_answers=0 if correct else 1,
                    total_points=points,
                    current_streak=1 if correct else 0,
                    best_streak=1 if correct else 0,
                    last_played=datetime.utcnow()
                )

                # Set difficulty-specific stats
                if difficulty == 'easy':
                    stats.easy_total = 1
                    stats.easy_correct = 1 if correct else 0
                elif difficulty == 'medium':
                    stats.medium_total = 1
                    stats.medium_correct = 1 if correct else 0
                elif difficulty == 'hard':
                    stats.hard_total = 1
                    stats.hard_correct = 1 if correct else 0
                elif difficulty == 'expert':
                    stats.expert_total = 1
                    stats.expert_correct = 1 if correct else 0

                session.add(stats)

            session.commit()
        finally:
            session.close()

    def log_trivia_competition(self, user_id: int, correct: int, total: int,
                               points: int, difficulty: str):
        """Log a completed trivia competition"""
        session = self.get_session()
        try:
            stats = session.query(TriviaStats).filter_by(user_id=user_id).first()

            if stats:
                stats.competitions_completed += 1
                if correct == total:
                    stats.competitions_perfect += 1
                if points > stats.best_competition_score:
                    stats.best_competition_score = points
                stats.last_updated = datetime.utcnow()
            else:
                stats = TriviaStats(
                    user_id=user_id,
                    competitions_completed=1,
                    competitions_perfect=1 if correct == total else 0,
                    best_competition_score=points
                )
                session.add(stats)

            session.commit()
        finally:
            session.close()

    def get_trivia_stats(self, user_id: int) -> Optional[Dict]:
        """Get trivia statistics for a user"""
        session = self.get_session()
        try:
            stats = session.query(TriviaStats).filter_by(user_id=user_id).first()

            if stats:
                return {
                    'total_questions': stats.total_questions,
                    'correct_answers': stats.correct_answers,
                    'wrong_answers': stats.wrong_answers,
                    'accuracy': (stats.correct_answers / stats.total_questions * 100) if stats.total_questions > 0 else 0,
                    'total_points': stats.total_points,
                    'easy_accuracy': (stats.easy_correct / stats.easy_total * 100) if stats.easy_total > 0 else 0,
                    'medium_accuracy': (stats.medium_correct / stats.medium_total * 100) if stats.medium_total > 0 else 0,
                    'hard_accuracy': (stats.hard_correct / stats.hard_total * 100) if stats.hard_total > 0 else 0,
                    'expert_accuracy': (stats.expert_correct / stats.expert_total * 100) if stats.expert_total > 0 else 0,
                    'competitions_completed': stats.competitions_completed,
                    'competitions_perfect': stats.competitions_perfect,
                    'best_competition_score': stats.best_competition_score,
                    'current_streak': stats.current_streak,
                    'best_streak': stats.best_streak,
                    'last_played': stats.last_played
                }
            return None
        finally:
            session.close()

    def get_trivia_leaderboard(self, stat_type: str = 'accuracy', limit: int = 10) -> List[Tuple[int, float]]:
        """Get trivia leaderboard"""
        session = self.get_session()
        try:
            stats = session.query(TriviaStats).filter(TriviaStats.total_questions > 0).all()

            if stat_type == 'accuracy':
                # Calculate accuracy and sort
                leaderboard = [(s.user_id, s.correct_answers / s.total_questions * 100)
                              for s in stats if s.total_questions > 0]
                leaderboard.sort(key=lambda x: x[1], reverse=True)
            elif stat_type == 'points':
                leaderboard = [(s.user_id, s.total_points) for s in stats]
                leaderboard.sort(key=lambda x: x[1], reverse=True)
            elif stat_type == 'streak':
                leaderboard = [(s.user_id, s.best_streak) for s in stats]
                leaderboard.sort(key=lambda x: x[1], reverse=True)
            elif stat_type == 'competitions':
                leaderboard = [(s.user_id, s.competitions_completed) for s in stats]
                leaderboard.sort(key=lambda x: x[1], reverse=True)
            else:
                leaderboard = []

            return leaderboard[:limit]
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

