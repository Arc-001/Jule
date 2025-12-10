#!/usr/bin/env python3
"""
Test script to verify AI Template Manager implementation
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all necessary modules can be imported"""
    print("Testing imports...")
    
    try:
        import discord
        print("✅ discord.py imported")
    except ImportError as e:
        print(f"❌ Failed to import discord: {e}")
        return False
    
    try:
        import yaml
        print("✅ yaml imported")
    except ImportError as e:
        print(f"❌ Failed to import yaml: {e}")
        return False
    
    try:
        from cogs.template_manager import TemplateManager
        print("✅ TemplateManager imported")
    except ImportError as e:
        print(f"❌ Failed to import TemplateManager: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that required files and directories exist"""
    print("\nTesting file structure...")
    
    required_files = [
        "src/cogs/template_manager.py",
        "src/config/roles.yaml",
        "src/config/channels.yaml",
        "AI_TEMPLATE_MANAGER_GUIDE.md",
        "AI_TEMPLATE_MANAGER_QUICK_REF.md",
        "AI_TEMPLATE_MANAGER_IMPLEMENTATION.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} not found")
            all_exist = False
    
    return all_exist

def test_protected_files():
    """Test that protected files are identified correctly"""
    print("\nTesting protected files...")
    
    try:
        from cogs.template_manager import TemplateManager
        from unittest.mock import MagicMock
        
        # Create mock bot
        bot = MagicMock()
        tm = TemplateManager(bot)
        
        # Check protected files list
        expected_protected = ['roles.yaml', 'channels.yaml']
        if tm.protected_files == expected_protected:
            print(f"✅ Protected files: {tm.protected_files}")
            return True
        else:
            print(f"❌ Protected files mismatch: {tm.protected_files}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing protected files: {e}")
        return False

def test_backup_directory():
    """Test that backup directory is created"""
    print("\nTesting backup directory...")
    
    try:
        from cogs.template_manager import TemplateManager
        from unittest.mock import MagicMock
        
        bot = MagicMock()
        tm = TemplateManager(bot)
        
        if tm.backup_dir.exists():
            print(f"✅ Backup directory exists: {tm.backup_dir}")
            return True
        else:
            print(f"❌ Backup directory not found: {tm.backup_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing backup directory: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Template Manager - Implementation Tests")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Protected Files", test_protected_files),
        ("Backup Directory", test_backup_directory),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Implementation is ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

