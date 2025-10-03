"""
Test data seeder - Populate database with sample data for testing.

Usage:
    python -m app.db.seed_test_data
"""
import asyncio
from datetime import datetime, timedelta
import random
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.security import hash_password
from app.models.campaign import Platform, CampaignStatus, OptimizationMode


async def seed_test_data():
    """Seed database with test data."""
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    print("🌱 Seeding test data...")
    
    # 1. Create test client
    test_client_id = "test-client-123"
    test_client = {
        "client_id": test_client_id,
        "company_name": "Test Company Inc",
        "email": "test@testcompany.com",
        "hashed_password": hash_password("password123"),
        "is_active": True,
        "settings": {
            "default_timezone": "UTC",
            "default_currency": "USD",
            "regions": ["NA", "EU"],
            "notification_email": "test@testcompany.com",
            "auto_optimization_enabled": True,
            "min_campaign_budget": 100.0,
            "max_daily_budget_change_percent": 20.0
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.clients.delete_many({"client_id": test_client_id})
    await db.clients.insert_one(test_client)
    print(f"✅ Created test client: {test_client['email']}")
    
    # 2. Create test SKUs
    skus = [
        {
            "client_id": test_client_id,
            "sku_id": "WIDGET-PRO-001",
            "name": "Premium Widget",
            "description": "High-end widget for enterprise customers",
            "category": "Electronics",
            "target_roas": 3.5,
            "daily_budget": 1000.0,
            "monthly_budget": 30000.0,
            "budget_allocation": {
                "google_ads": 400.0,
                "meta": 300.0,
                "tiktok": 200.0,
                "linkedin": 100.0
            },
            "status": "active",
            "created_at": datetime.utcnow() - timedelta(days=45),
            "updated_at": datetime.utcnow(),
            "total_spend": 15000.0,
            "total_revenue": 52500.0,
            "total_impressions": 250000,
            "total_clicks": 5000,
            "total_conversions": 350,
            "current_roas": 3.5,
            "metadata": {"product_line": "premium", "region": "NA"}
        },
        {
            "client_id": test_client_id,
            "sku_id": "WIDGET-STD-002",
            "name": "Standard Widget",
            "description": "Mid-range widget for SMB customers",
            "category": "Electronics",
            "target_roas": 2.8,
            "daily_budget": 500.0,
            "monthly_budget": 15000.0,
            "budget_allocation": {
                "google_ads": 250.0,
                "meta": 150.0,
                "tiktok": 75.0,
                "linkedin": 25.0
            },
            "status": "active",
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow(),
            "total_spend": 7500.0,
            "total_revenue": 21000.0,
            "total_impressions": 150000,
            "total_clicks": 3000,
            "total_conversions": 210,
            "current_roas": 2.8,
            "metadata": {"product_line": "standard", "region": "NA"}
        }
    ]
    
    await db.skus.delete_many({"client_id": test_client_id})
    await db.skus.insert_many(skus)
    print(f"✅ Created {len(skus)} test SKUs")
    
    # 3. Create test campaigns
    campaigns = []
    platforms = [Platform.GOOGLE_ADS, Platform.META, Platform.TIKTOK]
    
    for sku in skus:
        for platform in platforms:
            # Mature campaign (30+ days)
            campaign_id = f"{sku['sku_id']}-{platform.value}-mature"
            campaigns.append({
                "client_id": test_client_id,
                "sku_id": sku["sku_id"],
                "campaign_id": campaign_id,
                "name": f"{sku['name']} - {platform.value.title()} Campaign",
                "platform": platform.value,
                "platform_campaign_id": f"{platform.value.upper()}-{random.randint(100000, 999999)}",
                "daily_budget": 150.0,
                "target_cpa": None,
                "target_roas": sku["target_roas"],
                "status": CampaignStatus.ACTIVE.value,
                "optimization_mode": OptimizationMode.EXPLOIT.value,
                "integrator": None,
                "created_at": datetime.utcnow() - timedelta(days=35),
                "updated_at": datetime.utcnow(),
                "campaign_age_days": 35,
                "current_metrics": {
                    "impressions": 50000,
                    "clicks": 1000,
                    "conversions": 70,
                    "spend": 3500.0,
                    "revenue": 12250.0,
                    "ctr": 2.0,
                    "cpc": 3.5,
                    "cpa": 50.0,
                    "roas": 3.5,
                    "last_updated": datetime.utcnow()
                },
                "last_optimization": datetime.utcnow() - timedelta(hours=1),
                "optimization_count": 35,
                "metadata": {}
            })
            
            # New campaign (3 days) in EXPLORE mode
            campaign_id_new = f"{sku['sku_id']}-{platform.value}-new"
            campaigns.append({
                "client_id": test_client_id,
                "sku_id": sku["sku_id"],
                "campaign_id": campaign_id_new,
                "name": f"{sku['name']} - {platform.value.title()} New Campaign",
                "platform": platform.value,
                "platform_campaign_id": f"{platform.value.upper()}-{random.randint(100000, 999999)}",
                "daily_budget": 100.0,
                "target_cpa": None,
                "target_roas": sku["target_roas"],
                "status": CampaignStatus.ACTIVE.value,
                "optimization_mode": OptimizationMode.EXPLORE.value,
                "integrator": None,
                "created_at": datetime.utcnow() - timedelta(days=3),
                "updated_at": datetime.utcnow(),
                "campaign_age_days": 3,
                "current_metrics": {
                    "impressions": 800,
                    "clicks": 15,
                    "conversions": 1,
                    "spend": 250.0,
                    "revenue": 700.0,
                    "ctr": 1.88,
                    "cpc": 16.67,
                    "cpa": 250.0,
                    "roas": 2.8,
                    "last_updated": datetime.utcnow()
                },
                "last_optimization": None,
                "optimization_count": 0,
                "metadata": {}
            })
    
    await db.campaigns.delete_many({"client_id": test_client_id})
    await db.campaigns.insert_many(campaigns)
    print(f"✅ Created {len(campaigns)} test campaigns")
    
    # 4. Create performance metrics (last 48 hours)
    metrics = []
    for campaign in campaigns:
        # Generate hourly metrics for last 48 hours
        for hours_ago in range(48, 0, -1):
            timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
            
            # Simulate realistic metrics with some randomness
            base_impressions = random.randint(800, 1200)
            clicks = int(base_impressions * random.uniform(0.015, 0.025))
            conversions = int(clicks * random.uniform(0.05, 0.12))
            spend = campaign["daily_budget"] / 24 * random.uniform(0.8, 1.2)
            revenue = spend * random.uniform(2.5, 4.0)
            
            ctr = (clicks / base_impressions * 100) if base_impressions > 0 else 0
            cpc = (spend / clicks) if clicks > 0 else 0
            cpa = (spend / conversions) if conversions > 0 else 0
            cvr = (conversions / clicks * 100) if clicks > 0 else 0
            roas = (revenue / spend) if spend > 0 else 0
            
            metrics.append({
                "client_id": test_client_id,
                "campaign_id": campaign["campaign_id"],
                "sku_id": campaign["sku_id"],
                "platform": campaign["platform"],
                "timestamp": timestamp,
                "hour_of_day": timestamp.hour,
                "day_of_week": timestamp.weekday(),
                "impressions": base_impressions,
                "clicks": clicks,
                "conversions": conversions,
                "spend": round(spend, 2),
                "revenue": round(revenue, 2),
                "ctr": round(ctr, 2),
                "cpc": round(cpc, 2),
                "cpa": round(cpa, 2),
                "cvr": round(cvr, 2),
                "roas": round(roas, 2)
            })
    
    await db.performance_metrics.delete_many({"client_id": test_client_id})
    await db.performance_metrics.insert_many(metrics)
    print(f"✅ Created {len(metrics)} performance metric records")
    
    # 5. Create some intelligence decisions
    decisions = []
    for campaign in campaigns[:4]:  # Just for first few campaigns
        for days_ago in range(7, 0, -1):
            decisions.append({
                "client_id": test_client_id,
                "campaign_id": campaign["campaign_id"],
                "sku_id": campaign["sku_id"],
                "platform": campaign["platform"],
                "decision_type": random.choice(["budget_increase", "budget_decrease", "no_action"]),
                "mode": campaign["optimization_mode"],
                "confidence_score": random.uniform(0.6, 0.95),
                "reasoning": f"ROAS {random.uniform(2.5, 4.0):.2f} vs target {campaign['target_roas']:.2f}",
                "old_budget": campaign["daily_budget"],
                "new_budget": campaign["daily_budget"] * random.uniform(0.95, 1.05),
                "budget_change_percent": random.uniform(-5, 5),
                "expected_impact": "Moderate optimization",
                "metrics_snapshot": {
                    "impressions": random.randint(800, 1200),
                    "conversions": random.randint(50, 100),
                    "spend": random.uniform(100, 200),
                    "revenue": random.uniform(300, 800),
                    "roas": random.uniform(2.5, 4.0)
                },
                "timestamp": datetime.utcnow() - timedelta(days=days_ago),
                "applied": True,
                "applied_at": datetime.utcnow() - timedelta(days=days_ago),
                "success_score": random.uniform(0.6, 0.9)
            })
    
    await db.intelligence_decisions.delete_many({"client_id": test_client_id})
    await db.intelligence_decisions.insert_many(decisions)
    print(f"✅ Created {len(decisions)} intelligence decisions")
    
    # 6. Create system benchmarks
    benchmarks = []
    for platform in [Platform.GOOGLE_ADS, Platform.META, Platform.TIKTOK]:
        benchmarks.append({
            "platform": platform.value,
            "industry": "Electronics",
            "region": "NA",
            "avg_ctr": random.uniform(1.5, 3.0),
            "avg_cpc": random.uniform(2.0, 5.0),
            "avg_cpa": random.uniform(40, 80),
            "avg_cvr": random.uniform(5, 12),
            "avg_roas": random.uniform(2.5, 4.0),
            "median_roas": random.uniform(2.8, 3.5),
            "p75_roas": random.uniform(3.5, 4.5),
            "p90_roas": random.uniform(4.0, 5.5),
            "sample_size": random.randint(50, 200),
            "confidence_level": random.uniform(0.85, 0.95),
            "timestamp": datetime.utcnow(),
            "month": datetime.utcnow().strftime("%Y-%m"),
            "metadata": {}
        })
    
    await db.system_benchmarks.delete_many({})
    await db.system_benchmarks.insert_many(benchmarks)
    print(f"✅ Created {len(benchmarks)} system benchmarks")
    
    print("\n🎉 Test data seeding complete!")
    print("\n📝 Test Account Credentials:")
    print(f"   Email: {test_client['email']}")
    print(f"   Password: password123")
    print(f"\n🚀 You can now:")
    print(f"   1. Login at: http://localhost:8000/docs")
    print(f"   2. Use email: {test_client['email']}")
    print(f"   3. Password: password123")
    print(f"   4. Explore campaigns, metrics, and run optimizations!")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_test_data())
