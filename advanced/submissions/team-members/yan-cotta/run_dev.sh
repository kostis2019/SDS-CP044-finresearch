#!/bin/bash
# =============================================================================
# FinResearch AI - Development Server Runner
# Starts both FastAPI backend and Vite frontend dev server
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         FinResearch AI - Development Server                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for .env file
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}[WARNING] No .env file found. Create one with OPENAI_API_KEY.${NC}"
fi

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# Check if node_modules exists for frontend
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd "$FRONTEND_DIR"
    npm install
    cd "$PROJECT_DIR"
fi

# Start backend server
echo -e "${GREEN}Starting FastAPI backend on http://localhost:8000${NC}"
cd "$PROJECT_DIR"
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Give backend time to start
sleep 2

# Start frontend dev server
echo -e "${GREEN}Starting Vite frontend on http://localhost:5173${NC}"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Development servers running!                                ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  Frontend:  http://localhost:5173                            ║${NC}"
echo -e "${GREEN}║  Backend:   http://localhost:8000                            ║${NC}"
echo -e "${GREEN}║  API Docs:  http://localhost:8000/api/docs                   ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  Press Ctrl+C to stop all servers                            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID
