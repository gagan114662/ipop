#!/usr/bin/env python3
"""Test platform API credentials."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Change to parent directory for .env access
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
os.chdir(parent_dir)

load_dotenv()

async def test_google_ads():
    """Test Google Ads API connection."""
    print("\n🔍 Testing Google Ads API...")
    try:
        from google.ads.googleads.client import GoogleAdsClient

        credentials = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "use_proto_plus": True
        }

        client = GoogleAdsClient.load_from_dict(credentials)

        # Try to get customer service
        customer_service = client.get_service("CustomerService")
        print("✅ Google Ads API: Connected successfully")
        return True
    except Exception as e:
        print(f"❌ Google Ads API: Failed - {str(e)}")
        return False


async def test_meta_ads():
    """Test Meta Ads API connection."""
    print("\n🔍 Testing Meta Ads API...")
    try:
        from facebook_business.api import FacebookAdsApi
        from facebook_business.adobjects.user import User

        app_id = os.getenv("META_APP_ID")
        app_secret = os.getenv("META_APP_SECRET")
        access_token = os.getenv("META_ACCESS_TOKEN")

        FacebookAdsApi.init(app_id, app_secret, access_token)

        # Try to get user info
        me = User(fbid='me')
        me_data = me.api_get(fields=['id', 'name'])

        print(f"✅ Meta Ads API: Connected successfully")
        print(f"   User ID: {me_data.get('id', 'Unknown')}")
        if 'name' in me_data:
            print(f"   User Name: {me_data['name']}")
        return True
    except Exception as e:
        print(f"❌ Meta Ads API: Failed - {str(e)}")
        return False


async def test_linkedin():
    """Test LinkedIn API connection."""
    print("\n🔍 Testing LinkedIn API...")
    try:
        import requests

        client_id = os.getenv("LINKEDIN_CLIENT_ID")
        client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

        if not access_token:
            print("⚠️  LinkedIn API: No access token available")
            print(f"   Client ID: {client_id}")
            print(f"   Client Secret: {client_secret[:10]}..." if client_secret else "   Client Secret: Not set")
            print("   ℹ️  Need to complete OAuth flow to get access token")
            return False

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://api.linkedin.com/v2/me", headers=headers)

        if response.status_code == 200:
            print("✅ LinkedIn API: Connected successfully")
            return True
        else:
            print(f"❌ LinkedIn API: Failed - Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ LinkedIn API: Failed - {str(e)}")
        return False


async def main():
    """Run all API tests."""
    print("=" * 60)
    print("🧪 Platform API Credentials Test")
    print("=" * 60)

    results = {
        "Google Ads": await test_google_ads(),
        "Meta Ads": await test_meta_ads(),
        "LinkedIn": await test_linkedin()
    }

    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    for platform, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{platform:15} : {status}")

    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)

    print(f"\n📈 Total: {total_passed}/{total_tests} platforms connected successfully")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
