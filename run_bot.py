#!/usr/bin/env python3
"""
CZ.AI Telegram Bot - Startup Script

This script provides a convenient way to run the CZ.AI bot with proper configuration.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['TELEGRAM_TOKEN', 'GEMINI_API_KEY', 'ADMIN_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your environment or .env file")
        return False
    
    return True

def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path(".env")
    if env_file.exists():
        print("📦 Loading environment variables from .env file...")
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("⚠️  No .env file found. Make sure environment variables are set.")

def main():
    """Main function to run the CZ.AI bot."""
    print("🚀 Starting CZ.AI Telegram Bot...")
    print("⚠️  Not financial advice. Just CZ.AI vibes 🐂🚀")
    
    # Load environment variables
    load_env_file()
    
    # Check if required environment variables are set
    if not check_environment():
        sys.exit(1)
    
    # Verify dependencies
    try:
        import telegram
        import google.genai
        import dotenv
        print("✅ Dependencies verified")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        sys.exit(1)
    
    # Start the bot
    print("🤖 Initializing CZ.AI bot...")
    try:
        # Import and run the main bot
        from bot import main as bot_main
        import asyncio
        
        print("✅ CZ.AI bot started successfully!")
        print("💡 Bot is now running. Press Ctrl+C to stop.")
        asyncio.run(bot_main())
    except KeyboardInterrupt:
        print("\n⚠️  Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()