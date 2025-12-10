# 🚀 Roles Quick Start

## TL;DR

The roles system now works like channels:
- Edit `roles.yaml` (template)
- Run `!syncroles`
- Done! (`roles.json` auto-generated)

## Commands

```bash
!syncroles          # Sync from roles.yaml
!syncroles custom.yaml  # Sync from custom file
!reloadroles        # Reload mappings
```

## Files

```
src/config/
├── roles.yaml       ← Edit this (template)
└── roles.json       ← Auto-generated (IDs)
```

## Quick Example

### 1. Edit roles.yaml
```yaml
role_categories:
  "professional":
    roles:
      - name: "developer"
        color: "#5865F2"
        mentionable: true
```

### 2. Sync
```
!syncroles
```

### 3. Result
- ✅ Role created on Discord
- ✅ Blue color applied
- ✅ Mentionable enabled
- ✅ ID saved to roles.json

## Common Tasks

| Task | Steps |
|------|-------|
| **Add role** | 1. Add to roles.yaml<br>2. Run !syncroles |
| **Change color** | 1. Edit color in roles.yaml<br>2. Run !syncroles |
| **Reload cache** | Run !reloadroles |

## Pattern

Same as channels:

```
channels.yaml → !syncchannels → channels.json
roles.yaml    → !syncroles    → roles.json
```

## Properties

```yaml
- name: "role name"        # Required
  color: "#RRGGBB"         # Optional (default: #99AAB5)
  mentionable: true/false  # Optional (default: true)
```

## Documentation

- 📖 `ROLES_SYSTEM_GUIDE.md` - Full guide
- 📋 `ROLES_QUICK_REFERENCE.md` - Reference
- 🔄 `ROLES_MIGRATION_GUIDE.md` - Migration
- ✅ `ROLES_REVAMP_COMPLETE.md` - Summary

## That's It!

You're ready to use the new roles system. Just edit `roles.yaml` and run `!syncroles`! 🎉

