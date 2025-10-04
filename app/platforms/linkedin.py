"""
LinkedIn Ads platform integration client.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog
import httpx
import os

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
        # Read directly from environment to support testing with patched env vars
        return bool(os.getenv('LINKEDIN_ACCESS_TOKEN'))

    async def fetch_creative_performance(
        self,
        creative_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetch creative performance metrics from LinkedIn Ads.

        Args:
            creative_id: LinkedIn Creative ID
            start_date: Start date for metrics (defaults to 24 hours ago)
            end_date: End date for metrics (defaults to now)

        Returns:
            Dictionary with creative performance metrics
        """
        try:
            if not self.access_token:
                raise ValueError("LinkedIn Ads access token not configured")

            # Default date range
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=1)
            if not end_date:
                end_date = datetime.utcnow()

            # Prepare request
            url = f"{self.base_url}/adAnalytics"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }

            params = {
                "q": "analytics",
                "pivot": "CREATIVE",
                "dateRange.start.day": start_date.day,
                "dateRange.start.month": start_date.month,
                "dateRange.start.year": start_date.year,
                "dateRange.end.day": end_date.day,
                "dateRange.end.month": end_date.month,
                "dateRange.end.year": end_date.year,
                "creatives[0]": f"urn:li:sponsoredCreative:{creative_id}",
                "fields": "externalWebsiteConversions,clicks,impressions,costInUsd," \
                         "likes,comments,shares,follows,videoViews,videoCompletions"
            }

            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()

            # Parse response
            elements = data.get("elements", [])

            if not elements:
                logger.warning("linkedin_creative_no_metrics", creative_id=creative_id)
                return self._empty_creative_metrics(creative_id)

            # Aggregate metrics
            total_impressions = 0
            total_clicks = 0
            total_conversions = 0
            total_spend = 0.0

            # Social engagement
            total_likes = 0
            total_shares = 0
            total_comments = 0
            total_follows = 0

            # Video metrics
            total_video_views = 0
            total_video_completions = 0

            for element in elements:
                total_impressions += element.get("impressions", 0)
                total_clicks += element.get("clicks", 0)
                total_conversions += element.get("externalWebsiteConversions", 0)
                total_spend += element.get("costInUsd", 0)

                total_likes += element.get("likes", 0)
                total_shares += element.get("shares", 0)
                total_comments += element.get("comments", 0)
                total_follows += element.get("follows", 0)

                total_video_views += element.get("videoViews", 0)
                total_video_completions += element.get("videoCompletions", 0)

            # Calculate derived metrics
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
            cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
            cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0

            # Engagement rate
            total_engagements = total_likes + total_shares + total_comments + total_follows
            engagement_rate = (total_engagements / total_impressions * 100) if total_impressions > 0 else 0

            # Video completion rate
            video_completion_rate = (total_video_completions / total_video_views * 100) if total_video_views > 0 else 0

            # Estimate revenue (if not provided)
            revenue = total_conversions * 100  # Placeholder estimate

            roas = (revenue / total_spend) if total_spend > 0 else 0

            metrics = {
                "creative_id": creative_id,
                "creative_name": f"Creative {creative_id}",  # LinkedIn doesn't return name in analytics

                # Volume metrics
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "spend": round(total_spend, 2),
                "revenue": round(revenue, 2),

                # Efficiency metrics
                "ctr": round(ctr, 2),
                "cpc": round(cpc, 2),
                "cpm": round(cpm, 2),
                "cpa": round(cpa, 2),
                "cvr": round(cvr, 2),
                "roas": round(roas, 2),

                # Social engagement
                "likes": total_likes,
                "shares": total_shares,
                "comments": total_comments,
                "saves": 0,  # Not available
                "follows": total_follows,
                "engagement_rate": round(engagement_rate, 2),

                # Video metrics
                "video_views": total_video_views,
                "video_views_25": 0,  # Not directly available
                "video_views_50": 0,
                "video_views_75": 0,
                "video_views_100": total_video_completions,
                "video_completion_rate": round(video_completion_rate, 2),
                "avg_watch_time": 0.0,  # Not available

                # Quality indicators
                "relevance_score": 0.0,  # Not available
                "frequency": 0.0,  # Not available at creative level

                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().date()
            }

            logger.info(
                "linkedin_creative_metrics_fetched",
                creative_id=creative_id,
                impressions=total_impressions,
                ctr=ctr,
                engagement_rate=engagement_rate
            )

            return metrics

        except Exception as e:
            logger.error(
                "linkedin_creative_fetch_failed",
                creative_id=creative_id,
                error=str(e)
            )
            raise

    async def fetch_all_creatives_in_campaign(
        self,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[Dict[str, Any]]:
        """
        Fetch performance metrics for all creatives in a campaign.

        Args:
            campaign_id: LinkedIn Campaign ID
            start_date: Start date for metrics
            end_date: End date for metrics

        Returns:
            List of creative performance dictionaries
        """
        try:
            if not self.access_token:
                raise ValueError("LinkedIn Ads access token not configured")

            # Get all creatives for campaign
            url = f"{self.base_url}/adCreatives"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            params = {
                "q": "search",
                "search.campaign.values[0]": f"urn:li:sponsoredCampaign:{campaign_id}",
                "count": 100
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()

            elements = data.get("elements", [])

            creative_metrics = []

            for element in elements:
                # Extract creative ID from URN
                creative_urn = element.get("id", "")
                creative_id = creative_urn.split(":")[-1] if creative_urn else None

                if not creative_id:
                    continue

                try:
                    metrics = await self.fetch_creative_performance(
                        creative_id=creative_id,
                        start_date=start_date,
                        end_date=end_date
                    )

                    metrics['platform_creative_id'] = creative_id
                    creative_metrics.append(metrics)

                except Exception as e:
                    logger.warning(
                        "linkedin_creative_fetch_skipped",
                        creative_id=creative_id,
                        error=str(e)
                    )
                    continue

            logger.info(
                "linkedin_campaign_creatives_fetched",
                campaign_id=campaign_id,
                creative_count=len(creative_metrics)
            )

            return creative_metrics

        except Exception as e:
            logger.error(
                "linkedin_campaign_creatives_fetch_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise

    def _empty_creative_metrics(self, creative_id: str) -> Dict[str, Any]:
        """Return empty creative metrics structure."""
        return {
            "creative_id": creative_id,
            "creative_name": "Unknown",
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "spend": 0.0,
            "revenue": 0.0,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpm": 0.0,
            "cpa": 0.0,
            "cvr": 0.0,
            "roas": 0.0,
            "likes": 0,
            "shares": 0,
            "comments": 0,
            "saves": 0,
            "follows": 0,
            "engagement_rate": 0.0,
            "video_views": 0,
            "video_views_25": 0,
            "video_views_50": 0,
            "video_views_75": 0,
            "video_views_100": 0,
            "video_completion_rate": 0.0,
            "avg_watch_time": 0.0,
            "relevance_score": 0.0,
            "frequency": 0.0,
            "timestamp": datetime.utcnow(),
            "date": datetime.utcnow().date()
        }
