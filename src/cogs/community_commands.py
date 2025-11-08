"""
Community commands cog for Jule bot
Handles points, birthdays, and community engagement
"""

import discord
from discord.ext import commands
from typing import Optional

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.services import PointsService, BirthdayService
from utils import format_birthday, validate_birthday


class CommunityCommands(commands.Cog):
    """Community engagement and management commands"""

    def __init__(self, bot: commands.Bot, points_service: PointsService, birthday_service: BirthdayService):
        self.bot = bot
        self.points_service = points_service
        self.birthday_service = birthday_service

    @commands.command(name="points", help="Check your community points!")
    async def points(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Check community points for yourself or another user"""
        target = member if member else ctx.author
        pts = self.points_service.get_points(target.id)
        await ctx.send(f"🌟 {target.display_name} has **{pts}** community points!")

    @commands.command(name="leaderboard", help="See the top community members!")
    async def leaderboard(self, ctx: commands.Context):
        """Display the community points leaderboard"""
        top_users = self.points_service.get_leaderboard(limit=10)

        if not top_users:
            await ctx.send("No points earned yet! Start chatting to earn points! 💬")
            return

        embed = discord.Embed(
            title="🏆 Community Leaderboard",
            description="Top contributors in our cozy nook!",
            color=discord.Color.gold()
        )

        medals = ["🥇", "🥈", "🥉"]
        for idx, (user_id, pts) in enumerate(top_users):
            member = ctx.guild.get_member(user_id)
            if member:
                medal = medals[idx] if idx < 3 else f"{idx + 1}."
                embed.add_field(
                    name=f"{medal} {member.display_name}",
                    value=f"{pts} points",
                    inline=False
                )

        await ctx.send(embed=embed)

    @commands.command(name="birthday", help="Set your birthday! Usage: !birthday <month> <day>")
    async def birthday(self, ctx: commands.Context, month: int, day: int):
        """Set your birthday"""
        is_valid, error_message = validate_birthday(month, day)

        if not is_valid:
            await ctx.send(error_message)
            return

        self.birthday_service.add_birthday(ctx.author.id, month, day)
        birthday_str = format_birthday(month, day)
        await ctx.send(f"🎂 Birthday set to {birthday_str}! I'll wish you on your special day!")

    @commands.command(name="birthdays", help="See upcoming birthdays!")
    async def birthdays(self, ctx: commands.Context):
        """Show today's birthdays"""
        birthday_users = self.birthday_service.get_todays_birthdays()

        if not birthday_users:
            await ctx.send("🎂 No birthdays today! Use `!birthday` to add yours.")
            return

        embed = discord.Embed(
            title="🎉 Today's Birthdays!",
            color=discord.Color.gold()
        )

        for user_id in birthday_users:
            member = ctx.guild.get_member(user_id)
            if member:
                embed.add_field(
                    name=member.display_name,
                    value="🎂 Happy Birthday!",
                    inline=False
                )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    points_service = bot.points_service
    birthday_service = bot.birthday_service
    await bot.add_cog(CommunityCommands(bot, points_service, birthday_service))

