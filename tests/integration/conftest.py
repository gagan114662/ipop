"""
Integration test configuration - simpler version that doesn't load full app.
"""
import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    # Set minimum required env vars
    os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-integration-tests-32-chars-minimum')
    os.environ.setdefault('MONGODB_URL', 'mongodb://localhost:27017')
    os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')
    os.environ.setdefault('ENVIRONMENT', 'test')
    os.environ.setdefault('DEBUG', 'False')
