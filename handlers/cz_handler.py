import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.ai_service import AIService
from utils.rate_limiter import RateLimiter
from config.settings import settings

logger = logging.getLogger(__name__)

# Initialize rate limiter and AI service
rate_limiter = RateLimiter(settings.rate_limit_seconds)
ai_service = AIService()

async def cz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /CZ command."""
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    
    # Check if user is allowed to use the command
    if not rate_limiter.is_allowed(user_id):
        remaining_time = rate_limiter.get_remaining_time(user_id)
        rate_limit_message = (
            f"Slow down, degen — one CZ consult every {settings.rate_limit_seconds}s. "
            f"({remaining_time}s remaining)\n"
            f"⚠️ Not financial advice. Just CZ.AI vibes 🐂🚀"
        )
        await update.message.reply_text(rate_limit_message)
        return
    
    # Extract the user's question
    if context.args:
        user_query = " ".join(context.args)
    else:
        user_query = "What should I know about crypto markets?"
    
    logger.info(f"User {user_id} ({user_name}) asked: {user_query}")
    
    # Update rate limiter
    rate_limiter.update_usage(user_id)
    
    try:
        # Generate response using AI service
        response = ai_service.generate_response(user_query)
        
        # Add disclaimer to response if not already present
        if "⚠️ Not financial advice. Just CZ.AI vibes 🐂🚀" not in response:
            response += "\n⚠️ Not financial advice. Just CZ.AI vibes 🐂🚀"
        
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error processing /CZ command for user {user_id}: {e}")
        error_message = (
            "Oops! CZ is temporarily indisposed. Try again later.\n"
            "⚠️ Not financial advice. Just CZ.AI vibes 🐂🚀"
        )
        await update.message.reply_text(error_message)