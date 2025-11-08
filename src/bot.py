import discord
from discord.ext import commands, tasks
import os
import random
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv
from model.model import Database
from model.services import SpamDetector, ReminderService, PointsService, BirthdayService

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GREET_CHANNEL_ID = 1436379982015365251
DEFAULT_ROLE_ID = 1316483824854634586

# Bot with commands framework for better organization
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Initialize database and services
db = Database("data/jule.db")
spam_detector = SpamDetector(db, threshold=5, timeframe=20)
reminder_service = ReminderService(db)
points_service = PointsService(db)
birthday_service = BirthdayService(db)

# Storage for bot data (now using database)
bot.user_points = defaultdict(int)  # Legacy - will migrate to DB
bot.birthdays = {}  # Legacy - will migrate to DB
bot.reminders = []  # Legacy - will migrate to DB
bot.user_messages = defaultdict(int)  # Legacy - will migrate to DB

# Fun responses for engagement
GREETINGS = [
    "Hey there! 👋 What's up?",
    "Hello! 😊 How can I make your day better?",
    "Hi! 🌟 Great to see you!",
    "Heya! 💫 Ready for some fun?",
    "Greetings! ✨ How are you doing today?"
]

ENCOURAGEMENTS = [
    "You're doing amazing! 🌟",
    "Keep being awesome! 💪",
    "You're a star! ⭐",
    "Love your energy! ✨",
    "You're the best! 🎉"
]

RANDOM_FACTS = [
    "Honey never spoils! Archaeologists have found 3000-year-old honey that's still edible.",
    "Octopuses have three hearts! Two pump blood to the gills, one to the rest of the body.",
    "Bananas are berries, but strawberries aren't! 🍌",
    "A group of flamingos is called a 'flamboyance'! 🦩",
    "The inventor of the Pringles can is now buried in one!",
    "Sea otters hold hands while sleeping so they don't drift apart! 🦦",
    "A bolt of lightning is five times hotter than the surface of the sun! ⚡"
]

# ============= EVENTS =============

@bot.event
async def on_ready():
    print(f'🤖 Logged in as {bot.user}')
    print('✨ I am alive and ready to make this community amazing!!')
    print(f'📊 Database initialized at: {db.db_path}')
    activity = discord.Activity(type=discord.ActivityType.watching, name="over our cozy nook 🏡")
    await bot.change_presence(activity=activity)
    check_reminders.start()
    cleanup_tracking.start()
    check_birthdays.start()

@bot.event
async def on_member_join(member):
    # Setting up the greet channel
    greet = member.guild.get_channel(GREET_CHANNEL_ID)

    # Sending aesthetic greet message
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
    embed.set_thumbnail(url=member.avatar.url if member.avatar else bot.user.avatar.url)
    embed.set_footer(text="Feel free to ask questions or introduce yourself!")

    await greet.send(embed=embed)

    # Setting up the roles to be given on default
    role = member.guild.get_role(DEFAULT_ROLE_ID)
    if role:
        await member.add_roles(role)

@bot.event
async def on_message(message):
    # Prevents self referential loop
    if message.author == bot.user:
        return

    # Skip bot messages and DMs
    if message.author.bot or not message.guild:
        await bot.process_commands(message)
        return

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

    # Track message count for engagement (using database)
    points_awarded = points_service.increment_message(message.author.id)

    # Legacy tracking for backward compatibility
    bot.user_messages[message.author.id] += 1
    if bot.user_messages[message.author.id] % 10 == 0:
        bot.user_points[message.author.id] += 1

    # Natural language responses
    content_lower = message.content.lower()

    if any(word in content_lower for word in ["hey jule", "hi jule", "hello jule"]):
        await message.channel.send(random.choice(GREETINGS))

    elif "thanks jule" in content_lower or "thank you jule" in content_lower:
        await message.channel.send("You're very welcome! 💙 Happy to help!")

    elif "good bot" in content_lower:
        await message.channel.send("Aww, thank you! 🥰 You're pretty great yourself!")

    elif "avatar" in content_lower and len(message.mentions) == 0:
        await message.channel.send(message.author.avatar.url if message.author.avatar else "No avatar found!")

    # Random reactions to keep things lively
    if random.random() < 0.05:  # 5% chance
        reactions = ["👍", "❤️", "✨", "🎉", "😊", "👏", "🌟"]
        await message.add_reaction(random.choice(reactions))

    # Process commands
    await bot.process_commands(message)

# ============= FUN COMMANDS =============

@bot.command(name="hello", help="Say hello to Jule!")
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}! {random.choice(['😊', '👋', '✨', '🌟'])}")

@bot.command(name="roll", help="Roll a dice! Usage: !roll [sides] (default: 6)")
async def roll(ctx, sides: int = 6):
    if sides < 2:
        await ctx.send("Come on, I need at least 2 sides! 🎲")
        return
    result = random.randint(1, sides)
    await ctx.send(f"🎲 You rolled a {result}!")

@bot.command(name="flip", help="Flip a coin!")
async def flip(ctx):
    result = random.choice(["Heads", "Tails"])
    await ctx.send(f"🪙 The coin landed on: **{result}**!")

@bot.command(name="8ball", help="Ask the magic 8-ball a question!")
async def eightball(ctx, *, question: str = None):
    if not question:
        await ctx.send("You need to ask a question! 🔮")
        return

    responses = [
        "Yes, absolutely! ✨", "No doubt about it! 💫", "Definitely yes! 🌟",
        "Maybe... 🤔", "Ask again later... ⏰", "Cannot predict now... 🔮",
        "No way! ❌", "Don't count on it... 😬", "Very doubtful... 🤨"
    ]
    await ctx.send(f"🔮 {random.choice(responses)}")

@bot.command(name="fact", help="Get a random fun fact!")
async def fact(ctx):
    await ctx.send(f"💡 **Fun Fact:** {random.choice(RANDOM_FACTS)}")

@bot.command(name="compliment", help="Get a compliment or give one to someone!")
async def compliment(ctx, member: discord.Member = None):
    compliments = [
        "is absolutely wonderful! 🌟",
        "lights up the server! ✨",
        "is incredibly kind! 💖",
        "has amazing energy! ⚡",
        "is a true gem! 💎",
        "makes everyone smile! 😊",
        "is super awesome! 🚀"
    ]

    target = member if member else ctx.author
    await ctx.send(f"{target.mention} {random.choice(compliments)}")

@bot.command(name="choose", help="Let Jule choose for you! Usage: !choose option1 option2 option3...")
async def choose(ctx, *choices):
    if len(choices) < 2:
        await ctx.send("Give me at least 2 options to choose from! 🤔")
        return
    await ctx.send(f"I choose: **{random.choice(choices)}**! ✨")

# ============= COMMUNITY ENGAGEMENT =============

@bot.command(name="points", help="Check your community points!")
async def points(ctx, member: discord.Member = None):
    target = member if member else ctx.author
    pts = points_service.get_points(target.id)
    await ctx.send(f"🌟 {target.display_name} has **{pts}** community points!")

@bot.command(name="leaderboard", help="See the top community members!")
async def leaderboard(ctx):
    top_users = points_service.get_leaderboard(limit=10)

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

@bot.command(name="encourage", help="Send encouragement to someone!")
async def encourage(ctx, member: discord.Member = None):
    target = member if member else ctx.author
    await ctx.send(f"{target.mention} {random.choice(ENCOURAGEMENTS)}")

@bot.command(name="birthday", help="Set your birthday! Usage: !birthday <month> <day>")
async def birthday(ctx, month: int, day: int):
    if not (1 <= month <= 12):
        await ctx.send("❌ Month must be between 1 and 12!")
        return

    if not (1 <= day <= 31):
        await ctx.send("❌ Day must be between 1 and 31!")
        return

    birthday_service.add_birthday(ctx.author.id, month, day)
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    await ctx.send(f"🎂 Birthday set to {month_names[month-1]} {day}! I'll wish you on your special day!")

@bot.command(name="birthdays", help="See upcoming birthdays!")
async def birthdays(ctx):
    # For now, just show today's birthdays
    birthday_users = birthday_service.get_todays_birthdays()

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

# ============= UTILITY COMMANDS =============

@bot.command(name="poll", help="Create a poll! Usage: !poll 'Question' option1 option2 option3...")
async def poll(ctx, question: str, *options):
    if len(options) < 2:
        await ctx.send("I need at least 2 options for a poll! 📊")
        return
    if len(options) > 10:
        await ctx.send("Maximum 10 options please! 📊")
        return

    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    embed = discord.Embed(
        title=f"📊 {question}",
        description="\n".join([f"{reactions[i]} {option}" for i, option in enumerate(options)]),
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Poll by {ctx.author.display_name}")

    poll_msg = await ctx.send(embed=embed)

    for i in range(len(options)):
        await poll_msg.add_reaction(reactions[i])

@bot.command(name="remind", help="Set a reminder! Usage: !remind <minutes> <message>")
async def remind(ctx, minutes: int, *, message: str):
    if minutes < 1:
        await ctx.send("Please set at least 1 minute! ⏰")
        return
    if minutes > 1440:  # 24 hours
        await ctx.send("Maximum reminder time is 24 hours (1440 minutes)! ⏰")
        return

    reminder_service.add_reminder(ctx.author.id, ctx.channel.id, message, minutes)
    await ctx.send(f"⏰ Got it! I'll remind you in {minutes} minute(s): '{message}'")

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
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else bot.user.avatar.url)
                    await greet_channel.send(embed=embed)
            break

@bot.command(name="serverinfo", help="Get information about the server!")
async def serverinfo(ctx):
    guild = ctx.guild

    embed = discord.Embed(
        title=f"📊 {guild.name} - Server Info",
        color=discord.Color.purple()
    )

    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
    embed.add_field(name="📅 Created", value=guild.created_at.strftime("%B %d, %Y"), inline=True)
    embed.add_field(name="💬 Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)

    await ctx.send(embed=embed)

@bot.command(name="avatar", help="Get someone's avatar! Usage: !avatar [@user]")
async def avatar(ctx, member: discord.Member = None):
    target = member if member else ctx.author

    embed = discord.Embed(
        title=f"🖼️ {target.display_name}'s Avatar",
        color=discord.Color.blue()
    )
    embed.set_image(url=target.avatar.url if target.avatar else target.default_avatar.url)

    await ctx.send(embed=embed)

@bot.command(name="userinfo", help="Get info about a user! Usage: !userinfo [@user]")
async def userinfo(ctx, member: discord.Member = None):
    target = member if member else ctx.author

    embed = discord.Embed(
        title=f"👤 {target.display_name}",
        color=target.color
    )

    embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
    embed.add_field(name="🏷️ Username", value=str(target), inline=True)
    embed.add_field(name="🆔 ID", value=target.id, inline=True)
    embed.add_field(name="📅 Joined Server", value=target.joined_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="📅 Account Created", value=target.created_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="🌟 Community Points", value=points_service.get_points(target.id), inline=True)

    # Add birthday if set
    birthday = birthday_service.get_birthday(target.id)
    if birthday:
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        birthday_str = f"{month_names[birthday[0]-1]} {birthday[1]}"
        embed.add_field(name="🎂 Birthday", value=birthday_str, inline=True)

    await ctx.send(embed=embed)

# ============= ADMIN COMMANDS =============

@bot.command(name="announce", help="[Admin] Make an announcement!")
@commands.has_permissions(administrator=True)
async def announce(ctx, *, message: str):
    embed = discord.Embed(
        title="📢 Announcement",
        description=message,
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Announced by {ctx.author.display_name}")

    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command(name="clear", help="[Admin] Clear messages! Usage: !clear <amount>")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("Please specify between 1 and 100 messages!")
        return

    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Cleared {amount} messages!")
    await asyncio.sleep(3)
    await msg.delete()

# ============= FUN GAMES =============

@bot.command(name="rps", help="Play rock paper scissors! Usage: !rps <rock/paper/scissors>")
async def rps(ctx, choice: str):
    choices = ["rock", "paper", "scissors"]
    choice = choice.lower()

    if choice not in choices:
        await ctx.send("Choose rock, paper, or scissors! 🪨📄✂️")
        return

    bot_choice = random.choice(choices)

    emoji_map = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}

    result = ""
    if choice == bot_choice:
        result = "It's a tie! 🤝"
    elif (choice == "rock" and bot_choice == "scissors") or \
         (choice == "paper" and bot_choice == "rock") or \
         (choice == "scissors" and bot_choice == "paper"):
        result = "You win! 🎉"
        points_service.add_points(ctx.author.id, 2)
        bot.user_points[ctx.author.id] += 2  # Legacy
    else:
        result = "I win! 😄"

    await ctx.send(f"{emoji_map[choice]} vs {emoji_map[bot_choice]}\n{result}")

@bot.command(name="guess", help="Guess a number between 1-100!")
async def guess(ctx):
    number = random.randint(1, 100)
    await ctx.send("🎯 I'm thinking of a number between 1 and 100! You have 6 tries. Type your guess:")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

    for attempt in range(6):
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=check)
            guess_num = int(msg.content)

            if guess_num == number:
                points_service.add_points(ctx.author.id, 5)
                bot.user_points[ctx.author.id] += 5  # Legacy
                await ctx.send(f"🎉 Correct! The number was {number}! You earned 5 points!")
                return
            elif guess_num < number:
                await ctx.send(f"Higher! {5 - attempt} tries left.")
            else:
                await ctx.send(f"Lower! {5 - attempt} tries left.")
        except asyncio.TimeoutError:
            await ctx.send("⏰ Time's up!")
            return

    await ctx.send(f"😅 Out of tries! The number was {number}. Better luck next time!")

# ============= ERROR HANDLING =============

@bot.event
async def on_command_error(ctx, error):
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

