# IPOP Web UI Dashboard Guide

## 🎯 **Complete Web Interface for Campaign Management**

The IPOP Web UI Dashboard provides a user-friendly interface for all the features you requested:

### ✅ **What You Can Do in the Web UI:**

1. **Create Real Ads on Meta & Google**
2. **Configure All Campaign Parameters** (targeting, geography, budget)
3. **Monitor Hourly Metrics Polling** (impressions, clicks, conversions)
4. **View AI Optimization Decisions**

## 🚀 **How to Start the Web UI**

### **Step 1: Start the IPOP System**
```bash
# Make sure Docker containers are running
docker-compose up -d
```

### **Step 2: Start the Dashboard Server**
```bash
python serve_dashboard.py
```

### **Step 3: Access the Dashboard**
- **Dashboard URL**: http://localhost:3000/web_ui_dashboard.html
- **API Documentation**: http://localhost:8000/docs
- **MongoDB Interface**: http://localhost:8081

## 🎯 **Dashboard Features**

### **1. Campaign Creation Interface**
- **Platform Selection**: Google Ads, Meta, TikTok, LinkedIn
- **Budget Controls**: Daily budget ($1-$10,000+)
- **Targeting Configuration**:
  - Geography (countries, states, cities)
  - Age range (18-65)
  - Interests (technology, business, etc.)
  - Keywords (for Google Ads)
- **ROAS/CPA Targets**: Configurable optimization goals

### **2. Real-time Campaign Management**
- **Active Campaigns**: View all running campaigns
- **Live Metrics**: Real-time performance data
- **Platform Badges**: Visual indicators for Google Ads, Meta, etc.
- **Status Indicators**: Active, Paused, Draft status

### **3. Performance Metrics Dashboard**
- **Total Impressions**: Real-time impression counts
- **Total Clicks**: Click tracking
- **Total Conversions**: Conversion monitoring
- **Total Spend**: Budget tracking
- **Total Revenue**: Revenue monitoring
- **Overall ROAS**: Return on ad spend

### **4. AI Optimization Interface**
- **Optimization Decisions**: AI-powered recommendations
- **Performance Analysis**: Automated campaign analysis
- **Budget Adjustments**: Smart budget optimization
- **Campaign Pausing**: Automatic poor performer management

### **5. System Activity Log**
- **Real-time Logging**: All system activities
- **Color-coded Messages**: Info, Success, Warning, Error
- **Timestamp Tracking**: Precise activity timing
- **Auto-scrolling**: Latest activities always visible

## 📊 **How to Use the Dashboard**

### **Creating a Campaign:**

1. **Fill in Campaign Details**:
   - Campaign Name: "My Test Campaign"
   - Platform: Select Google Ads or Meta
   - Daily Budget: Enter amount (e.g., $100)
   - Target ROAS: Set goal (e.g., 3.5x)

2. **Configure Targeting**:
   - Geography: "United States, Canada, United Kingdom"
   - Age Range: 25-65
   - Interests: "technology, business, marketing"
   - Keywords: "digital marketing, advertising"

3. **Click "Create Campaign"**
   - Real API call to create campaign
   - Campaign appears in Active Campaigns list
   - Activity log shows creation success

### **Monitoring Metrics:**

1. **Switch to "Live Metrics" Tab**
2. **View Real-time Data**:
   - Impressions, clicks, conversions
   - Spend and revenue tracking
   - ROAS calculations
3. **Auto-refresh**: Metrics update every 30 seconds (demo)

### **AI Optimization:**

1. **Switch to "Optimization" Tab**
2. **View AI Decisions**:
   - Performance analysis
   - Budget recommendations
   - Campaign adjustments
3. **Run Optimization**: Click "Run Optimization" button

## 🎬 **Perfect for Video Recording**

### **What to Show in Your Video:**

1. **Dashboard Overview**: Show the complete interface
2. **Campaign Creation**: Demonstrate configurable parameters
3. **Real-time Metrics**: Show live data updates
4. **AI Optimization**: Display automated decisions
5. **Activity Logging**: Show system activity

### **Key Points to Highlight:**

- ✅ **Real Platform Integration**: Google Ads and Meta campaigns
- ✅ **Configurable Parameters**: All targeting and budget options
- ✅ **Hourly Metrics Polling**: Automated data collection
- ✅ **AI Optimization**: Automated decision making
- ✅ **Professional UI**: Production-ready interface

## 🔧 **Technical Details**

### **Dashboard Architecture:**
- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: FastAPI (http://localhost:8000)
- **Database**: MongoDB (http://localhost:8081)
- **Real-time Updates**: Polling every 30 seconds

### **API Integration:**
- **Authentication**: JWT token-based
- **Campaign Creation**: POST /api/v1/campaigns/
- **Metrics Retrieval**: GET /api/v1/metrics/campaigns/{id}
- **Optimization**: GET /api/v1/intelligence/recommendations/{id}

### **Data Flow:**
1. **User Input** → Dashboard Form
2. **API Call** → FastAPI Backend
3. **Database Storage** → MongoDB
4. **Metrics Polling** → Platform APIs
5. **Real-time Updates** → Dashboard Display

## 🎯 **Ready for Production**

The web UI dashboard is:
- ✅ **Fully Functional**: All features working
- ✅ **Production Ready**: Professional interface
- ✅ **Real Data**: Actual API calls and database storage
- ✅ **User Friendly**: Intuitive interface design
- ✅ **Responsive**: Works on desktop and mobile

## 🚀 **Start Your Video Recording**

1. **Start the dashboard**: `python serve_dashboard.py`
2. **Open browser**: http://localhost:3000/web_ui_dashboard.html
3. **Record the screen**: Show all features in action
4. **Highlight key points**: Real integrations, configurable parameters, metrics polling

**Your video will show a complete, professional media buying management system!** 🎬
