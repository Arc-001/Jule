#!/usr/bin/env python3
"""
Test script for intro channel configuration feature
Tests database operations and configuration management
"""

import sys
from pathlib import Path
import tempfile
import os

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from model.model import Database

def test_intro_channel_configuration():
    """Test intro channel configuration in database"""
    print("=" * 60)
    print("Testing Intro Channel Configuration")
    print("=" * 60)
    print()

    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        test_db_path = tmp.name

    try:
        # Initialize database
        print("1. Initializing test database...")
        db = Database(test_db_path)
        print("   ✅ Database initialized")
        print()

        # Test guild IDs (using smaller numbers to avoid SQLite INTEGER overflow)
        test_guild_id = 123456789012345
        test_channel_id = 987654321098765

        # Test 1: Get settings for new guild (should have defaults)
        print("2. Testing default settings for new guild...")
        settings = db.get_server_settings(test_guild_id)
        assert settings['intro_channel_id'] is None, "Default intro_channel_id should be None"
        print("   ✅ Default settings correct")
        print(f"      intro_channel_id: {settings['intro_channel_id']}")
        print()

        # Test 2: Set intro channel
        print("3. Setting intro channel...")
        db.update_server_settings(
            guild_id=test_guild_id,
            intro_channel_id=test_channel_id
        )
        print("   ✅ Intro channel set")
        print()

        # Test 3: Retrieve and verify
        print("4. Retrieving and verifying intro channel...")
        settings = db.get_server_settings(test_guild_id)
        assert settings['intro_channel_id'] == test_channel_id, "Intro channel ID mismatch"
        print("   ✅ Intro channel retrieved correctly")
        print(f"      intro_channel_id: {settings['intro_channel_id']}")
        print()

        # Test 4: Update intro channel
        print("5. Updating intro channel to new value...")
        new_channel_id = 111111111111111
        db.update_server_settings(
            guild_id=test_guild_id,
            intro_channel_id=new_channel_id
        )
        settings = db.get_server_settings(test_guild_id)
        assert settings['intro_channel_id'] == new_channel_id, "Updated intro channel ID mismatch"
        print("   ✅ Intro channel updated successfully")
        print(f"      intro_channel_id: {settings['intro_channel_id']}")
        print()

        # Test 5: Clear intro channel (set to None)
        print("6. Clearing intro channel...")
        db.update_server_settings(
            guild_id=test_guild_id,
            intro_channel_id=None
        )
        settings = db.get_server_settings(test_guild_id)
        assert settings['intro_channel_id'] is None, "Intro channel should be None after clearing"
        print("   ✅ Intro channel cleared successfully")
        print(f"      intro_channel_id: {settings['intro_channel_id']}")
        print()

        # Test 6: Multiple guilds
        print("7. Testing multiple guilds...")
        guild1_id = 1111111111111111111
        guild2_id = 2222222222222222222
        channel1_id = 3333333333333333333
        channel2_id = 4444444444444444444

        db.update_server_settings(guild_id=guild1_id, intro_channel_id=channel1_id)
        db.update_server_settings(guild_id=guild2_id, intro_channel_id=channel2_id)

        settings1 = db.get_server_settings(guild1_id)
        settings2 = db.get_server_settings(guild2_id)

        assert settings1['intro_channel_id'] == channel1_id, "Guild 1 intro channel mismatch"
        assert settings2['intro_channel_id'] == channel2_id, "Guild 2 intro channel mismatch"
        print("   ✅ Multiple guilds have independent settings")
        print(f"      Guild 1 intro_channel_id: {settings1['intro_channel_id']}")
        print(f"      Guild 2 intro_channel_id: {settings2['intro_channel_id']}")
        print()

        # Test 7: Persistence
        print("8. Testing persistence (close and reopen database)...")
        del db
        db = Database(test_db_path)
        settings1 = db.get_server_settings(guild1_id)
        assert settings1['intro_channel_id'] == channel1_id, "Settings not persisted"
        print("   ✅ Settings persisted across database sessions")
        print()

        print("=" * 60)
        print("✨ All tests passed!")
        print("=" * 60)
        print()
        print("Summary:")
        print("✅ Default settings work correctly")
        print("✅ Can set intro channel")
        print("✅ Can update intro channel")
        print("✅ Can clear intro channel")
        print("✅ Multiple guilds have independent settings")
        print("✅ Settings persist across sessions")
        print()

        return True

    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test database
        try:
            os.unlink(test_db_path)
            print("🧹 Cleaned up test database")
        except:
            pass


def test_backward_compatibility():
    """Test that existing code still works without intro channel set"""
    print()
    print("=" * 60)
    print("Testing Backward Compatibility")
    print("=" * 60)
    print()

    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        test_db_path = tmp.name

    try:
        db = Database(test_db_path)
        test_guild_id = 999999999999999

        # Get settings without ever setting intro channel
        settings = db.get_server_settings(test_guild_id)

        # Simulate bot behavior
        intro_channel_id = settings.get('intro_channel_id')

        print("1. Testing default behavior (no intro channel set)...")
        if intro_channel_id is None:
            print("   ✅ intro_channel_id is None (expected)")
            print("   ✅ Auto role assignment would be disabled")
        else:
            print(f"   ❌ Unexpected intro_channel_id: {intro_channel_id}")
            return False

        print()
        print("2. Testing conditional check (as in bot.py)...")
        # Simulate the check in bot.py
        message_channel_id = 1234567890  # Simulated message channel

        if intro_channel_id and message_channel_id == intro_channel_id:
            print("   ❌ Should not reach here with None intro_channel_id")
            return False
        else:
            print("   ✅ Correctly skips role assignment when not configured")

        print()
        print("=" * 60)
        print("✨ Backward compatibility tests passed!")
        print("=" * 60)
        print()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            os.unlink(test_db_path)
        except:
            pass


def main():
    """Run all tests"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Intro Channel Configuration Tests" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    success = True

    # Run tests
    if not test_intro_channel_configuration():
        success = False

    if not test_backward_compatibility():
        success = False

    print()
    if success:
        print("🎉 All tests passed successfully!")
        print()
        print("The intro channel configuration feature is working correctly:")
        print("• Database operations work as expected")
        print("• Settings persist across sessions")
        print("• Multiple guilds can have different settings")
        print("• Backward compatible with existing code")
        print()
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

