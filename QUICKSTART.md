# Quick Start Guide - IPOP Media Buying Management System

This guide will help you get the system up and running quickly.

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended)
- MongoDB 6.0+ (if not using Docker)
- Redis 7.0+ (if not using Docker)

## Option 1: Quick Start with Docker (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/gagan114662/ipop.git
cd ipop
git checkout staging
```

2. **Create environment file:**
```bash
cp .env.example .env
```

Edit `.env` and set your `SECRET_KEY` (minimum 32 characters):
```bash
SECRET_KEY=your-super-secret-key-here-min-32-chars
```

3. **Start all services:**
```bash
docker-compose up -d
```

This will start:
- FastAPI application on http://localhost:8000
- MongoDB on localhost:27017
- Redis on localhost:6379
- MongoDB Express (Web UI) on http://localhost:8081

4. **Access the API:**
- API Documentation: http://localhost:8000/docs
- API Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
- MongoDB Web UI: http://localhost:8081 (admin/admin123)

## Option 2: Local Development Setup

1. **Clone and setup:**
```bash
git clone https://github.com/gagan114662/ipop.git
cd ipop
git checkout staging
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup environment:**
```bash
cp .env.example .env
# Edit .env with your MongoDB and Redis URLs
```

5. **Start MongoDB and Redis** (if not using Docker):
```bash
# MongoDB
mongod --dbpath /path/to/data

# Redis
redis-server
```

6. **Run the application:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing the API

### 1. Register a Client

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Acme Corp",
    "email": "admin@acmecorp.com",
    "password": "securepassword123"
  }'
```

Save the `access_token` from the response.

### 2. Create a SKU

```bash
curl -X POST http://localhost:8000/api/v1/skus/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "sku_id": "PROD-001",
    "name": "Premium Widget",
    "daily_budget": 500.0,
    "monthly_budget": 15000.0,
    "target_roas": 3.0
  }'
```

### 3. Create a Campaign

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "campaign_id": "CAMP-001",
    "name": "Google Ads - Premium Widget",
    "platform": "google_ads",
    "platform_campaign_id": "GA-123456",
    "sku_id": "PROD-001",
    "daily_budget": 200.0,
    "target_roas": 3.0
  }'
```

### 4. Get Optimization Recommendations

```bash
curl -X GET "http://localhost:8000/api/v1/intelligence/recommendations/CAMP-001" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Run Optimization

```bash
curl -X POST "http://localhost:8000/api/v1/intelligence/optimize/campaigns/CAMP-001?apply=false" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_explore_exploit.py -v
```

## Key Features to Try

1. **Multi-tenant Architecture**: Create multiple client accounts, each isolated
2. **SKU Management**: Organize campaigns by products
3. **Campaign Management**: Support for Google Ads, Meta, TikTok, LinkedIn
4. **Intelligence Engine**: 
   - EXPLORE mode for new campaigns (bold 20% budget changes)
   - EXPLOIT mode for mature campaigns (conservative 5% changes)
5. **Real-time Metrics**: Track performance, burn rates, and ROAS
6. **Decision History**: Audit trail of all optimization decisions

## Next Steps

1. Review the [full README](README.md) for complete documentation
2. Check the [API documentation](http://localhost:8000/docs) for all endpoints
3. Explore the models in `app/models/` to understand data structures
4. Review the intelligence logic in `app/intelligence/`

## Troubleshooting

**MongoDB connection error:**
- Ensure MongoDB is running: `docker ps` or check local MongoDB service
- Verify MONGODB_URL in `.env`

**Redis connection error:**
- Ensure Redis is running: `docker ps` or check local Redis service
- Verify REDIS_URL in `.env`

**JWT token expired:**
- Use the `/api/v1/auth/refresh` endpoint with your refresh token
- Access tokens expire after 15 minutes by default

## Support

For issues and questions, please check:
- API Documentation: http://localhost:8000/docs
- Project README: [README.md](README.md)
- Test examples: `tests/` directory
