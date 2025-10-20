"""Test module structure imports.

This test file verifies that all newly created modules can be imported correctly.
Following TDD approach - these tests will fail initially, then pass after module creation.
"""

import pytest


def test_strategy_engine_imports():
    """Test all strategy_engine modules can be imported."""
    from app.strategy_engine import analysis, intelligence, testing, creative, data_sources

    assert analysis is not None
    assert intelligence is not None
    assert testing is not None
    assert creative is not None
    assert data_sources is not None


def test_design_research_imports():
    """Test all design_research modules can be imported."""
    from app.design_research import scrapers, analyzers, training, synthesis

    assert scrapers is not None
    assert analyzers is not None
    assert training is not None
    assert synthesis is not None


def test_other_modules_import():
    """Test other modules can be imported."""
    from app import creative_generation, autopilot, meta_learning

    assert creative_generation is not None
    assert autopilot is not None
    assert meta_learning is not None


def test_strategy_engine_submodules_have_models():
    """Test that strategy_engine submodules have models.py files."""
    # These imports should work if models.py exists and is properly structured
    try:
        from app.strategy_engine.analysis import models as analysis_models
        from app.strategy_engine.intelligence import models as intelligence_models
        from app.strategy_engine.testing import models as testing_models
        from app.strategy_engine.creative import models as creative_models
        from app.strategy_engine.data_sources import models as data_sources_models

        assert analysis_models is not None
        assert intelligence_models is not None
        assert testing_models is not None
        assert creative_models is not None
        assert data_sources_models is not None
    except ImportError as e:
        pytest.fail(f"Failed to import models: {e}")


def test_design_research_has_models():
    """Test that design_research has models.py file."""
    try:
        from app.design_research import models
        assert models is not None
    except ImportError as e:
        pytest.fail(f"Failed to import design_research models: {e}")
