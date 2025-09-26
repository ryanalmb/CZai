import logging
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import settings

logger = logging.getLogger(__name__)

async def announce_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /announce command (admin only)."""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id != settings.admin_id:
        logger.warning(f"User {user_id} tried to use /announce command without admin privileges")
        await update.message.reply_text("You don't have permission to use this command.")
        return
    
    # Extract the announcement message
    if context.args:
        announcement = " ".join(context.args)
    else:
        await update.message.reply_text("Please provide an announcement message.")
        return
    
    logger.info(f"Admin {user_id} made an announcement: {announcement}")
    
    # Add disclaimer to announcement
    announcement_with_disclaimer = f"📢 ADMIN ANNOUNCEMENT: {announcement}\n\n⚠️ Not financial advice. Just CZ.AI vibes 🐂🚀"
    
    # In a real implementation, you would broadcast this to all users
    # For now, just send it back to the admin as confirmation
    await update.message.reply_text(announcement_with_disclaimer)
    logger.info("Announcement sent successfully")