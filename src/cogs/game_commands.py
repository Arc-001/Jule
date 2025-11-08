"""
Game commands cog for Jule bot
Handles interactive games
"""

import random
import asyncio
from discord.ext import commands

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    RPS_CHOICES, RPS_EMOJI_MAP, RPS_WIN_POINTS,
    GUESS_MIN, GUESS_MAX, GUESS_ATTEMPTS, GUESS_TIMEOUT, GUESS_WIN_POINTS
)
from model.services import PointsService


class GameCommands(commands.Cog):
    """Interactive game commands"""

    def __init__(self, bot: commands.Bot, points_service: PointsService):
        self.bot = bot
        self.points_service = points_service

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


async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    # Get points_service from bot
    points_service = bot.points_service
    await bot.add_cog(GameCommands(bot, points_service))

