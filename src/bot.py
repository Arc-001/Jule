"""Jule Discord bot — main entry point and core event handlers."""

from __future__ import annotations

import asyncio
import random
from typing import List

import discord
from discord.ext import commands, tasks

from constants import (
    DATABASE_PATH,
    DISCORD_TOKEN,
    GREETINGS,
    MIN_INTRO_LENGTH,
    RANDOM_REACTION_CHANCE,
    RANDOM_REACTIONS,
    ROLES_CONFIG_PATH,
    SPAM_THRESHOLD,
    SPAM_TIMEFRAME,
)
from logger import get_logger
from model.model import Birthday, Database
from model.role_assigner import RoleAssigner
from model.services import (
    BirthdayService,
    GameStatsService,
    MusicService,
    PointsService,
    ReminderService,
    SpamDetector,
)
from utils import get_avatar_url

log = get_logger(__name__)


# ============================================================================
# Bot setup
# ============================================================================

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

db = Database(DATABASE_PATH)
spam_detector = SpamDetector(db, threshold=SPAM_THRESHOLD, timeframe=SPAM_TIMEFRAME)
reminder_service = ReminderService(db)
points_service = PointsService(db)
birthday_service = BirthdayService(db)
music_service = MusicService(db)
game_stats_service = GameStatsService(db)
role_assigner = RoleAssigner(ROLES_CONFIG_PATH)

bot.db = db
bot.spam_detector = spam_detector
bot.reminder_service = reminder_service
bot.points_service = points_service
bot.birthday_service = birthday_service
bot.music_service = music_service
bot.game_stats_service = game_stats_service
bot.role_assigner = role_assigner


EXTENSIONS: List[str] = [
    "cogs.help_commands",
    "cogs.fun_commands",
    "cogs.game_commands",
    "cogs.community_commands",
    "cogs.utility_commands",
    "cogs.admin_commands",
    "cogs.music_commands",
    "cogs.ai_commands",
    "cogs.template_manager",
]


# ============================================================================
# Event handlers
# ============================================================================

async def handle_intro_message(message: discord.Message) -> None:
    """Analyze an intro channel message and auto-assign roles."""
    try:
        if len(message.content) < MIN_INTRO_LENGTH:
            return

        async with message.channel.typing():
            role_names, role_ids = await role_assigner.assign_roles_from_intro(message.content)

            if not role_names:
                await message.add_reaction("👋")
                return

            assigned: List[str] = []
            for role_id in role_ids:
                role = message.guild.get_role(role_id)
                if not role:
                    continue
                try:
                    await message.author.add_roles(role)
                    assigned.append(role.name)
                except discord.Forbidden:
                    log.warning("Bot lacks permission to assign role %s", role.name)
                except Exception as e:
                    log.error("Error assigning role %s: %s", role.name, e)

            if not assigned:
                await message.add_reaction("👋")
                return

            role_list = ", ".join(f"**{r}**" for r in assigned)
            embed = discord.Embed(
                title="🎉 Welcome to the community!",
                description=(
                    f"Hey {message.author.mention}! I've assigned you some roles "
                    f"based on your introduction: {role_list}"
                ),
                color=discord.Color.green(),
            )
            embed.set_footer(text="If you'd like different roles, feel free to ask a moderator!")
            await message.channel.send(embed=embed)
            await message.add_reaction("✨")

    except Exception as e:
        log.error("Error handling intro message: %s", e)
        try:
            await message.add_reaction("👋")
        except Exception:
            pass


async def handle_natural_responses(message: discord.Message) -> None:
    """Plain-text chit-chat triggers."""
    content = message.content.lower()

    if any(greet in content for greet in ("hey jule", "hi jule", "hello jule")):
        await message.channel.send(random.choice(GREETINGS))
    elif "thanks jule" in content or "thank you jule" in content:
        await message.channel.send("You're very welcome! 💙 Happy to help!")
    elif "good bot" in content:
        await message.channel.send("Aww, thank you! 🥰 You're pretty great yourself!")
    elif "avatar" in content and not message.mentions:
        await message.channel.send(get_avatar_url(message.author))


async def _cache_member(member: discord.abc.User) -> None:
    db.update_user_cache(
        user_id=member.id,
        username=str(member),
        display_name=getattr(member, "display_name", None),
        avatar_url=str(member.avatar.url) if member.avatar else None,
    )


@bot.event
async def on_ready() -> None:
    log.info("Logged in as %s", bot.user)
    log.info("Database initialized at %s", db.db_path)

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="over our cozy nook 🏡",
    )
    await bot.change_presence(activity=activity)

    await load_extensions()

    check_reminders.start()
    cleanup_tracking.start()
    check_birthdays.start()
    update_user_cache.start()


async def load_extensions() -> None:
    for ext in EXTENSIONS:
        try:
            await bot.load_extension(ext)
            log.info("Loaded extension: %s", ext)
        except Exception as e:
            log.error("Failed to load extension %s: %s", ext, e)


@bot.event
async def on_member_join(member: discord.Member) -> None:
    await _cache_member(member)

    settings = db.get_server_settings(member.guild.id)

    welcome_channel_id = settings.get("welcome_channel_id")
    greet_channel = member.guild.get_channel(welcome_channel_id) if welcome_channel_id else None
    if greet_channel:
        embed = discord.Embed(
            title="🌟 Welcome to Small Cozy Nook! 🌟",
            description=(
                f"Hello, {member.mention}! It is amazing to see you here.\n\n"
                "🎮 Use `!help` to see what I can do!\n"
                "💬 Explore the channels - minimal by design (definitely not because we're lazy XDD)\n"
                "🎉 Have fun and make yourself at home!\n"
            ),
            color=discord.Color.blurple(),
        )
        embed.set_thumbnail(url=get_avatar_url(member))
        embed.set_footer(text="Feel free to ask questions or introduce yourself!")
        await greet_channel.send(embed=embed)

    default_role_id = settings.get("default_role_id")
    if not default_role_id:
        log.info("No default role configured for server %s", member.guild.id)
        return

    default_role = member.guild.get_role(default_role_id)
    if not default_role:
        log.warning("Default role ID %s not found in server", default_role_id)
        return

    try:
        await member.add_roles(default_role)
        log.info("Assigned default role '%s' to %s", default_role.name, member)
    except discord.Forbidden:
        log.error("Bot lacks permission to assign default role '%s'", default_role.name)
    except Exception as e:
        log.error("Error assigning default role: %s", e)


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user:
        return

    if message.author.bot or not message.guild:
        await bot.process_commands(message)
        return

    # Sampled cache refresh to avoid per-message DB writes.
    if random.random() < 0.1:
        await _cache_member(message.author)

    if await spam_detector.track_message(message):
        deleted = await spam_detector.handle_spam(message)
        if deleted:
            warning = await message.channel.send(
                f"⚠️ {message.author.mention} Whoa there! Slow down a bit. "
                f"({len(deleted)} messages deleted for spam)"
            )
            await asyncio.sleep(5)
            try:
                await warning.delete()
            except Exception:
                pass
        return

    settings = db.get_server_settings(message.guild.id)
    intro_channel_id = settings.get("intro_channel_id")
    if intro_channel_id and message.channel.id == intro_channel_id:
        await handle_intro_message(message)

    points_service.increment_message(message.author.id)

    await handle_natural_responses(message)

    if random.random() < RANDOM_REACTION_CHANCE:
        await message.add_reaction(random.choice(RANDOM_REACTIONS))

    await bot.process_commands(message)


# ============================================================================
# Background tasks
# ============================================================================

@tasks.loop(seconds=30)
async def check_reminders() -> None:
    for reminder in reminder_service.get_due_reminders():
        channel = bot.get_channel(reminder["channel"])
        user = bot.get_user(reminder["user"])
        if channel and user:
            await channel.send(f"⏰ {user.mention} Reminder: {reminder['message']}")
        reminder_service.complete_reminder(reminder["id"])


@tasks.loop(hours=1)
async def cleanup_tracking() -> None:
    await spam_detector.cleanup_database()
    log.info("Cleaned up old message tracking data")


@tasks.loop(hours=24)
async def check_birthdays() -> None:
    birthday_users = birthday_service.get_todays_birthdays()
    if not birthday_users:
        return

    for guild in bot.guilds:
        settings = db.get_server_settings(guild.id)
        welcome_channel_id = settings.get("welcome_channel_id")
        greet_channel = guild.get_channel(welcome_channel_id) if welcome_channel_id else None
        if not greet_channel:
            continue

        for user_id in birthday_users:
            member = guild.get_member(user_id)
            if not member:
                continue
            embed = discord.Embed(
                title="🎉 Happy Birthday! 🎂",
                description=f"Wishing {member.mention} an amazing birthday! 🎈🎁",
                color=discord.Color.gold(),
            )
            embed.set_thumbnail(url=get_avatar_url(member))
            await greet_channel.send(embed=embed)
        break


@tasks.loop(hours=6)
async def update_user_cache() -> None:
    try:
        leaderboard = db.get_leaderboard(limit=100)
        user_ids = {uid for uid, _ in leaderboard}

        with db.session_scope(commit=False) as session:
            user_ids.update(b.user_id for b in session.query(Birthday).all())

        updated = 0
        for guild in bot.guilds:
            for uid in user_ids:
                member = guild.get_member(uid)
                if not member:
                    continue
                await _cache_member(member)
                updated += 1

        if updated:
            log.info("Updated user cache for %s users", updated)
    except Exception as e:
        log.error("Error updating user cache: %s", e)


# ============================================================================
# Error handling
# ============================================================================

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument! Check `!help {ctx.command}` for usage.")
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
        return
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `!help` to see available commands.")
        return

    error_msg = str(error)
    if len(error_msg) > 1800:
        error_msg = error_msg[:1800] + "... (truncated)"
    try:
        await ctx.send(f"❌ An error occurred: {error_msg}")
    except discord.HTTPException:
        await ctx.send("❌ An error occurred. Please check the bot logs for details.")

    log.error("Command error in '%s': %s", ctx.command, error)


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN not set in environment")
    bot.run(DISCORD_TOKEN)
