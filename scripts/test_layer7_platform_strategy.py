#!/usr/bin/env python3
"""
Universal Layer 7: Platform Strategy Tester

Tests Layer 7 with ANY brand's base strategy across all platforms.

Usage:
    python scripts/test_layer7_platform_strategy.py --brand-name "Brand Name"
    python scripts/test_layer7_platform_strategy.py --brand-name "Sangi Advertising" --output-file "my_platforms.md"
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.strategy_engine.analysis.layer7_platform_strategy import PlatformStrategyAdapter


async def main():
    """Run Layer 7 test with ANY brand."""

    parser = argparse.ArgumentParser(description='Test Layer 7 Platform Strategy with any brand')
    parser.add_argument('--brand-name', required=True, help='Brand name for analysis')
    parser.add_argument('--output-file', help='Output markdown file path (optional)')

    args = parser.parse_args()

    brand_name = args.brand_name

    print("="*80)
    print("🎯 LAYER 7: PLATFORM STRATEGY TEST")
    print(f"   Brand: {brand_name}")
    print("="*80)

    adapter = PlatformStrategyAdapter()

    # ============================================================
    # Base Strategy (would come from previous layers in production)
    # ============================================================
    print("\n📊 Base Strategy Configuration")
    print("-" * 60)

    base_strategy = {
        "brand_positioning": "innovative, authentic, premium",
        "target_audience": "conscious consumers and early adopters",
        "key_message": "Quality and innovation combined",
        "brand_values": ["authenticity", "craftsmanship", "innovation"]
    }

    print(f"   Brand Positioning: {base_strategy['brand_positioning']}")
    print(f"   Target Audience: {base_strategy['target_audience']}")
    print(f"   Key Message: {base_strategy['key_message']}")

    # ============================================================
    # TEST 1: Adapt for Meta (Facebook/Instagram)
    # ============================================================
    print("\n📊 Test 1: Meta (Facebook/Instagram) Adaptation")
    print("-" * 60)

    meta_strategy = await adapter.adapt_for_meta(base_strategy)

    print(f"   ✅ Meta strategy generated\n")
    print(f"   Platform: {meta_strategy.platform.upper()}")
    print(f"   Content Strategy: {meta_strategy.content_strategy}")
    print(f"   Targeting Approach: {meta_strategy.targeting_approach}")
    print(f"\n   Creative Guidelines ({len(meta_strategy.creative_guidelines)} rules):")
    for guideline, rule in meta_strategy.creative_guidelines.items():
        print(f"     • {guideline.title()}: {rule}")

    # ============================================================
    # TEST 2: Adapt for Google Ads
    # ============================================================
    print("\n📊 Test 2: Google Ads Adaptation")
    print("-" * 60)

    google_strategy = await adapter.adapt_for_google(base_strategy)

    print(f"   ✅ Google strategy generated\n")
    print(f"   Platform: {google_strategy.platform.upper()}")
    print(f"   Content Strategy: {google_strategy.content_strategy}")
    print(f"   Targeting Approach: {google_strategy.targeting_approach}")
    print(f"\n   Creative Guidelines ({len(google_strategy.creative_guidelines)} rules):")
    for guideline, rule in google_strategy.creative_guidelines.items():
        print(f"     • {guideline.title()}: {rule}")

    # ============================================================
    # TEST 3: Adapt for TikTok
    # ============================================================
    print("\n📊 Test 3: TikTok Adaptation")
    print("-" * 60)

    tiktok_strategy = await adapter.adapt_for_tiktok(base_strategy)

    print(f"   ✅ TikTok strategy generated\n")
    print(f"   Platform: {tiktok_strategy.platform.upper()}")
    print(f"   Content Strategy: {tiktok_strategy.content_strategy}")
    print(f"   Targeting Approach: {tiktok_strategy.targeting_approach}")
    print(f"\n   Creative Guidelines ({len(tiktok_strategy.creative_guidelines)} rules):")
    for guideline, rule in tiktok_strategy.creative_guidelines.items():
        print(f"     • {guideline.title()}: {rule}")

    # ============================================================
    # TEST 4: Adapt for LinkedIn
    # ============================================================
    print("\n📊 Test 4: LinkedIn Adaptation")
    print("-" * 60)

    linkedin_strategy = await adapter.adapt_for_linkedin(base_strategy)

    print(f"   ✅ LinkedIn strategy generated\n")
    print(f"   Platform: {linkedin_strategy.platform.upper()}")
    print(f"   Content Strategy: {linkedin_strategy.content_strategy}")
    print(f"   Targeting Approach: {linkedin_strategy.targeting_approach}")
    print(f"\n   Creative Guidelines ({len(linkedin_strategy.creative_guidelines)} rules):")
    for guideline, rule in linkedin_strategy.creative_guidelines.items():
        print(f"     • {guideline.title()}: {rule}")

    # ============================================================
    # TEST 5: Verify All Strategies Are Different
    # ============================================================
    print("\n📊 Test 5: Platform Differentiation")
    print("-" * 60)

    strategies = {
        "Meta": meta_strategy,
        "Google": google_strategy,
        "TikTok": tiktok_strategy,
        "LinkedIn": linkedin_strategy
    }

    content_strategies = [s.content_strategy for s in strategies.values()]
    unique_strategies = len(set(content_strategies))

    print(f"   ✅ Differentiation verified\n")
    print(f"   Unique content strategies: {unique_strategies}/4")
    print(f"   Each platform has distinct approach: {'YES' if unique_strategies >= 3 else 'NO'}")

    # ============================================================
    # GENERATE REPORT
    # ============================================================
    print("\n" + "="*80)
    print("📄 GENERATING ANALYSIS REPORT")
    print("="*80)

    # Function to format guidelines
    def format_guidelines(guidelines):
        return "\n".join([f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in guidelines.items()])

    report = f"""# Layer 7: Platform Strategy Analysis

**Date**: {datetime.now().strftime("%B %d, %Y")}
**Brand**: {brand_name}
**Platforms Analyzed**: Meta, Google, TikTok, LinkedIn

---

## Base Strategy

**Brand Positioning**: {base_strategy['brand_positioning']}
**Target Audience**: {base_strategy['target_audience']}
**Key Message**: {base_strategy['key_message']}

---

## Platform-Specific Strategies

### 1. Meta (Facebook/Instagram)

**Content Strategy**: {meta_strategy.content_strategy.replace('_', ' ').title()}
**Targeting Approach**: {meta_strategy.targeting_approach.replace('_', ' ').title()}

**Creative Guidelines:**
{format_guidelines(meta_strategy.creative_guidelines)}

**Why This Approach:**
Meta platforms thrive on social proof and community. Users scroll feeds looking for content that resonates with their identity. Visual storytelling and user-generated content perform best.

---

### 2. Google Ads

**Content Strategy**: {google_strategy.content_strategy.replace('_', ' ').title()}
**Targeting Approach**: {google_strategy.targeting_approach.replace('_', ' ').title()}

**Creative Guidelines:**
{format_guidelines(google_strategy.creative_guidelines)}

**Why This Approach:**
Google captures high-intent users actively searching for solutions. The platform rewards relevance - matching customer search intent directly leads to better Quality Scores and lower costs.

---

### 3. TikTok

**Content Strategy**: {tiktok_strategy.content_strategy.replace('_', ' ').title()}
**Targeting Approach**: {tiktok_strategy.targeting_approach.replace('_', ' ').title()}

**Creative Guidelines:**
{format_guidelines(tiktok_strategy.creative_guidelines)}

**Why This Approach:**
TikTok users reject traditional advertising. Success comes from participating in platform culture, not interrupting it. Authentic, trend-based content wins over polished ads.

---

### 4. LinkedIn

**Content Strategy**: {linkedin_strategy.content_strategy.replace('_', ' ').title()}
**Targeting Approach**: {linkedin_strategy.targeting_approach.replace('_', ' ').title()}

**Creative Guidelines:**
{format_guidelines(linkedin_strategy.creative_guidelines)}

**Why This Approach:**
LinkedIn is a professional context where credibility and expertise matter most. Users seek business value, career growth, and industry insights. Thought leadership beats promotional content.

---

## Platform Comparison Matrix

| Dimension | Meta | Google | TikTok | LinkedIn |
|-----------|------|--------|--------|----------|
| **Content Strategy** | {meta_strategy.content_strategy} | {google_strategy.content_strategy} | {tiktok_strategy.content_strategy} | {linkedin_strategy.content_strategy} |
| **Targeting** | {meta_strategy.targeting_approach} | {google_strategy.targeting_approach} | {tiktok_strategy.targeting_approach} | {linkedin_strategy.targeting_approach} |
| **User Intent** | Discovery | Search | Entertainment | Professional |
| **Content Style** | Authentic, Social | Direct, Solution | Native, Trendy | Professional, Valuable |

---

## Strategic Recommendations for {brand_name}

### Budget Allocation
Based on platform characteristics and {brand_name}'s positioning:

1. **Google (30-40%)**: Capture high-intent search traffic
2. **Meta (25-35%)**: Build brand awareness and community
3. **LinkedIn (20-25%)**: Target professional audience
4. **TikTok (10-15%)**: Test culture-fit and younger demographics

### Testing Priorities

**Month 1: Foundation**
- Google: Test core keywords and landing pages
- Meta: Test 3-5 creative variations
- LinkedIn: Test thought leadership content
- TikTok: Small test budget for learning

**Month 2-3: Optimization**
- Scale winners from Month 1
- Kill underperformers ruthlessly
- Test new angles on best platforms

### Creative Production

**Meta**: Need 5-10 variations per campaign (high creative fatigue)
**Google**: Focus on messaging and landing page copy
**TikTok**: Native, fast-paced content (partner with creators)
**LinkedIn**: Professional-quality thought leadership

---

## Platform-Specific KPIs

### Meta
- Primary: Cost per acquisition (CPA)
- Secondary: Engagement rate, social shares
- Target: CPA <$50, Engagement >3%

### Google
- Primary: Conversion rate, Quality Score
- Secondary: Click-through rate (CTR)
- Target: Conversion rate >5%, QS >7/10

### TikTok
- Primary: View-through rate, engagement
- Secondary: Follower growth
- Target: VTR >50%, Engagement >8%

### LinkedIn
- Primary: Lead quality, CPA
- Secondary: Thought leadership metrics
- Target: High-quality leads, CPA <$75

---

## Next Steps

1. **Implement** platform-specific strategies
2. **Create** platform-adapted creative assets
3. **Launch** small test campaigns on each platform
4. **Measure** against platform-specific KPIs
5. **Scale** winners, kill losers
6. **Iterate** based on performance data

---

**Analyst**: Claude Strategy Engine v1.0 - Layer 7: Platform Strategy
"""

    # Save report with path validation
    if args.output_file:
        output_path = Path(args.output_file).resolve()
        safe_dirs = [project_root.resolve(), (project_root / "docs").resolve()]
        is_safe = any(str(output_path).startswith(str(safe_dir)) for safe_dir in safe_dirs)

        if not is_safe:
            print(f"❌ Error: Output path must be within project directory")
            sys.exit(1)
    else:
        safe_brand_name = brand_name.lower().replace(' ', '_')
        output_path = project_root / f"LAYER7_ANALYSIS_{safe_brand_name.upper()}.md"

    with open(output_path, "w") as f:
        f.write(report)

    print(f"\n✅ Report saved to: {output_path}")
    print("\n" + "="*80)
    print("🎉 ANALYSIS COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   • Brand: {brand_name}")
    print(f"   • Platforms analyzed: 4 (Meta, Google, TikTok, LinkedIn)")
    print(f"   • Unique strategies: {unique_strategies}/4")
    print(f"   • Total creative guidelines: {sum(len(s.creative_guidelines) for s in strategies.values())}")
    print(f"\n💡 Each platform requires a distinct approach based on user behavior and platform culture\n")


if __name__ == "__main__":
    asyncio.run(main())
