# 🚀 Quick Start Guide for Jule

## First Time Setup

### 1. Get Your Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the token

### 2. Invite Bot to Your Server
1. Go to OAuth2 → URL Generator
2. Select these scopes:
   - `bot`
   - `applications.commands`
3. Select these bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Attach Files
   - Add Reactions
   - Manage Messages
   - Manage Roles
   - Read Message History
4. Copy the generated URL and open it in your browser
5. Select your server and authorize

### 3. Configure the Bot

Edit `src/bot.py` and update:
```python
GREET_CHANNEL_ID = your_channel_id_here
DEFAULT_ROLE_ID = your_role_id_here
```

**To get IDs:**
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click on channels/roles and select "Copy ID"

### 4. Set Up Environment

Create a `.env` file:
```bash
echo "DISCORD_TOKEN=your_token_here" > .env
```

### 5. Install and Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python src/bot.py
```

## Testing Your Bot

Once running, try these commands in your server:

1. `!hello` - Basic greeting
2. `!help` - See all commands
3. `!roll` - Roll a dice
4. `!fact` - Get a fun fact
5. `!poll "Pizza or Pasta?" Pizza Pasta` - Create a poll

## Customization Ideas

### Change Bot Personality
Edit these lists in `bot.py`:
- `GREETINGS` - Welcome messages
- `ENCOURAGEMENTS` - Positive messages
- `RANDOM_FACTS` - Fun facts to share

### Add More Commands
Follow the pattern:
```python
@bot.command(name="mycommand", help="Description")
async def mycommand(ctx):
    await ctx.send("Response!")
```

### Adjust Point System
Change this line in `on_message`:
```python
if bot.user_messages[message.author.id] % 10 == 0:  # Change 10 to any number
    bot.user_points[message.author.id] += 1  # Change point value
```

## Common Issues

### Bot doesn't respond
- Check if bot is online in server members list
- Verify bot has "Send Messages" permission in channels
- Make sure you're using the correct command prefix (`!`)

### Welcome messages not showing
- Verify `GREET_CHANNEL_ID` is correct
- Ensure bot has permissions in that channel

### Roles not assigned
- Check `DEFAULT_ROLE_ID` is correct
- Verify bot's role is higher than the role it's trying to assign
- Ensure bot has "Manage Roles" permission

## Tips for Your Community

1. **Pin the help message** - Use `!help` and pin it for easy reference
2. **Introduce the bot** - Post about Jule's features in your server
3. **Encourage games** - Use `!guess` and `!rps` to get members engaged
4. **Use polls** - Make community decisions with `!poll`
5. **Celebrate milestones** - Post the `!leaderboard` regularly

## Next Steps

- Customize greeting messages
- Add your own fun facts
- Create polls for community input
- Set up announcements for events
- Encourage members to earn points

---

Need help? Check the full README.md for detailed documentation!

