"""
Script to get Channel IDs for all your Telegram channels/groups
Run this to find the ID of channels without usernames
"""

import asyncio
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
from config import API_ID, API_HASH, PHONE_NUMBER, SESSION_NAME

async def get_all_channels():
    """List all channels and groups with their IDs"""
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    await client.start(phone=PHONE_NUMBER)
    print("\n" + "="*70)
    print("YOUR TELEGRAM CHANNELS & GROUPS")
    print("="*70 + "\n")
    
    # Get all dialogs (chats, groups, channels)
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        
        # Only show channels and groups
        if isinstance(entity, (Channel, Chat)):
            channel_type = "Channel" if isinstance(entity, Channel) and entity.broadcast else "Group"
            username = f"@{entity.username}" if hasattr(entity, 'username') and entity.username else "No username"
            
            print(f"📱 {entity.title}")
            print(f"   Type: {channel_type}")
            print(f"   ID: {entity.id}")
            print(f"   Username: {username}")
            print(f"   For .env use: {entity.id}")
            print("-" * 70)
    
    await client.disconnect()
    print("\n✅ Done! Copy the channel ID you need and paste it in your .env file")
    print("   Format: SOURCE_CHANNEL_ID=-1001234567890")
    print("   (Include the minus sign if present)\n")

if __name__ == "__main__":
    asyncio.run(get_all_channels())
