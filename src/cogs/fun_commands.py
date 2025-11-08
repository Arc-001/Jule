"""
Fun commands cog for Jule bot
Handles entertainment and casual interaction commands
"""

import random
import discord
from discord.ext import commands
from typing import Optional

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    GREETINGS, ENCOURAGEMENTS, RANDOM_FACTS, COMPLIMENTS,
    EIGHT_BALL_RESPONSES
)


class FunCommands(commands.Cog):
    """Fun and entertainment commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="hello", help="Say hello to Jule!")
    async def hello(self, ctx: commands.Context):
        """Greet the user"""
        emoji = random.choice(['😊', '👋', '✨', '🌟'])
        await ctx.send(f"Hello {ctx.author.mention}! {emoji}")

    @commands.command(name="roll", help="Roll a dice! Usage: !roll [sides] (default: 6)")
    async def roll(self, ctx: commands.Context, sides: int = 6):
        """Roll a dice with specified number of sides"""
        if sides < 2:
            await ctx.send("Come on, I need at least 2 sides! 🎲")
            return

        result = random.randint(1, sides)
        await ctx.send(f"🎲 You rolled a {result}!")

    @commands.command(name="flip", help="Flip a coin!")
    async def flip(self, ctx: commands.Context):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        await ctx.send(f"🪙 The coin landed on: **{result}**!")

    @commands.command(name="8ball", help="Ask the magic 8-ball a question!")
    async def eightball(self, ctx: commands.Context, *, question: Optional[str] = None):
        """Ask the magic 8-ball"""
        if not question:
            await ctx.send("You need to ask a question! 🔮")
            return

        response = random.choice(EIGHT_BALL_RESPONSES)
        await ctx.send(f"🔮 {response}")

    @commands.command(name="fact", help="Get a random fun fact!")
    async def fact(self, ctx: commands.Context):
        """Get a random fact"""
        await ctx.send(f"💡 **Fun Fact:** {random.choice(RANDOM_FACTS)}")

    @commands.command(name="compliment", help="Get a compliment or give one to someone!")
    async def compliment(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Give a compliment to yourself or someone else"""
        target = member if member else ctx.author
        compliment = random.choice(COMPLIMENTS)
        await ctx.send(f"{target.mention} {compliment}")

    @commands.command(name="choose", help="Let Jule choose for you! Usage: !choose option1 option2 option3...")
    async def choose(self, ctx: commands.Context, *choices: str):
        """Let the bot choose from multiple options"""
        if len(choices) < 2:
            await ctx.send("Give me at least 2 options to choose from! 🤔")
            return

        await ctx.send(f"I choose: **{random.choice(choices)}**! ✨")

    @commands.command(name="encourage", help="Send encouragement to someone!")
    async def encourage(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Send an encouraging message"""
        target = member if member else ctx.author
        encouragement = random.choice(ENCOURAGEMENTS)
        await ctx.send(f"{target.mention} {encouragement}")


async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    await bot.add_cog(FunCommands(bot))

