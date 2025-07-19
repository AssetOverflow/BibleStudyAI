#!/bin/bash
# Build Optimization Script
# Creates cached base images for ultra-fast development builds

set -e

echo "🚀 Building Optimized Docker Images for BibleStudyAI"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running ✅"

# Build backend base image (dependencies only)
print_status "Building backend base image with dependencies..."
cd backend
docker build -f Dockerfile.optimized -t biblestudyai-backend-base:latest --target builder . || {
    print_error "Failed to build backend base image"
    exit 1
}
print_success "Backend base image built successfully"

# Build frontend base image (dependencies only)  
print_status "Building frontend base image with dependencies..."
cd ../frontend
docker build -f Dockerfile.optimized -t biblestudyai-frontend-base:latest --target builder . || {
    print_error "Failed to build frontend base image"
    exit 1
}
print_success "Frontend base image built successfully"

cd ..

# Build full optimized images
print_status "Building full optimized application images..."
docker-compose -f docker-compose.optimized.yml build --parallel || {
    print_error "Failed to build optimized images"
    exit 1
}
print_success "Optimized application images built successfully"

# Clean up dangling images
print_status "Cleaning up dangling images..."
docker image prune -f

print_success "🎉 Build optimization complete!"
echo ""
echo "📊 Image Summary:"
docker images | grep biblestudyai
echo ""
echo "🚀 To start the optimized stack:"
echo "   docker-compose -f docker-compose.optimized.yml up -d"
echo ""
echo "⚡ For lightning-fast rebuilds (dependencies cached):"
echo "   docker-compose -f docker-compose.optimized.yml build --no-cache fastapi-backend"
echo "   docker-compose -f docker-compose.optimized.yml build --no-cache react-frontend"
echo ""
print_success "Ready for ultra-fast development! 🔥"
