#!/usr/bin/env python3
"""Get Meta/Facebook Access Token."""

import os
import webbrowser
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")

# Meta OAuth endpoints
REDIRECT_URI = "https://yourdomain.com/auth/meta/callback"

def get_user_access_token():
    """Guide user to get a long-lived access token."""
    print("=" * 70)
    print("🔐 Meta/Facebook Access Token Generator")
    print("=" * 70)

    print(f"\n📋 App ID: {APP_ID}")
    print(f"📋 App Secret: {APP_SECRET}")

    print("\n" + "=" * 70)
    print("📝 Option 1: Graph API Explorer (Easiest)")
    print("=" * 70)

    print("\n1. Go to Graph API Explorer:")
    print("   https://developers.facebook.com/tools/explorer/")

    print("\n2. Select your app from dropdown (top right)")

    print("\n3. Click 'Generate Access Token' button")

    print("\n4. Grant permissions (select these):")
    permissions = [
        "ads_management",
        "ads_read",
        "business_management",
        "pages_read_engagement",
        "pages_manage_ads"
    ]
    for perm in permissions:
        print(f"   ✓ {perm}")

    print("\n5. Copy the generated access token")

    print("\n" + "=" * 70)
    print("📝 Option 2: Manual OAuth Flow")
    print("=" * 70)

    # Build OAuth URL
    scope = "ads_management,ads_read,business_management,pages_read_engagement,pages_manage_ads"
    auth_url = f"https://www.facebook.com/v23.0/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&scope={scope}&response_type=code"

    print("\n1. Visit this URL to authorize:")
    print(f"\n{auth_url}\n")

    print("2. After authorizing, copy the 'code' from the redirect URL")

    print("\n3. Exchange code for token using this URL:")
    token_url = f"https://graph.facebook.com/v23.0/oauth/access_token?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&client_secret={APP_SECRET}&code=YOUR_CODE_HERE"
    print(f"\n{token_url}\n")

    print("\n" + "=" * 70)
    print("💡 Get Long-Lived Token (60 days)")
    print("=" * 70)

    print("\nOnce you have a short-lived token, exchange it for a long-lived one:")
    print(f"\nhttps://graph.facebook.com/v23.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token=YOUR_SHORT_LIVED_TOKEN")

    print("\n" + "=" * 70)

    choice = input("\n🤔 Which method do you want? (1/2): ").strip()

    if choice == "1":
        print("\nOpening Graph API Explorer...")
        webbrowser.open("https://developers.facebook.com/tools/explorer/")
    elif choice == "2":
        print("\nOpening OAuth URL...")
        webbrowser.open(auth_url)

    print("\n" + "=" * 70)
    access_token = input("\n🔑 Paste your access token here: ").strip()

    if access_token:
        print("\n" + "=" * 70)
        print("✅ Testing Access Token")
        print("=" * 70)

        # Test the token
        import requests
        test_url = f"https://graph.facebook.com/v23.0/me?access_token={access_token}"
        response = requests.get(test_url)

        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Token is valid!")
            print(f"   User ID: {data.get('id')}")
            if 'name' in data:
                print(f"   Name: {data['name']}")

            # Update .env
            update = input("\n💾 Update .env file? (yes/no): ").strip().lower()

            if update == "yes":
                with open(".env", "r") as f:
                    lines = f.readlines()

                # Update META_ACCESS_TOKEN
                updated = False
                for i, line in enumerate(lines):
                    if line.startswith("META_ACCESS_TOKEN="):
                        lines[i] = f"META_ACCESS_TOKEN={access_token}\n"
                        updated = True
                        break

                if not updated:
                    lines.append(f"META_ACCESS_TOKEN={access_token}\n")

                with open(".env", "w") as f:
                    f.writelines(lines)

                print("\n✅ .env file updated!")
                print("\nNow run: python3 test_platform_apis.py")
        else:
            print(f"\n❌ Token test failed: {response.text}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    get_user_access_token()
