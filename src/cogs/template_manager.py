"""
AI-Based Template Generator and Manager for Discord Server
Generates, manages, and syncs role/channel templates using AI
"""

import discord
from discord.ext import commands
import yaml
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import shutil

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from constants import GEMINI_API_KEY
    import google.generativeai as genai
except ImportError:
    GEMINI_API_KEY = None
    genai = None


class TemplateManager(commands.Cog):
    """AI-powered template generation and management system"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_dir = Path(__file__).parent.parent / "config"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Configure Gemini API
        if not GEMINI_API_KEY or not genai:
            print("Warning: GEMINI_API_KEY not found or genai not available. Template generation will be limited.")
            self.model = None
        else:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

        # Protected files that should never be overwritten
        self.protected_files = ['roles.yaml', 'channels.yaml']

        # Files to track currently active templates
        self.active_roles_template_file = self.config_dir / ".active_roles_template"
        self.active_channels_template_file = self.config_dir / ".active_channels_template"

    def _get_active_template(self, template_type: str) -> Optional[str]:
        """Get the currently active template name for roles or channels"""
        if template_type == 'roles':
            tracking_file = self.active_roles_template_file
        elif template_type == 'channels':
            tracking_file = self.active_channels_template_file
        else:
            return None

        if tracking_file.exists():
            try:
                with open(tracking_file, 'r') as f:
                    template_name = f.read().strip()
                    # Verify the template file still exists
                    if (self.config_dir / template_name).exists():
                        return template_name
            except:
                pass
        return None

    def _set_active_template(self, template_type: str, template_name: str):
        """Set the currently active template name for roles or channels"""
        if template_type == 'roles':
            tracking_file = self.active_roles_template_file
        elif template_type == 'channels':
            tracking_file = self.active_channels_template_file
        else:
            return

        try:
            with open(tracking_file, 'w') as f:
                f.write(template_name)
        except Exception as e:
            print(f"Warning: Could not update active template tracking: {e}")

    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """Create a timestamped backup of a file"""
        if not file_path.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(file_path, backup_path)
        return backup_path

    def _list_backups(self, template_type: str) -> List[Tuple[str, Path]]:
        """List all backups for a specific template type (roles/channels)"""
        pattern = f"{template_type}_*.yaml"
        backups = sorted(self.backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

        result = []
        for backup in backups[:10]:  # Return last 10 backups
            timestamp_str = backup.stem.replace(f"{template_type}_", "")
            try:
                dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                result.append((display_time, backup))
            except ValueError:
                continue

        return result

    async def _generate_roles_template(self, description: str) -> Dict:
        """Generate a roles template using AI based on user description"""
        if not self.model:
            raise Exception("AI service is not available. Please configure GEMINI_API_KEY.")

        prompt = f"""Generate a Discord server roles configuration in YAML format based on this description:
{description}

Create a comprehensive role structure with appropriate categories. Follow this EXACT format:

role_categories:
  "category_name":
    description: "Category description"
    roles:
      - name: "role name"
        color: "#HEXCOLOR"
        mentionable: true/false

Guidelines:
- Use appropriate hex colors for each role
- Set mentionable to true for roles users might want to ping, false for personal roles (age, gender, etc.)
- Create 3-7 categories based on the description
- Each category should have 3-10 roles
- Use lowercase for role names
- Be creative and relevant to the description
- Include practical categories like hobbies, interests, regions, etc. if applicable

Output ONLY the YAML content, no explanations or markdown code blocks."""

        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            yaml_content = response.text.strip()

            # Remove markdown code blocks if present
            if yaml_content.startswith('```'):
                lines = yaml_content.split('\n')
                yaml_content = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

            # Parse and validate
            config = yaml.safe_load(yaml_content)
            if not config or 'role_categories' not in config:
                raise ValueError("Invalid YAML structure generated")

            return config
        except Exception as e:
            raise Exception(f"Failed to generate roles template: {str(e)}")

    async def _generate_channels_template(self, description: str) -> Dict:
        """Generate a channels template using AI based on user description"""
        if not self.model:
            raise Exception("AI service is not available. Please configure GEMINI_API_KEY.")

        prompt = f"""Generate a Discord server channels configuration in YAML format based on this description:
{description}

Create a comprehensive channel structure with categories. Follow this EXACT format:

categories:
  "Category Name":
    channels:
      - name: "channel-name"
        type: "text" or "voice"
        description: "Channel description"

standalone:
  - name: "standalone-channel"
    type: "text"
    description: "Description"

Guidelines:
- Use emojis in category names to make them visually appealing
- Channel names should use dashes and lowercase
- Create 3-6 categories based on the description
- Each category should have 2-6 channels
- Include both text and voice channels appropriately
- Use "text" or "voice" for type field
- Standalone channels are optional
- Be creative and relevant to the description

Output ONLY the YAML content, no explanations or markdown code blocks."""

        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            yaml_content = response.text.strip()

            # Remove markdown code blocks if present
            if yaml_content.startswith('```'):
                lines = yaml_content.split('\n')
                yaml_content = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

            # Parse and validate
            config = yaml.safe_load(yaml_content)
            if not config or 'categories' not in config:
                raise ValueError("Invalid YAML structure generated")

            return config
        except Exception as e:
            raise Exception(f"Failed to generate channels template: {str(e)}")

    async def _remove_managed_roles(self, ctx: commands.Context, yaml_file: str) -> Dict:
        """Remove all roles that were created from a specific YAML template"""
        yaml_path = self.config_dir / yaml_file
        if not yaml_path.exists():
            return {'deleted': 0, 'errors': []}

        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        stats = {'deleted': 0, 'errors': []}

        if not config or 'role_categories' not in config:
            return stats

        for category_name, category_data in config['role_categories'].items():
            if 'roles' not in category_data:
                continue

            for role_info in category_data['roles']:
                role_name = role_info['name']
                existing_role = discord.utils.get(ctx.guild.roles, name=role_name)

                if existing_role:
                    try:
                        # Don't delete @everyone or managed roles
                        if existing_role.is_default() or existing_role.managed:
                            continue

                        await existing_role.delete(reason=f"Removed by template manager")
                        stats['deleted'] += 1
                        await asyncio.sleep(0.5)  # Rate limiting
                    except discord.Forbidden:
                        stats['errors'].append(f"Missing permissions to delete role: {role_name}")
                    except Exception as e:
                        stats['errors'].append(f"Error deleting role {role_name}: {str(e)}")

        return stats

    async def _remove_managed_channels(self, ctx: commands.Context, yaml_file: str) -> Dict:
        """Remove all channels that were created from a specific YAML template"""
        yaml_path = self.config_dir / yaml_file
        if not yaml_path.exists():
            return {'deleted': 0, 'categories_deleted': 0, 'errors': []}

        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        stats = {'deleted': 0, 'categories_deleted': 0, 'errors': []}

        if not config:
            return stats

        # Remove channels from categories
        if 'categories' in config:
            for category_name, category_data in config['categories'].items():
                category = discord.utils.get(ctx.guild.categories, name=category_name)

                if category:
                    # Delete all channels in category
                    if 'channels' in category_data:
                        for channel_info in category_data['channels']:
                            channel_name = channel_info['name']
                            channel = discord.utils.get(category.channels, name=channel_name)

                            if channel:
                                try:
                                    await channel.delete(reason="Removed by template manager")
                                    stats['deleted'] += 1
                                    await asyncio.sleep(0.5)
                                except discord.Forbidden:
                                    stats['errors'].append(f"Missing permissions to delete channel: {channel_name}")
                                except Exception as e:
                                    stats['errors'].append(f"Error deleting channel {channel_name}: {str(e)}")

                    # Delete category if empty
                    try:
                        if len(category.channels) == 0:
                            await category.delete(reason="Removed by template manager")
                            stats['categories_deleted'] += 1
                            await asyncio.sleep(0.5)
                    except Exception as e:
                        stats['errors'].append(f"Error deleting category {category_name}: {str(e)}")

        # Remove standalone channels
        if 'standalone' in config:
            for channel_info in config['standalone']:
                channel_name = channel_info['name']
                # Find in all text/voice channels without category
                channel = discord.utils.get(
                    [ch for ch in ctx.guild.channels if ch.category is None],
                    name=channel_name
                )

                if channel:
                    try:
                        await channel.delete(reason="Removed by template manager")
                        stats['deleted'] += 1
                        await asyncio.sleep(0.5)
                    except discord.Forbidden:
                        stats['errors'].append(f"Missing permissions to delete channel: {channel_name}")
                    except Exception as e:
                        stats['errors'].append(f"Error deleting channel {channel_name}: {str(e)}")

        return stats

    @commands.command(name="genroles", help="[Admin] Generate a new roles template using AI")
    @commands.has_permissions(administrator=True)
    async def generate_roles_template(self, ctx: commands.Context, *, description: str):
        """
        Generate a new roles template using AI based on a description.

        Usage: !genroles <description>
        Example: !genroles Create roles for a gaming community with competitive ranks and game preferences
        """
        status_msg = None
        template_name = None
        try:
            async with ctx.typing():
                # Send initial message
                status_msg = await ctx.send("🤖 AI is generating your roles template...")

                # Generate template
                config = await self._generate_roles_template(description)

                # Create filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                template_name = f"roles_generated_{timestamp}.yaml"
                template_path = self.config_dir / template_name

                # Save template
                with open(template_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

                # Count roles
                total_roles = sum(len(cat['roles']) for cat in config['role_categories'].values() if 'roles' in cat)
                total_categories = len(config['role_categories'])

                # Create embed
                embed = discord.Embed(
                    title="✅ Roles Template Generated",
                    description=f"Created `{template_name}` with **{total_roles} roles** across **{total_categories} categories**",
                    color=discord.Color.green()
                )

                # Add preview of categories (truncate long names to avoid Discord's 2000 char limit)
                preview = []
                for cat_name, cat_data in list(config['role_categories'].items())[:3]:
                    role_count = len(cat_data.get('roles', []))
                    # Truncate category name if too long
                    display_name = cat_name[:50] + "..." if len(cat_name) > 50 else cat_name
                    preview.append(f"**{display_name}**: {role_count} roles")

                if len(config['role_categories']) > 3:
                    preview.append(f"... and {len(config['role_categories']) - 3} more categories")

                # Ensure preview doesn't exceed reasonable length
                preview_text = "\n".join(preview)
                if len(preview_text) > 500:
                    preview_text = preview_text[:500] + "..."

                embed.add_field(
                    name="📋 Categories Preview",
                    value=preview_text,
                    inline=False
                )

                embed.add_field(
                    name="📝 Next Steps",
                    value=f"Review the template and apply it using:\n`!applyroles {template_name}`",
                    inline=False
                )

                embed.set_footer(text="Template saved in config folder")

                await status_msg.delete()

                # Try to send the embed, catch if it's too long
                try:
                    await ctx.send(embed=embed)
                except discord.HTTPException as e:
                    # Embed was too long, send simplified message
                    if "length" in str(e).lower():
                        await ctx.send(
                            f"✅ Template `{template_name}` generated successfully!\n"
                            f"**{total_roles} roles** across **{total_categories} categories**\n\n"
                            f"Use `!listtemplates` to view and `!applyroles {template_name}` to apply it."
                        )
                    else:
                        raise  # Re-raise if it's a different HTTP error

        except discord.HTTPException as e:
            # Discord message too long or other HTTP error
            if status_msg:
                try:
                    await status_msg.delete()
                except:
                    pass

            if template_name:
                # Template was saved but message failed
                try:
                    await ctx.send(
                        f"✅ Template saved as `{template_name}`\n"
                        f"Use `!listtemplates` to see it and `!applyroles {template_name}` to apply it."
                    )
                except:
                    pass  # If even this fails, the global handler will catch it
            else:
                # Truncate error message if needed
                error_msg = str(e)
                if len(error_msg) > 1500:
                    error_msg = error_msg[:1500] + "..."
                try:
                    await ctx.send(f"❌ Error: {error_msg}")
                except:
                    await ctx.send("❌ An error occurred while sending the response.")
        except Exception as e:
            if status_msg:
                try:
                    await status_msg.delete()
                except:
                    pass

            # Truncate error message to avoid exceeding Discord's limit
            error_msg = str(e)
            if len(error_msg) > 1500:
                error_msg = error_msg[:1500] + "..."

            try:
                await ctx.send(f"❌ Error generating roles template: {error_msg}")
            except discord.HTTPException:
                await ctx.send("❌ An error occurred. Please check the bot logs.")

    @commands.command(name="genchannels", help="[Admin] Generate a new channels template using AI")
    @commands.has_permissions(administrator=True)
    async def generate_channels_template(self, ctx: commands.Context, *, description: str):
        """
        Generate a new channels template using AI based on a description.

        Usage: !genchannels <description>
        Example: !genchannels Create channels for an art community with separate spaces for different mediums
        """
        status_msg = None
        template_name = None
        try:
            async with ctx.typing():
                # Send initial message
                status_msg = await ctx.send("🤖 AI is generating your channels template...")

                # Generate template
                config = await self._generate_channels_template(description)

                # Create filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                template_name = f"channels_generated_{timestamp}.yaml"
                template_path = self.config_dir / template_name

                # Save template
                with open(template_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

                # Count channels
                total_channels = sum(
                    len(cat.get('channels', []))
                    for cat in config['categories'].values()
                )
                if 'standalone' in config:
                    total_channels += len(config['standalone'])
                total_categories = len(config['categories'])

                # Create embed
                embed = discord.Embed(
                    title="✅ Channels Template Generated",
                    description=f"Created `{template_name}` with **{total_channels} channels** across **{total_categories} categories**",
                    color=discord.Color.blue()
                )

                # Add preview of categories (truncate long names to avoid Discord's 2000 char limit)
                preview = []
                for cat_name, cat_data in list(config['categories'].items())[:3]:
                    channel_count = len(cat_data.get('channels', []))
                    # Truncate category name if too long
                    display_name = cat_name[:50] + "..." if len(cat_name) > 50 else cat_name
                    preview.append(f"**{display_name}**: {channel_count} channels")

                if len(config['categories']) > 3:
                    preview.append(f"... and {len(config['categories']) - 3} more categories")

                # Ensure preview doesn't exceed reasonable length
                preview_text = "\n".join(preview)
                if len(preview_text) > 500:
                    preview_text = preview_text[:500] + "..."

                embed.add_field(
                    name="📋 Categories Preview",
                    value=preview_text,
                    inline=False
                )

                embed.add_field(
                    name="📝 Next Steps",
                    value=f"Review the template and apply it using:\n`!applychannels {template_name}`",
                    inline=False
                )

                embed.set_footer(text="Template saved in config folder")

                await status_msg.delete()

                # Try to send the embed, catch if it's too long
                try:
                    await ctx.send(embed=embed)
                except discord.HTTPException as e:
                    # Embed was too long, send simplified message
                    if "length" in str(e).lower():
                        await ctx.send(
                            f"✅ Template `{template_name}` generated successfully!\n"
                            f"**{total_channels} channels** across **{total_categories} categories**\n\n"
                            f"Use `!listtemplates` to view and `!applychannels {template_name}` to apply it."
                        )
                    else:
                        raise  # Re-raise if it's a different HTTP error

        except discord.HTTPException as e:
            # Discord message too long or other HTTP error
            if status_msg:
                try:
                    await status_msg.delete()
                except:
                    pass

            if template_name:
                # Template was saved but message failed
                try:
                    await ctx.send(
                        f"✅ Template saved as `{template_name}`\n"
                        f"Use `!listtemplates` to see it and `!applychannels {template_name}` to apply it."
                    )
                except:
                    pass  # If even this fails, the global handler will catch it
            else:
                # Truncate error message if needed
                error_msg = str(e)
                if len(error_msg) > 1500:
                    error_msg = error_msg[:1500] + "..."
                try:
                    await ctx.send(f"❌ Error: {error_msg}")
                except:
                    await ctx.send("❌ An error occurred while sending the response.")
        except Exception as e:
            if status_msg:
                try:
                    await status_msg.delete()
                except:
                    pass

            # Truncate error message to avoid exceeding Discord's limit
            error_msg = str(e)
            if len(error_msg) > 1500:
                error_msg = error_msg[:1500] + "..."

            try:
                await ctx.send(f"❌ Error generating channels template: {error_msg}")
            except discord.HTTPException:
                await ctx.send("❌ An error occurred. Please check the bot logs.")

    @commands.command(name="applyroles", help="[Admin] Apply a roles template (removes old, applies new)")
    @commands.has_permissions(administrator=True)
    async def apply_roles_template(self, ctx: commands.Context, template_file: str, confirm: str = None):
        """
        Apply a roles template to the server. This will:
        1. Backup current active template
        2. Remove all roles from current template
        3. Apply new template

        Usage: !applyroles <template_file> confirm
        Example: !applyroles roles_generated_20250110_143022.yaml confirm
        """
        # Safety check for protected files
        if template_file in self.protected_files:
            await ctx.send(f"❌ Cannot apply protected file `{template_file}`. The default templates are read-only.")
            return

        template_path = self.config_dir / template_file
        if not template_path.exists():
            await ctx.send(f"❌ Template file `{template_file}` not found in config directory!")
            return

        # Require confirmation
        if confirm != "confirm":
            embed = discord.Embed(
                title="⚠️ Confirmation Required",
                description="This action will **delete existing roles** from the current template and apply the new template.",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="What will happen:",
                value="1️⃣ Current template is backed up\n"
                      "2️⃣ All roles from current template are **deleted**\n"
                      "3️⃣ New roles from template are created\n"
                      "4️⃣ Role mappings are updated",
                inline=False
            )
            embed.add_field(
                name="To proceed, run:",
                value=f"`!applyroles {template_file} confirm`",
                inline=False
            )
            embed.set_footer(text="⚠️ This action cannot be undone easily")
            await ctx.send(embed=embed)
            return

        try:
            async with ctx.typing():
                status_msg = await ctx.send("🔄 Starting template application...")

                # Get the currently active template from tracking file
                current_template = self._get_active_template('roles')

                # Step 1: Backup current template if exists
                if current_template:
                    await status_msg.edit(content=f"💾 Backing up current template: {current_template}...")
                    current_path = self.config_dir / current_template
                    backup_path = self._create_backup(current_path)
                    await asyncio.sleep(1)

                    # Step 2: Remove old roles
                    await status_msg.edit(content=f"🗑️ Removing roles from: {current_template}...")
                    remove_stats = await self._remove_managed_roles(ctx, current_template)

                    # Show deletion stats if any
                    if remove_stats['deleted'] > 0 or remove_stats['errors']:
                        status_parts = []
                        if remove_stats['deleted'] > 0:
                            status_parts.append(f"Deleted {remove_stats['deleted']} roles")
                        if remove_stats['errors']:
                            status_parts.append(f"{len(remove_stats['errors'])} errors")
                        await status_msg.edit(content=f"🗑️ Cleanup: {', '.join(status_parts)}")

                    await asyncio.sleep(1)
                else:
                    await status_msg.edit(content="ℹ️ No previous template to remove...")
                    await asyncio.sleep(1)

                # Step 3: Apply new template using existing syncroles command
                await status_msg.edit(content=f"✨ Applying new template: {template_file}...")

                # Call the existing syncroles command
                syncroles_cog = self.bot.get_cog("AdminCommands")
                if syncroles_cog:
                    await syncroles_cog.syncroles(ctx, template_file)

                    # Update active template tracking
                    self._set_active_template('roles', template_file)

                    await status_msg.delete()
                else:
                    await status_msg.edit(content="❌ Could not find AdminCommands cog to sync roles")

        except Exception as e:
            await ctx.send(f"❌ Error applying roles template: {str(e)}")

    @commands.command(name="applychannels", help="[Admin] Apply a channels template (removes old, applies new)")
    @commands.has_permissions(administrator=True)
    async def apply_channels_template(self, ctx: commands.Context, template_file: str, confirm: str = None):
        """
        Apply a channels template to the server. This will:
        1. Backup current active template
        2. Remove all channels from current template
        3. Apply new template

        Usage: !applychannels <template_file> confirm
        Example: !applychannels channels_generated_20250110_143022.yaml confirm
        """
        # Safety check for protected files
        if template_file in self.protected_files:
            await ctx.send(f"❌ Cannot apply protected file `{template_file}`. The default templates are read-only.")
            return

        template_path = self.config_dir / template_file
        if not template_path.exists():
            await ctx.send(f"❌ Template file `{template_file}` not found in config directory!")
            return

        # Require confirmation
        if confirm != "confirm":
            embed = discord.Embed(
                title="⚠️ Confirmation Required",
                description="This action will **delete existing channels** from the current template and apply the new template.",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="What will happen:",
                value="1️⃣ Current template is backed up\n"
                      "2️⃣ All channels from current template are **deleted**\n"
                      "3️⃣ New channels from template are created\n"
                      "4️⃣ Channel mappings are updated",
                inline=False
            )
            embed.add_field(
                name="To proceed, run:",
                value=f"`!applychannels {template_file} confirm`",
                inline=False
            )
            embed.set_footer(text="⚠️ This action cannot be undone easily")
            await ctx.send(embed=embed)
            return

        try:
            async with ctx.typing():
                status_msg = await ctx.send("🔄 Starting template application...")

                # Get the currently active template from tracking file
                current_template = self._get_active_template('channels')

                # Step 1: Backup current template if exists
                if current_template:
                    await status_msg.edit(content=f"💾 Backing up current template: {current_template}...")
                    current_path = self.config_dir / current_template
                    backup_path = self._create_backup(current_path)
                    await asyncio.sleep(1)

                    # Step 2: Remove old channels
                    await status_msg.edit(content=f"🗑️ Removing channels from: {current_template}...")
                    remove_stats = await self._remove_managed_channels(ctx, current_template)

                    # Show deletion stats if any
                    if remove_stats['deleted'] > 0 or remove_stats['categories_deleted'] > 0 or remove_stats['errors']:
                        status_parts = []
                        if remove_stats['deleted'] > 0:
                            status_parts.append(f"Deleted {remove_stats['deleted']} channels")
                        if remove_stats['categories_deleted'] > 0:
                            status_parts.append(f"{remove_stats['categories_deleted']} categories")
                        if remove_stats['errors']:
                            status_parts.append(f"{len(remove_stats['errors'])} errors")
                        await status_msg.edit(content=f"🗑️ Cleanup: {', '.join(status_parts)}")

                    await asyncio.sleep(1)
                else:
                    await status_msg.edit(content="ℹ️ No previous template to remove...")
                    await asyncio.sleep(1)

                # Step 3: Apply new template using existing syncchannels command
                await status_msg.edit(content=f"✨ Applying new template: {template_file}...")

                # Call the existing syncchannels command
                syncchannels_cog = self.bot.get_cog("AdminCommands")
                if syncchannels_cog:
                    await syncchannels_cog.syncchannels(ctx, template_file)

                    # Update active template tracking
                    self._set_active_template('channels', template_file)

                    await status_msg.delete()
                else:
                    await status_msg.edit(content="❌ Could not find AdminCommands cog to sync channels")

        except Exception as e:
            await ctx.send(f"❌ Error applying channels template: {str(e)}")

    @commands.command(name="listbackups", help="[Admin] List available backups")
    @commands.has_permissions(administrator=True)
    async def list_backups(self, ctx: commands.Context, template_type: str = None):
        """
        List available template backups.

        Usage: !listbackups [roles|channels]
        Example: !listbackups roles
        """
        if template_type and template_type not in ['roles', 'channels']:
            await ctx.send("❌ Invalid type. Use `roles` or `channels`, or leave empty for both.")
            return

        embed = discord.Embed(
            title="📦 Template Backups",
            description="Available backups (showing last 10 per type)",
            color=discord.Color.blue()
        )

        types_to_check = [template_type] if template_type else ['roles', 'channels']

        for ttype in types_to_check:
            backups = self._list_backups(ttype)

            if backups:
                backup_list = []
                for i, (timestamp, path) in enumerate(backups, 1):
                    backup_list.append(f"{i}. `{path.name}` - {timestamp}")

                embed.add_field(
                    name=f"{'🎭' if ttype == 'roles' else '🌌'} {ttype.title()} Backups",
                    value="\n".join(backup_list),
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{'🎭' if ttype == 'roles' else '🌌'} {ttype.title()} Backups",
                    value="No backups found",
                    inline=False
                )

        embed.set_footer(text="Use !reverttemplate to restore a backup")
        await ctx.send(embed=embed)

    @commands.command(name="reverttemplate", help="[Admin] Revert to a previous template backup")
    @commands.has_permissions(administrator=True)
    async def revert_template(self, ctx: commands.Context, backup_file: str, confirm: str = None):
        """
        Revert to a previous template backup.

        Usage: !reverttemplate <backup_file> confirm
        Example: !reverttemplate roles_20250110_143022.yaml confirm
        """
        backup_path = self.backup_dir / backup_file

        if not backup_path.exists():
            await ctx.send(f"❌ Backup file `{backup_file}` not found!")
            return

        # Determine if it's a roles or channels backup
        if backup_file.startswith('roles_'):
            template_type = 'roles'
        elif backup_file.startswith('channels_'):
            template_type = 'channels'
        else:
            await ctx.send("❌ Could not determine template type from filename")
            return

        # Require confirmation
        if confirm != "confirm":
            embed = discord.Embed(
                title="⚠️ Confirmation Required",
                description=f"This will restore the backup and apply it to your server.",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="Backup to restore:",
                value=f"`{backup_file}`",
                inline=False
            )
            embed.add_field(
                name="What will happen:",
                value=f"1️⃣ Backup is copied to active template\n"
                      f"2️⃣ Current {template_type} are removed\n"
                      f"3️⃣ Backup {template_type} are applied",
                inline=False
            )
            embed.add_field(
                name="To proceed, run:",
                value=f"`!reverttemplate {backup_file} confirm`",
                inline=False
            )
            await ctx.send(embed=embed)
            return

        try:
            # Create a new template file from backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_template_name = f"{template_type}_restored_{timestamp}.yaml"
            new_template_path = self.config_dir / new_template_name

            # Copy backup to new template
            shutil.copy2(backup_path, new_template_path)

            # Apply the template
            if template_type == 'roles':
                await self.apply_roles_template(ctx, new_template_name, 'confirm')
            else:
                await self.apply_channels_template(ctx, new_template_name, 'confirm')

        except Exception as e:
            await ctx.send(f"❌ Error reverting template: {str(e)}")

    @commands.command(name="listtemplates", help="[Admin] List all available templates")
    @commands.has_permissions(administrator=True)
    async def list_templates(self, ctx: commands.Context):
        """
        List all available templates in the config directory.

        Usage: !listtemplates
        """
        embed = discord.Embed(
            title="📝 Available Templates",
            color=discord.Color.blue()
        )

        # List role templates
        role_templates = [f for f in self.config_dir.glob("roles*.yaml")]
        if role_templates:
            template_list = []
            for template in sorted(role_templates, key=lambda p: p.stat().st_mtime, reverse=True)[:15]:
                size_kb = template.stat().st_size / 1024
                is_protected = "🔒" if template.name in self.protected_files else ""
                template_list.append(f"{is_protected}`{template.name}` ({size_kb:.1f} KB)")

            embed.add_field(
                name="🎭 Role Templates",
                value="\n".join(template_list),
                inline=False
            )

        # List channel templates
        channel_templates = [f for f in self.config_dir.glob("channels*.yaml")]
        if channel_templates:
            template_list = []
            for template in sorted(channel_templates, key=lambda p: p.stat().st_mtime, reverse=True)[:15]:
                size_kb = template.stat().st_size / 1024
                is_protected = "🔒" if template.name in self.protected_files else ""
                template_list.append(f"{is_protected}`{template.name}` ({size_kb:.1f} KB)")

            embed.add_field(
                name="🌌 Channel Templates",
                value="\n".join(template_list),
                inline=False
            )

        embed.set_footer(text="🔒 = Protected (default) template | Use !applyroles or !applychannels to apply")
        await ctx.send(embed=embed)

    @commands.command(name="activetemplate", help="[Admin] Check or set the currently active template")
    @commands.has_permissions(administrator=True)
    async def active_template(self, ctx: commands.Context, template_type: str = None, template_file: str = None):
        """
        Check or set the currently active template for roles or channels.

        Usage:
        - !activetemplate - Check both active templates
        - !activetemplate roles - Check active roles template
        - !activetemplate channels <template.yaml> - Set active channels template

        Example: !activetemplate channels channels_generated_20250110_143022.yaml
        """
        if not template_type:
            # Show both active templates
            roles_template = self._get_active_template('roles')
            channels_template = self._get_active_template('channels')

            embed = discord.Embed(
                title="📌 Active Templates",
                description="Currently tracked active templates",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="🎭 Roles Template",
                value=f"`{roles_template}`" if roles_template else "None set",
                inline=False
            )

            embed.add_field(
                name="🌌 Channels Template",
                value=f"`{channels_template}`" if channels_template else "None set",
                inline=False
            )

            embed.set_footer(text="These templates will be removed when applying a new template")
            await ctx.send(embed=embed)
            return

        if template_type not in ['roles', 'channels']:
            await ctx.send("❌ Invalid type. Use `roles` or `channels`.")
            return

        if not template_file:
            # Just show the active template for this type
            active = self._get_active_template(template_type)
            if active:
                await ctx.send(f"✅ Active {template_type} template: `{active}`")
            else:
                await ctx.send(f"ℹ️ No active {template_type} template is set.")
            return

        # Set the active template
        template_path = self.config_dir / template_file
        if not template_path.exists():
            await ctx.send(f"❌ Template file `{template_file}` not found in config directory!")
            return

        self._set_active_template(template_type, template_file)
        await ctx.send(f"✅ Set active {template_type} template to: `{template_file}`")


async def setup(bot: commands.Bot):
    await bot.add_cog(TemplateManager(bot))

