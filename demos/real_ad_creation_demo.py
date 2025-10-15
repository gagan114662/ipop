"""
Real Ad Creation Demo - Shows actual ads being created on Meta and Google platforms.

This demo demonstrates:
1. Creating actual campaigns on Meta (Facebook/Instagram)
2. Creating actual campaigns on Google Ads
3. Showing the created ads in the platform interfaces
4. Fetching real metrics from the platforms

Requirements:
- Valid Meta Ads API credentials
- Valid Google Ads API credentials
- Test ad accounts with sufficient permissions
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog

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


class RealAdCreationDemo:
    """Demo class for creating real ads on Meta and Google platforms."""
    
    def __init__(self):
        self.meta_api = None
        self.google_client = None
        self.created_campaigns = []
        
    def setup_meta_api(self, app_id: str, app_secret: str, access_token: str):
        """Initialize Meta Ads API."""
        try:
            self.meta_api = FacebookAdsApi.init(
                app_id=app_id,
                app_secret=app_secret,
                access_token=access_token
            )
            logger.info("✅ Meta Ads API initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Meta API: {e}")
            return False
    
    def setup_google_ads(self, credentials: Dict[str, str]):
        """Initialize Google Ads API."""
        try:
            self.google_client = GoogleAdsClient.load_from_dict(credentials)
            logger.info("✅ Google Ads API initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Ads API: {e}")
            return False
    
    async def create_meta_campaign(self, ad_account_id: str, campaign_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a real campaign on Meta (Facebook/Instagram).
        
        Args:
            ad_account_id: Meta Ad Account ID
            campaign_data: Campaign configuration
            
        Returns:
            Campaign ID if successful, None otherwise
        """
        try:
            if not self.meta_api:
                logger.error("❌ Meta API not initialized")
                return None
            
            # Create Campaign
            campaign = Campaign(parent_id=ad_account_id)
            campaign[Campaign.Field.name] = campaign_data['name']
            campaign[Campaign.Field.objective] = Campaign.Objective.conversions
            campaign[Campaign.Field.status] = Campaign.Status.paused  # Start paused for safety
            campaign[Campaign.Field.special_ad_categories] = []
            
            campaign.remote_create()
            campaign_id = campaign['id']
            
            logger.info(f"✅ Meta Campaign created: {campaign_id}")
            
            # Create Ad Set
            adset = AdSet(parent_id=ad_account_id)
            adset[AdSet.Field.name] = f"{campaign_data['name']} - Ad Set"
            adset[AdSet.Field.campaign_id] = campaign_id
            adset[AdSet.Field.daily_budget] = int(campaign_data['daily_budget'] * 100)  # Convert to cents
            adset[AdSet.Field.billing_event] = AdSet.BillingEvent.impressions
            adset[AdSet.Field.optimization_goal] = AdSet.OptimizationGoal.conversions
            adset[AdSet.Field.bid_amount] = 100  # $1.00 bid
            adset[AdSet.Field.status] = AdSet.Status.paused
            
            # Targeting
            targeting = {
                'geo_locations': {
                    'countries': campaign_data.get('countries', ['US'])
                },
                'age_min': campaign_data.get('age_min', 18),
                'age_max': campaign_data.get('age_max', 65),
                'interests': campaign_data.get('interests', [])
            }
            adset[AdSet.Field.targeting] = targeting
            
            adset.remote_create()
            adset_id = adset['id']
            
            logger.info(f"✅ Meta Ad Set created: {adset_id}")
            
            # Create Ad Creative
            creative = AdCreative(parent_id=ad_account_id)
            creative[AdCreative.Field.name] = f"{campaign_data['name']} - Creative"
            creative[AdCreative.Field.object_story_spec] = {
                'page_id': campaign_data.get('page_id', 'YOUR_PAGE_ID'),
                'link_data': {
                    'link': campaign_data.get('website_url', 'https://example.com'),
                    'message': campaign_data.get('ad_text', 'Check out our amazing product!')
                }
            }
            
            creative.remote_create()
            creative_id = creative['id']
            
            logger.info(f"✅ Meta Ad Creative created: {creative_id}")
            
            # Create Ad
            ad = Ad(parent_id=ad_account_id)
            ad[Ad.Field.name] = f"{campaign_data['name']} - Ad"
            ad[Ad.Field.adset_id] = adset_id
            ad[Ad.Field.creative] = {'creative_id': creative_id}
            ad[Ad.Field.status] = Ad.Status.paused
            
            ad.remote_create()
            ad_id = ad['id']
            
            logger.info(f"✅ Meta Ad created: {ad_id}")
            
            # Store campaign info
            campaign_info = {
                'platform': 'Meta',
                'campaign_id': campaign_id,
                'adset_id': adset_id,
                'creative_id': creative_id,
                'ad_id': ad_id,
                'name': campaign_data['name'],
                'status': 'PAUSED',
                'created_at': datetime.now().isoformat()
            }
            self.created_campaigns.append(campaign_info)
            
            return campaign_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create Meta campaign: {e}")
            return None
    
    async def create_google_ads_campaign(self, customer_id: str, campaign_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a real campaign on Google Ads.
        
        Args:
            customer_id: Google Ads Customer ID
            campaign_data: Campaign configuration
            
        Returns:
            Campaign ID if successful, None otherwise
        """
        try:
            if not self.google_client:
                logger.error("❌ Google Ads API not initialized")
                return None
            
            # Remove dashes from customer ID
            customer_id = customer_id.replace("-", "")
            
            # Create Campaign
            campaign_service = self.google_client.get_service("CampaignService")
            campaign_operation = self.google_client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            
            campaign.name = campaign_data['name']
            campaign.advertising_channel_type = self.google_client.enums.AdvertisingChannelTypeEnum.SEARCH
            campaign.status = self.google_client.enums.CampaignStatusEnum.PAUSED  # Start paused for safety
            campaign.campaign_budget = f"customers/{customer_id}/campaignBudgets/1"  # Use existing budget
            
            # Set bidding strategy
            campaign.maximize_conversions.target_cpa_micros = int(campaign_data.get('target_cpa', 10) * 1000000)
            
            # Set start and end dates
            campaign.start_date = datetime.now().strftime("%Y-%m-%d")
            campaign.end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Create campaign
            campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id,
                operations=[campaign_operation]
            )
            
            campaign_id = campaign_response.results[0].resource_name.split("/")[-1]
            logger.info(f"✅ Google Ads Campaign created: {campaign_id}")
            
            # Create Ad Group
            ad_group_service = self.google_client.get_service("AdGroupService")
            ad_group_operation = self.google_client.get_type("AdGroupOperation")
            ad_group = ad_group_operation.create
            
            ad_group.name = f"{campaign_data['name']} - Ad Group"
            ad_group.campaign = f"customers/{customer_id}/campaigns/{campaign_id}"
            ad_group.status = self.google_client.enums.AdGroupStatusEnum.ENABLED
            ad_group.type_ = self.google_client.enums.AdGroupTypeEnum.SEARCH_STANDARD
            ad_group.cpc_bid_micros = int(campaign_data.get('cpc_bid', 1) * 1000000)
            
            ad_group_response = ad_group_service.mutate_ad_groups(
                customer_id=customer_id,
                operations=[ad_group_operation]
            )
            
            ad_group_id = ad_group_response.results[0].resource_name.split("/")[-1]
            logger.info(f"✅ Google Ads Ad Group created: {ad_group_id}")
            
            # Create Keywords
            keyword_service = self.google_client.get_service("AdGroupCriterionService")
            keyword_operations = []
            
            for keyword_text in campaign_data.get('keywords', ['example keyword']):
                keyword_operation = self.google_client.get_type("AdGroupCriterionOperation")
                keyword_criterion = keyword_operation.create
                keyword_criterion.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
                keyword_criterion.status = self.google_client.enums.AdGroupCriterionStatusEnum.ENABLED
                keyword_criterion.keyword.text = keyword_text
                keyword_criterion.keyword.match_type = self.google_client.enums.KeywordMatchTypeEnum.EXACT
                keyword_operations.append(keyword_operation)
            
            if keyword_operations:
                keyword_response = keyword_service.mutate_ad_group_criteria(
                    customer_id=customer_id,
                    operations=keyword_operations
                )
                logger.info(f"✅ Google Ads Keywords created: {len(keyword_response.results)} keywords")
            
            # Create Ad
            ad_service = self.google_client.get_service("AdGroupAdService")
            ad_operation = self.google_client.get_type("AdGroupAdOperation")
            ad_group_ad = ad_operation.create
            
            ad_group_ad.ad_group = f"customers/{customer_id}/adGroups/{ad_group_id}"
            ad_group_ad.status = self.google_client.enums.AdGroupAdStatusEnum.ENABLED
            
            # Create responsive search ad
            ad_group_ad.ad.responsive_search_ad.headlines.extend([
                self.google_client.get_type("AdTextAsset")(text=campaign_data.get('headline1', 'Amazing Product')),
                self.google_client.get_type("AdTextAsset")(text=campaign_data.get('headline2', 'Best Quality')),
                self.google_client.get_type("AdTextAsset")(text=campaign_data.get('headline3', 'Great Value'))
            ])
            
            ad_group_ad.ad.responsive_search_ad.descriptions.extend([
                self.google_client.get_type("AdTextAsset")(text=campaign_data.get('description1', 'Check out our amazing product!')),
                self.google_client.get_type("AdTextAsset")(text=campaign_data.get('description2', 'High quality and great value.'))
            ])
            
            ad_group_ad.ad.final_urls.append(campaign_data.get('website_url', 'https://example.com'))
            
            ad_response = ad_service.mutate_ad_group_ads(
                customer_id=customer_id,
                operations=[ad_operation]
            )
            
            ad_id = ad_response.results[0].resource_name.split("/")[-1]
            logger.info(f"✅ Google Ads Ad created: {ad_id}")
            
            # Store campaign info
            campaign_info = {
                'platform': 'Google Ads',
                'campaign_id': campaign_id,
                'ad_group_id': ad_group_id,
                'ad_id': ad_id,
                'name': campaign_data['name'],
                'status': 'PAUSED',
                'created_at': datetime.now().isoformat()
            }
            self.created_campaigns.append(campaign_info)
            
            return campaign_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create Google Ads campaign: {e}")
            return None
    
    async def fetch_platform_metrics(self, platform: str, campaign_id: str, account_id: str) -> Dict[str, Any]:
        """Fetch real metrics from the platform."""
        try:
            if platform == 'Meta':
                return await self._fetch_meta_metrics(account_id, campaign_id)
            elif platform == 'Google Ads':
                return await self._fetch_google_metrics(account_id, campaign_id)
            else:
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to fetch {platform} metrics: {e}")
            return {}
    
    async def _fetch_meta_metrics(self, ad_account_id: str, campaign_id: str) -> Dict[str, Any]:
        """Fetch Meta campaign metrics."""
        try:
            campaign = Campaign(campaign_id)
            insights = campaign.get_insights(fields=[
                'impressions', 'clicks', 'spend', 'actions', 'ctr', 'cpc', 'cpm'
            ])
            
            if insights:
                insight = insights[0]
                return {
                    'impressions': int(insight.get('impressions', 0)),
                    'clicks': int(insight.get('clicks', 0)),
                    'spend': float(insight.get('spend', 0)),
                    'ctr': float(insight.get('ctr', 0)),
                    'cpc': float(insight.get('cpc', 0)),
                    'cpm': float(insight.get('cpm', 0)),
                    'actions': insight.get('actions', [])
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Failed to fetch Meta metrics: {e}")
            return {}
    
    async def _fetch_google_metrics(self, customer_id: str, campaign_id: str) -> Dict[str, Any]:
        """Fetch Google Ads campaign metrics."""
        try:
            ga_service = self.google_client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT 
                    campaign.id,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.ctr,
                    metrics.average_cpc
                FROM campaign 
                WHERE campaign.id = {campaign_id}
                AND segments.date >= '{datetime.now().strftime('%Y-%m-%d')}'
            """
            
            response = ga_service.search(customer_id=customer_id, query=query)
            
            for row in response:
                return {
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'spend': row.metrics.cost_micros / 1000000,  # Convert from micros
                    'ctr': row.metrics.ctr,
                    'cpc': row.metrics.average_cpc / 1000000  # Convert from micros
                }
            return {}
        except Exception as e:
            logger.error(f"❌ Failed to fetch Google Ads metrics: {e}")
            return {}
    
    def print_campaign_summary(self):
        """Print summary of all created campaigns."""
        print("\n" + "="*80)
        print("🎯 REAL AD CREATION SUMMARY")
        print("="*80)
        
        for campaign in self.created_campaigns:
            print(f"\n📊 {campaign['platform']} Campaign:")
            print(f"   Name: {campaign['name']}")
            print(f"   Campaign ID: {campaign['campaign_id']}")
            print(f"   Status: {campaign['status']}")
            print(f"   Created: {campaign['created_at']}")
            
            if campaign['platform'] == 'Meta':
                print(f"   Ad Set ID: {campaign.get('adset_id', 'N/A')}")
                print(f"   Creative ID: {campaign.get('creative_id', 'N/A')}")
                print(f"   Ad ID: {campaign.get('ad_id', 'N/A')}")
            elif campaign['platform'] == 'Google Ads':
                print(f"   Ad Group ID: {campaign.get('ad_group_id', 'N/A')}")
                print(f"   Ad ID: {campaign.get('ad_id', 'N/A')}")
        
        print(f"\n✅ Total campaigns created: {len(self.created_campaigns)}")
        print("\n🔗 To view these ads:")
        print("   Meta: https://business.facebook.com/adsmanager")
        print("   Google Ads: https://ads.google.com/")
        print("="*80)


async def main():
    """Main demo function."""
    print("🚀 REAL AD CREATION DEMO")
    print("="*50)
    print("This demo will create ACTUAL ads on Meta and Google platforms!")
    print("⚠️  WARNING: This will create real campaigns that may incur costs!")
    print("="*50)
    
    # Initialize demo
    demo = RealAdCreationDemo()
    
    # Configuration - REPLACE WITH YOUR ACTUAL CREDENTIALS
    META_CONFIG = {
        'app_id': 'YOUR_META_APP_ID',
        'app_secret': 'YOUR_META_APP_SECRET',
        'access_token': 'YOUR_META_ACCESS_TOKEN',
        'ad_account_id': 'act_YOUR_AD_ACCOUNT_ID'
    }
    
    GOOGLE_CONFIG = {
        'developer_token': 'YOUR_GOOGLE_DEVELOPER_TOKEN',
        'client_id': 'YOUR_GOOGLE_CLIENT_ID',
        'client_secret': 'YOUR_GOOGLE_CLIENT_SECRET',
        'refresh_token': 'YOUR_GOOGLE_REFRESH_TOKEN',
        'customer_id': 'YOUR_GOOGLE_CUSTOMER_ID'
    }
    
    # Check if credentials are configured
    if META_CONFIG['app_id'] == 'YOUR_META_APP_ID':
        print("❌ Meta credentials not configured. Please update META_CONFIG in the script.")
        return
    
    if GOOGLE_CONFIG['developer_token'] == 'YOUR_GOOGLE_DEVELOPER_TOKEN':
        print("❌ Google Ads credentials not configured. Please update GOOGLE_CONFIG in the script.")
        return
    
    # Initialize APIs
    print("\n🔧 Initializing APIs...")
    meta_ready = demo.setup_meta_api(
        META_CONFIG['app_id'],
        META_CONFIG['app_secret'],
        META_CONFIG['access_token']
    )
    
    google_ready = demo.setup_google_ads(GOOGLE_CONFIG)
    
    if not meta_ready and not google_ready:
        print("❌ No platforms configured. Exiting.")
        return
    
    # Campaign configurations
    campaigns_to_create = [
        {
            'name': 'IPOP Demo - Meta Campaign',
            'daily_budget': 10.0,  # $10/day
            'countries': ['US'],
            'age_min': 25,
            'age_max': 55,
            'interests': [{'id': '6003107902433', 'name': 'Marketing'}],  # Marketing interest
            'page_id': 'YOUR_PAGE_ID',
            'website_url': 'https://example.com',
            'ad_text': 'Discover our amazing marketing solutions!'
        },
        {
            'name': 'IPOP Demo - Google Campaign',
            'daily_budget': 10.0,  # $10/day
            'target_cpa': 5.0,  # $5 target CPA
            'cpc_bid': 1.0,  # $1 CPC bid
            'keywords': ['marketing automation', 'advertising platform', 'media buying'],
            'headline1': 'Marketing Automation Platform',
            'headline2': 'Advanced Advertising Tools',
            'headline3': 'Media Buying Made Easy',
            'description1': 'Streamline your marketing with our powerful platform.',
            'description2': 'Get better results with intelligent automation.',
            'website_url': 'https://example.com'
        }
    ]
    
    # Create campaigns
    print("\n🎯 Creating campaigns...")
    
    for i, campaign_data in enumerate(campaigns_to_create, 1):
        print(f"\n📝 Creating campaign {i}/{len(campaigns_to_create)}: {campaign_data['name']}")
        
        if 'Meta' in campaign_data['name'] and meta_ready:
            campaign_id = await demo.create_meta_campaign(
                META_CONFIG['ad_account_id'],
                campaign_data
            )
            if campaign_id:
                print(f"✅ Meta campaign created successfully: {campaign_id}")
            else:
                print("❌ Failed to create Meta campaign")
        
        elif 'Google' in campaign_data['name'] and google_ready:
            campaign_id = await demo.create_google_ads_campaign(
                GOOGLE_CONFIG['customer_id'],
                campaign_data
            )
            if campaign_id:
                print(f"✅ Google Ads campaign created successfully: {campaign_id}")
            else:
                print("❌ Failed to create Google Ads campaign")
        
        # Wait between creations to avoid rate limits
        await asyncio.sleep(2)
    
    # Print summary
    demo.print_campaign_summary()
    
    # Fetch metrics (if campaigns were created)
    if demo.created_campaigns:
        print("\n📊 Fetching campaign metrics...")
        for campaign in demo.created_campaigns:
            print(f"\n🔍 Fetching metrics for {campaign['platform']} campaign: {campaign['campaign_id']}")
            
            account_id = META_CONFIG['ad_account_id'] if campaign['platform'] == 'Meta' else GOOGLE_CONFIG['customer_id']
            metrics = await demo.fetch_platform_metrics(
                campaign['platform'],
                campaign['campaign_id'],
                account_id
            )
            
            if metrics:
                print(f"   Impressions: {metrics.get('impressions', 0)}")
                print(f"   Clicks: {metrics.get('clicks', 0)}")
                print(f"   Spend: ${metrics.get('spend', 0):.2f}")
                print(f"   CTR: {metrics.get('ctr', 0):.2%}")
            else:
                print("   No metrics available (campaign may be too new)")
    
    print("\n🎉 Demo completed!")
    print("\n📋 Next steps:")
    print("1. Check your Meta Ads Manager: https://business.facebook.com/adsmanager")
    print("2. Check your Google Ads account: https://ads.google.com/")
    print("3. Review the created campaigns and their settings")
    print("4. Consider activating campaigns if you want to run them")
    print("5. Monitor performance metrics in both platforms")


if __name__ == "__main__":
    asyncio.run(main())
