import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    welcome_message = (
        "Welcome to CZ.AI! 🚀\n\n"
        "I'm a fan-made parody bot in the style of CZ. Not affiliated with CZ or Binance.\n\n"
        "Use /CZ to get market insights in CZ's style.\n\n"
        "⚠️ Not financial advice. Just CZ.AI vibes 🐂🚀"
    )
    
    await update.message.reply_text(welcome_message)
    logger.info(f"User {update.effective_user.id} started the bot")