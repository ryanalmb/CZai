import asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from config.settings import settings
from handlers.start_handler import start_command
from handlers.cz_handler import cz_command
from handlers.announce_handler import announce_command

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.log_level.upper())
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the Telegram bot."""
    logger.info("Starting CZ.AI bot...")
    logger.info("CZ.AI is a fan-made parody. Not affiliated with CZ or Binance.")
    
    # Create the application
    application = ApplicationBuilder().token(settings.telegram_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("CZ", cz_command))
    application.add_handler(CommandHandler("announce", announce_command))
    
    logger.info("CZ.AI bot is running...")
    
    # Run the bot - run_polling() handles the event loop internally
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Keep the bot running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            await application.updater.stop()
            await application.stop()

if __name__ == "__main__":
    asyncio.run(main())