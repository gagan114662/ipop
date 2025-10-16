#!/bin/bash
# Start Resize Backend Application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$SCRIPT_DIR"

echo "🚀 Starting Resize Backend Application..."
echo "📂 Working directory: $SCRIPT_DIR"
echo ""

# Check if MongoDB is running
if ! lsof -i :27017 > /dev/null 2>&1; then
    echo "⚠️  WARNING: MongoDB doesn't appear to be running on port 27017"
    echo "   Please start MongoDB first using: ./start_mongodb.sh"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the application
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "⚠️  Application stopped"
