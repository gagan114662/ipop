#!/bin/bash

# MongoDB Setup Script for IPOP Media Buying System
# This script sets up MongoDB with all required collections and indexes

set -e

echo "🔧 MongoDB Setup for IPOP Media Buying System"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running${NC}"
        echo "Please start Docker Desktop and try again"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Docker is running"
}

# Start MongoDB via Docker Compose
start_mongodb() {
    echo ""
    echo "📦 Starting MongoDB with Docker Compose..."

    cd /Users/gagan/Desktop/gagan_projects/computeruse2/ipop

    # Start only MongoDB and Redis (not the API yet)
    docker-compose up -d mongodb redis

    echo -e "${GREEN}✓${NC} MongoDB container started"
    echo ""
    echo "Waiting for MongoDB to be ready..."
    sleep 5

    # Wait for MongoDB to be ready
    for i in {1..30}; do
        if docker exec ipop_mongodb mongosh --eval "db.version()" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} MongoDB is ready!"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
}

# Create database and collections
setup_database() {
    echo ""
    echo "🗄️  Setting up database and collections..."

    docker exec ipop_mongodb mongosh <<EOF
use ipop_media_buying

// Create collections
db.createCollection("clients")
db.createCollection("skus")
db.createCollection("campaigns")
db.createCollection("performance_metrics")
db.createCollection("intelligence_decisions")
db.createCollection("system_benchmarks")

print("✓ Collections created")
EOF

    echo -e "${GREEN}✓${NC} Database and collections created"
}

# Create indexes using the project's script
create_indexes() {
    echo ""
    echo "📑 Creating database indexes..."

    cd /Users/gagan/Desktop/gagan_projects/computeruse2/ipop

    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # Run the index creation script
    python3 -m app.db.create_indexes create

    echo -e "${GREEN}✓${NC} All indexes created"
}

# Verify setup
verify_setup() {
    echo ""
    echo "🔍 Verifying MongoDB setup..."

    docker exec ipop_mongodb mongosh --eval "
    use ipop_media_buying
    print('Database: ' + db.getName())
    print('Collections:')
    db.getCollectionNames().forEach(function(c) { print('  - ' + c) })
    print('')
    print('Indexes:')
    db.clients.getIndexes().forEach(function(idx) { print('  clients.' + idx.name) })
    db.campaigns.getIndexes().forEach(function(idx) { print('  campaigns.' + idx.name) })
    " 2>/dev/null | grep -v "Current Mongosh"

    echo ""
    echo -e "${GREEN}✓${NC} MongoDB setup verified!"
}

# Display connection info
show_connection_info() {
    echo ""
    echo "📊 MongoDB Connection Information"
    echo "================================="
    echo ""
    echo "MongoDB URL: mongodb://localhost:27017"
    echo "Database Name: ipop_media_buying"
    echo ""
    echo "Collections created:"
    echo "  • clients - User/client accounts"
    echo "  • skus - Product/SKU management"
    echo "  • campaigns - Ad campaigns"
    echo "  • performance_metrics - Campaign performance data"
    echo "  • intelligence_decisions - AI optimization decisions"
    echo "  • system_benchmarks - Industry benchmarks"
    echo ""
    echo "MongoDB Compass Connection:"
    echo "  Open MongoDB Compass"
    echo "  Connection String: mongodb://localhost:27017"
    echo "  Database: ipop_media_buying"
    echo ""
    echo "Mongo Express Web UI:"
    echo "  URL: http://localhost:8081"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
}

# Main execution
main() {
    echo "Step 1: Checking Docker..."
    check_docker

    echo ""
    echo "Step 2: Starting MongoDB..."
    start_mongodb

    echo ""
    echo "Step 3: Creating database and collections..."
    setup_database

    echo ""
    echo "Step 4: Creating indexes..."
    create_indexes

    echo ""
    echo "Step 5: Verifying setup..."
    verify_setup

    show_connection_info

    echo ""
    echo -e "${GREEN}🎉 MongoDB setup complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start the API: docker-compose up -d api"
    echo "  2. Access API docs: http://localhost:8000/docs"
    echo "  3. Connect MongoDB Compass to: mongodb://localhost:27017"
    echo ""
}

# Run main function
main
