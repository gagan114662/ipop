# app/services/mongodb_service.py
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings

logger = logging.getLogger(__name__)


class MongoDBService:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection_name = "resize_jobs"

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DB]

            # Test connection
            await self.client.admin.command('ping')

            # Create index on status and timestamp for efficient queries
            await self.db[self.collection_name].create_index([
                ("status", 1),
                ("timestamp", 1)
            ])

            logger.info("✅ Connected to MongoDB")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("🔌 Disconnected from MongoDB")

    async def add_job(self, job_data: dict):
        """Add a job to the processing queue"""
        if not self.db:
            raise Exception("MongoDB not connected")

        # Add status and timestamp for queue management
        job_document = {
            **job_data,
            "status": "PENDING",
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }

        result = await self.db[self.collection_name].insert_one(job_document)
        logger.info(f"📤 Job {job_data.get('job_id', 'unknown')} added to MongoDB queue")
        return result.inserted_id

    async def get_job(self) -> Optional[Dict[str, Any]]:
        """Get the next job from the queue (FIFO with atomic update)"""
        if not self.db:
            raise Exception("MongoDB not connected")

        # Use findOneAndUpdate to atomically get and mark job as processing
        # This ensures no two workers pick up the same job
        result = await self.db[self.collection_name].find_one_and_update(
            {"status": "PENDING"},
            {
                "$set": {
                    "status": "PROCESSING",
                    "processing_started_at": datetime.utcnow()
                }
            },
            sort=[("timestamp", 1)],  # FIFO - oldest first
            return_document=True
        )

        if result:
            # Remove MongoDB's _id field before returning
            result.pop('_id', None)
            logger.info(f"📥 Job {result.get('job_id', 'unknown')} retrieved from MongoDB queue")
            return result

        return None

    async def get_pending_job_count(self) -> int:
        """Get count of pending jobs in queue"""
        if not self.db:
            raise Exception("MongoDB not connected")

        count = await self.db[self.collection_name].count_documents({"status": "PENDING"})
        return count

    async def mark_job_completed(self, job_id: str):
        """Mark a job as completed"""
        if not self.db:
            raise Exception("MongoDB not connected")

        await self.db[self.collection_name].update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "COMPLETED",
                    "completed_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"✅ Job {job_id} marked as completed in MongoDB")

    async def mark_job_failed(self, job_id: str, error: str):
        """Mark a job as failed"""
        if not self.db:
            raise Exception("MongoDB not connected")

        await self.db[self.collection_name].update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "FAILED",
                    "error": error,
                    "failed_at": datetime.utcnow()
                }
            }
        )
        logger.error(f"❌ Job {job_id} marked as failed in MongoDB: {error}")

    async def cleanup_old_jobs(self, days: int = 7):
        """Clean up completed/failed jobs older than specified days"""
        if not self.db:
            raise Exception("MongoDB not connected")

        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await self.db[self.collection_name].delete_many({
            "status": {"$in": ["COMPLETED", "FAILED"]},
            "timestamp": {"$lt": cutoff_date}
        })

        logger.info(f"🧹 Cleaned up {result.deleted_count} old jobs from MongoDB")
        return result.deleted_count
