"""
Game commands cog for Jule bot
Handles interactive games
"""

import random
import asyncio
import discord
from discord.ext import commands
from typing import List, Dict, Optional
from datetime import datetime

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    RPS_CHOICES, RPS_EMOJI_MAP, RPS_WIN_POINTS,
    GUESS_MIN, GUESS_MAX, GUESS_ATTEMPTS, GUESS_TIMEOUT, GUESS_WIN_POINTS,
    GEMINI_API_KEY
)
from model.services import PointsService

# Add these imports (keep concise)
import json
import re
import google.generativeai as genai


class TriviaSession:
    """Tracks a trivia session for a user"""
    def __init__(self, user_id: int, difficulty: str = "medium", genre: str = "general",
                 is_competition: bool = False, total_questions: int = 1):
        self.user_id = user_id
        self.difficulty = difficulty.lower()
        self.genre = genre
        self.is_competition = is_competition
        self.total_questions = total_questions
        self.current_question = 0
        self.correct_answers = 0
        self.total_points = 0
        self.start_time = datetime.now()
        self.questions_answered = []

    def record_answer(self, correct: bool, points: int):
        """Record an answer"""
        self.current_question += 1
        if correct:
            self.correct_answers += 1
            self.total_points += points
        self.questions_answered.append(correct)

    def is_complete(self) -> bool:
        """Check if the session is complete"""
        return self.current_question >= self.total_questions

    def get_summary(self) -> str:
        """Get session summary"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        accuracy = (self.correct_answers / self.total_questions * 100) if self.total_questions > 0 else 0

        summary = f"""
**📊 Trivia Session Complete!**
━━━━━━━━━━━━━━━━━━━━━━
✅ Correct: {self.correct_answers}/{self.total_questions}
📈 Accuracy: {accuracy:.1f}%
⭐ Total Points: {self.total_points}
⏱️ Time: {elapsed:.1f}s
🎯 Difficulty: {self.difficulty.title()}
📚 Genre: {self.genre.title()}
"""
        return summary


class GameCommands(commands.Cog):
    """Interactive game commands"""

    def __init__(self, bot: commands.Bot, points_service: PointsService, game_stats_service):
        self.bot = bot
        self.points_service = points_service
        self.game_stats_service = game_stats_service

        # Track active trivia sessions
        self.active_trivia_sessions: Dict[int, TriviaSession] = {}

        # Configure Gemini if API key is present
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')
            except Exception as e:
                print(f"Warning: Failed to configure Gemini model: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None

    @commands.command(name="rps", help="Play rock paper scissors! Usage: !rps <rock/paper/scissors>")
    async def rps(self, ctx: commands.Context, choice: str):
        """Play rock, paper, scissors"""
        choice = choice.lower()

        if choice not in RPS_CHOICES:
            await ctx.send("Choose rock, paper, or scissors! 🪨📄✂️")
            return

        bot_choice = random.choice(RPS_CHOICES)

        # Determine winner
        if choice == bot_choice:
            result = "It's a tie! 🤝"
        elif (choice == "rock" and bot_choice == "scissors") or \
             (choice == "paper" and bot_choice == "rock") or \
             (choice == "scissors" and bot_choice == "paper"):
            result = "You win! 🎉"
            self.points_service.add_points(ctx.author.id, RPS_WIN_POINTS)
        else:
            result = "I win! 😄"

        # Send result
        user_emoji = RPS_EMOJI_MAP[choice]
        bot_emoji = RPS_EMOJI_MAP[bot_choice]
        await ctx.send(f"{user_emoji} vs {bot_emoji}\n{result}")

    @commands.command(name="guess", help="Guess a number between 1-100!")
    async def guess(self, ctx: commands.Context):
        """Number guessing game"""
        number = random.randint(GUESS_MIN, GUESS_MAX)
        await ctx.send(
            f"🎯 I'm thinking of a number between {GUESS_MIN} and {GUESS_MAX}! "
            f"You have {GUESS_ATTEMPTS} tries. Type your guess:"
        )

        def check(m):
            return (m.author == ctx.author and
                    m.channel == ctx.channel and
                    m.content.isdigit())

        for attempt in range(GUESS_ATTEMPTS):
            remaining_tries = GUESS_ATTEMPTS - attempt - 1

            try:
                msg = await self.bot.wait_for('message', timeout=GUESS_TIMEOUT, check=check)
                guess_num = int(msg.content)

                if guess_num == number:
                    self.points_service.add_points(ctx.author.id, GUESS_WIN_POINTS)
                    await ctx.send(
                        f"🎉 Correct! The number was {number}! "
                        f"You earned {GUESS_WIN_POINTS} points!"
                    )
                    return
                elif guess_num < number:
                    if remaining_tries > 0:
                        await ctx.send(f"Higher! {remaining_tries} tries left.")
                else:
                    if remaining_tries > 0:
                        await ctx.send(f"Lower! {remaining_tries} tries left.")

            except asyncio.TimeoutError:
                await ctx.send("⏰ Time's up!")
                return

        await ctx.send(f"😅 Out of tries! The number was {number}. Better luck next time!")

    async def _generate_trivia_with_gemini(self, difficulty: str = "medium", genre: str = "general") -> dict:
        """
        Ask Gemini to create one multiple-choice trivia question and return a dict:
        { "question": str, "options": ["optA","optB","optC","optD"], "answer": "A",
          "explanation": str, "category": str, "difficulty": "easy|medium|hard", "hint": str }
        """
        if not self.gemini_model:
            raise RuntimeError("Gemini not configured")

        # Build difficulty guidelines
        difficulty_guide = {
            "easy": "The question should be simple and commonly known. Suitable for general knowledge.",
            "medium": "The question should require some specific knowledge but not be too obscure.",
            "hard": "The question should be challenging and require detailed or specialized knowledge.",
            "expert": "The question should be very difficult, suitable only for experts in the field."
        }

        diff_desc = difficulty_guide.get(difficulty.lower(), difficulty_guide["medium"])

        prompt = f"""
Create a single multiple-choice trivia question. Output ONLY valid JSON with these fields:
{{ "question": string, "options": [string,string,string,string], "answer": "A"|"B"|"C"|"D",
  "explanation": string, "category": string, "difficulty": "{difficulty}", "hint": string }}

Constraints:
- Exactly 4 options.
- Answer must be one of "A","B","C","D".
- Difficulty level: {difficulty} - {diff_desc}
- Genre/Category: {genre}
- Keep text concise and ensure the question is appropriate for the difficulty level.
- Make sure incorrect options are plausible but clearly wrong.
"""

        try:
            response = await asyncio.to_thread(self.gemini_model.generate_content, prompt)
            text = response.text if response else ""

            # Try to extract and parse JSON
            # First, try direct parsing
            try:
                return json.loads(text)
            except Exception:
                pass

            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except Exception:
                    pass

            # Try to find JSON object between first { and last }
            first_brace = text.find('{')
            last_brace = text.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                try:
                    json_text = text[first_brace:last_brace + 1]
                    return json.loads(json_text)
                except Exception:
                    pass

            # If all parsing attempts failed, raise to fallback
            raise ValueError("Failed to parse JSON from Gemini response")
        except Exception as e:
            # Bubble up to let caller fallback to static questions
            raise

    @commands.command(name="trivia", help="Answer trivia questions! Usage: !trivia [difficulty] [genre]")
    async def trivia(self, ctx: commands.Context, difficulty: str = "medium", *, genre: str = "general"):
        """
        Enhanced trivia with difficulty levels and genre selection
        Usage: !trivia [easy/medium/hard/expert] [genre]
        Examples: !trivia hard science, !trivia easy, !trivia medium history
        """
        # Normalize difficulty
        valid_difficulties = ["easy", "medium", "hard", "expert"]
        difficulty = difficulty.lower()
        if difficulty not in valid_difficulties:
            # Maybe they provided genre first, swap them
            if genre != "general" and genre.lower() in valid_difficulties:
                difficulty, genre = genre.lower(), difficulty
            else:
                # Use as genre and default difficulty
                genre = difficulty + " " + genre if genre != "general" else difficulty
                difficulty = "medium"

        # Check if user already has a session
        if ctx.author.id in self.active_trivia_sessions:
            session = self.active_trivia_sessions[ctx.author.id]
            await self._ask_trivia_question(ctx, session)
        else:
            # Create new single-question session
            session = TriviaSession(ctx.author.id, difficulty, genre, False, 1)
            self.active_trivia_sessions[ctx.author.id] = session
            await self._ask_trivia_question(ctx, session)

    @commands.command(name="triviacomp", aliases=["triviacompetition", "tc"],
                      help="Start a 10-question trivia competition! Usage: !triviacomp [difficulty] [genre]")
    async def trivia_competition(self, ctx: commands.Context, difficulty: str = "medium", *, genre: str = "general"):
        """
        10-question trivia competition with scoring
        Usage: !triviacomp [easy/medium/hard/expert] [genre]
        """
        # Normalize difficulty
        valid_difficulties = ["easy", "medium", "hard", "expert"]
        difficulty = difficulty.lower()
        if difficulty not in valid_difficulties:
            if genre != "general" and genre.lower() in valid_difficulties:
                difficulty, genre = genre.lower(), difficulty
            else:
                genre = difficulty + " " + genre if genre != "general" else difficulty
                difficulty = "medium"

        # Check if user already has an active session
        if ctx.author.id in self.active_trivia_sessions:
            await ctx.send("❌ You already have an active trivia session! Finish it first or use `!triviaend` to end it.")
            return

        # Create competition session
        session = TriviaSession(ctx.author.id, difficulty, genre, True, 10)
        self.active_trivia_sessions[ctx.author.id] = session

        embed = discord.Embed(
            title="🏆 Trivia Competition Started!",
            description=f"""
**10 Questions Challenge**
━━━━━━━━━━━━━━━━━━━━
🎯 Difficulty: {difficulty.title()}
📚 Genre: {genre.title()}
⭐ Points per question vary by difficulty
⏱️ 30 seconds per question

Good luck! Question 1 coming up...
""",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
        await asyncio.sleep(2)

        await self._ask_trivia_question(ctx, session)

    @commands.command(name="triviaend", aliases=["endtrivia"], help="End your current trivia session")
    async def trivia_end(self, ctx: commands.Context):
        """End an active trivia session"""
        if ctx.author.id not in self.active_trivia_sessions:
            await ctx.send("❌ You don't have an active trivia session.")
            return

        session = self.active_trivia_sessions[ctx.author.id]

        if session.is_competition:
            # Show partial results
            embed = discord.Embed(
                title="🛑 Competition Ended Early",
                description=session.get_summary(),
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

        del self.active_trivia_sessions[ctx.author.id]
        await ctx.send("✅ Your trivia session has been ended.")

    @commands.command(name="triviahelp", aliases=["th"], help="Show trivia system help and options")
    async def trivia_help(self, ctx: commands.Context):
        """Show comprehensive trivia help"""
        embed = discord.Embed(
            title="🎯 Trivia System Guide",
            description="Master the trivia commands and options!",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📝 Single Question Mode",
            value="""
`!trivia` - Random medium difficulty question
`!trivia easy` - Easy question
`!trivia hard science` - Hard science question
`!trivia expert history` - Expert history question
            """.strip(),
            inline=False
        )

        embed.add_field(
            name="🏆 Competition Mode (10 Questions)",
            value="""
`!triviacomp` - Medium difficulty, general
`!triviacomp hard` - Hard difficulty
`!triviacomp medium science` - Medium science
`!tc easy history` - Easy history (short alias)
            """.strip(),
            inline=False
        )

        embed.add_field(
            name="🎚️ Difficulty Levels",
            value="""
**Easy** (5 pts) - Common knowledge
**Medium** (10 pts) - General knowledge
**Hard** (15 pts) - Challenging questions
**Expert** (20 pts) - Very difficult
            """.strip(),
            inline=False
        )

        embed.add_field(
            name="📚 Popular Genres",
            value="""
• Science • History • Geography
• Technology • Mathematics • Art
• Literature • Sports • Music
• Movies • General • Pop Culture
• Nature • Space • Animals
            """.strip(),
            inline=False
        )

        embed.add_field(
            name="⚙️ Other Commands",
            value="""
`!triviaend` - End current session
`!triviastats [@user]` - View trivia stats
`!trivialeaderboard [type]` - View leaderboards
            """.strip(),
            inline=False
        )

        embed.set_footer(text="Pro tip: Answer faster for style points! Type A/B/C/D or the full answer.")
        await ctx.send(embed=embed)

    @commands.command(name="triviastats", aliases=["ts"], help="View trivia statistics. Usage: !triviastats [@user]")
    async def trivia_stats(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """View trivia statistics for a user"""
        target_user = user or ctx.author

        stats = self.game_stats_service.get_trivia_stats(target_user.id)

        if not stats or stats['total_questions'] == 0:
            await ctx.send(f"❌ {target_user.display_name} hasn't played any trivia yet!")
            return

        embed = discord.Embed(
            title=f"📊 {target_user.display_name}'s Trivia Statistics",
            color=discord.Color.blue()
        )

        # Overall stats
        embed.add_field(
            name="📈 Overall Performance",
            value=f"""
**Questions:** {stats['total_questions']}
**Correct:** {stats['correct_answers']} ✅
**Wrong:** {stats['wrong_answers']} ❌
**Accuracy:** {stats['accuracy']:.1f}%
**Total Points:** {stats['total_points']} ⭐
            """.strip(),
            inline=False
        )

        # Streaks
        embed.add_field(
            name="🔥 Streaks",
            value=f"""
**Current:** {stats['current_streak']}
**Best Ever:** {stats['best_streak']}
            """.strip(),
            inline=True
        )

        # By difficulty
        difficulty_text = []
        if stats.get('easy_accuracy', 0) > 0:
            difficulty_text.append(f"Easy: {stats['easy_accuracy']:.1f}%")
        if stats.get('medium_accuracy', 0) > 0:
            difficulty_text.append(f"Medium: {stats['medium_accuracy']:.1f}%")
        if stats.get('hard_accuracy', 0) > 0:
            difficulty_text.append(f"Hard: {stats['hard_accuracy']:.1f}%")
        if stats.get('expert_accuracy', 0) > 0:
            difficulty_text.append(f"Expert: {stats['expert_accuracy']:.1f}%")

        if difficulty_text:
            embed.add_field(
                name="🎚️ By Difficulty",
                value="\n".join(difficulty_text),
                inline=True
            )

        # Competitions
        if stats['competitions_completed'] > 0:
            embed.add_field(
                name="🏆 Competitions",
                value=f"""
**Completed:** {stats['competitions_completed']}
**Perfect Scores:** {stats['competitions_perfect']}
**Best Score:** {stats['best_competition_score']} pts
                """.strip(),
                inline=False
            )

        # Last played
        if stats['last_played']:
            from datetime import datetime
            last_played = stats['last_played']
            if isinstance(last_played, str):
                last_played = datetime.fromisoformat(last_played)
            embed.set_footer(text=f"Last played: {last_played.strftime('%Y-%m-%d %H:%M UTC')}")

        await ctx.send(embed=embed)

    @commands.command(name="trivialeaderboard", aliases=["tlb", "trivialtop"],
                      help="View trivia leaderboards. Usage: !trivialeaderboard [accuracy/points/streak/competitions]")
    async def trivia_leaderboard(self, ctx: commands.Context, stat_type: str = "accuracy"):
        """View trivia leaderboards"""
        stat_type = stat_type.lower()

        valid_types = ["accuracy", "points", "streak", "competitions"]
        if stat_type not in valid_types:
            stat_type = "accuracy"

        leaderboard = self.game_stats_service.get_trivia_leaderboard(stat_type, limit=10)

        if not leaderboard:
            await ctx.send("❌ No trivia statistics available yet!")
            return

        # Map stat types to display names
        type_names = {
            "accuracy": ("Accuracy", "%"),
            "points": ("Total Points", " pts"),
            "streak": ("Best Streak", " correct"),
            "competitions": ("Competitions", " completed")
        }

        title_name, suffix = type_names[stat_type]

        embed = discord.Embed(
            title=f"🏆 Trivia Leaderboard - {title_name}",
            color=discord.Color.gold()
        )

        description_lines = []
        for idx, (user_id, value) in enumerate(leaderboard, 1):
            try:
                user = await self.bot.fetch_user(user_id)
                username = user.display_name
            except:
                username = f"User {user_id}"

            medal = ""
            if idx == 1:
                medal = "🥇 "
            elif idx == 2:
                medal = "🥈 "
            elif idx == 3:
                medal = "🥉 "
            else:
                medal = f"{idx}. "

            if stat_type == "accuracy":
                description_lines.append(f"{medal}**{username}**: {value:.1f}{suffix}")
            else:
                description_lines.append(f"{medal}**{username}**: {int(value)}{suffix}")

        embed.description = "\n".join(description_lines)
        embed.set_footer(text=f"Type: !trivialeaderboard [accuracy/points/streak/competitions]")

        await ctx.send(embed=embed)

    async def _ask_trivia_question(self, ctx: commands.Context, session: TriviaSession):
        """Ask a single trivia question within a session"""
        # Points by difficulty
        points_map = {"easy": 5, "medium": 10, "hard": 15, "expert": 20}

        # Try Gemini first if configured
        trivia_data = None
        if self.gemini_model:
            try:
                trivia_data = await self._generate_trivia_with_gemini(session.difficulty, session.genre)
            except Exception as e:
                print(f"Gemini trivia generation failed: {e}")
                trivia_data = None

        # Fallback to static questions if Gemini fails
        if not trivia_data:
            trivia_data = self._get_fallback_trivia(session.difficulty, session.genre)

        if not trivia_data:
            await ctx.send("❌ Failed to generate question. Please try again.")
            if ctx.author.id in self.active_trivia_sessions:
                del self.active_trivia_sessions[ctx.author.id]
            return

        # Extract question data
        question = trivia_data.get("question", "No question generated.")
        options = trivia_data.get("options", [])[:4]
        answer_letter = str(trivia_data.get("answer", "A")).strip().upper()
        explanation = trivia_data.get("explanation", "")
        category = trivia_data.get("category", session.genre)
        difficulty = trivia_data.get("difficulty", session.difficulty).lower()
        hint = trivia_data.get("hint", "")

        # Ensure we have 4 options
        if len(options) < 4:
            await ctx.send("❌ Generated question was invalid. Try again.")
            if ctx.author.id in self.active_trivia_sessions:
                del self.active_trivia_sessions[ctx.author.id]
            return

        # Build description with lettered options
        letters = ["A", "B", "C", "D"]
        desc_lines = [question, ""]
        for i, opt in enumerate(options):
            desc_lines.append(f"{letters[i]}) {opt}")
        desc_lines.append("")
        if hint:
            desc_lines.append(f"💡 Hint: {hint}")

        # Create embed
        if session.is_competition:
            title = f"🏆 Question {session.current_question + 1}/10 - {category} ({difficulty.title()})"
            footer_text = f"Score: {session.correct_answers}/{session.current_question} | Type A/B/C/D | 30 seconds"
        else:
            title = f"🎯 Trivia - {category} ({difficulty.title()})"
            footer_text = "Type A/B/C/D or the full answer. You have 30 seconds."

        embed = discord.Embed(
            title=title,
            description="\n".join(desc_lines),
            color=discord.Color.blue() if not session.is_competition else discord.Color.gold()
        )
        embed.set_footer(text=footer_text)
        await ctx.send(embed=embed)

        # Wait for answer
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.strip() != ""

        try:
            user_msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            user_ans = user_msg.content.strip()

            # Normalize answer
            user_letter = user_ans.upper()
            if user_letter in letters:
                selected_idx = letters.index(user_letter)
            else:
                # Try matching to option text
                selected_idx = None
                normalized_user = re.sub(r'\s+', ' ', user_ans.strip().lower())
                for i, opt in enumerate(options):
                    if normalized_user == opt.strip().lower():
                        selected_idx = i
                        break
                    # partial match
                    if normalized_user in opt.strip().lower() or opt.strip().lower() in normalized_user:
                        selected_idx = i
                        break

            correct_idx = letters.index(answer_letter) if answer_letter in letters else 0
            is_correct = selected_idx is not None and selected_idx == correct_idx

            # Calculate points
            pts = points_map.get(difficulty, 10)

            # Record answer in session
            session.record_answer(is_correct, pts if is_correct else 0)

            # Log to database
            self.game_stats_service.log_trivia_answer(
                user_id=ctx.author.id,
                correct=is_correct,
                difficulty=difficulty,
                points=pts if is_correct else 0
            )

            if is_correct:
                self.points_service.add_points(ctx.author.id, pts)
                await ctx.send(f"✅ Correct! You earned {pts} points! ✨\n**Explanation:** {explanation}")
            else:
                correct_option = options[correct_idx]
                await ctx.send(f"❌ Wrong. The correct answer was **{letters[correct_idx]}) {correct_option}**.\n**Explanation:** {explanation}")

        except asyncio.TimeoutError:
            correct_idx = letters.index(answer_letter) if answer_letter in letters else 0
            correct_option = options[correct_idx]
            session.record_answer(False, 0)

            # Log timeout as wrong answer
            self.game_stats_service.log_trivia_answer(
                user_id=ctx.author.id,
                correct=False,
                difficulty=difficulty,
                points=0
            )

            await ctx.send(f"⏰ Time's up! The correct answer was **{letters[correct_idx]}) {correct_option}**.\n**Explanation:** {explanation}")

        # Check if session is complete
        if session.is_complete():
            await asyncio.sleep(1)

            # Log competition completion if applicable
            if session.is_competition:
                self.game_stats_service.log_trivia_competition(
                    user_id=ctx.author.id,
                    correct=session.correct_answers,
                    total=session.total_questions,
                    points=session.total_points,
                    difficulty=session.difficulty
                )

            # Show summary
            embed = discord.Embed(
                title="🏆 Competition Complete!" if session.is_competition else "✅ Trivia Complete!",
                description=session.get_summary(),
                color=discord.Color.gold()
            )

            # Add performance badges
            accuracy = (session.correct_answers / session.total_questions * 100)
            if accuracy == 100:
                embed.add_field(name="🏅 Achievement", value="Perfect Score!", inline=False)
            elif accuracy >= 80:
                embed.add_field(name="🏅 Achievement", value="Excellent Performance!", inline=False)
            elif accuracy >= 60:
                embed.add_field(name="🏅 Achievement", value="Good Job!", inline=False)

            await ctx.send(embed=embed)

            # Clean up session
            del self.active_trivia_sessions[ctx.author.id]
        elif session.is_competition:
            # Ask next question in competition
            await asyncio.sleep(2)
            await ctx.send(f"**Next question coming up...** ({session.current_question + 1}/10)")
            await asyncio.sleep(1)
            await self._ask_trivia_question(ctx, session)
        else:
            # Clean up single question session
            del self.active_trivia_sessions[ctx.author.id]

    def _get_fallback_trivia(self, difficulty: str, genre: str) -> Optional[dict]:
        """Get a fallback trivia question when Gemini is unavailable"""
        # Static questions organized by difficulty and genre
        fallback_questions = {
            "easy": {
                "science": [
                    {"q": "What planet is known as the Red Planet?", "opts": ["Mars", "Venus", "Jupiter", "Saturn"], "ans": "A", "exp": "Mars is called the Red Planet because of its reddish appearance caused by iron oxide on its surface."},
                    {"q": "What is H2O?", "opts": ["Water", "Oxygen", "Hydrogen", "Carbon dioxide"], "ans": "A", "exp": "H2O is the chemical formula for water, consisting of two hydrogen atoms and one oxygen atom."},
                ],
                "history": [
                    {"q": "Who was the first President of the United States?", "opts": ["George Washington", "Thomas Jefferson", "John Adams", "Benjamin Franklin"], "ans": "A", "exp": "George Washington served as the first President from 1789 to 1797."},
                ],
                "general": [
                    {"q": "How many continents are there?", "opts": ["7", "5", "6", "8"], "ans": "A", "exp": "There are seven continents: Africa, Antarctica, Asia, Europe, North America, Oceania, and South America."},
                    {"q": "What is the capital of France?", "opts": ["Paris", "London", "Berlin", "Madrid"], "ans": "A", "exp": "Paris has been the capital of France for centuries and is known for landmarks like the Eiffel Tower."},
                ],
            },
            "medium": {
                "science": [
                    {"q": "What is the speed of light?", "opts": ["299,792,458 m/s", "300,000 m/s", "150,000,000 m/s", "299,792 m/s"], "ans": "A", "exp": "The speed of light in vacuum is exactly 299,792,458 meters per second."},
                ],
                "history": [
                    {"q": "In what year did World War II end?", "opts": ["1945", "1944", "1946", "1943"], "ans": "A", "exp": "World War II ended in 1945 with Germany's surrender in May and Japan's in September."},
                ],
                "general": [
                    {"q": "What is the largest ocean?", "opts": ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean"], "ans": "A", "exp": "The Pacific Ocean is the largest, covering more than 60 million square miles."},
                ],
            },
        }

        # Try to find matching questions
        diff_questions = fallback_questions.get(difficulty, fallback_questions.get("easy", {}))

        # Check for genre match
        genre_lower = genre.lower()
        questions_list = None

        for key in diff_questions:
            if key in genre_lower or genre_lower in key:
                questions_list = diff_questions[key]
                break

        if not questions_list:
            questions_list = diff_questions.get("general", [])

        if not questions_list:
            # Get any questions from any category
            for cat_questions in diff_questions.values():
                if cat_questions:
                    questions_list = cat_questions
                    break

        if not questions_list:
            return None

        q_data = random.choice(questions_list)
        return {
            "question": q_data["q"],
            "options": q_data["opts"],
            "answer": q_data["ans"],
            "explanation": q_data["exp"],
            "category": genre.title(),
            "difficulty": difficulty,
            "hint": ""
        }

    @commands.command(name="scramble", help="Unscramble the word! Win 8 points!")
    async def scramble(self, ctx: commands.Context):
        """Word scrambling game"""
        words = [
            "python", "discord", "computer", "keyboard", "programming",
            "algorithm", "database", "internet", "developer", "software",
            "javascript", "function", "variable", "rainbow", "butterfly",
            "elephant", "mountain", "chocolate", "adventure", "treasure"
        ]

        word = random.choice(words)
        scrambled = ''.join(random.sample(word, len(word)))

        # Make sure it's actually scrambled
        while scrambled == word and len(word) > 3:
            scrambled = ''.join(random.sample(word, len(word)))

        embed = discord.Embed(
            title="📝 Word Scramble",
            description=f"Unscramble this word: **{scrambled.upper()}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Hint", value=f"The word has {len(word)} letters", inline=False)
        embed.set_footer(text="You have 30 seconds! Type your answer below.")
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)

            if msg.content.lower() == word:
                self.points_service.add_points(ctx.author.id, 8)
                await ctx.send(f"🎉 Correct! The word was **{word}**! You earned 8 points! ✨")
            else:
                await ctx.send(f"❌ Not quite! The word was: **{word}**")

        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time's up! The word was: **{word}**")

    @commands.command(name="math", help="Solve a math problem! Win 5 points!")
    async def math_challenge(self, ctx: commands.Context):
        """Quick math challenge"""
        operations = [
            ("addition", "+", lambda a, b: a + b),
            ("subtraction", "-", lambda a, b: a - b),
            ("multiplication", "×", lambda a, b: a * b),
        ]

        op_name, op_symbol, op_func = random.choice(operations)

        if op_name == "multiplication":
            num1 = random.randint(2, 12)
            num2 = random.randint(2, 12)
        elif op_name == "subtraction":
            num1 = random.randint(10, 50)
            num2 = random.randint(1, num1)  # Ensure positive result
        else:
            num1 = random.randint(1, 50)
            num2 = random.randint(1, 50)

        answer = op_func(num1, num2)

        embed = discord.Embed(
            title="🧮 Quick Math!",
            description=f"What is **{num1} {op_symbol} {num2}**?",
            color=discord.Color.purple()
        )
        embed.set_footer(text="You have 15 seconds! Type your answer below.")
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lstrip('-').isdigit()

        try:
            msg = await self.bot.wait_for('message', timeout=15.0, check=check)

            if int(msg.content) == answer:
                self.points_service.add_points(ctx.author.id, 5)
                await ctx.send(f"🎉 Correct! {num1} {op_symbol} {num2} = {answer}! You earned 5 points! ✨")
            else:
                await ctx.send(f"❌ Not quite! The answer was: **{answer}**")

        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time's up! The answer was: **{answer}**")

    @commands.command(name="reaction", help="Test your reaction speed! Win 15 points!")
    async def reaction_test(self, ctx: commands.Context):
        """Reaction time test game"""
        await ctx.send("⏳ Get ready... I'll say GO in a moment!")

        # Random delay between 2-5 seconds
        await asyncio.sleep(random.uniform(2.0, 5.0))

        start_time = asyncio.get_event_loop().time()
        await ctx.send("🚀 **GO! Type anything NOW!**")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', timeout=5.0, check=check)
            end_time = asyncio.get_event_loop().time()
            reaction_time = round((end_time - start_time) * 1000)  # Convert to ms

            if reaction_time < 1000:
                self.points_service.add_points(ctx.author.id, 15)
                await ctx.send(f"⚡ Lightning fast! Your reaction time: **{reaction_time}ms**! You earned 15 points! 🎉")
            elif reaction_time < 2000:
                self.points_service.add_points(ctx.author.id, 10)
                await ctx.send(f"🏃 Pretty quick! Your reaction time: **{reaction_time}ms**! You earned 10 points!")
            else:
                self.points_service.add_points(ctx.author.id, 5)
                await ctx.send(f"🐌 Not bad! Your reaction time: **{reaction_time}ms**! You earned 5 points!")

        except asyncio.TimeoutError:
            await ctx.send("😴 Too slow! You took more than 5 seconds!")

    @commands.command(name="twenty-one", aliases=["21", "blackjack"], help="Play 21/Blackjack! Win 20 points!")
    async def twenty_one(self, ctx: commands.Context):
        """Simple 21/Blackjack game"""
        def get_card():
            return random.randint(1, 11)

        def calculate_hand(cards: List[int]) -> int:
            total = sum(cards)
            # Convert Aces (11) to 1 if needed to avoid bust
            aces = cards.count(11)
            while total > 21 and aces > 0:
                total -= 10
                aces -= 1
            return total

        player_cards = [get_card(), get_card()]
        dealer_cards = [get_card(), get_card()]

        player_total = calculate_hand(player_cards)
        dealer_total = calculate_hand(dealer_cards)

        # Check for instant blackjack
        if player_total == 21:
            self.points_service.add_points(ctx.author.id, 30)
            await ctx.send(f"🎉 **BLACKJACK!** You win big! 30 points! 🃏✨")
            return

        embed = discord.Embed(
            title="🃏 Twenty-One (21)",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="Your Hand",
            value=f"Cards: {' + '.join(map(str, player_cards))} = **{player_total}**",
            inline=False
        )
        embed.add_field(
            name="Dealer's Hand",
            value=f"Showing: **{dealer_cards[0]}** + ?",
            inline=False
        )
        embed.set_footer(text="Type 'hit' to draw another card or 'stand' to hold!")
        await ctx.send(embed=embed)

        def check(m):
            return (m.author == ctx.author and
                   m.channel == ctx.channel and
                   m.content.lower() in ['hit', 'stand'])

        # Player's turn
        while player_total < 21:
            try:
                msg = await self.bot.wait_for('message', timeout=30.0, check=check)

                if msg.content.lower() == 'stand':
                    break

                # Hit
                new_card = get_card()
                player_cards.append(new_card)
                player_total = calculate_hand(player_cards)

                if player_total > 21:
                    await ctx.send(f"🎴 Drew **{new_card}**! Total: **{player_total}** - BUST! 💥 You lose!")
                    return
                elif player_total == 21:
                    await ctx.send(f"🎴 Drew **{new_card}**! Total: **{player_total}** - Perfect 21!")
                    break
                else:
                    await ctx.send(f"🎴 Drew **{new_card}**! Your total: **{player_total}**. Hit or stand?")

            except asyncio.TimeoutError:
                await ctx.send("⏰ Time's up! You stood by default.")
                break

        # Dealer's turn
        await ctx.send(f"🎰 Dealer reveals: {' + '.join(map(str, dealer_cards))} = **{dealer_total}**")

        while dealer_total < 17:
            await asyncio.sleep(1.5)
            new_card = get_card()
            dealer_cards.append(new_card)
            dealer_total = calculate_hand(dealer_cards)
            await ctx.send(f"🎴 Dealer draws **{new_card}**! Dealer total: **{dealer_total}**")

        # Determine winner
        await asyncio.sleep(1)
        if dealer_total > 21:
            self.points_service.add_points(ctx.author.id, 20)
            await ctx.send(f"💥 Dealer busts! **You win!** 🎉 You earned 20 points!")
        elif player_total > dealer_total:
            self.points_service.add_points(ctx.author.id, 20)
            await ctx.send(f"🎊 You win! **{player_total}** vs **{dealer_total}**! You earned 20 points!")
        elif player_total == dealer_total:
            await ctx.send(f"🤝 Push! It's a tie at **{player_total}**. No points lost or gained.")
        else:
            await ctx.send(f"😞 Dealer wins! **{dealer_total}** vs **{player_total}**. Better luck next time!")

    @commands.command(name="flip", help="Flip a coin! Guess correctly for 3 points!")
    async def coin_flip(self, ctx: commands.Context, guess: str = None):
        """Coin flip game"""
        if not guess or guess.lower() not in ['heads', 'tails', 'h', 't']:
            await ctx.send("🪙 Usage: `!flip heads` or `!flip tails` (or use h/t)")
            return

        guess = guess.lower()
        if guess == 'h':
            guess = 'heads'
        elif guess == 't':
            guess = 'tails'

        result = random.choice(['heads', 'tails'])

        # Animated flip
        flip_msg = await ctx.send("🪙 Flipping the coin...")
        await asyncio.sleep(1)
        await flip_msg.edit(content="🪙 Flipping... 🌪️")
        await asyncio.sleep(1)

        if result == guess:
            self.points_service.add_points(ctx.author.id, 3)
            await flip_msg.edit(content=f"🪙 It's **{result.upper()}**! You guessed right! +3 points! 🎉")
        else:
            await flip_msg.edit(content=f"🪙 It's **{result.upper()}**! You guessed {guess}. Better luck next time! 😄")

    @commands.command(name="slots", help="Play the slot machine! Win up to 50 points!")
    async def slots(self, ctx: commands.Context):
        """Slot machine game"""
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣", "⭐"]
        weights = [25, 25, 20, 15, 10, 3, 2]  # Rarity weights

        # Spin the slots
        slot1 = random.choices(symbols, weights=weights)[0]
        slot2 = random.choices(symbols, weights=weights)[0]
        slot3 = random.choices(symbols, weights=weights)[0]

        # Animation
        spin_msg = await ctx.send("🎰 Spinning... ⚡")
        await asyncio.sleep(0.8)
        await spin_msg.edit(content=f"🎰 | {slot1} | ??? | ??? |")
        await asyncio.sleep(0.8)
        await spin_msg.edit(content=f"🎰 | {slot1} | {slot2} | ??? |")
        await asyncio.sleep(0.8)
        await spin_msg.edit(content=f"🎰 | {slot1} | {slot2} | {slot3} |")
        await asyncio.sleep(0.5)

        # Check for wins
        if slot1 == slot2 == slot3:
            if slot1 == "7️⃣":
                points = 100
                message = "🎰 **JACKPOT!!! TRIPLE SEVENS!!!** 🎰"
            elif slot1 == "💎":
                points = 50
                message = "💎 **AMAZING! TRIPLE DIAMONDS!** 💎"
            elif slot1 == "⭐":
                points = 40
                message = "⭐ **FANTASTIC! TRIPLE STARS!** ⭐"
            else:
                points = 25
                message = f"🎉 **Triple {slot1}! Nice win!** 🎉"

            self.points_service.add_points(ctx.author.id, points)
            await ctx.send(f"{message}\nYou won **{points} points**! 🎊")

        elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
            points = 5
            self.points_service.add_points(ctx.author.id, points)
            await ctx.send(f"🎰 Two matching symbols! You won **{points} points**! 🎉")

        else:
            await ctx.send("🎰 No match this time! Try again! 🎲")


async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    # Get services from bot
    points_service = bot.points_service
    game_stats_service = bot.game_stats_service
    await bot.add_cog(GameCommands(bot, points_service, game_stats_service))
