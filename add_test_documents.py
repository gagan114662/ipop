#!/usr/bin/env python3
"""
Add test documents to MongoDB for migration verification
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def add_test_documents():
    """Add various test documents to verify MongoDB setup"""
    print("="*60)
    print("Adding Test Documents to MongoDB")
    print("="*60)

    try:
        # Connect to MongoDB
        print("\n1. Connecting to MongoDB...")
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        await client.admin.command('ping')
        print("   ✅ Connected to MongoDB")

        db = client["creative_resizer"]
        ad_briefs_collection = db["ad_briefs"]
        jobs_collection = db["resize_jobs"]

        # Test Document 1: Minimal Ad Brief Document
        print("\n2. Adding Minimal Ad Brief Document...")
        minimal_doc = {
            "title": "Test Ad Resizer Brief",
            "description": "Basic migration test entry.",
            "createdAt": "2025-10-15T15:02:00Z",
            "owner": "testuser@ipop.ai",
            "status": "draft"
        }
        result1 = await ad_briefs_collection.insert_one(minimal_doc)
        print(f"   ✅ Inserted minimal document with ID: {result1.inserted_id}")

        # Test Document 2: Full Ad Brief With Attachments
        print("\n3. Adding Full Ad Brief With Attachments...")
        full_doc = {
            "title": "Migration Validation Ad",
            "description": "Full field population for migration QA.",
            "createdAt": "2025-10-15T15:02:00Z",
            "updatedAt": "2025-10-15T15:02:00Z",
            "owner": "gagan@getfoolish.com",
            "projectId": "1234567890",
            "taskId": "0987654321",
            "status": "active",
            "attachments": [
                {
                    "filename": "Screenshot-2025-10-14-at-4.47.53-PM.jpg",
                    "url": "link_to_file_storage"
                }
            ]
        }
        result2 = await ad_briefs_collection.insert_one(full_doc)
        print(f"   ✅ Inserted full document with ID: {result2.inserted_id}")

        # Test Document 3: Edge Case Document (missing/extra fields)
        print("\n4. Adding Edge Case Document...")
        edge_doc = {
            "title": "Edge Case Test",
            "extraField": "Testing unrecognized field retention",
            "status": None
        }
        result3 = await ad_briefs_collection.insert_one(edge_doc)
        print(f"   ✅ Inserted edge case document with ID: {result3.inserted_id}")

        # Test Document 4: Relation/Reference Test
        print("\n5. Adding Relation/Reference Test Document...")
        relation_doc = {
            "title": "Relational Integrity Test",
            "linkedTaskIds": ["101", "102", "103"],
            "owner": "gagan@getfoolish.com"
        }
        result4 = await ad_briefs_collection.insert_one(relation_doc)
        print(f"   ✅ Inserted relation test document with ID: {result4.inserted_id}")

        # Add some sample job queue documents too
        print("\n6. Adding Sample Job Queue Documents...")

        job1 = {
            "job_id": "job-001",
            "status": "PENDING",
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "file_type": "image",
            "platforms": ["instagram_feed", "facebook_feed"]
        }
        result5 = await jobs_collection.insert_one(job1)
        print(f"   ✅ Inserted pending job with ID: {result5.inserted_id}")

        job2 = {
            "job_id": "job-002",
            "status": "PROCESSING",
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "processing_started_at": datetime.utcnow(),
            "file_type": "video",
            "platforms": ["tiktok_short", "youtube_short"]
        }
        result6 = await jobs_collection.insert_one(job2)
        print(f"   ✅ Inserted processing job with ID: {result6.inserted_id}")

        job3 = {
            "job_id": "job-003",
            "status": "COMPLETED",
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "processing_started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "file_type": "image",
            "platforms": ["instagram_feed"],
            "output_files": {
                "instagram_feed": "/path/to/output.jpg"
            }
        }
        result7 = await jobs_collection.insert_one(job3)
        print(f"   ✅ Inserted completed job with ID: {result7.inserted_id}")

        # Display summary
        print("\n" + "="*60)
        print("✅ All test documents added successfully!")
        print("="*60)
        print("\nDatabase: creative_resizer")
        print("\nCollections created:")
        print(f"  1. ad_briefs - {await ad_briefs_collection.count_documents({})} documents")
        print(f"  2. resize_jobs - {await jobs_collection.count_documents({})} documents")
        print("\n📊 View in MongoDB Compass:")
        print("   Connection: mongodb://localhost:27017")
        print("   Database: creative_resizer")
        print("\nCollections to check:")
        print("   • ad_briefs (4 test documents)")
        print("   • resize_jobs (3 job queue documents)")

        # Close connection
        client.close()
        return True

    except Exception as e:
        print(f"\n❌ Failed to add test documents: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    result = asyncio.run(add_test_documents())
    sys.exit(0 if result else 1)
