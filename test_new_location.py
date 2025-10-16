import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['creative_resizer']
    
    print("✅ Testing MongoDB Connection...")
    print("=" * 50)
    
    # List collections
    collections = await db.list_collection_names()
    print(f"Collections: {collections}")
    
    # Count documents
    for col in ['jobs', 'resize_jobs', 'ad_briefs']:
        count = await db[col].count_documents({})
        print(f"  {col}: {count} documents")
    
    client.close()
    print("\n✅ Connection test successful!")

asyncio.run(test())
