"""
Jule Discord Bot - Main Entry Point
A friendly, feature-rich community bot
"""

import random
import asyncio
import discord
from discord.ext import commands, tasks

from constants import (
    DISCORD_TOKEN, DATABASE_PATH, CHANNELS_CONFIG_PATH, ROLES_CONFIG_PATH,
    GREET_CHANNEL_ID, DEFAULT_ROLE_ID, SPAM_THRESHOLD, SPAM_TIMEFRAME,
    GREETINGS, RANDOM_REACTIONS, RANDOM_REACTION_CHANCE, MIN_INTRO_LENGTH
)
from model.model import Database
from model.services import SpamDetector, ReminderService, PointsService, BirthdayService, MusicService
from model.role_assigner import RoleAssigner
from utils import load_json_config, get_avatar_url


# ============= BOT SETUP =============

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Initialize database and services
db = Database(DATABASE_PATH)
spam_detector = SpamDetector(db, threshold=SPAM_THRESHOLD, timeframe=SPAM_TIMEFRAME)
reminder_service = ReminderService(db)
points_service = PointsService(db)
birthday_service = BirthdayService(db)
music_service = MusicService(db)
role_assigner = RoleAssigner(ROLES_CONFIG_PATH)

# Attach services to bot for cog access
bot.db = db
bot.spam_detector = spam_detector
bot.reminder_service = reminder_service
bot.points_service = points_service
bot.birthday_service = birthday_service
bot.music_service = music_service
bot.role_assigner = role_assigner

# Load channel mappings
CHANNEL_MAPPINGS = load_json_config(CHANNELS_CONFIG_PATH)
INTRO_CHANNEL_ID = CHANNEL_MAPPINGS.get("intro")


# ============= EVENT HANDLERS =============

async def handle_intro_message(message: discord.Message) -> None:
    """
    Handle messages in the intro channel and assign roles based on content

    Args:
        message: Discord message to analyze
    """
    try:
        # Ignore very short messages
        if len(message.content) < MIN_INTRO_LENGTH:
            return

        # Show typing indicator while processing
        async with message.channel.typing():
            # Analyze the intro and get suggested roles
            role_names, role_ids = await role_assigner.assign_roles_from_intro(message.content)

            if not role_names:
                # No roles suggested, just react positively
                await message.add_reaction("👋")
                return

            # Assign roles to the user
            assigned_roles = []
            for role_id in role_ids:
                role = message.guild.get_role(role_id)
                if role:
                    try:
                        await message.author.add_roles(role)
                        assigned_roles.append(role.name)
                    except discord.Forbidden:
                        print(f"Error: Bot lacks permission to assign role {role.name}")
                    except Exception as e:
                        print(f"Error assigning role {role.name}: {e}")

            if assigned_roles:
                # Send a welcome message with assigned roles
                role_list = ", ".join([f"**{role}**" for role in assigned_roles])
                embed = discord.Embed(
                    title="🎉 Welcome to the community!",
                    description=(
                        f"Hey {message.author.mention}! I've assigned you some roles "
                        f"based on your introduction: {role_list}"
                    ),
                    color=discord.Color.green()
                )
                embed.set_footer(text="If you'd like different roles, feel free to ask a moderator!")
                await message.channel.send(embed=embed)
                await message.add_reaction("✨")
            else:
                # Roles were suggested but couldn't be assigned
                await message.add_reaction("👋")

    except Exception as e:
        print(f"Error handling intro message: {e}")
        # Still give a positive reaction even if role assignment fails
        try:
            await message.add_reaction("👋")
        except:
            pass



@bot.event
async def on_ready():
    """Initialize bot when ready"""
    print(f'🤖 Logged in as {bot.user}')
    print('✨ I am alive and ready to make this community amazing!!')
    print(f'📊 Database initialized at: {db.db_path}')

    # Set bot presence
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="over our cozy nook 🏡"
    )
    await bot.change_presence(activity=activity)

    # Load command cogs
    await load_extensions()

    # Start background tasks
    check_reminders.start()
    cleanup_tracking.start()
    check_birthdays.start()
    update_user_cache.start()


async def load_extensions():
    """Load all command cogs"""
    extensions = [
        'cogs.fun_commands',
        'cogs.game_commands',
        'cogs.community_commands',
        'cogs.utility_commands',
        'cogs.admin_commands',
        'cogs.music_commands'
    ]

    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f'✅ Loaded extension: {extension}')
        except Exception as e:
            print(f'❌ Failed to load extension {extension}: {e}')



@bot.event
async def on_member_join(member: discord.Member):
    """Handle new member joins"""
    # Cache user info
    db.update_user_cache(
        user_id=member.id,
        username=str(member),
        display_name=member.display_name,
        avatar_url=str(member.avatar.url) if member.avatar else None
    )

    # Get greet channel
    greet_channel = member.guild.get_channel(GREET_CHANNEL_ID)
    if not greet_channel:
        print(f"Warning: Greet channel {GREET_CHANNEL_ID} not found")
        return

    # Send welcome message
    embed = discord.Embed(
        title="🌟 Welcome to Small Cozy Nook! 🌟",
        description=(
            f"Hello, {member.mention}! It is amazing to see you here.\n\n"
            "🎮 Use `!help` to see what I can do!\n"
            "💬 Explore the channels - minimal by design (definitely not because we're lazy XDD)\n"
            "🎉 Have fun and make yourself at home!\n"
        ),
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=get_avatar_url(member))
    embed.set_footer(text="Feel free to ask questions or introduce yourself!")

    await greet_channel.send(embed=embed)

    # Assign default role
    default_role = member.guild.get_role(DEFAULT_ROLE_ID)
    if default_role:
        try:
            await member.add_roles(default_role)
        except discord.Forbidden:
            print(f"Error: Bot lacks permission to assign default role")
        except Exception as e:
            print(f"Error assigning default role: {e}")



@bot.event
async def on_message(message: discord.Message):
    """Handle incoming messages"""
    # Ignore own messages
    if message.author == bot.user:
        return

    # Skip bot messages and DMs
    if message.author.bot or not message.guild:
        await bot.process_commands(message)
        return

    # Cache user info periodically (to avoid database overhead on every message)
    # Only update if we have a guild member
    if random.random() < 0.1:  # 10% chance to update cache on each message
        db.update_user_cache(
            user_id=message.author.id,
            username=str(message.author),
            display_name=message.author.display_name,
            avatar_url=str(message.author.avatar.url) if message.author.avatar else None
        )

    # Spam detection
    is_spam = await spam_detector.track_message(message)

    if is_spam:
        # Handle spam - delete messages
        deleted_ids = await spam_detector.handle_spam(message)

        if deleted_ids:
            # Send warning message
            warning = await message.channel.send(
                f"⚠️ {message.author.mention} Whoa there! Slow down a bit. "
                f"({len(deleted_ids)} messages deleted for spam)"
            )
            # Delete warning after 5 seconds
            await asyncio.sleep(5)
            try:
                await warning.delete()
            except:
                pass

        return  # Don't process commands or award points for spam

    # Check if message is in intro channel and assign roles
    if INTRO_CHANNEL_ID and message.channel.id == INTRO_CHANNEL_ID:
        await handle_intro_message(message)

    # Track message count and award points
    points_service.increment_message(message.author.id)

    # Handle natural language responses
    await handle_natural_responses(message)

    # Random reactions to keep things lively
    if random.random() < RANDOM_REACTION_CHANCE:
        await message.add_reaction(random.choice(RANDOM_REACTIONS))

    # Process commands
    await bot.process_commands(message)


async def handle_natural_responses(message: discord.Message):
    """Handle natural language interactions with the bot"""
    content_lower = message.content.lower()

    if any(word in content_lower for word in ["hey jule", "hi jule", "hello jule"]):
        await message.channel.send(random.choice(GREETINGS))

    elif "thanks jule" in content_lower or "thank you jule" in content_lower:
        await message.channel.send("You're very welcome! 💙 Happy to help!")

    elif "good bot" in content_lower:
        await message.channel.send("Aww, thank you! 🥰 You're pretty great yourself!")

    elif "avatar" in content_lower and len(message.mentions) == 0:
        avatar_url = get_avatar_url(message.author)
        await message.channel.send(avatar_url)


# ============= BACKGROUND TASKS =============

@tasks.loop(seconds=30)
async def check_reminders():
    """Check for due reminders every 30 seconds"""
    due_reminders = reminder_service.get_due_reminders()

    for reminder in due_reminders:
        channel = bot.get_channel(reminder['channel'])
        user = bot.get_user(reminder['user'])
        if channel and user:
            await channel.send(f"⏰ {user.mention} Reminder: {reminder['message']}")
        reminder_service.complete_reminder(reminder['id'])


@tasks.loop(hours=1)
async def cleanup_tracking():
    """Clean up old message tracking data every hour"""
    await spam_detector.cleanup_database()
    print("🧹 Cleaned up old message tracking data")


@tasks.loop(hours=24)
async def check_birthdays():
    """Check for birthdays once per day"""
    birthday_users = birthday_service.get_todays_birthdays()

    if not birthday_users:
        return

    # Get first available guild to send messages
    for guild in bot.guilds:
        greet_channel = guild.get_channel(GREET_CHANNEL_ID)
        if greet_channel:
            for user_id in birthday_users:
                member = guild.get_member(user_id)
                if member:
                    embed = discord.Embed(
                        title="🎉 Happy Birthday! 🎂",
                        description=f"Wishing {member.mention} an amazing birthday! 🎈🎁",
                        color=discord.Color.gold()
                    )
                    avatar_url = get_avatar_url(member)
                    embed.set_thumbnail(url=avatar_url)
                    await greet_channel.send(embed=embed)
            break


@tasks.loop(hours=6)
async def update_user_cache():
    """Update user cache for users in database every 6 hours"""
    try:
        # Get all user IDs from leaderboard (top 100 users)
        leaderboard = db.get_leaderboard(limit=100)
        user_ids = [user_id for user_id, _ in leaderboard]

        # Also get users with birthdays
        session = db.get_session()
        from model.model import Birthday
        birthdays = session.query(Birthday).all()
        for b in birthdays:
            if b.user_id not in user_ids:
                user_ids.append(b.user_id)
        session.close()

        # Update cache for each user
        updated_count = 0
        for guild in bot.guilds:
            for user_id in user_ids:
                member = guild.get_member(user_id)
                if member:
                    db.update_user_cache(
                        user_id=member.id,
                        username=str(member),
                        display_name=member.display_name,
                        avatar_url=str(member.avatar.url) if member.avatar else None
                    )
                    updated_count += 1

        if updated_count > 0:
            print(f"👥 Updated user cache for {updated_count} users")
    except Exception as e:
        print(f"Error updating user cache: {e}")


# ============= ERROR HANDLING =============

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Handle command errors"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument! Check `!help {ctx.command}` for usage.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `!help` to see available commands.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Error: {error}")


# ============= RUN BOT =============

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)


