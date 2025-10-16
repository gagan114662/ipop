#!/usr/bin/env python3
"""
Simple MongoDB connection test without requiring app settings
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongodb():
    """Test MongoDB connection directly"""
    print("="*60)
    print("MongoDB Connection Test")
    print("="*60)

    try:
        # Connect to MongoDB
        print("\n1. Connecting to MongoDB...")
        client = AsyncIOMotorClient("mongodb://localhost:27017")

        # Test connection
        await client.admin.command('ping')
        print("   ✅ Successfully connected to MongoDB")

        # Get database
        db = client["creative_resizer"]
        collection = db["resize_jobs"]

        # Test insert
        print("\n2. Testing insert operation...")
        test_doc = {
            "job_id": "test-12345",
            "status": "PENDING",
            "test": True
        }
        result = await collection.insert_one(test_doc)
        print(f"   ✅ Successfully inserted document with ID: {result.inserted_id}")

        # Test find
        print("\n3. Testing find operation...")
        found_doc = await collection.find_one({"job_id": "test-12345"})
        if found_doc:
            print(f"   ✅ Successfully found document: job_id={found_doc['job_id']}")

        # Test update
        print("\n4. Testing update operation...")
        update_result = await collection.update_one(
            {"job_id": "test-12345"},
            {"$set": {"status": "COMPLETED"}}
        )
        print(f"   ✅ Successfully updated {update_result.modified_count} document(s)")

        # Clean up test data
        print("\n5. Cleaning up test data...")
        delete_result = await collection.delete_one({"job_id": "test-12345"})
        print(f"   ✅ Successfully deleted {delete_result.deleted_count} document(s)")

        # Close connection
        client.close()

        print("\n" + "="*60)
        print("✅ All MongoDB tests passed!")
        print("="*60)
        print("\nMongoDB URL: mongodb://localhost:27017")
        print("Database: creative_resizer")
        print("Collection: resize_jobs")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    result = asyncio.run(test_mongodb())
    sys.exit(0 if result else 1)
