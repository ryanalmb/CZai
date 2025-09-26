import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from config.settings import settings
from handlers.start_handler import start_command
from handlers.cz_handler import cz_command
from handlers.announce_handler import announce_command
from handlers.about_handler import about_command

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.log_level.upper())
)
logger = logging.getLogger(__name__)

def main():
    """Run the Telegram bot in webhook or polling mode based on settings."""
    logger.info("Starting CZ.AI bot...")
    logger.info("CZ.AI is a fan-made parody. Not affiliated with CZ or Binance.")

    application = ApplicationBuilder().token(settings.telegram_token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("CZ", cz_command))
    application.add_handler(CommandHandler("announce", announce_command))
    application.add_handler(CommandHandler("about", about_command))

    if settings.use_webhook:
        if not settings.webhook_base_url:
            raise ValueError("WEBHOOK_BASE_URL must be set when USE_WEBHOOK=true")
        webhook_url = f"{settings.webhook_base_url.rstrip('/')}/{settings.webhook_path.lstrip('/')}"
        logger.info("Running in webhook mode on port %s with path /%s", settings.port, settings.webhook_path)
        application.run_webhook(
            listen="0.0.0.0",
            port=settings.port,
            url_path=settings.webhook_path,
            webhook_url=webhook_url,
            secret_token=(settings.webhook_secret or None),
        )
    else:
        logger.info("Running in polling mode")
        application.run_polling()

if __name__ == "__main__":
    main()
