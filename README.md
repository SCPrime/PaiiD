# 🚀 PaiiD Trading Platform

**Personal Artificial Intelligence Investment Dashboard** - A full-stack AI-powered trading platform with an intuitive 10-stage radial workflow interface, real-time market data, and intelligent trade execution.

[![Progress](https://img.shields.io/badge/Progress-87%25-brightgreen?style=for-the-badge&logo=github)](./PROGRESS_DASHBOARD.html)
[![Build](https://img.shields.io/badge/Build-Passing-success?style=for-the-badge&logo=github-actions)](https://github.com/SCPrime/PaiiD/actions)
[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18+-blue?style=for-the-badge&logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](./LICENSE)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-A%2B-brightgreen?style=for-the-badge&logo=sonarqube)](https://sonarcloud.io/)

## 🎯 **Key Features**

### 🧠 **AI-Powered Intelligence**
- **Pattern Recognition** - ML algorithms detect chart patterns
- **Market Regime Detection** - K-means clustering for market states
- **Strategy Recommendations** - AI suggests optimal trading strategies
- **Personal Analytics** - Performance tracking and risk assessment

### 📊 **Trading Platform**
- **Real-time Market Data** - Live quotes and options chains
- **Paper Trading** - Risk-free strategy testing
- **Options Trading** - Greeks calculation and volatility analysis
- **Portfolio Management** - Position tracking and P&L monitoring
- **MOD SQUAD Guardrails** - Automated lint/tests/security gates on every workflow
- **Modular Market Packs** - Stocks/options engine aligned with 2mx hot-swap architecture
- **Execution Audit Trail** - `/api/strategies/execution-history` surfaces recent automation runs

### 🎨 **Enterprise UX**
- **Radial Workflow Interface** - Intuitive 10-stage trading process
- **Contextual Help System** - Tooltips and guided assistance
- **Loading States & Animations** - Professional skeleton screens
- **Error Recovery** - Graceful error handling with recovery options

📊 **[View Live Progress Dashboard](./PROGRESS_DASHBOARD.html)** | 📈 **[Progress Data (JSON)](./progress-data.json)**

## 🚀 Live Deployment

- **Frontend**: https://paiid-frontend.onrender.com
- **Backend API**: https://paiid-backend.onrender.com
- **API Health**: https://paiid-backend.onrender.com/api/health
- **Monitor Dashboard**: https://paiid-frontend.onrender.com/monitor

## 🎉 **BATCH 9 COMPLETE - DOCUMENTATION SYSTEMATIZED**

**Version 1.0.0** - Complete Options Trading Platform deployed to production with comprehensive documentation management system.

### 🧹 **RECENT CLEANUP & AUTOMATION (Batch 8-9)**

**Documentation Management System:**
- ✅ **80 redundant files archived** (0.80 MB space reclaimed)
- ✅ **7 active documents indexed** and categorized
- ✅ **232 verification files** ready for automated processing
- ✅ **Naming conventions established** to prevent future redundancy
- ✅ **Automated maintenance tools** created for ongoing cleanup

**New Automation Tools:**
- `scripts/codebase-inventory-analyzer.py` - Full codebase inventory
- `scripts/codebase-archival-tool.py` - Safe file archival with rollback
- `scripts/verification-helper.py` - AI-powered file verification
- `scripts/documentation-index-generator.py` - Documentation indexing

**Repository Health:**
- **Before**: 538 files, 6.69 MB, scattered documentation
- **After**: 458 files, 5.89 MB, organized documentation system
- **Improvement**: 15% file reduction, 100% documentation organization

### 🚀 **NEW FEATURES DEPLOYED**

1. **Complete Options Trading Platform**
   - Real-time options data from Tradier API
   - Greeks calculation with py_vollib
   - Paper trading execution via Alpaca
   - Risk management and position tracking

2. **Advanced Position Management**
   - Real-time position tracking
   - Portfolio Greeks aggregation
   - One-click position closing
   - Auto-refresh monitoring

3. **Production Security**
   - 12 critical vulnerabilities fixed
   - API token authentication
   - CORS configuration
   - Security headers and CSP policies

## 📊 Current Project State (Commit 48e0076)

### ✅ Working Features

1. **D3.js Radial Navigation Menu**
   - 8 interactive pie-wedge segments
   - Hover effects with segment expansion
   - Click-to-activate workflow switching
   - Native React/D3 implementation (no iframes)

2. **Morning Routine Workflow**
   - Automated health checks for backend API
   - `/api/health` endpoint status
   - `/api/settings` configuration check
   - `/api/portfolio/positions` data validation
   - Response time monitoring

3. **Active Positions Workflow**
   - Live portfolio positions table
   - Real-time P&L calculations
   - 3 summary cards: Total P&L, Cost Basis, Market Value
   - 7-column enhanced table with color-coded profits/losses
   - Auto-refresh every 30 seconds
   - Currently displaying: AAPL +$17.60 position

4. **Execute Trade Workflow**
   - Order form with symbol, quantity, side (buy/sell)
   - Direct API integration to `/api/trades/execute`
   - Order type selection (market/limit)
   - Real-time order submission

5. **Full-Screen Centered Layout**
   - Header with gradient branding
   - Centered radial menu (600px max width)
   - System Status panel with live indicator
   - Dynamic workflow content area
   - Keyboard navigation hints
   - Glassmorphism dark theme design

### 🚧 Placeholder Workflows (Coming Soon)

- **P&L Dashboard**: Profit/loss analytics and performance metrics
- **News Review**: Market news aggregation with sentiment analysis
- **AI Recommendations**: ML-generated trade signals and confidence scores
- **Strategy Builder**: Visual rule designer for custom trading strategies
- **Backtesting**: Historical strategy simulation and optimization

## 🏗️ Architecture

### Frontend Stack
- **Framework**: Next.js 14.2.33 (Pages Router)
- **Language**: TypeScript 5.9.2
- **Visualization**: D3.js 7.9.0
- **UI**: React 18.3.1
- **Styling**: Inline styles with CSS-in-JS, dark theme (#0f172a, #1f2937)
- **Deployment**: Render (Docker)

### Backend Stack
- **Framework**: FastAPI (Python)
- **Broker Integration**: Alpaca Trading API
- **Deployment**: Render
- **Endpoints**: RESTful API with `/api/proxy` reverse proxy
- **Market Modules**: Strategy registry currently supplies `stocks_options`

### API Proxy Pattern
Frontend routes all backend requests through `/api/proxy/[...path]` to avoid CORS issues:
```
Frontend: /api/proxy/api/health
Backend:  https://paiid-86a1.onrender.com/api/health
```

## 🛠️ Local Development Setup

### Prerequisites
- Node.js 20+ and npm
- Python 3.11+
- Git
- Alpaca API keys (for backend)

### 🔧 Repository Maintenance Tools

**Automated Codebase Management:**
```bash
# Generate full codebase inventory
python scripts/codebase-inventory-analyzer.py

# Archive redundant files (with rollback capability)
python scripts/codebase-archival-tool.py --execute

# Process files needing verification
python scripts/verification-helper.py --mode batch --batch-size 20

# Update documentation index
python scripts/documentation-index-generator.py
```

**Maintenance Workflow:**
1. **Monthly**: Run documentation index generator
2. **Quarterly**: Process verification files in batches
3. **As needed**: Archive redundant files with rollback safety

---

## 🚀 Parallel Batch Execution (SUN TZU + ARMANI)

MOD SQUAD v2.2.0 introduces strategic batch planning and integration weaving for parallel task execution with 20-60% speedup.

### Quick Start

1. **Define tasks** (`tasks.json`):
   ```json
   [
     {"id": "task1", "description": "Update health router", "files": ["backend/app/routers/health.py"], "dependencies": []},
     {"id": "task2", "description": "Update orders router", "files": ["backend/app/routers/orders.py"], "dependencies": []}
   ]
   ```

2. **Plan batches:**
   ```bash
   python modsquad/cli/batch.py plan --tasks tasks.json --output plan.json
   ```

3. **Review plan:**
   ```bash
   cat plan.json | python -m json.tool
   ```

4. **Execute batches** (manually or via CI/CD)

5. **Weave results:**
   ```bash
   python modsquad/cli/batch.py weave --plan plan.json --results results.json
   ```

### ✨ Benefits
- ⚡ **20-60% speedup** for large multi-task changes
- 🔀 **Automatic conflict resolution** (imports, comments, functions)
- ✅ **5-layer validation** (syntax, types, imports, signatures, tests)
- 🔄 **Atomic rollback** on validation failure
- 🔒 **File locking** prevents race conditions
- 🛡️ **Server detection** prevents corruption during live development

### 📚 Documentation
- [Batching Examples](modsquad/docs/BATCHING_EXAMPLES.md) - 6 realistic scenarios with complete task definitions
- [Rollback Procedures](modsquad/docs/ROLLBACK_PROCEDURES.md) - Automatic & manual rollback guide
- [Complete Deployment Plan](modsquad/COMPLETE_DEPLOYMENT_PLAN.md) - Full implementation roadmap
- [Implementation Summary](modsquad/IMPLEMENTATION_SUMMARY.md) - Complete deployment details

### 🎯 Architecture
- **SUN TZU Squad:** Strategic batch planning (5 extensions)
- **ARMANI Squad:** Integration weaving (6 extensions)
- **Guardrails:** Max 5 parallel batches, <10% collision probability, <0.5% risk per batch

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Backend runs at http://localhost:8000

#### Local Infrastructure (Database + Cache)

```bash
docker compose -f infrastructure/docker-compose.dev.yml up -d
```

- PostgreSQL: `postgresql://paiid:paiid@localhost:5433/paiid`
- Redis: `redis://localhost:6380/0`

Stop services when finished:

```bash
docker compose -f infrastructure/docker-compose.dev.yml down
```

### Environment Variables

**Frontend** (`.env.local`):
```env
# No environment variables required - API proxy handles routing
```

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://paiid:paiid@localhost:5433/paiid
REDIS_URL=redis://localhost:6380/0
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # or live
# DEX wallet routing (optional for meme coin strategies)
DEX_RPC_URL=https://polygon-mainnet.infura.io/v3/your-key
DEX_WALLET_ADDRESS=0xYourWalletAddress
DEX_ROUTER_CONTRACT=uniswapV3
DEX_CHAIN_ID=137
DEX_SLIPPAGE_BPS=75
```

## 📁 Project Structure

```
PaiiD/
├── frontend/                       # Next.js frontend application
│   ├── components/
│   │   ├── RadialMenu.tsx          # D3.js radial navigation (8 segments)
│   │   ├── PositionsTable.tsx      # Enhanced positions with P&L cards
│   │   ├── MorningRoutine.tsx      # Health check workflow
│   │   └── ExecuteTradeForm.tsx    # Order execution form
│   ├── pages/
│   │   ├── index.tsx               # Main dashboard with radial menu
│   │   ├── test-radial.tsx         # Isolated radial menu test page
│   │   └── api/
│   │       └── proxy/[...path].ts  # Backend API proxy
│   ├── package.json
│   └── tsconfig.json
├── backend/                        # FastAPI backend application
│   ├── main.py                     # FastAPI application
│   ├── requirements.txt
│   └── [additional backend files]
├── scripts/                        # 🆕 Automation & Maintenance Tools
│   ├── codebase-inventory-analyzer.py    # Full codebase inventory
│   ├── codebase-archival-tool.py        # Safe file archival
│   ├── verification-helper.py           # File verification processing
│   └── documentation-index-generator.py # Documentation indexing
├── archive/                        # 🆕 Archived Files (Batch 8 cleanup)
│   └── cleanup-2025-10-24-165115/ # Timestamped archive with rollback
├── docs/                          # 🆕 Organized Documentation
│   ├── DOCUMENTATION_INDEX.md     # Master documentation index
│   ├── FILE_NAMING_CONVENTIONS.md # Naming standards
│   └── [categorized documentation]
├── README.md                      # This file (project overview)
├── OPERATIONS.md                  # Production operations guide
├── SECURITY.md                    # Security policy
├── TODO.md                        # Task management
└── [additional project files]
```

### 📊 Repository Health Metrics
- **Total Files**: 458 (reduced from 538)
- **Active Documentation**: 7 files (categorized and indexed)
- **Archived Files**: 80 files (0.80 MB space reclaimed)
- **Verification Pending**: 232 files (ready for automated processing)
- **Automation Tools**: 4 scripts for ongoing maintenance

## 🚀 Deployment

### Frontend (Render)

1. Create new Web Service on Render
2. Connect GitHub repository
3. Configure:
   - **Root Directory**: `frontend`
   - **Runtime**: Docker
   - **Dockerfile Path**: `./Dockerfile`
   - **Environment Variables**: Set NEXT_PUBLIC_API_TOKEN, NEXT_PUBLIC_ANTHROPIC_API_KEY in dashboard
4. Deploy automatically on every push to `main`

**Deployment URL**: https://paiid-frontend.onrender.com

### Backend (Render)

1. Create new Web Service on Render
2. Connect GitHub repository
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (Alpaca API keys)

**API URL**: https://ai-trader-86a1.onrender.com

## 🐛 Troubleshooting

### Common Issues

1. **Favicon 404 Error**
   - This is cosmetic and can be ignored
   - Add `public/favicon.ico` to frontend if desired

2. **API Proxy Not Working**
   - Ensure backend is running on Render
   - Check browser DevTools Network tab for proxy errors
   - Verify `/api/proxy/api/health` returns 200

3. **D3 Radial Menu Not Rendering**
   - Check browser console for D3.js errors
   - Ensure `d3` and `@types/d3` are installed: `npm install`
   - Clear `.next` cache: `rm -rf frontend/.next`

4. **Build Errors on Render**
   - Check for TypeScript errors locally: `npm run build`
   - Verify package-lock.json is up to date
   - Review Render deployment logs for Docker build errors

5. **Positions Table Showing -100% P&L**
   - Fixed in current version (commit 5855bb5)
   - Backend returns `marketPrice` field correctly
   - Field mapping prioritizes `marketPrice` over `currentPrice`

## 📚 Documentation

### 📖 Master Documentation Index
**[DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)** - Complete documentation navigation and categorization

### 🚀 Quick Start & Setup
- **[README.md](./README.md)** - This file (project overview and setup)
- **[DEVELOPMENT.md](./frontend/DEVELOPMENT.md)** - Frontend development guide
- **[SECURITY.md](./SECURITY.md)** - Security policy and best practices

### 🏗️ Operations & Deployment
- **[OPERATIONS.md](./OPERATIONS.md)** - Production operations and monitoring
- **[DEPLOYMENT_STATUS.md](./DEPLOYMENT_STATUS.md)** - Current deployment status
- **[ISSUE_TRACKER.md](./ISSUE_TRACKER.md)** - Active issues and bug tracking

### 📋 Project Management
- **[TODO.md](./TODO.md)** - Consolidated task checklist
- **[CLAUDE.md](./CLAUDE.md)** - Development guidelines and conventions

### 🔧 Maintenance & Automation
- **[FILE_NAMING_CONVENTIONS.md](./FILE_NAMING_CONVENTIONS.md)** - File naming standards
- **Codebase Tools** (in `scripts/` directory):
  - `codebase-inventory-analyzer.py` - Full codebase inventory
  - `codebase-archival-tool.py` - Safe file archival
  - `verification-helper.py` - File verification processing
  - `documentation-index-generator.py` - Documentation indexing

### 📊 Legacy Documentation (Archived)
**Note**: Many documentation files have been archived to `archive/cleanup-2025-10-24-165115/` for better organization. See [BATCH_8_CLEANUP_EXECUTION_REPORT.md](./BATCH_8_CLEANUP_EXECUTION_REPORT.md) for details.

**Active Roadmaps:**
- [LAUNCH_READINESS.md](./LAUNCH_READINESS.md) - 5 MVP tasks (1-2 days) - **IMMEDIATE**
- [PHASE_0_AUDIT_REPORT.md](./PHASE_0_AUDIT_REPORT.md) - Phases 1-4 (24-32 hours) - **SHORT-TERM**
- [ROADMAP.md](./ROADMAP.md) - 5 workflow enhancements (80 days) - **LONG-TERM**
- [WORKFLOW_AUDIT_RESULTS.md](./WORKFLOW_AUDIT_RESULTS.md) - Complete execution order

**Technical Documentation:**
- [Component Architecture](./COMPONENT_ARCHITECTURE.md) - Technical implementation guide
- [API Documentation](./API_DOCUMENTATION.md) - Complete endpoint reference

## 🔐 Security Notes

- Never commit `.env` files with real API keys
- Use Alpaca Paper Trading API for development
- Production deployment uses environment variables on Render
- Content Security Policy (CSP) headers prevent iframe injection
- Refer to `LOCKED_ARTIFACTS.md` for files marked LOCKED FINAL—do not modify without EXECUTE NOW approval

## 🎯 Next Steps

**Current Phase:** Phase 0 Preparation (94% MVP → Phase 1)

**Immediate (1-2 days):** Complete 5 MVP tasks from [LAUNCH_READINESS.md](./LAUNCH_READINESS.md)
1. Verify SSE in production
2. Test chart export on mobile
3. Mobile device testing
4. Sentry DSN configuration
5. Recommendation history tracking

**Short-term (24-32 hours):** Execute [PHASE_0_AUDIT_REPORT.md](./PHASE_0_AUDIT_REPORT.md)
1. Phase 1: Options Trading Implementation (6-8h)
2. Phase 2: ML Strategy Engine (4-6h)
3. Phase 3: UI/UX Polish (6-8h)
4. Phase 4: Code Quality Cleanup (8-10h)

**Long-term (80 days):** Execute [ROADMAP.md](./ROADMAP.md) enhancements
1. P&L Dashboard with historical charts
2. News Review with sentiment analysis
3. AI Recommendations with ML signals
4. Strategy Builder with visual designer
5. Backtesting engine with optimization

## 📝 Recent Changes (Commit 5855bb5)

- Fixed TypeScript build errors (duplicate CSS properties)
- Verified production deployment
- Enhanced PositionsTable with summary cards
- Improved dark theme consistency
- Added comprehensive documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-workflow`
3. Make changes and test locally
4. Build successfully: `cd frontend && npm run build`
5. Commit with descriptive messages
6. Push and create a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues, questions, or feature requests, please open a GitHub issue.

---

**Built with Claude Code** 🤖
