# Web Interface

Web dashboard and server files for the IPOP Media Buying Management System.

## Files

- `web_ui_dashboard.html` - Main dashboard interface with:
  - SKU management
  - Campaign creation with configurable parameters
  - Real-time metrics monitoring
  - AI optimization controls
  - Activity logging
  
- `serve_dashboard.py` - Simple HTTP server for the dashboard

## Usage

### Start the Dashboard Server

```bash
python web/serve_dashboard.py
```

### Access the Dashboard

Open your browser to:
```
http://localhost:3000/web_ui_dashboard.html
```

## Features

- **SKU Management**: Create and view product SKUs
- **Campaign Creation**: Configure campaigns with custom parameters:
  - Platform selection (Google Ads, Meta)
  - Budget settings
  - Geographic targeting
  - Demographic targeting (age, interests)
  - Keywords and bidding strategies
- **Real-time Metrics**: View campaign performance metrics
- **AI Optimization**: Manual campaign optimization controls
- **Auto-refresh**: Campaigns and metrics update automatically

## Requirements

The IPOP API must be running for full functionality:
```bash
docker-compose up -d
```

Or run in demo mode (simulated data) without the API.

