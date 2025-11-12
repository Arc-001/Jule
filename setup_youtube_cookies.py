#!/usr/bin/env python3
"""
YouTube Cookie Setup Helper for Jule Bot

This script helps set up YouTube cookies to avoid bot detection.
Run this if you're getting "Sign in to confirm you're not a bot" errors.

Options:
1. Use browser cookies (recommended)
2. Manual cookie setup
"""

import os
import sys

def setup_browser_cookies():
    """Setup to use cookies from browser"""
    print("\n🍪 Browser Cookie Setup")
    print("=" * 50)
    print("\nThis will configure yt-dlp to use cookies from your browser.")
    print("Supported browsers: Firefox, Chrome, Chromium, Edge, Safari")
    
    print("\n📋 Steps:")
    print("1. Make sure you're logged into YouTube in your browser")
    print("2. Choose which browser to use:")
    
    browsers = {
        '1': 'firefox',
        '2': 'chrome',
        '3': 'chromium',
        '4': 'edge',
        '5': 'safari'
    }
    
    print("\n  1. Firefox")
    print("  2. Chrome")
    print("  3. Chromium")
    print("  4. Edge")
    print("  5. Safari")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice not in browsers:
        print("❌ Invalid choice!")
        return
    
    browser = browsers[choice]
    
    print(f"\n✅ Selected: {browser.title()}")
    print("\n📝 Configuration Instructions:")
    print("-" * 50)
    print("\nIn your music_commands.py file, update the YTDL_OPTIONS:")
    print(f"\n  'cookiesfrombrowser': ('{browser}',),")
    print("\nReplace this line:")
    print("  'cookiesfrombrowser': None,")
    print("\nWith:")
    print(f"  'cookiesfrombrowser': ('{browser}',),")
    
    print("\n⚠️  Important Notes:")
    print("• Make sure you're logged into YouTube in your browser")
    print("• The browser profile must be accessible to the bot")
    print("• If using Chrome, close all Chrome windows first")
    print(f"• Browser: {browser.title()}")
    
    # Try to automatically update the file
    update_choice = input("\n🔧 Would you like me to update music_commands.py automatically? (y/n): ").strip().lower()
    
    if update_choice == 'y':
        try:
            music_commands_path = os.path.join(os.path.dirname(__file__), 'src', 'cogs', 'music_commands.py')
            
            if not os.path.exists(music_commands_path):
                print(f"❌ Could not find music_commands.py at {music_commands_path}")
                return
            
            with open(music_commands_path, 'r') as f:
                content = f.read()
            
            # Replace the cookiesfrombrowser line
            old_line = "'cookiesfrombrowser': None,"
            new_line = f"'cookiesfrombrowser': ('{browser}',),"
            
            if old_line in content:
                content = content.replace(old_line, new_line)
                
                with open(music_commands_path, 'w') as f:
                    f.write(content)
                
                print(f"\n✅ Successfully updated music_commands.py!")
                print(f"   Set browser to: {browser}")
                print("\n🔄 Restart the bot for changes to take effect.")
            else:
                print(f"\n⚠️  Could not find the line to replace in music_commands.py")
                print("   Please update manually using the instructions above.")
        except Exception as e:
            print(f"\n❌ Error updating file: {e}")
            print("   Please update manually using the instructions above.")

def manual_cookie_setup():
    """Instructions for manual cookie export"""
    print("\n🍪 Manual Cookie Setup")
    print("=" * 50)
    print("\nFor manual cookie setup, you'll need to export cookies from your browser.")
    print("\n📋 Steps:")
    print("\n1. Install a browser extension to export cookies:")
    print("   • Firefox: 'cookies.txt' extension")
    print("   • Chrome: 'Get cookies.txt' extension")
    
    print("\n2. Log into YouTube in your browser")
    
    print("\n3. Use the extension to export YouTube cookies")
    print("   • Save as: youtube_cookies.txt")
    print("   • Location: /home/arc/repo/Jule/")
    
    print("\n4. Update music_commands.py:")
    print("   Change:")
    print("     'cookiesfrombrowser': None,")
    print("   To:")
    print("     'cookiefile': 'youtube_cookies.txt',")
    
    print("\n5. Restart the bot")
    
    print("\n⚠️  Security Note:")
    print("   • Keep your cookies file private")
    print("   • Don't commit it to version control")
    print("   • Add 'youtube_cookies.txt' to .gitignore")

def check_yt_dlp():
    """Check if yt-dlp is installed and up to date"""
    try:
        import yt_dlp
        print(f"\n✅ yt-dlp is installed (version: {yt_dlp.version.__version__})")
        return True
    except ImportError:
        print("\n❌ yt-dlp is not installed!")
        print("   Install with: pip install yt-dlp")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("🎵 Jule Bot - YouTube Cookie Setup Helper")
    print("=" * 50)
    
    if not check_yt_dlp():
        return
    
    print("\nThis helper will configure YouTube cookies to avoid bot detection.")
    print("\nChoose a setup method:")
    print("  1. Use browser cookies (recommended - easier)")
    print("  2. Manual cookie export (advanced)")
    print("  3. Test current configuration")
    print("  4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        setup_browser_cookies()
    elif choice == '2':
        manual_cookie_setup()
    elif choice == '3':
        test_youtube_access()
    elif choice == '4':
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice!")

def test_youtube_access():
    """Test if YouTube access is working"""
    print("\n🧪 Testing YouTube Access")
    print("=" * 50)
    
    try:
        import yt_dlp
        
        print("\nAttempting to search YouTube...")
        
        ytdl = yt_dlp.YoutubeDL({
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1',
        })
        
        result = ytdl.extract_info("test search", download=False)
        
        if result and 'entries' in result and result['entries']:
            print("✅ YouTube access is working!")
            print(f"   Found: {result['entries'][0].get('title', 'Unknown')}")
        else:
            print("⚠️  Search completed but no results returned")
        
    except Exception as e:
        error_msg = str(e)
        if 'Sign in to confirm' in error_msg or 'bot' in error_msg.lower():
            print("❌ YouTube bot detection active!")
            print("   You need to set up cookies.")
            print("\n   Run this script again and choose option 1 or 2.")
        else:
            print(f"❌ Error: {error_msg}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
        sys.exit(0)

