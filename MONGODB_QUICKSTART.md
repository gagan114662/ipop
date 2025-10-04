# MongoDB Quick Start - IPOP System

## ✅ What I've Set Up For You

### 1. Created Setup Scripts
- `setup_mongodb.sh` - Automated MongoDB setup script
- `MONGODB_SETUP_GUIDE.md` - Complete setup documentation

### 2. Docker Configuration
- `docker-compose.yml` - Already configured with MongoDB 7.0
- Includes: MongoDB, Redis, API, and Mongo Express Web UI

### 3. Database Schema
- Index creation scripts in `app/db/create_indexes.py`
- 6 collections with optimized indexes

---

## 🚀 Quick Start (3 Steps)

### Step 1: Wait for Docker Images to Download
Docker is currently downloading MongoDB and Redis images. This is a one-time download (~300MB).

Check progress:
```bash
docker ps -a
```

When you see containers with names like `ipop_mongodb` and `ipop_redis`, proceed to Step 2.

### Step 2: Run the Setup Script
```bash
cd /Users/gagan/Desktop/gagan_projects/computeruse2/ipop
./setup_mongodb.sh
```

This will:
- ✅ Start MongoDB on port 27017
- ✅ Start Redis on port 6379
- ✅ Create database `ipop_media_buying`
- ✅ Create 6 collections
- ✅ Create all indexes
- ✅ Verify everything works

### Step 3: Connect MongoDB Compass
1. Open `/Applications/MongoDB Compass.app`
2. Click "New Connection"
3. Enter: `mongodb://localhost:27017`
4. Click "Connect"
5. Select database: `ipop_media_buying`

---

## 📊 What Gets Created

### Database
```
Name: ipop_media_buying
```

### Collections (6 total)
| Collection | Purpose |
|------------|---------|
| `clients` | User accounts & authentication |
| `skus` | Product/SKU management |
| `campaigns` | Ad campaigns (Google, Meta, TikTok, LinkedIn) |
| `performance_metrics` | Campaign performance data |
| `intelligence_decisions` | AI optimization decisions |
| `system_benchmarks` | Industry benchmarks |

### Indexes (22 total)
All optimized for query performance:
- Unique indexes on email, client_id, campaign_id
- Compound indexes for filtering and sorting
- Timestamp indexes for time-series queries

---

## 🔍 Verify Setup

### Check MongoDB is Running
```bash
docker ps
# Should show: ipop_mongodb, ipop_redis
```

### Check Database Exists
```bash
docker exec ipop_mongodb mongosh --eval "show dbs"
# Should include: ipop_media_buying
```

### Check Collections
```bash
docker exec ipop_mongodb mongosh --eval "
use ipop_media_buying
db.getCollectionNames()
"
# Should show all 6 collections
```

### Test API Connection
```bash
# Start the API
docker-compose up -d api

# Test health
curl http://localhost:8000/health
```

---

## 🌐 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **MongoDB** | localhost:27017 | No auth (dev) |
| **MongoDB Compass** | mongodb://localhost:27017 | No auth |
| **Mongo Express** | http://localhost:8081 | admin / admin123 |
| **API Docs** | http://localhost:8000/docs | JWT token |
| **Redis** | localhost:6379 | No auth (dev) |

---

## 📝 Manual Setup (If Script Fails)

### 1. Start Containers
```bash
docker-compose up -d mongodb redis
```

### 2. Create Database
```bash
docker exec -it ipop_mongodb mongosh
```

In mongosh:
```javascript
use ipop_media_buying
db.createCollection("clients")
db.createCollection("skus")
db.createCollection("campaigns")
db.createCollection("performance_metrics")
db.createCollection("intelligence_decisions")
db.createCollection("system_benchmarks")
exit
```

### 3. Create Indexes
```bash
cd /Users/gagan/Desktop/gagan_projects/computeruse2/ipop
source venv/bin/activate
python3 -m app.db.create_indexes create
```

---

## 🎯 Success Checklist

- [ ] Docker images downloaded (check `docker images`)
- [ ] MongoDB container running (`docker ps | grep mongodb`)
- [ ] Database `ipop_media_buying` created
- [ ] All 6 collections exist
- [ ] All indexes created
- [ ] MongoDB Compass can connect
- [ ] API starts without errors

---

## 🚨 Troubleshooting

### "Cannot connect to Docker daemon"
```bash
open -a Docker
# Wait 30 seconds for Docker to start
```

### "Port 27017 already in use"
```bash
# Stop other MongoDB instances
brew services stop mongodb-community
lsof -ti:27017 | xargs kill -9
```

### "Collection already exists"
This is normal - the setup script is idempotent and safe to run multiple times.

### "Connection refused"
Wait a few more seconds for MongoDB to finish starting:
```bash
docker logs ipop_mongodb
# Look for "Waiting for connections"
```

---

## 🎉 Next Steps After Setup

### 1. Start the Full System
```bash
docker-compose up -d
```

### 2. View Logs
```bash
docker-compose logs -f
```

### 3. Access API Documentation
```
http://localhost:8000/docs
```

### 4. Create Your First Client
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company",
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### 5. Browse with MongoDB Compass
- Connect to `localhost:27017`
- Explore `ipop_media_buying` database
- View collections and documents

---

## 📦 Current Status

✅ Docker is running
⏳ MongoDB images downloading (~300MB, one-time)
✅ Setup scripts created and ready
✅ Configuration files ready
✅ Index creation scripts ready

**Estimated time to complete**: 5-10 minutes (depending on download speed)

---

**Need help?** See `MONGODB_SETUP_GUIDE.md` for detailed instructions.
