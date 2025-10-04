# # app/services/redis_service.py
# import json
# import logging
# from typing import Optional, Dict, Any

# import redis.asyncio as redis 
# from app.config.settings import settings

# logger = logging.getLogger(__name__)


# class RedisService:
#     def __init__(self):
#         self.redis: Optional[redis.Redis] = None
#         self.queue_name = "resize_jobs"

#     async def connect(self):
#         """Connect to Redis"""
#         try:
#             self.redis = redis.from_url(
#                 settings.REDIS_URL,
#                 db=settings.REDIS_DB,
#                 encoding="utf-8",
#                 decode_responses=True
#             )
#             # Test connection
#             await self.redis.ping()
#             logger.info("✅ Connected to Redis")
#         except Exception as e:
#             logger.error(f"❌ Failed to connect to Redis: {e}")
#             raise

#     async def disconnect(self):
#         """Disconnect from Redis"""
#         if self.redis:
#             await self.redis.close()
#             logger.info("🔌 Disconnected from Redis")

#     async def add_job(self, job_data: dict):
#         """Add a job to the processing queue"""
#         if not self.redis:
#             raise Exception("Redis not connected")
#         await self.redis.lpush(self.queue_name, json.dumps(job_data))
#         logger.info(f"📤 Job {job_data['job_id']} added to Redis queue")

#     async def get_job(self) -> Optional[Dict[str, Any]]:
#         """Get the next job from the queue (blocking)"""
#         if not self.redis:
#             raise Exception("Redis not connected")
#         # Use BRPOP for blocking pop (waits for 5 seconds)
#         result = await self.redis.brpop(self.queue_name, timeout=5)
#         if result:
#             _, job_data_json = result
#             return json.loads(job_data_json)
#         return None



# app/services/redis_service.py
import json
import logging
from typing import Optional, Dict, Any

import redis.asyncio as redis
from app.config.settings import settings

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.queue_name = "resize_jobs"

    async def connect(self):
        """Connect to Redis (Upstash-compatible)"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("🔌 Disconnected from Redis")

    async def add_job(self, job_data: dict):
        """Add a job to the processing queue"""
        if not self.redis:
            raise Exception("Redis not connected")
        await self.redis.lpush(self.queue_name, json.dumps(job_data))
        logger.info(f"📤 Job {job_data.get('job_id', 'unknown')} added to Redis queue")

    async def get_job(self) -> Optional[Dict[str, Any]]:
        """Get the next job from the queue (blocking)"""
        if not self.redis:
            raise Exception("Redis not connected")
        # Use BRPOP for blocking pop (waits for 5 seconds)
        result = await self.redis.brpop(self.queue_name, timeout=5)
        if result:
            _, job_data_json = result
            return json.loads(job_data_json)
        return None
