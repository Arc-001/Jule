"""
Custom Help Command for Jule Bot
Mobile-friendly help display with organized categories
"""

import discord
from discord.ext import commands
from typing import Optional


class CustomHelpCommand(commands.Cog):
    """Custom help command with mobile-friendly formatting"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Remove default help command
        self.bot.remove_command('help')

    @commands.command(name="help", aliases=["h", "commands"])
    async def help_command(self, ctx: commands.Context, *, command_name: Optional[str] = None):
        """
        Display help information
        Usage: !help [command_name]
        """
        if command_name:
            # Show detailed help for a specific command
            await self._show_command_help(ctx, command_name)
        else:
            # Show main help menu
            await self._show_main_help(ctx)

    async def _show_main_help(self, ctx: commands.Context):
        """Display the main help menu with all command categories"""
        embed = discord.Embed(
            title="🤖 Jule Bot Commands",
            description=(
                "Your friendly community bot!\n"
                "Use `!help <command>` for details\n"
                "━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.blurple()
        )

        # Fun Commands
        embed.add_field(
            name="🎉 Fun",
            value=(
                "`!hello` - Say hi\n"
                "`!roll [sides]` - Roll dice\n"
                "`!flip` - Flip coin\n"
                "`!8ball` - Magic 8-ball\n"
                "`!fact` - Random fact\n"
                "`!compliment [@user]` - Compliment\n"
                "`!choose <opts>` - Choose for you\n"
                "`!encourage [@user]` - Encourage"
            ),
            inline=False
        )

        # Game Commands
        embed.add_field(
            name="🎮 Games",
            value=(
                "`!rps <choice>` - Rock Paper Scissors\n"
                "`!guess` - Number guessing game"
            ),
            inline=False
        )

        # Community Commands
        embed.add_field(
            name="🌟 Community",
            value=(
                "`!points [@user]` - Check points\n"
                "`!leaderboard` - Top members\n"
                "`!birthday <DD/MM>` - Set birthday\n"
                "`!birthdays` - Upcoming birthdays"
            ),
            inline=False
        )

        # Utility Commands
        embed.add_field(
            name="🛠️ Utility",
            value=(
                "`!poll 'Q' opt1 opt2` - Create poll\n"
                "`!remind <min> <msg>` - Set reminder\n"
                "`!avatar [@user]` - Show avatar\n"
                "`!userinfo [@user]` - User info\n"
                "`!serverinfo` - Server info"
            ),
            inline=False
        )

        # Music Commands
        embed.add_field(
            name="🎵 Music",
            value=(
                "`!join` - Join voice channel\n"
                "`!leave` - Leave channel\n"
                "`!play <query>` - Play music\n"
                "`!pause` - Pause playback\n"
                "`!resume` - Resume playback\n"
                "`!skip` - Skip song\n"
                "`!queue` - Show queue\n"
                "`!clearqueue` - Clear queue\n"
                "`!nowplaying` - Current song\n"
                "`!shuffle` - Shuffle queue\n"
                "`!loop` - Toggle loop\n"
                "`!musicstats` - Your stats"
            ),
            inline=False
        )

        # AI Commands
        embed.add_field(
            name="🧠 AI",
            value=(
                "`!ask <question>` - Ask AI\n"
                "`!explain <topic>` - Get explanation\n"
                "`!wiki <query>` - Wikipedia search\n"
                "`!topicstarter` - Conversation ideas"
            ),
            inline=False
        )

        # Admin Commands (only show if user has permissions)
        if ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_messages:
            embed.add_field(
                name="👑 Admin",
                value=(
                    "`!announce <msg>` - Announcement\n"
                    "`!clear <num>` - Clear messages\n"
                    "`!reloadroles` - Reload roles\n"
                    "`!testrole <msg>` - Test role assign\n"
                    "`!syncroles` - Sync roles config"
                ),
                inline=False
            )

        embed.set_footer(text="💡 Tip: Type !help <command> for more info")
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)

        await ctx.send(embed=embed)

    async def _show_command_help(self, ctx: commands.Context, command_name: str):
        """Show detailed help for a specific command"""
        # Find the command
        cmd = self.bot.get_command(command_name.lower())

        if not cmd:
            await ctx.send(f"❌ Command `{command_name}` not found! Use `!help` to see all commands.")
            return

        # Create detailed embed
        embed = discord.Embed(
            title=f"📖 Command: !{cmd.name}",
            description=cmd.help or "No description available.",
            color=discord.Color.green()
        )

        # Add aliases if any
        if cmd.aliases:
            aliases = ", ".join([f"`!{alias}`" for alias in cmd.aliases])
            embed.add_field(name="Aliases", value=aliases, inline=False)

        # Add usage example
        if cmd.usage:
            embed.add_field(name="Usage", value=f"`!{cmd.name} {cmd.usage}`", inline=False)

        # Add signature
        params = []
        for param_name, param in cmd.clean_params.items():
            if param.default is param.empty:
                params.append(f"<{param_name}>")
            else:
                params.append(f"[{param_name}]")

        if params:
            signature = f"`!{cmd.name} {' '.join(params)}`"
            embed.add_field(name="Format", value=signature, inline=False)

        embed.set_footer(text="<required> [optional]")

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    await bot.add_cog(CustomHelpCommand(bot))

