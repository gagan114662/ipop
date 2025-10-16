#!/bin/bash
# Start both MongoDB and Application in the background

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MONGODB_DATA_PATH="$SCRIPT_DIR/mongodb_data"
MONGODB_BIN="/Users/gaganarora/Downloads/mongodb-macos-aarch64--8.2.1/bin/mongod"

echo "🚀 Starting Resize Backend System..."
echo "=================================="
echo ""

# Create data directory if it doesn't exist
mkdir -p "$MONGODB_DATA_PATH"

# Check if MongoDB is already running
if lsof -i :27017 > /dev/null 2>&1; then
    echo "✅ MongoDB is already running on port 27017"
else
    echo "📂 Starting MongoDB..."
    echo "   Data path: $MONGODB_DATA_PATH"
    "$MONGODB_BIN" --dbpath "$MONGODB_DATA_PATH" --port 27017 --fork --logpath "$MONGODB_DATA_PATH/mongod.log"
    sleep 2
    if lsof -i :27017 > /dev/null 2>&1; then
        echo "✅ MongoDB started successfully"
    else
        echo "❌ Failed to start MongoDB"
        exit 1
    fi
fi

echo ""

# Check if application is already running
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use"
    echo "   Starting on port 8001 instead..."
    APP_PORT=8001
else
    APP_PORT=8000
fi

# Start the application
cd "$SCRIPT_DIR"
echo "🚀 Starting application on port $APP_PORT..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT --reload &
APP_PID=$!

sleep 3

if kill -0 $APP_PID 2>/dev/null; then
    echo "✅ Application started successfully"
    echo ""
    echo "=================================="
    echo "📊 System Status:"
    echo "=================================="
    echo "✅ MongoDB:     Running on port 27017"
    echo "✅ Application: Running on port $APP_PORT"
    echo "✅ Database:    creative_resizer"
    echo "✅ Data folder: $MONGODB_DATA_PATH"
    echo ""
    echo "🌐 Access points:"
    echo "   • API Docs:  http://localhost:$APP_PORT/docs"
    echo "   • Health:    http://localhost:$APP_PORT/health"
    echo "   • Platforms: http://localhost:$APP_PORT/api/v1/platforms"
    echo ""
    echo "📝 Logs:"
    echo "   • MongoDB: $MONGODB_DATA_PATH/mongod.log"
    echo ""
    echo "⏹  To stop: Press Ctrl+C"
    echo "=================================="

    # Wait for the app to finish
    wait $APP_PID
else
    echo "❌ Failed to start application"
    exit 1
fi
