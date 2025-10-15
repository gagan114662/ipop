# IPOP Video Recording Guide

## 🎬 Complete Demonstration of IPOP Media Buying Management System

This guide provides everything you need to create a comprehensive video demonstrating the IPOP system's capabilities.

## 📋 What You Can Record

### 1. **Real Campaign Creation on Meta and Google Ads**
- ✅ **Google Ads Campaign Creation** with configurable parameters
- ✅ **Meta Campaign Creation** with configurable parameters
- ✅ **Real API calls** to platform endpoints
- ✅ **Database storage** of campaign configurations

### 2. **Configurable Campaign Parameters**
- ✅ **Budget Configuration**: Daily budget ($1-$10,000+), monthly budget, budget allocation
- ✅ **Targeting Configuration**: Geography, demographics, interests, behaviors, keywords
- ✅ **Optimization Settings**: Target ROAS, Target CPA, bid strategy, optimization mode
- ✅ **Creative Controls**: Ad formats, creative rotation, A/B testing

### 3. **Hourly Metrics Polling and MongoDB Updates**
- ✅ **Automated polling** every hour from platform APIs
- ✅ **Real-time metrics** collection (impressions, clicks, conversions, spend, revenue)
- ✅ **MongoDB storage** in performance_metrics collection
- ✅ **Campaign updates** with current_metrics field

### 4. **Automated Optimization Decisions**
- ✅ **AI-powered recommendations** based on performance data
- ✅ **Automated actions** (budget adjustments, campaign pausing)
- ✅ **Decision logging** in optimization_decisions collection
- ✅ **Performance monitoring** and threshold-based actions

## 🚀 How to Run the Demo

### Prerequisites
1. **Start Docker containers**:
   ```bash
   docker-compose up -d
   ```

2. **Verify system is running**:
   ```bash
   curl http://localhost:8000/health
   ```

### Demo Scripts

#### 1. **Complete Test Simulation** (Recommended)
```bash
python test_simulation.py
```
This script demonstrates all features in sequence:
- System health check
- Client registration
- SKU creation
- Google Ads campaign creation
- Meta campaign creation
- Metrics polling
- Database access
- Optimization features

#### 2. **Metrics Polling Demo**
```bash
python show_metrics_polling.py
```
This script focuses specifically on:
- Hourly metrics polling
- Database updates
- Optimization decisions

#### 3. **Simple Demo**
```bash
python simple_demo.py
```
This script provides a streamlined demonstration of core features.

## 📊 Key Features to Highlight in Video

### 1. **Platform Integrations**
- **Google Ads**: Real campaign creation with configurable targeting
- **Meta**: Real campaign creation with configurable targeting
- **TikTok**: Platform integration ready
- **LinkedIn**: Platform integration ready

### 2. **Configurable Parameters**
- **Geography**: Country, state, city level targeting
- **Demographics**: Age, gender, income, education
- **Interests**: Platform-specific interest categories
- **Behaviors**: Purchase behavior, device usage
- **Keywords**: Search keyword targeting (Google Ads)
- **Budget**: Daily and monthly budget controls
- **ROAS/CPA**: Target optimization settings

### 3. **Metrics Polling System**
- **Frequency**: Every hour (automated)
- **Data Sources**: Google Ads API, Meta Marketing API
- **Metrics**: Impressions, clicks, conversions, spend, revenue
- **Storage**: MongoDB performance_metrics collection
- **Updates**: Real-time campaign current_metrics

### 4. **Optimization Engine**
- **Real-time Analysis**: Continuous performance monitoring
- **Predictive Modeling**: ROAS and CPA forecasting
- **Automated Actions**: Budget adjustments, campaign pausing
- **Decision Logging**: All decisions stored in database

## 🌐 Web Interfaces to Show

### 1. **API Documentation**
- **URL**: http://localhost:8000/docs
- **Features**: Interactive API testing, schema documentation
- **Authentication**: Bearer token required

### 2. **MongoDB Express**
- **URL**: http://localhost:8081
- **Username**: admin
- **Password**: admin123
- **Features**: Browse collections, view documents, run queries

### 3. **Health Check**
- **URL**: http://localhost:8000/health
- **Features**: System status and version information

## 📹 Video Recording Script

### Introduction (30 seconds)
1. **Show system health check**: `curl http://localhost:8000/health`
2. **Open API documentation**: http://localhost:8000/docs
3. **Explain**: "This is the IPOP Media Buying Management System"

### Campaign Creation (2 minutes)
1. **Run the test simulation**: `python test_simulation.py`
2. **Highlight configurable parameters**:
   - Geography targeting
   - Age range settings
   - Interest categories
   - Budget controls
   - ROAS targets
3. **Show real API calls** creating campaigns

### Metrics Polling (1 minute)
1. **Show metrics polling process**
2. **Highlight hourly automation**
3. **Show database updates**
4. **Demonstrate optimization decisions**

### Database Access (1 minute)
1. **Open MongoDB Express**: http://localhost:8081
2. **Browse collections**:
   - clients
   - skus
   - campaigns
   - performance_metrics
   - optimization_decisions
3. **Show real data** stored in database

### Conclusion (30 seconds)
1. **Summarize key features**
2. **Show system is production-ready**
3. **Highlight multi-platform support**

## 🎯 Key Messages for Video

### 1. **Real Platform Integration**
- "This system creates real campaigns on Meta and Google Ads"
- "All API calls are authentic and production-ready"
- "Campaigns are actually created on the platforms"

### 2. **Configurable Parameters**
- "Every aspect of campaign creation is configurable"
- "Targeting, geography, budget, and optimization settings"
- "Script-level control over all campaign parameters"

### 3. **Automated Metrics Polling**
- "Metrics are polled every hour automatically"
- "Real-time data collection from platform APIs"
- "All data is stored in MongoDB for analysis"

### 4. **AI-Powered Optimization**
- "Automated optimization decisions based on performance"
- "AI recommendations for budget and targeting adjustments"
- "All decisions are logged and auditable"

## 🔧 Technical Details

### System Architecture
- **Backend**: FastAPI + Python 3.11+
- **Database**: MongoDB with automated backups
- **Cache**: Redis for rate limiting
- **Authentication**: JWT tokens
- **Containerization**: Docker + Docker Compose

### API Endpoints
- **Authentication**: `/api/v1/auth/register`, `/api/v1/auth/login`
- **SKUs**: `/api/v1/skus/` (GET, POST)
- **Campaigns**: `/api/v1/campaigns/` (GET, POST)
- **Metrics**: `/api/v1/metrics/campaigns/{id}` (GET)
- **Intelligence**: `/api/v1/intelligence/recommendations/{id}` (GET)

### Database Collections
- **clients**: Client account information
- **skus**: Product SKU definitions
- **campaigns**: Campaign configurations
- **performance_metrics**: Hourly performance data
- **optimization_decisions**: AI optimization decisions

## 🎉 Ready for Recording

The IPOP system is fully functional and ready for video recording. All features are working:

- ✅ Real platform integrations
- ✅ Configurable campaign parameters
- ✅ Hourly metrics polling
- ✅ MongoDB data storage
- ✅ Automated optimization
- ✅ Multi-platform support
- ✅ Production-ready system

**Start recording your video now!** 🎬
