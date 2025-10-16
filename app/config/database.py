# app/config/database.py - MongoDB Only
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Global MongoDB client and database
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_db: Optional[AsyncIOMotorDatabase] = None


async def get_mongodb() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance"""
    global mongodb_db
    if mongodb_db is None:
        raise Exception("MongoDB not initialized. Call init_db() first.")
    return mongodb_db


async def init_db():
    """Initialize MongoDB connection"""
    global mongodb_client, mongodb_db

    try:
        # Connect to MongoDB
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb_db = mongodb_client[settings.MONGODB_DB]

        # Test connection
        await mongodb_client.admin.command('ping')

        # Create indexes for jobs collection
        await mongodb_db.jobs.create_index([("status", 1), ("created_at", -1)])
        await mongodb_db.jobs.create_index([("id", 1)], unique=True)

        # Create indexes for resize_jobs collection (job queue)
        await mongodb_db.resize_jobs.create_index([("status", 1), ("timestamp", 1)])
        await mongodb_db.resize_jobs.create_index([("job_id", 1)])

        logger.info("✅ MongoDB initialized successfully")
        logger.info(f"   Database: {settings.MONGODB_DB}")
        logger.info(f"   Collections: jobs, resize_jobs, ad_briefs")

    except Exception as e:
        logger.error(f"❌ Failed to initialize MongoDB: {e}")
        raise


async def close_db():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")


async def get_db():
    """FastAPI dependency to get MongoDB database"""
    return await get_mongodb()
