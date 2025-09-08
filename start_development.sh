#!/bin/bash

# EquityScope v2-Optimized Development Startup Script

echo "🚀 Starting EquityScope v2-Optimized Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "start_development.sh" ]; then
    echo -e "${RED}❌ Please run this script from the v2-optimized root directory${NC}"
    exit 1
fi

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
        return 1
    else
        return 0
    fi
}

# Create necessary directories
echo -e "${BLUE}📂 Creating directories...${NC}"
mkdir -p backend/data/users
mkdir -p backend/cache
mkdir -p backend/logs

# Initialize empty JSON files for file-based storage
echo -e "${BLUE}📄 Initializing data files...${NC}"
echo "[]" > backend/data/users/users.json
echo "[]" > backend/data/users/sessions.json  
echo "[]" > backend/data/users/api_keys.json

echo -e "${GREEN}✅ Data files initialized${NC}"

# Check ports
echo -e "${BLUE}🔍 Checking ports...${NC}"
if ! check_port 8000; then
    echo -e "${RED}❌ Backend port 8000 is in use. Please free it or change the port.${NC}"
    exit 1
fi

if ! check_port 3000; then
    echo -e "${YELLOW}⚠️  Frontend port 3000 is in use. React will try to use the next available port.${NC}"
fi

# Start backend
echo -e "${BLUE}🔧 Starting Backend Server...${NC}"
cd backend

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install -r requirements.txt > /dev/null 2>&1

# Start backend server in background
echo -e "${GREEN}🚀 Starting FastAPI server on http://localhost:8000${NC}"
python start_server.py &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${BLUE}⏳ Waiting for backend to start...${NC}"
sleep 5

# Check if backend started successfully
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend server started successfully${NC}"
else
    echo -e "${RED}❌ Backend server failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo -e "${BLUE}🎨 Starting Frontend Development Server...${NC}"
cd ../frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    npm install
fi

# Start frontend server
echo -e "${GREEN}🚀 Starting React development server...${NC}"
npm start &
FRONTEND_PID=$!

# Store PIDs for cleanup
echo $BACKEND_PID > ../backend_pid.txt
echo $FRONTEND_PID > ../frontend_pid.txt

echo ""
echo -e "${GREEN}🎉 EquityScope v2-Optimized is now running!${NC}"
echo ""
echo -e "${BLUE}📍 URLs:${NC}"
echo -e "   Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   Health:   ${GREEN}http://localhost:8000/health${NC}"
echo ""
echo -e "${BLUE}📊 Data Storage:${NC}"
echo -e "   User Data: ${YELLOW}backend/data/users/${NC}"
echo -e "   Cache:     ${YELLOW}backend/cache/${NC}"
echo -e "   Logs:      ${YELLOW}backend/logs/${NC}"
echo ""
echo -e "${BLUE}🔧 Demo Mode:${NC}"
echo -e "   Pre-built analyses for: ${GREEN}TCS, Reliance, HDFC Bank${NC}"
echo ""
echo -e "${YELLOW}💡 To stop servers, run: ./stop_development.sh${NC}"
echo -e "${YELLOW}💡 Or press Ctrl+C to stop this script${NC}"

# Keep script running and handle cleanup
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    
    if [ -f backend_pid.txt ]; then
        BACKEND_PID=$(cat backend_pid.txt)
        kill $BACKEND_PID 2>/dev/null
        rm backend_pid.txt
    fi
    
    if [ -f frontend_pid.txt ]; then    
        FRONTEND_PID=$(cat frontend_pid.txt)
        kill $FRONTEND_PID 2>/dev/null
        rm frontend_pid.txt
    fi
    
    echo -e "${GREEN}✅ Servers stopped successfully${NC}"
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait