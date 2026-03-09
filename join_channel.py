"""
Script to join a Telegram channel/group and verify access
Use this to make your bot account join channels with topics/forums
"""

import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from config import API_ID, API_HASH, PHONE_NUMBER, SESSION_NAME

async def join_and_verify_channel(channel_id):
    """Join a channel and verify we can access it"""
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    await client.start(phone=PHONE_NUMBER)
    print(f"\n🔍 Attempting to access channel: {channel_id}\n")
    
    try:
        # Try to get the entity first
        entity = await client.get_entity(channel_id)
        print(f"✅ Successfully accessed channel!")
        print(f"   Name: {entity.title}")
        print(f"   ID: {entity.id}")
        print(f"   Type: {'Forum/Topics' if getattr(entity, 'forum', False) else 'Regular Channel'}")
        
        # Try to join if it's a channel
        try:
            await client(JoinChannelRequest(entity))
            print(f"✅ Successfully joined the channel!")
        except Exception as join_error:
            if "already" in str(join_error).lower():
                print(f"ℹ️  Already a member of this channel")
            else:
                print(f"⚠️  Join attempt: {join_error}")
        
        # Test reading messages
        print(f"\n📝 Testing message access...")
        async for message in client.iter_messages(entity, limit=3):
            print(f"   ✓ Can read messages (latest: {message.date})")
            break
        else:
            print(f"   ⚠️  No messages found or can't read messages")
            
    except ValueError as e:
        print(f"❌ Cannot access channel: {e}")
        print(f"\n💡 Possible solutions:")
        print(f"   1. Make sure you manually joined this channel in Telegram app")
        print(f"   2. If it's a private channel, you need an invite link")
        print(f"   3. Try using the channel username instead of ID (or vice versa)")
        print(f"   4. For forum/topic channels, ensure you have access to read all topics")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await client.disconnect()
    print("\n✅ Done!\n")

if __name__ == "__main__":
    # Test the problematic channel
    channel_id = "-1002880641050"  # Change this if needed
    
    print("=" * 60)
    print("Testing Channel Access")
    print("=" * 60)
    
    asyncio.run(join_and_verify_channel(channel_id))
