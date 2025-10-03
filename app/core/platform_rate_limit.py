"""
Platform API Rate Limiter - Track and enforce platform-specific rate limits.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import structlog
import redis
import asyncio

from app.core.config import settings

logger = structlog.get_logger(__name__)


class PlatformRateLimiter:
    """
    Track and enforce rate limits for advertising platform APIs.
    
    Each platform has different rate limits:
    - Google Ads: 15,000 requests/day
    - Meta: 200 requests/hour per app
    - TikTok: 10,000 requests/hour
    - LinkedIn: 100,000 requests/day
    """
    
    # Platform-specific limits
    LIMITS = {
        "google_ads": {
            "requests_per_day": 15000,
            "requests_per_hour": 625,
            "window_seconds": 3600
        },
        "meta": {
            "requests_per_hour": 200,
            "requests_per_day": 4800,
            "window_seconds": 3600
        },
        "tiktok": {
            "requests_per_hour": 10000,
            "requests_per_day": 240000,
            "window_seconds": 3600
        },
        "linkedin": {
            "requests_per_day": 100000,
            "requests_per_hour": 4166,
            "window_seconds": 3600
        }
    }
    
    def __init__(self):
        """Initialize rate limiter with Redis."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self.enabled = True
            logger.info("platform_rate_limiter_initialized")
        except Exception as e:
            logger.error("platform_rate_limiter_init_failed", error=str(e))
            self.enabled = False
    
    async def check_rate_limit(
        self,
        platform: str,
        operation: str = "api_call"
    ) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            platform: Platform name (google_ads, meta, tiktok, linkedin)
            operation: Operation type (for logging)
        
        Returns:
            True if within limit
        
        Raises:
            Exception if rate limit exceeded
        """
        if not self.enabled:
            return True
        
        platform_lower = platform.lower()
        if platform_lower not in self.LIMITS:
            logger.warning("unknown_platform_rate_limit", platform=platform)
            return True
        
        limits = self.LIMITS[platform_lower]
        now = datetime.utcnow()
        
        # Check hourly limit
        hourly_key = f"platform_rate:{platform_lower}:hour:{now.strftime('%Y-%m-%d-%H')}"
        hourly_count = self.redis_client.get(hourly_key)
        
        if hourly_count and int(hourly_count) >= limits["requests_per_hour"]:
            logger.error(
                "platform_rate_limit_exceeded",
                platform=platform,
                limit="hourly",
                count=hourly_count,
                max=limits["requests_per_hour"]
            )
            raise Exception(
                f"{platform} hourly rate limit exceeded. "
                f"Max {limits['requests_per_hour']}/hour. "
                f"Try again in next hour."
            )
        
        # Check daily limit
        daily_key = f"platform_rate:{platform_lower}:day:{now.strftime('%Y-%m-%d')}"
        daily_count = self.redis_client.get(daily_key)
        
        if daily_count and int(daily_count) >= limits["requests_per_day"]:
            logger.error(
                "platform_rate_limit_exceeded",
                platform=platform,
                limit="daily",
                count=daily_count,
                max=limits["requests_per_day"]
            )
            raise Exception(
                f"{platform} daily rate limit exceeded. "
                f"Max {limits['requests_per_day']}/day. "
                f"Try again tomorrow."
            )
        
        # Increment counters
        pipe = self.redis_client.pipeline()
        
        # Increment hourly
        pipe.incr(hourly_key)
        pipe.expire(hourly_key, 3600)  # 1 hour
        
        # Increment daily
        pipe.incr(daily_key)
        pipe.expire(daily_key, 86400)  # 24 hours
        
        pipe.execute()
        
        new_hourly = int(hourly_count or 0) + 1
        new_daily = int(daily_count or 0) + 1
        
        # Log warnings at 80% threshold
        if new_hourly >= limits["requests_per_hour"] * 0.8:
            logger.warning(
                "platform_rate_limit_approaching",
                platform=platform,
                period="hourly",
                count=new_hourly,
                max=limits["requests_per_hour"],
                percentage=round(new_hourly / limits["requests_per_hour"] * 100, 1)
            )
        
        if new_daily >= limits["requests_per_day"] * 0.8:
            logger.warning(
                "platform_rate_limit_approaching",
                platform=platform,
                period="daily",
                count=new_daily,
                max=limits["requests_per_day"],
                percentage=round(new_daily / limits["requests_per_day"] * 100, 1)
            )
        
        return True
    
    def get_usage_stats(self, platform: str) -> Dict:
        """Get current usage statistics for a platform."""
        if not self.enabled:
            return {}
        
        platform_lower = platform.lower()
        if platform_lower not in self.LIMITS:
            return {}
        
        now = datetime.utcnow()
        limits = self.LIMITS[platform_lower]
        
        hourly_key = f"platform_rate:{platform_lower}:hour:{now.strftime('%Y-%m-%d-%H')}"
        daily_key = f"platform_rate:{platform_lower}:day:{now.strftime('%Y-%m-%d')}"
        
        hourly_count = int(self.redis_client.get(hourly_key) or 0)
        daily_count = int(self.redis_client.get(daily_key) or 0)
        
        return {
            "platform": platform,
            "hourly": {
                "used": hourly_count,
                "limit": limits["requests_per_hour"],
                "remaining": limits["requests_per_hour"] - hourly_count,
                "percentage": round(hourly_count / limits["requests_per_hour"] * 100, 1)
            },
            "daily": {
                "used": daily_count,
                "limit": limits["requests_per_day"],
                "remaining": limits["requests_per_day"] - daily_count,
                "percentage": round(daily_count / limits["requests_per_day"] * 100, 1)
            }
        }
    
    def get_all_usage_stats(self) -> Dict:
        """Get usage stats for all platforms."""
        stats = {}
        for platform in self.LIMITS.keys():
            stats[platform] = self.get_usage_stats(platform)
        return stats
    
    async def wait_if_needed(self, platform: str, max_wait_seconds: int = 300):
        """
        Wait if rate limit is exceeded, up to max_wait_seconds.
        
        Returns True if can proceed, False if max wait exceeded.
        """
        try:
            await self.check_rate_limit(platform)
            return True
        except Exception as e:
            if "hourly" in str(e):
                # Wait until next hour (max 1 hour)
                wait_seconds = min(max_wait_seconds, 3600)
                logger.info(
                    "waiting_for_rate_limit_reset",
                    platform=platform,
                    wait_seconds=wait_seconds
                )
                await asyncio.sleep(wait_seconds)
                return True
            elif "daily" in str(e):
                # Daily limit hit - can't wait
                return False
            return False


# Global instance
_platform_rate_limiter = None


def get_platform_rate_limiter() -> PlatformRateLimiter:
    """Get global platform rate limiter instance."""
    global _platform_rate_limiter
    if _platform_rate_limiter is None:
        _platform_rate_limiter = PlatformRateLimiter()
    return _platform_rate_limiter
