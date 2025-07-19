#!/bin/bash
# Quick Development Test Script
# Tests the temporary containers before flattening

set -e

echo "🧪 Testing Temporary Containers"
echo "==============================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Building and starting temporary containers...${NC}"
docker-compose -f docker-compose.temp.yml up --build -d

echo -e "${BLUE}Waiting for containers to be ready...${NC}"
sleep 5

echo -e "${YELLOW}Testing backend container...${NC}"
if docker exec temp-backend-container python --version; then
    echo -e "${GREEN}✅ Backend Python working${NC}"
else
    echo -e "❌ Backend Python failed"
fi

if docker exec temp-backend-container pip list | grep fastapi; then
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
else
    echo -e "❌ Backend dependencies missing"
fi

echo -e "${YELLOW}Testing frontend container...${NC}"
if docker exec temp-frontend-container node --version; then
    echo -e "${GREEN}✅ Frontend Node.js working${NC}"
else
    echo -e "❌ Frontend Node.js failed"
fi

if docker exec temp-frontend-container npm list --depth=0 | grep vite; then
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
else
    echo -e "❌ Frontend dependencies missing"
fi

echo -e "\n${BLUE}Container sizes:${NC}"
docker images | grep temp-biblestudyai

echo -e "\n${YELLOW}Stopping temporary containers...${NC}"
docker-compose -f docker-compose.temp.yml down

echo -e "\n${GREEN}🎉 Test complete! Ready to flatten containers.${NC}"
echo -e "${BLUE}Next step: Run ${YELLOW}./build-and-flatten.sh${NC}"
