# How to Start the System

## Prerequisites
✅ MongoDB is already running on port 27017

## Start the Application

### Option 1: Start Just the API (Quick Test)
```bash
cd /Users/gaganarora/Desktop/gagan_projects/Database_migration/Resize_backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Start Full System (API + Worker)

**Terminal 1 - FastAPI Application:**
```bash
cd /Users/gaganarora/Desktop/gagan_projects/Database_migration/Resize_backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Background Worker:**
```bash
cd /Users/gaganarora/Desktop/gagan_projects/Database_migration/Resize_backend
python3 start_worker.py
```

## Verify It's Working

### 1. Check API Health
Open browser: http://localhost:8000

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": 1760554543.305
}
```

### 2. Check API Documentation
Open browser: http://localhost:8000/docs

You should see the Swagger UI with all endpoints.

### 3. Check MongoDB Connection in Logs
Look for this in the terminal output:
```
✅ Connected to MongoDB
```

## Test MongoDB Migration

### Create a test job via API:
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "accept: application/json" \
  -F "file=@your_image.jpg" \
  -F 'platforms=["instagram_feed","facebook_feed"]'
```

### Check MongoDB Compass:
1. Connect to: `mongodb://localhost:27017`
2. Database: `creative_resizer`
3. Collection: `resize_jobs`
4. You should see new job documents appearing!

## Stop the System

Press `Ctrl+C` in each terminal window to stop the services.
