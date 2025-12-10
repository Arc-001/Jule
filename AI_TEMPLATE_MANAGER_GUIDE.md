# AI Template Manager Guide

## Overview

The AI Template Manager is a powerful system that allows you to generate, manage, and apply Discord server templates for roles and channels using AI. This system provides:

- **AI-Powered Generation**: Describe what you want, and AI creates the template
- **Safe Management**: Protected default templates, automatic backups
- **Easy Application**: Remove old structures and apply new ones with a single command
- **Rollback Support**: Revert to previous templates anytime

## 🚀 Quick Start

### Generate a New Template

#### For Roles:
```
!genroles Create roles for a gaming community with competitive ranks, casual players, and game preferences like FPS, RPG, and Strategy
```

#### For Channels:
```
!genchannels Create channels for an art community with separate spaces for digital art, traditional art, photography, and critique
```

The AI will generate a YAML template and save it in the config directory.

### Apply a Template

Once you have a template, apply it:

```
!applyroles roles_generated_20250110_143022.yaml confirm
!applychannels channels_generated_20250110_143022.yaml confirm
```

**Important**: The `confirm` parameter is required to prevent accidental changes.

## 📋 Command Reference

### Generation Commands

#### `!genroles <description>`
Generate a new roles template using AI.

**Example:**
```
!genroles Create roles for a book club with genres like fantasy, sci-fi, mystery, romance, and reading frequency preferences
```

**Output:** Creates a file like `roles_generated_20250110_143022.yaml`

#### `!genchannels <description>`
Generate a new channels template using AI.

**Example:**
```
!genchannels Create channels for a coding community with separate channels for different programming languages, help requests, and project showcases
```

**Output:** Creates a file like `channels_generated_20250110_143022.yaml`

### Application Commands

#### `!applyroles <template_file> confirm`
Apply a roles template to your server.

**What it does:**
1. Backs up the current active template
2. Removes all roles from the current template
3. Creates all roles from the new template
4. Updates role mappings

**Example:**
```
!applyroles roles_generated_20250110_143022.yaml confirm
```

**⚠️ Warning:** This will DELETE existing roles from the current template.

#### `!applychannels <template_file> confirm`
Apply a channels template to your server.

**What it does:**
1. Backs up the current active template
2. Removes all channels from the current template
3. Creates all channels from the new template
4. Updates channel mappings

**Example:**
```
!applychannels channels_generated_20250110_143022.yaml confirm
```

**⚠️ Warning:** This will DELETE existing channels from the current template.

### Management Commands

#### `!listtemplates`
List all available templates in the config directory.

Shows:
- Role templates (roles*.yaml)
- Channel templates (channels*.yaml)
- Protected templates (marked with 🔒)

#### `!listbackups [type]`
List available template backups.

**Examples:**
```
!listbackups           # Show all backups
!listbackups roles     # Show only role backups
!listbackups channels  # Show only channel backups
```

Shows the last 10 backups for each type with timestamps.

#### `!reverttemplate <backup_file> confirm`
Restore a previous template from backup.

**Example:**
```
!reverttemplate roles_20250110_143022.yaml confirm
```

This will:
1. Copy the backup to a new template file
2. Remove current roles/channels
3. Apply the backup template

## 🛡️ Safety Features

### Protected Files
The default templates `roles.yaml` and `channels.yaml` are **PROTECTED** and cannot be:
- Overwritten
- Applied directly
- Modified by the template manager

This ensures you always have your original templates safe.

### Automatic Backups
Every time you apply a template, the system:
1. Creates a timestamped backup in `config/backups/`
2. Stores backups with format: `roles_YYYYMMDD_HHMMSS.yaml`
3. Keeps backups indefinitely (you can manually delete old ones)

### Confirmation Required
All destructive operations require explicit confirmation:
- `!applyroles <file> confirm`
- `!applychannels <file> confirm`
- `!reverttemplate <file> confirm`

Without `confirm`, you'll see a warning message.

## 📁 File Structure

```
src/config/
├── roles.yaml                          # 🔒 Protected default template
├── channels.yaml                       # 🔒 Protected default template
├── roles_generated_20250110_143022.yaml   # Generated template
├── channels_generated_20250110_143022.yaml # Generated template
├── roles.json                          # Role name → ID mappings
├── current_channels.json               # Channel name → ID mappings
└── backups/
    ├── roles_20250110_120000.yaml      # Backup
    ├── roles_20250110_140000.yaml      # Backup
    ├── channels_20250110_120000.yaml   # Backup
    └── channels_20250110_140000.yaml   # Backup
```

## 🎯 Use Cases

### Scenario 1: New Server Theme
You want to transform your server from a generic community to a space-themed community:

```
!genchannels Create a space-themed server with Mission Control for announcements, Galaxy Hub for general chat, Space Station for topics, and Asteroid Belt for voice channels

!applychannels channels_generated_20250110_143022.yaml confirm
```

### Scenario 2: Seasonal Event
Create temporary roles for a holiday event:

```
!genroles Create festive roles for a winter holiday event including Secret Santa participant, Gingerbread Baker, Snowball Fighter, and Caroler

!applyroles roles_generated_20250110_150000.yaml confirm
```

When the event is over, revert to the previous template:

```
!listbackups roles
!reverttemplate roles_20250110_120000.yaml confirm
```

### Scenario 3: Community Rebranding
Your gaming community is expanding into art:

```
!genroles Create hybrid roles for both gaming and art including Game Developer, 3D Artist, Concept Artist, Indie Game Creator, Pixel Artist, and Game Music Composer

!applyroles roles_generated_20250110_160000.yaml confirm
```

## 🔧 Template Format

### Roles Template (YAML)
```yaml
role_categories:
  "category_name":
    description: "Category description"
    roles:
      - name: "role name"
        color: "#HEXCOLOR"
        mentionable: true/false
```

### Channels Template (YAML)
```yaml
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
```

## 💡 Tips & Best Practices

1. **Be Specific**: The more detailed your description, the better the AI-generated template
   - Good: "Create roles for a music production community with genres like EDM, Hip-Hop, Rock, skill levels from beginner to professional, and DAW preferences"
   - Less Good: "Create music roles"

2. **Review Before Applying**: Always check the generated template file before applying it
   - Templates are saved in `src/config/`
   - Open them to see what will be created

3. **Backup Strategy**: Keep backups organized
   - Use `!listbackups` regularly
   - Note which backups correspond to important server states

4. **Test First**: If possible, test templates on a test server before applying to production

5. **Gradual Changes**: Consider applying roles and channels separately to minimize disruption

6. **Communication**: Warn your community before major template changes

## 🚨 Troubleshooting

### AI Service Not Available
**Error:** "AI service is not available. Please configure GEMINI_API_KEY."

**Solution:** Ensure `GEMINI_API_KEY` is set in your `.env` file.

### Permission Errors
**Error:** "Missing permissions to create/delete role/channel"

**Solution:** Ensure the bot has:
- Administrator permission, OR
- Manage Roles and Manage Channels permissions
- Bot's role is above roles it needs to manage

### Template Not Found
**Error:** "Template file `X` not found in config directory!"

**Solution:** Use `!listtemplates` to see available templates and use the exact filename.

### Rate Limiting
If you see delays during application, this is normal. The system includes rate limiting to avoid Discord API limits.

## ⚠️ Important Notes

1. **Default Templates are Safe**: `roles.yaml` and `channels.yaml` can NEVER be overwritten
2. **Backups are Automatic**: Created every time you apply a template
3. **Confirmation Required**: All destructive actions need explicit `confirm` parameter
4. **No Undo Button**: Once applied, changes are live (but you can revert to backups)
5. **Existing Members**: Applying new roles won't affect existing member role assignments
6. **Existing Channels**: Only channels from the previous template are removed

## 📞 Support

If you encounter issues:
1. Check the bot console for error messages
2. Use `!listbackups` to see available restore points
3. Review this guide for command syntax
4. Check bot permissions

## 🔄 Workflow Example

Complete workflow for changing your server theme:

```bash
# 1. Generate new template
!genroles Create cyberpunk-themed roles with Netrunner, Corpo, Street Kid, and Tech Specialist

# 2. Review the generated file (check config folder)
# File created: roles_generated_20250110_143022.yaml

# 3. List current templates to confirm
!listtemplates

# 4. Apply the new template (creates automatic backup)
!applyroles roles_generated_20250110_143022.yaml confirm

# 5. If something goes wrong, check backups
!listbackups roles

# 6. Revert if needed
!reverttemplate roles_20250110_120000.yaml confirm
```

---

**Version:** 1.0  
**Last Updated:** January 10, 2025  
**Compatible With:** Jule Bot v2.0+

