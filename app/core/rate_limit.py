"""
Rate limiting middleware using Redis.
"""
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
import structlog
import redis

from app.core.config import settings

logger = structlog.get_logger(__name__)


class RateLimiter:
    """
    Rate limiter using Redis sliding window algorithm.
    """
    
    def __init__(self):
        """Initialize rate limiter with Redis connection."""
        if settings.RATE_LIMIT_ENABLED:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
                self.enabled = True
                logger.info("rate_limiter_initialized")
            except Exception as e:
                logger.error("rate_limiter_init_failed", error=str(e))
                self.enabled = False
        else:
            self.enabled = False
            logger.info("rate_limiter_disabled")
    
    async def check_rate_limit(
        self,
        request: Request,
        limit: int = None,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request should be rate limited.
        
        Args:
            request: FastAPI request
            limit: Maximum requests per window (defaults to config)
            window_seconds: Time window in seconds
        
        Returns:
            True if within limit, raises HTTPException if exceeded
        """
        if not self.enabled:
            return True
        
        if limit is None:
            limit = settings.RATE_LIMIT_PER_MINUTE
        
        # Get identifier (client_id from token or IP address)
        identifier = self._get_identifier(request)
        
        try:
            # Create key with window
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window_seconds)
            
            key = f"rate_limit:{identifier}"
            
            # Remove old entries
            self.redis_client.zremrangebyscore(
                key,
                0,
                window_start.timestamp()
            )
            
            # Count requests in current window
            request_count = self.redis_client.zcard(key)
            
            if request_count >= limit:
                # Rate limit exceeded
                logger.warning(
                    "rate_limit_exceeded",
                    identifier=identifier,
                    count=request_count,
                    limit=limit
                )
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {limit} requests per minute.",
                    headers={"Retry-After": str(window_seconds)}
                )
            
            # Add current request
            self.redis_client.zadd(
                key,
                {str(now.timestamp()): now.timestamp()}
            )
            
            # Set expiry on key
            self.redis_client.expire(key, window_seconds)
            
            # Add rate limit headers
            request.state.rate_limit_remaining = limit - request_count - 1
            request.state.rate_limit_limit = limit
            request.state.rate_limit_reset = int((now + timedelta(seconds=window_seconds)).timestamp())
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("rate_limit_check_failed", error=str(e))
            # Fail open - don't block requests if rate limiter fails
            return True
    
    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting."""
        # Try to get client_id from authenticated user
        if hasattr(request.state, "user"):
            return f"client:{request.state.user.get('client_id', 'unknown')}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get first IP in chain
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
