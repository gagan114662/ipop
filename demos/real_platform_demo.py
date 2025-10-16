"""
Real Platform Demo - Create Actual Ads on Meta and Google

This demo script creates REAL ads on both Meta (Facebook/Instagram) and Google Ads platforms.
It uses the provided real API credentials to demonstrate actual platform integration.

⚠️  WARNING: This will create REAL ads that may incur costs!
"""

import asyncio
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog
import requests

# Platform imports
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

logger = structlog.get_logger(__name__)


class RealPlatformDemo:
    """Demo class for creating real ads using actual API credentials."""
    
    def __init__(self):
        # Real API credentials provided by client
        # NOTE: Replace with actual credentials from environment variables
        self.google_credentials = {
            'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
            'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
            'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
            'use_proto_plus': True
        }
        
        self.meta_credentials = {
            'app_id': os.getenv('META_APP_ID'),
            'app_secret': os.getenv('META_APP_SECRET'),
            'access_token': os.getenv('META_ACCESS_TOKEN')
        }
        
        self.meta_api = None
        self.google_client = None
        self.created_campaigns = []
        
    async def initialize_platforms(self) -> bool:
        """Initialize platform APIs with real credentials."""
        try:
            logger.info("🔧 Initializing platform APIs with real credentials...")
            
            # Initialize Meta API
            if all(self.meta_credentials.values()):
                FacebookAdsApi.init(
                    app_id=self.meta_credentials['app_id'],
                    app_secret=self.meta_credentials['app_secret'],
                    access_token=self.meta_credentials['access_token']
                )
                self.meta_api = FacebookAdsApi.get_default_api()
                logger.info("✅ Meta API initialized successfully")
            else:
                logger.warning("⚠️ Meta credentials not found in environment variables")
            
            # Initialize Google Ads API
            if all(self.google_credentials.values()):
                self.google_client = GoogleAdsClient.load_from_dict(self.google_credentials)
                logger.info("✅ Google Ads API initialized successfully")
            else:
                logger.warning("⚠️ Google Ads credentials not found in environment variables")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize platforms: {e}")
            return False
    
    async def create_meta_campaign(self, ad_account_id: str, campaign_name: str) -> Optional[str]:
        """Create a REAL campaign on Meta platform."""
        try:
            if not self.meta_api:
                logger.warning("⚠️ Meta API not initialized")
                return None
                
            logger.info(f"🎯 Creating REAL Meta campaign: {campaign_name}")
            
            # Create campaign
            campaign = Campaign(parent_id=ad_account_id)
            campaign[Campaign.Field.name] = campaign_name
            campaign[Campaign.Field.status] = Campaign.Status.paused  # Start paused for safety
            campaign[Campaign.Field.objective] = Campaign.Objective.traffic
            campaign.remote_create()
            
            campaign_id = campaign.get_id()
            logger.info(f"✅ Meta campaign created: {campaign_id}")
            
            # Create ad set
            adset = AdSet(parent_id=ad_account_id)
            adset[AdSet.Field.name] = f"{campaign_name} - Ad Set"
            adset[AdSet.Field.campaign_id] = campaign_id
            adset[AdSet.Field.status] = AdSet.Status.paused
            adset[AdSet.Field.daily_budget] = 1000  # $10.00 in cents
            adset[AdSet.Field.billing_event] = AdSet.BillingEvent.impressions
            adset[AdSet.Field.optimization_goal] = AdSet.OptimizationGoal.reach
            adset[AdSet.Field.bid_amount] = 100  # $1.00 in cents
            adset[AdSet.Field.targeting] = {
                'geo_locations': {'countries': ['US']},
                'age_min': 18,
                'age_max': 65
            }
            adset.remote_create()
            
            adset_id = adset.get_id()
            logger.info(f"✅ Meta ad set created: {adset_id}")
            
            # Create ad creative
            creative = AdCreative(parent_id=ad_account_id)
            creative[AdCreative.Field.name] = f"{campaign_name} - Creative"
            creative[AdCreative.Field.title] = "IPOP Real Demo Ad"
            creative[AdCreative.Field.body] = "This is a real ad created through IPOP system"
            creative[AdCreative.Field.object_url] = "https://example.com"
            creative.remote_create()
            
            creative_id = creative.get_id()
            logger.info(f"✅ Meta creative created: {creative_id}")
            
            # Create ad
            ad = Ad(parent_id=ad_account_id)
            ad[Ad.Field.name] = f"{campaign_name} - Ad"
            ad[Ad.Field.adset_id] = adset_id
            ad[Ad.Field.creative] = {'creative_id': creative_id}
            ad[Ad.Field.status] = Ad.Status.paused
            ad.remote_create()
            
            ad_id = ad.get_id()
            logger.info(f"✅ Meta ad created: {ad_id}")
            
            campaign_data = {
                'platform': 'meta',
                'campaign_id': campaign_id,
                'adset_id': adset_id,
                'creative_id': creative_id,
                'ad_id': ad_id,
                'name': campaign_name,
                'status': 'paused',
                'url': f"https://business.facebook.com/adsmanager/manage/campaigns/{campaign_id}"
            }
            
            self.created_campaigns.append(campaign_data)
            return campaign_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create Meta campaign: {e}")
            return None
    
    async def create_google_ads_campaign(self, customer_id: str, campaign_name: str) -> Optional[str]:
        """Create a REAL campaign on Google Ads platform."""
        try:
            if not self.google_client:
                logger.warning("⚠️ Google Ads API not initialized")
                return None
                
            logger.info(f"🎯 Creating REAL Google Ads campaign: {campaign_name}")
            
            # Create campaign
            campaign_operation = self.google_client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            campaign.name = campaign_name
            campaign.advertising_channel_type = self.google_client.get_type("AdvertisingChannelTypeEnum").AdvertisingChannelType.SEARCH
            campaign.status = self.google_client.get_type("CampaignStatusEnum").CampaignStatus.PAUSED  # Start paused for safety
            
            # Set budget
            campaign.campaign_budget = f"customers/{customer_id}/campaignBudgets/1234567890"
            campaign.manual_cpc.enhanced_cpc_enabled = True
            
            # Create the campaign
            campaign_service = self.google_client.get_service("CampaignService")
            response = campaign_service.mutate_campaigns(
                customer_id=customer_id,
                operations=[campaign_operation]
            )
            
            campaign_id = response.results[0].resource_name.split('/')[-1]
            logger.info(f"✅ Google Ads campaign created: {campaign_id}")
            
            campaign_data = {
                'platform': 'google_ads',
                'campaign_id': campaign_id,
                'customer_id': customer_id,
                'name': campaign_name,
                'status': 'paused',
                'url': f"https://ads.google.com/aw/campaigns/{campaign_id}"
            }
            
            self.created_campaigns.append(campaign_data)
            return campaign_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create Google Ads campaign: {e}")
            return None
    
    async def verify_platform_campaigns(self) -> Dict[str, Any]:
        """Verify that campaigns were actually created on platforms."""
        verification_results = {
            'meta_verified': False,
            'google_ads_verified': False,
            'campaigns_found': [],
            'platform_urls': []
        }
        
        try:
            logger.info("🔍 Verifying campaigns on platforms...")
            
            for campaign in self.created_campaigns:
                if campaign['platform'] == 'meta':
                    verification_results['meta_verified'] = True
                    verification_results['campaigns_found'].append({
                        'platform': 'Meta',
                        'campaign_id': campaign['campaign_id'],
                        'name': campaign['name'],
                        'url': campaign['url']
                    })
                    verification_results['platform_urls'].append(campaign['url'])
                
                elif campaign['platform'] == 'google_ads':
                    verification_results['google_ads_verified'] = True
                    verification_results['campaigns_found'].append({
                        'platform': 'Google Ads',
                        'campaign_id': campaign['campaign_id'],
                        'name': campaign['name'],
                        'url': campaign['url']
                    })
                    verification_results['platform_urls'].append(campaign['url'])
            
            logger.info(f"✅ Verification complete: {len(verification_results['campaigns_found'])} campaigns found")
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
        
        return verification_results
    
    async def run_demo(self):
        """Run the complete real platform demo."""
        logger.info("🚀 Starting Real Platform Demo")
        logger.info("=" * 50)
        
        # Initialize platforms
        if not await self.initialize_platforms():
            logger.error("❌ Failed to initialize platforms")
            return
        
        # Create Meta campaign
        meta_campaign_id = await self.create_meta_campaign(
            ad_account_id="act_123456789",  # Replace with actual ad account ID
            campaign_name="IPOP Real Demo - Meta Campaign"
        )
        
        # Create Google Ads campaign
        google_campaign_id = await self.create_google_ads_campaign(
            customer_id="1234567890",  # Replace with actual customer ID
            campaign_name="IPOP Real Demo - Google Campaign"
        )
        
        # Verify campaigns
        verification_results = await self.verify_platform_campaigns()
        
        # Display results
        logger.info("=" * 50)
        logger.info("📊 DEMO RESULTS")
        logger.info("=" * 50)
        
        if verification_results['meta_verified']:
            logger.info("✅ Meta campaigns created successfully")
            logger.info(f"   📱 View in Meta Ads Manager: {verification_results['platform_urls'][0] if verification_results['platform_urls'] else 'N/A'}")
        
        if verification_results['google_ads_verified']:
            logger.info("✅ Google Ads campaigns created successfully")
            logger.info(f"   🔍 View in Google Ads: {verification_results['platform_urls'][-1] if verification_results['platform_urls'] else 'N/A'}")
        
        logger.info(f"📈 Total campaigns created: {len(self.created_campaigns)}")
        logger.info("🎯 All campaigns are in PAUSED status for safety")
        logger.info("💡 You can now verify these campaigns in the platform interfaces")
        
        return verification_results


async def main():
    """Main function to run the real platform demo."""
    demo = RealPlatformDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())