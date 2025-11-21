#!/bin/bash

# CCTV Crime Detection System v5.0 - React + FastAPI
# Starts FastAPI backend (8000) and React Vite frontend (5173)
# Features: YOLO detection, real-time alerts, live video feed, authentication

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   CCTV Crime Detection System v5.0 (React + FastAPI)        ║"
echo "║   Real-Time Detection • Live Alerts • Modern Dashboard      ║"
echo "║   Starting Services...                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Validate core files and directories
for file in normal.onnx auth_manager.py cctv_detector.py alert_logger.py; do
  if [ ! -f "$file" ]; then
    echo -e "${RED}❌ Error: $file not found!${NC}"
    exit 1
  fi
done

for dir in yolo backend frontend; do
  if [ ! -d "$dir" ]; then
    echo -e "${RED}❌ Error: $dir directory not found!${NC}"
    exit 1
  fi
done

PYTHON_EXEC="$SCRIPT_DIR/yolo/bin/python"
PYTHON_VERSION=$("$PYTHON_EXEC" --version 2>&1)
MODEL_SIZE=$(ls -lh normal.onnx | awk '{print $5}')

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ System Status:${NC}"
echo -e "${GREEN}   • Python: $PYTHON_VERSION${NC}"
echo -e "${GREEN}   • Location: $SCRIPT_DIR${NC}"
echo -e "${GREEN}   • Model: normal.onnx ($MODEL_SIZE)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}🧹 Cleaning up any existing processes...${NC}"
pkill -9 -f "uvicorn|npm.*dev" 2>/dev/null || true
sleep 1

echo -e "${BLUE}🚀 Starting Backend API Server (FastAPI on port 8000)...${NC}"
"$PYTHON_EXEC" -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
  echo -e "${RED}❌ Backend failed to start!${NC}"
  exit 1
fi

echo ""
echo -e "${BLUE}🚀 Starting Frontend React Server (Vite on port 5173)...${NC}"
cd frontend
npm install --legacy-peer-deps > /dev/null 2>&1 || true
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
cd ..

sleep 3

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 All services running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}📍 Service URLs:${NC}"
echo -e "   ${BLUE}🌐 Frontend Dashboard:${NC}  http://localhost:5173"
echo -e "   ${BLUE}⚙️  Backend API:${NC}           http://localhost:8000"
echo -e "   ${BLUE}📚 API Documentation:${NC}    http://localhost:8000/docs"
echo ""
echo -e "${CYAN}🔐 Demo Credentials:${NC}"
echo "   Username: ${YELLOW}admin${NC}"
echo "   Password: ${YELLOW}admin123${NC}"
echo ""
echo -e "${CYAN}✨ Quick Start:${NC}"
echo "   1. Open ${YELLOW}http://localhost:5173${NC} in your browser"
echo "   2. Log in with admin / admin123"
echo "   3. Click ${YELLOW}'Start Detection'${NC} to begin live monitoring"
echo "   4. Watch real-time alerts appear in the dashboard"
echo ""
echo -e "${YELLOW}✋ To stop services, press Ctrl+C${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true

echo -e "${YELLOW}ℹ️  Services stopped${NC}"
