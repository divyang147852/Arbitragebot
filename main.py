"""
Telegram Arbitrage Forwarder Bot
Monitors a source Telegram channel for arbitrage opportunities and forwards them 
to your channel with improved formatting.
"""

import asyncio
import logging
import logging.handlers
import re
import hashlib
from datetime import datetime, timedelta
from collections import deque
from telethon import TelegramClient, events
from telethon.tl.types import Message
from config import (
    API_ID,
    API_HASH,
    PHONE_NUMBER,
    SOURCE_CHANNELS,
    TARGET_CHANNEL_ID,
    SESSION_NAME
)
from message_formatter import format_arbitrage_message
from date_utils import is_match_within_days, get_match_date_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            'bot.log', maxBytes=1*1024*1024, backupCount=2  # Max 1MB, keep 2 backups = 3MB total max
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ArbitrageForwarder:
    """Bot that forwards and formats arbitrage messages from source to target channel."""
    
    def __init__(self):
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.source_channels = SOURCE_CHANNELS  # Now supports multiple channels
        self.target_channel = TARGET_CHANNEL_ID
        # Deduplicate messages: store hashes of recent messages for 10 minutes
        self.recent_messages = {}  # {hash: timestamp}
        self.dedup_window_minutes = 10
        
    async def start(self):
        """Start the bot and begin monitoring."""
        await self.client.start(phone=PHONE_NUMBER)
        logger.info("Bot started successfully!")
        
        # Verify we can access all source channels and target channel
        try:
            logger.info(f"Monitoring {len(self.source_channels)} source channel(s):")
            for channel_id in self.source_channels:
                try:
                    source = await self.client.get_entity(channel_id)
                    channel_name = source.title if hasattr(source, 'title') else channel_id
                    logger.info(f"  ✓ {channel_name} ({channel_id})")
                except Exception as e:
                    logger.error(f"  ✗ Cannot access {channel_id}: {e}")
                    logger.error(f"    Make sure you're a member of this channel!")
            
            target = await self.client.get_entity(self.target_channel)
            logger.info(f"Posting to: {target.title if hasattr(target, 'title') else self.target_channel}")
        except Exception as e:
            logger.error(f"Error accessing channels: {e}")
            return
        
        # Register message handler for ALL source channels
        @self.client.on(events.NewMessage(chats=self.source_channels))
        async def handler(event):
            await self.handle_new_message(event)
        
        logger.info("Listening for new messages from all source channels...")
        await self.client.run_until_disconnected()
    
    async def handle_new_message(self, event):
        """Process new message from source channel."""
        try:
            message_text = event.message.message
            
            if not message_text:
                logger.debug("Skipping empty message")
                return
            
            # Get message ID for logging
            msg_id = event.message.id
            
            # Get source channel info early for logging
            chat = await event.get_chat()
            source_name = chat.title if hasattr(chat, 'title') else chat.username if hasattr(chat, 'username') else 'Unknown'
            chat_id = chat.id
            
            # Clean up old entries from dedup cache (older than 10 minutes)
            now = datetime.now()
            cutoff = now - timedelta(minutes=self.dedup_window_minutes)
            self.recent_messages = {h: t for h, t in self.recent_messages.items() if t > cutoff}
            
            # Create hash of message content + message ID for deduplication
            message_hash = hashlib.md5(f"{chat_id}:{msg_id}:{message_text}".encode()).hexdigest()
            
            # Check if we've seen this message recently
            if message_hash in self.recent_messages:
                time_ago = (now - self.recent_messages[message_hash]).seconds
                logger.info(f"⚠ Skipping duplicate from [{source_name}] (ID: {msg_id}, seen {time_ago}s ago)")
                return
            
            # Mark this message as seen
            self.recent_messages[message_hash] = now
            
            # Extract URLs from message entities (hidden links)
            full_text = message_text
            if event.message.entities:
                urls = []
                for entity in event.message.entities:
                    # Check for text URLs (hidden links)
                    if hasattr(entity, 'url'):
                        urls.append(entity.url)
                
                # Append URLs to text for processing
                if urls:
                    full_text = message_text + "\n" + "\n".join(urls)
                    logger.debug(f"Extracted {len(urls)} hidden URLs from message entities")
            
            # Check if this looks like an arbitrage opportunity (Kalshi + Polymarket)
            if not self.is_arbitrage_message(full_text):
                logger.debug(f"Message from [{source_name}] doesn't have both platforms")
                return
            
            # Check if match is within 3 days
            date_info = get_match_date_info(full_text)
            
            if not date_info['within_range']:
                if date_info['date_found']:
                    logger.info(f"✗ Skipping [{source_name}]: {date_info['reason']} (Date: {date_info['date_str']})")
                else:
                    logger.debug(f"⚠ No date found in message from [{source_name}], posting anyway")
            
            # Only post if within 3 days (or no date found)
            if date_info['within_range']:
                date_str = f" (Match: {date_info['date_str']})" if date_info['date_found'] else " (Date unknown)"
                logger.info(f"✓ Detected valid arbitrage from [{source_name}]{date_str}")
                
                # Format the message (use full_text which includes extracted URLs)
                formatted_message = format_arbitrage_message(full_text)
                
                # Post to target channel
                await self.client.send_message(
                    self.target_channel,
                    formatted_message,
                    parse_mode='markdown'
                )
                
                logger.info(f"✓ Posted to target channel")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
    
    def is_arbitrage_message(self, text: str) -> bool:
        """
        STRICT MODE: Only forward if message contains BOTH Kalshi AND Polymarket.
        No other platform combinations will be forwarded.
        """
        text_lower = text.lower()
        
        # Must contain BOTH Kalshi AND Polymarket
        has_kalshi = 'kalshi' in text_lower
        has_polymarket = 'polymarket' in text_lower
        
        if has_kalshi and has_polymarket:
            logger.debug("✓ Message contains BOTH Kalshi and Polymarket")
            return True
        
        # Log what's missing
        if has_kalshi and not has_polymarket:
            logger.debug("✗ Skipping: Has Kalshi but missing Polymarket")
        elif has_polymarket and not has_kalshi:
            logger.debug("✗ Skipping: Has Polymarket but missing Kalshi")
        else:
            logger.debug("✗ Skipping: Missing both platforms")
        
        return False


async def main():
    """Main entry point."""
    bot = ArbitrageForwarder()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        if bot.client.is_connected():
            await bot.client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
