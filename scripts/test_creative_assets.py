#!/usr/bin/env python3
"""
Test creative API with real image and video assets.
"""
import asyncio
import httpx
import os
from pathlib import Path


async def test_creative_with_real_assets():
    """Test creative API endpoints with actual media files."""

    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

    # File paths
    video_path = Path("20250423_1735_Ethereal Underwater Serenity_simple_compose_01jsj97ny4e1dbr7k8msj89hm2.mp4")
    image_path = Path("a8K1It2U_400x400.jpg")

    print("=" * 60)
    print("🎬 Testing Creative API with Real Media Assets")
    print("=" * 60)

    timeout = float(os.getenv("HTTP_TIMEOUT_SECONDS", "30.0"))
    async with httpx.AsyncClient(base_url=base_url, timeout=timeout) as client:
        # Step 1: Register/Login
        print("\n1️⃣  Authenticating...")
        register_response = await client.post("/api/v1/auth/register", json={
            "email": "media_test@example.com",
            "password": "testpass123",
            "company_name": "Media Test Co"
        })

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "media_test@example.com",
            "password": "testpass123"
        })

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Authenticated successfully")

        # Step 2: Create Image Creative
        print(f"\n2️⃣  Creating Image Creative...")
        print(f"   📁 File: {image_path.name}")
        print(f"   📊 Size: {image_path.stat().st_size / 1024:.2f} KB")

        image_creative_data = {
            "creative_id": "real_image_001",
            "name": "Twitter Profile Image Creative",
            "creative_type": "image",
            "platform": "meta",
            "headline": "Professional Profile Image",
            "description": "High-quality profile image for social media",
            "image_url": f"file://{image_path.absolute()}",
            "format": "image/jpeg",
            "dimensions": "400x400",
            "status": "active"
        }

        image_response = await client.post(
            "/api/v1/creatives/",
            json=image_creative_data,
            headers=headers
        )

        if image_response.status_code in [200, 201]:
            print(f"✅ Image creative created successfully")
            print(f"   ID: {image_response.json()['creative_id']}")
        else:
            print(f"❌ Image creative creation failed: {image_response.status_code}")
            print(f"   Error: {image_response.text}")

        # Step 3: Create Video Creative
        print(f"\n3️⃣  Creating Video Creative...")
        print(f"   📁 File: {video_path.name}")
        print(f"   📊 Size: {video_path.stat().st_size / (1024 * 1024):.2f} MB")

        video_creative_data = {
            "creative_id": "real_video_001",
            "name": "Ethereal Underwater Serenity Video",
            "creative_type": "video",
            "platform": "google_ads",
            "headline": "Stunning Underwater Visuals",
            "description": "Mesmerizing underwater scenery for brand storytelling",
            "video_url": f"file://{video_path.absolute()}",
            "format": "video/mp4",
            "duration_seconds": 30,
            "call_to_action": "learn_more",
            "status": "active"
        }

        video_response = await client.post(
            "/api/v1/creatives/",
            json=video_creative_data,
            headers=headers
        )

        if video_response.status_code in [200, 201]:
            print(f"✅ Video creative created successfully")
            print(f"   ID: {video_response.json()['creative_id']}")
        else:
            print(f"❌ Video creative creation failed: {video_response.status_code}")
            print(f"   Error: {video_response.text}")

        # Step 4: List all creatives
        print(f"\n4️⃣  Listing all creatives...")
        list_response = await client.get("/api/v1/creatives/", headers=headers)

        if list_response.status_code == 200:
            data = list_response.json()
            print(f"✅ Found {data['total']} creative(s)")
            for creative in data['creatives']:
                print(f"\n   📄 {creative['name']}")
                print(f"      Type: {creative['creative_type']}")
                print(f"      Platform: {creative['platform']}")
                print(f"      Status: {creative['status']}")
                if 'image_url' in creative:
                    print(f"      Image: {creative['image_url']}")
                if 'video_url' in creative:
                    print(f"      Video: {creative['video_url']}")

        # Step 5: Create A/B test with the two creatives
        print(f"\n5️⃣  Setting up A/B test with media creatives...")

        # Create SKU and Campaign first
        sku_response = await client.post("/api/v1/skus/", json={
            "sku_id": "media_test_sku",
            "name": "Media Test Product",
            "description": "Product for testing media creatives",
            "target_roas": 3.0,
            "daily_budget": 500.0,
            "monthly_budget": 15000.0
        }, headers=headers)

        campaign_response = await client.post("/api/v1/campaigns/", json={
            "campaign_id": "media_test_campaign",
            "name": "Media Creative Test Campaign",
            "sku_id": "media_test_sku",
            "platform": "google_ads",
            "platform_campaign_id": "GA-media-test",
            "status": "active",
            "daily_budget": 100.0,
            "target_roas": 3.0
        }, headers=headers)

        if campaign_response.status_code in [200, 201]:
            ab_test_data = {
                "test_id": "media_ab_test_001",
                "name": "Image vs Video Creative Test",
                "campaign_id": "media_test_campaign",
                "variants": [
                    {
                        "creative_id": "real_image_001",
                        "variant_name": "Image Control",
                        "traffic_allocation": 50,
                        "is_control": True
                    },
                    {
                        "creative_id": "real_video_001",
                        "variant_name": "Video Variant",
                        "traffic_allocation": 50,
                        "is_control": False
                    }
                ],
                "test_type": "ab_test",
                "min_sample_size": 1000,
                "confidence_level": 0.95
            }

            ab_response = await client.post(
                "/api/v1/creative-tests/",
                json=ab_test_data,
                headers=headers
            )

            if ab_response.status_code in [200, 201]:
                print(f"✅ A/B test created successfully")
                print(f"   Test: Image vs Video")
                print(f"   Variants: 2 (50/50 split)")
            else:
                print(f"❌ A/B test creation failed: {ab_response.status_code}")
                print(f"   Error: {ab_response.text}")

        # Step 6: Get creative comparison
        print(f"\n6️⃣  Comparing creatives...")
        compare_response = await client.post(
            "/api/v1/creatives/compare",
            json={"creative_ids": ["real_image_001", "real_video_001"]},
            headers=headers
        )

        if compare_response.status_code == 200:
            comparison = compare_response.json()
            print(f"✅ Creative comparison:")
            for item in comparison.get('comparison', []):
                print(f"\n   {item['name']}:")
                print(f"      Impressions: {item.get('impressions', 0)}")
                print(f"      Clicks: {item.get('clicks', 0)}")
                print(f"      CTR: {item.get('ctr', 0):.2%}")

    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_creative_with_real_assets())
