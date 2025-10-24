#!/bin/bash
# PaiiD Developer Environment Setup Script
# One-command setup for new developers
#
# Usage: ./scripts/setup-dev-env.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "============================================================"
echo -e "${CYAN}🚀 PaiiD Developer Environment Setup${NC}"
echo "============================================================"
echo ""

# Check if running from project root
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    echo "   cd /path/to/PaiiD && ./scripts/setup-dev-env.sh"
    exit 1
fi

# Step 1: Check prerequisites
echo -e "${BLUE}📋 Step 1/7: Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 20+${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js ${NODE_VERSION}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓${NC} npm ${NPM_VERSION}"

# Check git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ git not found. Please install git${NC}"
    exit 1
fi
GIT_VERSION=$(git --version | awk '{print $3}')
echo -e "${GREEN}✓${NC} git ${GIT_VERSION}"

echo ""

# Step 2: Backend setup
echo -e "${BLUE}🐍 Step 2/7: Setting up backend...${NC}"

cd backend

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠${NC}  No .env file found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓${NC} Created .env from template"
        echo -e "${YELLOW}⚠${NC}  ${YELLOW}ACTION REQUIRED:${NC} Edit backend/.env and add your API keys"
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓${NC} pip upgraded"

# Install dependencies
echo -e "${BLUE}Installing backend dependencies...${NC}"
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Backend dependencies installed"

# Install dev dependencies
if [ -f requirements-dev.txt ]; then
    echo -e "${BLUE}Installing dev dependencies...${NC}"
    pip install -r requirements-dev.txt > /dev/null 2>&1
    echo -e "${GREEN}✓${NC} Dev dependencies installed"
fi

cd ..
echo ""

# Step 3: Frontend setup
echo -e "${BLUE}⚛️  Step 3/7: Setting up frontend...${NC}"

cd frontend

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo -e "${YELLOW}⚠${NC}  No .env.local file found"
    echo "NEXT_PUBLIC_API_TOKEN=rnd_bDRqi1TvLvd3rC78yvUSgDraH2Kl" > .env.local
    echo "NEXT_PUBLIC_BACKEND_API_BASE_URL=http://127.0.0.1:8001" >> .env.local
    echo -e "${GREEN}✓${NC} Created .env.local with defaults"
else
    echo -e "${GREEN}✓${NC} .env.local file exists"
fi

# Install dependencies
echo -e "${BLUE}Installing frontend dependencies...${NC}"
npm ci > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Frontend dependencies installed"

cd ..
echo ""

# Step 4: Setup PyPI mirror
echo -e "${BLUE}🔒 Step 4/7: Setting up internal PyPI mirror...${NC}"

cd backend/pypi-mirror

if [ ! -d "simple" ] || [ -z "$(ls -A simple 2>/dev/null)" ]; then
    echo -e "${BLUE}Populating mirror...${NC}"
    chmod +x scripts/download-packages.sh
    ./scripts/download-packages.sh | grep -E "(✓|✅|📊|Summary)" || true
    echo -e "${GREEN}✓${NC} Mirror populated"
else
    echo -e "${GREEN}✓${NC} Mirror already populated"
fi

# Make scripts executable
chmod +x scripts/*.sh scripts/*.py activate-mirror.sh

cd ../..
echo ""

# Step 5: Git configuration
echo -e "${BLUE}🔧 Step 5/7: Configuring git hooks...${NC}"

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${GREEN}✓${NC} Current branch: ${CURRENT_BRANCH}"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠${NC}  You have uncommitted changes"
fi

echo ""

# Step 6: Verify installation
echo -e "${BLUE}✅ Step 6/7: Verifying installation...${NC}"

# Test backend
cd backend
source venv/bin/activate
if python -c "import fastapi" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backend imports working"
else
    echo -e "${RED}❌ Backend imports failed${NC}"
fi
cd ..

# Test frontend
cd frontend
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓${NC} Frontend node_modules exists"
else
    echo -e "${RED}❌ Frontend node_modules missing${NC}"
fi
cd ..

# Test mirror
if [ -f "backend/pypi-mirror/scripts/verify-mirror.sh" ]; then
    echo -e "${GREEN}✓${NC} Mirror scripts available"
else
    echo -e "${RED}❌ Mirror scripts missing${NC}"
fi

echo ""

# Step 7: Summary and next steps
echo "============================================================"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "============================================================"
echo ""
echo -e "${CYAN}Backend:${NC}"
echo "  • Virtual environment: backend/venv/"
echo "  • Configuration: backend/.env ${YELLOW}(ADD YOUR API KEYS!)${NC}"
echo "  • Start server: cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8001"
echo ""
echo -e "${CYAN}Frontend:${NC}"
echo "  • Configuration: frontend/.env.local"
echo "  • Start dev server: cd frontend && npm run dev"
echo ""
echo -e "${CYAN}PyPI Mirror:${NC}"
echo "  • Location: backend/pypi-mirror/"
echo "  • Start server: cd backend/pypi-mirror && python scripts/serve-mirror.py"
echo "  • Run audit: cd backend/pypi-mirror && ./scripts/quick-audit.sh"
echo ""
echo -e "${CYAN}Documentation:${NC}"
echo "  • Main README: README.md"
echo "  • Backend guide: backend/README_BACKEND.md"
echo "  • Mirror docs: backend/pypi-mirror/README.md"
echo "  • Contributing: CONTRIBUTING.md"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Next Steps${NC}"
echo "1. Edit backend/.env and add your API keys:"
echo "   - ALPACA_PAPER_API_KEY"
echo "   - ALPACA_PAPER_SECRET_KEY"
echo "   - TRADIER_API_KEY"
echo "   - TRADIER_ACCOUNT_ID"
echo "   - ANTHROPIC_API_KEY"
echo ""
echo "2. Start the backend:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8001"
echo ""
echo "3. In another terminal, start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo "============================================================"
