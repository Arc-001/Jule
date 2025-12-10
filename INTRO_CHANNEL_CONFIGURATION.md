# Intro Channel Configuration Guide

## Overview

The intro channel configuration feature allows server administrators to dynamically configure which channel should be used for automatic role assignment based on user introductions. This removes the hardcoded channel dependency and makes the bot more flexible across different servers.

## Features

- **Dynamic Configuration**: Set or change the intro channel at any time without restarting the bot
- **Persistent Storage**: Channel settings are stored in the database and survive bot restarts
- **Easy Management**: Simple commands to set, view, and clear the intro channel
- **Fallback Behavior**: If no intro channel is set, automatic role assignment is disabled (safe default)

## Admin Commands

### !setintrochannel

Set the channel where introductions will trigger automatic role assignment.

**Usage:**
```
!setintrochannel #channel-name
```

**Example:**
```
!setintrochannel #introductions
```

**To disable:**
```
!setintrochannel
```

**Features:**
- Only administrators can use this command
- Immediately takes effect (no restart needed)
- Provides detailed confirmation with usage information
- Can be cleared by calling without arguments

### !getintrochannel

Check which channel is currently configured for intro role allocation.

**Usage:**
```
!getintrochannel
```

**Shows:**
- Current intro channel (if set)
- Channel ID for reference
- Status (active/disabled/invalid)
- Instructions on how to configure

### !testrole

Test what roles would be assigned for a given introduction message.

**Usage:**
```
!testrole <introduction text>
```

**Example:**
```
!testrole Hi everyone! I'm a developer who loves Python and gaming. I also enjoy creating digital art in my spare time.
```

**Features:**
- Doesn't actually assign roles (test mode only)
- Shows which roles would be assigned
- Displays role IDs and mentions
- Useful for testing before setting the intro channel

## How It Works

### 1. Configuration
Admin sets the intro channel using `!setintrochannel #channel`

### 2. User Posts Introduction
When a user posts in the configured channel:
- Message must be at least 50 characters long
- Bot shows typing indicator while processing
- AI analyzes the content using Gemini

### 3. Role Assignment
If the intro qualifies:
- Bot suggests appropriate roles based on content
- Roles are automatically assigned to the user
- Welcome message is sent with assigned roles
- Positive reactions are added to the message

### 4. Requirements
- Message length: minimum 50 characters
- Channel: must match configured intro channel
- Roles: must exist in `roles.json` configuration
- Permissions: bot needs role assignment permissions

## Database Schema

The intro channel ID is stored in the `server_settings` table:

```sql
CREATE TABLE server_settings (
    guild_id BIGINT PRIMARY KEY,
    intro_channel_id BIGINT,
    -- other settings...
);
```

## Migration from Hardcoded System

### Before (Hardcoded)
```python
# In channels.json
{
  "intro": 1436756182709698619,
  ...
}

# In bot.py
INTRO_CHANNEL_ID = CHANNEL_MAPPINGS.get("intro")
```

### After (Dynamic)
```python
# In database (per-guild)
server_settings = db.get_server_settings(guild_id)
intro_channel_id = server_settings.get('intro_channel_id')

# Set via command
!setintrochannel #introductions
```

## Benefits

1. **Multi-Server Support**: Each server can have its own intro channel
2. **No Hardcoding**: No need to edit config files or restart bot
3. **Flexible**: Easy to change channels as server structure evolves
4. **Fault Tolerant**: Gracefully handles deleted/invalid channels
5. **Admin Control**: Server admins control their own settings

## Example Workflow

### Initial Setup
```
Admin: !setintrochannel #welcome
Bot: ✅ Intro Channel Set
     Automatic role assignment is now enabled for #welcome
     
     How it works:
     • Messages must be at least 50 characters
     • AI analyzes their intro and suggests roles
     • Roles are automatically assigned
     • A welcome message is sent
```

### Testing
```
Admin: !testrole I'm a Python developer who loves gaming and making music
Bot: 🔍 Role Assignment Test
     Here's what roles would be assigned:
     
     developer
     🎮 @Developer (ID: 123456789)
     
     gamer
     🎮 @Gamer (ID: 987654321)
     
     musician
     🎵 @Musician (ID: 456789123)
```

### Checking Status
```
Admin: !getintrochannel
Bot: 📍 Current Intro Channel
     Auto role assignment is enabled for #welcome
     
     Channel ID: 1436756182709698619
     Status: ✅ Active
```

### Disabling
```
Admin: !setintrochannel
Bot: 🔕 Intro Channel Cleared
     Automatic role assignment has been disabled.
     
     To re-enable:
     Use !setintrochannel #channel to set a new intro channel
```

## Troubleshooting

### Issue: Roles not being assigned
**Check:**
1. Is the intro channel properly set? Use `!getintrochannel`
2. Is the message long enough? (50+ characters required)
3. Are the roles in `roles.json`? Use `!syncroles`
4. Does the bot have role assignment permissions?

### Issue: Channel not found error
**Solution:**
1. The configured channel was deleted
2. Use `!setintrochannel #new-channel` to set a valid channel

### Issue: No roles suggested
**Possible reasons:**
1. Message doesn't match any role keywords
2. Roles.json doesn't have relevant roles
3. Use `!testrole <message>` to test the AI's suggestions

## Security Considerations

- Only administrators can configure the intro channel
- Channel ID is validated before setting
- Invalid/deleted channels are detected and reported
- Bot gracefully handles missing permissions

## Future Enhancements

Possible future improvements:
- Multiple intro channels per server
- Custom minimum message length per server
- Intro channel presets/templates
- Analytics on role assignment success rate
- Customizable welcome messages per server

