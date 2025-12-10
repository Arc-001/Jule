# Roles System Migration Guide

## Overview

The roles system has been revamped to follow the same pattern as the channels system:
- **roles.yaml** = Template (defines role structure and properties)
- **roles.json** = Mapping (auto-generated name-to-ID mappings)

## What Changed?

### Before (Old System) ❌

```
roles.json  →  Both template AND mapping
   ↓
!syncroles  →  Creates roles, updates IDs in same file
```

**Problems:**
- Couldn't define role colors or mentionable status
- Mixed template data with instance data
- Manual ID management

### After (New System) ✅

```
roles.yaml  →  Template (defines structure)
   ↓
!syncroles  →  Syncs to Discord
   ↓
roles.json  →  Auto-generated ID mappings
```

**Benefits:**
- Define role colors and mentionable status
- Clear separation: template vs instance
- Consistent with channels system
- YAML comments and organization

## Migration Steps

### Step 1: Backup Current Config
```bash
cd /home/arc/repo/Jule/src/config
cp roles.json roles.json.backup
```

### Step 2: Verify New Files Exist
- ✅ `roles.yaml` - Already created with all existing roles
- ✅ `roles.json` - Keep existing file (will be regenerated)

### Step 3: Run Sync Command
```
!syncroles
```

This will:
1. Read `roles.yaml` template
2. Match existing roles by name
3. Update role properties (colors, mentionable)
4. Create any missing roles
5. Regenerate `roles.json` with mappings

### Step 4: Verify
- Check Discord to see roles have correct colors
- Test role assignment in intro channel
- Run `!reloadroles` to refresh cache

## New Command Usage

### !syncroles [filename]
```
!syncroles                 # Uses roles.yaml (default)
!syncroles roles.yaml      # Explicit
!syncroles custom.yaml     # Custom template
```

**What it does:**
- Reads YAML template
- Creates/updates roles on Discord
- Exports name-to-ID mappings to roles.json
- Reloads mappings in memory

### !reloadroles
```
!reloadroles              # Reload mappings from JSON
```

**What it does:**
- Reloads roles.json into memory
- Does NOT sync with Discord
- Use after manual JSON edits

## File Structure

### roles.yaml (Template - You Edit This)
```yaml
role_categories:
  "professional":
    description: "Career roles"
    roles:
      - name: "developer"
        color: "#5865F2"
        mentionable: true
```

**Properties:**
- `name`: Role name (required)
- `color`: Hex color code (optional, default: #99AAB5)
- `mentionable`: Boolean (optional, default: true)

### roles.json (Mapping - Auto-Generated)
```json
{
  "developer": 1448329075805523978,
  "designer": 1448329077516795969
}
```

**DO NOT** manually edit unless you know what you're doing. Regenerate with `!syncroles`.

## Common Tasks

### Adding New Roles
1. Edit `roles.yaml`:
```yaml
- name: "new role"
  color: "#FF0000"
  mentionable: true
```
2. Run `!syncroles`

### Changing Role Colors
1. Edit color in `roles.yaml`:
```yaml
- name: "developer"
  color: "#00FF00"  # Changed
```
2. Run `!syncroles`

### Removing Roles
1. Remove from `roles.yaml`
2. Manually delete from Discord server
3. Run `!syncroles` to regenerate JSON

## Troubleshooting

### "Role not found" errors
**Solution:** Run `!syncroles` then `!reloadroles`

### Colors not updating
**Solution:** Check hex format `"#RRGGBB"` and run `!syncroles`

### Role assignment not working
**Solution:**
1. Check role is in `roles.yaml`
2. Run `!syncroles`
3. Verify role in `roles.json`
4. Run `!reloadroles`

## Rollback (If Needed)

If you need to revert:

```bash
cd /home/arc/repo/Jule/src/config
cp roles.json.backup roles.json
```

Then restore the old `syncroles` command from git history.

## Comparison with Channels System

Both systems now follow the same pattern:

| Aspect | Channels | Roles |
|--------|----------|-------|
| Template | channels.yaml | roles.yaml |
| Mapping | channels.json | roles.json |
| Sync Command | !syncchannels | !syncroles |
| Reload Command | N/A | !reloadroles |

## Benefits Summary

✅ **Consistency**: Same pattern as channels  
✅ **Properties**: Define colors and mentionable status  
✅ **Organization**: Categories for grouping  
✅ **Comments**: YAML supports comments  
✅ **Version Control**: Template in git, not IDs  
✅ **Maintainability**: Easy to understand and modify

## Next Steps

1. Run `!syncroles` to sync your server
2. Verify roles look correct in Discord
3. Test intro channel role assignment
4. Update your documentation/workflows

## Support

See detailed documentation:
- `ROLES_SYSTEM_GUIDE.md` - Complete system documentation
- `ROLES_QUICK_REFERENCE.md` - Quick command reference

