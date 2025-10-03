"""
Pytest configuration and fixtures.
"""
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
import asyncio

from app.main import app
from app.core.config import settings
from app.core.database import Database


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db():
    """Create a test database connection."""
    # Use test database
    test_db_name = settings.TEST_DATABASE_NAME
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[test_db_name]
    
    yield db
    
    # Cleanup: Drop test database after tests
    await client.drop_database(test_db_name)
    client.close()


@pytest_asyncio.fixture
async def client():
    """Create a test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_client_data():
    """Sample client data for testing."""
    return {
        "company_name": "Test Company",
        "email": "test@example.com",
        "password": "testpassword123",
        "is_active": True
    }


@pytest.fixture
def test_sku_data():
    """Sample SKU data for testing."""
    return {
        "sku_id": "TEST-SKU-001",
        "name": "Test Product",
        "description": "A test product",
        "category": "Electronics",
        "target_roas": 3.0,
        "daily_budget": 500.0,
        "monthly_budget": 15000.0,
        "status": "active"
    }


@pytest.fixture
def test_campaign_data():
    """Sample campaign data for testing."""
    return {
        "campaign_id": "TEST-CAMP-001",
        "name": "Test Campaign",
        "platform": "google_ads",
        "platform_campaign_id": "GA-12345",
        "sku_id": "TEST-SKU-001",
        "daily_budget": 200.0,
        "target_roas": 3.0,
        "status": "active",
        "optimization_mode": "explore"
    }
