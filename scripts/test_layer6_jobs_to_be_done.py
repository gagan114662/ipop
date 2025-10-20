#!/usr/bin/env python3
"""
Universal Layer 6: Jobs-to-be-Done Tester

Tests Layer 6 with ANY brand's product and customer data.

Usage:
    python scripts/test_layer6_jobs_to_be_done.py --brand-name "Brand Name" --product-category "Category"
    python scripts/test_layer6_jobs_to_be_done.py --brand-name "Sangi Advertising" --product-category "advertising_services"
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.strategy_engine.analysis.layer6_jobs_to_be_done import JobsToBeDone


async def main():
    """Run Layer 6 test with ANY brand."""

    parser = argparse.ArgumentParser(description='Test Layer 6 Jobs-to-be-Done with any brand')
    parser.add_argument('--brand-name', required=True, help='Brand name for analysis')
    parser.add_argument('--product-category', required=True, help='Product category (e.g., fitness_tracker, luxury_watch)')
    parser.add_argument('--output-file', help='Output markdown file path (optional)')

    args = parser.parse_args()

    brand_name = args.brand_name
    product_category = args.product_category

    print("="*80)
    print("💼 LAYER 6: JOBS-TO-BE-DONE TEST")
    print(f"   Brand: {brand_name}")
    print(f"   Product Category: {product_category}")
    print("="*80)

    analyzer = JobsToBeDone()

    # ============================================================
    # TEST 1: Identify Jobs Hierarchy
    # ============================================================
    print("\n📊 Test 1: Identifying Job Hierarchy")
    print("-" * 60)

    # Sample brand data (in production, scraped from website)
    brand_data = {
        "product_category": product_category,
        "features": ["feature_1", "feature_2", "feature_3"],
        "marketing_messaging": ["achieve your goals", "join the community", "premium quality"]
    }

    # Sample customer data (in production, from analytics/surveys)
    customer_data = {
        "usage_patterns": ["daily_usage", "social_sharing", "goal_tracking"],
        "emotional_triggers": ["motivation", "achievement", "pride"],
        "customer_priorities": ["social_acceptance", "personal_achievement", "practical_utility"],
        "purchase_drivers": ["peer_approval", "self_improvement", "functionality"]
    }

    print(f"   Analyzing brand positioning...")
    print(f"   - Product category: {product_category}")
    print(f"   - Features analyzed: {len(brand_data['features'])}")
    print(f"   - Customer priorities: {len(customer_data['customer_priorities'])}")

    jobs_analysis = await analyzer.identify_jobs({**brand_data, **customer_data})

    print(f"\n   ✅ Job hierarchy identified\n")
    print(f"   Functional Job: {jobs_analysis.functional_job.description}")
    print(f"     Importance: {jobs_analysis.functional_job.importance:.0%}")
    print(f"\n   Emotional Job: {jobs_analysis.emotional_job.description}")
    print(f"     Importance: {jobs_analysis.emotional_job.importance:.0%}")
    print(f"\n   Social Job: {jobs_analysis.social_job.description}")
    print(f"     Importance: {jobs_analysis.social_job.importance:.0%}")

    # ============================================================
    # TEST 2: Identify Primary Job
    # ============================================================
    print("\n📊 Test 2: Identifying Primary Job")
    print("-" * 60)

    analysis = await analyzer.analyze(brand_data, customer_data)

    print(f"   ✅ Primary job identified\n")
    print(f"   Primary Job Type: {analysis.primary_job.job_type.upper()}")
    print(f"   Description: {analysis.primary_job.description}")
    print(f"   Importance: {analysis.primary_job.importance:.0%}")

    # Check if primary is different from functional
    is_deep_insight = analysis.primary_job.job_type != "functional"
    if is_deep_insight:
        print(f"\n   💡 INSIGHT: Primary job is {analysis.primary_job.job_type}, not functional!")
        print(f"      This reveals the deeper reason customers hire this product.")

    # ============================================================
    # TEST 3: Find Alternative Solutions
    # ============================================================
    print("\n📊 Test 3: Finding Alternative Solutions")
    print("-" * 60)

    alternatives = await analyzer.find_alternatives(analysis.primary_job)

    print(f"   ✅ Found {len(alternatives)} alternative solutions\n")
    for i, alt in enumerate(alternatives, 1):
        print(f"   {i}. {alt.name} ({alt.category})")
        print(f"      Description: {alt.description}")
        print(f"      Switching Cost: {alt.switching_cost:.0%}")
        print()

    # ============================================================
    # TEST 4: Rank Jobs by Importance
    # ============================================================
    print("📊 Test 4: Ranking Jobs by Importance")
    print("-" * 60)

    ranked_jobs = await analyzer.rank_jobs(customer_data)

    print(f"   ✅ Jobs ranked by customer priorities\n")

    # Sort by importance
    sorted_jobs = sorted(ranked_jobs.items(), key=lambda x: x[1].importance, reverse=True)

    for i, (job_type, job) in enumerate(sorted_jobs, 1):
        print(f"   {i}. {job_type.upper()}: {job.importance:.0%}")
        print(f"      {job.description}")
        print()

    # ============================================================
    # TEST 5: Complete Analysis
    # ============================================================
    print("📊 Test 5: Complete Jobs-to-be-Done Analysis")
    print("-" * 60)

    print(f"   ✅ Complete analysis generated\n")
    print(f"   Primary Job: {analysis.primary_job.job_type}")
    print(f"   Job Hierarchy:")
    for job_type, importance in analysis.job_hierarchy.items():
        print(f"     • {job_type}: {importance:.0%}")
    print(f"   Alternatives Considered: {len(analysis.alternatives)}")

    # ============================================================
    # GENERATE REPORT
    # ============================================================
    print("\n" + "="*80)
    print("📄 GENERATING ANALYSIS REPORT")
    print("="*80)

    # Format alternatives section
    alternatives_section = "\n".join([
        f"### {i+1}. {alt.name}\n"
        f"- **Category**: {alt.category.replace('_', ' ').title()}\n"
        f"- **Description**: {alt.description}\n"
        f"- **Switching Cost**: {alt.switching_cost:.0%}\n"
        for i, alt in enumerate(analysis.alternatives)
    ])

    # Determine competitive insight
    non_consumption_present = any("non-consumption" in alt.name.lower() for alt in analysis.alternatives)
    competitive_insight = "Main competitor is inertia/status quo" if non_consumption_present else "Multiple alternative solutions exist"

    report = f"""# Layer 6: Jobs-to-be-Done Analysis

**Date**: {datetime.now().strftime("%B %d, %Y")}
**Brand**: {brand_name}
**Product Category**: {product_category}

---

## Executive Summary

**Primary Job**: {analysis.primary_job.job_type.upper()}
**Primary Job Description**: {analysis.primary_job.description}
**Importance**: {analysis.primary_job.importance:.0%}

{f"💡 **Key Insight**: Customers hire {brand_name} primarily for {analysis.primary_job.job_type} reasons, not just functional utility." if is_deep_insight else ""}

---

## Job Hierarchy

### Functional Job
**Description**: {analysis.functional_job.description}
**Importance**: {analysis.functional_job.importance:.0%}

This is what the product *does* - the practical, tangible outcome.

### Emotional Job
**Description**: {analysis.emotional_job.description}
**Importance**: {analysis.emotional_job.importance:.0%}

This is how customers want to *feel* when using the product.

### Social Job
**Description**: {analysis.social_job.description}
**Importance**: {analysis.social_job.importance:.0%}

This is how customers want to be *perceived* by others.

---

## Job Ranking

{chr(10).join([f"{i}. **{job_type.title()}**: {importance:.0%}" for i, (job_type, importance) in enumerate(sorted(analysis.job_hierarchy.items(), key=lambda x: x[1], reverse=True), 1)])}

---

## Alternative Solutions

Customers consider these alternatives when trying to get the job done:

{alternatives_section}

---

## Strategic Implications

### What This Means for {brand_name}

**1. Product Positioning**
Focus marketing on the {analysis.primary_job.job_type} job, not just functional features.

**2. Competitive Advantage**
{competitive_insight}

**3. Messaging Strategy**
Emphasize how {brand_name} helps customers:
- {analysis.primary_job.description}
- Stand out from alternatives by addressing {analysis.primary_job.job_type} needs

**4. Product Development**
Enhance features that support the {analysis.primary_job.job_type} job ({analysis.primary_job.importance:.0%} importance)

---

## Jobs-to-be-Done Framework

**Core Question**: What job is the customer hiring {brand_name} to do?

**Answer**: {analysis.primary_job.description}

**Deeper Insight**:
The job hierarchy reveals that customers value {list(dict(sorted(analysis.job_hierarchy.items(), key=lambda x: x[1], reverse=True)).keys())[0]} outcomes most highly. This should drive all strategic decisions.

---

**Analyst**: Claude Strategy Engine v1.0 - Layer 6: Jobs-to-be-Done
"""

    # Save report
    if args.output_file:
        output_path = Path(args.output_file)
        # Validate path
        output_path = output_path.resolve()
        safe_dirs = [project_root.resolve(), (project_root / "docs").resolve()]
        is_safe = any(str(output_path).startswith(str(safe_dir)) for safe_dir in safe_dirs)

        if not is_safe:
            print(f"❌ Error: Output path must be within project directory")
            sys.exit(1)
    else:
        safe_brand_name = brand_name.lower().replace(' ', '_')
        output_path = project_root / f"LAYER6_ANALYSIS_{safe_brand_name.upper()}.md"

    with open(output_path, "w") as f:
        f.write(report)

    print(f"\n✅ Report saved to: {output_path}")
    print("\n" + "="*80)
    print("🎉 ANALYSIS COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   • Brand: {brand_name}")
    print(f"   • Product category: {product_category}")
    print(f"   • Primary job: {analysis.primary_job.job_type} ({analysis.primary_job.importance:.0%})")
    print(f"   • Job hierarchy: {' > '.join(dict(sorted(analysis.job_hierarchy.items(), key=lambda x: x[1], reverse=True)).keys())}")
    print(f"   • Alternatives found: {len(analysis.alternatives)}")
    print(f"\n💡 Key Insight: Customers hire {brand_name} for {analysis.primary_job.job_type} reasons\n")


if __name__ == "__main__":
    asyncio.run(main())
