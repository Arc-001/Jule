"""Discord bot entrypoint.

Configure via environment variables or a .env file:
- DISCORD_TOKEN: token for your bot (required to actually connect)
- SERVER_IP: IP address used when creating DNS A records (optional)
- PORKBUN_APIKEY / PORKBUN_SECRET: optional DNS provider credentials

This script is intentionally minimal. It exposes a `!create <html>` command that
creates a site for the invoking user and replies with the URL (dry-run if DNS keys
aren't present).
"""
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

from subdomain_manager import SubdomainManager


load_dotenv()

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
COMMAND_PREFIX = os.environ.get("COMMAND_PREFIX", "!")

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=None)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id: {bot.user.id})")


@bot.event
async def on_guild_join(guild):
    """Send a greeting message when the bot joins a new server."""
    # Try to send to system channel, or the first available text channel
    channel = guild.system_channel
    if channel is None:
        # Find first text channel we can send to
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                break
    
    if channel:
        greeting = (
            f"👋 Hello {guild.name}!\n\n"
            f"I'm **Jule**, a bot that creates dynamic HTML sites for your users.\n\n"
            f"**Usage:** `{COMMAND_PREFIX}create <html_content>`\n"
            f"I'll sanitize the HTML, create a subdomain site, and reply with the URL!\n\n"
            f"Example: `{COMMAND_PREFIX}create <h1>Hello World!</h1><p>My awesome site</p>`"
        )
        try:
            await channel.send(greeting)
        except Exception as e:
            print(f"Could not send greeting to {guild.name}: {e}")


@bot.command(name="create")
async def create_site(ctx, *, html_content: str):
    """Create a site using the message author as identifier.

    Usage: !create <html content>
    """
    await ctx.send("Creating your site... This may take a moment.")
    manager = SubdomainManager()
    try:
        url = await manager.create_user_site(ctx.author.name, html_content)
        await ctx.send(f"✅ Your site is (or will be) available at: {url}")
    except Exception as exc:
        await ctx.send(f"❌ Error creating site: {exc}")



def main():
    if not DISCORD_TOKEN:
        print("DISCORD_TOKEN not set. The bot will not connect — you can still run tests locally.")
        return
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
