# Intro Channel Configuration - Quick Start

## What Changed?

The intro channel for automatic role assignment is no longer hardcoded! Admins can now configure it dynamically using bot commands.

## Quick Setup

### 1. Set the Intro Channel
```
!setintrochannel #introductions
```

### 2. Test It
```
!testrole Hi! I'm a Python developer who loves gaming and music.
```

### 3. Verify
```
!getintrochannel
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!setintrochannel #channel` | Set the intro channel | `!setintrochannel #welcome` |
| `!setintrochannel` | Clear/disable intro channel | `!setintrochannel` |
| `!getintrochannel` | View current intro channel | `!getintrochannel` |
| `!testrole <text>` | Test role assignment | `!testrole I love coding!` |

## Migration from Old System

If you're upgrading from a version that used hardcoded intro channels:

### Option 1: Use the Bot Command (Recommended)
```
!setintrochannel #your-intro-channel
```

### Option 2: Use the Migration Script
```bash
python migrate_intro_channel.py YOUR_GUILD_ID
```

Replace `YOUR_GUILD_ID` with your Discord server's ID.

## How It Works

### Before (Hardcoded)
```json
// channels.json
{
  "intro": 1234567890123456789
}
```
❌ Required editing config files  
❌ Required bot restart  
❌ Same for all servers  

### After (Dynamic)
```
!setintrochannel #introductions
```
✅ No config file editing  
✅ No bot restart needed  
✅ Different per server  
✅ Easy to change  

## Features

- **Per-Server Configuration**: Each Discord server can have its own intro channel
- **Dynamic Updates**: Changes take effect immediately
- **Safe Defaults**: If not set, role assignment is disabled
- **Easy Testing**: Test role assignment before enabling
- **Persistent**: Settings survive bot restarts

## Requirements

- Administrator permissions to use configuration commands
- At least 50 characters in intro messages
- Roles must be defined in `roles.json`
- Bot needs role assignment permissions

## Example Workflow

```bash
# Admin sets intro channel
!setintrochannel #welcome
✅ Intro Channel Set - Auto role assignment enabled for #welcome

# User posts in #welcome
User: "Hi everyone! I'm a Python developer who enjoys gaming..."
🎉 Welcome! I've assigned you: Developer, Gamer

# Admin checks configuration
!getintrochannel
📍 Current Intro Channel: #welcome
Status: ✅ Active

# Admin tests before changing
!testrole I love making music and digital art
🔍 Would assign: Musician, Artist

# Admin changes channel
!setintrochannel #introductions
✅ Intro Channel Set - Auto role assignment enabled for #introductions
```

## Troubleshooting

### Roles not being assigned?
1. Check intro channel is set: `!getintrochannel`
2. Ensure message is 50+ characters
3. Verify roles exist: `!syncroles`
4. Check bot permissions

### Channel was deleted?
```
!setintrochannel #new-channel
```

### Want to disable temporarily?
```
!setintrochannel
```

## Technical Details

- Settings stored in `server_settings` table in database
- Loaded per-message for flexibility
- No caching issues - always uses latest setting
- Backward compatible (won't break existing installs)

## See Also

- [Full Documentation](INTRO_CHANNEL_CONFIGURATION.md) - Detailed guide
- [Role Configuration](QUICK_START_CHANNEL_MANAGER.md) - Setting up roles
- [Admin Commands](README.md#admin-commands) - All admin commands

## Need Help?

1. Check current setting: `!getintrochannel`
2. Test role assignment: `!testrole <your message>`
3. Review bot permissions in Discord server settings
4. Check `roles.json` has the roles you want to assign

