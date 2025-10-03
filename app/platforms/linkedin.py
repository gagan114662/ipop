"""
LinkedIn Ads platform integration client.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog
import httpx

from app.core.config import settings

logger = structlog.get_logger(__name__)


class LinkedInAdsClient:
    """Client for interacting with LinkedIn Marketing API."""
    
    def __init__(self):
        """Initialize LinkedIn Ads client."""
        self.base_url = "https://api.linkedin.com/rest"
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self._initialized = False
    
    async def fetch_campaign_performance(
        self,
        ad_account_id: str,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetch campaign performance metrics from LinkedIn Ads.
        
        Args:
            ad_account_id: LinkedIn Ad Account ID
            campaign_id: Campaign ID
            start_date: Start date for metrics (defaults to 24 hours ago)
            end_date: End date for metrics (defaults to now)
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            if not self.access_token:
                raise ValueError("LinkedIn Ads access token not configured")
            
            # Default date range
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=1)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Convert to LinkedIn timestamps (milliseconds since epoch)
            start_ts = int(start_date.timestamp() * 1000)
            end_ts = int(end_date.timestamp() * 1000)
            
            # Prepare request
            url = f"{self.base_url}/adAnalytics"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            
            params = {
                "q": "analytics",
                "pivot": "CAMPAIGN",
                "dateRange.start.day": start_date.day,
                "dateRange.start.month": start_date.month,
                "dateRange.start.year": start_date.year,
                "dateRange.end.day": end_date.day,
                "dateRange.end.month": end_date.month,
                "dateRange.end.year": end_date.year,
                "campaigns[0]": f"urn:li:sponsoredCampaign:{campaign_id}",
                "fields": "externalWebsiteConversions,clicks,impressions,costInUsd"
            }
            
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
            
            # Parse response
            elements = data.get("elements", [])
            
            if not elements:
                logger.warning("linkedin_no_metrics", campaign_id=campaign_id)
                return self._empty_metrics(campaign_id)
            
            # Aggregate metrics
            total_impressions = 0
            total_clicks = 0
            total_spend = 0.0
            total_conversions = 0
            
            for element in elements:
                total_impressions += element.get("impressions", 0)
                total_clicks += element.get("clicks", 0)
                total_spend += element.get("costInUsd", 0)
                total_conversions += element.get("externalWebsiteConversions", 0)
            
            # Calculate derived metrics
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
            cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            
            # Get campaign details for budget
            campaign_details = await self._get_campaign_details(campaign_id)
            
            metrics = {
                "campaign_id": campaign_id,
                "campaign_name": campaign_details.get("name", "Unknown"),
                "status": campaign_details.get("status", "UNKNOWN"),
                "daily_budget": campaign_details.get("budget", 0),
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "spend": round(total_spend, 2),
                "revenue": round(total_conversions * 100, 2),  # Estimate if not provided
                "ctr": round(ctr, 2),
                "cpc": round(cpc, 2),
                "cpa": round(cpa, 2),
                "cvr": round(cvr, 2),
                "roas": 0.0,  # Calculate if revenue data available
                "timestamp": datetime.utcnow()
            }
            
            logger.info(
                "linkedin_ads_metrics_fetched",
                campaign_id=campaign_id,
                impressions=total_impressions,
                spend=total_spend
            )
            
            return metrics
            
        except Exception as e:
            logger.error(
                "linkedin_ads_fetch_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
    
    async def _get_campaign_details(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign details including budget."""
        try:
            url = f"{self.base_url}/adCampaigns/{campaign_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
            
            budget_amount = 0
            if "dailyBudget" in data:
                budget_amount = data["dailyBudget"].get("amount", 0)
            
            return {
                "name": data.get("name", "Unknown"),
                "status": data.get("status", "UNKNOWN"),
                "budget": budget_amount
            }
            
        except Exception as e:
            logger.error("linkedin_campaign_details_failed", error=str(e))
            return {}
    
    async def update_campaign_budget(
        self,
        campaign_id: str,
        new_budget: float
    ) -> bool:
        """Update campaign daily budget in LinkedIn Ads."""
        try:
            if not self.access_token:
                raise ValueError("LinkedIn Ads access token not configured")
            
            url = f"{self.base_url}/adCampaigns/{campaign_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            
            payload = {
                "patch": {
                    "$set": {
                        "dailyBudget": {
                            "amount": str(new_budget),
                            "currencyCode": "USD"
                        }
                    }
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
            
            logger.info(
                "linkedin_ads_budget_updated",
                campaign_id=campaign_id,
                new_budget=new_budget
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "linkedin_ads_budget_update_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a LinkedIn Ads campaign."""
        try:
            url = f"{self.base_url}/adCampaigns/{campaign_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            
            payload = {
                "patch": {
                    "$set": {
                        "status": "PAUSED"
                    }
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
            
            logger.info("linkedin_ads_campaign_paused", campaign_id=campaign_id)
            return True
            
        except Exception as e:
            logger.error("linkedin_ads_pause_failed", campaign_id=campaign_id, error=str(e))
            raise
    
    async def activate_campaign(self, campaign_id: str) -> bool:
        """Activate a LinkedIn Ads campaign."""
        try:
            url = f"{self.base_url}/adCampaigns/{campaign_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            
            payload = {
                "patch": {
                    "$set": {
                        "status": "ACTIVE"
                    }
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
            
            logger.info("linkedin_ads_campaign_activated", campaign_id=campaign_id)
            return True
            
        except Exception as e:
            logger.error("linkedin_ads_activate_failed", campaign_id=campaign_id, error=str(e))
            raise
    
    def _empty_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Return empty metrics structure."""
        return {
            "campaign_id": campaign_id,
            "campaign_name": "Unknown",
            "status": "UNKNOWN",
            "daily_budget": 0,
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "spend": 0.0,
            "revenue": 0.0,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpa": 0.0,
            "cvr": 0.0,
            "roas": 0.0,
            "timestamp": datetime.utcnow()
        }
    
    def is_configured(self) -> bool:
        """Check if LinkedIn Ads credentials are configured."""
        return bool(settings.LINKEDIN_ACCESS_TOKEN)
