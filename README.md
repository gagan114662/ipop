# Media Buying Management System (IPOP)

An intelligent, API-only media buying management system with multi-tenant support and two layers of intelligence:
- **SKU-level intelligence**: Per-product optimization
- **System-wide intelligence**: Cross-client learning

## Technology Stack

- **Backend**: FastAPI + Python 3.11+ (async/await)
- **Database**: MongoDB
- **Cache/Rate Limiting**: Redis
- **Cloud**: Google Cloud Platform (GCP)
- **Authentication**: JWT with refresh token rotation
- **Supported Platforms**: Google Ads, Meta, TikTok, LinkedIn
- **Integrators**: Revealbot, AdRoll, StackAdapt, AdEspresso, Madgicx

## Quick Start

### Prerequisites
- Python 3.11+
- MongoDB 6.0+
- Redis 7.0+
- GCP account with Secret Manager enabled

### Installation

```bash
# Clone repository
git clone https://github.com/gagan114662/ipop.git
cd ipop

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your configurations

# Run migrations
python -m app.db.migrations

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
ipop/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── clients.py       # Client management
│   │   │   ├── skus.py          # SKU management
│   │   │   ├── campaigns.py     # Campaign management
│   │   │   ├── metrics.py       # Performance metrics
│   │   │   └── intelligence.py  # Intelligence decisions
│   ├── core/
│   │   ├── config.py            # App configuration
│   │   ├── security.py          # JWT & security utilities
│   │   └── database.py          # MongoDB connection
│   ├── models/
│   │   ├── client.py            # Client model
│   │   ├── sku.py               # SKU model
│   │   ├── campaign.py          # Campaign model
│   │   ├── metrics.py           # Metrics model
│   │   └── benchmark.py         # Benchmark model
│   ├── intelligence/
│   │   ├── decision_engine.py   # Core decision logic
│   │   ├── explore_exploit.py   # EXPLORE/EXPLOIT modes
│   │   ├── thompson_sampling.py # Cold-start optimization
│   │   └── portfolio_theory.py  # Portfolio optimization
│   ├── integrators/
│   │   ├── base.py              # Base integrator class
│   │   ├── revealbot.py         # Revealbot integration
│   │   ├── adroll.py            # AdRoll integration
│   │   └── ...
│   ├── platforms/
│   │   ├── base.py              # Base platform class
│   │   ├── google_ads.py        # Google Ads integration
│   │   ├── meta.py              # Meta Ads integration
│   │   ├── tiktok.py            # TikTok Ads integration
│   │   └── linkedin.py          # LinkedIn Ads integration
│   └── main.py                  # FastAPI application
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── requirements.txt
├── .env.example
└── docker-compose.yml
```

## Development Phases

### Phase 1: Foundation ✓
- FastAPI + MongoDB + JWT auth
- Google Ads + Meta integration
- Revealbot + AdRoll connectors
- Basic EXPLORE/EXPLOIT intelligence
- Performance tracking APIs

### Phase 2: Intelligence Enhancement
- TikTok integration
- Thompson Sampling for cold-start
- Time-pattern optimization
- System-wide benchmarks

### Phase 3: Advanced Features
- Remaining integrators
- A/B testing framework
- Portfolio Theory optimization
- Predictive eROAS ML models

### Phase 4: LinkedIn & Expansion
- LinkedIn Ads integration
- Geographic expansion features
- Advanced reporting

### Phase 5: Production
- Monitoring + alerting
- Security hardening
- Load testing + deployment

## API Documentation

Once running, access interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_intelligence.py
```

## Contributing

1. Create feature branch from `staging`
2. Make changes with tests
3. Ensure >80% test coverage
4. Submit PR to `staging` branch

## License

Proprietary - All Rights Reserved
