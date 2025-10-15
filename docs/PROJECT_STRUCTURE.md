# IPOP Project Structure

This document describes the organization of the IPOP (Intelligent Pixel Optimization Platform) codebase.

## Directory Layout

```
ipop/
├── app/                    # Main application code
│   ├── api/               # API endpoints
│   │   └── v1/           # API version 1
│   ├── core/             # Core utilities (config, database, security)
│   ├── db/               # Database utilities (indexes, seeds)
│   ├── intelligence/     # AI/ML optimization engines
│   ├── integrators/      # Third-party integrations
│   ├── models/           # Pydantic data models
│   ├── platforms/        # Ad platform clients (Google, Meta, etc.)
│   ├── tasks/            # Background tasks (metrics, scheduling)
│   └── main.py           # FastAPI application entry point
│
├── assets/                # Static assets (images, logos)
│
├── demos/                 # Demo scripts and examples
│   ├── create_demo_video.py
│   ├── demo_campaign_creation.py
│   ├── demo_metrics_polling.py
│   ├── demo_with_docker.py
│   ├── simple_demo.py
│   ├── test_simulation.py
│   ├── create_sku.py
│   ├── create_sku_for_campaign.py
│   ├── simple_app.py
│   ├── test_app.py
│   └── README.md
│
├── docs/                  # Documentation
│   ├── ALL_FIXES_COMPLETE.md
│   ├── API_KEYS_GUIDE.md
│   ├── CODE_AUDIT.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── FINAL_GRADE.md
│   ├── FINAL_SUMMARY.md
│   ├── PROJECT_STRUCTURE.md (this file)
│   ├── PUSH_COMPLETE.md
│   ├── QUICKSTART.md
│   ├── README.md (symlink to ../README.md)
│   ├── SETUP_SUMMARY.md
│   ├── TESTING_GUIDE.md
│   ├── VIDEO_RECORDING_GUIDE.md
│   └── WEB_UI_GUIDE.md
│
├── scripts/               # Utility scripts
│   ├── linkedin_oauth.py
│   ├── meta_access_token.py
│   ├── setup_mongodb.sh
│   ├── verify_setup.py
│   └── README.md
│
├── tests/                 # Test suite
│   ├── integration/      # Integration tests
│   ├── unit/             # Unit tests
│   ├── conftest.py       # Pytest configuration
│   ├── test_creative_assets.py
│   ├── test_google_ads_credentials.py
│   ├── test_linkedin_credentials.py
│   └── test_platform_apis.py
│
├── web/                   # Web interface
│   ├── web_ui_dashboard.html
│   ├── serve_dashboard.py
│   └── README.md
│
├── docker-compose.yml     # Docker services configuration
├── Dockerfile             # Container image definition
├── pytest.ini             # Pytest configuration
├── README.md              # Main project README
└── requirements.txt       # Python dependencies
```

## Core Components

### Application (`app/`)

The main application code following a layered architecture:

- **API Layer** (`api/v1/`): RESTful endpoints for all operations
- **Core Layer** (`core/`): Configuration, database, security, rate limiting
- **Data Layer** (`models/`): Pydantic models for validation and serialization
- **Intelligence Layer** (`intelligence/`): AI/ML engines for optimization
- **Platform Layer** (`platforms/`): Integrations with ad platforms
- **Task Layer** (`tasks/`): Background jobs and schedulers

### Demonstrations (`demos/`)

Scripts demonstrating various system capabilities:

- Campaign creation with configurable parameters
- Metrics polling and ingestion
- Docker-based testing
- Simplified testing applications

### Documentation (`docs/`)

Comprehensive documentation including:

- Quick start guides
- Deployment instructions
- API documentation
- Testing guides
- Setup summaries

### Scripts (`scripts/`)

Utility scripts for:

- Platform authentication (OAuth, access tokens)
- System setup and verification
- Database initialization

### Tests (`tests/`)

Comprehensive test suite with:

- **Unit tests**: Individual component testing
- **Integration tests**: Multi-component and API testing
- Platform API credential verification
- Creative asset testing

### Web Interface (`web/`)

Modern web dashboard providing:

- SKU management
- Campaign creation and configuration
- Real-time metrics visualization
- AI optimization controls

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database for data storage
- **Redis**: Caching and rate limiting
- **Pydantic**: Data validation and settings management

### Platform Integrations
- **Google Ads API**: Campaign management and metrics
- **Meta Marketing API**: Facebook/Instagram advertising
- **TikTok Ads API**: TikTok advertising
- **LinkedIn Ads API**: LinkedIn advertising

### Intelligence/ML
- **Thompson Sampling**: Multi-armed bandit for creative testing
- **Explore-Exploit**: Balance between exploration and exploitation
- **Decision Engine**: Automated optimization decisions

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Uvicorn**: ASGI server
- **APScheduler**: Task scheduling

## Best Practices

### Code Organization
- Each module has a single, clear responsibility
- Dependencies flow inward (API → Services → Models)
- Configuration is externalized via environment variables

### Testing
- Unit tests for business logic
- Integration tests for API endpoints
- Platform-specific credential testing
- Test fixtures and mocks for external services

### Documentation
- Inline code documentation
- Comprehensive README files per directory
- API documentation via OpenAPI/Swagger
- Deployment and setup guides

### Security
- JWT-based authentication
- Rate limiting on API endpoints
- Environment-based secrets management
- Multi-tenant data isolation

## Getting Started

1. **Setup**: See `docs/QUICKSTART.md`
2. **Development**: See `README.md`
3. **Testing**: See `docs/TESTING_GUIDE.md`
4. **Deployment**: See `docs/DEPLOYMENT_GUIDE.md`
5. **Web UI**: See `web/README.md`

