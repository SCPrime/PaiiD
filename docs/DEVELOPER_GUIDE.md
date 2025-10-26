# PaiiD Developer Guide

## Welcome to PaiiD Development

This guide will help you set up your development environment, understand the codebase structure, and contribute effectively to the PaiiD trading platform.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Common Development Tasks](#common-development-tasks)
6. [Code Style and Best Practices](#code-style-and-best-practices)
7. [Testing Guide](#testing-guide)
8. [Debugging Tips](#debugging-tips)
9. [API Development](#api-development)
10. [Component Development](#component-development)

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| **Node.js** | 20.17.0+ | Frontend runtime |
| **npm** | 10.0.0+ | Package manager |
| **Python** | 3.10+ | Backend runtime |
| **pip** | Latest | Python package manager |
| **Git** | Latest | Version control |
| **PostgreSQL** | 13+ (optional) | Database (local dev) |
| **Redis** | 5.0+ (optional) | Caching (local dev) |

**Recommended Tools:**
- **VS Code** with extensions:
  - ESLint
  - Prettier
  - Python
  - TypeScript Vue Plugin (Volar)
- **Postman** or **Insomnia** for API testing
- **Docker Desktop** (optional, for containerized development)

### Quick Start (5 Minutes)

```bash
# 1. Clone the repository
git clone https://github.com/YOUR-USERNAME/PaiiD.git
cd PaiiD

# 2. Setup frontend
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your API keys

# 3. Setup backend
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# 4. Start development servers
# Terminal 1 - Frontend
cd frontend
npm run dev

# Terminal 2 - Backend
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

**Verify Setup:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8001/api/health
- API Docs: http://localhost:8001/docs

---

## Development Environment Setup

### 1. Frontend Setup

**Install Dependencies:**
```bash
cd frontend
npm install
```

**Environment Variables (.env.local):**
```env
# Backend API Configuration
NEXT_PUBLIC_BACKEND_API_BASE_URL=http://127.0.0.1:8001

# API Authentication Token
NEXT_PUBLIC_API_TOKEN=your-api-token-here

# Anthropic AI API Key (optional, for AI features)
NEXT_PUBLIC_ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Development Mode
NODE_ENV=development
```

**Generate API Token:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Start Development Server:**
```bash
npm run dev
```

The frontend will be available at http://localhost:3000 with hot module reloading.

### 2. Backend Setup

**Create Virtual Environment:**
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Environment Variables (.env):**
```env
# Backend API Token (must match frontend)
API_TOKEN=your-api-token-here

# JWT Authentication
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/paiid
# For local dev without PostgreSQL:
# DATABASE_URL=sqlite:///./dev.db

# Tradier API (Market Data)
TRADIER_API_KEY=your-tradier-api-key
TRADIER_ACCOUNT_ID=your-tradier-account-id
TRADIER_API_BASE_URL=https://api.tradier.com/v1

# Alpaca API (Paper Trading)
ALPACA_PAPER_API_KEY=your-alpaca-key
ALPACA_PAPER_SECRET_KEY=your-alpaca-secret

# Optional Services
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=your-anthropic-key
SENTRY_DSN=your-sentry-dsn

# Development Settings
TESTING=false
USE_TEST_FIXTURES=false
LOG_LEVEL=INFO
LIVE_TRADING=false
```

**Generate Secrets:**
```bash
# API Token
python -c "import secrets; print(secrets.token_urlsafe(32))"

# JWT Secret Key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Initialize Database:**
```bash
# Create database (PostgreSQL)
createdb paiid

# Run migrations
cd backend
alembic upgrade head
```

**Start Development Server:**
```bash
python -m uvicorn app.main:app --reload --port 8001
```

The backend will be available at http://localhost:8001 with auto-reload on code changes.

### 3. API Keys Setup

**Tradier API (Market Data):**
1. Sign up at https://tradier.com/
2. Navigate to API Access
3. Generate API key
4. Copy key and account ID to `.env`

**Alpaca API (Paper Trading):**
1. Sign up at https://alpaca.markets/
2. Navigate to Paper Trading
3. Generate API keys
4. Copy keys to `.env`

**Anthropic API (AI Features):**
1. Sign up at https://console.anthropic.com/
2. Generate API key
3. Copy key to `.env.local` and `.env`

---

## Project Structure

### Monorepo Layout

```
PaiiD/
├── frontend/                     # Next.js frontend application
│   ├── components/               # React components
│   │   ├── RadialMenu.tsx        # D3.js radial navigation
│   │   ├── ExecuteTradeForm.tsx  # Trade execution
│   │   ├── PositionManager.tsx   # Position tracking
│   │   ├── AIRecommendations.tsx # AI suggestions
│   │   ├── workflows/            # Workflow components
│   │   ├── trading/              # Trading components
│   │   └── ui/                   # Reusable UI components
│   ├── pages/                    # Next.js pages (routes)
│   │   ├── index.tsx             # Main dashboard
│   │   ├── _app.tsx              # Global layout
│   │   └── api/                  # API routes
│   │       └── proxy/[...path].ts # Backend proxy
│   ├── lib/                      # Utility libraries
│   │   ├── alpaca.ts             # Alpaca client
│   │   ├── aiAdapter.ts          # AI integration
│   │   ├── logger.ts             # Logging utility
│   │   └── userManagement.ts     # User session
│   ├── hooks/                    # Custom React hooks
│   │   ├── useBreakpoint.ts      # Responsive detection
│   │   └── useHelp.ts            # Help system
│   ├── styles/                   # Style constants
│   ├── tests/                    # Test files
│   ├── public/                   # Static assets
│   ├── package.json              # Dependencies
│   ├── tsconfig.json             # TypeScript config
│   ├── next.config.js            # Next.js config
│   └── Dockerfile                # Production build
│
├── backend/                      # FastAPI backend application
│   ├── app/
│   │   ├── routers/              # API endpoints (25 modules)
│   │   │   ├── auth.py           # Authentication
│   │   │   ├── portfolio.py      # Portfolio data
│   │   │   ├── orders.py         # Trade execution
│   │   │   ├── market.py         # Market data
│   │   │   ├── ai.py             # AI recommendations
│   │   │   ├── ml.py             # ML models
│   │   │   └── ...               # 19 more routers
│   │   ├── services/             # Business logic
│   │   │   ├── cache.py          # Cache service
│   │   │   ├── tradier_stream.py # Tradier streaming
│   │   │   └── ...               # Additional services
│   │   ├── models/               # Database models
│   │   │   └── database.py       # SQLAlchemy models
│   │   ├── core/                 # Core functionality
│   │   │   ├── config.py         # Settings
│   │   │   ├── auth.py           # Auth utilities
│   │   │   ├── unified_auth.py   # Unified auth
│   │   │   └── ...               # Additional core
│   │   ├── middleware/           # Middleware
│   │   │   ├── rate_limit.py     # Rate limiting
│   │   │   ├── security.py       # Security headers
│   │   │   └── ...               # Additional middleware
│   │   ├── db/                   # Database
│   │   │   └── session.py        # DB session
│   │   ├── ml/                   # Machine learning
│   │   │   ├── ensemble.py       # Ensemble models
│   │   │   └── regime_detection.py
│   │   └── utils/                # Utilities
│   ├── alembic/                  # Database migrations
│   │   └── versions/             # Migration files
│   ├── tests/                    # Test files
│   ├── requirements.txt          # Python dependencies
│   └── .env                      # Environment variables
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md           # System architecture
│   ├── DEVELOPER_GUIDE.md        # This file
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── TROUBLESHOOTING.md        # Common issues
│   └── ...                       # Additional docs
│
├── scripts/                      # Automation scripts
│   ├── start-dev.ps1             # Windows dev startup
│   └── ...                       # Additional scripts
│
├── .github/                      # GitHub workflows
│   └── workflows/                # CI/CD pipelines
│
├── README.md                     # Project overview
├── CLAUDE.md                     # Development guidelines
└── CONTRIBUTING.md               # Contribution guide
```

---

## Development Workflow

### Standard Workflow

```
1. Sync with main branch
   ↓
2. Create feature branch
   ↓
3. Make changes
   ↓
4. Run tests locally
   ↓
5. Commit with conventional message
   ↓
6. Push to remote
   ↓
7. Create pull request
   ↓
8. Address review feedback
   ↓
9. Merge to main
```

### Step-by-Step Example

**1. Sync with Main:**
```bash
git checkout main
git pull origin main
```

**2. Create Feature Branch:**
```bash
git checkout -b feat/add-stop-loss-orders
```

**3. Make Changes:**
Edit code in your IDE following project conventions.

**4. Test Locally:**
```bash
# Frontend tests
cd frontend
npm run test
npm run lint
npm run type-check

# Backend tests
cd backend
pytest -v
python -m ruff check
```

**5. Commit Changes:**
```bash
git add .
git commit -m "feat(trading): add stop-loss order support

Implement stop-loss order type with configurable trigger price.
Updates OrderTemplate model and ExecuteTradeForm component.

Closes #456"
```

**6. Push to Remote:**
```bash
git push origin feat/add-stop-loss-orders
```

**7. Create Pull Request:**
- Go to GitHub repository
- Click "Compare & pull request"
- Fill out PR template
- Request reviews

---

## Common Development Tasks

### Adding a New API Endpoint

**Backend (FastAPI):**

```python
# backend/app/routers/orders.py
from fastapi import APIRouter, Depends
from ..core.unified_auth import get_current_user_unified
from ..models.database import User

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/stop-loss")
async def create_stop_loss_order(
    symbol: str,
    quantity: int,
    stop_price: float,
    current_user: User = Depends(get_current_user_unified)
):
    """Create a stop-loss order"""
    # Implementation
    return {
        "order_id": "abc123",
        "status": "submitted"
    }
```

**Register Router:**
```python
# backend/app/main.py
from .routers import orders

app.include_router(orders.router, prefix="/api")
```

**Frontend Integration:**
```typescript
// frontend/lib/api.ts
export async function createStopLossOrder(
  symbol: string,
  quantity: number,
  stopPrice: number
) {
  const response = await fetch('/api/proxy/api/orders/stop-loss', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`
    },
    body: JSON.stringify({ symbol, quantity, stop_price: stopPrice })
  });

  if (!response.ok) {
    throw new Error('Failed to create stop-loss order');
  }

  return response.json();
}
```

**Use in Component:**
```typescript
// frontend/components/ExecuteTradeForm.tsx
import { createStopLossOrder } from '../lib/api';

const handleStopLoss = async () => {
  try {
    const result = await createStopLossOrder('AAPL', 10, 150.00);
    console.log('Order created:', result);
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### Adding a New Frontend Component

**1. Create Component File:**
```typescript
// frontend/components/StopLossForm.tsx
import React, { useState } from 'react';

interface StopLossFormProps {
  symbol: string;
  onSubmit: (stopPrice: number) => void;
}

const StopLossForm: React.FC<StopLossFormProps> = ({ symbol, onSubmit }) => {
  const [stopPrice, setStopPrice] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(parseFloat(stopPrice));
  };

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="stopPrice">Stop Price</label>
      <input
        id="stopPrice"
        type="number"
        step="0.01"
        value={stopPrice}
        onChange={(e) => setStopPrice(e.target.value)}
        placeholder="Enter stop price"
      />
      <button type="submit">Set Stop Loss</button>
    </form>
  );
};

export default StopLossForm;
```

**2. Use in Parent Component:**
```typescript
// frontend/pages/index.tsx
import StopLossForm from '../components/StopLossForm';

const Dashboard = () => {
  const handleStopLossSubmit = (stopPrice: number) => {
    console.log('Stop price:', stopPrice);
    // Call API
  };

  return (
    <div>
      <StopLossForm symbol="AAPL" onSubmit={handleStopLossSubmit} />
    </div>
  );
};
```

### Adding Database Migration

**1. Create Migration:**
```bash
cd backend
alembic revision -m "add stop loss orders table"
```

**2. Edit Migration File:**
```python
# backend/alembic/versions/xxx_add_stop_loss_orders.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'stop_loss_orders',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('symbol', sa.String(10), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('stop_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )

def downgrade():
    op.drop_table('stop_loss_orders')
```

**3. Apply Migration:**
```bash
alembic upgrade head
```

### Adding Unit Tests

**Frontend Test (Jest):**
```typescript
// frontend/components/__tests__/StopLossForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import StopLossForm from '../StopLossForm';

test('submits stop loss with valid price', () => {
  const mockSubmit = jest.fn();
  render(<StopLossForm symbol="AAPL" onSubmit={mockSubmit} />);

  const input = screen.getByPlaceholderText('Enter stop price');
  fireEvent.change(input, { target: { value: '150.00' } });

  const button = screen.getByText('Set Stop Loss');
  fireEvent.click(button);

  expect(mockSubmit).toHaveBeenCalledWith(150.00);
});
```

**Backend Test (pytest):**
```python
# backend/tests/test_stop_loss.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_stop_loss_order():
    """Test creating a stop-loss order"""
    headers = {"Authorization": "Bearer test-token"}
    data = {
        "symbol": "AAPL",
        "quantity": 10,
        "stop_price": 150.00
    }

    response = client.post("/api/orders/stop-loss", json=data, headers=headers)

    assert response.status_code == 200
    assert response.json()["status"] == "submitted"
```

---

## Code Style and Best Practices

### Frontend (TypeScript/React)

**TypeScript Best Practices:**

```typescript
// ✅ DO: Use interfaces for object shapes
interface UserProfile {
  id: number;
  username: string;
  email: string;
}

// ✅ DO: Use type for unions
type OrderSide = 'buy' | 'sell';

// ❌ DON'T: Use 'any'
const data: any = fetchData();  // ❌ Bad

// ✅ DO: Use proper types
const data: UserProfile = fetchData();  // ✅ Good

// ✅ DO: Add return types to functions
function calculateProfit(cost: number, revenue: number): number {
  return revenue - cost;
}
```

**React Best Practices:**

```typescript
// ✅ DO: Use functional components with hooks
const MyComponent: React.FC<Props> = ({ title }) => {
  const [count, setCount] = useState<number>(0);

  useEffect(() => {
    // Effect logic
  }, []);

  return <div>{title}</div>;
};

// ❌ DON'T: Use class components (legacy)
class MyComponent extends React.Component { ... }

// ✅ DO: Extract reusable logic into custom hooks
const useMarketData = (symbol: string) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchMarketData(symbol).then(setData);
  }, [symbol]);

  return data;
};
```

**Styling Convention:**

```typescript
// ✅ DO: Use inline styles with glassmorphism theme
const styles = {
  container: {
    background: 'rgba(30, 41, 59, 0.8)',
    backdropFilter: 'blur(10px)',
    borderRadius: '16px',
    padding: '20px',
    border: '1px solid rgba(16, 185, 129, 0.2)'
  }
};

// ❌ DON'T: Use external CSS files or Tailwind
// No .css or .module.css files
```

### Backend (Python/FastAPI)

**Python Best Practices:**

```python
# ✅ DO: Use type hints
def execute_trade(symbol: str, quantity: int, side: str) -> dict:
    """Execute a trade with the given parameters."""
    return {"order_id": "123", "status": "filled"}

# ✅ DO: Follow PEP 8 naming conventions
user_profile = get_user_profile()  # snake_case for variables
UserProfile = namedtuple('UserProfile', ['id', 'name'])  # PascalCase for classes

# ✅ DO: Use docstrings
def calculate_greeks(option_data: dict) -> dict:
    """
    Calculate Black-Scholes Greeks for an option.

    Args:
        option_data: Dictionary containing option parameters

    Returns:
        Dictionary with calculated Greeks (delta, gamma, theta, vega)
    """
    # Implementation
```

**FastAPI Best Practices:**

```python
# ✅ DO: Use Pydantic models for validation
from pydantic import BaseModel, Field

class OrderRequest(BaseModel):
    symbol: str = Field(..., regex=r"^[A-Z]{1,5}$")
    quantity: int = Field(..., gt=0, le=10000)
    side: Literal["buy", "sell"]

# ✅ DO: Use dependency injection
from fastapi import Depends
from app.core.unified_auth import get_current_user_unified

@router.post("/orders")
async def create_order(
    order: OrderRequest,
    current_user: User = Depends(get_current_user_unified)
):
    # Implementation

# ✅ DO: Use proper HTTP status codes
from fastapi import HTTPException, status

@router.get("/positions/{position_id}")
async def get_position(position_id: int):
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )
    return position
```

---

## Testing Guide

### Frontend Testing (Jest + React Testing Library)

**Run Tests:**
```bash
cd frontend
npm run test              # Watch mode
npm run test:ci           # CI mode with coverage
npm run test:coverage     # Generate coverage report
```

**Test Structure:**
```typescript
// frontend/components/__tests__/ExecuteTradeForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ExecuteTradeForm from '../ExecuteTradeForm';

describe('ExecuteTradeForm', () => {
  test('renders form fields', () => {
    render(<ExecuteTradeForm />);

    expect(screen.getByLabelText('Symbol')).toBeInTheDocument();
    expect(screen.getByLabelText('Quantity')).toBeInTheDocument();
    expect(screen.getByText('Submit Order')).toBeInTheDocument();
  });

  test('submits order with valid inputs', async () => {
    const mockSubmit = jest.fn();
    render(<ExecuteTradeForm onSubmit={mockSubmit} />);

    fireEvent.change(screen.getByLabelText('Symbol'), {
      target: { value: 'AAPL' }
    });
    fireEvent.change(screen.getByLabelText('Quantity'), {
      target: { value: '10' }
    });
    fireEvent.click(screen.getByText('Submit Order'));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        symbol: 'AAPL',
        quantity: 10
      });
    });
  });

  test('displays error for invalid symbol', () => {
    render(<ExecuteTradeForm />);

    fireEvent.change(screen.getByLabelText('Symbol'), {
      target: { value: 'invalid' }
    });
    fireEvent.blur(screen.getByLabelText('Symbol'));

    expect(screen.getByText('Invalid symbol format')).toBeInTheDocument();
  });
});
```

### Backend Testing (pytest)

**Run Tests:**
```bash
cd backend
pytest -v                 # Verbose output
pytest --cov=app          # With coverage
pytest -k test_orders     # Run specific tests
```

**Test Structure:**
```python
# backend/tests/test_orders.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Fixture providing authentication headers"""
    return {"Authorization": "Bearer test-token-12345"}

def test_create_order_requires_auth():
    """Test /api/orders requires authentication"""
    response = client.post("/api/orders", json={
        "symbol": "AAPL",
        "quantity": 10,
        "side": "buy"
    })
    assert response.status_code == 401

def test_create_order_success(auth_headers):
    """Test creating an order with valid data"""
    response = client.post("/api/orders", json={
        "symbol": "AAPL",
        "quantity": 10,
        "side": "buy"
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["status"] in ["submitted", "pending"]

def test_create_order_invalid_symbol(auth_headers):
    """Test order creation with invalid symbol"""
    response = client.post("/api/orders", json={
        "symbol": "INVALID123",
        "quantity": 10,
        "side": "buy"
    }, headers=auth_headers)

    assert response.status_code == 422
```

---

## Debugging Tips

### Frontend Debugging

**Console Logging:**
```typescript
// Use logger utility instead of console.log
import { logger } from '../lib/logger';

logger.info('Trade executed', { symbol: 'AAPL', quantity: 10 });
logger.error('API call failed', error);
```

**React DevTools:**
- Install React DevTools browser extension
- Inspect component props and state
- Profile performance issues

**Network Debugging:**
- Open browser DevTools (F12)
- Navigate to Network tab
- Filter by "Fetch/XHR"
- Inspect API requests and responses

### Backend Debugging

**Print Debugging:**
```python
import logging

logger = logging.getLogger(__name__)

@router.post("/orders")
async def create_order(order: OrderRequest):
    logger.info(f"Received order: {order.dict()}")
    # Implementation
    logger.debug(f"Order processed: {result}")
    return result
```

**Interactive Debugger:**
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint()
breakpoint()
```

**FastAPI Docs:**
- Navigate to http://localhost:8001/docs
- Interactive API documentation
- Test endpoints directly

---

## API Development

### API Documentation

All API endpoints are automatically documented at:
- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

### Creating New Endpoints

Follow the established pattern in existing routers:

```python
# backend/app/routers/example.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..core.unified_auth import get_current_user_unified
from ..models.database import User

router = APIRouter(prefix="/example", tags=["example"])

class ExampleRequest(BaseModel):
    """Request model with validation"""
    field1: str
    field2: int

class ExampleResponse(BaseModel):
    """Response model for type safety"""
    result: str
    status: str

@router.post("/", response_model=ExampleResponse)
async def create_example(
    request: ExampleRequest,
    current_user: User = Depends(get_current_user_unified)
):
    """
    Create a new example resource.

    - **field1**: Description of field1
    - **field2**: Description of field2
    """
    # Implementation
    return ExampleResponse(result="success", status="ok")
```

---

## Component Development

### Creating Reusable Components

**Component Template:**

```typescript
// frontend/components/ui/Button.tsx
import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  disabled = false
}) => {
  const styles = {
    primary: {
      background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
      color: '#fff'
    },
    secondary: {
      background: 'rgba(59, 130, 246, 0.2)',
      color: '#3b82f6'
    },
    danger: {
      background: 'rgba(239, 68, 68, 0.2)',
      color: '#ef4444'
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        ...styles[variant],
        padding: '12px 24px',
        borderRadius: '8px',
        border: 'none',
        fontWeight: '600',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1
      }}
    >
      {children}
    </button>
  );
};

export default Button;
```

**Usage:**
```typescript
import Button from '../components/ui/Button';

<Button variant="primary" onClick={() => console.log('Clicked')}>
  Execute Trade
</Button>
```

---

## Next Steps

Now that you're set up, explore these resources:

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture overview
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions
- **[API_DOCUMENTATION_COMPREHENSIVE.md](./API_DOCUMENTATION_COMPREHENSIVE.md)** - API reference

**Join the Development:**
1. Pick an issue from GitHub Issues
2. Follow the development workflow
3. Submit a pull request
4. Celebrate your contribution! 🎉

---

**Document Version:** 1.0.0
**Last Updated:** October 26, 2025
**Maintainer:** PaiiD Development Team
