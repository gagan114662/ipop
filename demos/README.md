# Demos

This directory contains demonstration scripts and examples for the IPOP system.

## Scripts

- `create_demo_video.py` - Comprehensive demo for video recording
- `demo_campaign_creation.py` - Campaign creation demonstration
- `demo_metrics_polling.py` - Metrics polling demonstration  
- `demo_with_docker.py` - Docker-based demonstration
- `simple_demo.py` - Simple demonstration script
- `test_simulation.py` - Full simulation for testing
- `create_sku.py` - SKU creation helper
- `create_sku_for_campaign.py` - SKU creation for campaign testing
- `simple_app.py` - Simplified app for testing (no DB required)
- `test_app.py` - Test application

## Usage

Run any demo script with:
```bash
python demos/<script_name>.py
```

For Docker-based demos:
```bash
docker-compose up -d
python demos/demo_with_docker.py
```

