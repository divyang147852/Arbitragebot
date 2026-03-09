"""
Script to test different ID formats and find which one works
"""

import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH, PHONE_NUMBER, SESSION_NAME

async def test_id_formats(base_id):
    """Test different ID formats to find the working one"""
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    
    formats_to_try = [
        base_id,                    # Original: 2880641050
        -int(base_id),              # Negative: -2880641050
        f"-100{base_id}",           # With -100: -1002880641050
        int(f"-100{base_id}")       # As int: -1002880641050
    ]
    
    print(f"\n🔍 Testing ID formats for: {base_id}\n")
    print("=" * 70)
    
    for id_format in formats_to_try:
        try:
            entity = await client.get_entity(id_format)
            print(f"✅ SUCCESS with format: {id_format}")
            print(f"   Channel Name: {entity.title}")
            print(f"   Type: {'Forum/Topics' if getattr(entity, 'forum', False) else 'Regular'}")
            print(f"   👉 USE THIS IN .ENV: {id_format}")
            print("=" * 70)
            break
        except Exception as e:
            print(f"❌ Failed with format: {id_format}")
            print(f"   Error: {str(e)[:50]}")
            print("-" * 70)
    
    await client.disconnect()

if __name__ == "__main__":
    # The ID from get_channel_ids.py
    channel_id = "2880641050"
    asyncio.run(test_id_formats(channel_id))
