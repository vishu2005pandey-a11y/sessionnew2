# Telegram Mini App Authentication System

## Setup Instructions

1. **Create a Telegram Bot**
   - Go to @BotFather on Telegram
   - Create a new bot and get your bot token
   - Set the bot token in the `.env` file

2. **Install Dependencies**
   ```
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Host the Mini App**
   - You need to host the `static` folder on a public HTTPS server (e.g., Vercel, Netlify, or ngrok)
   - Update `MINI_APP_URL` in `.env` with your mini app URL

4. **Run the Bot**
   ```
   python bot.py
   ```

5. **Run the Local Server (for development)**
   ```
   python server.py
   ```

## Features

- `/start` command sends a message with a button to open the mini app
- Mini app has video background, emoji center, 5-digit OTP input, and keypad
- Bot sends OTP and verifies it
- 2FA verification page available
