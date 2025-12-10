# Quick Start Guide - Testing Channel Manager

## Prerequisites

1. **Bot is running** and connected to Discord
2. **You have Administrator permissions** on the test server
3. **Bot has permissions**: Manage Channels, Manage Roles

## Quick Test Steps

### Step 1: Start with Minimal Template

Run this command in your Discord server:

```
!syncchannels channels_minimal_test.yaml
```

This will create a minimal space-themed server structure for testing.

### Step 2: Verify Results

You should see:
- ✅ An embed showing statistics (categories/channels created)
- ✅ New channels appearing in your server
- ✅ File `src/config/current_channels.json` created with channel IDs

### Step 3: Check the JSON Output

```bash
cat src/config/current_channels.json
```

Example output:
```json
{
  "announcements": 1234567890123456789,
  "info": 1234567890123456790,
  "general": 1234567890123456791,
  "introductions": 1234567890123456792,
  "bottesting": 1234567890123456793,
  "generalvoice": 1234567890123456794,
  "highlights": 1234567890123456795
}
```

### Step 4: Test Re-sync (Update Existing)

Edit `channels_minimal_test.yaml` - change a description:

```yaml
- name: "💬・general"
  type: "text"
  description: "General chat - NOW WITH NEW DESCRIPTION!"  # Changed
```

Run again:
```
!syncchannels channels_minimal_test.yaml
```

You should see:
- ✅ Existing channels found (not duplicated)
- ✅ Channel description updated
- ✅ No new channels created

### Step 5: Test Full Template

Once minimal test works, try the full template:

```
!syncchannels channels.yaml
```

This creates a more complete server structure.

## Expected Channel Structure (Minimal)

After running the minimal test, you should have:

```
🚀 Mission Control
  ├─ 📢・announcements
  └─ 📋・info

🌌 Launch Bay
  ├─ 💬・general
  ├─ 👋・introductions
  └─ 🤖・bot-testing

🎤 Voice Hangar
  └─ 🔊・General Voice

(No Category)
  └─ 🌟・highlights
```

## Testing Other Commands

Once channels are set up, test other bot commands:

```
# In bot-testing channel:
!help
!ping
!rps rock
!guess
```

## Troubleshooting Quick Checks

**Command doesn't work?**
```bash
# Check if bot is running
ps aux | grep bot.py

# Check bot logs
tail -f /path/to/bot.log
```

**Permission errors?**
- Ensure bot role is high in server role hierarchy
- Check bot has "Manage Channels" permission
- Verify you have Administrator permission

**YAML file not found?**
```bash
# List config files
ls -la src/config/

# Check YAML syntax
python3 -c "import yaml; print(yaml.safe_load(open('src/config/channels_minimal_test.yaml')))"
```

## Cleanup (Optional)

To remove all test channels:
1. Right-click each category
2. Select "Delete Category"
3. Confirm deletion (deletes all channels in category)

Or keep them for further testing!

## Next Steps

1. **Customize**: Create your own YAML template
2. **Integrate**: Use `current_channels.json` in your bot code
3. **Deploy**: Use full template for production server
4. **Maintain**: Re-run sync when adding new channels

## Command Summary

```
!syncchannels                          # Uses channels.yaml (default)
!syncchannels channels_minimal_test.yaml   # Uses minimal test template
!syncchannels my_custom.yaml           # Uses custom template
```

## Visual Example

Before:
```
Your Server
  ├─ general
  ├─ random
  └─ voice
```

After `!syncchannels channels_minimal_test.yaml`:
```
Your Server
  ├─ 🚀 Mission Control
  │   ├─ 📢・announcements
  │   └─ 📋・info
  ├─ 🌌 Launch Bay
  │   ├─ 💬・general
  │   ├─ 👋・introductions
  │   └─ 🤖・bot-testing
  ├─ 🎤 Voice Hangar
  │   └─ 🔊・General Voice
  ├─ 🌟・highlights
  ├─ general (old)
  ├─ random (old)
  └─ voice (old)
```

*Note: Old channels remain untouched*

## Success Indicators

✅ Embed shows "Channel Synchronization Complete"
✅ Categories appear in server
✅ Channels have correct emojis and names
✅ `current_channels.json` exists and contains IDs
✅ Re-running command doesn't duplicate channels
✅ Channel descriptions match YAML file

Happy testing! 🚀

