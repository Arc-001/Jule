"""
Admin commands cog for Jule bot
Handles moderation and administration commands
"""

import asyncio
import json
import yaml
from pathlib import Path
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

    @commands.command(name="setintrochannel", help="[Admin] Set the intro channel for role allocation! Usage: !setintrochannel #channel")
    @commands.has_permissions(administrator=True)
    async def setintrochannel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """
        Set the channel where introductions trigger automatic role assignment.

        Usage:
        - !setintrochannel #introductions - Set the intro channel
        - !setintrochannel - Clear the intro channel (disable auto role assignment)
        """
        try:
            if channel:
                # Set the intro channel
                self.bot.db.update_server_settings(
                    guild_id=ctx.guild.id,
                    intro_channel_id=channel.id
                )

                embed = discord.Embed(
                    title="✅ Intro Channel Set",
                    description=f"Automatic role assignment is now enabled for {channel.mention}",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="How it works",
                    value=(
                        "When users post introductions in this channel:\n"
                        "• Messages must be at least 50 characters\n"
                        "• AI analyzes their intro and suggests roles\n"
                        "• Roles are automatically assigned\n"
                        "• A welcome message is sent"
                    ),
                    inline=False
                )
                embed.set_footer(text="Use !testrole <message> to test role assignment")
                await ctx.send(embed=embed)
            else:
                # Clear the intro channel
                self.bot.db.update_server_settings(
                    guild_id=ctx.guild.id,
                    intro_channel_id=None
                )

                embed = discord.Embed(
                    title="🔕 Intro Channel Cleared",
                    description="Automatic role assignment has been disabled.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="To re-enable",
                    value="Use `!setintrochannel #channel` to set a new intro channel",
                    inline=False
                )
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error setting intro channel: {str(e)}")

    @commands.command(name="getintrochannel", help="[Admin] Check which channel is set for intro role allocation")
    @commands.has_permissions(administrator=True)
    async def getintrochannel(self, ctx: commands.Context):
        """Check the current intro channel setting"""
        try:
            server_settings = self.bot.db.get_server_settings(ctx.guild.id)
            intro_channel_id = server_settings.get('intro_channel_id')

            if intro_channel_id:
                channel = ctx.guild.get_channel(intro_channel_id)
                if channel:
                    embed = discord.Embed(
                        title="📍 Current Intro Channel",
                        description=f"Auto role assignment is enabled for {channel.mention}",
                        color=discord.Color.blue()
                    )
                    embed.add_field(
                        name="Channel ID",
                        value=str(intro_channel_id),
                        inline=True
                    )
                    embed.add_field(
                        name="Status",
                        value="✅ Active",
                        inline=True
                    )
                else:
                    embed = discord.Embed(
                        title="⚠️ Invalid Intro Channel",
                        description=f"Channel ID {intro_channel_id} is set but channel not found.",
                        color=discord.Color.orange()
                    )
                    embed.add_field(
                        name="Action Required",
                        value="Use `!setintrochannel #channel` to set a valid channel",
                        inline=False
                    )
            else:
                embed = discord.Embed(
                    title="📍 No Intro Channel Set",
                    description="Automatic role assignment is currently disabled.",
                    color=discord.Color.grey()
                )
                embed.add_field(
                    name="To enable",
                    value="Use `!setintrochannel #channel` to set an intro channel",
                    inline=False
                )

            embed.set_footer(text="Use !testrole <message> to test role assignment")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error getting intro channel: {str(e)}")

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

    @commands.command(name="syncroles", help="[Admin] Sync roles from YAML file! Usage: !syncroles [filename]")
    @commands.has_permissions(administrator=True)
    async def syncroles(self, ctx: commands.Context, yaml_file: str = "roles.yaml"):
        """
        Create and sync roles from a YAML configuration file.
        Creates roles with specified properties, then exports the mapping to roles.json

        Usage: !syncroles [filename]
        Example: !syncroles roles.yaml
        Default: roles.yaml
        """
        try:
            async with ctx.typing():
                # Construct path to YAML file
                config_dir = Path(__file__).parent.parent / "config"
                yaml_path = config_dir / yaml_file
                output_json = config_dir / "roles.json"

                # Check if YAML file exists
                if not yaml_path.exists():
                    await ctx.send(f"❌ Error: Configuration file `{yaml_file}` not found in config directory!")
                    return

                # Load YAML configuration
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)

                if not config or 'role_categories' not in config:
                    await ctx.send(f"❌ Error: Configuration file is empty or invalid!")
                    return

                # Send initial status message
                status_msg = await ctx.send("🎭 Starting role synchronization...")

                # Track statistics
                stats = {
                    'roles_created': 0,
                    'roles_found': 0,
                    'roles_updated': 0,
                    'errors': []
                }

                # Dictionary to store role mappings
                role_mapping = {}

                # Process role categories
                await status_msg.edit(content="🔄 Processing roles...")

                for category_name, category_data in config['role_categories'].items():
                    if 'roles' not in category_data:
                        continue

                    for role_info in category_data['roles']:
                        role_name = role_info['name']
                        role_color_hex = role_info.get('color', '#99AAB5')
                        role_mentionable = role_info.get('mentionable', True)

                        # Convert hex color to discord.Color
                        try:
                            color_int = int(role_color_hex.replace('#', ''), 16)
                            role_color = discord.Color(color_int)
                        except:
                            role_color = discord.Color.default()

                        # Find existing role
                        existing_role = discord.utils.get(ctx.guild.roles, name=role_name)

                        if existing_role:
                            # Update role properties if different
                            needs_update = False
                            if existing_role.color != role_color or existing_role.mentionable != role_mentionable:
                                try:
                                    await existing_role.edit(
                                        color=role_color,
                                        mentionable=role_mentionable,
                                        reason=f"Updated by syncroles from {yaml_file}"
                                    )
                                    stats['roles_updated'] += 1
                                    needs_update = True
                                except discord.Forbidden:
                                    stats['errors'].append(f"Missing permissions to update role: {role_name}")
                                except Exception as e:
                                    stats['errors'].append(f"Error updating role {role_name}: {str(e)}")

                            if not needs_update:
                                stats['roles_found'] += 1

                            # Store in mapping
                            role_mapping[role_name] = existing_role.id
                        else:
                            # Create new role
                            try:
                                new_role = await ctx.guild.create_role(
                                    name=role_name,
                                    color=role_color,
                                    mentionable=role_mentionable,
                                    reason=f"Auto-created by syncroles from {yaml_file}"
                                )
                                stats['roles_created'] += 1
                                role_mapping[role_name] = new_role.id

                            except discord.Forbidden:
                                stats['errors'].append(f"Missing permissions to create role: {role_name}")
                                continue
                            except Exception as e:
                                stats['errors'].append(f"Error creating role {role_name}: {str(e)}")
                                continue

                # Save role mapping to JSON
                await status_msg.edit(content="💾 Saving role mappings...")
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(role_mapping, f, indent=2)

                # Reload the role mappings in the role assigner
                self.role_assigner.reload_role_mappings()

                # Create detailed summary embed
                embed_color = discord.Color.orange() if stats['errors'] else discord.Color.green()
                embed = discord.Embed(
                    title="🎭 Role Synchronization Complete",
                    description=f"Processed {len(role_mapping)} roles from `{yaml_file}`",
                    color=embed_color
                )

                if stats['roles_created'] > 0:
                    embed.add_field(
                        name=f"✨ Created ({stats['roles_created']})",
                        value="New roles created on server",
                        inline=True
                    )

                if stats['roles_updated'] > 0:
                    embed.add_field(
                        name=f"📝 Updated ({stats['roles_updated']})",
                        value="Role properties updated",
                        inline=True
                    )

                if stats['roles_found'] > 0:
                    embed.add_field(
                        name=f"✅ Already Synced ({stats['roles_found']})",
                        value="Roles already up-to-date",
                        inline=True
                    )

                if stats['errors']:
                    error_text = "\n".join(stats['errors'][:5])
                    if len(stats['errors']) > 5:
                        error_text += f"\n... and {len(stats['errors']) - 5} more errors"
                    embed.add_field(
                        name=f"⚠️ Errors ({len(stats['errors'])})",
                        value=error_text,
                        inline=False
                    )

                embed.add_field(
                    name="📋 Files Updated",
                    value=f"✅ `roles.json` - Role name to ID mappings\n✅ Loaded from `{yaml_file}`",
                    inline=False
                )

                embed.set_footer(text=f"Total: {stats['roles_created']} created, {stats['roles_updated']} updated, {stats['roles_found']} unchanged")
                await status_msg.delete()
                await ctx.send(embed=embed)

        except FileNotFoundError:
            await ctx.send(f"❌ Error: {yaml_file} not found in config directory")
        except yaml.YAMLError as e:
            await ctx.send(f"❌ Error: Invalid YAML in {yaml_file}\n```{str(e)}```")
        except json.JSONDecodeError:
            await ctx.send(f"❌ Error: Could not write to roles.json")
        except Exception as e:
            await ctx.send(f"❌ Error syncing roles: {str(e)}")

    @commands.command(name="syncchannels", help="[Admin] Sync channels from YAML file! Usage: !syncchannels [filename]")
    @commands.has_permissions(administrator=True)
    async def syncchannels(self, ctx: commands.Context, yaml_file: str = "channels.yaml"):
        """
        Create and sync channels from a YAML configuration file.
        Creates categories and channels, then exports the mapping to current_channels.json

        Usage: !syncchannels [filename]
        Example: !syncchannels channels_minimal_test.yaml
        Default: channels.yaml
        """
        try:
            async with ctx.typing():
                # Construct path to YAML file
                config_dir = Path(__file__).parent.parent / "config"
                yaml_path = config_dir / yaml_file
                output_json = config_dir / "current_channels.json"

                # Check if YAML file exists
                if not yaml_path.exists():
                    await ctx.send(f"❌ Error: Configuration file `{yaml_file}` not found in config directory!")
                    return

                # Load YAML configuration
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)

                if not config:
                    await ctx.send(f"❌ Error: Configuration file is empty or invalid!")
                    return

                # Send initial status message
                status_msg = await ctx.send("🚀 Starting channel synchronization...")

                # Track statistics
                stats = {
                    'categories_created': 0,
                    'categories_found': 0,
                    'channels_created': 0,
                    'channels_found': 0,
                    'channels_updated': 0,
                    'errors': []
                }

                # Dictionary to store channel mappings
                channel_mapping = {}

                # Process categories
                if 'categories' in config:
                    await status_msg.edit(content="🔄 Processing categories and channels...")

                    for category_name, category_data in config['categories'].items():
                        # Find or create category
                        category = discord.utils.get(ctx.guild.categories, name=category_name)

                        if not category:
                            try:
                                category = await ctx.guild.create_category(
                                    name=category_name,
                                    reason=f"Auto-created by syncchannels command from {yaml_file}"
                                )
                                stats['categories_created'] += 1
                            except discord.Forbidden:
                                stats['errors'].append(f"Missing permissions to create category: {category_name}")
                                continue
                            except Exception as e:
                                stats['errors'].append(f"Error creating category {category_name}: {str(e)}")
                                continue
                        else:
                            stats['categories_found'] += 1

                        # Process channels in this category
                        if 'channels' in category_data:
                            for channel_info in category_data['channels']:
                                channel_name = channel_info['name']
                                channel_type = channel_info.get('type', 'text')
                                channel_desc = channel_info.get('description', '')

                                # Find existing channel
                                if channel_type == 'voice':
                                    existing_channel = discord.utils.get(category.voice_channels, name=channel_name)
                                else:
                                    existing_channel = discord.utils.get(category.text_channels, name=channel_name)

                                if existing_channel:
                                    # Update description if different
                                    if channel_type == 'text' and existing_channel.topic != channel_desc:
                                        try:
                                            await existing_channel.edit(topic=channel_desc)
                                            stats['channels_updated'] += 1
                                        except:
                                            pass

                                    stats['channels_found'] += 1
                                    # Store in mapping (remove emojis and special characters for key)
                                    clean_name = ''.join(c for c in channel_name if c.isalnum() or c in ['-', '_']).strip('-_').lower()
                                    channel_mapping[clean_name] = existing_channel.id
                                else:
                                    # Create new channel
                                    try:
                                        if channel_type == 'voice':
                                            new_channel = await category.create_voice_channel(
                                                name=channel_name,
                                                reason=f"Auto-created by syncchannels from {yaml_file}"
                                            )
                                        else:
                                            new_channel = await category.create_text_channel(
                                                name=channel_name,
                                                topic=channel_desc,
                                                reason=f"Auto-created by syncchannels from {yaml_file}"
                                            )

                                        stats['channels_created'] += 1
                                        # Store in mapping
                                        clean_name = ''.join(c for c in channel_name if c.isalnum() or c in ['-', '_']).strip('-_').lower()
                                        channel_mapping[clean_name] = new_channel.id

                                    except discord.Forbidden:
                                        stats['errors'].append(f"Missing permissions to create channel: {channel_name}")
                                        continue
                                    except Exception as e:
                                        stats['errors'].append(f"Error creating channel {channel_name}: {str(e)}")
                                        continue

                # Process standalone channels (no category)
                if 'standalone' in config:
                    await status_msg.edit(content="🔄 Processing standalone channels...")

                    for channel_info in config['standalone']:
                        channel_name = channel_info['name']
                        channel_type = channel_info.get('type', 'text')
                        channel_desc = channel_info.get('description', '')

                        # Find existing channel (without category)
                        if channel_type == 'voice':
                            existing_channel = discord.utils.get(
                                [ch for ch in ctx.guild.voice_channels if ch.category is None],
                                name=channel_name
                            )
                        else:
                            existing_channel = discord.utils.get(
                                [ch for ch in ctx.guild.text_channels if ch.category is None],
                                name=channel_name
                            )

                        if existing_channel:
                            # Update description if different
                            if channel_type == 'text' and existing_channel.topic != channel_desc:
                                try:
                                    await existing_channel.edit(topic=channel_desc)
                                    stats['channels_updated'] += 1
                                except:
                                    pass

                            stats['channels_found'] += 1
                            clean_name = ''.join(c for c in channel_name if c.isalnum() or c in ['-', '_']).strip('-_').lower()
                            channel_mapping[clean_name] = existing_channel.id
                        else:
                            # Create new channel
                            try:
                                if channel_type == 'voice':
                                    new_channel = await ctx.guild.create_voice_channel(
                                        name=channel_name,
                                        reason=f"Auto-created by syncchannels from {yaml_file}"
                                    )
                                else:
                                    new_channel = await ctx.guild.create_text_channel(
                                        name=channel_name,
                                        topic=channel_desc,
                                        reason=f"Auto-created by syncchannels from {yaml_file}"
                                    )

                                stats['channels_created'] += 1
                                clean_name = ''.join(c for c in channel_name if c.isalnum() or c in ['-', '_']).strip('-_').lower()
                                channel_mapping[clean_name] = new_channel.id

                            except discord.Forbidden:
                                stats['errors'].append(f"Missing permissions to create channel: {channel_name}")
                                continue
                            except Exception as e:
                                stats['errors'].append(f"Error creating channel {channel_name}: {str(e)}")
                                continue

                # Save channel mapping to JSON
                await status_msg.edit(content="💾 Saving channel mappings...")
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(channel_mapping, f, indent=2)

                # Create detailed summary embed
                embed = discord.Embed(
                    title="🌌 Channel Synchronization Complete",
                    color=discord.Color.blue()
                )

                # Categories summary
                if stats['categories_created'] > 0 or stats['categories_found'] > 0:
                    cat_summary = []
                    if stats['categories_created'] > 0:
                        cat_summary.append(f"✨ Created: {stats['categories_created']}")
                    if stats['categories_found'] > 0:
                        cat_summary.append(f"✅ Found: {stats['categories_found']}")
                    embed.add_field(
                        name="📁 Categories",
                        value=" | ".join(cat_summary),
                        inline=False
                    )

                # Channels summary
                channel_summary = []
                if stats['channels_created'] > 0:
                    channel_summary.append(f"✨ Created: {stats['channels_created']}")
                if stats['channels_found'] > 0:
                    channel_summary.append(f"✅ Found: {stats['channels_found']}")
                if stats['channels_updated'] > 0:
                    channel_summary.append(f"📝 Updated: {stats['channels_updated']}")

                embed.add_field(
                    name="📺 Channels",
                    value=" | ".join(channel_summary) if channel_summary else "No changes",
                    inline=False
                )

                # Total synced channels
                total_synced = len(channel_mapping)
                embed.add_field(
                    name="💾 Channel Mapping",
                    value=f"Saved {total_synced} channel IDs to `current_channels.json`",
                    inline=False
                )

                # Errors (if any)
                if stats['errors']:
                    error_text = "\n".join(stats['errors'][:5])  # Show first 5 errors
                    if len(stats['errors']) > 5:
                        error_text += f"\n... and {len(stats['errors']) - 5} more errors"
                    embed.add_field(
                        name=f"⚠️ Errors ({len(stats['errors'])})",
                        value=error_text,
                        inline=False
                    )
                    embed.color = discord.Color.orange()

                embed.set_footer(text=f"Configuration: {yaml_file}")

                await status_msg.delete()
                await ctx.send(embed=embed)

        except FileNotFoundError:
            await ctx.send(f"❌ Error: Configuration file `{yaml_file}` not found!")
        except yaml.YAMLError as e:
            await ctx.send(f"❌ Error parsing YAML file: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ Unexpected error during channel sync: {str(e)}")

    @commands.command(name="setdefaultrole", help="[Admin] Set the default role for new members! Usage: !setdefaultrole @role")
    @commands.has_permissions(administrator=True)
    async def setdefaultrole(self, ctx: commands.Context, role: discord.Role = None):
        """
        Set the role that will be automatically assigned to new members when they join.

        Usage:
        - !setdefaultrole @Member - Set the default role
        - !setdefaultrole - Clear the default role (disable auto assignment)
        """
        try:
            if role:
                # Validate that the bot can assign this role
                if role.position >= ctx.guild.me.top_role.position:
                    await ctx.send(f"❌ I cannot assign the role {role.mention} because it's higher than or equal to my highest role!")
                    return

                if role.managed:
                    await ctx.send(f"❌ The role {role.mention} is managed by an integration and cannot be assigned manually!")
                    return

                # Set the default role
                self.bot.db.update_server_settings(
                    guild_id=ctx.guild.id,
                    default_role_id=role.id
                )

                embed = discord.Embed(
                    title="✅ Default Role Set",
                    description=f"New members will automatically receive {role.mention}",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Role Details",
                    value=(
                        f"**Name:** {role.name}\n"
                        f"**ID:** {role.id}\n"
                        f"**Color:** {role.color}\n"
                        f"**Members:** {len(role.members)}"
                    ),
                    inline=False
                )
                embed.set_footer(text="This role will be assigned when new members join the server")
                await ctx.send(embed=embed)

            else:
                # Clear the default role
                self.bot.db.update_server_settings(
                    guild_id=ctx.guild.id,
                    default_role_id=None
                )

                embed = discord.Embed(
                    title="🔕 Default Role Cleared",
                    description="New members will no longer receive a role automatically.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="To re-enable",
                    value="Use `!setdefaultrole @role` to set a new default role",
                    inline=False
                )
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error setting default role: {str(e)}")

    @commands.command(name="getdefaultrole", help="[Admin] Check which role is set as the default for new members")
    @commands.has_permissions(administrator=True)
    async def getdefaultrole(self, ctx: commands.Context):
        """Check the current default role setting"""
        try:
            server_settings = self.bot.db.get_server_settings(ctx.guild.id)
            default_role_id = server_settings.get('default_role_id')

            if default_role_id:
                role = ctx.guild.get_role(default_role_id)
                if role:
                    embed = discord.Embed(
                        title="📍 Current Default Role",
                        description=f"New members will automatically receive {role.mention}",
                        color=discord.Color.blue()
                    )
                    embed.add_field(
                        name="Role Details",
                        value=(
                            f"**Name:** {role.name}\n"
                            f"**ID:** {role.id}\n"
                            f"**Color:** {role.color}\n"
                            f"**Members:** {len(role.members)}"
                        ),
                        inline=False
                    )
                    embed.add_field(
                        name="Status",
                        value="✅ Active",
                        inline=True
                    )
                else:
                    embed = discord.Embed(
                        title="⚠️ Invalid Default Role",
                        description=f"Role ID {default_role_id} is set but the role no longer exists.",
                        color=discord.Color.orange()
                    )
                    embed.add_field(
                        name="Action Required",
                        value="Use `!setdefaultrole @role` to set a valid role",
                        inline=False
                    )
            else:
                embed = discord.Embed(
                    title="📍 No Default Role Set",
                    description="New members will not receive a role automatically.",
                    color=discord.Color.grey()
                )
                embed.add_field(
                    name="To enable",
                    value="Use `!setdefaultrole @role` to set a default role",
                    inline=False
                )

            embed.set_footer(text="Default roles are assigned when users join the server")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error getting default role: {str(e)}")


async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    role_assigner = bot.role_assigner
    await bot.add_cog(AdminCommands(bot, role_assigner))

