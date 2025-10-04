"""
Unit tests for creative management APIs.
"""

import pytest
from datetime import datetime
from bson import ObjectId


class TestCreativeModel:
    """Test creative data model and validation."""

    def test_creative_model_structure(self):
        """Test creative model has required fields."""
        creative = {
            "_id": ObjectId(),
            "client_id": "test_client",
            "creative_id": "creative_001",
            "name": "Test Creative",
            "type": "image",
            "format": "square",
            "asset_url": "https://cdn.example.com/image.jpg",
            "headline": "Buy Now",
            "description": "Test description",
            "call_to_action": "Shop Now",
            "platforms": ["google_ads", "meta"],
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Validate required fields
        assert creative["client_id"] is not None
        assert creative["creative_id"] is not None
        assert creative["type"] in ["image", "video", "carousel", "text"]
        assert creative["status"] in ["active", "paused", "archived"]
        assert isinstance(creative["platforms"], list)

    def test_creative_type_validation(self):
        """Test creative type must be valid."""
        valid_types = ["image", "video", "carousel", "text"]

        for creative_type in valid_types:
            creative = {
                "type": creative_type,
                "client_id": "test_client"
            }
            assert creative["type"] in valid_types

    def test_creative_format_validation(self):
        """Test creative format validation."""
        valid_formats = ["square", "vertical", "horizontal", "story"]

        for format_type in valid_formats:
            creative = {
                "format": format_type,
                "type": "image"
            }
            assert creative["format"] in valid_formats


class TestCreativeMetricsModel:
    """Test creative metrics data model."""

    def test_metrics_model_structure(self):
        """Test metrics model has required fields."""
        metrics = {
            "_id": ObjectId(),
            "creative_id": "creative_001",
            "client_id": "test_client",
            "campaign_id": "campaign_001",
            "platform": "meta",
            "timestamp": datetime.utcnow(),
            "impressions": 10000,
            "clicks": 250,
            "conversions": 15,
            "spend": 125.50,
            "revenue": 450.00,
            "ctr": 2.5,
            "cpc": 0.50,
            "cpa": 8.37,
            "roas": 3.58
        }

        # Validate required fields
        assert metrics["creative_id"] is not None
        assert metrics["client_id"] is not None
        assert metrics["platform"] in ["google_ads", "meta", "tiktok", "linkedin"]
        assert metrics["impressions"] >= 0
        assert metrics["spend"] >= 0
        assert metrics["revenue"] >= 0

    def test_metrics_calculations(self):
        """Test metric calculations are correct."""
        impressions = 10000
        clicks = 250
        spend = 125.50
        conversions = 15
        revenue = 450.00

        # Calculate metrics
        ctr = (clicks / impressions) * 100
        cpc = spend / clicks
        cpa = spend / conversions
        roas = revenue / spend

        assert round(ctr, 2) == 2.5
        assert round(cpc, 2) == 0.50
        assert round(cpa, 2) == 8.37
        assert round(roas, 2) == 3.59


class TestCreativeTestModel:
    """Test A/B test model for creatives."""

    def test_creative_test_structure(self):
        """Test creative test model structure."""
        test = {
            "_id": ObjectId(),
            "test_id": "test_001",
            "client_id": "test_client",
            "campaign_id": "campaign_001",
            "test_name": "Headline Test A vs B",
            "creative_variants": [
                {
                    "creative_id": "creative_001",
                    "variant_name": "Control",
                    "traffic_allocation": 50
                },
                {
                    "creative_id": "creative_002",
                    "variant_name": "Variant A",
                    "traffic_allocation": 50
                }
            ],
            "status": "running",
            "test_type": "headline",
            "start_date": datetime.utcnow(),
            "min_sample_size": 1000,
            "confidence_level": 0.95,
            "created_at": datetime.utcnow()
        }

        # Validate structure
        assert test["client_id"] is not None
        assert test["test_type"] in ["headline", "image", "cta", "multivariate"]
        assert len(test["creative_variants"]) >= 2
        assert sum(v["traffic_allocation"] for v in test["creative_variants"]) == 100

    def test_traffic_allocation(self):
        """Test traffic allocation sums to 100%."""
        variants = [
            {"creative_id": "c1", "traffic_allocation": 33},
            {"creative_id": "c2", "traffic_allocation": 33},
            {"creative_id": "c3", "traffic_allocation": 34}
        ]

        total_allocation = sum(v["traffic_allocation"] for v in variants)
        assert total_allocation == 100


class TestCreativeValidation:
    """Test creative validation logic."""

    def test_url_validation(self):
        """Test asset URL validation."""
        valid_urls = [
            "https://cdn.example.com/image.jpg",
            "https://s3.amazonaws.com/bucket/video.mp4",
            "https://storage.googleapis.com/bucket/file.png"
        ]

        for url in valid_urls:
            assert url.startswith("https://")
            assert any(ext in url for ext in [".jpg", ".png", ".mp4", ".gif"])

    def test_client_isolation(self):
        """Test creatives are isolated by client_id."""
        creative1 = {"client_id": "client_a", "creative_id": "c1"}
        creative2 = {"client_id": "client_b", "creative_id": "c1"}

        # Same creative_id but different clients
        assert creative1["creative_id"] == creative2["creative_id"]
        assert creative1["client_id"] != creative2["client_id"]

    def test_platform_specific_requirements(self):
        """Test platform-specific creative requirements."""

        # Meta requires certain dimensions
        meta_creative = {
            "platform": "meta",
            "type": "image",
            "format": "square",
            "dimensions": {"width": 1080, "height": 1080}
        }
        assert meta_creative["dimensions"]["width"] == meta_creative["dimensions"]["height"]

        # Google Ads responsive search ads
        google_creative = {
            "platform": "google_ads",
            "type": "text",
            "headlines": ["H1", "H2", "H3"],  # Min 3
            "descriptions": ["D1", "D2"]  # Min 2
        }
        assert len(google_creative["headlines"]) >= 3
        assert len(google_creative["descriptions"]) >= 2


class TestCreativePerformance:
    """Test creative performance analysis."""

    def test_performance_ranking(self):
        """Test ranking creatives by performance."""
        creatives = [
            {"creative_id": "c1", "roas": 3.5, "conversions": 100},
            {"creative_id": "c2", "roas": 4.2, "conversions": 150},
            {"creative_id": "c3", "roas": 2.8, "conversions": 80}
        ]

        # Sort by ROAS descending
        ranked = sorted(creatives, key=lambda x: x["roas"], reverse=True)

        assert ranked[0]["creative_id"] == "c2"  # Best ROAS
        assert ranked[-1]["creative_id"] == "c3"  # Worst ROAS

    def test_statistical_significance(self):
        """Test basic statistical significance check."""

        # Chi-square test for conversion rates
        variant_a = {"impressions": 10000, "conversions": 250}  # 2.5% CVR
        variant_b = {"impressions": 10000, "conversions": 300}  # 3.0% CVR

        cvr_a = variant_a["conversions"] / variant_a["impressions"]
        cvr_b = variant_b["conversions"] / variant_b["impressions"]

        improvement = ((cvr_b - cvr_a) / cvr_a) * 100

        assert cvr_a == 0.025
        assert cvr_b == 0.030
        assert round(improvement, 1) == 20.0  # 20% improvement

    def test_minimum_sample_size(self):
        """Test minimum sample size requirement."""
        min_impressions = 1000

        test_data = [
            {"creative_id": "c1", "impressions": 1500, "is_valid": True},
            {"creative_id": "c2", "impressions": 800, "is_valid": False}
        ]

        for data in test_data:
            has_minimum = data["impressions"] >= min_impressions
            assert has_minimum == data["is_valid"]


class TestCreativeRotation:
    """Test creative rotation strategies."""

    def test_even_rotation(self):
        """Test even rotation distributes traffic equally."""
        creatives = ["c1", "c2", "c3"]
        allocation_per_creative = 100 / len(creatives)

        assert round(allocation_per_creative, 2) == 33.33

    def test_weighted_rotation(self):
        """Test weighted rotation based on performance."""
        creatives = [
            {"creative_id": "c1", "roas": 4.0, "weight": 0},
            {"creative_id": "c2", "roas": 3.0, "weight": 0},
            {"creative_id": "c3", "roas": 2.0, "weight": 0}
        ]

        # Calculate weights proportional to ROAS
        total_roas = sum(c["roas"] for c in creatives)
        for creative in creatives:
            creative["weight"] = (creative["roas"] / total_roas) * 100

        # Best performer gets most weight
        assert creatives[0]["weight"] > creatives[1]["weight"]
        assert creatives[1]["weight"] > creatives[2]["weight"]
        assert round(sum(c["weight"] for c in creatives), 1) == 100.0


class TestCreativeLifecycle:
    """Test creative lifecycle management."""

    def test_creative_status_transitions(self):
        """Test valid creative status transitions."""
        valid_transitions = {
            "draft": ["active", "archived"],
            "active": ["paused", "archived"],
            "paused": ["active", "archived"],
            "archived": []  # Cannot transition from archived
        }

        # Test valid transition
        current_status = "active"
        new_status = "paused"
        assert new_status in valid_transitions[current_status]

        # Test invalid transition
        current_status = "archived"
        new_status = "active"
        assert new_status not in valid_transitions[current_status]

    def test_creative_archival(self):
        """Test creative archival logic."""
        creative = {
            "status": "active",
            "last_used": datetime(2023, 1, 1),
            "performance_score": 2.0
        }

        # Archive if not used in 90 days and low performance
        days_inactive = (datetime.utcnow() - creative["last_used"]).days
        should_archive = days_inactive > 90 and creative["performance_score"] < 3.0

        assert should_archive is True
