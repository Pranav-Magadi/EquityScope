#!/bin/bash

# EquityScope v2-Optimized Health Check Script

echo "🩺 EquityScope v2-Optimized Health Check"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if servers are running
echo -e "${BLUE}🔍 Checking Server Status...${NC}"

# Check backend (port 8000)
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend Server: Running on http://localhost:8000${NC}"
    BACKEND_STATUS="✅ UP"
else  
    echo -e "${RED}❌ Backend Server: Not running or unreachable${NC}"
    BACKEND_STATUS="❌ DOWN"
fi

# Check frontend (port 3000)
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✅ Frontend Server: Running on http://localhost:3000${NC}"
    FRONTEND_STATUS="✅ UP"
else
    echo -e "${RED}❌ Frontend Server: Not running or unreachable${NC}"
    FRONTEND_STATUS="❌ DOWN"
fi

echo ""
echo -e "${BLUE}🔗 Testing API Endpoints...${NC}"

# Test health endpoint
if curl -s http://localhost:8000/health | grep -q "healthy\|ok"; then
    echo -e "${GREEN}✅ Health Endpoint: /health${NC}"
else
    echo -e "${RED}❌ Health Endpoint: Failed${NC}"
fi

# Test demo analyses endpoint
if curl -s http://localhost:8000/api/v2/demo-analyses > /dev/null; then
    echo -e "${GREEN}✅ Demo Analyses: /api/v2/demo-analyses${NC}"
else
    echo -e "${RED}❌ Demo Analyses: Failed${NC}"
fi

# Test subscription plans endpoint
if curl -s http://localhost:8000/api/v2/subscription-plans > /dev/null; then
    echo -e "${GREEN}✅ Subscription Plans: /api/v2/subscription-plans${NC}"
else
    echo -e "${RED}❌ Subscription Plans: Failed${NC}"
fi

# Test demo analysis for TCS
if curl -s http://localhost:8000/api/v2/demo-analyses/TCS.NS > /dev/null; then
    echo -e "${GREEN}✅ TCS Demo Analysis: /api/v2/demo-analyses/TCS.NS${NC}"
else
    echo -e "${RED}❌ TCS Demo Analysis: Failed${NC}"
fi

echo ""
echo -e "${BLUE}📂 Checking Data Directories...${NC}"

# Check data directories
if [ -d "backend/data/users" ]; then
    echo -e "${GREEN}✅ User Data Directory: backend/data/users/${NC}"
else
    echo -e "${RED}❌ User Data Directory: Missing${NC}"
fi

if [ -d "backend/cache" ]; then
    echo -e "${GREEN}✅ Cache Directory: backend/cache/${NC}"
else
    echo -e "${RED}❌ Cache Directory: Missing${NC}"
fi

if [ -d "backend/logs" ]; then
    echo -e "${GREEN}✅ Logs Directory: backend/logs/${NC}"
else
    echo -e "${RED}❌ Logs Directory: Missing${NC}"
fi

# Check data files
if [ -f "backend/data/users/users.json" ]; then
    echo -e "${GREEN}✅ Users Database: backend/data/users/users.json${NC}"
else
    echo -e "${RED}❌ Users Database: Missing${NC}"
fi

echo ""
echo -e "${BLUE}📊 System Summary${NC}"
echo "==================="
echo -e "Backend:  $BACKEND_STATUS"
echo -e "Frontend: $FRONTEND_STATUS"
echo -e "Data Dir: $([ -d "backend/data" ] && echo "✅ OK" || echo "❌ Missing")"
echo -e "Config:   $([ -f ".env" ] && echo "✅ OK" || echo "❌ Missing")"

echo ""
if [[ "$BACKEND_STATUS" == *"UP"* ]] && [[ "$FRONTEND_STATUS" == *"UP"* ]]; then
    echo -e "${GREEN}🎉 EquityScope v2-Optimized is healthy and ready for testing!${NC}"
    echo ""
    echo -e "${BLUE}🚀 Quick Test Links:${NC}"
    echo -e "   Frontend:     ${GREEN}http://localhost:3000${NC}"
    echo -e "   API Health:   ${GREEN}http://localhost:8000/health${NC}"
    echo -e "   API Docs:     ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "   Demo Mode:    ${GREEN}http://localhost:3000 → Try TCS Demo${NC}"
    echo ""
    echo -e "${YELLOW}💡 Start testing with the demo analyses for TCS, Reliance, or HDFC Bank${NC}"
else
    echo -e "${RED}⚠️  Some services are not running. Please start the development environment first.${NC}"
    echo -e "${YELLOW}💡 Run: ./start_development.sh${NC}"
fi

echo ""