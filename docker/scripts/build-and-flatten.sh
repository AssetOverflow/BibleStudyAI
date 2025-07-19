#!/bin/bash
# Build and Flatten Script for BibleStudyAI
# Creates optimized production images from temporary containers

set -e

echo "🚀 BibleStudyAI - Docker Build & Flatten Process"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEMP_BACKEND_IMAGE="temp-biblestudyai-backend:latest"
TEMP_FRONTEND_IMAGE="temp-biblestudyai-frontend:latest"
PROD_BACKEND_IMAGE="elsquaz/biblestudyai-backend:latest"
PROD_FRONTEND_IMAGE="elsquaz/biblestudyai-frontend:latest"

echo -e "${BLUE}Step 1: Building temporary containers...${NC}"
docker-compose -f docker-compose.temp.yml build --no-cache

echo -e "${BLUE}Step 2: Starting temporary containers...${NC}"
docker-compose -f docker-compose.temp.yml up -d

echo -e "${BLUE}Step 3: Waiting for containers to be ready...${NC}"
sleep 5

echo -e "${BLUE}Step 4: Copying application code into containers...${NC}"

# Copy backend code
echo -e "${YELLOW}  📦 Copying backend code...${NC}"
docker cp ./backend/. temp-backend-container:/app/

# Copy frontend code  
echo -e "${YELLOW}  📦 Copying frontend code...${NC}"
docker cp ./frontend/. temp-frontend-container:/app/

echo -e "${BLUE}Step 5: Flattening containers into production images...${NC}"

# Flatten backend
echo -e "${YELLOW}  🔨 Flattening backend container...${NC}"
docker commit temp-backend-container $PROD_BACKEND_IMAGE

# Flatten frontend
echo -e "${YELLOW}  🔨 Flattening frontend container...${NC}"
docker commit temp-frontend-container $PROD_FRONTEND_IMAGE

echo -e "${BLUE}Step 6: Cleaning up temporary containers...${NC}"
docker-compose -f docker-compose.temp.yml down
docker rmi $TEMP_BACKEND_IMAGE $TEMP_FRONTEND_IMAGE || true

echo -e "${GREEN}✅ Build complete!${NC}"
echo -e "${GREEN}📦 Production images created:${NC}"
echo -e "   • ${PROD_BACKEND_IMAGE}"
echo -e "   • ${PROD_FRONTEND_IMAGE}"

echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Test images: ${YELLOW}docker run -p 8000:8000 ${PROD_BACKEND_IMAGE}${NC}"
echo -e "2. Push to registry: ${YELLOW}docker push ${PROD_BACKEND_IMAGE}${NC}"
echo -e "3. Push to registry: ${YELLOW}docker push ${PROD_FRONTEND_IMAGE}${NC}"

echo -e "\n🎉 Ready for production deployment!"
