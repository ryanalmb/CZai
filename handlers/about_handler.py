import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

ABOUT_SNIPPET = (
    "CZ.AI — Your CZ‑style consultant and assistant (bilingual)\n\n"
    "English: A confident, upbeat CZ‑style consultant for BNB Chain. Short, educational replies with builder energy — no financial advice.\n"
    "中文：你的 CZ 风格顾问与助手（双语）。自信积极、简洁有力，提供高层次教育内容——不提供投资建议。\n\n"
    "Use me for: welcomes, concept explainers, safety basics, community vibes, and quick overviews.\n"
    "适用场景：新手欢迎、概念科普、安全基础、社区氛围、与主题速览。\n\n"
    "Disclaimer: Parody project. Not affiliated with CZ or Binance. Educational only — not financial advice.\n"
    "免责声明：本项目为戏仿创作，与 CZ 或 Binance 无关联。仅用于教育与娱乐，不构成任何投资建议。"
)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /about command with a concise bilingual description."""
    await update.message.reply_text(ABOUT_SNIPPET)
    logger.info("Sent /about snippet to user %s", update.effective_user.id)
