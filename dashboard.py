"""
Modern Dashboard for Jule Bot
Provides web interface for viewing stats, logs, and user data
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from src.model.model import Database
from datetime import datetime, timedelta
import os

app = Flask(__name__, 
            template_folder='dashboard/templates',
            static_folder='dashboard/static')
CORS(app)

# Database instance
db = Database('src/data/jule.db')


# ============= ROUTES =============

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/stats/overview')
def stats_overview():
    """Get overview statistics"""
    session = db.get_session()
    try:
        from sqlalchemy import func
        from src.model.model import UserPoints, Reminder, Birthday, SpamLog, MessageTracking, UserCache

        # Total users
        total_users = session.query(func.count(UserPoints.user_id)).scalar() or 0
        
        # Total points distributed
        total_points = session.query(func.sum(UserPoints.points)).scalar() or 0
        
        # Total messages tracked
        total_messages = session.query(func.sum(UserPoints.message_count)).scalar() or 0
        
        # Active reminders
        active_reminders = session.query(func.count(Reminder.id)).scalar() or 0
        
        # Birthdays registered
        total_birthdays = session.query(func.count(Birthday.user_id)).scalar() or 0
        
        # Spam events today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        spam_today = session.query(func.count(SpamLog.id)).filter(
            SpamLog.detected_at >= today_start
        ).scalar() or 0
        
        # Messages in last 24h
        yesterday = datetime.utcnow() - timedelta(days=1)
        messages_24h = session.query(func.count(MessageTracking.id)).filter(
            MessageTracking.timestamp >= yesterday
        ).scalar() or 0
        
        return jsonify({
            'total_users': total_users,
            'total_points': total_points,
            'total_messages': total_messages,
            'active_reminders': active_reminders,
            'total_birthdays': total_birthdays,
            'spam_today': spam_today,
            'messages_24h': messages_24h
        })
    finally:
        session.close()


@app.route('/api/users/leaderboard')
def users_leaderboard():
    """Get top users by points"""
    limit = request.args.get('limit', 10, type=int)
    leaderboard = db.get_leaderboard(limit=min(limit, 100))
    
    # Get user IDs and fetch their cached info
    user_ids = [user_id for user_id, _ in leaderboard]
    user_cache = db.get_users_from_cache(user_ids)

    return jsonify({
        'leaderboard': [
            {
                'user_id': user_id,
                'username': user_cache.get(user_id, {}).get('username', f'User {user_id}'),
                'display_name': user_cache.get(user_id, {}).get('display_name'),
                'avatar_url': user_cache.get(user_id, {}).get('avatar_url'),
                'points': points
            }
            for user_id, points in leaderboard
        ]
    })


@app.route('/api/users/<int:user_id>')
def user_details(user_id):
    """Get detailed user information"""
    session = db.get_session()
    try:
        from src.model.model import UserPoints, Birthday, Reminder
        
        user = session.query(UserPoints).filter_by(user_id=user_id).first()
        birthday = session.query(Birthday).filter_by(user_id=user_id).first()
        reminders = session.query(Reminder).filter_by(user_id=user_id).all()
        
        return jsonify({
            'user_id': user_id,
            'points': user.points if user else 0,
            'message_count': user.message_count if user else 0,
            'last_updated': user.last_updated.isoformat() if user else None,
            'birthday': {
                'month': birthday.birth_month,
                'day': birthday.birth_day
            } if birthday else None,
            'active_reminders': len(reminders)
        })
    finally:
        session.close()


@app.route('/api/logs/spam')
def spam_logs():
    """Get spam detection logs"""
    limit = request.args.get('limit', 50, type=int)
    hours = request.args.get('hours', 24, type=int)
    
    session = db.get_session()
    try:
        from src.model.model import SpamLog
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        logs = session.query(SpamLog).filter(
            SpamLog.detected_at >= cutoff
        ).order_by(SpamLog.detected_at.desc()).limit(limit).all()
        
        # Get usernames for logs
        user_ids = list(set(log.user_id for log in logs))
        user_cache = db.get_users_from_cache(user_ids)

        return jsonify({
            'logs': [
                {
                    'id': log.id,
                    'user_id': log.user_id,
                    'username': user_cache.get(log.user_id, {}).get('username', f'User {log.user_id}'),
                    'guild_id': log.guild_id,
                    'message_count': log.message_count,
                    'timeframe': log.timeframe_seconds,
                    'action': log.action_taken,
                    'detected_at': log.detected_at.isoformat()
                }
                for log in logs
            ]
        })
    finally:
        session.close()


@app.route('/api/reminders')
def reminders_list():
    """Get all reminders"""
    session = db.get_session()
    try:
        from src.model.model import Reminder
        
        reminders = session.query(Reminder).order_by(Reminder.remind_time).all()
        
        # Get usernames for reminders
        user_ids = list(set(r.user_id for r in reminders))
        user_cache = db.get_users_from_cache(user_ids)

        return jsonify({
            'reminders': [
                {
                    'id': r.id,
                    'user_id': r.user_id,
                    'username': user_cache.get(r.user_id, {}).get('username', f'User {r.user_id}'),
                    'channel_id': r.channel_id,
                    'message': r.message,
                    'remind_time': r.remind_time.isoformat(),
                    'created_at': r.created_at.isoformat()
                }
                for r in reminders
            ]
        })
    finally:
        session.close()


@app.route('/api/birthdays/calendar')
def birthdays_calendar():
    """Get all birthdays for calendar view"""
    session = db.get_session()
    try:
        from src.model.model import Birthday

        # Get all birthdays
        birthdays = session.query(Birthday).order_by(
            Birthday.birth_month, Birthday.birth_day
        ).all()

        # Get usernames for birthdays
        user_ids = [b.user_id for b in birthdays]
        user_cache = db.get_users_from_cache(user_ids)

        result = []
        for b in birthdays:
            result.append({
                'user_id': b.user_id,
                'username': user_cache.get(b.user_id, {}).get('username', f'User {b.user_id}'),
                'display_name': user_cache.get(b.user_id, {}).get('display_name'),
                'month': b.birth_month,
                'day': b.birth_day
            })

        return jsonify({'birthdays': result})
    finally:
        session.close()


@app.route('/api/birthdays/upcoming')
def upcoming_birthdays():
    """Get upcoming birthdays"""
    session = db.get_session()
    try:
        from src.model.model import Birthday
        
        now = datetime.now()
        current_month = now.month
        current_day = now.day
        
        # Get birthdays in current and next month
        birthdays = session.query(Birthday).filter(
            (Birthday.birth_month == current_month) |
            (Birthday.birth_month == (current_month % 12) + 1)
        ).order_by(Birthday.birth_month, Birthday.birth_day).all()
        
        # Get usernames for birthdays
        user_ids = [b.user_id for b in birthdays]
        user_cache = db.get_users_from_cache(user_ids)

        result = []
        for b in birthdays:
            # Calculate days until birthday
            birthday_this_year = datetime(now.year, b.birth_month, b.birth_day)
            if birthday_this_year < now:
                birthday_this_year = datetime(now.year + 1, b.birth_month, b.birth_day)
            
            days_until = (birthday_this_year - now).days
            
            result.append({
                'user_id': b.user_id,
                'username': user_cache.get(b.user_id, {}).get('username', f'User {b.user_id}'),
                'display_name': user_cache.get(b.user_id, {}).get('display_name'),
                'month': b.birth_month,
                'day': b.birth_day,
                'days_until': days_until
            })
        
        # Sort by days until
        result.sort(key=lambda x: x['days_until'])
        
        return jsonify({'birthdays': result[:10]})
    finally:
        session.close()


@app.route('/api/activity/chart')
def activity_chart():
    """Get activity data for charts"""
    days = request.args.get('days', 7, type=int)
    
    session = db.get_session()
    try:
        from src.model.model import MessageTracking
        from sqlalchemy import func
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Get message count per day
        results = session.query(
            func.date(MessageTracking.timestamp).label('date'),
            func.count(MessageTracking.id).label('count')
        ).filter(
            MessageTracking.timestamp >= cutoff
        ).group_by(func.date(MessageTracking.timestamp)).all()
        
        data = {str(r.date): r.count for r in results}
        
        # Fill in missing days with 0
        chart_data = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=days-i-1)).date()
            chart_data.append({
                'date': str(date),
                'count': data.get(str(date), 0)
            })
        
        return jsonify({'activity': chart_data})
    finally:
        session.close()


@app.route('/api/games/stats')
def games_stats():
    """Get game statistics"""
    session = db.get_session()
    try:
        from src.model.model import UserGameStats, GameStats
        from sqlalchemy import func

        # Get game type statistics
        game_types = session.query(
            UserGameStats.game_type,
            func.sum(UserGameStats.total_played).label('total_played'),
            func.sum(UserGameStats.total_wins).label('total_wins'),
            func.sum(UserGameStats.total_losses).label('total_losses'),
            func.max(UserGameStats.best_win_streak).label('best_streak')
        ).group_by(UserGameStats.game_type).all()

        # Total games across all types
        total_games = session.query(func.count(GameStats.id)).scalar() or 0

        games_data = []
        for game in game_types:
            win_rate = (game.total_wins / game.total_played * 100) if game.total_played > 0 else 0
            games_data.append({
                'game_type': game.game_type,
                'total_played': game.total_played,
                'total_wins': game.total_wins,
                'total_losses': game.total_losses,
                'win_rate': round(win_rate, 1),
                'best_streak': game.best_streak or 0
            })

        return jsonify({
            'total_games': total_games,
            'games': games_data
        })
    finally:
        session.close()


@app.route('/api/music/top')
def music_top():
    """Get top played songs"""
    limit = request.args.get('limit', 10, type=int)

    session = db.get_session()
    try:
        from src.model.model import MusicStats
        from sqlalchemy import func

        # Get most played songs
        top_songs = session.query(
            MusicStats.song_title,
            MusicStats.artist,
            func.count(MusicStats.id).label('play_count')
        ).group_by(
            MusicStats.song_title,
            MusicStats.artist
        ).order_by(
            func.count(MusicStats.id).desc()
        ).limit(limit).all()

        # Get total songs played
        total_songs = session.query(func.count(MusicStats.id)).scalar() or 0

        return jsonify({
            'total_songs': total_songs,
            'top_songs': [
                {
                    'title': song.song_title,
                    'artist': song.artist or 'Unknown',
                    'plays': song.play_count
                }
                for song in top_songs
            ]
        })
    finally:
        session.close()


@app.route('/api/trivia/stats')
def trivia_stats():
    """Get trivia statistics"""
    session = db.get_session()
    try:
        from src.model.model import TriviaStats
        from sqlalchemy import func

        # Get aggregate trivia stats
        total_questions = session.query(func.sum(TriviaStats.total_questions)).scalar() or 0
        correct_answers = session.query(func.sum(TriviaStats.correct_answers)).scalar() or 0

        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0

        return jsonify({
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'accuracy': round(accuracy, 1)
        })
    finally:
        session.close()


if __name__ == '__main__':
    # Ensure dashboard folders exist
    os.makedirs('dashboard/templates', exist_ok=True)
    os.makedirs('dashboard/static/css', exist_ok=True)
    os.makedirs('dashboard/static/js', exist_ok=True)
    
    print("🚀 Starting Jule Dashboard on http://localhost:8080")
    print("📊 Dashboard ready!")
    print("✨ Modern design with real-time analytics")

    app.run(host='0.0.0.0', port=8080, debug=True)

