# AI Template Manager - Quick Reference

## 🚀 Quick Commands

### Generate Templates
```bash
!genroles <description>         # Generate roles template
!genchannels <description>      # Generate channels template
```

### Apply Templates
```bash
!applyroles <file> confirm      # Apply roles (DESTRUCTIVE)
!applychannels <file> confirm   # Apply channels (DESTRUCTIVE)
```

### Manage Templates
```bash
!listtemplates                  # List all templates
!listbackups [roles|channels]   # List backups
!reverttemplate <file> confirm  # Restore backup
```

## ⚡ Common Workflows

### Change Server Theme
```bash
!genchannels Create fantasy-themed channels with Castle Gates, Grand Hall, Training Grounds, and Mystic Library
!applychannels channels_generated_TIMESTAMP.yaml confirm
```

### Add New Role Categories
```bash
!genroles Add hobby roles for photography, cooking, gardening, and traveling enthusiasts
!applyroles roles_generated_TIMESTAMP.yaml confirm
```

### Revert Changes
```bash
!listbackups roles
!reverttemplate roles_TIMESTAMP.yaml confirm
```

## 🛡️ Safety Reminders

- ✅ Default `roles.yaml` and `channels.yaml` are **PROTECTED**
- ✅ Automatic backups created on every apply
- ✅ `confirm` parameter required for destructive actions
- ⚠️ Applied changes are immediate and visible to all users

## 📝 Template Generation Tips

**Good Description Examples:**

✅ "Create roles for a fitness community with workout types (cardio, strength, yoga), experience levels (beginner, intermediate, advanced), and fitness goals (weight loss, muscle gain, flexibility)"

✅ "Create channels for a study group with categories for different subjects (Math, Science, Literature), resource sharing, study sessions, and Q&A"

❌ "Create some roles"  
❌ "Make channels"

**The more specific, the better the result!**

## 🔗 Related Commands

- `!syncroles [file]` - Sync roles without removing old ones
- `!syncchannels [file]` - Sync channels without removing old ones
- `!help template` - Get detailed help

## 📍 File Locations

- Templates: `src/config/roles_*.yaml` or `channels_*.yaml`
- Backups: `src/config/backups/`
- Protected: `src/config/roles.yaml`, `src/config/channels.yaml` (🔒 READ-ONLY)

---

For detailed documentation, see `AI_TEMPLATE_MANAGER_GUIDE.md`

