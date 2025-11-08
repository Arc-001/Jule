# 🤖 Jule - Your Cozy Community Bot

A friendly and feature-rich Discord bot designed specifically for small, cozy communities. Jule brings warmth, fun, and engagement to your server!

## ✨ Features

### 🎮 Fun Commands
- **!hello** - Get a warm greeting from Jule
- **!roll [sides]** - Roll a dice (default 6 sides)
- **!flip** - Flip a coin
- **!8ball [question]** - Ask the magic 8-ball anything
- **!fact** - Get a random fun fact
- **!compliment [@user]** - Give or receive compliments
- **!choose [options...]** - Let Jule decide for you

### 🎯 Interactive Games
- **!rps [rock/paper/scissors]** - Play rock-paper-scissors with Jule
- **!guess** - Number guessing game (earn points!)

### 🏆 Community Engagement
- **!points [@user]** - Check community points
- **!leaderboard** - See top community contributors
- **!encourage [@user]** - Send encouragement to members
- **!birthday [month] [day]** - Set your birthday
- **!birthdays** - See today's birthdays

### 🛠️ Utility Commands
- **!poll "Question" [options...]** - Create interactive polls
- **!remind [minutes] [message]** - Set reminders (up to 24 hours)
- **!serverinfo** - Get server statistics
- **!avatar [@user]** - View someone's avatar
- **!userinfo [@user]** - Get detailed user information

### 👑 Admin Commands
- **!announce [message]** - Make beautiful announcements (Admin only)
- **!clear [amount]** - Clear messages (Manage Messages permission)

## 🎨 Special Features

### Natural Language Interaction
Jule responds naturally when you:
- Say "hey jule", "hi jule", or "hello jule"
- Thank Jule with "thanks jule" or "thank you jule"
- Say "good bot" for a sweet response

### Automatic Features
- **Welcome Messages** - Beautiful embeds for new members
- **Auto Roles** - Assigns default role to new members
- **Random Reactions** - 5% chance to react to messages with emojis
- **Points System** - Earn points by being active (1 point per 10 messages)
- **Activity Tracking** - Keeps track of community engagement

## 🚀 Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token
- Discord Server with proper permissions

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Jule
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_discord_bot_token_here
```

4. Update the channel and role IDs in `src/bot.py`:
```python
GREET_CHANNEL_ID = your_greet_channel_id
DEFAULT_ROLE_ID = your_default_role_id
```

### Running the Bot

```bash
python src/bot.py
```

## 🎯 Configuration

Edit these constants in `bot.py` to customize:
- `GREET_CHANNEL_ID` - Channel for welcome messages
- `DEFAULT_ROLE_ID` - Role assigned to new members
- `GREETINGS` - Custom greeting messages
- `ENCOURAGEMENTS` - Custom encouragement messages
- `RANDOM_FACTS` - Fun facts to share

## 🤝 Perfect for Small Communities

This bot is specifically designed for small, cozy communities with features that:
- Encourage participation through points and leaderboards
- Keep members engaged with fun games and commands
- Foster positivity with compliments and encouragement
- Maintain organization with polls and announcements
- Build community through personalized interactions

## 💡 Tips for Maximum Engagement

1. **Use polls** for community decisions
2. **Encourage participation** with the points system
3. **Celebrate milestones** with the leaderboard
4. **Keep it fun** with games and random facts
5. **Stay organized** with reminders and announcements

## 📝 Command Prefix

All commands use the `!` prefix. For a full list of commands, use `!help` in your Discord server.

## 🐛 Error Handling

Jule includes comprehensive error handling for:
- Missing arguments
- Missing permissions
- Invalid commands
- General errors

## 🌟 What Makes Jule Special?

- **Personality** - Friendly, warm, and engaging
- **Visual Appeal** - Beautiful embeds for all features
- **Community Focus** - Built for small, tight-knit groups
- **Easy to Use** - Intuitive commands and helpful messages
- **Active Engagement** - Random reactions and natural responses
- **Gamification** - Points system to reward participation

## 📄 License

This project is open source and available for your community needs!

## 💬 Support

For issues or questions, feel free to open an issue or reach out to the development team.

---

Made with ❤️ for cozy communities
# 🤖 Jule - Your Cozy Community Bot

A friendly and feature-rich Discord bot designed specifically for small, cozy communities. Jule brings warmth, fun, and engagement to your server with **persistent SQLite storage** and **intelligent spam detection**!

## ✨ Features

### 🛡️ Automatic Spam Protection
- **Smart Detection**: Identifies rapid message spam (5+ messages in 20 seconds)
- **Auto-Cleanup**: Automatically deletes spam messages
- **Logged Events**: All spam detection logged for review
- **Zero Config**: Works out of the box!

### 💾 Persistent Data Storage
- **SQLite Database**: All data survives bot restarts
- **User Points**: Points and message counts preserved
- **Reminders**: Set reminders that persist
- **Birthdays**: Never forget a community member's birthday
- **Spam Logs**: Full audit trail of moderation actions

### 🎮 Fun Commands
- **!hello** - Get a warm greeting from Jule
- **!roll [sides]** - Roll a dice (default 6 sides)
- **!flip** - Flip a coin
- **!8ball [question]** - Ask the magic 8-ball anything
- **!fact** - Get a random fun fact
- **!compliment [@user]** - Give or receive compliments
- **!choose [options...]** - Let Jule decide for you

### 🎯 Interactive Games
- **!rps [rock/paper/scissors]** - Play rock-paper-scissors with Jule
- **!guess** - Number guessing game (earn points!)

### 🏆 Community Engagement
- **!points [@user]** - Check community points
- **!leaderboard** - See top community contributors
- **!encourage [@user]** - Send encouragement to members

### 🛠️ Utility Commands
- **!poll "Question" [options...]** - Create interactive polls
- **!remind [minutes] [message]** - Set reminders (up to 24 hours)
- **!serverinfo** - Get server statistics
- **!avatar [@user]** - View someone's avatar
- **!userinfo [@user]** - Get detailed user information

### 👑 Admin Commands
- **!announce [message]** - Make beautiful announcements (Admin only)
- **!clear [amount]** - Clear messages (Manage Messages permission)

## 🎨 Special Features

### Natural Language Interaction
Jule responds naturally when you:
- Say "hey jule", "hi jule", or "hello jule"
- Thank Jule with "thanks jule" or "thank you jule"
- Say "good bot" for a sweet response

### Automatic Features
- **Welcome Messages** - Beautiful embeds for new members
- **Auto Roles** - Assigns default role to new members
- **Random Reactions** - 5% chance to react to messages with emojis
- **Points System** - Earn points by being active (1 point per 10 messages)
- **Activity Tracking** - Keeps track of community engagement

## 🚀 Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token
- Discord Server with proper permissions

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Jule
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_discord_bot_token_here
```

4. Update the channel and role IDs in `src/bot.py`:
```python
GREET_CHANNEL_ID = your_greet_channel_id
DEFAULT_ROLE_ID = your_default_role_id
```

### Running the Bot

```bash
python src/bot.py
```

## 🎯 Configuration

Edit these constants in `bot.py` to customize:
- `GREET_CHANNEL_ID` - Channel for welcome messages
- `DEFAULT_ROLE_ID` - Role assigned to new members
- `GREETINGS` - Custom greeting messages
- `ENCOURAGEMENTS` - Custom encouragement messages
- `RANDOM_FACTS` - Fun facts to share

## 🤝 Perfect for Small Communities

This bot is specifically designed for small, cozy communities with features that:
- Encourage participation through points and leaderboards
- Keep members engaged with fun games and commands
- Foster positivity with compliments and encouragement
- Maintain organization with polls and announcements
- Build community through personalized interactions

## 💡 Tips for Maximum Engagement

1. **Use polls** for community decisions
2. **Encourage participation** with the points system
3. **Celebrate milestones** with the leaderboard
4. **Keep it fun** with games and random facts
5. **Stay organized** with reminders and announcements

## 📝 Command Prefix

All commands use the `!` prefix. For a full list of commands, use `!help` in your Discord server.

## 🐛 Error Handling

Jule includes comprehensive error handling for:
- Missing arguments
- Missing permissions
- Invalid commands
- General errors

## 🌟 What Makes Jule Special?

- **Personality** - Friendly, warm, and engaging
- **Visual Appeal** - Beautiful embeds for all features
- **Community Focus** - Built for small, tight-knit groups
- **Easy to Use** - Intuitive commands and helpful messages
- **Active Engagement** - Random reactions and natural responses
- **Gamification** - Points system to reward participation

## 📄 License

This project is open source and available for your community needs!

## 💬 Support

For issues or questions, feel free to open an issue or reach out to the development team.

---

Made with ❤️ for cozy communities

