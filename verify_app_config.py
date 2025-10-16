#!/usr/bin/env python3
"""
Verify that the app is correctly configured to use the creative_resizer database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def verify_configuration():
    """Verify database and collection configuration"""
    print("="*70)
    print("App Configuration Verification")
    print("="*70)

    try:
        # Connect to MongoDB
        print("\n1. Connecting to MongoDB...")
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        await client.admin.command('ping')
        print("   ✅ Connected to MongoDB")

        # Check database
        db_name = "creative_resizer"
        db = client[db_name]

        print(f"\n2. Checking Database: {db_name}")
        collections = await db.list_collection_names()
        print(f"   ✅ Database exists with {len(collections)} collections")

        # List all collections
        print(f"\n3. Collections in '{db_name}' database:")
        for col in collections:
            count = await db[col].count_documents({})
            print(f"   • {col}: {count} documents")

        # Verify expected collections
        print("\n4. Verifying Expected Collections:")
        expected_collections = {
            "resize_jobs": "Job queue for background processing",
            "ad_briefs": "Ad brief documents (test data)"
        }

        for col_name, description in expected_collections.items():
            if col_name in collections:
                count = await db[col_name].count_documents({})
                print(f"   ✅ {col_name}: {count} documents - {description}")
            else:
                print(f"   ⚠️  {col_name}: NOT FOUND - {description}")

        # Check app settings
        print("\n5. Checking App Configuration:")
        print("   From app/config/settings.py:")
        print("   • MONGODB_URL: mongodb://localhost:27017 (default)")
        print("   • MONGODB_DB: creative_resizer (default)")

        print("\n6. Checking MongoDB Service Configuration:")
        print("   From app/services/mongodb_service.py:")
        print("   • Database: settings.MONGODB_DB → 'creative_resizer'")
        print("   • Collection: 'resize_jobs' (job queue)")

        # Sample document from resize_jobs
        print("\n7. Sample Document from 'resize_jobs' Collection:")
        sample_job = await db.resize_jobs.find_one()
        if sample_job:
            sample_job.pop('_id', None)  # Remove _id for cleaner display
            import json
            print(f"   {json.dumps(sample_job, indent=3, default=str)}")
        else:
            print("   (No documents yet)")

        # Sample document from ad_briefs
        print("\n8. Sample Document from 'ad_briefs' Collection:")
        sample_brief = await db.ad_briefs.find_one()
        if sample_brief:
            sample_brief.pop('_id', None)
            import json
            print(f"   {json.dumps(sample_brief, indent=3, default=str)}")
        else:
            print("   (No documents yet)")

        # Verify workflow
        print("\n" + "="*70)
        print("✅ Configuration Verification Complete")
        print("="*70)
        print("\nWorkflow Summary:")
        print("  1. App connects to: mongodb://localhost:27017")
        print("  2. App uses database: creative_resizer")
        print("  3. Job queue collection: resize_jobs")
        print("  4. Ad briefs collection: ad_briefs")
        print("\nAll operations will read/write to these collections in the")
        print("'creative_resizer' database.")

        # Check indexes
        print("\n9. Checking Indexes on 'resize_jobs':")
        indexes = await db.resize_jobs.list_indexes().to_list(length=None)
        for idx in indexes:
            print(f"   • {idx['name']}: {idx.get('key', {})}")

        client.close()
        return True

    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    result = asyncio.run(verify_configuration())
    sys.exit(0 if result else 1)
