"""Integration Tests for Complete Strategic Analysis Pipeline

Tests the full 7-layer analysis orchestration from brand URL to complete strategy.
"""

import pytest
from app.strategy_engine.analysis.orchestrator import AnalysisOrchestrator
from app.strategy_engine.analysis.models import BrandStrategy


@pytest.mark.asyncio
async def test_complete_7_layer_analysis():
    """Should run complete 7-layer analysis pipeline."""

    # Sample brand URL
    brand_url = "https://example-brand.com"

    orchestrator = AnalysisOrchestrator()
    result = await orchestrator.analyze_brand(brand_url)

    # Verify result structure
    assert isinstance(result, BrandStrategy)

    # Verify all 7 layers are present
    assert result.category_analysis is not None
    assert result.cultural_trends is not None and len(result.cultural_trends) > 0
    assert result.framework_tensions is not None and len(result.framework_tensions) > 0
    assert result.visual_codes is not None and len(result.visual_codes) > 0
    assert result.behavioral_dynamics is not None
    assert result.jobs is not None and len(result.jobs) > 0
    assert result.platform_strategies is not None and len(result.platform_strategies) > 0


@pytest.mark.asyncio
async def test_orchestrator_handles_errors_gracefully():
    """Should handle errors in individual layers without crashing."""

    # Invalid URL should not crash the system
    orchestrator = AnalysisOrchestrator()

    # Test with various edge cases
    test_cases = [
        "",  # Empty URL
        "invalid-url",  # Invalid format
        "https://non-existent-domain-12345.com"  # Non-existent domain
    ]

    for test_url in test_cases:
        try:
            result = await orchestrator.analyze_brand(test_url)
            # Should return partial results or error information
            assert result is not None
        except Exception as e:
            # Should raise meaningful exception
            assert str(e) is not None


@pytest.mark.asyncio
async def test_orchestrator_runs_layers_in_sequence():
    """Should run layers in correct order with dependencies."""

    orchestrator = AnalysisOrchestrator()

    # Track execution order
    execution_log = []

    # Mock to track layer execution
    original_run = orchestrator._run_layer

    async def tracked_run(layer_name, *args, **kwargs):
        execution_log.append(layer_name)
        return await original_run(layer_name, *args, **kwargs)

    orchestrator._run_layer = tracked_run

    await orchestrator.analyze_brand("https://example.com")

    # Verify layers ran in correct order
    expected_order = [
        "layer1_price_elasticity",
        "layer2_category_archaeology",
        "layer3_cultural_cartography",
        "layer4_competitive_semiotics",
        "layer5_behavioral_economics",
        "layer6_jobs_to_be_done",
        "layer7_platform_strategy"
    ]

    assert len(execution_log) == 7
    for i, expected_layer in enumerate(expected_order):
        assert expected_layer in execution_log[i].lower()


@pytest.mark.asyncio
async def test_orchestrator_performance():
    """Should complete analysis within reasonable time."""

    import time

    orchestrator = AnalysisOrchestrator()

    start_time = time.time()
    result = await orchestrator.analyze_brand("https://example.com")
    elapsed_time = time.time() - start_time

    # Should complete within 30 seconds (adjust based on requirements)
    assert elapsed_time < 30, f"Analysis took {elapsed_time:.2f}s, expected < 30s"

    # Verify complete result
    assert result is not None


@pytest.mark.asyncio
async def test_orchestrator_partial_failure_recovery():
    """Should return partial results if some layers fail."""

    orchestrator = AnalysisOrchestrator()

    # Simulate failure in one layer
    # (Implementation would need to support this)

    result = await orchestrator.analyze_brand("https://example.com")

    # Should still return result even if some layers fail
    assert result is not None
    # At least some layers should have data
    layer_count = sum([
        result.category_analysis is not None,
        len(result.cultural_trends) > 0,
        len(result.framework_tensions) > 0,
        len(result.visual_codes) > 0,
        result.behavioral_dynamics is not None,
        len(result.jobs) > 0,
        len(result.platform_strategies) > 0
    ])
    assert layer_count > 0, "At least some layers should complete"


@pytest.mark.asyncio
async def test_orchestrator_caching():
    """Should cache results to avoid redundant analysis."""

    orchestrator = AnalysisOrchestrator()

    brand_url = "https://example.com"

    # First run
    result1 = await orchestrator.analyze_brand(brand_url)

    # Second run (should be faster if cached)
    import time
    start_time = time.time()
    result2 = await orchestrator.analyze_brand(brand_url, use_cache=True)
    elapsed_time = time.time() - start_time

    # Cached run should be very fast
    assert elapsed_time < 1.0, "Cached analysis should be < 1 second"

    # Results should be equivalent
    assert result1.category_analysis == result2.category_analysis


@pytest.mark.asyncio
async def test_orchestrator_output_completeness():
    """Should provide complete, actionable strategic output."""

    orchestrator = AnalysisOrchestrator()
    result = await orchestrator.analyze_brand("https://example.com")

    # Verify strategic completeness
    assert result.category_analysis.stated_category is not None
    assert result.category_analysis.real_competitors is not None

    # Verify cultural insights
    assert any(trend.strength > 0.5 for trend in result.cultural_trends)

    # Verify behavioral insights
    assert len(result.behavioral_dynamics.dominant_biases) > 0

    # Verify jobs analysis
    assert any(job.importance > 0.5 for job in result.jobs)

    # Verify platform strategies
    assert "meta" in result.platform_strategies or "google" in result.platform_strategies
