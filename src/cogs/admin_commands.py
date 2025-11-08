"""
Admin commands cog for Jule bot
Handles moderation and administration commands
"""

import asyncio
import json
import discord
from discord.ext import commands

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import MIN_CLEAR_MESSAGES, MAX_CLEAR_MESSAGES
from model.role_assigner import RoleAssigner


class AdminCommands(commands.Cog):
    """Administrative and moderation commands"""

    def __init__(self, bot: commands.Bot, role_assigner: RoleAssigner):
        self.bot = bot
        self.role_assigner = role_assigner

    @commands.command(name="announce", help="[Admin] Make an announcement!")
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx: commands.Context, *, message: str):
        """Make an announcement"""
        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Announced by {ctx.author.display_name}")

        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command(name="clear", help="[Admin] Clear messages! Usage: !clear <amount>")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int):
        """Clear a specified number of messages"""
        if amount < MIN_CLEAR_MESSAGES or amount > MAX_CLEAR_MESSAGES:
            await ctx.send(f"Please specify between {MIN_CLEAR_MESSAGES} and {MAX_CLEAR_MESSAGES} messages!")
            return

        await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🧹 Cleared {amount} messages!")
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command(name="reloadroles", help="[Admin] Reload role mappings configuration")
    @commands.has_permissions(administrator=True)
    async def reloadroles(self, ctx: commands.Context):
        """Reload role configuration"""
        try:
            self.role_assigner.reload_role_mappings()
            await ctx.send("✅ Role mappings reloaded successfully!")
        except Exception as e:
            await ctx.send(f"❌ Error reloading role mappings: {str(e)}")

    @commands.command(name="testrole", help="[Admin] Test role assignment for a message! Usage: !testrole <message>")
    @commands.has_permissions(administrator=True)
    async def testrole(self, ctx: commands.Context, *, intro_text: str):
        """Test what roles would be assigned for a given intro message"""
        try:
            async with ctx.typing():
                role_names, role_ids = await self.role_assigner.assign_roles_from_intro(intro_text)

                if not role_names:
                    await ctx.send("No roles would be assigned for this intro.")
                    return

                # Create an embed showing the results
                embed = discord.Embed(
                    title="🔍 Role Assignment Test",
                    description="Here's what roles would be assigned:",
                    color=discord.Color.blue()
                )

                for role_name, role_id in zip(role_names, role_ids):
                    role = ctx.guild.get_role(role_id)
                    if role:
                        embed.add_field(
                            name=role_name,
                            value=f"{role.mention} (ID: {role_id})",
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name=role_name,
                            value=f"⚠️ Role not found (ID: {role_id})",
                            inline=False
                        )

                embed.set_footer(text="This is a test - no roles were actually assigned")
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error testing role assignment: {str(e)}")

    @commands.command(name="syncroles", help="[Admin] Create all roles from roles.json and update with server IDs")
    @commands.has_permissions(administrator=True)
    async def syncroles(self, ctx: commands.Context):
        """Create all roles from roles.json and update the file with actual server IDs"""
        try:
            async with ctx.typing():
                # Load the roles.json file
                roles_config_path = self.role_assigner.roles_config_path
                with open(roles_config_path, 'r') as f:
                    roles_config = json.load(f)

                created_roles = []
                updated_roles = []
                existing_roles = []

                # Process each role in the config
                for role_name in roles_config.keys():
                    # Check if role already exists on the server
                    existing_role = discord.utils.get(ctx.guild.roles, name=role_name)

                    if existing_role:
                        # Role exists, update the JSON with the correct ID
                        if roles_config[role_name] != existing_role.id:
                            roles_config[role_name] = existing_role.id
                            updated_roles.append(f"{role_name} (ID: {existing_role.id})")
                        else:
                            existing_roles.append(role_name)
                    else:
                        # Role doesn't exist, create it
                        try:
                            new_role = await ctx.guild.create_role(
                                name=role_name,
                                mentionable=True,
                                reason="Auto-created by syncroles command"
                            )
                            roles_config[role_name] = new_role.id
                            created_roles.append(f"{role_name} (ID: {new_role.id})")
                        except discord.Forbidden:
                            await ctx.send(f"❌ Missing permissions to create role: {role_name}")
                            continue
                        except Exception as e:
                            await ctx.send(f"❌ Error creating role {role_name}: {str(e)}")
                            continue

                # Write updated config back to file
                with open(roles_config_path, 'w') as f:
                    json.dump(roles_config, f, indent=2)

                # Reload the role mappings in the role assigner
                self.role_assigner.reload_role_mappings()

                # Create summary embed
                embed = discord.Embed(
                    title="🔄 Role Synchronization Complete",
                    color=discord.Color.green()
                )

                if created_roles:
                    embed.add_field(
                        name=f"✨ Created Roles ({len(created_roles)})",
                        value="\n".join(created_roles),
                        inline=False
                    )

                if updated_roles:
                    embed.add_field(
                        name=f"📝 Updated IDs ({len(updated_roles)})",
                        value="\n".join(updated_roles),
                        inline=False
                    )

                if existing_roles:
                    embed.add_field(
                        name=f"✅ Already Synced ({len(existing_roles)})",
                        value=", ".join(existing_roles),
                        inline=False
                    )

                if not created_roles and not updated_roles:
                    embed.description = "All roles were already synced with the server!"
                else:
                    embed.description = f"Synced {len(created_roles) + len(updated_roles)} roles with the server."

                embed.set_footer(text="roles.json has been updated with current server role IDs")
                await ctx.send(embed=embed)

        except FileNotFoundError:
            await ctx.send(f"❌ Error: roles.json not found at {roles_config_path}")
        except json.JSONDecodeError:
            await ctx.send(f"❌ Error: roles.json contains invalid JSON")
        except Exception as e:
            await ctx.send(f"❌ Error syncing roles: {str(e)}")


async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    role_assigner = bot.role_assigner
    await bot.add_cog(AdminCommands(bot, role_assigner))

