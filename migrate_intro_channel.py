#!/usr/bin/env python3
"""
Migration script to move intro channel from hardcoded channels.json to database
This script helps migrate from the old hardcoded intro channel system to the new dynamic system.
"""

import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from model.model import Database

def migrate_intro_channel(guild_id: int, db_path: str = "data/jule.db", channels_json_path: str = "src/config/channels.json"):
    """
    Migrate intro channel from channels.json to database
    
    Args:
        guild_id: Discord guild ID to set the intro channel for
        db_path: Path to the database file
        channels_json_path: Path to the channels.json file
    """
    print("🔄 Starting intro channel migration...")
    print(f"Guild ID: {guild_id}")
    print(f"Database: {db_path}")
    print(f"Channels config: {channels_json_path}")
    print()
    
    # Load channels.json
    try:
        with open(channels_json_path, 'r') as f:
            channels = json.load(f)
        print(f"✅ Loaded channels.json")
    except FileNotFoundError:
        print(f"❌ Error: {channels_json_path} not found")
        return False
    except json.JSONDecodeError:
        print(f"❌ Error: {channels_json_path} is not valid JSON")
        return False
    
    # Get intro channel ID
    intro_channel_id = channels.get("intro")
    if not intro_channel_id:
        print("⚠️  No 'intro' channel found in channels.json")
        print("   You can set it manually using: !setintrochannel #channel")
        return True
    
    print(f"📍 Found intro channel ID: {intro_channel_id}")
    
    # Initialize database
    try:
        db = Database(db_path)
        print(f"✅ Connected to database")
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False
    
    # Update server settings
    try:
        db.update_server_settings(
            guild_id=guild_id,
            intro_channel_id=intro_channel_id
        )
        print(f"✅ Set intro channel in database for guild {guild_id}")
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        return False
    
    # Verify the setting
    try:
        settings = db.get_server_settings(guild_id)
        stored_id = settings.get('intro_channel_id')
        if stored_id == intro_channel_id:
            print(f"✅ Verified: intro_channel_id = {stored_id}")
        else:
            print(f"⚠️  Warning: Stored ID ({stored_id}) doesn't match expected ({intro_channel_id})")
    except Exception as e:
        print(f"⚠️  Warning: Could not verify setting: {e}")
    
    print()
    print("=" * 60)
    print("✨ Migration completed successfully!")
    print()
    print("Next steps:")
    print("1. The intro channel is now configured in the database")
    print("2. You can change it anytime using: !setintrochannel #channel")
    print("3. Check the setting using: !getintrochannel")
    print("4. Test role assignment using: !testrole <message>")
    print()
    print("The bot will now use the database setting instead of channels.json")
    print("=" * 60)
    
    return True


def main():
    """Main entry point"""
    print("=" * 60)
    print("Intro Channel Migration Script")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python migrate_intro_channel.py <guild_id>")
        print()
        print("Example:")
        print("  python migrate_intro_channel.py 1234567890123456789")
        print()
        print("To find your guild ID:")
        print("1. Enable Developer Mode in Discord settings")
        print("2. Right-click your server name")
        print("3. Click 'Copy ID'")
        print()
        return 1
    
    try:
        guild_id = int(sys.argv[1])
    except ValueError:
        print(f"❌ Error: '{sys.argv[1]}' is not a valid guild ID")
        print("Guild ID must be a number")
        return 1
    
    # Optional: custom paths
    db_path = sys.argv[2] if len(sys.argv) > 2 else "data/jule.db"
    channels_path = sys.argv[3] if len(sys.argv) > 3 else "src/config/channels.json"
    
    success = migrate_intro_channel(guild_id, db_path, channels_path)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

