"""SQLAlchemy models and database access layer for Jule bot."""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Dict, Iterator, List, Optional, Tuple

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker

Base = declarative_base()


# ============================================================================
# Models
# ============================================================================

class UserPoints(Base):
    __tablename__ = "user_points"

    user_id = Column(BigInteger, primary_key=True)
    points = Column(Integer, default=0, nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_user_points_points", "points"),
    )


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    remind_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_reminders_remind_time", "remind_time"),
        Index("ix_reminders_user_id", "user_id"),
    )


class Birthday(Base):
    __tablename__ = "birthdays"

    user_id = Column(BigInteger, primary_key=True)
    birth_month = Column(Integer, nullable=False)
    birth_day = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_birthdays_month_day", "birth_month", "birth_day"),
    )


class SpamLog(Base):
    __tablename__ = "spam_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    message_count = Column(Integer, nullable=False)
    timeframe_seconds = Column(Float, nullable=False)
    action_taken = Column(String(100))
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_spam_logs_detected_at", "detected_at"),
        Index("ix_spam_logs_user_id", "user_id"),
    )


class MessageTracking(Base):
    __tablename__ = "message_tracking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_message_tracking_user_ts", "user_id", "timestamp"),
        Index("ix_message_tracking_timestamp", "timestamp"),
        Index("ix_message_tracking_message_id", "message_id"),
    )


class UserCache(Base):
    __tablename__ = "user_cache"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ServerSettings(Base):
    __tablename__ = "server_settings"

    guild_id = Column(BigInteger, primary_key=True)
    spam_threshold = Column(Integer, default=5, nullable=False)
    spam_timeframe = Column(Integer, default=20, nullable=False)
    welcome_channel_id = Column(BigInteger, nullable=True)
    default_role_id = Column(BigInteger, nullable=True)
    intro_channel_id = Column(BigInteger, nullable=True)
    settings_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class MusicStats(Base):
    __tablename__ = "music_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    song_title = Column(String(500), nullable=False)
    song_url = Column(Text, nullable=False)
    artist = Column(String(255), nullable=True)
    duration = Column(Integer, nullable=True)
    played_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    guild_id = Column(BigInteger, nullable=True)

    __table_args__ = (
        Index("ix_music_stats_user_id", "user_id"),
        Index("ix_music_stats_played_at", "played_at"),
    )


class UserMusicStats(Base):
    __tablename__ = "user_music_stats"

    user_id = Column(BigInteger, primary_key=True)
    total_songs_played = Column(Integer, default=0, nullable=False)
    total_listening_time = Column(BigInteger, default=0, nullable=False)
    favorite_song = Column(String(500), nullable=True)
    last_played_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class GameStats(Base):
    __tablename__ = "game_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    game_type = Column(String(50), nullable=False)
    result = Column(String(20), nullable=False)
    points_earned = Column(Integer, default=0, nullable=False)
    difficulty = Column(String(20), nullable=True)
    genre = Column(String(100), nullable=True)
    score = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    played_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    guild_id = Column(BigInteger, nullable=True)

    __table_args__ = (
        Index("ix_game_stats_user_id", "user_id"),
        Index("ix_game_stats_game_type", "game_type"),
        Index("ix_game_stats_played_at", "played_at"),
    )


class UserGameStats(Base):
    __tablename__ = "user_game_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    game_type = Column(String(50), nullable=False)

    total_played = Column(Integer, default=0, nullable=False)
    total_wins = Column(Integer, default=0, nullable=False)
    total_losses = Column(Integer, default=0, nullable=False)
    total_ties = Column(Integer, default=0, nullable=False)
    total_points_earned = Column(Integer, default=0, nullable=False)

    current_win_streak = Column(Integer, default=0, nullable=False)
    best_win_streak = Column(Integer, default=0, nullable=False)

    average_score = Column(Float, nullable=True)
    highest_score = Column(Integer, nullable=True)

    first_played = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_played = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "game_type", name="uq_user_game_stats_user_game"),
        Index("ix_user_game_stats_game_type", "game_type"),
    )


class TriviaStats(Base):
    __tablename__ = "trivia_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, unique=True)

    total_questions = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    wrong_answers = Column(Integer, default=0, nullable=False)
    total_points = Column(Integer, default=0, nullable=False)

    easy_correct = Column(Integer, default=0, nullable=False)
    easy_total = Column(Integer, default=0, nullable=False)
    medium_correct = Column(Integer, default=0, nullable=False)
    medium_total = Column(Integer, default=0, nullable=False)
    hard_correct = Column(Integer, default=0, nullable=False)
    hard_total = Column(Integer, default=0, nullable=False)
    expert_correct = Column(Integer, default=0, nullable=False)
    expert_total = Column(Integer, default=0, nullable=False)

    competitions_completed = Column(Integer, default=0, nullable=False)
    competitions_perfect = Column(Integer, default=0, nullable=False)
    best_competition_score = Column(Integer, default=0, nullable=False)

    current_streak = Column(Integer, default=0, nullable=False)
    best_streak = Column(Integer, default=0, nullable=False)

    last_played = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# ============================================================================
# Constants
# ============================================================================

_DIFFICULTY_FIELDS = {
    "easy": ("easy_total", "easy_correct"),
    "medium": ("medium_total", "medium_correct"),
    "hard": ("hard_total", "hard_correct"),
    "expert": ("expert_total", "expert_correct"),
}

_DEFAULT_SERVER_SETTINGS = {
    "spam_threshold": 5,
    "spam_timeframe": 20,
    "welcome_channel_id": None,
    "default_role_id": None,
    "intro_channel_id": None,
}

_VALID_SERVER_SETTING_KEYS = frozenset(_DEFAULT_SERVER_SETTINGS.keys())


# ============================================================================
# Database
# ============================================================================

class Database:
    """Thin persistence layer wrapping SQLAlchemy sessions."""

    def __init__(self, db_path: str = "data/jule.db") -> None:
        data_dir = os.path.dirname(db_path) or "data"
        os.makedirs(data_dir, exist_ok=True)

        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)
        Base.metadata.create_all(self.engine)

        self._session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.Session = scoped_session(self._session_factory)

    # ------------------------------------------------------------------ session

    def get_session(self) -> Session:
        """Return a raw scoped session. Prefer `session_scope` for new code."""
        return self.Session()

    @contextmanager
    def session_scope(self, commit: bool = True) -> Iterator[Session]:
        """Context manager that yields a session, commits on success, rolls back on error."""
        session = self.Session()
        try:
            yield session
            if commit:
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        self.Session.remove()
        self.engine.dispose()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # ------------------------------------------------------------- user points

    def get_user_points(self, user_id: int) -> int:
        with self.session_scope(commit=False) as s:
            row = s.query(UserPoints).filter_by(user_id=user_id).first()
            return row.points if row else 0

    def add_points(self, user_id: int, points: int = 1) -> None:
        with self.session_scope() as s:
            row = s.query(UserPoints).filter_by(user_id=user_id).first()
            if row:
                row.points += points
            else:
                s.add(UserPoints(user_id=user_id, points=points, message_count=1))

    def increment_message_count(self, user_id: int) -> None:
        with self.session_scope() as s:
            row = s.query(UserPoints).filter_by(user_id=user_id).first()
            if row:
                row.message_count += 1
            else:
                s.add(UserPoints(user_id=user_id, points=0, message_count=1))

    def get_message_count(self, user_id: int) -> int:
        with self.session_scope(commit=False) as s:
            row = s.query(UserPoints).filter_by(user_id=user_id).first()
            return row.message_count if row else 0

    def get_leaderboard(self, limit: int = 10) -> List[Tuple[int, int]]:
        with self.session_scope(commit=False) as s:
            rows = s.query(UserPoints).order_by(UserPoints.points.desc()).limit(limit).all()
            return [(r.user_id, r.points) for r in rows]

    # --------------------------------------------------------------- reminders

    def add_reminder(self, user_id: int, channel_id: int, message: str, remind_time: datetime) -> None:
        with self.session_scope() as s:
            s.add(Reminder(
                user_id=user_id,
                channel_id=channel_id,
                message=message,
                remind_time=remind_time,
            ))

    def get_due_reminders(self) -> List[Dict]:
        with self.session_scope(commit=False) as s:
            rows = s.query(Reminder).filter(Reminder.remind_time <= datetime.utcnow()).all()
            return [{
                "id": r.id,
                "user": r.user_id,
                "channel": r.channel_id,
                "message": r.message,
                "time": r.remind_time,
            } for r in rows]

    def delete_reminder(self, reminder_id: int) -> None:
        with self.session_scope() as s:
            s.query(Reminder).filter_by(id=reminder_id).delete()

    # --------------------------------------------------------------- birthdays

    def add_birthday(self, user_id: int, month: int, day: int) -> None:
        with self.session_scope() as s:
            row = s.query(Birthday).filter_by(user_id=user_id).first()
            if row:
                row.birth_month = month
                row.birth_day = day
            else:
                s.add(Birthday(user_id=user_id, birth_month=month, birth_day=day))

    def get_birthday(self, user_id: int) -> Optional[Tuple[int, int]]:
        with self.session_scope(commit=False) as s:
            row = s.query(Birthday).filter_by(user_id=user_id).first()
            return (row.birth_month, row.birth_day) if row else None

    def get_todays_birthdays(self) -> List[int]:
        now = datetime.utcnow()
        with self.session_scope(commit=False) as s:
            rows = s.query(Birthday).filter_by(birth_month=now.month, birth_day=now.day).all()
            return [r.user_id for r in rows]

    # ---------------------------------------------------------- spam detection

    def track_message(self, user_id: int, message_id: int, channel_id: int, guild_id: int) -> None:
        with self.session_scope() as s:
            s.add(MessageTracking(
                user_id=user_id,
                message_id=message_id,
                channel_id=channel_id,
                guild_id=guild_id,
            ))

    def get_recent_messages(self, user_id: int, seconds: int = 20) -> List[Dict]:
        cutoff = datetime.utcnow() - timedelta(seconds=seconds)
        with self.session_scope(commit=False) as s:
            rows = (
                s.query(MessageTracking)
                .filter(MessageTracking.user_id == user_id, MessageTracking.timestamp >= cutoff)
                .order_by(MessageTracking.timestamp.desc())
                .all()
            )
            return [{
                "message_id": r.message_id,
                "channel_id": r.channel_id,
                "timestamp": r.timestamp,
            } for r in rows]

    def log_spam_detection(
        self,
        user_id: int,
        guild_id: int,
        message_count: int,
        timeframe: float,
        action: str,
    ) -> None:
        with self.session_scope() as s:
            s.add(SpamLog(
                user_id=user_id,
                guild_id=guild_id,
                message_count=message_count,
                timeframe_seconds=timeframe,
                action_taken=action,
            ))

    def cleanup_old_message_tracking(self, hours: int = 1) -> None:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        with self.session_scope() as s:
            s.query(MessageTracking).filter(MessageTracking.timestamp < cutoff).delete()

    def delete_tracked_messages(self, message_ids: List[int]) -> None:
        if not message_ids:
            return
        with self.session_scope() as s:
            s.query(MessageTracking).filter(
                MessageTracking.message_id.in_(message_ids)
            ).delete(synchronize_session=False)

    # ---------------------------------------------------------- server settings

    def get_server_settings(self, guild_id: int) -> Dict:
        with self.session_scope(commit=False) as s:
            row = s.query(ServerSettings).filter_by(guild_id=guild_id).first()
            if not row:
                return dict(_DEFAULT_SERVER_SETTINGS)
            return {
                "spam_threshold": row.spam_threshold,
                "spam_timeframe": row.spam_timeframe,
                "welcome_channel_id": row.welcome_channel_id,
                "default_role_id": row.default_role_id,
                "intro_channel_id": row.intro_channel_id,
            }

    def update_server_settings(self, guild_id: int, **settings) -> None:
        updates = {k: v for k, v in settings.items() if k in _VALID_SERVER_SETTING_KEYS}
        if not updates:
            return
        with self.session_scope() as s:
            row = s.query(ServerSettings).filter_by(guild_id=guild_id).first()
            if row:
                for key, value in updates.items():
                    setattr(row, key, value)
            else:
                s.add(ServerSettings(guild_id=guild_id, **updates))

    # -------------------------------------------------------------- user cache

    def update_user_cache(
        self,
        user_id: int,
        username: str,
        display_name: Optional[str],
        avatar_url: Optional[str],
    ) -> None:
        with self.session_scope() as s:
            row = s.query(UserCache).filter_by(user_id=user_id).first()
            if row:
                row.username = username
                row.display_name = display_name
                row.avatar_url = avatar_url
            else:
                s.add(UserCache(
                    user_id=user_id,
                    username=username,
                    display_name=display_name,
                    avatar_url=avatar_url,
                ))

    def get_user_cache(self, user_id: int) -> Optional[Dict]:
        with self.session_scope(commit=False) as s:
            row = s.query(UserCache).filter_by(user_id=user_id).first()
            if not row:
                return None
            return {
                "user_id": row.user_id,
                "username": row.username,
                "display_name": row.display_name,
                "avatar_url": row.avatar_url,
                "last_updated": row.last_updated,
            }

    # Back-compat alias for older callers.
    get_user_from_cache = get_user_cache

    def get_users_from_cache(self, user_ids: List[int]) -> Dict[int, Dict]:
        if not user_ids:
            return {}
        with self.session_scope(commit=False) as s:
            rows = s.query(UserCache).filter(UserCache.user_id.in_(user_ids)).all()
            return {
                r.user_id: {
                    "username": r.username,
                    "display_name": r.display_name,
                    "avatar_url": r.avatar_url,
                }
                for r in rows
            }

    # ------------------------------------------------------------- music stats

    def log_music_play(
        self,
        user_id: int,
        song_title: str,
        song_url: str,
        artist: Optional[str] = None,
        duration: Optional[int] = None,
        guild_id: Optional[int] = None,
    ) -> None:
        with self.session_scope() as s:
            s.add(MusicStats(
                user_id=user_id,
                song_title=song_title,
                song_url=song_url,
                artist=artist,
                duration=duration,
                guild_id=guild_id,
            ))

            agg = s.query(UserMusicStats).filter_by(user_id=user_id).first()
            now = datetime.utcnow()
            if agg:
                agg.total_songs_played += 1
                if duration:
                    agg.total_listening_time += duration
                agg.last_played_at = now
            else:
                s.add(UserMusicStats(
                    user_id=user_id,
                    total_songs_played=1,
                    total_listening_time=duration or 0,
                    last_played_at=now,
                ))

    def get_user_music_stats(self, user_id: int) -> Optional[Dict]:
        with self.session_scope(commit=False) as s:
            row = s.query(UserMusicStats).filter_by(user_id=user_id).first()
            if not row:
                return None
            return {
                "total_songs": row.total_songs_played,
                "total_time": row.total_listening_time,
                "favorite_song": row.favorite_song,
                "last_played": row.last_played_at,
            }

    def get_user_top_songs(self, user_id: int, limit: int = 10) -> List[Dict]:
        with self.session_scope(commit=False) as s:
            rows = (
                s.query(
                    MusicStats.song_title,
                    MusicStats.artist,
                    func.count(MusicStats.id).label("play_count"),
                )
                .filter(MusicStats.user_id == user_id)
                .group_by(MusicStats.song_title, MusicStats.artist)
                .order_by(func.count(MusicStats.id).desc())
                .limit(limit)
                .all()
            )
            return [
                {"title": r.song_title, "artist": r.artist, "plays": r.play_count}
                for r in rows
            ]

    def get_music_leaderboard(self, limit: int = 10) -> List[Tuple[int, int]]:
        with self.session_scope(commit=False) as s:
            rows = (
                s.query(UserMusicStats)
                .order_by(UserMusicStats.total_songs_played.desc())
                .limit(limit)
                .all()
            )
            return [(r.user_id, r.total_songs_played) for r in rows]

    def update_favorite_song(self, user_id: int, song_title: str) -> None:
        with self.session_scope() as s:
            row = s.query(UserMusicStats).filter_by(user_id=user_id).first()
            if row:
                row.favorite_song = song_title

    # -------------------------------------------------------------- game stats

    def log_game_result(
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
        with self.session_scope() as s:
            s.add(GameStats(
                user_id=user_id,
                game_type=game_type,
                result=result,
                points_earned=points_earned,
                difficulty=difficulty,
                genre=genre,
                score=score,
                details=details,
                guild_id=guild_id,
            ))

            agg = (
                s.query(UserGameStats)
                .filter_by(user_id=user_id, game_type=game_type)
                .first()
            )
            now = datetime.utcnow()

            if agg is None:
                agg = UserGameStats(
                    user_id=user_id,
                    game_type=game_type,
                    total_played=1,
                    total_wins=1 if result == "win" else 0,
                    total_losses=1 if result == "loss" else 0,
                    total_ties=1 if result == "tie" else 0,
                    total_points_earned=points_earned,
                    current_win_streak=1 if result == "win" else 0,
                    best_win_streak=1 if result == "win" else 0,
                    average_score=float(score) if score is not None else None,
                    highest_score=score,
                    last_played=now,
                )
                s.add(agg)
                return

            agg.total_played += 1
            if result == "win":
                agg.total_wins += 1
                agg.current_win_streak += 1
                agg.best_win_streak = max(agg.best_win_streak, agg.current_win_streak)
            elif result == "loss":
                agg.total_losses += 1
                agg.current_win_streak = 0
            elif result == "tie":
                agg.total_ties += 1

            agg.total_points_earned += points_earned
            agg.last_played = now

            if score is not None:
                prior_total = (agg.average_score or 0) * (agg.total_played - 1)
                agg.average_score = (prior_total + score) / agg.total_played
                if agg.highest_score is None or score > agg.highest_score:
                    agg.highest_score = score

    def get_user_game_stats(self, user_id: int, game_type: Optional[str] = None) -> Dict:
        with self.session_scope(commit=False) as s:
            if game_type:
                row = (
                    s.query(UserGameStats)
                    .filter_by(user_id=user_id, game_type=game_type)
                    .first()
                )
                return _game_stats_to_dict(row, include_type=True) if row else {}

            rows = s.query(UserGameStats).filter_by(user_id=user_id).all()
            return {r.game_type: _game_stats_to_dict(r) for r in rows}

    def get_game_leaderboard(
        self,
        game_type: str,
        stat_type: str = "wins",
        limit: int = 10,
    ) -> List[Tuple[int, int]]:
        column_map = {
            "wins": UserGameStats.total_wins,
            "played": UserGameStats.total_played,
            "points": UserGameStats.total_points_earned,
            "streak": UserGameStats.best_win_streak,
            "score": UserGameStats.highest_score,
        }
        order_col = column_map.get(stat_type)
        if order_col is None:
            return []

        with self.session_scope(commit=False) as s:
            rows = (
                s.query(UserGameStats)
                .filter_by(game_type=game_type)
                .order_by(order_col.desc())
                .limit(limit)
                .all()
            )

            if stat_type == "wins":
                return [(r.user_id, r.total_wins) for r in rows]
            if stat_type == "played":
                return [(r.user_id, r.total_played) for r in rows]
            if stat_type == "points":
                return [(r.user_id, r.total_points_earned) for r in rows]
            if stat_type == "streak":
                return [(r.user_id, r.best_win_streak) for r in rows]
            return [(r.user_id, r.highest_score or 0) for r in rows]

    # ------------------------------------------------------------ trivia stats

    def log_trivia_answer(self, user_id: int, correct: bool, difficulty: str, points: int = 0) -> None:
        with self.session_scope() as s:
            row = s.query(TriviaStats).filter_by(user_id=user_id).first()
            now = datetime.utcnow()

            if row is None:
                row = TriviaStats(
                    user_id=user_id,
                    total_questions=1,
                    correct_answers=1 if correct else 0,
                    wrong_answers=0 if correct else 1,
                    total_points=points,
                    current_streak=1 if correct else 0,
                    best_streak=1 if correct else 0,
                    last_played=now,
                )
                _apply_trivia_difficulty(row, difficulty, correct)
                s.add(row)
                return

            row.total_questions += 1
            if correct:
                row.correct_answers += 1
                row.current_streak += 1
                row.best_streak = max(row.best_streak, row.current_streak)
            else:
                row.wrong_answers += 1
                row.current_streak = 0

            row.total_points += points
            row.last_played = now
            _apply_trivia_difficulty(row, difficulty, correct)

    def log_trivia_competition(
        self,
        user_id: int,
        correct: int,
        total: int,
        points: int,
        difficulty: str,
    ) -> None:
        with self.session_scope() as s:
            row = s.query(TriviaStats).filter_by(user_id=user_id).first()
            if row is None:
                s.add(TriviaStats(
                    user_id=user_id,
                    competitions_completed=1,
                    competitions_perfect=1 if correct == total else 0,
                    best_competition_score=points,
                ))
                return

            row.competitions_completed += 1
            if correct == total:
                row.competitions_perfect += 1
            if points > row.best_competition_score:
                row.best_competition_score = points

    def get_trivia_stats(self, user_id: int) -> Optional[Dict]:
        with self.session_scope(commit=False) as s:
            row = s.query(TriviaStats).filter_by(user_id=user_id).first()
            if not row:
                return None

            def _acc(correct: int, total: int) -> float:
                return (correct / total * 100) if total > 0 else 0.0

            return {
                "total_questions": row.total_questions,
                "correct_answers": row.correct_answers,
                "wrong_answers": row.wrong_answers,
                "accuracy": _acc(row.correct_answers, row.total_questions),
                "total_points": row.total_points,
                "easy_accuracy": _acc(row.easy_correct, row.easy_total),
                "medium_accuracy": _acc(row.medium_correct, row.medium_total),
                "hard_accuracy": _acc(row.hard_correct, row.hard_total),
                "expert_accuracy": _acc(row.expert_correct, row.expert_total),
                "competitions_completed": row.competitions_completed,
                "competitions_perfect": row.competitions_perfect,
                "best_competition_score": row.best_competition_score,
                "current_streak": row.current_streak,
                "best_streak": row.best_streak,
                "last_played": row.last_played,
            }

    def get_trivia_leaderboard(
        self,
        stat_type: str = "accuracy",
        limit: int = 10,
    ) -> List[Tuple[int, float]]:
        with self.session_scope(commit=False) as s:
            rows = s.query(TriviaStats).filter(TriviaStats.total_questions > 0).all()

            if stat_type == "accuracy":
                board = [(r.user_id, r.correct_answers / r.total_questions * 100) for r in rows]
            elif stat_type == "points":
                board = [(r.user_id, float(r.total_points)) for r in rows]
            elif stat_type == "streak":
                board = [(r.user_id, float(r.best_streak)) for r in rows]
            elif stat_type == "competitions":
                board = [(r.user_id, float(r.competitions_completed)) for r in rows]
            else:
                return []

            board.sort(key=lambda x: x[1], reverse=True)
            return board[:limit]


# ============================================================================
# Helpers
# ============================================================================

def _apply_trivia_difficulty(row: TriviaStats, difficulty: str, correct: bool) -> None:
    fields = _DIFFICULTY_FIELDS.get(difficulty)
    if not fields:
        return
    total_field, correct_field = fields
    setattr(row, total_field, getattr(row, total_field) + 1)
    if correct:
        setattr(row, correct_field, getattr(row, correct_field) + 1)


def _game_stats_to_dict(row: UserGameStats, include_type: bool = False) -> Dict:
    win_rate = (row.total_wins / row.total_played * 100) if row.total_played > 0 else 0
    data = {
        "total_played": row.total_played,
        "total_wins": row.total_wins,
        "total_losses": row.total_losses,
        "total_ties": row.total_ties,
        "total_points": row.total_points_earned,
        "win_rate": win_rate,
        "current_streak": row.current_win_streak,
        "best_streak": row.best_win_streak,
        "average_score": row.average_score,
        "highest_score": row.highest_score,
        "last_played": row.last_played,
    }
    if include_type:
        data["game_type"] = row.game_type
        data["first_played"] = row.first_played
    return data
