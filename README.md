# Jule Bot

Jule is a comprehensive and robust Discord bot designed to enhance community engagement through a suite of interactive features, moderation tools, and AI-powered capabilities. Built with Python and discord.py, it serves as a reliable assistant for managing and enlivening your Discord server.

## Overview

This project aims to provide a powerful yet accessible experience for server members. It automates routine tasks, facilitates community interaction, and offers entertainment options, all while maintaining a user-friendly environment. The bot comes with an integrated web dashboard for easy monitoring.

## Unique Features & AI Capabilities

Jule sets itself apart with deep integration of Google's Gemini AI, going beyond simple chatbots to provide structural server management and intelligent content generation.

### AI-Powered Template Manager
One of Jule's most powerful features is the intelligent generation and management of server infrastructure.
- **Generative Configuration**: The bot can design entire role hierarchies or channel layouts based on a simple text description (e.g., "Create a layout for a competitive gaming community").
- **Zero-Touch Application**: Generated templates can be applied automatically, creating channels and roles while managing permissions.
- **Safety First**: Includes a robust backup and restore system, ensuring you can always revert changes if needed.

### Intelligent Context & Content
- **Smart Role Assignment**: The bot analyzes introduction messages to infer user interests and assigns appropriate roles automatically, reducing manual moderation overhead.
- **Structured Knowledge**: Unlike generic chat commands, Jule offers structured AI tools like `!debate` (generating balanced pros/cons), `!howto` (step-by-step guides), and `!quiz` (interactive learning).
- **Conversation Engine**: Capable of generating context-aware conversation starters and brainstorming sessions to keep community channels active.

## Features

### Community & Engagement
- **Welcome System**: Greets new members with custom embeds and helpful server information.
- **Birthday Tracking**: Remembers and celebrates member birthdays.
- **Engagement Points**: Activity-based point system to reward active community members.

### Entertainment & Games
- **Music Player**: Full-featured music playback system supporting queues and search (powered by Wavelink).
- **Mini-Games**: Includes interactive games like Rock-Paper-Scissors and Number Guessing.
- **Fun Commands**: Magic 8-Ball, random facts, and compliment generators.

### Utility & Moderation
- **Spam Detection**: Automated protection against message spam with temporary warnings and cleanup.
- **Reminders**: Custom reminder system for users.
- **Polls**: Easy-to-create polls for community feedback.
- **Admin Tools**: Various commands for server management and cleanup.

### Web Dashboard
- **Live Status**: Real-time monitoring of bot status.
- **Logs**: Viewable logs for bot and system activities.
- **Database Limits**: Visual representation of stored data.

## Command Reference

### Fun & Games
Interactive games and casual commands to keep the server lively.
- `!hello`: Say hello to Jule.
- `!roll [sides]`: Roll a dice (default 6 sides).
- `!flip`: Flip a coin.
- `!8ball [question]`: Ask the magic 8-ball a question.
- `!fact`: Get a random fun fact.
- `!compliment [@user]`: Give a compliment to yourself or someone else.
- `!choose <option1> <option2> ...`: Let Jule choose between options.
- `!encourage [@user]`: Send an encouraging message.
- `!rps <rock|paper|scissors>`: Play Rock, Paper, Scissors against the bot.
- `!guess`: Start a number guessing game (1-100).
- `!trivia [difficulty] [genre]`: Answer a trivia question (e.g., `!trivia hard science`).
- `!triviacomp [difficulty] [genre]`: Start a 10-question trivia competition.
- `!triviahelp`: Detailed help for the trivia system.
- `!triviastats [@user]`: View a user's trivia statistics.
- `!trivialeaderboard [type]`: View trivia leaderboards.
- `!scramble`: Unscramble a word for points.

### Music
High-quality music playback directly in voice channels.
- `!join`: Summon Jule to your voice channel.
- `!leave`: Disconnect the bot.
- `!play <query|url>`: Search for or play a song/URL.
- `!pause`: Pause current playback.
- `!resume`: Resume playback.
- `!skip`: Skip the current song.
- `!queue`: Show the current music queue.
- `!clearqueue`: Remove all songs from the queue.
- `!nowplaying`: Show details about the current song.
- `!shuffle`: Shuffle the queue.
- `!loop`: Toggle song looping.
- `!musicstats`: View your personal music listening stats.
- `!musicleaderboard`: View the server's top listeners.

### AI & Knowledge
Powered by Google Gemini to answer questions and generate ideas.
- `!ask <question>`: Ask the AI any question.
- `!explain <topic>`: Get a simple explanation of a topic.
- `!wiki <query>`: Search Wikipedia for a summary.
- `!topicstarter [theme]`: Generate conversation starters.
- `!compare <item1> vs <item2>`: Compare two things.
- `!summarize <topic>`: Get a concise summary of a subject.
- `!debate <topic>`: Generate arguments for and against a topic.
- `!brainstorm <topic>`: Generate creative ideas.
- `!howto <task>`: Get a step-by-step guide.
- `!quiz [topic]`: Generate a multiple-choice quiz question.
- `!translate <language> <text>`: Translate text to another language.

### Community
Tools for engagement and member recognition.
- `!points [@user]`: Check community points.
- `!leaderboard`: View the top active members.
- `!birthday <month> <day>`: Set your birthday (e.g., `!birthday 5 20`).
- `!birthdays`: Check for upcoming birthdays.

### Utilities
Helpful tools for information and scheduling.
- `!poll <question> <option1> <option2> ...`: Create a poll with reactions.
- `!remind <minutes> <message>`: Set a reminder for yourself.
- `!serverinfo`: Display server statistics.
- `!userinfo [@user]`: Display detailed user information.
- `!avatar [@user]`: View a user's avatar in full size.

### Administration
Advanced tools for server management and configuration. *Requires Admin permissions.*
- `!announce <message>`: Send a formal announcement embed.
- `!clear <amount>`: Bulk delete messages.
- `!setintrochannel [#channel]`: Set the channel for auto-role assignment on introductions.
- `!getintrochannel`: Check which channel is currently set for intros.
- `!testrole <message>`: Test the AI role assignment logic without saving.
- `!syncroles [file]`: Sync server roles from a YAML configuration file.
- `!syncchannels [file]`: Sync server channels from a YAML configuration file.
- `!reloadroles`: Reload the role configuration mapping.

#### Template Manager
AI-powered system to generate and apply server layouts.
- `!genroles <description>`: Generate a roles structure using AI.
- `!genchannels <description>`: Generate a channel layout using AI.
- `!applyroles <file> confirm`: Apply a generated roles template.
- `!applychannels <file> confirm`: Apply a generated channel template.
- `!listtemplates`: List all available YAML templates.
- `!listbackups`: List backups of previous configurations.
- `!reverttemplate <backup> confirm`: Restore a previous configuration.
- `!activetemplate`: Check currently active configuration files.

## Getting Started

### Prerequisites
- Python 3.8 or higher, preferably 3.10+
- A Discord Bot Token
- A Google Gemini API Key

### Installation

1. **Clone the repository**
   Download the source code to your local machine.

2. **Environment Configuration**
   Create a `.env` file in the `src/` directory with the following credentials:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   Note: Verify that `src/constants.py` matches your desired configuration for channel IDs and role IDs.

3. **Data Directories**
   Ensure the following directories exist (they will be created automatically by the start script):
   - `src/data/`: For the SQLite database.
   - `src/config/`: For JSON/YAML configurations.

### Running the Bot

The project includes a startup script that handles virtual environment creation and dependency installation automatically.

**Run the startup script:**
```bash
./start.sh
```

This script will:
1. Create a Python virtual environment (`.venv`) if one does not exist.
2. Install all required dependencies from `requirements.txt`.
3. Initialize the database.
4. Launch the Discord Bot.
5. Launch the Web Dashboard on port 8080 (default).

## Output Logs
- **Bot Logs**: `bot.log`
- **Dashboard Logs**: `dashboard.log`

## Project Structure
- `src/bot.py`: Main entry point for the Discord bot.
- `dashboard.py`: Entry point for the Flask web dashboard.
- `src/cogs/`: Directory containing bot extensions (commands and listeners).
- `src/model/`: Database models and service layers.
- `src/constants.py`: Central configuration file.

## License
This project is open for private and educational use.
