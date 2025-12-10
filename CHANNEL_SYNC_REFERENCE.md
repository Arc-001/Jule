# 📢 Channel Manager Quick Reference

## What is Channel Sync?

The `!syncchannels` command allows administrators to automatically create and organize Discord channels using a YAML configuration file. It's perfect for:

- 🚀 Setting up new servers
- 🔄 Standardizing channel structure
- 📋 Managing large channel lists
- 🎨 Creating themed server layouts

---

## Basic Usage

```bash
# Use default channels.yaml
!syncchannels

# Use a specific YAML file
!syncchannels channels_minimal_test.yaml

# Use custom configuration
!syncchannels my_custom.yaml
```

**Note:** Only administrators can use this command!

---

## What It Does

1. ✅ **Creates missing categories** based on YAML config
2. ✅ **Creates missing channels** in each category
3. ✅ **Updates channel descriptions** if changed
4. ✅ **Finds existing channels** (no duplicates!)
5. ✅ **Exports channel IDs** to `current_channels.json`
6. ✅ **Provides detailed feedback** with statistics

---

## Features

### Smart Sync
- Detects existing channels by name
- Updates descriptions without recreating
- Preserves channel IDs in JSON export
- No duplicate channels created on re-run

### Statistics Report
After running, you get a detailed embed showing:
- Categories created vs found
- Channels created vs found vs updated
- Total channels mapped
- Any errors encountered

### Clean Names
Channel IDs are exported with cleaned names:
- `📢・announcements` → `announcements`
- `🤖・bot-testing` → `bottesting`
- Emojis and special chars removed
- Perfect for bot code references

---

## Example Output

```
🌌 Channel Synchronization Complete

📁 Categories
✨ Created: 3 | ✅ Found: 0

📺 Channels
✨ Created: 8 | ✅ Found: 2 | 📝 Updated: 1

💾 Channel Mapping
Saved 10 channel IDs to current_channels.json
```

---

## Using Channel IDs in Code

After syncing, use the exported IDs:

```python
# Load the channel mapping
with open('src/config/current_channels.json', 'r') as f:
    channels = json.load(f)

# Get channel IDs
announcements_id = channels['announcements']
bottesting_id = channels['bottesting']

# Use in your bot
channel = bot.get_channel(announcements_id)
await channel.send("Hello!")
```

---

## YAML File Format

### Basic Structure

```yaml
categories:
  Category Name:
    channels:
      - name: "📢・channel-name"
        type: "text"
        description: "Channel description"
      
      - name: "🔊・voice-channel"
        type: "voice"

standalone:
  - name: "🌟・standalone-channel"
    type: "text"
    description: "Channel without a category"
```

### Channel Types
- `text` - Text channel (default)
- `voice` - Voice channel

---

## Available Templates

### 1. Minimal Test (`channels_minimal_test.yaml`)
Perfect for testing! Creates:
- 🚀 Mission Control (2 channels)
- 🌌 Launch Bay (3 channels)  
- 🎤 Voice Hangar (1 channel)
- 1 standalone channel

**Use for:** Testing the sync feature

### 2. Full Template (`channels.yaml`)
Complete server structure with multiple categories

**Use for:** Production servers

---

## Permissions Required

### Bot Needs:
- ✅ Manage Channels
- ✅ Manage Roles (for role sync)

### User Needs:
- ✅ Administrator permission

---

## Common Use Cases

### 1. Fresh Server Setup
```bash
!syncchannels channels.yaml
```
Creates entire server structure from scratch!

### 2. Update Descriptions
Edit YAML file → Change descriptions → Run sync
```bash
!syncchannels
```

### 3. Add New Channels
Add to YAML → Run sync → New channels appear!

### 4. Testing Changes
```bash
!syncchannels channels_minimal_test.yaml
```
Test on small structure first

---

## Troubleshooting

### ❌ "Configuration file not found"
**Solution:** File must be in `src/config/` directory

### ❌ "Missing permissions"
**Solution:** Ensure bot role is high in role hierarchy

### ❌ "YAML parsing error"
**Solution:** Check YAML syntax (indentation matters!)

### ❌ Channels created but not in right category
**Solution:** Check YAML indentation under categories

---

## Pro Tips

### 🎯 Best Practices
1. **Test first** with minimal template
2. **Backup** your YAML before editing
3. **Run sync** after any YAML changes
4. **Use emojis** for visual organization
5. **Keep names** consistent (lowercase, hyphens)

### 🚀 Advanced
- Create multiple YAML files for different setups
- Use version control (git) for YAML files
- Export `current_channels.json` to use in other bots
- Combine with `!syncroles` for complete setup

---

## Integration with Bot Code

### Auto-Updating Constants

```python
# constants.py
import json

def load_channels():
    with open('src/config/current_channels.json', 'r') as f:
        return json.load(f)

CHANNELS = load_channels()
GREET_CHANNEL_ID = CHANNELS.get('general', 0)
```

### Dynamic Channel Access

```python
# In your bot code
CHANNEL_MAPPINGS = load_json_config('src/config/current_channels.json')

async def send_to_channel(channel_key: str, message: str):
    channel_id = CHANNEL_MAPPINGS.get(channel_key)
    if channel_id:
        channel = bot.get_channel(channel_id)
        await channel.send(message)

# Usage
await send_to_channel('announcements', 'Hello everyone!')
```

---

## Related Commands

```bash
!syncroles              # Sync role configuration
!reloadroles            # Reload role mappings
!testrole <message>     # Test role assignment
```

---

## Complete Workflow Example

### 1. Setup
```bash
# Admin runs initial sync
!syncchannels channels.yaml
```

### 2. Verify
Check Discord - all channels created!
Check `src/config/current_channels.json` - IDs exported!

### 3. Use in Bot
Bot automatically uses new channel IDs from JSON

### 4. Update Later
Edit YAML → `!syncchannels` → Changes applied!

---

## Safety Features

- ❌ **Never deletes** existing channels
- ❌ **Never modifies** channel permissions
- ❌ **Never changes** channel position
- ✅ **Only creates** missing channels
- ✅ **Only updates** descriptions
- ✅ **Preserves** all channel settings

---

## Performance

- ⚡ Fast: Creates 10 channels in ~5 seconds
- 🔄 Smart: Finds existing channels instantly
- 💾 Efficient: Single JSON export
- 📊 Detailed: Complete statistics report

---

## Need Help?

1. Check YAML syntax: https://yaml.org/
2. Review templates in `src/config/`
3. Test with minimal template first
4. See full guide: `CHANNEL_MANAGER_DOCS.md`
5. Quick start: `QUICK_START_CHANNEL_MANAGER.md`

---

**Happy Channel Managing!** 🎉📢

*Use `!help syncchannels` for command syntax*

