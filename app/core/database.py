"""
MongoDB database connection and utilities.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class Database:
    """MongoDB database manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB."""
        try:
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=settings.MONGODB_MAX_CONNECTIONS,
                minPoolSize=settings.MONGODB_MIN_CONNECTIONS,
            )
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info(
                "mongodb_connected",
                database=settings.MONGODB_DB_NAME,
                url=settings.MONGODB_URL.split('@')[-1]  # Hide credentials
            )
            
            # Create indexes
            await cls._create_indexes()
            
        except Exception as e:
            logger.error("mongodb_connection_failed", error=str(e))
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("mongodb_disconnected")
    
    @classmethod
    async def _create_indexes(cls):
        """Create database indexes for performance."""
        if not cls.db:
            return
        
        # Clients collection indexes
        await cls.db.clients.create_index("email", unique=True)
        await cls.db.clients.create_index("is_active")
        await cls.db.clients.create_index("created_at")
        
        # SKUs collection indexes
        await cls.db.skus.create_index("client_id")
        await cls.db.skus.create_index([("client_id", 1), ("sku_id", 1)], unique=True)
        await cls.db.skus.create_index("is_active")
        
        # Campaigns collection indexes
        await cls.db.campaigns.create_index("client_id")
        await cls.db.campaigns.create_index("sku_id")
        await cls.db.campaigns.create_index([("client_id", 1), ("campaign_id", 1)])
        await cls.db.campaigns.create_index("platform")
        await cls.db.campaigns.create_index("status")
        await cls.db.campaigns.create_index("created_at")
        
        # Performance metrics indexes
        await cls.db.performance_metrics.create_index([("campaign_id", 1), ("timestamp", -1)])
        await cls.db.performance_metrics.create_index("client_id")
        await cls.db.performance_metrics.create_index("timestamp")
        await cls.db.performance_metrics.create_index([("client_id", 1), ("timestamp", -1)])
        
        # Intelligence decisions indexes
        await cls.db.intelligence_decisions.create_index([("campaign_id", 1), ("timestamp", -1)])
        await cls.db.intelligence_decisions.create_index("client_id")
        await cls.db.intelligence_decisions.create_index("mode")
        await cls.db.intelligence_decisions.create_index("timestamp")
        
        # System benchmarks indexes
        await cls.db.system_benchmarks.create_index("platform")
        await cls.db.system_benchmarks.create_index("industry")
        await cls.db.system_benchmarks.create_index("timestamp")
        
        logger.info("database_indexes_created")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if not cls.db:
            raise RuntimeError("Database not initialized. Call connect_db() first.")
        return cls.db


# Convenience function for dependency injection
async def get_db() -> AsyncIOMotorDatabase:
    """Get database instance for FastAPI dependency injection."""
    return Database.get_database()
