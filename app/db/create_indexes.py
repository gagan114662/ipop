"""
Database indexes initialization.

This script creates all necessary indexes for optimal query performance.
Run this during application startup or as a one-time setup.
"""
import asyncio
import structlog
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

logger = structlog.get_logger(__name__)


async def create_indexes():
    """Create all database indexes."""
    
    logger.info("creating_database_indexes")
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    try:
        # Clients collection
        await db.clients.create_index([("email", 1)], unique=True)
        await db.clients.create_index([("client_id", 1)], unique=True)
        logger.info("indexes_created", collection="clients")
        
        # SKUs collection
        await db.skus.create_index([("client_id", 1), ("sku_id", 1)], unique=True)
        await db.skus.create_index([("client_id", 1), ("status", 1)])
        logger.info("indexes_created", collection="skus")
        
        # Campaigns collection
        await db.campaigns.create_index([("client_id", 1), ("campaign_id", 1)], unique=True)
        await db.campaigns.create_index([("client_id", 1), ("status", 1)])
        await db.campaigns.create_index([("client_id", 1), ("sku_id", 1)])
        await db.campaigns.create_index([("platform", 1)])
        await db.campaigns.create_index([("client_id", 1), ("platform", 1)])
        await db.campaigns.create_index([("created_at", -1)])
        logger.info("indexes_created", collection="campaigns")
        
        # Performance metrics collection
        await db.performance_metrics.create_index([("campaign_id", 1), ("timestamp", -1)])
        await db.performance_metrics.create_index([("client_id", 1), ("timestamp", -1)])
        await db.performance_metrics.create_index([("client_id", 1), ("sku_id", 1), ("timestamp", -1)])
        await db.performance_metrics.create_index([("platform", 1), ("timestamp", -1)])
        await db.performance_metrics.create_index([("timestamp", -1)])
        # Compound index for time-based analytics
        await db.performance_metrics.create_index([
            ("client_id", 1),
            ("campaign_id", 1),
            ("timestamp", -1)
        ])
        logger.info("indexes_created", collection="performance_metrics")
        
        # Intelligence decisions collection
        await db.intelligence_decisions.create_index([("campaign_id", 1), ("timestamp", -1)])
        await db.intelligence_decisions.create_index([("client_id", 1), ("timestamp", -1)])
        await db.intelligence_decisions.create_index([("client_id", 1), ("applied", 1)])
        await db.intelligence_decisions.create_index([("timestamp", -1)])
        logger.info("indexes_created", collection="intelligence_decisions")
        
        # System benchmarks collection
        await db.system_benchmarks.create_index([("platform", 1), ("month", 1)], unique=True)
        await db.system_benchmarks.create_index([("platform", 1), ("timestamp", -1)])
        logger.info("indexes_created", collection="system_benchmarks")

        # Creatives collection
        await db.creatives.create_index([("client_id", 1), ("creative_id", 1)], unique=True)
        await db.creatives.create_index([("client_id", 1), ("status", 1)])
        await db.creatives.create_index([("campaign_ids", 1), ("status", 1)])
        await db.creatives.create_index([("platform", 1), ("platform_creative_id", 1)])
        await db.creatives.create_index([("created_at", -1)])
        await db.creatives.create_index([("tags", 1)])
        logger.info("indexes_created", collection="creatives")

        # Creative metrics collection
        await db.creative_metrics.create_index([("creative_id", 1), ("date", -1)])
        await db.creative_metrics.create_index([("campaign_id", 1), ("date", -1)])
        await db.creative_metrics.create_index([("client_id", 1), ("date", -1)])
        await db.creative_metrics.create_index([("platform", 1), ("date", -1)])
        await db.creative_metrics.create_index([("date", -1)])
        logger.info("indexes_created", collection="creative_metrics")

        # Creative tests collection
        await db.creative_tests.create_index([("client_id", 1), ("test_id", 1)], unique=True)
        await db.creative_tests.create_index([("campaign_id", 1), ("status", 1)])
        await db.creative_tests.create_index([("created_at", -1)])
        await db.creative_tests.create_index([("status", 1), ("is_concluded", 1)])
        logger.info("indexes_created", collection="creative_tests")

        # Platform tokens collection
        await db.platform_tokens.create_index(
            [("client_id", 1), ("platform", 1)],
            unique=True
        )
        await db.platform_tokens.create_index("updated_at")
        logger.info("indexes_created", collection="platform_tokens")

        logger.info("all_indexes_created_successfully")
        
    except Exception as e:
        logger.error("index_creation_failed", error=str(e))
        raise
    finally:
        client.close()


async def drop_indexes():
    """Drop all indexes (except _id). Use with caution!"""
    
    logger.warning("dropping_all_indexes")
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    try:
        collections = ["clients", "skus", "campaigns", "performance_metrics",
                      "intelligence_decisions", "system_benchmarks",
                      "creatives", "creative_metrics", "creative_tests",
                      "platform_tokens"]
        
        for collection_name in collections:
            collection = db[collection_name]
            await collection.drop_indexes()
            logger.info("indexes_dropped", collection=collection_name)
        
        logger.info("all_indexes_dropped")
        
    except Exception as e:
        logger.error("index_drop_failed", error=str(e))
        raise
    finally:
        client.close()


async def list_indexes():
    """List all indexes in database."""
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    try:
        collections = await db.list_collection_names()
        
        for collection_name in collections:
            collection = db[collection_name]
            indexes = await collection.list_indexes().to_list(length=100)
            
            print(f"\n{collection_name}:")
            for idx in indexes:
                print(f"  - {idx['name']}: {idx['key']}")
        
    finally:
        client.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            asyncio.run(create_indexes())
            print("✅ Indexes created successfully!")
        elif command == "drop":
            confirm = input("⚠️  Are you sure you want to drop all indexes? (yes/no): ")
            if confirm.lower() == "yes":
                asyncio.run(drop_indexes())
                print("✅ Indexes dropped!")
            else:
                print("❌ Cancelled")
        elif command == "list":
            asyncio.run(list_indexes())
        else:
            print("Usage: python -m app.db.create_indexes [create|drop|list]")
    else:
        # Default: create indexes
        asyncio.run(create_indexes())
        print("✅ Indexes created successfully!")
