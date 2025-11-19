"""
Seed the reference_creatives database with award-winning examples.

This script populates the database with curated award-winning ad creatives
that will be used as references for AI generation.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


# Sample award-winning creatives (replace with real examples)
REFERENCE_CREATIVES = [
    # Fashion
    {
        "category": "fashion",
        "image_url": "https://picsum.photos/seed/fashion1/1200/628",
        "title": "Nike Air Max Campaign 2023",
        "description": "Award-winning sneaker campaign with bold typography and dynamic composition",
        "platform": "meta",
        "quality_score": 0.95,
        "is_award_winning": True,
        "award_info": "Cannes Lions Silver 2023",
        "brand": "Nike",
        "year": 2023,
        "design_patterns": ["bold_typography", "action_photography", "vibrant_colors"],
        "color_scheme": ["#FF0000", "#000000", "#FFFFFF"],
        "engagement_rate": 8.5
    },
    {
        "category": "fashion",
        "image_url": "https://picsum.photos/seed/fashion2/1200/628",
        "title": "Zara Minimal Elegance",
        "description": "Minimalist fashion ad with clean composition",
        "platform": "instagram",
        "quality_score": 0.88,
        "is_award_winning": True,
        "award_info": "D&AD Yellow Pencil 2022",
        "brand": "Zara",
        "year": 2022,
        "design_patterns": ["minimalist", "centered_composition", "neutral_tones"],
        "color_scheme": ["#F5F5F5", "#2C2C2C"],
        "engagement_rate": 7.2
    },

    # Tech
    {
        "category": "tech",
        "image_url": "https://picsum.photos/seed/tech1/1200/628",
        "title": "Apple iPhone Pro Campaign",
        "description": "Premium product photography with elegant simplicity",
        "platform": "meta",
        "quality_score": 0.98,
        "is_award_winning": True,
        "award_info": "One Show Gold 2023",
        "brand": "Apple",
        "year": 2023,
        "design_patterns": ["product_focus", "minimalist", "premium_feel"],
        "color_scheme": ["#000000", "#FFFFFF", "#1D1D1F"],
        "engagement_rate": 9.1
    },
    {
        "category": "tech",
        "image_url": "https://picsum.photos/seed/tech2/1200/628",
        "title": "Samsung Galaxy Innovation",
        "description": "Dynamic tech ad with bold visuals",
        "platform": "google",
        "quality_score": 0.89,
        "is_award_winning": True,
        "award_info": "Clio Awards Bronze 2023",
        "brand": "Samsung",
        "year": 2023,
        "design_patterns": ["bold_colors", "dynamic_composition", "feature_callouts"],
        "color_scheme": ["#1428A0", "#FF6B00"],
        "engagement_rate": 7.8
    },

    # Beauty
    {
        "category": "beauty",
        "image_url": "https://picsum.photos/seed/beauty1/1200/628",
        "title": "Fenty Beauty Inclusive Campaign",
        "description": "Diverse beauty ad with warm tones and close-up photography",
        "platform": "instagram",
        "quality_score": 0.93,
        "is_award_winning": True,
        "award_info": "Webby Awards Winner 2023",
        "brand": "Fenty Beauty",
        "year": 2023,
        "design_patterns": ["closeup_photography", "warm_tones", "diversity"],
        "color_scheme": ["#D4A574", "#8B5A3C", "#FFF5F0"],
        "engagement_rate": 8.9
    },
    {
        "category": "beauty",
        "image_url": "https://picsum.photos/seed/beauty2/1200/628",
        "title": "Glossier Natural Beauty",
        "description": "Minimalist beauty ad with natural lighting",
        "platform": "meta",
        "quality_score": 0.87,
        "is_award_winning": True,
        "award_info": "Shorty Awards Gold 2022",
        "brand": "Glossier",
        "year": 2022,
        "design_patterns": ["natural_lighting", "soft_colors", "lifestyle_photography"],
        "color_scheme": ["#FFF4F0", "#FF6B9D", "#002FA7"],
        "engagement_rate": 7.5
    },

    # Food
    {
        "category": "food",
        "image_url": "https://picsum.photos/seed/food1/1200/628",
        "title": "McDonald's Fresh Ingredients",
        "description": "Food photography with vibrant colors and appetizing composition",
        "platform": "meta",
        "quality_score": 0.91,
        "is_award_winning": True,
        "award_info": "Effie Awards Gold 2023",
        "brand": "McDonald's",
        "year": 2023,
        "design_patterns": ["food_photography", "vibrant_colors", "appetite_appeal"],
        "color_scheme": ["#FFC72C", "#DA291C", "#FFFFFF"],
        "engagement_rate": 8.3
    },
    {
        "category": "food",
        "image_url": "https://picsum.photos/seed/food2/1200/628",
        "title": "Starbucks Seasonal Campaign",
        "description": "Lifestyle food ad with warm atmosphere",
        "platform": "instagram",
        "quality_score": 0.85,
        "is_award_winning": True,
        "award_info": "Facebook Awards Finalist 2023",
        "brand": "Starbucks",
        "year": 2023,
        "design_patterns": ["lifestyle", "warm_tones", "cozy_atmosphere"],
        "color_scheme": ["#00704A", "#D4AF37", "#FFFFFF"],
        "engagement_rate": 7.1
    },

    # Ecommerce
    {
        "category": "ecommerce",
        "image_url": "https://picsum.photos/seed/ecom1/1200/628",
        "title": "Amazon Prime Day Campaign",
        "description": "Dynamic ecommerce ad with clear CTAs and product showcase",
        "platform": "google",
        "quality_score": 0.90,
        "is_award_winning": True,
        "award_info": "Google Ads Excellence 2023",
        "brand": "Amazon",
        "year": 2023,
        "design_patterns": ["product_grid", "bold_cta", "promotional_design"],
        "color_scheme": ["#FF9900", "#232F3E", "#FFFFFF"],
        "engagement_rate": 8.0
    },
    {
        "category": "ecommerce",
        "image_url": "https://picsum.photos/seed/ecom2/1200/628",
        "title": "Shopify Success Stories",
        "description": "Trust-building ecommerce ad with social proof",
        "platform": "meta",
        "quality_score": 0.86,
        "is_award_winning": True,
        "award_info": "IAB MIXX Awards 2022",
        "brand": "Shopify",
        "year": 2022,
        "design_patterns": ["social_proof", "lifestyle", "success_stories"],
        "color_scheme": ["#96BF48", "#5E8E3E", "#FFFFFF"],
        "engagement_rate": 7.4
    },

    # Automotive
    {
        "category": "automotive",
        "image_url": "https://picsum.photos/seed/auto1/1200/628",
        "title": "Tesla Model S Campaign",
        "description": "Sleek automotive ad with futuristic design",
        "platform": "meta",
        "quality_score": 0.94,
        "is_award_winning": True,
        "award_info": "Automotive Brand Contest Winner 2023",
        "brand": "Tesla",
        "year": 2023,
        "design_patterns": ["sleek_design", "futuristic", "product_hero"],
        "color_scheme": ["#E82127", "#000000", "#FFFFFF"],
        "engagement_rate": 8.7
    },

    # Travel
    {
        "category": "travel",
        "image_url": "https://picsum.photos/seed/travel1/1200/628",
        "title": "Airbnb Experiences",
        "description": "Wanderlust-inducing travel ad with stunning photography",
        "platform": "instagram",
        "quality_score": 0.92,
        "is_award_winning": True,
        "award_info": "Travel Marketing Awards Gold 2023",
        "brand": "Airbnb",
        "year": 2023,
        "design_patterns": ["wanderlust", "destination_photography", "emotional"],
        "color_scheme": ["#FF5A5F", "#00A699", "#FFFFFF"],
        "engagement_rate": 8.6
    },

    # Finance
    {
        "category": "finance",
        "image_url": "https://picsum.photos/seed/finance1/1200/628",
        "title": "PayPal Trust Campaign",
        "description": "Trust-building fintech ad with clean design",
        "platform": "linkedin",
        "quality_score": 0.88,
        "is_award_winning": True,
        "award_info": "Fintech Marketing Awards 2023",
        "brand": "PayPal",
        "year": 2023,
        "design_patterns": ["trust_signals", "clean_design", "professional"],
        "color_scheme": ["#0070BA", "#1F2937", "#FFFFFF"],
        "engagement_rate": 6.9
    },

    # Health
    {
        "category": "health",
        "image_url": "https://picsum.photos/seed/health1/1200/628",
        "title": "Peloton Fitness Journey",
        "description": "Motivational health ad with active lifestyle imagery",
        "platform": "meta",
        "quality_score": 0.89,
        "is_award_winning": True,
        "award_info": "Health & Wellness Marketing Awards 2023",
        "brand": "Peloton",
        "year": 2023,
        "design_patterns": ["motivational", "action_photography", "lifestyle"],
        "color_scheme": ["#D71920", "#000000", "#FFFFFF"],
        "engagement_rate": 7.7
    },

    # Real Estate
    {
        "category": "real_estate",
        "image_url": "https://picsum.photos/seed/realestate1/1200/628",
        "title": "Zillow Home Dreams",
        "description": "Aspirational real estate ad with beautiful home photography",
        "platform": "google",
        "quality_score": 0.87,
        "is_award_winning": True,
        "award_info": "Real Estate Marketing Awards 2023",
        "brand": "Zillow",
        "year": 2023,
        "design_patterns": ["aspirational", "home_photography", "lifestyle"],
        "color_scheme": ["#0074E4", "#FFFFFF", "#2A2F38"],
        "engagement_rate": 7.3
    }
]


async def seed_database():
    """Seed the reference_creatives collection."""
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    try:
        # Check if collection already has data
        count = await db.reference_creatives.count_documents({})

        if count > 0:
            print(f"⚠️  Collection already has {count} documents.")
            response = input("Do you want to clear and reseed? (yes/no): ")
            if response.lower() != "yes":
                print("Aborted.")
                return

            # Clear existing data
            print("Clearing existing data...")
            await db.reference_creatives.delete_many({})

        # Insert reference creatives
        print(f"Inserting {len(REFERENCE_CREATIVES)} reference creatives...")
        result = await db.reference_creatives.insert_many(REFERENCE_CREATIVES)
        print(f"✅ Inserted {len(result.inserted_ids)} documents")

        # Create indexes
        print("Creating indexes...")
        await db.reference_creatives.create_index([("category", 1), ("quality_score", -1)])
        await db.reference_creatives.create_index("is_award_winning")
        await db.reference_creatives.create_index("platform")
        print("✅ Indexes created")

        # Create reference_cache collection with TTL index
        print("Setting up reference_cache collection...")
        await db.reference_cache.create_index("cache_key", unique=True)
        await db.reference_cache.create_index("expires_at", expireAfterSeconds=0)
        print("✅ Cache collection configured")

        # Display summary
        print("\n" + "="*60)
        print("DATABASE SEEDED SUCCESSFULLY")
        print("="*60)

        # Count by category
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        categories = await db.reference_creatives.aggregate(pipeline).to_list(None)

        print("\nReferences by category:")
        for cat in categories:
            print(f"  - {cat['_id']}: {cat['count']}")

        print(f"\nTotal: {len(REFERENCE_CREATIVES)} award-winning references")
        print("\n✅ Ready to generate AI creatives!")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
