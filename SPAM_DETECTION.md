# 🛡️ Spam Detection & Prevention

## Overview

Jule includes an intelligent spam detection system that automatically identifies and removes spam messages, keeping your community clean without heavy-handed moderation.

## How It Works

### Detection Algorithm

1. **Every message is tracked** with:
   - User ID
   - Message ID  
   - Timestamp
   - Channel ID

2. **Spam threshold**: 5 messages in 20 seconds
   - Configurable per your needs
   - Smart enough to catch rapid spam
   - Lenient enough for normal fast chat

3. **Automatic cleanup**: Old tracking data (>1 hour) is automatically removed

### What Happens When Spam is Detected?

```
User sends 5+ messages in 20 seconds
    ↓
🚨 Spam detected!
    ↓
✅ All recent messages from user deleted
    ↓
⚠️ Warning message sent (auto-deletes in 5 seconds)
    ↓
📊 Event logged to database for review
```

### Example Scenario

```
[12:00:00] User: "hey"
[12:00:02] User: "anyone there?"
[12:00:04] User: "hello?"
[12:00:06] User: "HELLO??"
[12:00:08] User: "WHY NO ONE ANSWERING"
           ↓
🤖 Jule: "⚠️ @User Whoa there! Slow down a bit. (5 messages deleted for spam)"
```

## Features

### ✨ Smart Detection
- **Not overly aggressive**: Normal fast conversation is fine
- **Context aware**: Only counts messages within timeframe
- **Automatic reset**: Counter resets after 20 seconds of normal behavior

### 🔍 Tracking
- All spam events logged to database
- Review spam patterns with SQL queries
- Identify repeat offenders

### 🧹 Self-Cleaning
- Warning messages auto-delete after 5 seconds
- No channel clutter
- Professional moderation feel

### 💾 Persistent
- Tracking data stored in SQLite
- Survives bot restarts
- Historical data for analysis

## Configuration

### Default Settings
```python
threshold = 5        # Number of messages
timeframe = 20       # Seconds
```

### Customize (in bot.py)
```python
# Stricter (3 messages in 10 seconds)
spam_detector = SpamDetector(db, threshold=3, timeframe=10)

# More lenient (7 messages in 30 seconds)
spam_detector = SpamDetector(db, threshold=7, timeframe=30)
```

## Database Tables

### `message_tracking`
Tracks recent messages for spam detection.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Unique ID |
| user_id | INTEGER | Discord user ID |
| message_id | INTEGER | Discord message ID |
| channel_id | INTEGER | Channel where sent |
| guild_id | INTEGER | Server ID |
| timestamp | TIMESTAMP | When sent |

**Cleanup**: Entries >1 hour old are deleted hourly

### `spam_logs`
Records spam detection events.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Unique ID |
| user_id | INTEGER | Spammer's user ID |
| guild_id | INTEGER | Server ID |
| message_count | INTEGER | How many messages |
| timeframe_seconds | REAL | Detection window |
| action_taken | TEXT | Action performed |
| detected_at | TIMESTAMP | When detected |

**Never deleted**: Permanent log for review

## Reviewing Spam Logs

### Using SQLite
```bash
sqlite3 data/jule.db

# Recent spam events
SELECT user_id, message_count, detected_at 
FROM spam_logs 
ORDER BY detected_at DESC 
LIMIT 20;

# Repeat offenders
SELECT user_id, COUNT(*) as spam_count 
FROM spam_logs 
GROUP BY user_id 
HAVING spam_count > 1 
ORDER BY spam_count DESC;

# Today's spam
SELECT * FROM spam_logs 
WHERE DATE(detected_at) = DATE('now');
```

### Future Enhancement: Admin Command
Could add `!spamlog` command:
```python
@bot.command(name="spamlog", help="[Admin] View recent spam events")
@commands.has_permissions(administrator=True)
async def spamlog(ctx, limit: int = 10):
    # Query database for recent spam
    # Display in embed
```

## Technical Details

### In-Memory Cache
For performance, recent messages are cached:
```python
message_history = {
    user_id: [(message_id, timestamp), ...]
}
```

Benefits:
- **Fast checks**: No database query per message
- **Efficient**: Auto-cleaned every message
- **Accurate**: Synchronized with database

### Message Deletion
```python
# Fetch and delete each tracked message
for message_id in tracked_messages:
    msg = await channel.fetch_message(message_id)
    await msg.delete()
```

Handles:
- ✅ Already deleted messages (NotFound)
- ✅ No permission (Forbidden)
- ✅ Other errors (gracefully logged)

## Best Practices

### 1. Monitor Initially
Check spam logs first few days:
```sql
SELECT * FROM spam_logs ORDER BY detected_at DESC;
```

### 2. Adjust Threshold
If too many false positives:
```python
# Increase threshold or timeframe
spam_detector = SpamDetector(db, threshold=7, timeframe=25)
```

### 3. Communicate with Users
Add to server rules:
```
🤖 Bot Protection: Sending 5+ messages rapidly will trigger 
automatic spam detection. Please pace your messages!
```

### 4. Backup Database
```bash
# Regular backups preserve spam logs
cp data/jule.db data/jule.db.backup
```

## Integration with Other Features

### Points System
- **No points awarded** for spam messages
- Points only given to legitimate participation
- Prevents gaming the system

### Commands
- Spam messages **don't trigger commands**
- User must send messages normally
- Prevents command spam

## Limitations

### What It Can't Do
❌ Detect content-based spam (same message repeated)
❌ Detect coordinated spam (multiple users)
❌ Detect mention spam
❌ Detect link spam

### Possible Enhancements
1. **Content matching**: Detect repeated messages
2. **Mention limits**: Max mentions per message
3. **Link filtering**: Suspicious URL detection
4. **User trust scores**: Relax limits for established members
5. **Temporary mutes**: Auto-mute repeat offenders

## Example: Add Content Detection

```python
# In SpamDetector class
def __init__(self, db, threshold=5, timeframe=20):
    # ...existing code...
    self.message_content = {}  # {user_id: [content1, content2, ...]}

async def track_message(self, message):
    # ...existing tracking...
    
    # Track content
    user_id = message.author.id
    if user_id not in self.message_content:
        self.message_content[user_id] = []
    self.message_content[user_id].append(message.content)
    
    # Check for repeated content
    if len(self.message_content[user_id]) >= 3:
        last_three = self.message_content[user_id][-3:]
        if len(set(last_three)) == 1:  # All same
            return True  # Spam detected
```

## Permissions Required

Bot needs these permissions:
- ✅ **Read Messages**: To see messages
- ✅ **Send Messages**: To send warnings
- ✅ **Manage Messages**: To delete spam
- ✅ **Read Message History**: To fetch messages

## Testing

### Manual Test
1. Send 5 messages rapidly
2. Watch for deletion and warning
3. Check database:
```sql
SELECT * FROM spam_logs ORDER BY detected_at DESC LIMIT 1;
SELECT COUNT(*) FROM message_tracking WHERE user_id = YOUR_ID;
```

### Expected Behavior
- Messages deleted within 1 second
- Warning appears immediately
- Warning auto-deletes after 5 seconds
- No error messages

## Troubleshooting

### Messages not deleted
- Check bot has **Manage Messages** permission
- Verify bot role is above user's highest role
- Check bot can see the channel

### False positives
- Increase threshold: `threshold=7`
- Increase timeframe: `timeframe=30`

### Performance issues
- Database cleanup running: Normal, runs hourly
- Too many tracked users: Increase cleanup frequency

---

## Summary

Jule's spam detection is:
- ⚡ **Fast**: In-memory cache + database
- 🎯 **Accurate**: Configurable threshold
- 🧹 **Clean**: Auto-cleanup of warnings
- 📊 **Logged**: Full audit trail
- 🔧 **Customizable**: Easy to adjust
- 💪 **Reliable**: Persistent storage

Perfect for small communities that want automatic spam protection without complex moderation bots!

---

Made with 🛡️ for safe, spam-free communities!

