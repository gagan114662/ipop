"""
Standalone test script for Layer 3 contradiction fix validation.
Tests robust data extraction and meaningful fallback values.
"""
import sys
import asyncio
sys.path.insert(0, '/Users/gagan/Desktop/gagan_projects/strategy_develpment_ipop')

from app.strategy_engine.analysis.layer3_framework_dialectics import FrameworkDialectics


async def test_complete_data():
    """Test with complete product/user data"""
    print("\n🧪 Test 1: Complete Data")
    analyzer = FrameworkDialectics()

    product_data = {
        "product_promise": "luxury craftsmanship",
        "messaging_focus": ["premium quality", "exclusive designs"]
    }

    user_data = {
        "purchase_drivers": ["status", "social proof", "quality"],
        "stated_values": ["sustainability", "quality"],
        "actual_behavior": "buys for social status"
    }

    tension = await analyzer.find_product_user_tension(product_data, user_data)

    print(f"   Contradiction: {tension.contradiction}")
    print(f"   Human Truth: {tension.human_truth}")

    assert "luxury craftsmanship" in tension.contradiction or "status" in tension.contradiction
    assert len(tension.contradiction) > 20
    print("   ✅ PASSED")
    return True


async def test_empty_data():
    """Test with completely empty data"""
    print("\n🧪 Test 2: Empty Data (Anti-regression)")
    analyzer = FrameworkDialectics()

    product_data = {
        "product_promise": "",
        "messaging_focus": []
    }

    user_data = {
        "purchase_drivers": [],
        "stated_values": [],
        "actual_behavior": ""
    }

    tension = await analyzer.find_product_user_tension(product_data, user_data)

    print(f"   Contradiction: {tension.contradiction}")
    print(f"   Human Truth: {tension.human_truth}")

    # Should NOT have empty strings
    assert "Brand emphasizes ''" not in tension.contradiction
    assert len(tension.contradiction) > 20
    assert len(tension.human_truth) > 20
    print("   ✅ PASSED: No empty contradiction strings")
    return True


async def test_data_extraction_from_brand():
    """Test extracting structured data from raw brand data"""
    print("\n🧪 Test 3: Data Extraction from Real Brand Structure")
    analyzer = FrameworkDialectics()

    brand_data = {
        "products": [
            {"name": "Sherwani", "price": "₹67,000", "description": "Handcrafted luxury embroidery"},
            {"name": "Bandhgala", "price": "₹79,000", "description": "Premium designer wear"}
        ],
        "brand_messaging": "Modern Craftsmanship Meets Tradition",
        "category_stated": "Ethnic Menswear",
        "currency": "INR",
        "region": "India",
        "price_range": (25500, 79000)
    }

    # Test product data extraction
    product_data = analyzer._extract_product_data(brand_data)
    print(f"   Product Promise: {product_data['product_promise']}")
    print(f"   Messaging Focus: {product_data['messaging_focus']}")
    assert product_data["product_promise"] != ""
    assert len(product_data["messaging_focus"]) > 0

    # Test user data extraction
    user_data = analyzer._extract_user_data(brand_data)
    print(f"   Purchase Drivers: {user_data['purchase_drivers']}")
    assert len(user_data["purchase_drivers"]) > 0

    # Test space data extraction
    space_data = analyzer._extract_space_data(brand_data)
    print(f"   Market Position: {space_data['market_position']}")
    assert space_data["market_position"] != ""

    # Test time data extraction
    time_data = analyzer._extract_time_data(brand_data)
    print(f"   Purchase Occasion: {time_data['purchase_occasion']}")
    assert time_data["purchase_occasion"] != ""

    print("   ✅ PASSED: All data extracted correctly")
    return True


async def test_analyze_brand_full():
    """Test full brand analysis with raw data"""
    print("\n🧪 Test 4: Full Brand Analysis (analyze_brand method)")
    analyzer = FrameworkDialectics()

    brand_data = {
        "products": [
            {"name": "Designer Sherwani", "price": "₹67,000"},
            {"name": "Luxury Bandhgala", "price": "₹79,000"}
        ],
        "brand_messaging": "Modern Craftsmanship Meets Tradition",
        "category_stated": "Ethnic Menswear",
        "currency": "INR",
        "region": "India",
        "price_range": (25500, 79000)
    }

    tensions = await analyzer.analyze_brand(brand_data)

    print(f"   Found {len(tensions)} tensions")
    for i, tension in enumerate(tensions, 1):
        print(f"   Tension {i} ({tension.tension_type}):")
        print(f"      Contradiction: {tension.contradiction[:80]}...")
        print(f"      Human Truth: {tension.human_truth[:80]}...")

        # Validate no empty strings
        assert "Brand emphasizes ''" not in tension.contradiction
        assert len(tension.contradiction) > 20
        assert len(tension.human_truth) > 20

    assert len(tensions) > 0
    print("   ✅ PASSED: Full analysis generates meaningful tensions")
    return True


async def test_space_time_empty_data():
    """Test space-time tension with empty data"""
    print("\n🧪 Test 5: Space-Time Tension with Empty Data")
    analyzer = FrameworkDialectics()

    space_data = {
        "market_position": "",
        "price_point": ""
    }

    time_data = {
        "purchase_occasion": "",
        "consideration_period": ""
    }

    tension = await analyzer.find_space_time_tension(space_data, time_data)

    print(f"   Contradiction: {tension.contradiction}")

    # Should not have meaningless empty strings like "Market position () matches purchase timing ()"
    assert tension.contradiction != "Market position () matches purchase timing ()"
    assert len(tension.contradiction) > 20
    print("   ✅ PASSED: Meaningful fallback for space-time tension")
    return True


async def test_indian_wedding_brand():
    """Test with Indian wedding brand (Sarab Khanijou-like)"""
    print("\n🧪 Test 6: Indian Wedding Brand Analysis")
    analyzer = FrameworkDialectics()

    brand_data = {
        "products": [
            {"name": "3D Embroidery Waistcoat Set", "price": "₹67,000"},
            {"name": "Aqua Open Bandhgala Set", "price": "₹79,000"},
            {"name": "Black Angrakha Cut Kurta", "price": "₹25,500"}
        ],
        "brand_messaging": "Modern Craftsmanship Meets Tradition",
        "category_stated": "Men's Indian Formal Wear",
        "currency": "INR",
        "region": "India",
        "price_range": (25500, 79500)
    }

    tensions = await analyzer.analyze_brand(brand_data)

    print(f"   Found {len(tensions)} tensions:")
    for tension in tensions:
        print(f"\n   {tension.tension_type.upper()}:")
        print(f"      {tension.contradiction}")

        # Critical validation: No empty strings
        assert "Brand emphasizes ''" not in tension.contradiction
        assert "''" not in tension.contradiction
        assert len(tension.contradiction) > 30
        assert len(tension.human_truth) > 30

    print("\n   ✅ PASSED: Indian wedding brand generates meaningful tensions")
    return True


async def main():
    """Run all tests"""
    print("="*60)
    print("🔍 LAYER 3 CONTRADICTION FIX VALIDATION")
    print("="*60)

    tests = [
        test_complete_data,
        test_empty_data,
        test_data_extraction_from_brand,
        test_analyze_brand_full,
        test_space_time_empty_data,
        test_indian_wedding_brand,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    print("="*60)

    if failed == 0:
        print("✅ ALL TESTS PASSED - Layer 3 contradiction fix validated!")
        return 0
    else:
        print(f"❌ {failed} tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
