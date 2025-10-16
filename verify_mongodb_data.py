import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def verify_data():
    # Connect to MongoDB
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['creative_resizer']
    
    print("📊 MongoDB Data Verification")
    print("=" * 50)
    
    # Check collections
    collections = await db.list_collection_names()
    print(f"\n✅ Collections: {collections}")
    
    # Count documents in each collection
    for collection_name in ['jobs', 'resize_jobs', 'ad_briefs']:
        count = await db[collection_name].count_documents({})
        print(f"   - {collection_name}: {count} documents")
    
    # Show sample from ad_briefs
    print("\n📝 Sample ad_brief:")
    brief = await db.ad_briefs.find_one()
    if brief:
        print(f"   Campaign: {brief.get('campaign_name', 'N/A')}")
        print(f"   Platforms: {brief.get('platforms', [])}")
    
    # Show sample from resize_jobs
    print("\n🔄 Sample resize_job:")
    job = await db.resize_jobs.find_one()
    if job:
        print(f"   Job ID: {job.get('job_id', 'N/A')}")
        print(f"   Status: {job.get('status', 'N/A')}")
    
    client.close()
    print("\n✅ MongoDB verification complete!")

if __name__ == "__main__":
    asyncio.run(verify_data())
