#!/usr/bin/env python3
"""
Universal Strategic Analysis Orchestrator Tester

Tests the complete 7-layer analysis pipeline with ANY brand.

Usage:
    python scripts/test_orchestrator.py --brand-url "https://example.com"
    python scripts/test_orchestrator.py --brand-url "https://sangi.ca" --output-file "my_analysis.md"
"""

import sys
import asyncio
import argparse
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.strategy_engine.analysis.orchestrator import AnalysisOrchestrator


async def main():
    """Run complete 7-layer orchestrator test with ANY brand."""

    parser = argparse.ArgumentParser(description='Test Complete Strategic Analysis Orchestrator')
    parser.add_argument('--brand-url', required=True, help='Brand website URL for analysis')
    parser.add_argument('--output-file', help='Output markdown file path (optional)')
    parser.add_argument('--use-cache', action='store_true', help='Use cached results if available')

    args = parser.parse_args()

    brand_url = args.brand_url

    print("="*80)
    print("🎯 COMPLETE STRATEGIC ANALYSIS ORCHESTRATOR TEST")
    print(f"   Brand URL: {brand_url}")
    print(f"   Cache: {'Enabled' if args.use_cache else 'Disabled'}")
    print("="*80)

    orchestrator = AnalysisOrchestrator()

    # ============================================================
    # RUN COMPLETE 7-LAYER ANALYSIS
    # ============================================================
    print("\n📊 Running Complete 7-Layer Analysis...")
    print("-" * 60)

    start_time = time.time()
    result = await orchestrator.analyze_brand(brand_url, use_cache=args.use_cache)
    elapsed_time = time.time() - start_time

    print(f"\n✅ Analysis complete in {elapsed_time:.2f}s")
    print(f"   Average per layer: {elapsed_time/7:.2f}s\n")

    # ============================================================
    # VERIFY ALL LAYERS
    # ============================================================
    print("📊 Layer Completion Verification")
    print("-" * 60)

    layer_status = {
        "Layer 1 (Category Archaeology)": result.category_analysis is not None,
        "Layer 2 (Cultural Cartography)": result.cultural_trends is not None and len(result.cultural_trends) > 0,
        "Layer 3 (Framework Dialectics)": result.framework_tensions is not None and len(result.framework_tensions) > 0,
        "Layer 4 (Competitive Semiotics)": result.visual_codes is not None and len(result.visual_codes) > 0,
        "Layer 5 (Behavioral Economics)": result.behavioral_dynamics is not None,
        "Layer 6 (Jobs-to-be-Done)": result.jobs is not None and len(result.jobs) > 0,
        "Layer 7 (Platform Strategy)": result.platform_strategies is not None and len(result.platform_strategies) > 0
    }

    for layer_name, is_complete in layer_status.items():
        status_icon = "✅" if is_complete else "❌"
        print(f"   {status_icon} {layer_name}")

    total_complete = sum(layer_status.values())
    print(f"\n   🎯 {total_complete}/7 layers completed successfully")

    # ============================================================
    # DETAILED RESULTS
    # ============================================================
    print("\n📊 Detailed Results Summary")
    print("-" * 60)

    if result.category_analysis:
        print(f"\n   Layer 1: Category Archaeology")
        print(f"     Stated Category: {result.category_analysis.stated_category}")
        print(f"     Functional Category: {result.category_analysis.functional_category or 'N/A'}")
        print(f"     Competitors: {len(result.category_analysis.real_competitors)}")

    if result.cultural_trends and len(result.cultural_trends) > 0:
        print(f"\n   Layer 2: Cultural Cartography")
        print(f"     Macro Trends: {len(result.cultural_trends)}")
        for trend in result.cultural_trends[:3]:
            print(f"       • {trend.trend_name} (strength: {trend.strength:.0%})")

    if result.framework_tensions and len(result.framework_tensions) > 0:
        print(f"\n   Layer 3: Framework Dialectics")
        print(f"     Tensions Found: {len(result.framework_tensions)}")
        for tension in result.framework_tensions[:3]:
            print(f"       • {tension.contradiction}")

    if result.visual_codes and len(result.visual_codes) > 0:
        print(f"\n   Layer 4: Competitive Semiotics")
        print(f"     Visual Codes: {len(result.visual_codes)}")
        for code in result.visual_codes[:3]:
            print(f"       • {code.code_name} ({code.frequency:.0%} frequency)")

    if result.behavioral_dynamics:
        print(f"\n   Layer 5: Behavioral Economics")
        print(f"     Dominant Biases: {len(result.behavioral_dynamics.dominant_biases)}")
        for bias in result.behavioral_dynamics.dominant_biases[:3]:
            print(f"       • {bias}")

    if result.jobs and len(result.jobs) > 0:
        print(f"\n   Layer 6: Jobs-to-be-Done")
        print(f"     Jobs Identified: {len(result.jobs)}")
        for job in result.jobs:
            print(f"       • {job.job_type.title()}: {job.description[:60]}...")

    if result.platform_strategies and len(result.platform_strategies) > 0:
        print(f"\n   Layer 7: Platform Strategy")
        print(f"     Platforms: {len(result.platform_strategies)}")
        for platform_name in result.platform_strategies.keys():
            print(f"       • {platform_name.title()}")

    # ============================================================
    # GENERATE REPORT
    # ============================================================
    print("\n" + "="*80)
    print("📄 GENERATING COMPLETE ANALYSIS REPORT")
    print("="*80)

    # Extract brand name from URL
    brand_name = brand_url.replace("https://", "").replace("http://", "").split("/")[0]
    brand_name = brand_name.replace(".com", "").replace(".ca", "").title()

    # Format layer results
    def format_category():
        if not result.category_analysis:
            return "Not available"
        return f"""
**Stated Category**: {result.category_analysis.stated_category}
**Functional Category**: {result.category_analysis.functional_category or 'Not specified'}
**Emotional Category**: {result.category_analysis.emotional_category or 'Not specified'}
**Social Category**: {result.category_analysis.social_category or 'Not specified'}
**Real Competitors**: {', '.join(result.category_analysis.real_competitors[:5]) if result.category_analysis.real_competitors else 'None identified'}
"""

    def format_cultural_trends():
        if not result.cultural_trends or len(result.cultural_trends) == 0:
            return "Not available"
        trends_list = "\n".join([
            f"- **{trend.trend_name}** (Strength: {trend.strength:.0%}): {trend.description}"
            for trend in result.cultural_trends
        ])
        return trends_list

    def format_tensions():
        if not result.framework_tensions or len(result.framework_tensions) == 0:
            return "Not available"
        tensions_list = "\n".join([
            f"### {i+1}. {tension.contradiction}\n"
            f"**Type**: {tension.tension_type.replace('_', ' ').title()}\n"
            f"**Human Truth**: {tension.human_truth}\n"
            f"**Strategic Implication**: {tension.strategic_implication}\n"
            for i, tension in enumerate(result.framework_tensions)
        ])
        return tensions_list

    def format_visual_codes():
        if not result.visual_codes or len(result.visual_codes) == 0:
            return "Not available"
        codes_list = "\n".join([
            f"- **{code.code_name}** (Frequency: {code.frequency:.0%})"
            for code in result.visual_codes
        ])
        return codes_list

    def format_behavioral():
        if not result.behavioral_dynamics:
            return "Not available"
        biases_list = "\n".join([
            f"- **{bias}**"
            for bias in result.behavioral_dynamics.dominant_biases
        ])
        return f"""
**Dominant Biases**:
{biases_list}

**Decision Speed**: {result.behavioral_dynamics.decision_speed}
"""

    def format_jobs():
        if not result.jobs or len(result.jobs) == 0:
            return "Not available"
        jobs_list = "\n".join([
            f"### {job.job_type.title()} Job\n"
            f"**Description**: {job.description}\n"
            f"**Importance**: {job.importance:.0%}\n"
            for job in result.jobs
        ])
        return jobs_list

    def format_platforms():
        if not result.platform_strategies or len(result.platform_strategies) == 0:
            return "Not available"
        platforms_list = "\n".join([
            f"### {platform.upper()}\n"
            f"**Content Strategy**: {strategy.content_strategy.replace('_', ' ').title()}\n"
            f"**Targeting**: {strategy.targeting_approach.replace('_', ' ').title()}\n"
            for platform, strategy in result.platform_strategies.items()
        ])
        return platforms_list

    report = f"""# Complete Strategic Analysis Report

**Date**: {datetime.now().strftime("%B %d, %Y")}
**Brand**: {brand_name}
**URL**: {brand_url}
**Analysis Time**: {elapsed_time:.2f} seconds
**Layers Completed**: {total_complete}/7

---

## Executive Summary

This report contains a complete 7-layer strategic analysis for {brand_name}, covering:

1. Category Archaeology - Understanding the true competitive landscape
2. Cultural Cartography - Mapping macro cultural trends
3. Framework Dialectics - Identifying strategic tensions and opportunities
4. Competitive Semiotics - Decoding visual communication codes
5. Behavioral Economics - Understanding decision-making patterns
6. Jobs-to-be-Done - Identifying customer hiring criteria
7. Platform Strategy - Adapting strategy for each advertising platform

**Performance**: Analysis completed in {elapsed_time:.2f}s using parallel execution across all 7 layers.

---

## Layer 1: Category Archaeology

{format_category()}

---

## Layer 2: Cultural Cartography

{format_cultural_trends()}

---

## Layer 3: Framework Dialectics

{format_tensions()}

---

## Layer 4: Competitive Semiotics

{format_visual_codes()}

---

## Layer 5: Behavioral Economics

{format_behavioral()}

---

## Layer 6: Jobs-to-be-Done

{format_jobs()}

---

## Layer 7: Platform Strategy

{format_platforms()}

---

## Strategic Recommendations

Based on the complete 7-layer analysis, here are the key strategic imperatives for {brand_name}:

### 1. Category Positioning
{"Position in the **" + (result.category_analysis.functional_category or "identified") + "** category, competing against " + ", ".join(result.category_analysis.real_competitors[:3]) if result.category_analysis and result.category_analysis.real_competitors else "Refine category positioning based on deeper analysis"}

### 2. Cultural Alignment
{"Align with macro trend: **" + result.cultural_trends[0].trend_name + "** (" + str(int(result.cultural_trends[0].strength * 100)) + "% strength)" if result.cultural_trends and len(result.cultural_trends) > 0 else "Identify and align with relevant cultural trends"}

### 3. Strategic Tension Resolution
{"Address the tension: **" + result.framework_tensions[0].contradiction + "**. " + result.framework_tensions[0].strategic_implication if result.framework_tensions and len(result.framework_tensions) > 0 else "Identify and resolve key strategic tensions"}

### 4. Visual Communication
Use visual codes that communicate the desired brand meaning consistently across all touchpoints.

### 5. Behavioral Levers
{"Activate the **" + result.behavioral_dynamics.dominant_biases[0] + "** bias to influence purchase decisions" if result.behavioral_dynamics and len(result.behavioral_dynamics.dominant_biases) > 0 else "Identify and activate relevant behavioral economics levers"}

### 6. Job-to-be-Done Focus
{"Primary job to be done: **" + (result.jobs[0].description if result.jobs and len(result.jobs) > 0 else "Identify primary customer job") + "**"}

### 7. Platform Execution
Execute platform-specific strategies that respect each platform's unique culture and user behavior.

---

## Next Steps

1. **Validate** findings with customer research and testing
2. **Develop** creative assets aligned with strategic insights
3. **Test** messaging and positioning across platforms
4. **Measure** performance against strategic KPIs
5. **Iterate** based on market feedback and performance data

---

**Analysis Engine**: Claude Strategy Engine v1.0 - Complete 7-Layer Orchestrator
**Execution Mode**: Parallel (all layers run concurrently for optimal performance)
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
        output_path = project_root / f"COMPLETE_ANALYSIS_{safe_brand_name.upper()}.md"

    with open(output_path, "w") as f:
        f.write(report)

    print(f"\n✅ Report saved to: {output_path}")
    print("\n" + "="*80)
    print("🎉 COMPLETE ANALYSIS FINISHED")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   • Brand: {brand_name}")
    print(f"   • URL: {brand_url}")
    print(f"   • Execution time: {elapsed_time:.2f}s")
    print(f"   • Layers completed: {total_complete}/7")
    print(f"   • Execution mode: Parallel (all layers run concurrently)")
    print(f"\n💡 All 7 strategic layers analyzed and integrated into complete brand strategy\n")


if __name__ == "__main__":
    asyncio.run(main())
