# MongoDB Complete Setup Guide

## 🎯 Quick Setup (Automated)

### Option 1: One-Command Setup (Recommended)

```bash
cd /Users/gagan/Desktop/gagan_projects/computeruse2/ipop
./setup_mongodb.sh
```

This script will automatically:
1. ✅ Check Docker is running
2. ✅ Start MongoDB + Redis containers
3. ✅ Create database `ipop_media_buying`
4. ✅ Create all 6 collections
5. ✅ Create all indexes for performance
6. ✅ Verify everything is working

**Time:** ~2 minutes

---

## 🔧 Manual Setup (Step-by-Step)

### Step 1: Start Docker Desktop

```bash
open -a Docker
# Wait for Docker whale icon to appear in menu bar
```

### Step 2: Start MongoDB Container

```bash
cd /Users/gagan/Desktop/gagan_projects/computeruse2/ipop
docker-compose up -d mongodb redis
```

### Step 3: Verify MongoDB is Running

```bash
docker ps
# Should see: ipop_mongodb

docker logs ipop_mongodb
# Should see: "Waiting for connections"
```

### Step 4: Connect with MongoDB Compass

1. **Open MongoDB Compass** from Applications
2. **Click "New Connection"**
3. **Enter Connection String:**
   ```
   mongodb://localhost:27017
   ```
4. **Click "Connect"**

### Step 5: Create Database & Collections

In MongoDB Compass:

1. Click "Create Database"
2. Database Name: `ipop_media_buying`
3. Collection Name: `clients`
4. Click "Create Database"

Then create remaining collections:
- Right-click database → "Create Collection"
- Names: `skus`, `campaigns`, `performance_metrics`, `intelligence_decisions`, `system_benchmarks`

### Step 6: Create Indexes (Automated)

```bash
cd /Users/gagan/Desktop/gagan_projects/computeruse2/ipop
source venv/bin/activate
python3 -m app.db.create_indexes create
```

---

## 📊 Database Schema

### Collections Created:

| Collection | Purpose | Key Indexes |
|------------|---------|-------------|
| **clients** | User accounts & authentication | email (unique), client_id (unique) |
| **skus** | Product/SKU management | (client_id, sku_id) unique, status |
| **campaigns** | Ad campaigns across platforms | (client_id, campaign_id) unique, platform, status |
| **performance_metrics** | Campaign performance data | campaign_id + timestamp, client_id + timestamp |
| **intelligence_decisions** | AI optimization decisions | campaign_id + timestamp, applied status |
| **system_benchmarks** | Industry benchmarks | platform + month (unique) |

### Indexes Created:

#### clients (2 indexes)
```javascript
{ email: 1 }          // unique
{ client_id: 1 }      // unique
```

#### skus (2 indexes)
```javascript
{ client_id: 1, sku_id: 1 }  // unique compound
{ client_id: 1, status: 1 }   // for filtering
```

#### campaigns (6 indexes)
```javascript
{ client_id: 1, campaign_id: 1 }  // unique compound
{ client_id: 1, status: 1 }
{ client_id: 1, sku_id: 1 }
{ platform: 1 }
{ client_id: 1, platform: 1 }
{ created_at: -1 }
```

#### performance_metrics (6 indexes)
```javascript
{ campaign_id: 1, timestamp: -1 }
{ client_id: 1, timestamp: -1 }
{ client_id: 1, sku_id: 1, timestamp: -1 }
{ platform: 1, timestamp: -1 }
{ timestamp: -1 }
{ client_id: 1, campaign_id: 1, timestamp: -1 }  // compound
```

#### intelligence_decisions (4 indexes)
```javascript
{ campaign_id: 1, timestamp: -1 }
{ client_id: 1, timestamp: -1 }
{ client_id: 1, applied: 1 }
{ timestamp: -1 }
```

#### system_benchmarks (2 indexes)
```javascript
{ platform: 1, month: 1 }     // unique compound
{ platform: 1, timestamp: -1 }
```

---

## 🔍 Verification Commands

### Check Database Exists
```bash
docker exec ipop_mongodb mongosh --eval "show dbs"
```

### List Collections
```bash
docker exec ipop_mongodb mongosh --eval "
use ipop_media_buying
db.getCollectionNames()
"
```

### List All Indexes
```bash
docker exec ipop_mongodb mongosh --eval "
use ipop_media_buying
db.clients.getIndexes()
db.campaigns.getIndexes()
db.performance_metrics.getIndexes()
"
```

### Check Collection Stats
```bash
docker exec ipop_mongodb mongosh --eval "
use ipop_media_buying
db.clients.countDocuments()
db.campaigns.countDocuments()
"
```

---

## 🌐 Connection URLs

### Local Development
```
mongodb://localhost:27017
```

### Docker Compose (from API container)
```
mongodb://mongodb:27017
```

### With Authentication (Production)
```
mongodb://username:password@localhost:27017/ipop_media_buying
```

---

## 🎨 MongoDB Compass Usage

### Connect to Database
1. Open MongoDB Compass
2. Connection: `mongodb://localhost:27017`
3. Click "Connect"
4. Select database: `ipop_media_buying`

### View Collections
- Click on any collection to browse documents
- Use "Documents" tab to see data
- Use "Indexes" tab to see indexes
- Use "Schema" tab to analyze data structure

### Query Data
```javascript
// Find all active campaigns
{ status: "active" }

// Find campaigns by platform
{ platform: "meta" }

// Find recent performance metrics
{ timestamp: { $gte: ISODate("2025-10-01") } }
```

### Create Sample Data
In Compass, select `clients` collection, click "Add Data" → "Insert Document":

```json
{
  "client_id": "client-test-001",
  "company_name": "Test Company",
  "email": "test@example.com",
  "hashed_password": "$2b$12$...",
  "is_active": true,
  "created_at": { "$date": "2025-10-03T00:00:00Z" }
}
```

---

## 🌐 Mongo Express Web UI

Alternative to Compass - browser-based UI:

1. **Start Mongo Express:**
   ```bash
   docker-compose up -d mongo-express
   ```

2. **Access in Browser:**
   ```
   http://localhost:8081
   ```

3. **Login:**
   - Username: `admin`
   - Password: `admin123`

4. **Select Database:**
   - Click on `ipop_media_buying`
   - View/edit collections

---

## 🧪 Test MongoDB Setup

### Test Connection from Python
```bash
cd /Users/gagan/Desktop/gagan_projects/computeruse2/ipop
source venv/bin/activate

python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ipop_media_buying']

    # List collections
    collections = await db.list_collection_names()
    print(f'Collections: {collections}')

    # Count documents
    count = await db.clients.count_documents({})
    print(f'Clients count: {count}')

    client.close()

asyncio.run(test())
"
```

### Test API Connection
```bash
# Start the API
docker-compose up -d api

# Wait for startup
sleep 5

# Test health endpoint
curl http://localhost:8000/health

# Check API can connect to MongoDB
curl http://localhost:8000/api/v1/admin/health
```

---

## 🔧 Troubleshooting

### Docker Not Starting
```bash
# Check Docker Desktop is running
docker info

# If not, start it
open -a Docker
sleep 30
```

### Port 27017 Already in Use
```bash
# Find what's using the port
lsof -i :27017

# Kill the process or stop other MongoDB
brew services stop mongodb-community
```

### Container Not Starting
```bash
# Check logs
docker logs ipop_mongodb

# Restart container
docker restart ipop_mongodb
```

### Can't Connect from Compass
```bash
# Verify MongoDB is listening
docker exec ipop_mongodb mongosh --eval "db.version()"

# Check port mapping
docker port ipop_mongodb
# Should show: 27017/tcp -> 0.0.0.0:27017
```

### Indexes Not Created
```bash
# Manually create indexes
cd /Users/gagan/Desktop/gagan_projects/computeruse2/ipop
python3 -m app.db.create_indexes create

# Verify indexes exist
python3 -m app.db.create_indexes list
```

---

## 📦 Complete Docker Compose Setup

### Start Everything
```bash
docker-compose up -d
```

This starts:
- ✅ MongoDB (port 27017)
- ✅ Redis (port 6379)
- ✅ FastAPI API (port 8000)
- ✅ Mongo Express (port 8081)

### Check All Services
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Just MongoDB
docker-compose logs -f mongodb

# Just API
docker-compose logs -f api
```

### Stop Everything
```bash
docker-compose down
```

### Stop and Remove Data
```bash
docker-compose down -v
```

---

## ✅ Setup Checklist

- [ ] Docker Desktop installed and running
- [ ] MongoDB container started (`docker ps`)
- [ ] MongoDB accessible on port 27017
- [ ] Database `ipop_media_buying` created
- [ ] All 6 collections created
- [ ] All indexes created (run script)
- [ ] MongoDB Compass can connect
- [ ] API can connect to MongoDB
- [ ] Test data can be inserted

---

## 🎉 Success Criteria

You'll know setup is complete when:

1. ✅ `docker ps` shows `ipop_mongodb` running
2. ✅ MongoDB Compass connects to `localhost:27017`
3. ✅ Database `ipop_media_buying` exists with 6 collections
4. ✅ Each collection has proper indexes
5. ✅ API health check returns 200 OK
6. ✅ Can create a test client and campaign

---

**Ready to start the API?**
```bash
docker-compose up -d
open http://localhost:8000/docs
```
