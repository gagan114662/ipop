"""
TikTok Ads platform integration client.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog
import httpx

from app.core.config import settings

logger = structlog.get_logger(__name__)


class TikTokAdsClient:
    """Client for interacting with TikTok Marketing API."""
    
    def __init__(self):
        """Initialize TikTok Ads client."""
        self.base_url = f"https://business-api.tiktok.com/open_api/{settings.TIKTOK_API_VERSION}"
        self.access_token = settings.TIKTOK_ACCESS_TOKEN
        self._initialized = False
    
    async def fetch_campaign_performance(
        self,
        advertiser_id: str,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetch campaign performance metrics from TikTok Ads.
        
        Args:
            advertiser_id: TikTok Advertiser ID
            campaign_id: Campaign ID
            start_date: Start date for metrics (defaults to 24 hours ago)
            end_date: End date for metrics (defaults to now)
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            if not self.access_token:
                raise ValueError("TikTok Ads access token not configured")
            
            # Default date range
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=settings.METRICS_LOOKBACK_DAYS)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Format dates for TikTok API
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Prepare request
            url = f"{self.base_url}/reports/integrated/get/"
            headers = {
                "Access-Token": self.access_token,
                "Content-Type": "application/json"
            }
            
            payload = {
                "advertiser_id": advertiser_id,
                "service_type": "AUCTION",
                "report_type": "BASIC",
                "data_level": "AUCTION_CAMPAIGN",
                "dimensions": ["campaign_id"],
                "metrics": [
                    "spend",
                    "impressions",
                    "clicks",
                    "conversion",
                    "cost_per_conversion",
                    "ctr",
                    "cpc"
                ],
                "start_date": start_date_str,
                "end_date": end_date_str,
                "filters": [
                    {
                        "field_name": "campaign_id",
                        "filter_type": "IN",
                        "filter_value": [campaign_id]
                    }
                ]
            }
            
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=settings.HTTP_TIMEOUT_SECONDS)
                response.raise_for_status()
                data = response.json()
            
            # Parse response
            if data.get("code") != 0:
                raise Exception(f"TikTok API error: {data.get('message')}")
            
            # Extract metrics
            metrics_data = data.get("data", {}).get("list", [])
            
            if not metrics_data:
                logger.warning("tiktok_no_metrics", campaign_id=campaign_id)
                return self._empty_metrics(campaign_id)
            
            # Aggregate metrics (usually single row for campaign)
            row = metrics_data[0].get("metrics", {})
            dimensions = metrics_data[0].get("dimensions", {})
            
            total_spend = float(row.get("spend", 0))
            total_impressions = int(row.get("impressions", 0))
            total_clicks = int(row.get("clicks", 0))
            total_conversions = int(row.get("conversion", 0))
            
            # Calculate derived metrics
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
            cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            
            # For TikTok, we need to fetch campaign details separately for budget
            campaign_details = await self._get_campaign_details(advertiser_id, campaign_id)
            
            metrics = {
                "campaign_id": campaign_id,
                "campaign_name": campaign_details.get("name", "Unknown"),
                "status": campaign_details.get("status", "UNKNOWN"),
                "daily_budget": campaign_details.get("budget", 0),
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "spend": round(total_spend, 2),
                "revenue": round(total_conversions * 50, 2),  # Estimate if not provided
                "ctr": round(ctr, 2),
                "cpc": round(cpc, 2),
                "cpa": round(cpa, 2),
                "cvr": round(cvr, 2),
                "roas": 0.0,  # Calculate if revenue data available
                "timestamp": datetime.utcnow()
            }
            
            logger.info(
                "tiktok_ads_metrics_fetched",
                campaign_id=campaign_id,
                impressions=total_impressions,
                spend=total_spend
            )
            
            return metrics
            
        except Exception as e:
            logger.error(
                "tiktok_ads_fetch_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
    
    async def _get_campaign_details(
        self,
        advertiser_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """Get campaign details including budget."""
        try:
            url = f"{self.base_url}/campaign/get/"
            headers = {
                "Access-Token": self.access_token,
                "Content-Type": "application/json"
            }
            
            payload = {
                "advertiser_id": advertiser_id,
                "filtering": {
                    "campaign_ids": [campaign_id]
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=payload, headers=headers, timeout=settings.HTTP_TIMEOUT_SECONDS)
                response.raise_for_status()
                data = response.json()
            
            if data.get("code") != 0:
                return {}
            
            campaigns = data.get("data", {}).get("list", [])
            if campaigns:
                campaign = campaigns[0]
                return {
                    "name": campaign.get("campaign_name"),
                    "status": campaign.get("operation_status"),
                    "budget": float(campaign.get("budget", 0))
                }
            
            return {}
            
        except Exception as e:
            logger.error("tiktok_campaign_details_failed", error=str(e))
            return {}
    
    async def update_campaign_budget(
        self,
        advertiser_id: str,
        campaign_id: str,
        new_budget: float
    ) -> bool:
        """Update campaign daily budget in TikTok Ads."""
        try:
            if not self.access_token:
                raise ValueError("TikTok Ads access token not configured")
            
            url = f"{self.base_url}/campaign/update/"
            headers = {
                "Access-Token": self.access_token,
                "Content-Type": "application/json"
            }
            
            payload = {
                "advertiser_id": advertiser_id,
                "campaign_id": campaign_id,
                "budget": new_budget,
                "budget_mode": "BUDGET_MODE_DAY"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=settings.HTTP_TIMEOUT_SECONDS)
                response.raise_for_status()
                data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"TikTok API error: {data.get('message')}")
            
            logger.info(
                "tiktok_ads_budget_updated",
                campaign_id=campaign_id,
                new_budget=new_budget
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "tiktok_ads_budget_update_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
    
    async def pause_campaign(
        self,
        advertiser_id: str,
        campaign_id: str
    ) -> bool:
        """Pause a TikTok Ads campaign."""
        try:
            url = f"{self.base_url}/campaign/update/status/"
            headers = {
                "Access-Token": self.access_token,
                "Content-Type": "application/json"
            }
            
            payload = {
                "advertiser_id": advertiser_id,
                "campaign_ids": [campaign_id],
                "opt_status": "DISABLE"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=settings.HTTP_TIMEOUT_SECONDS)
                response.raise_for_status()
                data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"TikTok API error: {data.get('message')}")
            
            logger.info("tiktok_ads_campaign_paused", campaign_id=campaign_id)
            return True
            
        except Exception as e:
            logger.error("tiktok_ads_pause_failed", campaign_id=campaign_id, error=str(e))
            raise
    
    async def activate_campaign(
        self,
        advertiser_id: str,
        campaign_id: str
    ) -> bool:
        """Activate a TikTok Ads campaign."""
        try:
            url = f"{self.base_url}/campaign/update/status/"
            headers = {
                "Access-Token": self.access_token,
                "Content-Type": "application/json"
            }
            
            payload = {
                "advertiser_id": advertiser_id,
                "campaign_ids": [campaign_id],
                "opt_status": "ENABLE"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=settings.HTTP_TIMEOUT_SECONDS)
                response.raise_for_status()
                data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"TikTok API error: {data.get('message')}")
            
            logger.info("tiktok_ads_campaign_activated", campaign_id=campaign_id)
            return True
            
        except Exception as e:
            logger.error("tiktok_ads_activate_failed", campaign_id=campaign_id, error=str(e))
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
        """Check if TikTok Ads credentials are configured."""
        return bool(settings.TIKTOK_ACCESS_TOKEN)
