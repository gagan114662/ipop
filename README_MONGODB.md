# Resize Backend - MongoDB Setup

## ✅ Database Migration Complete
This application now uses **MongoDB only** (PostgreSQL and Redis have been completely removed).

## 📁 Project Structure
```
Resize_backend/
├── mongodb_data/          # MongoDB database files (local data)
├── app/                   # Application code
├── start_mongodb.sh       # Start MongoDB server
├── start_app.sh          # Start application
├── start_all.sh          # Start everything at once
└── .env                  # Configuration
```

## 🚀 Quick Start

### Option 1: Start Everything at Once (Recommended)
```bash
cd /Users/gaganarora/Desktop/gagan_projects/Database_migration/Resize_backend
./start_all.sh
```

### Option 2: Start Services Separately

**Terminal 1 - Start MongoDB:**
```bash
cd /Users/gaganarora/Desktop/gagan_projects/Database_migration/Resize_backend
./start_mongodb.sh
```

**Terminal 2 - Start Application:**
```bash
cd /Users/gaganarora/Desktop/gagan_projects/Database_migration/Resize_backend
./start_app.sh
```

### Option 3: Manual Commands

**Start MongoDB:**
```bash
/Users/gaganarora/Downloads/mongodb-macos-aarch64--8.2.1/bin/mongod \
  --dbpath /Users/gaganarora/Desktop/gagan_projects/Database_migration/Resize_backend/mongodb_data \
  --port 27017
```

**Start Application:**
```bash
cd /Users/gaganarora/Desktop/gagan_projects/Database_migration/Resize_backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Access Points

Once started, access your application at:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Platforms Endpoint**: http://localhost:8000/api/v1/platforms
- **Alternative Docs**: http://localhost:8000/redoc

## 📊 MongoDB Collections

- `jobs` - Main job records
- `resize_jobs` - Job queue for background processing
- `ad_briefs` - Ad campaign briefs

## 🔧 Configuration

Edit `.env` file to customize:
```bash
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=creative_resizer
MONGODB_DATA_PATH=./mongodb_data
```

## 🛑 Stopping Services

Press `Ctrl+C` in the terminal where services are running.

Or kill by port:
```bash
# Stop application
kill $(lsof -t -i:8000)

# Stop MongoDB
kill $(lsof -t -i:27017)
```

## ✅ Migration Details

### What Changed:
- ✅ Removed PostgreSQL completely
- ✅ Removed Redis completely
- ✅ All data now in MongoDB
- ✅ Job queue uses MongoDB
- ✅ All models converted to Pydantic + MongoDB
- ✅ All routes updated to use MongoDB

### Database Location:
MongoDB data is stored in: `./mongodb_data/`

This folder contains all your database files and should NOT be committed to git.

## 📝 Verify Installation

Check if services are running:
```bash
# Check MongoDB
lsof -i :27017

# Check Application
lsof -i :8000

# View MongoDB data
python3 verify_mongodb_data.py
```

## 🔍 View Data

Use MongoDB Compass GUI:
- Download: https://www.mongodb.com/products/compass
- Connect to: `mongodb://localhost:27017`
- Database: `creative_resizer`

## 📦 Requirements

- Python 3.8+
- MongoDB binary (already downloaded)
- Dependencies in `requirements.txt`

Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

## 🎉 You're All Set!

Your application is fully integrated with MongoDB and ready to use!
