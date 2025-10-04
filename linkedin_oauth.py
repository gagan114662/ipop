#!/usr/bin/env python3
"""LinkedIn OAuth 2.0 Flow to get Access Token."""

import os
import webbrowser
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "https://yourdomain.com/auth/linkedin/callback"  # Your configured redirect URI

# LinkedIn OAuth endpoints
AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Scopes needed for LinkedIn Ads API
SCOPES = [
    "r_liteprofile",
    "r_emailaddress",
    "w_member_social",
    "r_ads",
    "rw_ads",
    "r_organization_social",
    "w_organization_social"
]

def get_authorization_url():
    """Generate LinkedIn OAuth authorization URL."""
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": "random_state_string_123"  # Use a random string in production
    }

    auth_url = f"{AUTHORIZATION_URL}?{urlencode(params)}"
    return auth_url


def exchange_code_for_token(authorization_code):
    """Exchange authorization code for access token."""
    import requests

    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(TOKEN_URL, data=data)

    if response.status_code == 200:
        token_data = response.json()
        return token_data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def main():
    """Run LinkedIn OAuth flow."""
    print("=" * 70)
    print("🔐 LinkedIn OAuth 2.0 Flow")
    print("=" * 70)

    print(f"\n📋 Client ID: {CLIENT_ID}")
    print(f"📋 Client Secret: {CLIENT_SECRET[:10]}..." if CLIENT_SECRET else "Not set")
    print(f"📋 Redirect URI: {REDIRECT_URI}")

    print("\n" + "=" * 70)
    print("📝 IMPORTANT: Before starting the OAuth flow")
    print("=" * 70)

    print("\n1. Go to LinkedIn Developer Portal:")
    print("   https://www.linkedin.com/developers/apps")

    print("\n2. Select your app and go to 'Auth' tab")

    print("\n3. Add this Redirect URL:")
    print(f"   {REDIRECT_URI}")

    print("\n4. Make sure these scopes are enabled:")
    for scope in SCOPES:
        print(f"   - {scope}")

    print("\n" + "=" * 70)

    proceed = input("\n✅ Have you completed the above steps? (yes/no): ").lower().strip()

    if proceed != "yes":
        print("\n⚠️  Please complete the setup first, then run this script again.")
        return

    # Generate authorization URL
    auth_url = get_authorization_url()

    print("\n" + "=" * 70)
    print("🌐 Step 1: Authorization")
    print("=" * 70)
    print("\nOpening your browser to authorize the application...")
    print(f"\nIf it doesn't open automatically, visit this URL:")
    print(f"\n{auth_url}\n")

    # Open browser
    webbrowser.open(auth_url)

    print("\n" + "=" * 70)
    print("📋 Step 2: Get Authorization Code")
    print("=" * 70)

    print("\nAfter authorizing, LinkedIn will redirect you to:")
    print(f"{REDIRECT_URI}?code=AUTHORIZATION_CODE&state=...")

    print("\n⚠️  The page will show an error (that's normal - we don't have a server running)")
    print("Just copy the 'code' parameter from the URL")

    authorization_code = input("\n🔑 Paste the authorization code here: ").strip()

    if not authorization_code:
        print("\n❌ No code provided. Exiting.")
        return

    print("\n" + "=" * 70)
    print("🔄 Step 3: Exchange Code for Access Token")
    print("=" * 70)

    token_data = exchange_code_for_token(authorization_code)

    if token_data:
        print("\n✅ Success! Access token obtained:")
        print(f"\n🔑 Access Token: {token_data.get('access_token')}")
        print(f"⏰ Expires in: {token_data.get('expires_in')} seconds")

        print("\n" + "=" * 70)
        print("💾 Update .env file")
        print("=" * 70)

        print("\nAdd this line to your .env file:")
        print(f"\nLINKEDIN_ACCESS_TOKEN={token_data.get('access_token')}")

        # Optionally update .env automatically
        update_env = input("\n📝 Auto-update .env file? (yes/no): ").lower().strip()

        if update_env == "yes":
            # Read current .env
            with open(".env", "r") as f:
                lines = f.readlines()

            # Update or add token line
            token_line = f"LINKEDIN_ACCESS_TOKEN={token_data.get('access_token')}\n"
            updated = False

            for i, line in enumerate(lines):
                if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                    lines[i] = token_line
                    updated = True
                    break

            if not updated:
                lines.append(token_line)

            # Write back
            with open(".env", "w") as f:
                f.writelines(lines)

            print("\n✅ .env file updated successfully!")
    else:
        print("\n❌ Failed to get access token")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
