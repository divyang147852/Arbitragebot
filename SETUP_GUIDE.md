# Quick Setup Guide

## Step-by-Step Instructions

### 1️⃣ Get Telegram API Credentials (5 minutes)

1. Open https://my.telegram.org/apps in your browser
2. Log in with your Telegram phone number
3. Fill in the application details:
   - App title: "Arbitrage Forwarder"
   - Short name: "arbforwarder"
   - Platform: Choose any (e.g., Desktop)
4. Click "Create application"
5. **Save your API ID and API Hash** - you'll need these!

### 2️⃣ Find Your Channel Usernames

**Source Channel (where arbitrage bets come from):**
- Open the channel in Telegram
- If it has a public link: `t.me/channelname` → use `@channelname`
- If it's private: You'll need the channel ID (use @userinfobot to find it)

**Target Channel (your channel):**
- This must be a channel where you are admin
- Find its username the same way
- Make sure the bot has posting permissions

### 3️⃣ Configure the Bot (2 minutes)

1. Copy `.env.example` to `.env`:
   ```
   copy .env.example .env
   ```

2. Open `.env` in a text editor and fill in:
   ```
   TELEGRAM_API_ID=12345678
   TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
   TELEGRAM_PHONE=+12345678900
   SOURCE_CHANNEL_ID=@source_channel
   TARGET_CHANNEL_ID=@your_channel
   ```

### 4️⃣ Install Dependencies (1 minute)

Open PowerShell or Command Prompt in this folder:

```powershell
# Optional: Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 5️⃣ Run the Bot (1 minute)

**Option A - Use the batch file:**
```
run.bat
```

**Option B - Run directly:**
```
python main.py
```

### 6️⃣ First Time Login

1. Bot will ask for verification code
2. Check your Telegram messages
3. Enter the 5-digit code
4. Done! A session file is created

**Next time you run it, no login needed! 🎉**

---

## ✅ Verification Checklist

- [ ] Got API ID and API Hash from my.telegram.org
- [ ] Found source channel username/ID
- [ ] I'm admin of my target channel
- [ ] Created `.env` file with credentials
- [ ] Installed requirements (`pip install -r requirements.txt`)
- [ ] Ran the bot (`python main.py` or `run.bat`)
- [ ] Completed first-time verification
- [ ] Bot is monitoring and forwarding messages

---

## 🎨 Customize Message Format (Optional)

The bot automatically formats messages nicely. To customize:

1. Open `message_formatter.py`
2. Find `create_structured_message()` function
3. Modify the formatting template
4. Save and restart the bot

---

## 🔍 Testing

1. Send a test message in the source channel (or wait for new one)
2. Message should contain keywords like: arbitrage, profit, kalshi, polymarket
3. Check your target channel - formatted message should appear!
4. Check `bot.log` for detailed activity

---

## 🆘 Common Issues

**"Phone number invalid"**
- Use international format: +1234567890
- Include country code

**"Could not find channel"**
- For public channels: use @username
- For private channels: use numeric ID (-1001234567890)
- Make sure you're a member!

**"Permission denied on target channel"**
- You must be admin of the target channel
- Check bot has "Post Messages" permission

**No messages being forwarded**
- Check if source messages have keywords (arbitrage, profit, etc.)
- Lower the profit threshold in config
- Check `bot.log` for details

---

## 📱 Next Steps

1. Let bot run and monitor `bot.log`
2. Adjust keywords in `main.py` → `is_arbitrage_message()`
3. Customize message format in `message_formatter.py`
4. Set profit threshold if needed
5. Enjoy automated arbitrage alerts! 🚀

---

**Need help? Check bot.log for detailed error messages!**
