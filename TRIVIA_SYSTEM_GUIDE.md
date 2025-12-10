# 🎯 Enhanced Trivia System Guide

## Overview
The Jule bot now features a comprehensive, stateful trivia system with difficulty levels, genre selection, and competitive modes!

## Features

### ✨ New Capabilities
- **Stateful Sessions** - Track your progress across multiple questions
- **Difficulty Levels** - Choose from Easy, Medium, Hard, or Expert
- **Genre Selection** - Pick from 15+ different categories
- **Competition Mode** - Challenge yourself with 10 consecutive questions
- **Score Tracking** - Real-time accuracy and points tracking
- **AI-Powered Questions** - Dynamic question generation using Gemini AI
- **Fallback Questions** - Static questions when AI is unavailable

---

## Commands

### 📝 Single Question Mode

**Basic Usage:**
```
!trivia
```
Asks a random medium-difficulty question from any genre.

**With Difficulty:**
```
!trivia easy
!trivia medium
!trivia hard
!trivia expert
```

**With Genre:**
```
!trivia science
!trivia history
!trivia technology
```

**With Both:**
```
!trivia hard science
!trivia easy history
!trivia expert mathematics
!trivia medium pop culture
```

### 🏆 Competition Mode (10 Questions)

**Start a Competition:**
```
!triviacomp
!tc  (short alias)
```

**With Difficulty:**
```
!triviacomp hard
!tc expert
```

**With Genre:**
```
!triviacomp medium science
!tc easy history
```

**Features:**
- Automatically asks 10 consecutive questions
- Tracks score throughout the session
- Shows progress (e.g., "Question 5/10")
- Displays comprehensive summary at the end
- Awards achievement badges for performance

### ⚙️ Management Commands

**End Current Session:**
```
!triviaend
!endtrivia
```
Stops your active trivia session and shows partial results if in competition mode.

**Get Help:**
```
!triviahelp
!th
```
Displays comprehensive guide with all options and genres.

---

## Difficulty Levels

| Difficulty | Points | Description |
|------------|--------|-------------|
| **Easy** | 5 pts | Common knowledge, accessible questions |
| **Medium** | 10 pts | General knowledge, moderate challenge |
| **Hard** | 15 pts | Challenging questions, specific knowledge |
| **Expert** | 20 pts | Very difficult, specialized knowledge |

---

## Available Genres

The system supports questions across these categories:

- 🔬 **Science** - Physics, Chemistry, Biology
- 📚 **History** - World history, events, figures
- 🌍 **Geography** - Countries, capitals, landmarks
- 💻 **Technology** - Computing, software, hardware
- 🔢 **Mathematics** - Algebra, geometry, arithmetic
- 🎨 **Art** - Paintings, artists, movements
- 📖 **Literature** - Books, authors, poetry
- ⚽ **Sports** - Athletes, teams, records
- 🎵 **Music** - Artists, songs, genres
- 🎬 **Movies** - Films, actors, directors
- 🌟 **General** - Mixed topics
- 🎭 **Pop Culture** - Entertainment, celebrities
- 🌿 **Nature** - Plants, ecosystems
- 🚀 **Space** - Astronomy, planets, cosmos
- 🐾 **Animals** - Wildlife, species, habitats

---

## How to Answer

You can answer in multiple ways:

**By Letter:**
```
A
B
C
D
```

**By Full Answer:**
```
Paris
The speed of light
Python
```

**Partial Matches:**
The system attempts to match partial answers to the correct option.

⏱️ **Time Limit:** 30 seconds per question

---

## Competition Mode Details

### Starting a Competition
- Choose difficulty and genre (optional)
- System automatically presents 10 questions
- Questions appear sequentially with 2-second breaks
- Cannot interrupt - must complete or end session

### During Competition
- **Progress Tracking** - "Question 5/10"
- **Current Score** - Shows correct answers so far
- **Automatic Flow** - Questions appear automatically

### End Summary
At completion, you'll receive:
- ✅ Total correct answers
- 📈 Accuracy percentage
- ⭐ Total points earned
- ⏱️ Time taken
- 🏅 Achievement badge (if earned)

### Achievement Badges
- 🏅 **Perfect Score** - 100% accuracy
- 🏅 **Excellent Performance** - 80%+ accuracy
- 🏅 **Good Job** - 60%+ accuracy

---

## Scoring System

### Points Calculation
Points are awarded based on difficulty:
- Easy questions: **5 points**
- Medium questions: **10 points**
- Hard questions: **15 points**
- Expert questions: **20 points**

### Competition Total
In a 10-question competition with medium difficulty:
- Maximum possible: **100 points** (10 × 10)
- Accuracy multiplier affects final score

---

## Examples

### Quick Easy Question
```
!trivia easy
```

### Science Challenge
```
!trivia hard science
```

### History Competition
```
!triviacomp medium history
```

### Expert Mathematics Marathon
```
!tc expert mathematics
```

### Mixed General Knowledge
```
!triviacomp hard
```

---

## Tips & Strategies

### 🎯 Maximizing Points
1. Start with your strong genres
2. Choose appropriate difficulty (challenge yourself!)
3. Use competitions for bigger point gains
4. Read questions carefully - no rush!

### 🧠 Improving Accuracy
1. Use the hint when provided
2. Eliminate obviously wrong answers
3. Don't second-guess yourself
4. Learn from explanations

### ⚡ Speed Tips
- Type single letters (A/B/C/D) for fastest answers
- Keep the chat window focused
- Read all options before answering

---

## Technical Details

### AI-Powered Generation
- Uses Gemini 2.5 Flash Lite model
- Generates dynamic questions with:
  - Multiple choice options
  - Detailed explanations
  - Contextual hints
  - Appropriate difficulty scaling

### Fallback System
- Static question bank for when AI is unavailable
- Organized by difficulty and genre
- Ensures uninterrupted gameplay

### Session Management
- Each user can have one active session
- Sessions auto-complete when finished
- Manual end available via `!triviaend`
- Sessions tracked in memory (reset on bot restart)

---

## Troubleshooting

**"You already have an active trivia session"**
- Complete your current session or use `!triviaend`

**"Failed to generate question"**
- AI service may be temporarily unavailable
- Try again - fallback questions will be used

**"Generated question was invalid"**
- Rare AI generation error
- Simply try the command again

**Questions seem too easy/hard**
- Adjust difficulty level in your command
- Try different genres that match your knowledge

---

## Future Enhancements (Coming Soon)

- 📊 **Personal Statistics** - Track your trivia history
- 🏆 **Leaderboards** - Compete with server members
- 🎲 **Random Mode** - Mixed difficulties and genres
- ⏰ **Timed Mode** - Speed bonus points
- 👥 **Multiplayer** - Compete head-to-head
- 🎁 **Daily Challenges** - Special rewards

---

## Command Quick Reference

| Command | Aliases | Description |
|---------|---------|-------------|
| `!trivia [diff] [genre]` | - | Single question |
| `!triviacomp [diff] [genre]` | `!tc` | 10-question competition |
| `!triviaend` | `!endtrivia` | End current session |
| `!triviahelp` | `!th` | Show this guide |

---

## Support

Having issues or suggestions? Contact the bot administrators or check the main help with `!help`.

Happy quizzing! 🎉

