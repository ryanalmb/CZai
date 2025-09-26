import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

ABOUT_SNIPPET = (
    "CZ.AI — Bilingual, Optimistic, Educational\n\n"
    "English: A playful, upbeat Telegram assistant inspired by CZ’s vibe — sharing short, high‑energy, educational context about crypto and blockchain. No financial advice.\n"
    "中文：一个风格轻松、积极乐观的双语助手，用简洁有力的方式科普加密与区块链的高层次知识。不提供任何投资建议。\n\n"
    "Use me for: friendly welcomes, concept explainers, community vibes, and quick overviews.\n"
    "适用场景：友好欢迎、概念讲解、社区互动、与主题速览。\n\n"
    "Disclaimer: Parody project. Not affiliated with CZ or Binance. Educational only — not financial advice.\n"
    "免责声明：本项目为戏仿创作，与 CZ 或 Binance 无关联。仅用于教育与娱乐，不构成任何投资建议。"
)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /about command with a concise bilingual description."""
    await update.message.reply_text(ABOUT_SNIPPET)
    logger.info("Sent /about snippet to user %s", update.effective_user.id)
