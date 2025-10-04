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
    from httpx import ASGITransport

    # Initialize database before tests
    await Database.connect_db()

    # Clean up test data from previous runs
    db = Database.get_database()
    await db.creatives.delete_many({})
    await db.creative_tests.delete_many({})
    await db.creative_metrics.delete_many({})
    await db.skus.delete_many({})
    await db.campaigns.delete_many({})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Cleanup database after tests
    await Database.close_db()


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


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    """Create authentication headers with a test user."""
    # Register a test user
    register_data = {
        "email": "test@example.com",
        "password": "testpass",
        "company_name": "Test Co"
    }

    reg_response = await client.post("/api/v1/auth/register", json=register_data)

    if reg_response.status_code not in [200, 201]:
        # User might already exist, try login
        pass

    # Login to get token
    login_data = {
        "email": "test@example.com",
        "password": "testpass"
    }

    response = await client.post("/api/v1/auth/login", json=login_data)

    if response.status_code != 200:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")

    token_data = response.json()
    access_token = token_data.get("access_token")

    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def test_client_id(auth_headers: dict, client: AsyncClient):
    """Return the test client ID from the authenticated user."""
    # Get current user info to extract client_id
    response = await client.get("/api/v1/clients/me", headers=auth_headers)
    if response.status_code == 200:
        return response.json().get("_id")
    return "test_client_id"


@pytest_asyncio.fixture
async def other_client_auth_headers(client: AsyncClient):
    """Create authentication headers for a second test user."""
    # Register a second test user
    register_data = {
        "email": "other@example.com",
        "password": "otherpass",
        "company_name": "Other Co"
    }

    await client.post("/api/v1/auth/register", json=register_data)

    # Login to get token
    login_data = {
        "email": "other@example.com",
        "password": "otherpass"
    }

    response = await client.post("/api/v1/auth/login", json=login_data)
    token_data = response.json()
    access_token = token_data.get("access_token")

    return {"Authorization": f"Bearer {access_token}"}
