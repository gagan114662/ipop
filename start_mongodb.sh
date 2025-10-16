#!/bin/bash
# Start MongoDB Server for Resize Backend

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MONGODB_DATA_PATH="$SCRIPT_DIR/mongodb_data"
MONGODB_BIN="/Users/gaganarora/Downloads/mongodb-macos-aarch64--8.2.1/bin/mongod"

echo "🚀 Starting MongoDB..."
echo "📂 Data path: $MONGODB_DATA_PATH"
echo ""

# Create data directory if it doesn't exist
mkdir -p "$MONGODB_DATA_PATH"

# Start MongoDB
"$MONGODB_BIN" --dbpath "$MONGODB_DATA_PATH" --port 27017

echo ""
echo "⚠️  MongoDB stopped"
