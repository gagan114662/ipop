"""
Google Ads platform integration client.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import structlog

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
        return all([
            settings.GOOGLE_ADS_DEVELOPER_TOKEN,
            settings.GOOGLE_ADS_CLIENT_ID,
            settings.GOOGLE_ADS_CLIENT_SECRET,
            settings.GOOGLE_ADS_REFRESH_TOKEN
        ])
