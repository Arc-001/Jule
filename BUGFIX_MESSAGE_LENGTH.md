# Bug Fix: Discord Message Length Error

## Issue
When using `!genchannels` or `!genroles`, the bot would crash with:
```
HTTPException: 400 Bad Request (error code: 50035): Invalid Form Body
In content: Must be 2000 or fewer in length.
```

This occurred because the embed preview could contain very long category names or too much content, exceeding Discord's 2000 character limit for message content.

## Root Cause
The embed was including full category names in the preview without truncation, and some AI-generated templates had very long category names or descriptions that made the total embed content exceed Discord's limits.

## Fix Applied

### 1. Category Name Truncation
- Category names are now truncated to 50 characters maximum
- Long names get "..." appended: `"Very Long Category Name That Goes On..."` 

### 2. Preview Text Limiting
- The entire preview text is limited to 500 characters
- If it exceeds this, it's truncated with "..." 

### 3. Better Error Handling
- Added specific `discord.HTTPException` catching
- If the template file was saved but the message failed, the user gets a simplified success message
- The user is informed to use `!listtemplates` to see the template

## Changes Made

**File**: `src/cogs/template_manager.py`

### For `!genchannels`:
```python
# Truncate category name if too long
display_name = cat_name[:50] + "..." if len(cat_name) > 50 else cat_name
preview.append(f"**{display_name}**: {channel_count} channels")

# Ensure preview doesn't exceed reasonable length
preview_text = "\n".join(preview)
if len(preview_text) > 500:
    preview_text = preview_text[:500] + "..."
```

### For `!genroles`:
Same truncation logic applied.

### Error Handling:
```python
except discord.HTTPException as e:
    if template_name:
        await ctx.send(f"✅ Template saved as `{template_name}` but preview was too long.\n"
                      f"Use `!listtemplates` to see it and `!applychannels {template_name}` to apply it.")
```

## Testing
The fix ensures:
- ✅ Template is always saved successfully
- ✅ User gets feedback even if preview is too long
- ✅ No data loss occurs
- ✅ Commands work with any length of AI-generated content

## Usage Example

**Before fix:**
```
!genchannels Make a space themed minimalist server channel template
🤖 AI is generating your channels template...
❌ An error occurred: HTTPException: 400 Bad Request...
```

**After fix:**
```
!genchannels Make a space themed minimalist server channel template
🤖 AI is generating your channels template...
✅ Template saved as `channels_generated_20251210_235200.yaml` but preview was too long.
Use `!listtemplates` to see it and `!applychannels channels_generated_20251210_235200.yaml` to apply it.
```

Or if the preview fits:
```
✅ Channels Template Generated
Created channels_generated_20251210_235200.yaml with 15 channels across 5 categories

📋 Categories Preview
**🚀 Mission Control**: 3 channels
**🌌 Social Hub**: 4 channels
**🛸 Activity Zones**: 5 channels
... and 2 more categories

📝 Next Steps
Review the template and apply it using:
!applychannels channels_generated_20251210_235200.yaml
```

## Related Files
- `src/cogs/template_manager.py` - Fixed both generation commands

## Status
✅ **Fixed and tested**

---

*Bug fix applied: December 10, 2025*

