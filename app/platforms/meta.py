"""
Meta (Facebook/Instagram) Ads platform integration client.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog
import httpx
import os

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative

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
                start_date = datetime.utcnow() - timedelta(days=settings.METRICS_LOOKBACK_DAYS)
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
        # Read directly from environment to support testing with patched env vars
        return all([
            os.getenv('META_APP_ID'),
            os.getenv('META_APP_SECRET'),
            os.getenv('META_ACCESS_TOKEN')
        ])

    async def fetch_creative_performance(
        self,
        ad_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetch creative performance metrics from Meta Ads.

        Args:
            ad_id: Meta Ad ID (which contains the creative)
            start_date: Start date for metrics (defaults to 24 hours ago)
            end_date: End date for metrics (defaults to now)

        Returns:
            Dictionary with creative performance metrics including:
            - Volume metrics (impressions, clicks, conversions)
            - Efficiency metrics (CTR, CPC, ROAS)
            - Social engagement (likes, shares, comments)
            - Video metrics (if video creative)
        """
        try:
            self._get_api()

            # Default date range
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=settings.METRICS_LOOKBACK_DAYS)
            if not end_date:
                end_date = datetime.utcnow()

            # Format dates for Meta API
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            # Get ad object
            ad = Ad(ad_id)

            # Define fields to fetch (including creative-specific metrics)
            fields = [
                'ad_name',
                'impressions',
                'clicks',
                'spend',
                'actions',
                'action_values',
                'ctr',
                'cpc',
                'cpm',
                'cpp',
                # Social engagement
                'post_engagement',
                'post_reactions',
                'post_shares',
                'post_comments',
                'post_saves',
                # Video metrics
                'video_play_actions',
                'video_p25_watched_actions',
                'video_p50_watched_actions',
                'video_p75_watched_actions',
                'video_p100_watched_actions',
                'video_avg_time_watched_actions',
                # Quality metrics
                'relevance_score',
                'frequency'
            ]

            # Define parameters
            params = {
                'time_range': {
                    'since': start_date_str,
                    'until': end_date_str
                },
                'level': 'ad',
                'breakdowns': []
            }

            # Fetch insights
            insights = ad.get_insights(
                fields=fields,
                params=params
            )

            # Process insights
            total_impressions = 0
            total_clicks = 0
            total_spend = 0.0
            total_conversions = 0
            total_revenue = 0.0
            ad_name = None

            # Social engagement
            total_likes = 0
            total_shares = 0
            total_comments = 0
            total_saves = 0

            # Video metrics
            video_views = 0
            video_views_25 = 0
            video_views_50 = 0
            video_views_75 = 0
            video_views_100 = 0
            avg_watch_time = 0.0

            # Quality
            relevance_score = 0.0
            frequency = 0.0

            for insight in insights:
                ad_name = insight.get('ad_name', '')
                total_impressions += int(insight.get('impressions', 0))
                total_clicks += int(insight.get('clicks', 0))
                total_spend += float(insight.get('spend', 0))

                # Extract conversions
                actions = insight.get('actions', [])
                for action in actions:
                    action_type = action.get('action_type', '')
                    value = int(action.get('value', 0))

                    if action_type in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                        total_conversions += value
                    elif action_type == 'post_reaction':
                        total_likes += value
                    elif action_type == 'post':
                        total_shares += value
                    elif action_type == 'comment':
                        total_comments += value
                    elif action_type == 'post_save':
                        total_saves += value

                # Extract revenue
                action_values = insight.get('action_values', [])
                for action_value in action_values:
                    if action_value.get('action_type') in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                        total_revenue += float(action_value.get('value', 0))

                # Extract video metrics
                video_play = insight.get('video_play_actions', [])
                if video_play:
                    video_views += int(video_play[0].get('value', 0))

                video_p25 = insight.get('video_p25_watched_actions', [])
                if video_p25:
                    video_views_25 += int(video_p25[0].get('value', 0))

                video_p50 = insight.get('video_p50_watched_actions', [])
                if video_p50:
                    video_views_50 += int(video_p50[0].get('value', 0))

                video_p75 = insight.get('video_p75_watched_actions', [])
                if video_p75:
                    video_views_75 += int(video_p75[0].get('value', 0))

                video_p100 = insight.get('video_p100_watched_actions', [])
                if video_p100:
                    video_views_100 += int(video_p100[0].get('value', 0))

                video_avg_time = insight.get('video_avg_time_watched_actions', [])
                if video_avg_time:
                    avg_watch_time = float(video_avg_time[0].get('value', 0))

                # Quality metrics
                relevance = insight.get('relevance_score', {})
                if isinstance(relevance, dict):
                    relevance_score = float(relevance.get('score', 0))

                frequency = float(insight.get('frequency', 0))

            # Calculate derived metrics
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
            cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
            cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            roas = (total_revenue / total_spend) if total_spend > 0 else 0

            # Calculate engagement rate
            total_engagements = total_likes + total_shares + total_comments + total_saves
            engagement_rate = (total_engagements / total_impressions * 100) if total_impressions > 0 else 0

            metrics = {
                "ad_id": ad_id,
                "ad_name": ad_name or "Unknown",

                # Volume metrics
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "spend": round(total_spend, 2),
                "revenue": round(total_revenue, 2),

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
                "saves": total_saves,
                "engagement_rate": round(engagement_rate, 2),

                # Video metrics
                "video_views": video_views,
                "video_views_25": video_views_25,
                "video_views_50": video_views_50,
                "video_views_75": video_views_75,
                "video_views_100": video_views_100,
                "avg_watch_time": round(avg_watch_time, 2),

                # Quality indicators
                "relevance_score": round(relevance_score, 2),
                "frequency": round(frequency, 2),

                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().date()
            }

            logger.info(
                "meta_creative_metrics_fetched",
                ad_id=ad_id,
                impressions=total_impressions,
                ctr=ctr,
                engagement_rate=engagement_rate
            )

            return metrics

        except Exception as e:
            logger.error(
                "meta_creative_fetch_failed",
                ad_id=ad_id,
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
            campaign_id: Meta Campaign ID
            start_date: Start date for metrics
            end_date: End date for metrics

        Returns:
            List of creative performance dictionaries
        """
        try:
            self._get_api()

            # Get campaign object
            campaign = Campaign(campaign_id)

            # Get all ads in the campaign
            ads = campaign.get_ads(fields=['id', 'name', 'creative'])

            creative_metrics = []

            for ad in ads:
                try:
                    metrics = await self.fetch_creative_performance(
                        ad_id=ad['id'],
                        start_date=start_date,
                        end_date=end_date
                    )

                    # Add creative ID
                    creative = ad.get('creative', {})
                    metrics['platform_creative_id'] = creative.get('id', '')

                    creative_metrics.append(metrics)

                except Exception as e:
                    logger.warning(
                        "meta_creative_fetch_skipped",
                        ad_id=ad['id'],
                        error=str(e)
                    )
                    continue

            logger.info(
                "meta_campaign_creatives_fetched",
                campaign_id=campaign_id,
                creative_count=len(creative_metrics)
            )

            return creative_metrics

        except Exception as e:
            logger.error(
                "meta_campaign_creatives_fetch_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
