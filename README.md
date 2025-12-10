# Jule Discord Bot 

A friendly, feature-rich Discord bot with AI-powered commands, music playback, community features, and more!

## Features

### AI Commands
- **Ask AI**: Conversational AI assistant using Google Gemini
- **Wikipedia Integration**: Quick information lookup
- **Explanations**: Get simple explanations of complex topics
- **Brainstorming**: Generate creative ideas
- **Quizzes**: Interactive quiz questions
- **Translations**: Multi-language text translation
- **Debates**: Generate balanced debate points
- **And more!** See [AI_COMMANDS.md](AI_COMMANDS.md) for full documentation

### Music Commands
- Play music from YouTube with search functionality
- Queue management (add, skip, clear, shuffle)
- Music statistics and leaderboards
- Auto-disconnect after inactivity

### Game Commands
- Truth or Dare
- Would You Rather
- 8Ball predictions
- Trivia questions

### Fun Commands
- Random jokes and facts
- Compliments
- Dad jokes
- Memes

### Community Commands
- User profiles and stats
- Leaderboards
- Birthday tracking
- Point system
- Introduction role assignment using AI

###  Utility Commands
- Polls with reactions
- Reminders
- Server information
- User avatars
- Birthday management

### Admin Commands
- Clear messages
- User warnings
- **AI Template Manager**: Generate and manage server roles/channels with AI
  - Generate custom templates from natural language descriptions
  - Safely apply templates with automatic backups
  - Revert to previous configurations
  - See [AI_TEMPLATE_MANAGER_GUIDE.md](AI_TEMPLATE_MANAGER_GUIDE.md) for details
- Kick/ban users
- Announcement system

## Setup

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Google Gemini API Key (for AI commands)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Jule
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Configure channels and roles**
   
   Edit `src/config/channels.json` and `src/config/roles.json` with your server's IDs.

6. **Run the bot**
   ```bash
   python src/bot.py
   ```

   Or use the start script:
   ```bash
   ./start.sh
   ```

## Getting API Keys

### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the token
5. Enable all Privileged Gateway Intents

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

## Configuration

### Channel IDs
Edit `src/constants.py` to set:
- `GREET_CHANNEL_ID`: Channel for welcome messages
- `MUSIC_CHANNEL_ID`: Channel for music commands (optional)

### Role IDs
Edit `src/constants.py` to set:
- `DEFAULT_ROLE_ID`: Role assigned to new members

### Channel Mappings
Edit `src/config/channels.json`:
```json
{
  "intro": 1234567890,
  "music": 1234567890,
  "general": 1234567890
}
```

### Role Mappings
Edit `src/config/roles.json` for AI-powered role assignment:
```json
{
  "developer": 1234567890,
  "gamer": 1234567890,
  "artist": 1234567890
}
```

## Command Reference

### Quick Command List

#### AI Commands
```
!ask <question>          - Ask the AI anything
!explain <topic>         - Get simple explanations
!wiki <query>            - Search Wikipedia
!topicstarter [theme]    - Generate conversation starters
!brainstorm <topic>      - Generate creative ideas
!quiz [topic]            - Interactive quiz questions
!aifact [category]       - AI-generated interesting facts
!howto <task>            - Step-by-step guides
!compare <A> vs <B>      - Compare two things
!debate <topic>          - Generate debate points
!summarize <topic>       - Get concise summaries
!translate <lang> <text> - Translate text
!dailychallenge [cat]    - Get daily challenges
!clearcontext            - Clear AI conversation history
```

#### Music Commands
```
!join                    - Join your voice channel
!leave                   - Leave voice channel
!music <query>           - Search and play music
!pause                   - Pause playback
!resume                  - Resume playback
!skip                    - Skip current song
!queue                   - Show music queue
!clearqueue              - Clear the queue
!loop                    - Toggle loop mode
!nowplaying              - Show current song
!shuffle                 - Shuffle queue
!musicstats [@user]      - Show music statistics
!musicleaderboard        - Top music listeners
```

#### Fun Commands
```
!hello                   - Greet Jule
!joke                    - Get a random joke
!dadjoke                 - Get a dad joke
!fact                    - Random fact
!8ball <question>        - Magic 8-ball
!compliment [@user]      - Give a compliment
```

#### Community Commands
```
!profile [@user]         - View user profile
!leaderboard             - Top users by points
!setbio <bio>            - Set your bio
!birthday <MM/DD>        - Set your birthday
```

#### Utility Commands
```
!poll "question" opt1 opt2...  - Create a poll
!remind <minutes> <msg>         - Set a reminder
!serverinfo                     - Server information
!avatar [@user]                 - View avatar
```

#### Admin Commands (Requires Permissions)
```
!clear <amount>          - Clear messages
!warn @user <reason>     - Warn a user
!kick @user <reason>     - Kick a user
!ban @user <reason>      - Ban a user
!announce <message>      - Send announcement
```

## Features in Detail

### AI-Powered Role Assignment
When users post in the introduction channel, the bot:
1. Analyzes their introduction using Gemini AI
2. Suggests appropriate roles based on interests
3. Automatically assigns matched roles
4. Sends a welcome message with assigned roles

### Music System
- YouTube search with multiple results
- Smart queue management
- Listening statistics tracking
- Leaderboards for top listeners
- Auto-disconnect after 5 minutes of inactivity

### Points System
- Earn points by chatting (1 point per 10 messages)
- View your rank on the leaderboard
- Track message count and activity

### Birthday System
- Set your birthday
- Automatic birthday notifications
- View upcoming birthdays

## Development

### Project Structure
```
Jule/
├── src/
│   ├── bot.py              # Main bot entry point
│   ├── constants.py        # Configuration constants
│   ├── services.py         # Core services
│   ├── utils.py            # Utility functions
│   ├── cogs/               # Command modules
│   │   ├── admin_commands.py
│   │   ├── ai_commands.py        
│   │   ├── community_commands.py
│   │   ├── fun_commands.py
│   │   ├── game_commands.py
│   │   ├── music_commands.py
│   │   └── utility_commands.py
│   ├── model/              # Database models
│   │   ├── model.py
│   │   ├── services.py
│   │   └── role_assigner.py
│   └── config/             # Configuration files
│       ├── channels.json
│       └── roles.json
├── data/
│   └── jule.db            # SQLite database
├── dashboard/             # Web dashboard (optional)
└── requirements.txt       # Python dependencies
```

### Adding New Commands

1. Create or edit a cog file in `src/cogs/`
2. Use the `@commands.command()` decorator
3. Add the cog to `bot.py` in the `load_extensions()` function

Example:
```python
@commands.command(name="example", help="An example command")
async def example(self, ctx: commands.Context):
    await ctx.send("This is an example!")
```

## Dashboard (Optional)

The bot includes a web dashboard for statistics:

```bash
python dashboard.py
```

Access at `http://localhost:5000`

## Testing

Use the provided test script for AI commands:
```bash
./test_ai_commands.sh
```

Or test individual commands in Discord:
```
!ask Hello! Can you introduce yourself?
!wiki Discord bot
!topicstarter
```

## Troubleshooting

### Bot not responding
- Check if bot is online
- Verify command prefix is `!`
- Ensure bot has necessary permissions

### AI commands not working
- Verify `GEMINI_API_KEY` is set in `.env`
- Check API key validity
- Ensure internet connectivity

### Music not playing
- Verify voice channel permissions
- Check FFmpeg installation
- Ensure yt-dlp is up to date

### Database errors
- Delete `data/jule.db` to reset (will lose data)
- Check file permissions
- Verify SQLite is installed

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Credits

- Discord.py library
- Google Gemini AI
- yt-dlp for music extraction
- Wikipedia API

