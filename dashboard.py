"""Flask dashboard for Jule bot — metrics, leaderboards, logs."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from sqlalchemy import func

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from logger import get_logger  # noqa: E402
from model.model import (  # noqa: E402
    Birthday,
    Database,
    GameStats,
    MessageTracking,
    MusicStats,
    Reminder,
    SpamLog,
    TriviaStats,
    UserGameStats,
    UserPoints,
)

log = get_logger(__name__)

DASHBOARD_DB_PATH = os.environ.get("DASHBOARD_DB_PATH", "src/data/jule.db")
DASHBOARD_HOST = os.environ.get("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.environ.get("DASHBOARD_PORT", "8080"))

app = Flask(
    __name__,
    template_folder="dashboard/templates",
    static_folder="dashboard/static",
)
CORS(app)

db = Database(DASHBOARD_DB_PATH)


# ============================================================================
# Helpers
# ============================================================================

def _enrich_with_users(rows: List[Dict], id_key: str = "user_id") -> List[Dict]:
    """Attach cached username/display_name/avatar_url to rows keyed by `id_key`."""
    user_ids = list({row[id_key] for row in rows if row.get(id_key) is not None})
    cache = db.get_users_from_cache(user_ids)
    for row in rows:
        info = cache.get(row[id_key], {})
        row.setdefault("username", info.get("username", f"User {row[id_key]}"))
        row.setdefault("display_name", info.get("display_name"))
        row.setdefault("avatar_url", info.get("avatar_url"))
    return rows


# ============================================================================
# Routes — views
# ============================================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================================
# Routes — stats
# ============================================================================

@app.route("/api/stats/overview")
def stats_overview():
    with db.session_scope(commit=False) as s:
        total_users = s.query(func.count(UserPoints.user_id)).scalar() or 0
        total_points = s.query(func.sum(UserPoints.points)).scalar() or 0
        total_messages = s.query(func.sum(UserPoints.message_count)).scalar() or 0
        active_reminders = s.query(func.count(Reminder.id)).scalar() or 0
        total_birthdays = s.query(func.count(Birthday.user_id)).scalar() or 0

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        spam_today = (
            s.query(func.count(SpamLog.id))
            .filter(SpamLog.detected_at >= today_start)
            .scalar() or 0
        )

        yesterday = datetime.utcnow() - timedelta(days=1)
        messages_24h = (
            s.query(func.count(MessageTracking.id))
            .filter(MessageTracking.timestamp >= yesterday)
            .scalar() or 0
        )

    return jsonify({
        "total_users": total_users,
        "total_points": total_points,
        "total_messages": total_messages,
        "active_reminders": active_reminders,
        "total_birthdays": total_birthdays,
        "spam_today": spam_today,
        "messages_24h": messages_24h,
    })


# ============================================================================
# Routes — users
# ============================================================================

@app.route("/api/users/leaderboard")
def users_leaderboard():
    limit = min(request.args.get("limit", 10, type=int), 100)
    leaderboard = db.get_leaderboard(limit=limit)

    rows = [{"user_id": uid, "points": pts} for uid, pts in leaderboard]
    return jsonify({"leaderboard": _enrich_with_users(rows)})


@app.route("/api/users/<int:user_id>")
def user_details(user_id: int):
    with db.session_scope(commit=False) as s:
        user = s.query(UserPoints).filter_by(user_id=user_id).first()
        birthday = s.query(Birthday).filter_by(user_id=user_id).first()
        reminders = s.query(func.count(Reminder.id)).filter_by(user_id=user_id).scalar() or 0

        return jsonify({
            "user_id": user_id,
            "points": user.points if user else 0,
            "message_count": user.message_count if user else 0,
            "last_updated": user.last_updated.isoformat() if user else None,
            "birthday": (
                {"month": birthday.birth_month, "day": birthday.birth_day}
                if birthday else None
            ),
            "active_reminders": reminders,
        })


# ============================================================================
# Routes — logs
# ============================================================================

@app.route("/api/logs/spam")
def spam_logs():
    limit = request.args.get("limit", 50, type=int)
    hours = request.args.get("hours", 24, type=int)
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    with db.session_scope(commit=False) as s:
        logs = (
            s.query(SpamLog)
            .filter(SpamLog.detected_at >= cutoff)
            .order_by(SpamLog.detected_at.desc())
            .limit(limit)
            .all()
        )
        rows = [{
            "id": l.id,
            "user_id": l.user_id,
            "guild_id": l.guild_id,
            "message_count": l.message_count,
            "timeframe": l.timeframe_seconds,
            "action": l.action_taken,
            "detected_at": l.detected_at.isoformat(),
        } for l in logs]

    return jsonify({"logs": _enrich_with_users(rows)})


# ============================================================================
# Routes — reminders
# ============================================================================

@app.route("/api/reminders")
def reminders_list():
    with db.session_scope(commit=False) as s:
        reminders = s.query(Reminder).order_by(Reminder.remind_time).all()
        rows = [{
            "id": r.id,
            "user_id": r.user_id,
            "channel_id": r.channel_id,
            "message": r.message,
            "remind_time": r.remind_time.isoformat(),
            "created_at": r.created_at.isoformat(),
        } for r in reminders]

    return jsonify({"reminders": _enrich_with_users(rows)})


# ============================================================================
# Routes — birthdays
# ============================================================================

@app.route("/api/birthdays/calendar")
def birthdays_calendar():
    with db.session_scope(commit=False) as s:
        birthdays = (
            s.query(Birthday)
            .order_by(Birthday.birth_month, Birthday.birth_day)
            .all()
        )
        rows = [{
            "user_id": b.user_id,
            "month": b.birth_month,
            "day": b.birth_day,
        } for b in birthdays]

    return jsonify({"birthdays": _enrich_with_users(rows)})


@app.route("/api/birthdays/upcoming")
def upcoming_birthdays():
    now = datetime.now()
    next_month = (now.month % 12) + 1

    with db.session_scope(commit=False) as s:
        birthdays = (
            s.query(Birthday)
            .filter((Birthday.birth_month == now.month) | (Birthday.birth_month == next_month))
            .order_by(Birthday.birth_month, Birthday.birth_day)
            .all()
        )

        rows: List[Dict] = []
        for b in birthdays:
            this_year = datetime(now.year, b.birth_month, b.birth_day)
            if this_year < now:
                this_year = datetime(now.year + 1, b.birth_month, b.birth_day)
            rows.append({
                "user_id": b.user_id,
                "month": b.birth_month,
                "day": b.birth_day,
                "days_until": (this_year - now).days,
            })

    rows = _enrich_with_users(rows)
    rows.sort(key=lambda x: x["days_until"])
    return jsonify({"birthdays": rows[:10]})


# ============================================================================
# Routes — activity
# ============================================================================

@app.route("/api/activity/chart")
def activity_chart():
    days = request.args.get("days", 7, type=int)
    cutoff = datetime.utcnow() - timedelta(days=days)

    with db.session_scope(commit=False) as s:
        results = (
            s.query(
                func.date(MessageTracking.timestamp).label("date"),
                func.count(MessageTracking.id).label("count"),
            )
            .filter(MessageTracking.timestamp >= cutoff)
            .group_by(func.date(MessageTracking.timestamp))
            .all()
        )
        data = {str(r.date): r.count for r in results}

    chart = [
        {
            "date": str((datetime.utcnow() - timedelta(days=days - i - 1)).date()),
            "count": data.get(str((datetime.utcnow() - timedelta(days=days - i - 1)).date()), 0),
        }
        for i in range(days)
    ]
    return jsonify({"activity": chart})


# ============================================================================
# Routes — games
# ============================================================================

@app.route("/api/games/stats")
def games_stats():
    with db.session_scope(commit=False) as s:
        rows = (
            s.query(
                UserGameStats.game_type,
                func.sum(UserGameStats.total_played).label("total_played"),
                func.sum(UserGameStats.total_wins).label("total_wins"),
                func.sum(UserGameStats.total_losses).label("total_losses"),
                func.max(UserGameStats.best_win_streak).label("best_streak"),
            )
            .group_by(UserGameStats.game_type)
            .all()
        )
        total_games = s.query(func.count(GameStats.id)).scalar() or 0

    games_data = []
    for g in rows:
        played = g.total_played or 0
        wins = g.total_wins or 0
        win_rate = (wins / played * 100) if played > 0 else 0
        games_data.append({
            "game_type": g.game_type,
            "total_played": played,
            "total_wins": wins,
            "total_losses": g.total_losses or 0,
            "win_rate": round(win_rate, 1),
            "best_streak": g.best_streak or 0,
        })

    return jsonify({"total_games": total_games, "games": games_data})


# ============================================================================
# Routes — music
# ============================================================================

@app.route("/api/music/top")
def music_top():
    limit = request.args.get("limit", 10, type=int)

    with db.session_scope(commit=False) as s:
        rows = (
            s.query(
                MusicStats.song_title,
                MusicStats.artist,
                func.count(MusicStats.id).label("play_count"),
            )
            .group_by(MusicStats.song_title, MusicStats.artist)
            .order_by(func.count(MusicStats.id).desc())
            .limit(limit)
            .all()
        )
        total_songs = s.query(func.count(MusicStats.id)).scalar() or 0

    return jsonify({
        "total_songs": total_songs,
        "top_songs": [
            {"title": r.song_title, "artist": r.artist or "Unknown", "plays": r.play_count}
            for r in rows
        ],
    })


# ============================================================================
# Routes — trivia
# ============================================================================

@app.route("/api/trivia/stats")
def trivia_stats():
    with db.session_scope(commit=False) as s:
        total_questions = s.query(func.sum(TriviaStats.total_questions)).scalar() or 0
        correct_answers = s.query(func.sum(TriviaStats.correct_answers)).scalar() or 0

    accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    return jsonify({
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "accuracy": round(accuracy, 1),
    })


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    for subdir in ("dashboard/templates", "dashboard/static/css", "dashboard/static/js"):
        os.makedirs(subdir, exist_ok=True)

    log.info("Starting Jule Dashboard on http://%s:%s", DASHBOARD_HOST, DASHBOARD_PORT)
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT, debug=True)
