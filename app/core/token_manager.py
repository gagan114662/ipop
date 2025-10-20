"""
Token Manager - Automatic token refresh for platform APIs.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import structlog
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings

logger = structlog.get_logger(__name__)


class TokenManager:
    """
    Manages API tokens with automatic refresh.
    
    Stores token expiration times and automatically refreshes before expiry.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize token manager."""
        self.db = db
    
    async def get_valid_token(
        self,
        platform: str,
        client_id: str
    ) -> Optional[str]:
        """
        Get a valid token for a platform, refreshing if needed.
        
        Args:
            platform: Platform name (google_ads, meta, tiktok, linkedin)
            client_id: Client identifier
        
        Returns:
            Valid access token or None
        """
        # Get token from database
        token_doc = await self.db.platform_tokens.find_one({
            "client_id": client_id,
            "platform": platform
        })
        
        if not token_doc:
            logger.warning("no_token_found", platform=platform, client_id=client_id)
            return None
        
        # Check if token needs refresh
        expires_at = token_doc.get("expires_at")
        refresh_token = token_doc.get("refresh_token")
        
        if expires_at:
            # Refresh if expires within configured buffer time
            if datetime.utcnow() + timedelta(minutes=settings.TOKEN_REFRESH_BUFFER_MINUTES) >= expires_at:
                logger.info("token_needs_refresh", platform=platform)
                
                if refresh_token:
                    new_token = await self._refresh_token(
                        platform=platform,
                        refresh_token=refresh_token
                    )
                    
                    if new_token:
                        # Update database with new token
                        await self.db.platform_tokens.update_one(
                            {"_id": token_doc["_id"]},
                            {
                                "$set": {
                                    "access_token": new_token["access_token"],
                                    "expires_at": new_token["expires_at"],
                                    "updated_at": datetime.utcnow()
                                }
                            }
                        )
                        return new_token["access_token"]
                    else:
                        logger.error("token_refresh_failed", platform=platform)
                        return None
        
        return token_doc.get("access_token")
    
    async def _refresh_token(
        self,
        platform: str,
        refresh_token: str
    ) -> Optional[Dict]:
        """
        Refresh an expired token.
        
        Args:
            platform: Platform name
            refresh_token: Refresh token
        
        Returns:
            Dict with new access_token and expires_at, or None
        """
        try:
            if platform == "google_ads":
                return await self._refresh_google_ads_token(refresh_token)
            elif platform == "meta":
                return await self._refresh_meta_token(refresh_token)
            elif platform == "tiktok":
                return await self._refresh_tiktok_token(refresh_token)
            elif platform == "linkedin":
                return await self._refresh_linkedin_token(refresh_token)
            
            return None
            
        except Exception as e:
            logger.error("token_refresh_error", platform=platform, error=str(e))
            return None
    
    async def _refresh_google_ads_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh Google Ads OAuth token."""
        import httpx
        
        url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": settings.GOOGLE_ADS_CLIENT_ID,
            "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "access_token": result["access_token"],
                    "expires_at": datetime.utcnow() + timedelta(seconds=result.get("expires_in", 3600))
                }
        
        return None
    
    async def _refresh_meta_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh Meta long-lived token."""
        import httpx
        
        url = f"https://graph.facebook.com/{settings.META_API_VERSION}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": settings.META_APP_ID,
            "client_secret": settings.META_APP_SECRET,
            "fb_exchange_token": refresh_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "access_token": result["access_token"],
                    "expires_at": datetime.utcnow() + timedelta(seconds=result.get("expires_in", 5184000))  # 60 days
                }
        
        return None
    
    async def _refresh_tiktok_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh TikTok token."""
        # TikTok token refresh implementation
        # This depends on TikTok's specific OAuth flow
        logger.warning("tiktok_token_refresh_not_implemented")
        return None
    
    async def _refresh_linkedin_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh LinkedIn token."""
        import httpx
        
        url = f"https://www.linkedin.com/oauth/{settings.LINKEDIN_API_VERSION}/accessToken"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "access_token": result["access_token"],
                    "expires_at": datetime.utcnow() + timedelta(seconds=result.get("expires_in", 5184000))
                }
        
        return None
    
    async def store_token(
        self,
        platform: str,
        client_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: int = 3600
    ):
        """
        Store a platform token in the database.
        
        Args:
            platform: Platform name
            client_id: Client identifier
            access_token: Access token
            refresh_token: Refresh token (optional)
            expires_in: Token lifetime in seconds
        """
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        await self.db.platform_tokens.update_one(
            {"client_id": client_id, "platform": platform},
            {
                "$set": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_at": expires_at,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        logger.info("token_stored", platform=platform, client_id=client_id)
