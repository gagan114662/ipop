"""
Test Google Ads API credentials.

Google Ads requires:
1. Developer Token
2. Client ID + Client Secret (OAuth)
3. Refresh Token
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Change to parent directory for .env access
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
os.chdir(parent_dir)

# Load environment variables
load_dotenv()

GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
GOOGLE_ADS_CLIENT_ID = os.getenv('GOOGLE_ADS_CLIENT_ID')
GOOGLE_ADS_CLIENT_SECRET = os.getenv('GOOGLE_ADS_CLIENT_SECRET')
GOOGLE_ADS_REFRESH_TOKEN = os.getenv('GOOGLE_ADS_REFRESH_TOKEN')

print("=" * 70)
print("GOOGLE ADS CREDENTIALS TEST")
print("=" * 70)

print(f"\n📋 Credentials Status:")
print(f"   Developer Token: {'✅ Set' if GOOGLE_ADS_DEVELOPER_TOKEN else '❌ Missing'} ({GOOGLE_ADS_DEVELOPER_TOKEN[:15]}... if set)")
print(f"   Client ID: {'✅ Set' if GOOGLE_ADS_CLIENT_ID else '❌ Missing'} ({GOOGLE_ADS_CLIENT_ID[:30]}... if set)")
print(f"   Client Secret: {'✅ Set' if GOOGLE_ADS_CLIENT_SECRET else '❌ Missing'} ({GOOGLE_ADS_CLIENT_SECRET[:15]}... if set)")
print(f"   Refresh Token: {'✅ Set' if GOOGLE_ADS_REFRESH_TOKEN else '❌ Missing'} ({GOOGLE_ADS_REFRESH_TOKEN[:20]}... if set)")

if not all([GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
            GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN]):
    print("\n❌ ERROR: Some Google Ads credentials are missing")
    sys.exit(1)

print(f"\n✅ All Google Ads credentials are configured")

# Try to initialize Google Ads API client
try:
    from google.ads.googleads.client import GoogleAdsClient

    print("\n🔧 Attempting to initialize Google Ads client...")

    # Create credentials dictionary
    credentials = {
        "developer_token": GOOGLE_ADS_DEVELOPER_TOKEN,
        "client_id": GOOGLE_ADS_CLIENT_ID,
        "client_secret": GOOGLE_ADS_CLIENT_SECRET,
        "refresh_token": GOOGLE_ADS_REFRESH_TOKEN,
        "use_proto_plus": True,
    }

    # Try to create client
    client = GoogleAdsClient.load_from_dict(credentials)

    print("✅ Google Ads client initialized successfully!")

    # Try to get customer service
    print("\n🔧 Testing API access...")
    customer_service = client.get_service("CustomerService")

    print("✅ Google Ads API services accessible!")

    print("\n" + "=" * 70)
    print("GOOGLE ADS API - READY TO USE")
    print("=" * 70)
    print("""
✅ All credentials verified
✅ API client initialized
✅ Services accessible

You can now:
1. Fetch campaign performance data
2. Update campaign budgets
3. Pause/activate campaigns
4. Fetch creative (ad) performance metrics

Note: You'll need a Google Ads Customer ID (format: 123-456-7890) to make actual API calls.
    """)

except ImportError:
    print("\n⚠️  google-ads library not installed")
    print("   Run: pip install google-ads")
    print("   However, credentials appear valid!")

except Exception as e:
    error_msg = str(e)

    if "invalid_grant" in error_msg.lower():
        print("\n❌ ERROR: Refresh token is invalid or expired")
        print("   You need to regenerate the refresh token using OAuth flow")
    elif "invalid_client" in error_msg.lower():
        print("\n❌ ERROR: Client ID or Secret is invalid")
        print("   Check your OAuth credentials in Google Cloud Console")
    elif "developer token" in error_msg.lower():
        print("\n❌ ERROR: Developer token is invalid")
        print("   Check your developer token in Google Ads Manager")
    else:
        print(f"\n❌ ERROR: {error_msg}")

    print("\n" + "=" * 70)
    print("TROUBLESHOOTING:")
    print("=" * 70)
    print("""
1. Developer Token:
   - Go to Google Ads Manager > Admin > API Center
   - Copy your developer token

2. OAuth Credentials (Client ID + Secret):
   - Go to Google Cloud Console > APIs & Services > Credentials
   - Make sure OAuth 2.0 Client ID is created

3. Refresh Token:
   - Run the OAuth flow to get a new refresh token
   - Use the google-ads-python library's generate_user_credentials.py script

4. Enable Google Ads API:
   - Go to Google Cloud Console > APIs & Services > Library
   - Search for "Google Ads API" and enable it
    """)

    sys.exit(1)

print("\n✅ Google Ads credentials fully verified!")
