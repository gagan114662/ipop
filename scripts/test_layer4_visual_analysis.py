#!/usr/bin/env python3
"""
Universal Layer 4: Competitive Semiotics Tester

Tests Layer 4 with ANY set of images and brand copy.

Usage:
    python scripts/test_layer4_visual_analysis.py --images-path /path/to/images --brand-name "Brand Name"
    python scripts/test_layer4_visual_analysis.py --images-path /Users/gagan/Desktop/Sangi_Advertising_Concepts/instagram_full --brand-name "Sangi Advertising"
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.strategy_engine.analysis.layer4_competitive_semiotics import CompetitiveSemiotics


async def main():
    """Run Layer 4 test with ANY brand assets."""

    parser = argparse.ArgumentParser(description='Test Layer 4 with any brand assets')
    parser.add_argument('--images-path', required=True, help='Path to directory containing images')
    parser.add_argument('--brand-name', required=True, help='Brand name for analysis')
    parser.add_argument('--num-images', type=int, default=20, help='Number of images to analyze (default: 20)')
    parser.add_argument('--output-file', help='Output markdown file path (optional)')

    args = parser.parse_args()

    images_path = Path(args.images_path)
    brand_name = args.brand_name
    num_images = args.num_images

    if not images_path.exists():
        print(f"❌ Error: Path '{images_path}' does not exist")
        sys.exit(1)

    print("="*80)
    print("🎨 LAYER 4: COMPETITIVE SEMIOTICS TEST")
    print(f"   Brand: {brand_name}")
    print(f"   Images Path: {images_path}")
    print("="*80)

    analyzer = CompetitiveSemiotics()

    # ============================================================
    # TEST 1: Analyze Visual Codes
    # ============================================================
    print("\n📊 Test 1: Analyzing Visual Codes")
    print("-" * 60)

    image_files = list(images_path.glob("*.jpg")) + list(images_path.glob("*.png")) + list(images_path.glob("*.jpeg"))
    image_files = image_files[:num_images]

    print(f"   Loading {len(image_files)} images...")

    visual_codes = await analyzer.extract_visual_codes(
        images=[str(img) for img in image_files],
        brand_name=brand_name
    )

    print(f"   ✅ Extracted {len(visual_codes)} visual codes")
    print("\n   Top Visual Codes:")
    for code in visual_codes[:5]:
        print(f"     • {code.code_name}: {code.frequency:.0%} frequency")
        print(f"       Examples: {len(code.examples)} images")

    # ============================================================
    # TEST 2: Analyze Brand Messaging (Auto-detect from brand)
    # ============================================================
    print("\n📊 Test 2: Brand Messaging Analysis")
    print("-" * 60)

    # Use generic messaging samples for testing
    # In production, these would come from actual brand copy
    brand_copy = [
        "Premium quality products",
        "Innovative design solutions",
        "Transforming ideas into reality"
    ]
    print(f"   Using {len(brand_copy)} default messaging samples for analysis")

    verbal_codes = await analyzer.extract_verbal_codes(
        copy=brand_copy,
        brand_name=brand_name
    )

    print(f"\n   ✅ Analyzed {len(brand_copy)} messaging samples")
    print(f"   Dominant Themes: {', '.join(verbal_codes['dominant_themes'])}")
    print(f"   Brand Tone: {verbal_codes['tone']}")
    print(f"   Messaging Patterns: {', '.join(verbal_codes['messaging_patterns'])}")

    # ============================================================
    # TEST 3: Competitive Mapping (Generic Competitors)
    # ============================================================
    print("\n📊 Test 3: Competitive Semiotic Mapping")
    print("-" * 60)

    # Generic competitor archetypes (not brand-specific)
    competitors_data = {
        "Traditional Player": {
            "visual_codes": ["corporate", "professional", "conservative"],
            "verbal_codes": ["reliable", "established", "traditional"]
        },
        "Modern Innovator": {
            "visual_codes": ["minimalist", "bold", "geometric"],
            "verbal_codes": ["innovative", "modern", "cutting-edge"]
        },
        "Creative Boutique": {
            "visual_codes": ["artistic", "colorful", "eclectic"],
            "verbal_codes": ["creative", "unique", "personalized"]
        }
    }

    semiotic_map = await analyzer.build_semiotic_map(competitors_data)

    print(f"   ✅ Mapped {len(competitors_data)} competitor archetypes")
    print(f"\n   Competitor Positioning Clusters:")
    for comp, data in semiotic_map['competitor_positions'].items():
        print(f"     • {comp}: {data['positioning_cluster']}")

    # ============================================================
    # TEST 4: White Space Identification
    # ============================================================
    print("\n📊 Test 4: Identifying Positioning White Space")
    print("-" * 60)

    white_space = await analyzer.identify_white_space(competitors_data)

    print(f"   ✅ Found {len(white_space)} white space opportunities")
    print(f"\n   Top 3 Opportunities:")
    for i, opp in enumerate(white_space[:3], 1):
        print(f"\n   {i}. {opp['visual_opportunity'].title()} + {opp['verbal_opportunity'].title()}")
        print(f"      Differentiation Score: {opp['differentiation_score']:.2%}")

    # ============================================================
    # TEST 5: Competitive Comparison
    # ============================================================
    print("\n📊 Test 5: Competitive Market Analysis")
    print("-" * 60)

    brand_data = {
        "visual_codes": [code.code_name for code in visual_codes[:5]],
        "verbal_codes": verbal_codes['dominant_themes']
    }

    comparison = await analyzer.compare_brand_to_market(
        brand_data=brand_data,
        competitors_data=competitors_data
    )

    print(f"   ✅ Competitive comparison complete")
    print(f"\n   Similarity to Competitors:")
    for competitor, score in comparison['similarity_scores'].items():
        print(f"     • {competitor}: {score:.0%}")

    print(f"\n   Competitive Advantage:")
    print(f"     {comparison['competitive_advantage']}")

    # ============================================================
    # GENERATE REPORT
    # ============================================================
    print("\n" + "="*80)
    print("📄 GENERATING ANALYSIS REPORT")
    print("="*80)

    report = f"""# Layer 4: Competitive Semiotics Analysis

**Date**: {datetime.now().strftime("%B %d, %Y")}
**Brand**: {brand_name}
**Images Analyzed**: {len(image_files)}
**Source**: {images_path}

---

## Visual Identity

### Top Visual Codes

{chr(10).join(f"{i+1}. **{code.code_name}** - {code.frequency:.0%} frequency"
for i, code in enumerate(visual_codes[:5]))}

---

## Verbal Identity

**Themes:** {', '.join(verbal_codes['dominant_themes'])}
**Tone:** {verbal_codes['tone'].title()}
**Patterns:** {', '.join(verbal_codes['messaging_patterns'])}

---

## Competitive Positioning

### Similarity Scores

{chr(10).join(f"- **{comp}**: {score:.0%}" for comp, score in comparison['similarity_scores'].items())}

### Competitive Advantage

{comparison['competitive_advantage']}

### Differentiation Areas

{chr(10).join(f"- {area}" for area in comparison['differentiation_areas'][:5])}

---

## White Space Opportunities

{chr(10).join(f'''### Option {i+1}: {opp['visual_opportunity'].title()} × {opp['verbal_opportunity'].title()}
- **Differentiation**: {opp['differentiation_score']:.0%}
- **Rationale**: {opp['strategic_rationale']}
''' for i, opp in enumerate(white_space[:3]))}

---

**Analyst**: Claude Strategy Engine v1.0 - Layer 4
"""

    # Save report
    if args.output_file:
        output_path = Path(args.output_file)
    else:
        safe_brand_name = brand_name.lower().replace(' ', '_')
        output_path = project_root / f"LAYER4_ANALYSIS_{safe_brand_name.upper()}.md"

    with open(output_path, "w") as f:
        f.write(report)

    print(f"\n✅ Report saved to: {output_path}")
    print("\n" + "="*80)
    print("🎉 ANALYSIS COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   • Brand: {brand_name}")
    print(f"   • Images: {len(image_files)}")
    print(f"   • Visual codes: {len(visual_codes)}")
    print(f"   • White space opportunities: {len(white_space)}")
    print(f"\n💡 {comparison['competitive_advantage']}\n")


if __name__ == "__main__":
    asyncio.run(main())
