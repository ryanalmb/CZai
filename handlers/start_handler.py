import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    welcome_message = (
        "Welcome to CZ.AI — your CZ‑style consultant and assistant on BNB Chain. 🚀\n\n"
        "I’m a fan‑made parody assistant (not affiliated with CZ or Binance). I keep things upbeat, educational, and bilingual (EN + 简体中文).\n\n"
        "Use /CZ to ask questions — I’ll reply in English first, then 简体中文.\n\n"
        "⚠️ Educational only. Not financial advice.\n"
    )
    
    await update.message.reply_text(welcome_message)
    logger.info(f"User {update.effective_user.id} started the bot")