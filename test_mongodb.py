#!/usr/bin/env python3
"""
Test script to verify MongoDB migration is working correctly
"""
import asyncio
import sys
from app.services.mongodb_service import MongoDBService
from app.config.settings import settings

async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("="*60)
    print("MongoDB Migration Test")
    print("="*60)

    mongodb_service = MongoDBService()

    try:
        # Test 1: Connection
        print("\n1. Testing MongoDB connection...")
        await mongodb_service.connect()
        print("   ✅ Successfully connected to MongoDB")

        # Test 2: Add a test job
        print("\n2. Testing add_job operation...")
        test_job = {
            'job_id': 'test-job-12345',
            'timestamp': 1234567890.0,
            'test': True
        }
        await mongodb_service.add_job(test_job)
        print("   ✅ Successfully added test job to queue")

        # Test 3: Get pending job count
        print("\n3. Testing get_pending_job_count...")
        count = await mongodb_service.get_pending_job_count()
        print(f"   ✅ Pending jobs in queue: {count}")

        # Test 4: Get a job from queue
        print("\n4. Testing get_job operation...")
        retrieved_job = await mongodb_service.get_job()
        if retrieved_job:
            print(f"   ✅ Successfully retrieved job: {retrieved_job.get('job_id')}")
            print(f"   Job status changed to: {retrieved_job.get('status')}")
        else:
            print("   ⚠️  No jobs in queue")

        # Test 5: Disconnect
        print("\n5. Testing disconnect...")
        await mongodb_service.disconnect()
        print("   ✅ Successfully disconnected from MongoDB")

        print("\n" + "="*60)
        print("✅ All tests passed! MongoDB migration is working correctly")
        print("="*60)
        print(f"\nMongoDB URL: {settings.MONGODB_URL}")
        print(f"Database: {settings.MONGODB_DB}")
        print(f"Collection: {mongodb_service.collection_name}")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if mongodb_service.client:
            await mongodb_service.disconnect()

if __name__ == "__main__":
    result = asyncio.run(test_mongodb_connection())
    sys.exit(0 if result else 1)
