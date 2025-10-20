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
│   ├── api/                     # REST API endpoints
│   ├── autopilot/               # Campaign automation
│   ├── core/                    # Configuration & security
│   ├── creative_generation/     # AI-powered creative assets
│   ├── design_research/         # Design intelligence
│   ├── intelligence/            # Decision engine
│   ├── integrators/             # Third-party platform integrators
│   ├── meta_learning/           # Cross-client learning
│   ├── models/                  # Database models
│   ├── platforms/               # Ad platform integrations
│   ├── strategy_engine/         # Strategic analysis (7 layers)
│   │   └── analysis/
│   │       ├── layer1_price_elasticity.py
│   │       ├── layer2_category_archaeology.py
│   │       ├── layer3_cultural_cartography.py
│   │       ├── layer4_competitive_semiotics.py
│   │       └── models.py
│   └── main.py
├── docs/
│   ├── guides/                  # User guides & documentation
│   │   ├── API_KEYS_GUIDE.md
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   ├── QUICKSTART.md
│   │   ├── SCRAPER_STATUS.md
│   │   └── TESTING_GUIDE.md
│   ├── analysis_outputs/        # Generated analysis reports
│   └── LAYER4_UNIVERSAL_SCRIPT_VERIFICATION.md
├── scripts/                     # Universal utility scripts
│   ├── analyze_any_brand.py     # Multi-layer brand analyzer
│   └── test_layer4_visual_analysis.py  # Layer 4 tester
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── requirements.txt
├── .env.example
├── IMPLEMENTATION_ROADMAP.md    # Development roadmap
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
