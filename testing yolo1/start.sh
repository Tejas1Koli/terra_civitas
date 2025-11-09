#!/bin/bash

# CCTV Crime Detection System - Start Script
# Version 2.0
# Purpose: Easy startup for the Streamlit web application

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   CCTV Crime Detection System v2.0                         ║"
echo "║   Starting Application...                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if normal.onnx exists
if [ ! -f "normal.onnx" ]; then
    echo -e "${RED}❌ Error: normal.onnx model file not found!${NC}"
    echo -e "${YELLOW}Please ensure normal.onnx is in: $SCRIPT_DIR${NC}"
    exit 1
fi

# Check if cctv_app_analytics.py exists
if [ ! -f "cctv_app_analytics.py" ]; then
    echo -e "${RED}❌ Error: cctv_app_analytics.py not found!${NC}"
    echo -e "${YELLOW}Please ensure cctv_app_analytics.py is in: $SCRIPT_DIR${NC}"
    exit 1
fi

# Check if cctv_detector.py exists
if [ ! -f "cctv_detector.py" ]; then
    echo -e "${RED}❌ Error: cctv_detector.py not found!${NC}"
    echo -e "${YELLOW}Please ensure cctv_detector.py is in: $SCRIPT_DIR${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "yolo/bin" ]; then
    echo -e "${RED}❌ Error: Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please ensure 'yolo' virtual environment exists in: $SCRIPT_DIR${NC}"
    exit 1
fi

# Get Python executable from venv
PYTHON_EXEC="$SCRIPT_DIR/yolo/bin/python"

echo -e "${GREEN}✅ All required files found${NC}"
echo -e "${BLUE}📊 Starting Streamlit application...${NC}"
echo ""

# Kill any existing Streamlit processes
echo -e "${YELLOW}🧹 Cleaning up any existing Streamlit processes...${NC}"
pkill -9 -f streamlit 2>/dev/null || true
sleep 1

# Display startup info
PYTHON_VERSION=$("$PYTHON_EXEC" --version 2>&1)
MODEL_SIZE=$(ls -lh normal.onnx | awk '{print $5}')
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ System Status:${NC}"
echo -e "${GREEN}   • Python: $PYTHON_VERSION${NC}"
echo -e "${GREEN}   • Location: $SCRIPT_DIR${NC}"
echo -e "${GREEN}   • Model: normal.onnx ($MODEL_SIZE)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Launch Streamlit app
echo -e "${BLUE}🚀 Launching application...${NC}"
echo -e "${YELLOW}⏳ The app will open in your browser shortly${NC}"
echo ""

# Run Streamlit with error logging disabled for cleaner output
"$PYTHON_EXEC" -m streamlit run cctv_app_analytics.py --logger.level=error

# If we get here, the app was stopped
echo ""
echo -e "${YELLOW}ℹ️  Application stopped${NC}"
