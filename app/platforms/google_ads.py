"""
Google Ads platform integration client.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import structlog
import os

from google.ads.googleads.client import GoogleAdsClient as GoogleClient
from google.ads.googleads.errors import GoogleAdsException

from app.core.config import settings

logger = structlog.get_logger(__name__)


class GoogleAdsClient:
    """Client for interacting with Google Ads API."""
    
    def __init__(self):
        """Initialize Google Ads client."""
        self.credentials = {
            'developer_token': settings.GOOGLE_ADS_DEVELOPER_TOKEN,
            'client_id': settings.GOOGLE_ADS_CLIENT_ID,
            'client_secret': settings.GOOGLE_ADS_CLIENT_SECRET,
            'refresh_token': settings.GOOGLE_ADS_REFRESH_TOKEN,
            'use_proto_plus': True
        }
        
        self._client = None
        self._initialized = False
    
    def _get_client(self) -> GoogleClient:
        """Get or create Google Ads client instance."""
        if not self._client:
            if not all([
                settings.GOOGLE_ADS_DEVELOPER_TOKEN,
                settings.GOOGLE_ADS_CLIENT_ID,
                settings.GOOGLE_ADS_CLIENT_SECRET,
                settings.GOOGLE_ADS_REFRESH_TOKEN
            ]):
                raise ValueError("Google Ads credentials not configured")
            
            self._client = GoogleClient.load_from_dict(self.credentials)
            self._initialized = True
            logger.info("google_ads_client_initialized")
        
        return self._client
    
    async def fetch_campaign_performance(
        self,
        customer_id: str,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetch campaign performance metrics from Google Ads.
        
        Args:
            customer_id: Google Ads customer ID (e.g., "123-456-7890")
            campaign_id: Google Ads campaign ID
            start_date: Start date for metrics (defaults to 24 hours ago)
            end_date: End date for metrics (defaults to now)
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            client = self._get_client()
            ga_service = client.get_service("GoogleAdsService")
            
            # Default date range
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=1)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Format dates for Google Ads API
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Build query
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign_budget.amount_micros,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.cost_micros,
                    metrics.conversions_value,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_per_conversion
                FROM campaign
                WHERE campaign.id = {campaign_id}
                AND segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
            """
            
            # Remove customer ID dashes
            customer_id = customer_id.replace("-", "")
            
            # Execute query
            response = ga_service.search(customer_id=customer_id, query=query)
            
            # Aggregate metrics
            total_impressions = 0
            total_clicks = 0
            total_conversions = 0
            total_cost_micros = 0
            total_conv_value = 0
            
            campaign_name = None
            campaign_status = None
            budget_micros = None
            
            for row in response:
                campaign_name = row.campaign.name
                campaign_status = row.campaign.status.name
                budget_micros = row.campaign_budget.amount_micros
                
                total_impressions += row.metrics.impressions
                total_clicks += row.metrics.clicks
                total_conversions += row.metrics.conversions
                total_cost_micros += row.metrics.cost_micros
                total_conv_value += row.metrics.conversions_value
            
            # Convert micros to actual amounts (1 micros = 0.000001)
            spend = total_cost_micros / 1_000_000
            revenue = total_conv_value
            budget = budget_micros / 1_000_000 if budget_micros else 0
            
            # Calculate derived metrics
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (spend / total_clicks) if total_clicks > 0 else 0
            cpa = (spend / total_conversions) if total_conversions > 0 else 0
            cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            roas = (revenue / spend) if spend > 0 else 0
            
            metrics = {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "status": campaign_status,
                "daily_budget": budget,
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": int(total_conversions),
                "spend": round(spend, 2),
                "revenue": round(revenue, 2),
                "ctr": round(ctr, 2),
                "cpc": round(cpc, 2),
                "cpa": round(cpa, 2),
                "cvr": round(cvr, 2),
                "roas": round(roas, 2),
                "timestamp": datetime.utcnow()
            }
            
            logger.info(
                "google_ads_metrics_fetched",
                campaign_id=campaign_id,
                impressions=total_impressions,
                spend=spend
            )
            
            return metrics
            
        except GoogleAdsException as ex:
            logger.error(
                "google_ads_api_error",
                campaign_id=campaign_id,
                error=str(ex)
            )
            raise
        except Exception as e:
            logger.error(
                "google_ads_fetch_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
    
    async def update_campaign_budget(
        self,
        customer_id: str,
        campaign_id: str,
        new_budget: float
    ) -> bool:
        """
        Update campaign daily budget in Google Ads.
        
        Args:
            customer_id: Google Ads customer ID
            campaign_id: Campaign ID to update
            new_budget: New daily budget in USD
        
        Returns:
            True if successful
        """
        try:
            client = self._get_client()
            campaign_service = client.get_service("CampaignService")
            campaign_budget_service = client.get_service("CampaignBudgetService")
            
            # Remove dashes from customer ID
            customer_id = customer_id.replace("-", "")
            
            # Get current campaign to find budget ID
            ga_service = client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                    campaign.id,
                    campaign.campaign_budget
                FROM campaign
                WHERE campaign.id = {campaign_id}
            """
            
            response = ga_service.search(customer_id=customer_id, query=query)
            
            budget_resource_name = None
            for row in response:
                budget_resource_name = row.campaign.campaign_budget
                break
            
            if not budget_resource_name:
                raise ValueError(f"Campaign budget not found for campaign {campaign_id}")
            
            # Convert budget to micros (1 USD = 1,000,000 micros)
            budget_micros = int(new_budget * 1_000_000)
            
            # Create budget operation
            budget_operation = client.get_type("CampaignBudgetOperation")
            budget = budget_operation.update
            budget.resource_name = budget_resource_name
            budget.amount_micros = budget_micros
            
            # Set field mask
            client.copy_from(
                budget_operation.update_mask,
                client.get_type("FieldMask")(paths=["amount_micros"])
            )
            
            # Update budget
            budget_response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=customer_id,
                operations=[budget_operation]
            )
            
            logger.info(
                "google_ads_budget_updated",
                campaign_id=campaign_id,
                new_budget=new_budget,
                budget_micros=budget_micros
            )
            
            return True
            
        except GoogleAdsException as ex:
            logger.error(
                "google_ads_budget_update_error",
                campaign_id=campaign_id,
                error=str(ex)
            )
            raise
        except Exception as e:
            logger.error(
                "google_ads_budget_update_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
    
    async def pause_campaign(
        self,
        customer_id: str,
        campaign_id: str
    ) -> bool:
        """Pause a Google Ads campaign."""
        try:
            client = self._get_client()
            campaign_service = client.get_service("CampaignService")
            
            customer_id = customer_id.replace("-", "")
            
            # Create campaign operation
            campaign_operation = client.get_type("CampaignOperation")
            campaign = campaign_operation.update
            campaign.resource_name = campaign_service.campaign_path(customer_id, campaign_id)
            campaign.status = client.enums.CampaignStatusEnum.PAUSED
            
            # Set field mask
            client.copy_from(
                campaign_operation.update_mask,
                client.get_type("FieldMask")(paths=["status"])
            )
            
            # Update campaign
            campaign_service.mutate_campaigns(
                customer_id=customer_id,
                operations=[campaign_operation]
            )
            
            logger.info("google_ads_campaign_paused", campaign_id=campaign_id)
            return True
            
        except Exception as e:
            logger.error("google_ads_pause_failed", campaign_id=campaign_id, error=str(e))
            raise
    
    async def activate_campaign(
        self,
        customer_id: str,
        campaign_id: str
    ) -> bool:
        """Activate a Google Ads campaign."""
        try:
            client = self._get_client()
            campaign_service = client.get_service("CampaignService")
            
            customer_id = customer_id.replace("-", "")
            
            # Create campaign operation
            campaign_operation = client.get_type("CampaignOperation")
            campaign = campaign_operation.update
            campaign.resource_name = campaign_service.campaign_path(customer_id, campaign_id)
            campaign.status = client.enums.CampaignStatusEnum.ENABLED
            
            # Set field mask
            client.copy_from(
                campaign_operation.update_mask,
                client.get_type("FieldMask")(paths=["status"])
            )
            
            # Update campaign
            campaign_service.mutate_campaigns(
                customer_id=customer_id,
                operations=[campaign_operation]
            )
            
            logger.info("google_ads_campaign_activated", campaign_id=campaign_id)
            return True
            
        except Exception as e:
            logger.error("google_ads_activate_failed", campaign_id=campaign_id, error=str(e))
            raise
    
    def is_configured(self) -> bool:
        """Check if Google Ads credentials are configured."""
        # Read directly from environment to support testing with patched env vars
        return all([
            os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
            os.getenv('GOOGLE_ADS_CLIENT_ID'),
            os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
            os.getenv('GOOGLE_ADS_REFRESH_TOKEN')
        ])

    async def fetch_creative_performance(
        self,
        customer_id: str,
        ad_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetch creative (ad) performance metrics from Google Ads.

        Args:
            customer_id: Google Ads customer ID (e.g., "123-456-7890")
            ad_id: Google Ads Ad ID
            start_date: Start date for metrics (defaults to 24 hours ago)
            end_date: End date for metrics (defaults to now)

        Returns:
            Dictionary with creative performance metrics including:
            - Volume metrics (impressions, clicks, conversions)
            - Efficiency metrics (CTR, CPC, ROAS)
            - Engagement metrics (interactions)
            - Video metrics (if video ad)
        """
        try:
            client = self._get_client()
            ga_service = client.get_service("GoogleAdsService")

            # Default date range
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=1)
            if not end_date:
                end_date = datetime.utcnow()

            # Format dates
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            # Build query for ad-level metrics
            query = f"""
                SELECT
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.name,
                    ad_group_ad.ad.type,
                    ad_group_ad.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.cost_micros,
                    metrics.conversions_value,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_per_conversion,
                    metrics.interactions,
                    metrics.interaction_rate,
                    metrics.video_views,
                    metrics.video_view_rate,
                    metrics.video_quartile_p25_rate,
                    metrics.video_quartile_p50_rate,
                    metrics.video_quartile_p75_rate,
                    metrics.video_quartile_p100_rate,
                    metrics.average_cpv
                FROM ad_group_ad
                WHERE ad_group_ad.ad.id = {ad_id}
                AND segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
            """

            # Remove customer ID dashes
            customer_id = customer_id.replace("-", "")

            # Execute query
            response = ga_service.search(customer_id=customer_id, query=query)

            # Aggregate metrics
            total_impressions = 0
            total_clicks = 0
            total_conversions = 0
            total_cost_micros = 0
            total_conv_value = 0
            total_interactions = 0
            total_video_views = 0

            ad_name = None
            ad_type = None
            ad_status = None

            for row in response:
                ad_name = row.ad_group_ad.ad.name if row.ad_group_ad.ad.name else f"Ad {ad_id}"
                ad_type = row.ad_group_ad.ad.type_.name
                ad_status = row.ad_group_ad.status.name

                total_impressions += row.metrics.impressions
                total_clicks += row.metrics.clicks
                total_conversions += row.metrics.conversions
                total_cost_micros += row.metrics.cost_micros
                total_conv_value += row.metrics.conversions_value
                total_interactions += row.metrics.interactions
                total_video_views += row.metrics.video_views

            # Convert micros to actual amounts
            spend = total_cost_micros / 1_000_000
            revenue = total_conv_value

            # Calculate derived metrics
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (spend / total_clicks) if total_clicks > 0 else 0
            cpm = (spend / total_impressions * 1000) if total_impressions > 0 else 0
            cpa = (spend / total_conversions) if total_conversions > 0 else 0
            cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            roas = (revenue / spend) if spend > 0 else 0
            engagement_rate = (total_interactions / total_impressions * 100) if total_impressions > 0 else 0

            metrics = {
                "ad_id": ad_id,
                "ad_name": ad_name or "Unknown",
                "ad_type": ad_type or "UNKNOWN",
                "status": ad_status or "UNKNOWN",

                # Volume metrics
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": int(total_conversions),
                "spend": round(spend, 2),
                "revenue": round(revenue, 2),

                # Efficiency metrics
                "ctr": round(ctr, 2),
                "cpc": round(cpc, 2),
                "cpm": round(cpm, 2),
                "cpa": round(cpa, 2),
                "cvr": round(cvr, 2),
                "roas": round(roas, 2),

                # Engagement
                "interactions": total_interactions,
                "engagement_rate": round(engagement_rate, 2),

                # Video metrics (if applicable)
                "video_views": total_video_views,
                "video_views_25": 0,  # Google Ads doesn't expose these directly
                "video_views_50": 0,
                "video_views_75": 0,
                "video_views_100": 0,
                "avg_watch_time": 0.0,

                # Quality indicators
                "relevance_score": 0.0,  # Google Ads uses Quality Score, but it's at keyword level
                "frequency": 0.0,  # Not directly available at ad level

                # Social engagement (not applicable for Google Ads)
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "saves": 0,

                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().date()
            }

            logger.info(
                "google_ads_creative_metrics_fetched",
                ad_id=ad_id,
                impressions=total_impressions,
                ctr=ctr,
                engagement_rate=engagement_rate
            )

            return metrics

        except GoogleAdsException as ex:
            logger.error(
                "google_ads_creative_fetch_failed",
                ad_id=ad_id,
                error=str(ex)
            )
            raise
        except Exception as e:
            logger.error(
                "google_ads_creative_fetch_failed",
                ad_id=ad_id,
                error=str(e)
            )
            raise

    async def fetch_all_creatives_in_campaign(
        self,
        customer_id: str,
        campaign_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[Dict[str, Any]]:
        """
        Fetch performance metrics for all creatives (ads) in a campaign.

        Args:
            customer_id: Google Ads customer ID
            campaign_id: Google Ads Campaign ID
            start_date: Start date for metrics
            end_date: End date for metrics

        Returns:
            List of creative performance dictionaries
        """
        try:
            client = self._get_client()
            ga_service = client.get_service("GoogleAdsService")

            # Default date range
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=1)
            if not end_date:
                end_date = datetime.utcnow()

            # Format dates
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            # Query to get all ads in campaign
            query = f"""
                SELECT
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.name,
                    campaign.id
                FROM ad_group_ad
                WHERE campaign.id = {campaign_id}
                AND segments.date BETWEEN '{start_date_str}' AND '{end_date_str}'
            """

            # Remove customer ID dashes
            customer_id = customer_id.replace("-", "")

            # Execute query
            response = ga_service.search(customer_id=customer_id, query=query)

            # Collect unique ad IDs
            ad_ids = set()
            for row in response:
                ad_ids.add(str(row.ad_group_ad.ad.id))

            # Fetch metrics for each ad
            creative_metrics = []

            for ad_id in ad_ids:
                try:
                    metrics = await self.fetch_creative_performance(
                        customer_id=customer_id,
                        ad_id=ad_id,
                        start_date=start_date,
                        end_date=end_date
                    )

                    metrics['platform_creative_id'] = ad_id
                    creative_metrics.append(metrics)

                except Exception as e:
                    logger.warning(
                        "google_ads_creative_fetch_skipped",
                        ad_id=ad_id,
                        error=str(e)
                    )
                    continue

            logger.info(
                "google_ads_campaign_creatives_fetched",
                campaign_id=campaign_id,
                creative_count=len(creative_metrics)
            )

            return creative_metrics

        except GoogleAdsException as ex:
            logger.error(
                "google_ads_campaign_creatives_fetch_failed",
                campaign_id=campaign_id,
                error=str(ex)
            )
            raise
        except Exception as e:
            logger.error(
                "google_ads_campaign_creatives_fetch_failed",
                campaign_id=campaign_id,
                error=str(e)
            )
            raise
