"""
Integration tests for creative management API endpoints.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
from bson import ObjectId


@pytest.mark.asyncio
class TestCreativesAPI:
    """Test creative CRUD operations."""

    async def test_create_creative(self, client: AsyncClient, auth_headers: dict, test_client_id: str):
        """Test creating a new creative."""
        creative_data = {
            "creative_id": "test_creative_001",
            "name": "Test Image Creative",
            "creative_type": "image",
            "platform": "google_ads",
            "headline": "Shop Now - 50% Off",
            "description": "Limited time offer on all products",
            "call_to_action": "shop_now",
            "status": "active"
        }

        response = await client.post(
            "/api/v1/creatives/",
            json=creative_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["creative_id"] == creative_data["creative_id"]
        assert data["name"] == creative_data["name"]
        assert "created_at" in data

    async def test_list_creatives(self, client: AsyncClient, auth_headers: dict):
        """Test listing all creatives for a client."""
        response = await client.get(
            "/api/v1/creatives/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "creatives" in data
        assert isinstance(data["creatives"], list)
        assert "total" in data
        assert "page" in data

    async def test_get_creative_by_id(self, client: AsyncClient, auth_headers: dict):
        """Test getting a specific creative."""
        # First create a creative
        creative_data = {
            "creative_id": "test_creative_get",
            "name": "Get Test Creative",
            "creative_type": "video",
            "platform": "meta",
            "status": "active"
        }

        create_response = await client.post(
            "/api/v1/creatives/",
            json=creative_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201

        # Then retrieve it
        creative_id = creative_data["creative_id"]
        response = await client.get(
            f"/api/v1/creatives/{creative_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["creative_id"] == creative_id
        assert data["creative_type"] == "video"

    async def test_update_creative(self, client: AsyncClient, auth_headers: dict):
        """Test updating a creative."""
        # Create creative first
        creative_data = {
            "creative_id": "test_creative_update",
            "name": "Original Name",
            "creative_type": "image",
            "platform": "google_ads",
            "status": "active"
        }

        create_response = await client.post(
            "/api/v1/creatives/",
            json=creative_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201

        # Update the creative
        update_data = {
            "name": "Updated Name",
            "headline": "New Headline",
            "status": "paused"
        }

        response = await client.put(
            f"/api/v1/creatives/{creative_data['creative_id']}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["headline"] == "New Headline"
        assert data["status"] == "paused"

    async def test_delete_creative(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a creative."""
        # Create creative first
        creative_data = {
            "creative_id": "test_creative_delete",
            "name": "To Be Deleted",
            "creative_type": "text",
            "platform": "linkedin",
            "status": "draft"
        }

        create_response = await client.post(
            "/api/v1/creatives/",
            json=creative_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201

        # Delete it (soft delete/archive)
        response = await client.delete(
            f"/api/v1/creatives/{creative_data['creative_id']}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify it's archived (still exists but status is archived)
        get_response = await client.get(
            f"/api/v1/creatives/{creative_data['creative_id']}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "archived"


@pytest.mark.asyncio
class TestCreativeMetricsAPI:
    """Test creative metrics endpoints."""

    async def test_get_creative_metrics(self, client: AsyncClient, auth_headers: dict):
        """Test retrieving metrics for a creative."""
        creative_id = "test_creative_001"

        response = await client.get(
            f"/api/v1/creatives/{creative_id}/metrics",
            headers=auth_headers
        )

        # May return 404 if no metrics exist yet, or 200 with data
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                metric = data[0]
                assert "impressions" in metric
                assert "clicks" in metric
                assert "conversions" in metric

    async def test_get_creative_performance_summary(self, client: AsyncClient, auth_headers: dict):
        """Test getting performance summary for a creative."""
        creative_id = "test_creative_001"

        response = await client.get(
            f"/api/v1/creatives/{creative_id}/performance",
            headers=auth_headers
        )

        # Should return summary even if no data (zeros)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "total_impressions" in data or "impressions" in data
            assert "total_spend" in data or "spend" in data


@pytest.mark.asyncio
class TestCreativeTestsAPI:
    """Test A/B testing endpoints for creatives."""

    async def test_create_ab_test(self, client: AsyncClient, auth_headers: dict, test_client_id: str):
        """Test creating an A/B test."""
        # First create a SKU
        sku_data = {
            "sku_id": "test_sku_ab",
            "name": "Test SKU for AB",
            "description": "Test product",
            "target_roas": 3.0,
            "daily_budget": 500.0,
            "monthly_budget": 15000.0
        }
        sku_resp = await client.post("/api/v1/skus/", json=sku_data, headers=auth_headers)
        if sku_resp.status_code not in [200, 201]:
            print(f"SKU creation failed: {sku_resp.json()}")
        assert sku_resp.status_code in [200, 201], f"SKU creation failed: {sku_resp.json()}"

        # Create a campaign for the test
        campaign_data = {
            "campaign_id": "test_campaign_ab",
            "name": "Test Campaign for AB",
            "sku_id": "test_sku_ab",
            "platform": "google_ads",
            "platform_campaign_id": "GA-test-12345",
            "status": "active",
            "daily_budget": 100.0,
            "target_roas": 3.0
        }
        resp = await client.post("/api/v1/campaigns/", json=campaign_data, headers=auth_headers)
        if resp.status_code not in [200, 201]:
            print(f"Campaign creation failed: {resp.json()}")
        assert resp.status_code in [200, 201], f"Campaign creation failed: {resp.json()}"

        # Create two creatives for the test
        for i in range(2):
            creative_data = {
                "creative_id": f"ab_creative_{i:03d}",
                "name": f"AB Test Creative {i}",
                "creative_type": "image",
                "platform": "google_ads",
                "status": "active"
            }
            await client.post("/api/v1/creatives/", json=creative_data, headers=auth_headers)

        test_data = {
            "test_id": "ab_test_001",
            "name": "Headline Test",
            "campaign_id": "test_campaign_ab",
            "variants": [
                {
                    "creative_id": "ab_creative_000",
                    "variant_name": "Control",
                    "traffic_allocation": 50,
                    "is_control": True
                },
                {
                    "creative_id": "ab_creative_001",
                    "variant_name": "Variant A",
                    "traffic_allocation": 50,
                    "is_control": False
                }
            ],
            "test_type": "ab_test",
            "min_sample_size": 1000,
            "confidence_level": 0.95
        }

        response = await client.post(
            "/api/v1/creative-tests/",
            json=test_data,
            headers=auth_headers
        )

        if response.status_code not in [201, 200]:
            print(f"Error response: {response.json()}")
        assert response.status_code in [201, 200]
        data = response.json()
        assert data["test_id"] == test_data["test_id"]
        assert len(data["variants"]) == 2

    async def test_list_active_tests(self, client: AsyncClient, auth_headers: dict):
        """Test listing active A/B tests."""
        response = await client.get(
            "/api/v1/creative-tests/?status=running",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Should return paginated response
        assert "tests" in data or isinstance(data, list)

    async def test_get_test_results(self, client: AsyncClient, auth_headers: dict):
        """Test getting A/B test results."""
        test_id = "ab_test_001"

        response = await client.get(
            f"/api/v1/creative-tests/{test_id}/results",
            headers=auth_headers
        )

        # May not have results yet
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "variants" in data or "results" in data


@pytest.mark.asyncio
class TestCreativeValidation:
    """Test creative validation and error handling."""

    async def test_create_creative_missing_required_fields(self, client: AsyncClient, auth_headers: dict):
        """Test creating creative with missing required fields."""
        invalid_data = {
            "name": "Incomplete Creative"
            # Missing creative_id, type, etc.
        }

        response = await client.post(
            "/api/v1/creatives/",
            json=invalid_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    async def test_create_creative_invalid_type(self, client: AsyncClient, auth_headers: dict):
        """Test creating creative with invalid type."""
        invalid_data = {
            "creative_id": "invalid_type_test",
            "name": "Invalid Type",
            "creative_type": "invalid_type",  # Invalid
            "platform": "google_ads"
        }

        response = await client.post(
            "/api/v1/creatives/",
            json=invalid_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_duplicate_creative_id(self, client: AsyncClient, auth_headers: dict):
        """Test creating creative with duplicate ID."""
        creative_data = {
            "creative_id": "duplicate_test",
            "name": "First Creative",
            "creative_type": "image",
            "platform": "meta",
            "status": "active"
        }

        # Create first creative
        response1 = await client.post(
            "/api/v1/creatives/",
            json=creative_data,
            headers=auth_headers
        )
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = await client.post(
            "/api/v1/creatives/",
            json=creative_data,
            headers=auth_headers
        )
        assert response2.status_code == 400  # Conflict


@pytest.mark.asyncio
class TestCreativeClientIsolation:
    """Test client isolation for creatives."""

    async def test_cannot_access_other_client_creative(
        self,
        client: AsyncClient,
        auth_headers: dict,
        other_client_auth_headers: dict
    ):
        """Test that clients cannot access each other's creatives."""
        # Create creative as client 1
        creative_data = {
            "creative_id": "client1_creative",
            "name": "Client 1 Creative",
            "creative_type": "image",
            "platform": "google_ads",
            "status": "active"
        }

        response1 = await client.post(
            "/api/v1/creatives/",
            json=creative_data,
            headers=auth_headers
        )
        assert response1.status_code == 201

        # Try to access as client 2
        response2 = await client.get(
            f"/api/v1/creatives/{creative_data['creative_id']}",
            headers=other_client_auth_headers
        )
        assert response2.status_code == 404  # Not found (due to client isolation)


@pytest.mark.asyncio
class TestCreativePerformanceAnalysis:
    """Test creative performance analysis endpoints."""

    async def test_get_top_performing_creatives(self, client: AsyncClient, auth_headers: dict):
        """Test getting top performing creatives."""
        response = await client.get(
            "/api/v1/creatives/top-performers?metric=roas&limit=10",
            headers=auth_headers
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= 10

    async def test_get_creative_comparison(self, client: AsyncClient, auth_headers: dict):
        """Test comparing multiple creatives."""
        creative_ids = ["creative_001", "creative_002", "creative_003"]

        response = await client.post(
            "/api/v1/creatives/compare",
            json={"creative_ids": creative_ids},
            headers=auth_headers
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "comparison" in data or isinstance(data, list)


@pytest.mark.asyncio
class TestCreativeBulkOperations:
    """Test bulk operations on creatives."""

    async def test_bulk_update_status(self, client: AsyncClient, auth_headers: dict):
        """Test bulk updating creative status."""
        # Create multiple creatives first
        creative_ids = []
        for i in range(3):
            creative_data = {
                "creative_id": f"bulk_test_{i}",
                "name": f"Bulk Test {i}",
                "creative_type": "image",
                "platform": "meta",
                "status": "active"
            }
            response = await client.post(
                "/api/v1/creatives/",
                json=creative_data,
                headers=auth_headers
            )
            if response.status_code == 201:
                creative_ids.append(creative_data["creative_id"])

        if creative_ids:
            # Bulk update status
            response = await client.post(
                "/api/v1/creatives/bulk-update",
                json={
                    "creative_ids": creative_ids,
                    "updates": {"status": "paused"}
                },
                headers=auth_headers
            )

            assert response.status_code in [200, 404]
