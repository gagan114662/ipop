"""
Integration tests for Platform Manager.

These tests verify that platform clients are properly configured and can
gracefully handle missing credentials.
"""
import pytest
import os
from unittest.mock import Mock, patch, AsyncMock

from app.models.campaign import Platform
from app.platforms.manager import PlatformManager


class TestPlatformManagerConfiguration:
    """Test platform manager configuration checks."""

    @pytest.fixture
    def manager(self):
        """Create platform manager instance."""
        return PlatformManager()

    def test_manager_initialization(self, manager):
        """Test that platform manager initializes all clients."""
        assert manager.google_ads is not None
        assert manager.meta is not None
        assert manager.tiktok is not None
        assert manager.linkedin is not None

    def test_get_client_for_each_platform(self, manager):
        """Test getting client for each platform."""
        assert manager.get_client(Platform.GOOGLE_ADS) == manager.google_ads
        assert manager.get_client(Platform.META) == manager.meta
        assert manager.get_client(Platform.TIKTOK) == manager.tiktok
        assert manager.get_client(Platform.LINKEDIN) == manager.linkedin

    def test_is_platform_configured_checks(self, manager):
        """Test platform configuration checks."""
        # This will check actual environment variables
        # Without credentials, all should return False
        for platform in [Platform.GOOGLE_ADS, Platform.META, Platform.TIKTOK, Platform.LINKEDIN]:
            is_configured = manager.is_platform_configured(platform)
            # We expect False unless env vars are actually set
            assert isinstance(is_configured, bool)

    def test_get_configured_platforms(self, manager):
        """Test getting list of configured platforms."""
        configured = manager.get_configured_platforms()
        assert isinstance(configured, list)
        # All items should be Platform enum values
        for platform in configured:
            assert isinstance(platform, Platform)


class TestPlatformManagerGracefulDegradation:
    """Test that platform manager handles missing credentials gracefully."""

    @pytest.fixture
    def manager(self):
        """Create platform manager with no credentials."""
        # Clear environment variables to simulate no credentials
        with patch.dict(os.environ, {}, clear=True):
            # Set minimum required env vars for app to load
            os.environ['SECRET_KEY'] = 'test-secret-key-32-characters-long'
            os.environ['MONGODB_URL'] = 'mongodb://localhost:27017'
            os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

            manager = PlatformManager()
        return manager

    @pytest.mark.asyncio
    async def test_fetch_metrics_without_credentials(self, manager):
        """Test that fetch_metrics returns None gracefully when platform not configured."""
        campaign = {
            "campaign_id": "test-campaign",
            "platform_campaign_id": "GA-123",
            "metadata": {"customer_id": "123-456-7890"}
        }

        result = await manager.fetch_metrics(
            Platform.GOOGLE_ADS,
            campaign
        )

        # Should return None, not raise an error
        assert result is None

    @pytest.mark.asyncio
    async def test_update_budget_without_credentials(self, manager):
        """Test that update_budget returns False gracefully when platform not configured."""
        campaign = {
            "campaign_id": "test-campaign",
            "platform_campaign_id": "GA-123",
            "metadata": {"customer_id": "123-456-7890"}
        }

        result = await manager.update_budget(
            Platform.GOOGLE_ADS,
            campaign,
            300.0
        )

        # Should return False, not raise an error
        assert result is False

    @pytest.mark.asyncio
    async def test_pause_campaign_without_credentials(self, manager):
        """Test that pause_campaign returns False gracefully when platform not configured."""
        campaign = {
            "campaign_id": "test-campaign",
            "platform_campaign_id": "GA-123",
            "metadata": {"customer_id": "123-456-7890"}
        }

        result = await manager.pause_campaign(
            Platform.GOOGLE_ADS,
            campaign
        )

        # Should return False, not raise an error
        assert result is False

    @pytest.mark.asyncio
    async def test_activate_campaign_without_credentials(self, manager):
        """Test that activate_campaign returns False gracefully when platform not configured."""
        campaign = {
            "campaign_id": "test-campaign",
            "platform_campaign_id": "GA-123",
            "metadata": {"customer_id": "123-456-7890"}
        }

        result = await manager.activate_campaign(
            Platform.GOOGLE_ADS,
            campaign
        )

        # Should return False, not raise an error
        assert result is False


class TestPlatformCredentialValidation:
    """Test platform credential validation logic."""

    def test_google_ads_requires_all_four_credentials(self):
        """Test that Google Ads requires all 4 credentials."""
        from app.platforms.google_ads import GoogleAdsClient

        # Without credentials, should not be configured
        with patch.dict(os.environ, {}, clear=True):
            client = GoogleAdsClient()
            assert client.is_configured() is False

    def test_meta_requires_three_credentials(self):
        """Test that Meta requires 3 credentials."""
        from app.platforms.meta import MetaAdsClient

        # Without credentials, should not be configured
        with patch.dict(os.environ, {}, clear=True):
            client = MetaAdsClient()
            assert client.is_configured() is False

    def test_tiktok_requires_access_token(self):
        """Test that TikTok requires access token."""
        from app.platforms.tiktok import TikTokAdsClient

        # Without credentials, should not be configured
        with patch.dict(os.environ, {}, clear=True):
            client = TikTokAdsClient()
            assert client.is_configured() is False

    def test_linkedin_requires_access_token(self):
        """Test that LinkedIn requires access token."""
        from app.platforms.linkedin import LinkedInAdsClient

        # Without credentials, should not be configured
        with patch.dict(os.environ, {}, clear=True):
            client = LinkedInAdsClient()
            assert client.is_configured() is False


class TestPlatformPartialConfiguration:
    """Test behavior when platform is partially configured."""

    @pytest.mark.asyncio
    async def test_google_ads_partial_config_fails_gracefully(self):
        """Test Google Ads with partial credentials fails gracefully."""
        from app.platforms.google_ads import GoogleAdsClient

        # Set only some credentials
        with patch.dict(os.environ, {
            'GOOGLE_ADS_DEVELOPER_TOKEN': 'test-token',
            'GOOGLE_ADS_CLIENT_ID': 'test-client-id',
            # Missing CLIENT_SECRET and REFRESH_TOKEN
        }, clear=True):
            client = GoogleAdsClient()
            # Should not be considered configured
            assert client.is_configured() is False

    @pytest.mark.asyncio
    async def test_meta_partial_config_fails_gracefully(self):
        """Test Meta with partial credentials fails gracefully."""
        from app.platforms.meta import MetaAdsClient

        # Set only some credentials
        with patch.dict(os.environ, {
            'META_APP_ID': 'test-app-id',
            'META_APP_SECRET': 'test-app-secret',
            # Missing ACCESS_TOKEN
        }, clear=True):
            client = MetaAdsClient()
            # Should not be considered configured
            assert client.is_configured() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
