# 📊 Database Architecture Documentation

## Overview

Jule bot now uses **SQLite** for persistent storage of all data. This ensures that user points, reminders, birthdays, and spam detection tracking are preserved across bot restarts.

## Database Location

```
data/jule.db
```

The database file is created automatically when the bot starts. The `data/` directory is created if it doesn't exist.

## Schema

### Tables

#### 1. `user_points`
Stores community points and message counts for users.

```sql
CREATE TABLE user_points (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `user_id`: Discord user ID (unique identifier)
- `points`: Total points earned by the user
- `message_count`: Total messages sent by the user
- `last_updated`: Last time points or messages were updated

**Usage:**
- Points awarded for participation (1 point per 10 messages)
- Points awarded for winning games (RPS: 2 points, Guess: 5 points)
- Displayed in `!points` and `!leaderboard` commands

---

#### 2. `reminders`
Stores user reminders with due times.

```sql
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    remind_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `id`: Unique reminder ID
- `user_id`: Discord user ID who set the reminder
- `channel_id`: Channel where reminder should be sent
- `message`: Reminder message content
- `remind_time`: When the reminder should trigger
- `created_at`: When the reminder was created

**Usage:**
- Created by `!remind <minutes> <message>` command
- Checked every 30 seconds by background task
- Deleted after being sent

---

#### 3. `birthdays`
Stores user birthdays for automatic wishes.

```sql
CREATE TABLE birthdays (
    user_id INTEGER PRIMARY KEY,
    birth_month INTEGER NOT NULL,
    birth_day INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `user_id`: Discord user ID (unique identifier)
- `birth_month`: Month (1-12)
- `birth_day`: Day of month (1-31)
- `added_at`: When birthday was added/updated

**Usage:**
- Set with `!birthday <month> <day>` command
- Checked daily at midnight
- Displayed in `!userinfo` and `!birthdays` commands

---

#### 4. `message_tracking`
Temporary table for spam detection tracking.

```sql
CREATE TABLE message_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `id`: Unique tracking ID
- `user_id`: Discord user ID who sent the message
- `message_id`: Discord message ID
- `channel_id`: Channel where message was sent
- `guild_id`: Server/guild ID
- `timestamp`: When message was sent

**Usage:**
- Tracks all messages for spam detection
- Used to detect rapid message sending (5+ in 20 seconds)
- Old entries (>1 hour) cleaned up automatically
- Messages deleted when spam is detected

---

#### 5. `spam_logs`
Logs spam detection events for moderation review.

```sql
CREATE TABLE spam_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    message_count INTEGER NOT NULL,
    timeframe_seconds REAL NOT NULL,
    action_taken TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `id`: Unique log ID
- `user_id`: User who triggered spam detection
- `guild_id`: Server where spam occurred
- `message_count`: Number of messages detected
- `timeframe_seconds`: Time window (default: 20 seconds)
- `action_taken`: Action performed (e.g., "messages_deleted")
- `detected_at`: When spam was detected

**Usage:**
- Automatically logged when spam is detected
- Can be reviewed by admins to monitor spam patterns
- Helps identify repeat offenders

---

#### 6. `server_settings`
Stores per-server configuration (for future multi-server support).

```sql
CREATE TABLE server_settings (
    guild_id INTEGER PRIMARY KEY,
    spam_threshold INTEGER DEFAULT 5,
    spam_timeframe INTEGER DEFAULT 20,
    welcome_channel_id INTEGER,
    default_role_id INTEGER,
    settings_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Columns:**
- `guild_id`: Discord server/guild ID
- `spam_threshold`: Number of messages to trigger spam detection
- `spam_timeframe`: Time window in seconds
- `welcome_channel_id`: Channel for welcome messages
- `default_role_id`: Role to assign to new members
- `settings_updated`: Last settings update time

**Usage:**
- Currently uses hardcoded defaults
- Ready for future per-server customization
- Can be extended for custom prefixes, features, etc.

---

## Spam Detection System

### How It Works

1. **Message Tracking**: Every message is tracked with user ID, message ID, and timestamp
2. **In-Memory Cache**: Recent messages stored in dictionary for fast access
3. **Threshold Check**: If user sends 5+ messages in 20 seconds, spam is detected
4. **Automatic Cleanup**: Messages deleted, warning sent, tracking cleared

### Data Flow

```
User sends message
    ↓
Track in database (message_tracking)
    ↓
Add to in-memory cache {user_id: [(msg_id, timestamp), ...]}
    ↓
Clean old entries (>20 seconds ago)
    ↓
Check count >= threshold (5)
    ↓
If spam: Delete messages, log event, send warning
```

### Configuration

Default values (can be customized in code):
- **Threshold**: 5 messages
- **Timeframe**: 20 seconds
- **Cleanup**: Every 1 hour (removes tracking >1 hour old)

---

## Service Layer

### Database Class (`model/model.py`)
Core database operations and queries.

**Key Methods:**
- `get_user_points()`, `add_points()`, `increment_message_count()`
- `add_reminder()`, `get_due_reminders()`, `delete_reminder()`
- `add_birthday()`, `get_birthday()`, `get_todays_birthdays()`
- `track_message()`, `get_recent_messages()`, `log_spam_detection()`
- `cleanup_old_message_tracking()`, `delete_tracked_messages()`

### SpamDetector Class (`model/services.py`)
Handles spam detection logic.

**Key Methods:**
- `track_message(message)`: Track message and check for spam
- `handle_spam(message)`: Delete spam messages
- `cleanup_database()`: Remove old tracking data

### PointsService Class (`model/services.py`)
Manages user points system.

**Key Methods:**
- `add_points(user_id, points)`: Award points
- `get_points(user_id)`: Get user's points
- `increment_message(user_id)`: Track message and auto-award points
- `get_leaderboard(limit)`: Get top users

### ReminderService Class (`model/services.py`)
Manages reminders.

**Key Methods:**
- `add_reminder(user_id, channel_id, message, minutes)`: Create reminder
- `get_due_reminders()`: Get reminders to send
- `complete_reminder(reminder_id)`: Delete sent reminder

### BirthdayService Class (`model/services.py`)
Manages birthdays.

**Key Methods:**
- `add_birthday(user_id, month, day)`: Set birthday
- `get_birthday(user_id)`: Get user's birthday
- `get_todays_birthdays()`: Get today's birthday users

---

## Background Tasks

### 1. `check_reminders` (every 30 seconds)
- Queries database for due reminders
- Sends reminder messages
- Deletes completed reminders

### 2. `cleanup_tracking` (every 1 hour)
- Removes message tracking entries >1 hour old
- Keeps database size manageable
- Prints confirmation message

### 3. `check_birthdays` (every 24 hours)
- Checks for users with birthdays today
- Sends birthday wishes in welcome channel
- Posts beautiful embedded messages

---

## Data Persistence

### What's Persistent?
✅ User points and message counts
✅ Reminders (even after bot restart)
✅ Birthdays
✅ Spam logs (for review)
✅ Server settings

### What's Temporary?
⚠️ Message tracking (cleaned after 1 hour)
⚠️ In-memory spam detection cache

### Backup Recommendations

```bash
# Backup database
cp data/jule.db data/jule.db.backup

# Scheduled backup (add to cron)
0 3 * * * cp /path/to/jule/data/jule.db /path/to/backups/jule-$(date +\%Y\%m\%d).db
```

---

## Migration Notes

### Legacy Compatibility

The bot maintains legacy in-memory dictionaries for backward compatibility:
```python
bot.user_points = defaultdict(int)  # Legacy
bot.user_messages = defaultdict(int)  # Legacy
```

These can be removed once database is confirmed working.

### Future Enhancements

Potential improvements:
1. **Leaderboard History**: Track daily/weekly/monthly stats
2. **User Profiles**: Extended user information
3. **Custom Commands**: Server-specific commands in database
4. **Moderation Logs**: Complete moderation action history
5. **Analytics**: Server growth, activity patterns
6. **Achievements**: Unlock rewards at point milestones

---

## Troubleshooting

### Database Locked
If you see "database is locked" errors:
```python
# Increase timeout in Database.__init__
self.conn = sqlite3.connect(db_path, timeout=30.0)
```

### Corrupted Database
```bash
# Check integrity
sqlite3 data/jule.db "PRAGMA integrity_check;"

# Restore from backup
cp data/jule.db.backup data/jule.db
```

### View Data
```bash
# Open database
sqlite3 data/jule.db

# List tables
.tables

# View points
SELECT * FROM user_points ORDER BY points DESC LIMIT 10;

# View spam logs
SELECT * FROM spam_logs ORDER BY detected_at DESC LIMIT 20;
```

---

## Performance

### Optimizations
- Connection reuse (single connection per bot instance)
- Row factory for dict-like access
- Indexed primary keys
- Batch operations where possible
- In-memory cache for spam detection (fast checks)

### Expected Performance
- **Points queries**: <1ms
- **Reminder checks**: <5ms
- **Spam detection**: <2ms (in-memory + DB)
- **Leaderboard**: <10ms

---

## Security

### Best Practices
✅ Parameterized queries (SQL injection prevention)
✅ Input validation on all user data
✅ No sensitive data stored
✅ File permissions (ensure `data/` is not world-readable)

### Recommendations
```bash
# Secure data directory
chmod 700 data/
chmod 600 data/jule.db
```

---

Made with 💙 for persistent, reliable community engagement!

