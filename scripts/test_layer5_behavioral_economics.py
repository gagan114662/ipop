#!/usr/bin/env python3
"""
Universal Layer 5: Behavioral Economics Tester

Tests Layer 5 with ANY brand's behavioral data.

Usage:
    python scripts/test_layer5_behavioral_economics.py --brand-name "Brand Name"
    python scripts/test_layer5_behavioral_economics.py --brand-name "Sangi Advertising" --output-file "my_analysis.md"
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.strategy_engine.analysis.layer5_behavioral_economics import BehavioralEconomics


async def main():
    """Run Layer 5 test with ANY brand."""

    parser = argparse.ArgumentParser(description='Test Layer 5 Behavioral Economics with any brand')
    parser.add_argument('--brand-name', required=True, help='Brand name for analysis')
    parser.add_argument('--output-file', help='Output markdown file path (optional)')

    args = parser.parse_args()

    brand_name = args.brand_name

    print("="*80)
    print("🧠 LAYER 5: BEHAVIORAL ECONOMICS TEST")
    print(f"   Brand: {brand_name}")
    print("="*80)

    analyzer = BehavioralEconomics()

    # ============================================================
    # TEST 1: Identify Active Biases
    # ============================================================
    print("\n📊 Test 1: Identifying Active Cognitive Biases")
    print("-" * 60)

    # Sample purchase behavior data (in production, this would come from analytics)
    purchase_data = {
        "average_consideration_time": "2_hours",  # Fast decision
        "review_dependency": "high",  # Social proof seeking
        "price_sensitivity": "medium",
        "brand_loyalty": "low",
        "impulse_purchase_rate": 0.45,
        "peer_influence_score": 0.78
    }

    print(f"   Analyzing purchase behavior patterns...")
    print(f"   - Consideration time: {purchase_data['average_consideration_time']}")
    print(f"   - Review dependency: {purchase_data['review_dependency']}")
    print(f"   - Impulse purchase rate: {purchase_data['impulse_purchase_rate']:.0%}")
    print(f"   - Peer influence score: {purchase_data['peer_influence_score']:.0%}")

    dynamics = await analyzer.identify_biases(purchase_data)

    print(f"\n   ✅ Analysis complete")
    print(f"\n   Dominant Biases:")
    for i, bias in enumerate(dynamics.dominant_biases, 1):
        print(f"     {i}. {bias}")

    print(f"\n   Decision Speed: {dynamics.decision_speed}")
    print(f"   System 1 Dominance: {dynamics.decision_architecture.get('system1_dominance', 0):.0%}")
    print(f"   System 2 Dominance: {dynamics.decision_architecture.get('system2_dominance', 0):.0%}")

    # ============================================================
    # TEST 2: Detect Specific Cognitive Biases
    # ============================================================
    print("\n📊 Test 2: Detecting Specific Cognitive Biases")
    print("-" * 60)

    patterns = {
        "first_seen_price_stickiness": 0.82,
        "last_minute_purchases": 0.65,
        "review_count_correlation": 0.89,
        "social_validation_seeking": 0.95,
        "authority_bias": 0.72
    }

    biases = await analyzer.detect_cognitive_biases(patterns)

    print(f"   ✅ Detected {len(biases)} cognitive biases\n")
    for bias in biases[:5]:
        print(f"   • {bias.bias_name.upper()}")
        print(f"     Strength: {bias.strength:.0%}")
        print(f"     {bias.description}")
        print()

    # ============================================================
    # TEST 3: Analyze Decision Drivers
    # ============================================================
    print("📊 Test 3: Analyzing Decision Drivers")
    print("-" * 60)

    behavior_data = {
        "emotional_triggers": ["fear_of_missing_out", "desire_for_status"],
        "rational_factors": ["price_comparison", "feature_checklist"],
        "social_factors": ["influencer_recommendations", "peer_reviews"],
        "impulse_purchase_rate": 0.65,
        "comparison_shopping_rate": 0.35,
        "peer_influence_score": 0.80
    }

    drivers = await analyzer.analyze_decision_drivers(behavior_data)

    print(f"   ✅ Found {len(drivers)} decision drivers\n")
    for driver in drivers:
        print(f"   • {driver.driver_name.upper()} ({driver.category})")
        print(f"     Importance: {driver.importance:.0%}")
        print(f"     {driver.description}")
        print()

    # ============================================================
    # TEST 4: Suggest Behavioral Levers
    # ============================================================
    print("📊 Test 4: Suggesting Behavioral Levers")
    print("-" * 60)

    levers = await analyzer.suggest_levers(dynamics.dominant_biases)

    print(f"   ✅ Generated {len(levers)} actionable levers\n")
    for lever in levers:
        print(f"   • {lever.lever_name.upper()}")
        print(f"     Targets: {lever.bias_targeted}")
        print(f"     Tactic: {lever.tactic}")
        print(f"     Expected Impact: {lever.expected_impact}")
        print()

    # ============================================================
    # TEST 5: Map Decision Architecture
    # ============================================================
    print("📊 Test 5: Mapping Decision Architecture")
    print("-" * 60)

    architecture = dynamics.decision_architecture

    print(f"   ✅ Decision architecture mapped\n")
    print(f"   System 1 (Fast Thinking): {architecture.get('system1_dominance', 0):.0%}")
    print(f"   System 2 (Slow Thinking): {architecture.get('system2_dominance', 0):.0%}")
    print(f"   Dominant Mode: {architecture.get('dominant_mode', 'unknown')}")
    print(f"   Decision Speed: {architecture.get('decision_speed', 'unknown')}")

    # ============================================================
    # GENERATE REPORT
    # ============================================================
    print("\n" + "="*80)
    print("📄 GENERATING ANALYSIS REPORT")
    print("="*80)

    # Format biases section
    biases_section = "\n".join([
        f"### {i+1}. {bias.bias_name.replace('_', ' ').title()}\n"
        f"- **Strength**: {bias.strength:.0%}\n"
        f"- **Description**: {bias.description}\n"
        f"- **Evidence**: {', '.join(bias.evidence or [])}\n"
        for i, bias in enumerate(biases[:5])
    ])

    # Format drivers section
    drivers_section = "\n".join([
        f"### {driver.driver_name.replace('_', ' ').title()} ({driver.category})\n"
        f"- **Importance**: {driver.importance:.0%}\n"
        f"- **Description**: {driver.description}\n"
        for driver in drivers
    ])

    # Format levers section
    levers_section = "\n".join([
        f"### {i+1}. {lever.lever_name.replace('_', ' ').title()}\n"
        f"- **Targets**: {lever.bias_targeted}\n"
        f"- **Tactic**: {lever.tactic}\n"
        f"- **Expected Impact**: {lever.expected_impact}\n"
        for i, lever in enumerate(levers)
    ])

    report = f"""# Layer 5: Behavioral Economics Analysis

**Date**: {datetime.now().strftime("%B %d, %Y")}
**Brand**: {brand_name}

---

## Executive Summary

**Decision Speed**: {dynamics.decision_speed.upper()}
**System 1 Dominance**: {architecture.get('system1_dominance', 0):.0%} (Fast, Intuitive Thinking)
**System 2 Dominance**: {architecture.get('system2_dominance', 0):.0%} (Slow, Deliberate Thinking)

**Dominant Mode**: {architecture.get('dominant_mode', 'unknown').replace('_', ' ').title()}

---

## Cognitive Biases Detected

{biases_section}

---

## Decision Drivers

{drivers_section}

---

## Behavioral Levers (Actionable Tactics)

{levers_section}

---

## Decision Architecture

### System 1: Fast Thinking ({architecture.get('system1_dominance', 0):.0%})
- Automatic, intuitive, emotional
- {"Dominant" if architecture.get('system1_dominance', 0) > 0.6 else "Present but not dominant"}

### System 2: Slow Thinking ({architecture.get('system2_dominance', 0):.0%})
- Controlled, deliberate, rational
- {"Dominant" if architecture.get('system2_dominance', 0) > 0.6 else "Present but not dominant"}

### Strategic Implications

**For {brand_name}:**

{"Since customers make fast, intuitive decisions, focus on:" if architecture.get('system1_dominance', 0) > 0.6 else "Since customers make deliberate decisions, focus on:"}

{chr(10).join([f"- {lever.tactic}" for lever in levers[:3]])}

---

**Analyst**: Claude Strategy Engine v1.0 - Layer 5: Behavioral Economics
"""

    # Save report with path validation
    if args.output_file:
        # Validate output path to prevent path traversal
        output_path = Path(args.output_file).resolve()

        # Ensure output is within safe directories (project root or docs)
        safe_dirs = [project_root.resolve(), (project_root / "docs").resolve()]
        is_safe = any(str(output_path).startswith(str(safe_dir)) for safe_dir in safe_dirs)

        if not is_safe:
            print(f"❌ Error: Output path must be within project directory")
            print(f"   Allowed: {project_root} or {project_root / 'docs'}")
            sys.exit(1)
    else:
        safe_brand_name = brand_name.lower().replace(' ', '_')
        output_path = project_root / f"LAYER5_ANALYSIS_{safe_brand_name.upper()}.md"

    with open(output_path, "w") as f:
        f.write(report)

    print(f"\n✅ Report saved to: {output_path}")
    print("\n" + "="*80)
    print("🎉 ANALYSIS COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   • Brand: {brand_name}")
    print(f"   • Cognitive biases detected: {len(biases)}")
    print(f"   • Decision drivers identified: {len(drivers)}")
    print(f"   • Behavioral levers suggested: {len(levers)}")
    print(f"   • Decision speed: {dynamics.decision_speed}")
    print(f"\n💡 Key Insight: {architecture.get('dominant_mode', 'unknown').replace('_', ' ').title()} decision-making\n")


if __name__ == "__main__":
    asyncio.run(main())
