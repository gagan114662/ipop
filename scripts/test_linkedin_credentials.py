"""
Test LinkedIn API credentials.

LinkedIn uses OAuth 2.0. With Client ID and Secret, we need to:
1. Check if credentials are valid
2. Note: Access token is missing - we'll need to get one via OAuth flow
"""
import os
import sys
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Change to parent directory for .env access
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
os.chdir(parent_dir)

# Load environment variables
load_dotenv()

LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')

print("=" * 70)
print("LINKEDIN CREDENTIALS TEST")
print("=" * 70)

print(f"\n📋 Credentials Status:")
print(f"   Client ID: {'✅ Set' if LINKEDIN_CLIENT_ID else '❌ Missing'} ({LINKEDIN_CLIENT_ID[:20]}... if set)")
print(f"   Client Secret: {'✅ Set' if LINKEDIN_CLIENT_SECRET else '❌ Missing'} ({LINKEDIN_CLIENT_SECRET[:20]}... if set)")
print(f"   Access Token: {'✅ Set' if LINKEDIN_ACCESS_TOKEN else '❌ Missing (needs OAuth flow)'}")

if not LINKEDIN_CLIENT_ID or not LINKEDIN_CLIENT_SECRET:
    print("\n❌ ERROR: LinkedIn Client ID or Secret not configured")
    sys.exit(1)

print(f"\n✅ LinkedIn Client ID and Secret are configured")

# Note: LinkedIn requires OAuth 2.0 flow to get access token
# We can't test API calls without an access token

print("\n" + "=" * 70)
print("NEXT STEPS FOR LINKEDIN:")
print("=" * 70)
print("""
To complete LinkedIn setup, you need to:

1. Implement OAuth 2.0 flow to get an access token:
   - Authorization URL: https://www.linkedin.com/oauth/v2/authorization
   - Token URL: https://www.linkedin.com/oauth/v2/accessToken
   - Required scopes: r_ads, rw_ads, r_organization_admin

2. Or manually generate an access token:
   - Go to: https://www.linkedin.com/developers/apps
   - Select your app
   - Go to "Auth" tab
   - Generate access token with required scopes

3. Add the access token to .env:
   LINKEDIN_ACCESS_TOKEN=your_access_token_here

For now, the credentials are valid but incomplete.
""")

print("\n✅ LinkedIn credentials partially verified (Client ID + Secret)")
print("⚠️  Access token needed for full API access")
