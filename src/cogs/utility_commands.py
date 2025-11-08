"""
Utility commands cog for Jule bot
Handles polls, reminders, and information commands
"""

import discord
from discord.ext import commands
from typing import Optional

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    MIN_POLL_OPTIONS, MAX_POLL_OPTIONS, POLL_REACTIONS,
    MIN_REMINDER_MINUTES, MAX_REMINDER_MINUTES
)
from model.services import ReminderService, BirthdayService, PointsService
from utils import get_avatar_url, format_birthday


class UtilityCommands(commands.Cog):
    """Utility and information commands"""

    def __init__(self, bot: commands.Bot, reminder_service: ReminderService,
                 birthday_service: BirthdayService, points_service: PointsService):
        self.bot = bot
        self.reminder_service = reminder_service
        self.birthday_service = birthday_service
        self.points_service = points_service

    @commands.command(name="poll", help="Create a poll! Usage: !poll 'Question' option1 option2 option3...")
    async def poll(self, ctx: commands.Context, question: str, *options: str):
        """Create a poll with reactions"""
        if len(options) < MIN_POLL_OPTIONS:
            await ctx.send(f"I need at least {MIN_POLL_OPTIONS} options for a poll! 📊")
            return

        if len(options) > MAX_POLL_OPTIONS:
            await ctx.send(f"Maximum {MAX_POLL_OPTIONS} options please! 📊")
            return

        # Create poll embed
        embed = discord.Embed(
            title=f"📊 {question}",
            description="\n".join([
                f"{POLL_REACTIONS[i]} {option}"
                for i, option in enumerate(options)
            ]),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Poll by {ctx.author.display_name}")

        poll_msg = await ctx.send(embed=embed)

        # Add reactions
        for i in range(len(options)):
            await poll_msg.add_reaction(POLL_REACTIONS[i])

    @commands.command(name="remind", help="Set a reminder! Usage: !remind <minutes> <message>")
    async def remind(self, ctx: commands.Context, minutes: int, *, message: str):
        """Set a reminder"""
        if minutes < MIN_REMINDER_MINUTES:
            await ctx.send(f"Please set at least {MIN_REMINDER_MINUTES} minute! ⏰")
            return

        if minutes > MAX_REMINDER_MINUTES:
            await ctx.send(f"Maximum reminder time is {MAX_REMINDER_MINUTES} minutes (24 hours)! ⏰")
            return

        self.reminder_service.add_reminder(ctx.author.id, ctx.channel.id, message, minutes)
        await ctx.send(f"⏰ Got it! I'll remind you in {minutes} minute(s): '{message}'")

    @commands.command(name="serverinfo", help="Get information about the server!")
    async def serverinfo(self, ctx: commands.Context):
        """Display server information"""
        guild = ctx.guild

        embed = discord.Embed(
            title=f"📊 {guild.name} - Server Info",
            color=discord.Color.purple()
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
        embed.add_field(name="📅 Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="💬 Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="avatar", help="Get someone's avatar! Usage: !avatar [@user]")
    async def avatar(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display a user's avatar"""
        target = member if member else ctx.author
        avatar_url = get_avatar_url(target)

        embed = discord.Embed(
            title=f"🖼️ {target.display_name}'s Avatar",
            color=discord.Color.blue()
        )
        embed.set_image(url=avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name="userinfo", help="Get info about a user! Usage: !userinfo [@user]")
    async def userinfo(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        """Display detailed user information"""
        target = member if member else ctx.author

        embed = discord.Embed(
            title=f"👤 {target.display_name}",
            color=target.color
        )

        embed.set_thumbnail(url=get_avatar_url(target))
        embed.add_field(name="🏷️ Username", value=str(target), inline=True)
        embed.add_field(name="🆔 ID", value=target.id, inline=True)
        embed.add_field(
            name="📅 Joined Server",
            value=target.joined_at.strftime("%B %d, %Y"),
            inline=False
        )
        embed.add_field(
            name="📅 Account Created",
            value=target.created_at.strftime("%B %d, %Y"),
            inline=False
        )
        embed.add_field(
            name="🌟 Community Points",
            value=self.points_service.get_points(target.id),
            inline=True
        )

        # Add birthday if set
        birthday = self.birthday_service.get_birthday(target.id)
        if birthday:
            birthday_str = format_birthday(birthday[0], birthday[1])
            embed.add_field(name="🎂 Birthday", value=birthday_str, inline=True)

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    reminder_service = bot.reminder_service
    birthday_service = bot.birthday_service
    points_service = bot.points_service
    await bot.add_cog(UtilityCommands(bot, reminder_service, birthday_service, points_service))

