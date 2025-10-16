# MongoDB Migration Guide

## Overview

The Resize Backend has been successfully migrated from **Redis** to **MongoDB** for job queue management.

## What Changed

### 1. **Job Queue Storage**
   - **Before**: Redis (in-memory key-value store)
   - **After**: MongoDB (persistent document database)

### 2. **Files Modified**
   - `app/services/mongodb_service.py` - New MongoDB service (replaces Redis)
   - `app/workers/resize_worker.py` - Updated to use MongoDB
   - `app/main.py` - Updated to initialize MongoDB connection
   - `app/config/settings.py` - Added MongoDB configuration
   - `requirements.txt` - Added motor and pymongo packages

### 3. **New Features**
   - **Persistent Job Queue**: Jobs survive server restarts
   - **Atomic Operations**: No race conditions between workers
   - **Job Status Tracking**: PENDING → PROCESSING → COMPLETED/FAILED
   - **Query Capabilities**: Easy job monitoring and debugging

## MongoDB Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# MongoDB Settings
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=creative_resizer
```

## Starting MongoDB

### Method 1: Direct Command (Recommended for macOS)

```bash
# Remove old socket file if exists
rm -f /tmp/mongodb-27017.sock

# Start MongoDB
/Users/gaganarora/Downloads/mongodb-macos-aarch64--8.2.1/bin/mongod \\
  --dbpath /Users/gaganarora/Desktop/gagan_projects/Database_migration/mongodb_data \\
  --port 27017 \\
  --bind_ip 127.0.0.1
```

### Method 2: Using Background Process

```bash
# In a separate terminal window
/Users/gaganarora/Downloads/mongodb-macos-aarch64--8.2.1/bin/mongod \\
  --dbpath /Users/gaganarora/Desktop/gagan_projects/Database_migration/mongodb_data \\
  --port 27017
```

## Testing the Migration

### 1. Test MongoDB Connection

```bash
python3 test_mongodb_simple.py
```

Expected output:
```
============================================================
MongoDB Connection Test
============================================================

1. Connecting to MongoDB...
   ✅ Successfully connected to MongoDB

2. Testing insert operation...
   ✅ Successfully inserted document

3. Testing find operation...
   ✅ Successfully found document

4. Testing update operation...
   ✅ Successfully updated document

5. Cleaning up test data...
   ✅ Successfully deleted document

============================================================
✅ All MongoDB tests passed!
============================================================
```

### 2. Start the Application

```bash
# Terminal 1: Start MongoDB (if not running)
/Users/gaganarora/Downloads/mongodb-macos-aarch64--8.2.1/bin/mongod \\
  --dbpath /Users/gaganarora/Desktop/gagan_projects/Database_migration/mongodb_data \\
  --port 27017

# Terminal 2: Start the FastAPI application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Start the background worker
python start_worker.py
```

## MongoDB Service API

### Key Methods

```python
from app.services.mongodb_service import MongoDBService

# Initialize
mongodb_service = MongoDBService()
await mongodb_service.connect()

# Add job to queue
await mongodb_service.add_job({
    'job_id': 'job-123',
    'timestamp': time.time()
})

# Get next job from queue (atomic)
job = await mongodb_service.get_job()

# Check pending jobs
count = await mongodb_service.get_pending_job_count()

# Mark job as completed
await mongodb_service.mark_job_completed('job-123')

# Mark job as failed
await mongodb_service.mark_job_failed('job-123', 'Error message')

# Cleanup old jobs (older than 7 days)
await mongodb_service.cleanup_old_jobs(days=7)
```

## Job Document Structure

```javascript
{
  _id: ObjectId("..."),
  job_id: "job-12345",
  status: "PENDING",  // PENDING | PROCESSING | COMPLETED | FAILED
  timestamp: ISODate("2025-10-15T18:00:00Z"),
  created_at: ISODate("2025-10-15T18:00:00Z"),
  processing_started_at: ISODate("2025-10-15T18:00:05Z"),  // optional
  completed_at: ISODate("2025-10-15T18:00:30Z"),  // optional
  failed_at: ISODate("2025-10-15T18:00:30Z"),  // optional
  error: "Error message"  // optional, only for failed jobs
}
```

## Monitoring MongoDB

### Check Job Queue Status

```bash
# Connect to MongoDB shell
/Users/gaganarora/Downloads/mongodb-macos-aarch64--8.2.1/bin/mongosh mongodb://localhost:27017/creative_resizer

# View all jobs
db.resize_jobs.find()

# Count pending jobs
db.resize_jobs.countDocuments({status: "PENDING"})

# View processing jobs
db.resize_jobs.find({status: "PROCESSING"})

# View failed jobs
db.resize_jobs.find({status: "FAILED"})
```

## Advantages of MongoDB Over Redis

1. **Persistence**: Jobs survive server restarts
2. **Atomic Operations**: Built-in `findOneAndUpdate` prevents race conditions
3. **Rich Queries**: Easy to monitor, filter, and debug jobs
4. **Scalability**: Better for growing applications
5. **Job History**: Keep completed/failed jobs for analysis
6. **Indexing**: Fast queries on status and timestamp

## Backward Compatibility

The Redis service code is kept but commented out in:
- `app/main.py` (lines 39-42, 59-60)
- `app/services/redis_service.py` (entire file preserved)

To revert to Redis:
1. Uncomment Redis initialization in `app/main.py`
2. Update worker to use `RedisService` instead of `MongoDBService`

## Troubleshooting

### MongoDB Won't Start

**Error**: "Failed to unlink socket file"
```bash
# Solution: Remove the socket file
sudo rm -f /tmp/mongodb-27017.sock
```

**Error**: "Permission denied" on data directory
```bash
# Solution: Fix permissions
chmod 755 /Users/gaganarora/Desktop/gagan_projects/Database_migration/mongodb_data
```

### Connection Refused

**Error**: "Connection refused"
```bash
# Check if MongoDB is running
ps aux | grep mongod

# If not running, start it
/Users/gaganarora/Downloads/mongodb-macos-aarch64--8.2.1/bin/mongod \\
  --dbpath /Users/gaganarora/Desktop/gagan_projects/Database_migration/mongodb_data \\
  --port 27017
```

### Test Connection

```bash
python3 test_mongodb_simple.py
```

## Summary

✅ **Migration Complete**
- Redis job queue → MongoDB job queue
- All functionality preserved
- Added job persistence and better monitoring
- Backward compatible (Redis code preserved)

**Next Steps:**
1. Start MongoDB server
2. Test with `test_mongodb_simple.py`
3. Start application and worker
4. Test with real resize jobs

For questions or issues, refer to the log files or MongoDB documentation.
