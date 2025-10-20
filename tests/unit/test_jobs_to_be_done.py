"""Tests for Layer 6: Jobs-to-be-Done

This layer identifies the actual jobs customers are hiring the product to do,
going beyond functional features to emotional and social jobs.
"""

import pytest
from app.strategy_engine.analysis.layer6_jobs_to_be_done import (
    JobsToBeDone,
    JobsAnalysis,
    Job,
    Alternative
)


@pytest.mark.asyncio
async def test_identify_primary_job():
    """Should identify primary job customer is hiring product for."""

    brand_data = {
        "product_category": "fitness_tracker",
        "stated_benefits": ["track steps", "monitor heart rate", "count calories"],
        "marketing_messaging": ["get fit", "achieve your goals", "join the community"]
    }

    customer_data = {
        "usage_patterns": ["daily_tracking", "social_sharing", "goal_setting"],
        "emotional_triggers": ["motivation", "accountability", "pride"],
        "alternative_solutions": ["gym_membership", "personal_trainer", "fitness_apps"]
    }

    analyzer = JobsToBeDone()
    jobs = await analyzer.analyze(brand_data, customer_data)

    # Assertions
    assert isinstance(jobs, JobsAnalysis)
    assert jobs.primary_job is not None
    assert jobs.primary_job.job_type in ["functional", "emotional", "social"]
    assert jobs.primary_job != jobs.functional_job  # Deep insight - primary isn't just functional


@pytest.mark.asyncio
async def test_identify_jobs_hierarchy():
    """Should identify functional, emotional, and social jobs."""

    data = {
        "product": "luxury_watch",
        "features": ["tells time", "water resistant", "Swiss made"],
        "customer_motivations": ["status_symbol", "craftsmanship", "investment"]
    }

    analyzer = JobsToBeDone()
    jobs = await analyzer.identify_jobs(data)

    # Assertions
    assert jobs.functional_job is not None
    assert jobs.emotional_job is not None
    assert jobs.social_job is not None
    assert jobs.functional_job.job_type == "functional"
    assert jobs.emotional_job.job_type == "emotional"
    assert jobs.social_job.job_type == "social"


@pytest.mark.asyncio
async def test_find_alternatives():
    """Should find alternative solutions customers consider."""

    job = Job(
        job_type="emotional",
        description="Feel accomplished and motivated",
        importance=0.85
    )

    analyzer = JobsToBeDone()
    alternatives = await analyzer.find_alternatives(job)

    # Assertions
    assert len(alternatives) > 0
    assert all(isinstance(alt, Alternative) for alt in alternatives)
    assert any(alt.category == "direct_competitor" for alt in alternatives)
    assert any(alt.category in ["indirect_competitor", "substitute"] for alt in alternatives)


@pytest.mark.asyncio
async def test_rank_jobs():
    """Should rank jobs by importance."""

    data = {
        "customer_priorities": ["social_acceptance", "personal_achievement", "practical_utility"],
        "purchase_drivers": ["peer_approval", "self_improvement", "functionality"]
    }

    analyzer = JobsToBeDone()
    ranked_jobs = await analyzer.rank_jobs(data)

    # Assertions
    assert len(ranked_jobs) > 0
    assert "functional" in ranked_jobs
    assert "emotional" in ranked_jobs
    assert "social" in ranked_jobs

    # Check that jobs have importance scores
    for job_type, job in ranked_jobs.items():
        assert hasattr(job, "importance")
        assert 0 <= job.importance <= 1


@pytest.mark.asyncio
async def test_uncover_hidden_jobs():
    """Should uncover jobs that aren't obvious from product features."""

    product_data = {
        "stated_purpose": "Project management software",
        "features": ["task tracking", "gantt charts", "team collaboration"],
        "actual_usage": ["status_reporting", "looking_busy", "CYA_documentation"]
    }

    analyzer = JobsToBeDone()
    jobs = await analyzer.identify_jobs(product_data)

    # The primary job should go beyond stated purpose
    assert jobs.primary_job.description != product_data["stated_purpose"]
    assert jobs.social_job is not None  # Should identify social dimension


@pytest.mark.asyncio
async def test_complete_jobs_analysis():
    """Should generate complete jobs-to-be-done analysis."""

    brand_data = {
        "product_category": "meditation_app",
        "features": ["guided meditations", "sleep sounds", "progress tracking"],
        "marketing_claims": ["reduce stress", "improve sleep", "find peace"]
    }

    customer_data = {
        "usage_context": ["bedtime", "stressful_moments", "daily_routine"],
        "desired_outcomes": ["calm_mind", "better_sleep", "emotional_control"],
        "alternatives": ["therapy", "medication", "exercise", "journaling"]
    }

    analyzer = JobsToBeDone()
    analysis = await analyzer.analyze(brand_data, customer_data)

    # Comprehensive assertions
    assert analysis.primary_job is not None
    assert analysis.functional_job is not None
    assert analysis.emotional_job is not None
    assert analysis.social_job is not None
    assert len(analysis.alternatives) > 0
    assert hasattr(analysis, "job_hierarchy")


@pytest.mark.asyncio
async def test_competing_against_non_consumption():
    """Should identify when main competitor is 'not doing anything'."""

    data = {
        "product": "meal_kit_delivery",
        "main_barrier": "inertia",
        "customer_hesitation": "effort_to_try_something_new"
    }

    analyzer = JobsToBeDone()
    alternatives = await analyzer.find_alternatives_for_product(data)

    # Should identify non-consumption as alternative
    non_consumption_found = any(
        "non-consumption" in alt.name.lower() or "nothing" in alt.name.lower()
        for alt in alternatives
    )
    assert non_consumption_found
