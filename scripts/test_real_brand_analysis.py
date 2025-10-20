"""Test strategic analysis with real brand: Sarab Khanijou"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.strategy_engine.analysis.layer1_category_archaeology import CategoryArchaeology
from app.strategy_engine.analysis.layer2_cultural_cartography import CulturalCartography
from app.strategy_engine.analysis.layer3_framework_dialectics import FrameworkDialectics


async def analyze_sarab_khanijou():
    """Analyze Sarab Khanijou brand using Layers 1-3"""

    print("=" * 80)
    print("STRATEGIC ANALYSIS: Sarab Khanijou")
    print("URL: https://sarabkhanijou.com/")
    print("=" * 80)
    print()

    # Brand data from website scraping
    brand_data = {
        "brand_name": "Sarab Khanijou",
        "url": "https://sarabkhanijou.com/",
        "products": [
            {
                "name": "3D Embroidery Waistcoat Set",
                "price": 67000,
                "type": "Waistcoat Set"
            },
            {
                "name": "Aqua Dhagai Sherwani Highlighted With 3D Thread Work And Pearl",
                "price": 74000,
                "type": "Sherwani Set"
            },
            {
                "name": "Aqua Open Bandhgala Set",
                "price": 79000,
                "type": "Bandhgala Set"
            },
            {
                "name": "Black Bandhgala With Pink Thread And Rivet Work",
                "price": 55500,
                "type": "Bandhgala Set"
            },
            {
                "name": "Banarasi Silk Sherwani",
                "price": 62500,
                "type": "Sherwani Set"
            },
            {
                "name": "Black Angrakha Cut Kurta",
                "price": 25500,
                "type": "Kurta Set"
            },
            {
                "name": "Akshay Kumar in Green Angrakha Cut Bandhgala",
                "price": 46500,
                "type": "Celebrity Closet"
            },
            {
                "name": "Ayushmann Khurrana in Off White Jacquard Tuxedo",
                "price": 67000,
                "type": "Celebrity Closet"
            }
        ],
        "category_stated": "Men's Indian Formal Wear / Ethnic Menswear",
        "price_range": (25500, 79500),  # INR pricing
        "brand_messaging": "Modern Craftsmanship Meets Tradition – Explore the New Drop",
        "about": "Designer ethnic menswear featuring waistcoats, bandhgalas, sherwanis, kurta sets, tuxedos, and indo-western styles. Known for celebrity clientele including Akshay Kumar, Ayushmann Khurrana, Armaan Malik.",
        "target_market": "India (INR pricing)",
        "product_categories": [
            "Waistcoat Set",
            "Bandhgala Set",
            "Sherwani Set",
            "Kurta Set",
            "Tuxedo",
            "Co-ord Set & Jacket",
            "Suit Set",
            "Indowestern",
            "Celebrity Closet"
        ]
    }

    # LAYER 1: Category Archaeology
    print("🔍 LAYER 1: CATEGORY ARCHAEOLOGY")
    print("-" * 80)

    archaeology = CategoryArchaeology()
    category_analysis = await archaeology.analyze(brand_data)

    print(f"Stated Category: {category_analysis.stated_category}")
    print(f"Functional Category: {category_analysis.functional_category}")
    print(f"Emotional Category: {category_analysis.emotional_category}")
    print(f"Social Category: {category_analysis.social_category}")
    print(f"Market Maturity: {category_analysis.maturity}")
    print(f"Strategic Implication: {category_analysis.strategic_implication}")
    print()

    # Real competitors
    category_data = {
        "stated_category": category_analysis.stated_category,
        "emotional_job": category_analysis.emotional_category,
        "social_job": category_analysis.social_category
    }

    competitors = await archaeology.identify_real_competitors(category_data)
    print(f"Real Competitors ({len(competitors)}):")
    for comp in competitors:
        print(f"  - {comp}")
    print()

    # LAYER 2: Cultural Cartography
    print("🌍 LAYER 2: CULTURAL CARTOGRAPHY")
    print("-" * 80)

    cartography = CulturalCartography()
    cultural_landscape = await cartography.analyze(category=category_analysis.stated_category)

    print(f"Macro Trends Detected: {len(cultural_landscape.macro_trends)}")
    for i, trend in enumerate(cultural_landscape.macro_trends[:5], 1):  # Top 5
        print(f"\n  {i}. {trend.trend_name}")
        print(f"     Description: {trend.description}")
        print(f"     Strength: {trend.strength * 10:.1f}/10")
        if trend.evidence:
            print(f"     Evidence: {', '.join(trend.evidence[:3])}")
    print()

    print(f"\nValue Shifts Detected: {len(cultural_landscape.value_shifts)}")
    for i, shift in enumerate(cultural_landscape.value_shifts[:5], 1):  # Top 5
        print(f"\n  {i}. {shift.old_value} → {shift.new_value}")
        print(f"     Strength: {shift.strength * 10:.1f}/10")
        if shift.evidence:
            print(f"     Evidence: {', '.join(shift.evidence[:3])}")
    print()

    # LAYER 3: Framework Dialectics
    print("⚡ LAYER 3: FRAMEWORK DIALECTICS (Tensions)")
    print("-" * 80)

    dialectics = FrameworkDialectics()

    # Prepare data for tension analysis
    analysis_data = {
        "product": {
            "promise": brand_data.get("brand_messaging", ""),
            "category": category_analysis.stated_category,
            "functional_job": category_analysis.functional_category,
            "price_range": brand_data.get("price_range")
        },
        "user": {
            "emotional_job": category_analysis.emotional_category,
            "social_job": category_analysis.social_category
        },
        "space": {
            "market": "premium",  # Based on pricing
            "stated_category": brand_data.get("category_stated"),
            "functional_category": category_analysis.functional_category
        },
        "time": {
            "purchase": "considered",  # Ethnic formal wear is considered purchase
            "usage": "episodic"  # Weddings, ceremonies
        }
    }

    tensions = await dialectics.find_all_tensions(analysis_data)

    print(f"Tensions Identified: {len(tensions)}")
    for i, tension in enumerate(tensions, 1):
        print(f"\n{'='*60}")
        print(f"TENSION {i}: {tension.tension_type}")
        print(f"{'='*60}")
        print(f"Contradiction: {tension.contradiction}")
        print(f"\nHuman Truth: {tension.human_truth}")
        print(f"\nStrategic Implication: {tension.strategic_implication}")

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()

    # Return data for further analysis
    return {
        "category_analysis": category_analysis,
        "cultural_landscape": cultural_landscape,
        "tensions": tensions,
        "competitors": competitors
    }


if __name__ == "__main__":
    results = asyncio.run(analyze_sarab_khanijou())
