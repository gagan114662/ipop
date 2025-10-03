"""
Meta (Facebook/Instagram) Ads platform integration client.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog
import httpx

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adsinsights import AdsInsights

from app.core.config import settings

logger = structlog.get_logger(__name__)


class MetaAdsClient:
    """Client for interacting with Meta Marketing API."""
    
    def __init__(self):
        """Initialize Meta Ads client."""
        self._api = None
        self._initialized = False
    
    def _get_api(self) -> FacebookAdsApi:
        """Get or create Meta Ads API instance."""
        if not self._api:
            if not all([
                settings.META_APP_ID,
                settings.META_APP_SECRET,
                settings.META_ACCESS_TOKEN
            ]):
                raise ValueError("Meta Ads credentials not configured")
            
            self._api = FacebookAdsApi.init(
                app_id=settings.META_APP_ID,
                app_secret=settings.META_APP_SECRET,
                access_token=settings.META_ACCESS_TOKEN
            )
            self._initialized = True
            logger.info("meta_ads_client_initialized")
        
        return self._api
    
    async def fetch_campaign_performance(
        self,
        ad_account_id: str,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetch campaign performance metrics from Meta Ads.
        
        Args:
            ad_account_id: Meta Ad Account ID (e.g., "act_123456789")
            campaign_id: Campaign ID
            start_date: Start date for metrics (defaults to 24 hours ago)
            end_date: End date for metrics (defaults to now)
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            self._get_api()
            
            # Default date range
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=1)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Format dates for Meta API
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Get campaign object
            campaign = Campaign(campaign_id)
            
            # Define fields to fetch
            fields = [
                'campaign_name',
                'impressions',
                'clicks',
                'spend',
                'actions',
                'action_values',
                'ctr',
                'cpc',
                'cpm',
                'cpp'
            ]
            
            # Define parameters
            params = {
                'time_range': {
                    'since': start_date_str,
                    'until': end_date_str
                },
                'level': 'campaign',
                'breakdowns': []
            }
            
            # Fetch insights
            insights = campaign.get_insights(
                fields=fields,
                params=params
            )
            
            # Process insights
            total_impressions = 0
            total_clicks = 0
            total_spend = 0.0
            total_conversions = 0
            total_revenue = 0.0
            campaign_name = None
            
            for insight in insights:
                campaign_name = insight.get('campaign_name', '')
                total_impressions += int(insight.get('impressions', 0))
                total_clicks += int(insight.get('clicks', 0))
                total_spend += float(insight.get('spend', 0))
                
                # Extract conversions
                actions = insight.get('actions', [])
                for action in actions:
                    if action.get('action_type') in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                        total_conversions += int(action.get('value', 0))
                
                # Extract revenue
                action_values = insight.get('action_values', [])
                for action_value in action_values:
                    if action_value.get('action_type') in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                        total_revenue += float(action_value.get('value', 0))
            
            # Calculate derived metrics
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
            cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            roas = (total_revenue / total_spend) if total_spend > 0 else 0
            
            # Get campaign details for budget
            campaign_details = campaign.api_get(fields=['daily_budget', 'status'])
            daily_budget = float(campaign_details.get('daily_budget', 0)) / 100  # Meta stores in cents
            
            metrics = {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name or "Unknown",
                "status": campaign_details.get('status', 'UNKNOWN'),
                "daily_budget": daily_budget,
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "spend": round(total_spend, 2),
                "revenue": round(total_revenue, 2),
                "ctr": round(ctr, 2),
                "cpc": round(cpc, 2),
                "cpa": round(cpa, 2),
                "cvr": round(cvr, 2),
                "roas": round(roas, 2),
                "timestamp": datetime.utcnow()
            }
            
            logger.info(
                "meta_ads_metrics_fetched",
                campaign_id=campaign_id,
                impressions=total_impressions,
                spend=total_spend
            )
            
            return metrics
            
        except Exception as e:
            logger.error(
                "meta_ads_fetch_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
    
    async def update_campaign_budget(
        self,
        campaign_id: str,
        new_budget: float
    ) -> bool:
        """
        Update campaign daily budget in Meta Ads.
        
        Args:
            campaign_id: Campaign ID to update
            new_budget: New daily budget in USD
        
        Returns:
            True if successful
        """
        try:
            self._get_api()
            
            # Convert to cents (Meta stores budget in cents)
            budget_cents = int(new_budget * 100)
            
            # Get campaign object
            campaign = Campaign(campaign_id)
            
            # Update budget
            campaign.api_update(params={
                'daily_budget': budget_cents
            })
            
            logger.info(
                "meta_ads_budget_updated",
                campaign_id=campaign_id,
                new_budget=new_budget,
                budget_cents=budget_cents
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "meta_ads_budget_update_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause a Meta Ads campaign."""
        try:
            self._get_api()
            
            campaign = Campaign(campaign_id)
            campaign.api_update(params={
                'status': Campaign.Status.paused
            })
            
            logger.info("meta_ads_campaign_paused", campaign_id=campaign_id)
            return True
            
        except Exception as e:
            logger.error("meta_ads_pause_failed", campaign_id=campaign_id, error=str(e))
            raise
    
    async def activate_campaign(self, campaign_id: str) -> bool:
        """Activate a Meta Ads campaign."""
        try:
            self._get_api()
            
            campaign = Campaign(campaign_id)
            campaign.api_update(params={
                'status': Campaign.Status.active
            })
            
            logger.info("meta_ads_campaign_activated", campaign_id=campaign_id)
            return True
            
        except Exception as e:
            logger.error("meta_ads_activate_failed", campaign_id=campaign_id, error=str(e))
            raise
    
    def is_configured(self) -> bool:
        """Check if Meta Ads credentials are configured."""
        return all([
            settings.META_APP_ID,
            settings.META_APP_SECRET,
            settings.META_ACCESS_TOKEN
        ])
