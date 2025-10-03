"""
Platform Manager - Unified interface for all advertising platforms.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

from app.models.campaign import Platform
from app.platforms.google_ads import GoogleAdsClient
from app.platforms.meta import MetaAdsClient
from app.platforms.tiktok import TikTokAdsClient
from app.platforms.linkedin import LinkedInAdsClient

logger = structlog.get_logger(__name__)


class PlatformManager:
    """
    Unified manager for all advertising platform integrations.
    
    Provides a single interface to interact with Google Ads, Meta, TikTok, and LinkedIn.
    """
    
    def __init__(self):
        """Initialize platform clients."""
        self.google_ads = GoogleAdsClient()
        self.meta = MetaAdsClient()
        self.tiktok = TikTokAdsClient()
        self.linkedin = LinkedInAdsClient()
        
        self._clients = {
            Platform.GOOGLE_ADS: self.google_ads,
            Platform.META: self.meta,
            Platform.TIKTOK: self.tiktok,
            Platform.LINKEDIN: self.linkedin
        }
    
    def get_client(self, platform: Platform):
        """Get client for specific platform."""
        return self._clients.get(platform)
    
    def is_platform_configured(self, platform: Platform) -> bool:
        """Check if platform credentials are configured."""
        client = self.get_client(platform)
        if client:
            return client.is_configured()
        return False
    
    async def fetch_metrics(
        self,
        platform: Platform,
        campaign: Dict[str, Any],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch performance metrics for a campaign.
        
        Args:
            platform: Advertising platform
            campaign: Campaign object with platform-specific IDs
            start_date: Start date for metrics
            end_date: End date for metrics
        
        Returns:
            Dictionary with performance metrics or None if platform not configured
        """
        client = self.get_client(platform)
        
        if not client or not client.is_configured():
            logger.warning(
                "platform_not_configured",
                platform=platform.value,
                campaign_id=campaign.get("campaign_id")
            )
            return None
        
        try:
            platform_campaign_id = campaign.get("platform_campaign_id")
            metadata = campaign.get("metadata", {})
            
            if platform == Platform.GOOGLE_ADS:
                customer_id = metadata.get("customer_id")
                if not customer_id:
                    logger.error("google_ads_customer_id_missing", campaign_id=campaign.get("campaign_id"))
                    return None
                
                return await client.fetch_campaign_performance(
                    customer_id=customer_id,
                    campaign_id=platform_campaign_id,
                    start_date=start_date,
                    end_date=end_date
                )
            
            elif platform == Platform.META:
                ad_account_id = metadata.get("ad_account_id")
                if not ad_account_id:
                    logger.error("meta_ad_account_id_missing", campaign_id=campaign.get("campaign_id"))
                    return None
                
                return await client.fetch_campaign_performance(
                    ad_account_id=ad_account_id,
                    campaign_id=platform_campaign_id,
                    start_date=start_date,
                    end_date=end_date
                )
            
            elif platform == Platform.TIKTOK:
                advertiser_id = metadata.get("advertiser_id")
                if not advertiser_id:
                    logger.error("tiktok_advertiser_id_missing", campaign_id=campaign.get("campaign_id"))
                    return None
                
                return await client.fetch_campaign_performance(
                    advertiser_id=advertiser_id,
                    campaign_id=platform_campaign_id,
                    start_date=start_date,
                    end_date=end_date
                )
            
            elif platform == Platform.LINKEDIN:
                ad_account_id = metadata.get("ad_account_id")
                if not ad_account_id:
                    logger.error("linkedin_ad_account_id_missing", campaign_id=campaign.get("campaign_id"))
                    return None
                
                return await client.fetch_campaign_performance(
                    ad_account_id=ad_account_id,
                    campaign_id=platform_campaign_id,
                    start_date=start_date,
                    end_date=end_date
                )
            
            return None
            
        except Exception as e:
            logger.error(
                "platform_fetch_failed",
                platform=platform.value,
                campaign_id=campaign.get("campaign_id"),
                error=str(e)
            )
            return None
    
    async def update_budget(
        self,
        platform: Platform,
        campaign: Dict[str, Any],
        new_budget: float
    ) -> bool:
        """
        Update campaign budget on the platform.
        
        Args:
            platform: Advertising platform
            campaign: Campaign object with platform-specific IDs
            new_budget: New daily budget in USD
        
        Returns:
            True if successful, False otherwise
        """
        client = self.get_client(platform)
        
        if not client or not client.is_configured():
            logger.warning(
                "platform_not_configured_for_update",
                platform=platform.value,
                campaign_id=campaign.get("campaign_id")
            )
            return False
        
        try:
            platform_campaign_id = campaign.get("platform_campaign_id")
            metadata = campaign.get("metadata", {})
            
            if platform == Platform.GOOGLE_ADS:
                customer_id = metadata.get("customer_id")
                return await client.update_campaign_budget(
                    customer_id=customer_id,
                    campaign_id=platform_campaign_id,
                    new_budget=new_budget
                )
            
            elif platform == Platform.META:
                return await client.update_campaign_budget(
                    campaign_id=platform_campaign_id,
                    new_budget=new_budget
                )
            
            elif platform == Platform.TIKTOK:
                advertiser_id = metadata.get("advertiser_id")
                return await client.update_campaign_budget(
                    advertiser_id=advertiser_id,
                    campaign_id=platform_campaign_id,
                    new_budget=new_budget
                )
            
            elif platform == Platform.LINKEDIN:
                return await client.update_campaign_budget(
                    campaign_id=platform_campaign_id,
                    new_budget=new_budget
                )
            
            return False
            
        except Exception as e:
            logger.error(
                "platform_budget_update_failed",
                platform=platform.value,
                campaign_id=campaign.get("campaign_id"),
                error=str(e)
            )
            return False
    
    async def pause_campaign(
        self,
        platform: Platform,
        campaign: Dict[str, Any]
    ) -> bool:
        """Pause campaign on the platform."""
        client = self.get_client(platform)
        
        if not client or not client.is_configured():
            return False
        
        try:
            platform_campaign_id = campaign.get("platform_campaign_id")
            metadata = campaign.get("metadata", {})
            
            if platform == Platform.GOOGLE_ADS:
                customer_id = metadata.get("customer_id")
                return await client.pause_campaign(customer_id, platform_campaign_id)
            elif platform == Platform.META:
                return await client.pause_campaign(platform_campaign_id)
            elif platform == Platform.TIKTOK:
                advertiser_id = metadata.get("advertiser_id")
                return await client.pause_campaign(advertiser_id, platform_campaign_id)
            elif platform == Platform.LINKEDIN:
                return await client.pause_campaign(platform_campaign_id)
            
            return False
            
        except Exception as e:
            logger.error("platform_pause_failed", error=str(e))
            return False
    
    async def activate_campaign(
        self,
        platform: Platform,
        campaign: Dict[str, Any]
    ) -> bool:
        """Activate campaign on the platform."""
        client = self.get_client(platform)
        
        if not client or not client.is_configured():
            return False
        
        try:
            platform_campaign_id = campaign.get("platform_campaign_id")
            metadata = campaign.get("metadata", {})
            
            if platform == Platform.GOOGLE_ADS:
                customer_id = metadata.get("customer_id")
                return await client.activate_campaign(customer_id, platform_campaign_id)
            elif platform == Platform.META:
                return await client.activate_campaign(platform_campaign_id)
            elif platform == Platform.TIKTOK:
                advertiser_id = metadata.get("advertiser_id")
                return await client.activate_campaign(advertiser_id, platform_campaign_id)
            elif platform == Platform.LINKEDIN:
                return await client.activate_campaign(platform_campaign_id)
            
            return False
            
        except Exception as e:
            logger.error("platform_activate_failed", error=str(e))
            return False
    
    def get_configured_platforms(self) -> list[Platform]:
        """Get list of configured platforms."""
        configured = []
        for platform, client in self._clients.items():
            if client.is_configured():
                configured.append(platform)
        return configured
