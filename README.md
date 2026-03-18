# Telegram Arbitrage Forwarder Bot

**Automatically fetch arbitrage opportunities from a Telegram channel and post them formatted to your own channel.**

## 🎯 Features

- ✅ Monitor any Telegram channel for arbitrage opportunities
- ✅ Automatically detect arbitrage-related messages
- ✅ Format messages professionally with emojis and structure
- ✅ Extract key information (platforms, odds, profit %)
- ✅ Post to your channel in real-time
- ✅ Configurable filtering options
- ✅ Logging for monitoring and debugging
- ✅ **AWS EC2 ready** - Optimized for cloud deployment

## 🌐 AWS EC2 Deployment

**Want to run this bot 24/7 on AWS EC2?** 

👉 **See [EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md) for complete step-by-step AWS deployment guide**

Benefits:
- 24/7 uptime
- Auto-restart on crashes
- Free tier eligible (~$0/month for first 12 months)
- Low cost (~$3-5/month after free tier)

---

## 📋 Prerequisites

- Python 3.8 or higher
- Telegram account and phone number
- Telegram API credentials (API ID and Hash)
- Admin access to your target channel

## 🚀 Quick Start

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Create a new application
4. Copy your `API_ID` and `API_HASH`

### 2. Setup Project

```bash
# Navigate to the project directory
cd telegram_arbitrage_forwarder

# Create a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Bot

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` file with your credentials:
   ```
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_PHONE=+1234567890
   SOURCE_CHANNEL_ID=@source_channel
   TARGET_CHANNEL_ID=@your_channel
   ```

### 4. Run the Bot

**On Windows:**
```bash
run.bat
```

**On Linux/Mac or directly:**
```bash
python main.py
```

### 5. First Time Setup

- On first run, Telegram will send you a verification code
- Enter the code when prompted
- A session file will be created (you won't need to verify again)

## ⚙️ Configuration

### Channel Settings

**Source Channel:**
- The channel you want to monitor
- Format: `@channelname` or `-1001234567890` (channel ID)
- You must be a member of this channel

**Target Channel:**
- Your channel where formatted messages will be posted
- You must be an admin with posting rights
- Format: `@your_channel_username` or channel ID

### Filtering Options

Edit `config.py` or `.env` to customize:

```python
# Minimum profit threshold (0 = forward all)
MIN_PROFIT_THRESHOLD=2.0

# Required keywords (comma-separated)
REQUIRED_KEYWORDS=arbitrage,profit

# Excluded keywords (comma-separated)
EXCLUDED_KEYWORDS=spam,test
```

## 📝 Message Format

The bot formats messages with:
- 🎯 Clear headers and sections
- 📊 Event/market information
- 🔹 Platform details with market cents pricing
- 💰 Profit percentage highlighted
- 🔗 Clickable links
- ⏰ Timestamp

**Example Output:**
```
🎯 **ARBITRAGE OPPORTUNITY**
━━━━━━━━━━━━━━━━━━━━━━

📊 **Event:** Presidential Election 2024

🔹 **Kalshi** @ 45¢
🔹 **Polymarket** @ 58¢

💰 **Expected Profit:** 3.15%

🔗 **Links:**
   [1] https://kalshi.com/...
   [2] https://polymarket.com/...

⏰ Posted at 14:32:15
━━━━━━━━━━━━━━━━━━━━━━
```

## 🛠️ Customization

### Custom Message Format

Edit `message_formatter.py` to customize the message format:

```python
def create_structured_message(info: dict) -> str:
    # Customize your message format here
    lines = [
        "🎯 **YOUR CUSTOM HEADER**",
        # Add your formatting logic
    ]
    return "\n".join(lines)
```

### Custom Detection Logic

Edit `main.py` to customize arbitrage detection:

```python
def is_arbitrage_message(self, text: str) -> bool:
    # Add your custom keywords or logic
    keywords = ['arbitrage', 'your_custom_keyword']
    # ...
```

## 📊 Monitoring

- All activity is logged to `bot.log`
- Console output shows real-time activity
- Check logs for errors or issues

## 🔧 Troubleshooting

### "Could not access channel"
- Verify you're a member of the source channel
- Verify you're admin of the target channel
- Check channel ID format (try both @username and numeric ID)

### "Phone number not authorized"
- Make sure you entered the verification code correctly
- Delete `.session` file and try again

### "No messages being forwarded"
- Check if messages contain your keywords
- Review `is_arbitrage_message()` logic
- Check logs for debugging info

### Getting Channel ID

To find a channel's numeric ID, use Telegram web or bots like @userinfobot

## 📁 Project Structure

```
telegram_arbitrage_forwarder/
│
├── main.py                 # Main bot script
├── message_formatter.py    # Message formatting logic
├── config.py               # Configuration file
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment file
├── .env                    # Your actual config (create this)
├── run.bat                 # Windows run script
├── README.md               # This file
└── bot.log                 # Log file (created on run)
```

## 🔒 Security Notes

- Never commit your `.env` file or `.session` file
- Keep your API credentials private
- Don't share your session file
- Add `.env` and `*.session` to `.gitignore`

## ⚖️ Legal & Ethics

- Only monitor channels you have permission to access
- Respect channel rules and ToS
- Don't spam or abuse the forwarding feature
- Be aware of rate limits

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `bot.log`
3. Verify your configuration in `.env`

## 🙏 Credits

Built with:
- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram API library
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment configuration

---

**Happy Arbitraging! 🚀💰**
