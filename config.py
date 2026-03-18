"""
Configuration file for Telegram Arbitrage Forwarder
Copy this to config.py and fill in your actual values.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# TELEGRAM API CREDENTIALS
# ============================================
# Get these from https://my.telegram.org/apps
API_ID = os.getenv('TELEGRAM_API_ID', 'your_api_id_here')
API_HASH = os.getenv('TELEGRAM_API_HASH', 'your_api_hash_here')
PHONE_NUMBER = os.getenv('TELEGRAM_PHONE', 'your_phone_number_here')  # Format: +1234567890

# ============================================
# CHANNEL CONFIGURATION
# ============================================
# Source channels: Where arbitrage opportunities are posted
# Can be username (e.g., '@channelname') or channel ID (e.g., -1001234567890)
# For MULTIPLE channels, separate with commas (no spaces after commas)
# Example: @channel1,@channel2,-1001234567890
SOURCE_CHANNEL_ID = os.getenv('SOURCE_CHANNEL_ID', '@source_channel_username')

# Parse multiple source channels if comma-separated
if ',' in SOURCE_CHANNEL_ID:
    SOURCE_CHANNELS = [ch.strip() for ch in SOURCE_CHANNEL_ID.split(',')]
else:
    SOURCE_CHANNELS = [SOURCE_CHANNEL_ID]

# Convert numeric IDs to integers (Telegram requires this)
def parse_channel_id(channel_id):
    """Convert string channel IDs to proper format (int or string)"""
    channel_id = channel_id.strip()
    # Check if it's a numeric ID (with or without minus sign)
    if channel_id.lstrip('-').isdigit():
        return int(channel_id)
    return channel_id

SOURCE_CHANNELS = [parse_channel_id(ch) for ch in SOURCE_CHANNELS]

# Target channel: Your channel where formatted messages will be posted
# You must be admin of this channel with posting rights
TARGET_CHANNEL_ID = os.getenv('TARGET_CHANNEL_ID', '@your_channel_username')
TARGET_CHANNEL_ID = parse_channel_id(TARGET_CHANNEL_ID)

# ============================================
# SESSION CONFIGURATION
# ============================================
# Session name for Telethon (will create a .session file)
SESSION_NAME = os.getenv('SESSION_NAME', 'arbitrage_forwarder')

# ============================================
# FILTERING OPTIONS (Optional)
# ============================================
# Minimum profit percentage to forward (set to 0 to forward all)
MIN_PROFIT_THRESHOLD = float(os.getenv('MIN_PROFIT_THRESHOLD', '2.5'))

# Keywords that must be present for a message to be forwarded
REQUIRED_KEYWORDS = os.getenv('REQUIRED_KEYWORDS', '').split(',') if os.getenv('REQUIRED_KEYWORDS') else []

# Keywords that will exclude a message from being forwarded
EXCLUDED_KEYWORDS = os.getenv('EXCLUDED_KEYWORDS', '').split(',') if os.getenv('EXCLUDED_KEYWORDS') else []
