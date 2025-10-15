"""
Platform Integration Demo - Shows how ads are created on Meta and Google platforms.

This demo demonstrates the complete flow of:
1. Creating campaigns through IPOP API
2. Platform-specific ad creation on Meta and Google
3. Real-time metrics fetching
4. Campaign optimization

Note: This demo uses simulated platform responses for demonstration purposes.
In production, this would create actual ads on the platforms.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog
import requests

logger = structlog.get_logger(__name__)


class PlatformIntegrationDemo:
    """Demo class showing platform integration for ad creation."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.access_token = None
        self.created_campaigns = []
        
    async def authenticate(self) -> bool:
        """Authenticate with IPOP API."""
        try:
            # Register or login
            client_data = {
                "company_name": "Platform Demo Company",
                "email": "platform-demo@example.com",
                "password": "demo123456"
            }
            
            # Try to register first
            response = requests.post(f"{self.api_base_url}/api/v1/auth/register", json=client_data)
            
            if response.status_code == 201:
                self.access_token = response.json()['access_token']
                logger.info("✅ Client registered successfully")
            elif response.status_code == 400 and "already registered" in response.text:
                # Try to login
                login_data = {"email": client_data["email"], "password": client_data["password"]}
                response = requests.post(f"{self.api_base_url}/api/v1/auth/login", json=login_data)
                if response.status_code == 200:
                    self.access_token = response.json()['access_token']
                    logger.info("✅ Client logged in successfully")
                else:
                    logger.error("❌ Login failed")
                    return False
            else:
                logger.error(f"❌ Registration failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False
    
    async def create_sku(self, sku_data: Dict[str, Any]) -> Optional[str]:
        """Create a SKU for campaign creation."""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/v1/skus/",
                json=sku_data,
                headers=headers
            )
            
            if response.status_code == 201:
                sku = response.json()
                logger.info(f"✅ SKU created: {sku['sku_id']}")
                return sku['sku_id']
            else:
                logger.error(f"❌ SKU creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ SKU creation error: {e}")
            return None
    
    async def create_campaign_via_ipop(self, campaign_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create campaign through IPOP API."""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/v1/campaigns/",
                json=campaign_data,
                headers=headers
            )
            
            if response.status_code == 201:
                campaign = response.json()
                logger.info(f"✅ Campaign created via IPOP: {campaign['campaign_id']}")
                return campaign
            else:
                logger.error(f"❌ Campaign creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Campaign creation error: {e}")
            return None
    
    async def simulate_meta_ad_creation(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate Meta ad creation process.
        In production, this would call the actual Meta Marketing API.
        """
        logger.info("🎯 Creating Meta campaign...")
        
        # Simulate API calls to Meta
        await asyncio.sleep(1)  # Simulate API delay
        
        # Simulate campaign creation
        meta_campaign_id = f"meta_{int(time.time())}"
        logger.info(f"✅ Meta Campaign created: {meta_campaign_id}")
        
        await asyncio.sleep(0.5)
        
        # Simulate ad set creation
        meta_adset_id = f"adset_{int(time.time())}"
        logger.info(f"✅ Meta Ad Set created: {meta_adset_id}")
        
        await asyncio.sleep(0.5)
        
        # Simulate creative creation
        meta_creative_id = f"creative_{int(time.time())}"
        logger.info(f"✅ Meta Ad Creative created: {meta_creative_id}")
        
        await asyncio.sleep(0.5)
        
        # Simulate ad creation
        meta_ad_id = f"ad_{int(time.time())}"
        logger.info(f"✅ Meta Ad created: {meta_ad_id}")
        
        return {
            'platform': 'Meta',
            'platform_campaign_id': meta_campaign_id,
            'platform_adset_id': meta_adset_id,
            'platform_creative_id': meta_creative_id,
            'platform_ad_id': meta_ad_id,
            'status': 'ACTIVE',
            'created_at': datetime.now().isoformat(),
            'platform_url': f"https://business.facebook.com/adsmanager/manage/campaigns/{meta_campaign_id}"
        }
    
    async def simulate_google_ads_creation(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate Google Ads creation process.
        In production, this would call the actual Google Ads API.
        """
        logger.info("🎯 Creating Google Ads campaign...")
        
        # Simulate API calls to Google Ads
        await asyncio.sleep(1)  # Simulate API delay
        
        # Simulate campaign creation
        google_campaign_id = f"google_{int(time.time())}"
        logger.info(f"✅ Google Ads Campaign created: {google_campaign_id}")
        
        await asyncio.sleep(0.5)
        
        # Simulate ad group creation
        google_adgroup_id = f"adgroup_{int(time.time())}"
        logger.info(f"✅ Google Ads Ad Group created: {google_adgroup_id}")
        
        await asyncio.sleep(0.5)
        
        # Simulate keyword creation
        keywords_created = len(campaign_data.get('keywords', []))
        logger.info(f"✅ Google Ads Keywords created: {keywords_created} keywords")
        
        await asyncio.sleep(0.5)
        
        # Simulate ad creation
        google_ad_id = f"ad_{int(time.time())}"
        logger.info(f"✅ Google Ads Ad created: {google_ad_id}")
        
        return {
            'platform': 'Google Ads',
            'platform_campaign_id': google_campaign_id,
            'platform_adgroup_id': google_adgroup_id,
            'platform_ad_id': google_ad_id,
            'keywords_count': keywords_created,
            'status': 'ACTIVE',
            'created_at': datetime.now().isoformat(),
            'platform_url': f"https://ads.google.com/aw/campaigns/{google_campaign_id}"
        }
    
    async def fetch_simulated_metrics(self, platform: str, campaign_id: str) -> Dict[str, Any]:
        """Simulate fetching metrics from platform APIs."""
        logger.info(f"📊 Fetching {platform} metrics for campaign: {campaign_id}")
        
        # Simulate API delay
        await asyncio.sleep(1)
        
        # Simulate realistic metrics
        import random
        
        if platform == 'Meta':
            return {
                'impressions': random.randint(1000, 5000),
                'clicks': random.randint(50, 200),
                'spend': round(random.uniform(10.0, 50.0), 2),
                'ctr': round(random.uniform(0.02, 0.08), 4),
                'cpc': round(random.uniform(0.5, 2.0), 2),
                'cpm': round(random.uniform(5.0, 15.0), 2),
                'conversions': random.randint(5, 25),
                'conversion_rate': round(random.uniform(0.05, 0.15), 4),
                'roas': round(random.uniform(2.0, 5.0), 2)
            }
        else:  # Google Ads
            return {
                'impressions': random.randint(2000, 8000),
                'clicks': random.randint(100, 400),
                'spend': round(random.uniform(20.0, 80.0), 2),
                'ctr': round(random.uniform(0.03, 0.10), 4),
                'cpc': round(random.uniform(0.8, 2.5), 2),
                'cpm': round(random.uniform(8.0, 20.0), 2),
                'conversions': random.randint(10, 40),
                'conversion_rate': round(random.uniform(0.08, 0.20), 4),
                'roas': round(random.uniform(2.5, 6.0), 2)
            }
    
    async def optimize_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Simulate campaign optimization."""
        logger.info(f"🔧 Optimizing campaign: {campaign_id}")
        
        # Simulate optimization process
        await asyncio.sleep(2)
        
        # Simulate optimization decisions
        optimizations = [
            "Increased bid for high-performing keywords",
            "Paused low-performing ad groups",
            "Adjusted targeting parameters",
            "Updated ad copy based on performance",
            "Reallocated budget to top performers"
        ]
        
        selected_optimizations = random.sample(optimizations, random.randint(2, 4))
        
        return {
            'campaign_id': campaign_id,
            'optimizations_applied': selected_optimizations,
            'expected_improvement': round(random.uniform(0.15, 0.35), 2),
            'optimized_at': datetime.now().isoformat()
        }
    
    def print_demo_summary(self):
        """Print comprehensive demo summary."""
        print("\n" + "="*80)
        print("🎯 PLATFORM INTEGRATION DEMO SUMMARY")
        print("="*80)
        
        print(f"\n📊 Total campaigns created: {len(self.created_campaigns)}")
        
        for i, campaign in enumerate(self.created_campaigns, 1):
            print(f"\n{i}. {campaign['platform']} Campaign:")
            print(f"   IPOP Campaign ID: {campaign['ipop_campaign_id']}")
            print(f"   Platform Campaign ID: {campaign['platform_campaign_id']}")
            print(f"   Status: {campaign['status']}")
            print(f"   Created: {campaign['created_at']}")
            print(f"   Platform URL: {campaign['platform_url']}")
            
            if 'metrics' in campaign:
                metrics = campaign['metrics']
                print(f"   📈 Performance Metrics:")
                print(f"      Impressions: {metrics['impressions']:,}")
                print(f"      Clicks: {metrics['clicks']:,}")
                print(f"      Spend: ${metrics['spend']:.2f}")
                print(f"      CTR: {metrics['ctr']:.2%}")
                print(f"      CPC: ${metrics['cpc']:.2f}")
                print(f"      Conversions: {metrics['conversions']}")
                print(f"      ROAS: {metrics['roas']:.2f}x")
        
        print("\n🔗 Platform Links:")
        print("   Meta Ads Manager: https://business.facebook.com/adsmanager")
        print("   Google Ads: https://ads.google.com/")
        print("   IPOP Dashboard: http://localhost:3000/web_ui_dashboard.html")
        
        print("\n✅ Demo completed successfully!")
        print("="*80)


async def main():
    """Main demo function."""
    print("🚀 PLATFORM INTEGRATION DEMO")
    print("="*50)
    print("This demo shows how IPOP creates ads on Meta and Google platforms")
    print("="*50)
    
    # Initialize demo
    demo = PlatformIntegrationDemo()
    
    # Authenticate
    print("\n🔐 Authenticating with IPOP API...")
    if not await demo.authenticate():
        print("❌ Authentication failed. Make sure the IPOP API is running.")
        return
    
    # Create SKU
    print("\n📦 Creating SKU...")
    sku_data = {
        'sku_id': 'DEMO-SKU-001',
        'name': 'Demo Product',
        'daily_budget': 50.0,
        'monthly_budget': 1500.0,
        'target_roas': 3.0
    }
    
    sku_id = await demo.create_sku(sku_data)
    if not sku_id:
        print("❌ SKU creation failed")
        return
    
    # Campaign configurations
    campaigns_to_create = [
        {
            'campaign_id': 'DEMO-META-001',
            'sku_id': sku_id,
            'name': 'Demo Meta Campaign',
            'platform': 'META',
            'daily_budget': 25.0,
            'target_roas': 3.5,
            'metadata': {
                'targeting': {
                    'age_range': [25, 55],
                    'interests': ['marketing', 'technology'],
                    'countries': ['US', 'CA']
                },
                'creative': {
                    'headline': 'Amazing Marketing Solution',
                    'description': 'Boost your marketing ROI with our platform'
                }
            }
        },
        {
            'campaign_id': 'DEMO-GOOGLE-001',
            'sku_id': sku_id,
            'name': 'Demo Google Campaign',
            'platform': 'GOOGLE_ADS',
            'daily_budget': 25.0,
            'target_roas': 4.0,
            'metadata': {
                'targeting': {
                    'keywords': ['marketing automation', 'advertising platform', 'media buying'],
                    'locations': ['United States', 'Canada']
                },
                'creative': {
                    'headline1': 'Marketing Automation Platform',
                    'headline2': 'Advanced Advertising Tools',
                    'description1': 'Streamline your marketing with our powerful platform'
                }
            }
        }
    ]
    
    # Create campaigns
    print("\n🎯 Creating campaigns...")
    
    for i, campaign_data in enumerate(campaigns_to_create, 1):
        print(f"\n📝 Creating campaign {i}/{len(campaigns_to_create)}: {campaign_data['name']}")
        
        # Create campaign via IPOP API
        ipop_campaign = await demo.create_campaign_via_ipop(campaign_data)
        if not ipop_campaign:
            print("❌ Failed to create campaign via IPOP API")
            continue
        
        # Create ads on the platform
        platform_result = None
        if campaign_data['platform'] == 'META':
            platform_result = await demo.simulate_meta_ad_creation(campaign_data)
        elif campaign_data['platform'] == 'GOOGLE_ADS':
            platform_result = await demo.simulate_google_ads_creation(campaign_data)
        
        if platform_result:
            # Combine IPOP and platform data
            campaign_info = {
                'ipop_campaign_id': ipop_campaign['campaign_id'],
                'platform': platform_result['platform'],
                'platform_campaign_id': platform_result['platform_campaign_id'],
                'status': platform_result['status'],
                'created_at': platform_result['created_at'],
                'platform_url': platform_result['platform_url']
            }
            
            # Add platform-specific IDs
            if platform_result['platform'] == 'Meta':
                campaign_info['platform_adset_id'] = platform_result['platform_adset_id']
                campaign_info['platform_creative_id'] = platform_result['platform_creative_id']
                campaign_info['platform_ad_id'] = platform_result['platform_ad_id']
            else:
                campaign_info['platform_adgroup_id'] = platform_result['platform_adgroup_id']
                campaign_info['platform_ad_id'] = platform_result['platform_ad_id']
                campaign_info['keywords_count'] = platform_result['keywords_count']
            
            demo.created_campaigns.append(campaign_info)
            print(f"✅ Campaign created successfully on {platform_result['platform']}")
        
        # Wait between creations
        await asyncio.sleep(1)
    
    # Fetch metrics for all campaigns
    print("\n📊 Fetching campaign metrics...")
    for campaign in demo.created_campaigns:
        print(f"\n🔍 Fetching metrics for {campaign['platform']} campaign...")
        metrics = await demo.fetch_simulated_metrics(
            campaign['platform'],
            campaign['platform_campaign_id']
        )
        campaign['metrics'] = metrics
        
        if metrics:
            print(f"   Impressions: {metrics['impressions']:,}")
            print(f"   Clicks: {metrics['clicks']:,}")
            print(f"   Spend: ${metrics['spend']:.2f}")
            print(f"   CTR: {metrics['ctr']:.2%}")
            print(f"   Conversions: {metrics['conversions']}")
            print(f"   ROAS: {metrics['roas']:.2f}x")
    
    # Simulate optimization
    print("\n🔧 Running campaign optimization...")
    for campaign in demo.created_campaigns:
        optimization = await demo.optimize_campaign(campaign['ipop_campaign_id'])
        campaign['optimization'] = optimization
        print(f"✅ Optimized {campaign['platform']} campaign")
    
    # Print summary
    demo.print_demo_summary()
    
    print("\n🎉 Platform Integration Demo completed!")
    print("\n📋 What this demo showed:")
    print("1. ✅ Campaign creation through IPOP API")
    print("2. ✅ Platform-specific ad creation (Meta & Google)")
    print("3. ✅ Real-time metrics fetching")
    print("4. ✅ Campaign optimization")
    print("5. ✅ Cross-platform campaign management")
    
    print("\n🔗 To see this in action:")
    print("1. Check IPOP Dashboard: http://localhost:3000/web_ui_dashboard.html")
    print("2. View Meta Ads Manager: https://business.facebook.com/adsmanager")
    print("3. View Google Ads: https://ads.google.com/")


if __name__ == "__main__":
    import random
    asyncio.run(main())
