# 📊 PaiiD Trading Architecture Guide

**Date:** October 12, 2025
**Status:** Reference Document - Broker Integration Strategy
**Author:** Dr. VS Code/Claude (Code Surgeon)

---

## Executive Summary

This document provides the complete trading architecture for PaiiD, including broker selection, API integration patterns, cost analysis, and implementation roadmap. Based on extensive research into optimal trading setups for options-focused strategies with PDT considerations.

---

## Table of Contents

1. [Current Architecture (Implemented)](#current-architecture)
2. [Optimal Trading Setup (Recommended)](#optimal-trading-setup)
3. [Broker Comparison Matrix](#broker-comparison-matrix)
4. [API Integration Architecture](#api-integration-architecture)
5. [Pattern Day Trading (PDT) Implementation](#pattern-day-trading-implementation)
6. [Data Sources & Market Data](#data-sources--market-data)
7. [Cost Analysis](#cost-analysis)
8. [Security & API Key Management](#security--api-key-management)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Current Architecture (Implemented)

### ✅ What's Live Today

**Broker:** Tradier Pro
**Account:** 6YB64299 (Cash account)
**Mode:** Paper trading
**API Key:** `1tIR8iQL9epAwNcc7HSXPuCypjkf`

**Backend Integration:**
- File: `backend/app/services/tradier_client.py`
- Endpoints: Account, Positions, Orders, Market Data, Options
- Status: ✅ **IMPLEMENTED** (October 2025)

**Key Features:**
- ✅ Real-time market data (consolidated)
- ✅ Options chain data with Greeks
- ✅ Commission-free stock/ETF options
- ✅ Account balance tracking
- ✅ Position management
- ✅ Order execution (market, limit, stop)

**Cost:** $10/month (Tradier Pro subscription)

---

## Optimal Trading Setup (Recommended)

### 🎯 Three-Tier Architecture

```
┌─────────────────────────────────────────────────┐
│         Paper Trading (Development)              │
│   Broker: Alpaca Paper + IEX Data (FREE)       │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│          Live Trading (Current)                  │
│   Broker: Tradier Pro ($10/month)              │
│   Data: Real-time consolidated + Greeks        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│        Future Expansion (Optional)               │
│   Broker: TD Ameritrade/Schwab                  │
│   Toggle: Runtime broker switching              │
└─────────────────────────────────────────────────┘
```

### Paper Trading Tier: Alpaca (FREE)

**Purpose:** Strategy development, backtesting, testing new features

**Configuration:**
```python
TRADING_MODE=paper
PAPER_BROKER=alpaca
ALPACA_PAPER_KEY=<your-key>
ALPACA_PAPER_SECRET=<your-secret>
```

**Features:**
- ✅ $100k simulated starting balance
- ✅ Real-time IEX market data (free)
- ✅ Full multi-leg options support
- ✅ PDT rule enforcement (realistic testing)
- ✅ 200 requests/minute rate limit
- ✅ Same API as live trading

**Limitations:**
- ⚠️ IEX data only (single exchange, not consolidated)
- ⚠️ Simplified fill logic (10% random partial fills)
- ⚠️ No regulatory fees simulated
- ⚠️ Overly optimistic multi-leg fills

**Cost:** $0

---

### Live Trading Tier: Tradier Pro (ACTIVE)

**Purpose:** Live paper trading → real money trading

**Configuration:**
```python
TRADING_MODE=paper  # or 'live' when ready
LIVE_BROKER=tradier
TRADIER_API_KEY=1tIR8iQL9epAwNcc7HSXPuCypjkf
TRADIER_ACCOUNT_ID=6YB64299
TRADIER_API_BASE_URL=https://api.tradier.com/v1
TRADIER_USE_SANDBOX=false
```

**Account Details:**
- **Type:** Cash account (NO PDT restrictions!)
- **Owner:** SPENCER-CARL SAINT-CYR
- **Account Number:** 6YB64299
- **Classification:** Individual
- **Option Level:** 1
- **Status:** Active (created 2025-10-09)
- **Day Trader Flag:** False

**Features:**
- ✅ Real-time consolidated market data (included)
- ✅ Options Greeks + IV (via ORATS partnership)
- ✅ Commission-free stock/ETF options
- ✅ Real-time options chain data
- ✅ Multi-leg support (up to 4 legs)
- ✅ WebSocket streaming available
- ✅ No separate data subscription needed

**Pricing:**
- Monthly Fee: $10 (Pro tier)
- Stock/ETF Options: $0 commission
- Index Options (SPX/NDX): $0.35/contract + fees
- Regulatory Fees: ~$0.05-0.08 per contract (unavoidable)

**Cost:** $10/month + regulatory fees

**Advantages:**
- Best value for options-focused trading
- Data + trading in one package
- No PDT restrictions (cash account)
- Professional-grade data included

---

### Future Expansion: TD Ameritrade/Schwab (Optional)

**Purpose:** Redundancy, broker failover, execution quality comparison

**Configuration:**
```python
TRADING_MODE=live
LIVE_BROKER=tdameritrade  # Runtime toggle
TD_CLIENT_ID=<when-you-get-access>
TD_REFRESH_TOKEN=<when-you-get-access>
```

**Status:** 🔄 STUB READY - Implementation pending API access

**Why Consider:**
- Hedge against single broker outages
- thinkorswim-quality options data
- Compare execution quality
- Institutional-grade platform
- Full PDT status exposure via API

**Implementation:** When you receive TD Ameritrade/Schwab API credentials

---

## Broker Comparison Matrix

### Feature Comparison

| Feature | Alpaca Paper (Dev) | Tradier Pro (Active) | TD Ameritrade (Future) |
|---------|-------------------|----------------------|------------------------|
| **Cost** | $0 | $10/month | TBD |
| **Market Data** | IEX (free) | Consolidated RT | SIP feed |
| **Options Support** | ✅ Full | ✅ Full | ✅ Full |
| **Multi-leg Orders** | ✅ 4 legs | ✅ 4 legs | ✅ Complex |
| **Greeks/IV** | ❌ No | ✅ ORATS | ✅ Native |
| **Stock Options Commission** | $0 | $0 | Varies |
| **Index Options Commission** | $0 | $0.35/contract | Varies |
| **PDT API Exposure** | ✅ `daytrade_count` | ❌ Manual tracking | ✅ Full API |
| **WebSocket Streaming** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Python SDK** | ✅ `alpaca-py` | ❌ REST only | ❌ REST only |
| **Paper Trading** | ✅ Built-in | ⚠️ 15-min delay | ✅ Full sim |
| **Rate Limits** | 200/min | 120/min | 120/min |
| **Historical Data** | ✅ Since 2024 | ✅ Available | ✅ Extensive |

### Recommendation Matrix

| Use Case | Recommended Broker | Reasoning |
|----------|-------------------|-----------|
| **Strategy Development** | Alpaca Paper | Free, realistic, fast iteration |
| **Options Day Trading** | Tradier Pro | Best value, real-time Greeks, $10/month |
| **High-Frequency** | Avoid free tier | Need full SIP feed ($99/month minimum) |
| **Production with Redundancy** | Tradier + TD | Failover capability, compare execution |
| **Starting with \u003c$25k** | Cash account (any broker) | Avoid PDT entirely |

---

## API Integration Architecture

### Broker Abstraction Layer

**Design Pattern:** Strategy Pattern with Factory

**File Structure:**
```
backend/app/
├── services/
│   ├── brokers/
│   │   ├── __init__.py
│   │   ├── base.py              # BrokerInterface abstract class
│   │   ├── alpaca_broker.py      # Alpaca implementation
│   │   ├── tradier_broker.py     # Tradier implementation ✅ DONE
│   │   ├── td_broker.py          # TD Ameritrade stub
│   │   └── factory.py            # BrokerFactory
```

### BrokerInterface (Abstract Base Class)

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class BrokerInterface(ABC):
    """Abstract interface for all broker implementations"""

    @abstractmethod
    def get_account(self) -> Dict:
        """Get account information"""
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """Get all current positions"""
        pass

    @abstractmethod
    def get_orders(self) -> List[Dict]:
        """Get order history"""
        pass

    @abstractmethod
    def place_order(self, symbol: str, side: str, quantity: int, **kwargs) -> Dict:
        """Place an order"""
        pass

    @abstractmethod
    def place_multileg_order(self, legs: List[Dict], quantity: int, limit_price: float) -> Dict:
        """Place multi-leg options order"""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        pass

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote"""
        pass

    @abstractmethod
    def get_option_chain(self, symbol: str, expiration: Optional[str] = None) -> Dict:
        """Get options chain"""
        pass

    @abstractmethod
    def get_day_trade_count(self) -> int:
        """Get number of day trades in last 5 business days"""
        pass

    @abstractmethod
    def is_pdt_flagged(self) -> bool:
        """Check if account is flagged as pattern day trader"""
        pass
```

### Tradier Implementation (✅ CURRENT)

**File:** `backend/app/services/tradier_client.py`

**Status:** ✅ FULLY IMPLEMENTED (October 2025)

**Key Methods:**
```python
class TradierClient(BrokerInterface):
    def __init__(self):
        self.api_key = os.getenv("TRADIER_API_KEY")
        self.account_id = os.getenv("TRADIER_ACCOUNT_ID")
        self.base_url = os.getenv("TRADIER_API_BASE_URL")

    def get_account(self) -> Dict:
        # Returns normalized account data
        # Maps Tradier fields to standard format

    def get_positions(self) -> List[Dict]:
        # Fetches positions, normalizes to standard format
        # Handles empty positions case

    def place_order(self, symbol, side, quantity, order_type="market", **kwargs):
        # Supports: market, limit, stop, stop_limit
        # Returns order confirmation

    def get_option_chains(self, symbol, expiration=None):
        # Returns full options chain with Greeks

    # MISSING: PDT tracking (Tradier doesn't expose via API)
    def get_day_trade_count(self) -> int:
        # TODO: Must implement manual tracking
        # Parse order history to count day trades
        pass
```

**Current Integration:**
- Used by: `backend/app/routers/portfolio.py`
- Endpoints: `/api/account`, `/api/positions`, `/api/orders`
- Status: ✅ Working (confirmed via testing)

### Alpaca Implementation (🔄 PAPER ONLY)

**File:** To be created: `backend/app/services/brokers/alpaca_broker.py`

**Status:** 🔄 STUB READY (needs implementation)

```python
from alpaca.trading.client import TradingClient
from .base import BrokerInterface

class AlpacaBroker(BrokerInterface):
    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.client = TradingClient(api_key, secret_key, paper=paper)

    def get_account(self) -> Dict:
        account = self.client.get_account()
        return {
            "account_number": account.account_number,
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value),
            "equity": float(account.equity),
            "status": account.status
        }

    def get_day_trade_count(self) -> int:
        # ✅ Alpaca PROVIDES this directly!
        account = self.client.get_account()
        return account.daytrade_count

    def is_pdt_flagged(self) -> bool:
        account = self.client.get_account()
        return account.pattern_day_trader

    # ... other methods
```

**Advantages:**
- Excellent Python SDK (`alpaca-py`)
- PDT status built-in
- Free paper trading
- Same API for paper and live

### TD Ameritrade/Schwab Implementation (🔄 STUB)

**File:** To be created: `backend/app/services/brokers/td_broker.py`

**Status:** 🔄 STUB (waiting for API credentials)

```python
import requests
from .base import BrokerInterface

class TDAmeritradeBroker(BrokerInterface):
    def __init__(self, client_id: str, refresh_token: str):
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.base_url = "https://api.tdameritrade.com/v1"
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        # OAuth 2.0 refresh token flow
        # Tokens expire every 90 days
        pass

    def get_account(self) -> Dict:
        # TD has different response structure
        # Must normalize to standard format
        pass

    def get_day_trade_count(self) -> int:
        # ✅ TD PROVIDES full PDT data
        # Better than Tradier for PDT tracking
        pass

    # ... other methods
```

**When to Implement:** After receiving TD Ameritrade/Schwab API access

---

### Broker Factory (Runtime Selection)

**File:** To be created: `backend/app/services/brokers/factory.py`

```python
from typing import Literal
from .base import BrokerInterface
from .alpaca_broker import AlpacaBroker
from .tradier_broker import TradierClient  # Already exists
from .td_broker import TDAmeritradeBroker

BrokerType = Literal["alpaca", "tradier", "tdameritrade"]

class BrokerFactory:
    @staticmethod
    def create_broker(broker_type: BrokerType, trading_mode: str = "paper") -> BrokerInterface:
        """
        Create appropriate broker instance based on configuration

        Args:
            broker_type: "alpaca", "tradier", or "tdameritrade"
            trading_mode: "paper" or "live"

        Returns:
            BrokerInterface implementation
        """
        if trading_mode == "paper":
            # Always use Alpaca for paper trading
            return AlpacaBroker(
                api_key=os.getenv("ALPACA_PAPER_KEY"),
                secret_key=os.getenv("ALPACA_PAPER_SECRET"),
                paper=True
            )

        # Live trading - select based on broker_type
        if broker_type == "alpaca":
            return AlpacaBroker(
                api_key=os.getenv("ALPACA_LIVE_KEY"),
                secret_key=os.getenv("ALPACA_LIVE_SECRET"),
                paper=False
            )
        elif broker_type == "tradier":
            return TradierClient()  # Uses existing implementation
        elif broker_type == "tdameritrade":
            if not os.getenv("TD_CLIENT_ID"):
                raise ValueError("TD Ameritrade credentials not configured")
            return TDAmeritradeBroker(
                client_id=os.getenv("TD_CLIENT_ID"),
                refresh_token=os.getenv("TD_REFRESH_TOKEN")
            )
        else:
            raise ValueError(f"Unknown broker type: {broker_type}")

# Usage in routers:
from .brokers.factory import BrokerFactory

broker = BrokerFactory.create_broker(
    broker_type=settings.LIVE_BROKER,  # "tradier" currently
    trading_mode=settings.TRADING_MODE   # "paper" currently
)

account = broker.get_account()
positions = broker.get_positions()
```

---

## Pattern Day Trading (PDT) Implementation

### What is PDT?

**FINRA Rule:** If you execute 4+ day trades within 5 business days AND day trades represent >6% of total trading activity, you're flagged as a Pattern Day Trader.

**PDT Requirements:**
- Must maintain $25,000 minimum equity
- If below $25k, restricted to 3 day trades per rolling 5-day period
- Violation = 90-day trading restriction

**Cash Account Exemption:** PDT rules do NOT apply to cash accounts!

### Day Trade Definition

**A day trade occurs when:**
1. You open a position
2. You close the SAME position
3. Both trades occur on the SAME trading day

**Examples:**
```
✅ Day Trade:
- 9:30 AM: BUY 100 shares AAPL
- 2:00 PM: SELL 100 shares AAPL
(Same day = 1 day trade)

❌ NOT a Day Trade:
- Monday: BUY 100 shares AAPL
- Tuesday: SELL 100 shares AAPL
(Different days = NOT a day trade)

✅ Day Trade (Multi-leg):
- 10:00 AM: Open iron condor (4 legs)
- 3:00 PM: Close iron condor (4 legs)
(Same day, same strategy = 1 day trade)

❌ Multiple Day Trades (Legging Out):
- 10:00 AM: Open iron condor (4 legs as one order)
- 2:00 PM: Close short call leg separately
- 3:00 PM: Close long call leg separately
(Same day, separate closes = 2 day trades!)
```

### 5-Business-Day Rolling Window

**Important:** The window is BUSINESS days, not calendar days.

**NYSE Holidays (excluded from count):**
- New Year's Day
- Martin Luther King Jr. Day
- Presidents' Day
- Good Friday
- Memorial Day
- Juneteenth
- Independence Day
- Labor Day
- Thanksgiving
- Christmas

**Example Calculation:**
```
Today: Thursday, October 12, 2025

5-Business-Day Window:
- Thursday Oct 12 (today)
- Wednesday Oct 11
- Tuesday Oct 10
- Monday Oct 9
- Friday Oct 6

(Skips weekends: Oct 7-8)

If you made 3 day trades on Friday Oct 6, and 1 more today,
you've hit 4 day trades in 5 business days = PDT FLAGGED
```

### Multi-Leg Options PDT Rules

**Best Practice:** Always enter and exit multi-leg strategies as complete strategies (single order).

**Single Order = 1 Day Trade:**
```python
# Opening trade
order = {
    "order_class": "mleg",  # Multi-leg
    "legs": [
        {"symbol": "SPY_241025C450", "side": "buy", "ratio": 1},
        {"symbol": "SPY_241025C455", "side": "sell", "ratio": 1},
        {"symbol": "SPY_241025P445", "side": "sell", "ratio": 1},
        {"symbol": "SPY_241025P440", "side": "buy", "ratio": 1}
    ]
}

# Closing trade (same day)
order_close = {
    "order_class": "mleg",
    "legs": [same legs, opposite sides]
}

# Result: 1 day trade (opened and closed as complete strategy)
```

**Legging Out = Multiple Day Trades:**
```python
# DON'T DO THIS on same day if trying to avoid PDT:

# Close each leg separately:
1. Close short call → 1 day trade
2. Close long call → 2nd day trade
3. Close short put → 3rd day trade
4. Close long put → 4th day trade

# Result: 4 day trades (triggered PDT if 0 previous)
```

### PDT Tracking Algorithm

**For Alpaca (Built-in):**
```python
def get_pdt_status():
    account = alpaca_client.get_account()
    return {
        "day_trade_count": account.daytrade_count,  # ✅ Provided
        "is_pdt_flagged": account.pattern_day_trader,  # ✅ Provided
        "equity": float(account.equity)
    }
```

**For Tradier (Manual Implementation Required):**
```python
import os
from datetime import datetime, timedelta
from typing import List, Dict

def get_nyse_holidays(year: int) -> List[datetime]:
    """Return list of NYSE holidays for given year"""
    # Hardcode or use holiday calculation library
    return [
        datetime(year, 1, 1),   # New Year's
        datetime(year, 1, 16),  # MLK Day (3rd Monday)
        # ... etc
    ]

def is_business_day(date: datetime) -> bool:
    """Check if date is a business day (not weekend/holiday)"""
    if date.weekday() >= 5:  # Saturday=5, Sunday=6
        return False

    holidays = get_nyse_holidays(date.year)
    return date.date() not in [h.date() for h in holidays]

def get_last_n_business_days(n: int = 5) -> List[datetime]:
    """Get last N business days including today"""
    days = []
    current = datetime.now()

    while len(days) < n:
        if is_business_day(current):
            days.append(current)
        current -= timedelta(days=1)

    return days

def is_day_trade(open_order: Dict, close_order: Dict) -> bool:
    """Determine if two orders constitute a day trade"""
    return (
        open_order["symbol"] == close_order["symbol"]
        and open_order["date"].date() == close_order["date"].date()
        and open_order["side"] != close_order["side"]
    )

def count_day_trades(orders: List[Dict]) -> int:
    """
    Count day trades from order history

    Args:
        orders: List of orders with {symbol, side, date, ...}

    Returns:
        Number of day trades in last 5 business days
    """
    window = get_last_n_business_days(5)
    window_start = min(window).date()

    # Filter orders to window
    window_orders = [
        o for o in orders
        if o["date"].date() >= window_start
    ]

    # Sort by timestamp
    window_orders.sort(key=lambda x: x["date"])

    day_trades = []
    for i, buy in enumerate(window_orders):
        if buy["side"] not in ["buy", "buy_to_open"]:
            continue

        # Find matching sell on same day
        for sell in window_orders[i+1:]:
            if is_day_trade(buy, sell):
                day_trades.append({
                    "open": buy,
                    "close": sell,
                    "date": buy["date"].date()
                })
                break

    return len(day_trades)

def is_pdt_flagged(orders: List[Dict]) -> bool:
    """
    Check if account should be flagged as PDT

    PDT Criteria:
    1. 4+ day trades in last 5 business days
    2. Day trades > 6% of total trades
    """
    day_trade_count = count_day_trades(orders)
    total_trades = len(orders)

    if day_trade_count >= 4 and (day_trade_count / total_trades) > 0.06:
        return True

    return False
```

**Implementation in Tradier Client:**
```python
# Add to backend/app/services/tradier_client.py

class TradierClient(BrokerInterface):
    # ... existing methods ...

    def get_day_trade_count(self) -> int:
        """
        Get number of day trades in last 5 business days
        NOTE: Tradier doesn't provide this via API, must calculate manually
        """
        orders = self.get_orders()

        # Convert to format needed by count_day_trades()
        order_list = []
        for order in orders:
            order_list.append({
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "date": datetime.fromisoformat(order.get("create_date"))
            })

        return count_day_trades(order_list)

    def is_pdt_flagged(self) -> bool:
        """Check if account meets PDT criteria"""
        orders = self.get_orders()

        order_list = []
        for order in orders:
            order_list.append({
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "date": datetime.fromisoformat(order.get("create_date"))
            })

        return is_pdt_flagged(order_list)
```

### Cash Account vs Margin Account

**Why Cash Account = PDT Freedom:**

| Account Type | PDT Rules Apply? | Day Trade Limit | Buying Power |
|--------------|------------------|-----------------|--------------|
| **Cash** | ❌ NO | Unlimited | Cash available |
| **Margin** | ✅ YES | 3 (if \u003c$25k) | 2x-4x equity |

**Cash Account Limitations:**
- **T+1 Settlement:** Funds from sales settle next business day
- **Cannot trade unsettled funds:** Must wait for settlement
- **Good Faith Violations:** 3 in 12 months = 90-day restriction

**Cash Account Strategy:**
```
Capital Rotation for Continuous Trading:

Total Capital: $6,000
Split into 3 tranches: $2,000 each

Monday: Trade with Tranche A ($2,000)
Tuesday: Trade with Tranche B ($2,000) [A settling]
Wednesday: Trade with Tranche C ($2,000) [B settling]
Thursday: Trade with Tranche A ($2,000) [settled from Monday]
Friday: Trade with Tranche B ($2,000) [settled from Tuesday]

Result: Unlimited day trades, no PDT restrictions!
```

**Current PaiiD Configuration:**
```python
TRADIER_ACCOUNT_ID=6YB64299
Account Type: Cash  # ✅ NO PDT restrictions!
Day Trader Flag: False
Option Level: 1
```

---

## Data Sources & Market Data

### Real-Time Data Requirements

**For Options Day Trading:**
- ✅ **Real-time is MANDATORY**
- ❌ **15-minute delayed data is unusable**

**Why:** Options pricing moves second-by-second based on:
- Underlying price movement
- Implied volatility changes
- Time decay (theta)
- Greeks exposure

**Delayed data creates information asymmetry = real money loss**

### Data Provider Comparison

| Provider | Type | Cost | Latency | Coverage | Notes |
|----------|------|------|---------|----------|-------|
| **Tradier (included)** | Real-time consolidated | $10/month | ~100ms | Stocks + Options | ✅ Current, best value |
| **Alpaca IEX** | Real-time single exchange | $0 | ~50ms | Stocks + Options | Limited liquidity view |
| **Alpaca SIP** | Real-time consolidated | $99/month | ~10ms | Stocks + Options | For HFT only |
| **Polygon** | Historical + Real-time | $99-199/month | Varies | Comprehensive | Overkill for our use |
| **IEX Cloud** | N/A | N/A | N/A | N/A | ❌ Shut down Aug 2024 |

### Options-Specific Data

**What You Need:**
1. **Options Chain** - All strikes/expirations for underlying
2. **Greeks** - Delta, Gamma, Theta, Vega, Rho
3. **Implied Volatility** - Both individual and IV rank
4. **Bid/Ask Spreads** - Critical for multi-leg pricing
5. **Volume/Open Interest** - Liquidity indicators

**Current Provider (Tradier):**
```python
# Get options chain with Greeks
client = TradierClient()
chain = client.get_option_chains(
    symbol="SPY",
    expiration="2024-10-25"  # Optional filter
)

# Response includes:
{
    "options": {
        "option": [
            {
                "symbol": "SPY241025C450",
                "strike": 450.0,
                "bid": 2.45,
                "ask": 2.47,
                "last": 2.46,
                "volume": 1234,
                "open_interest": 5678,
                "greeks": {
                    "delta": 0.52,
                    "gamma": 0.03,
                    "theta": -0.15,
                    "vega": 0.08,
                    "rho": 0.02,
                    "phi": -0.01,
                    "bid_iv": 0.18,
                    "mid_iv": 0.185,
                    "ask_iv": 0.19
                }
            },
            # ... more options
        ]
    }
}
```

**Greek Calculations Provided by ORATS:** Tradier partners with ORATS (Options Research & Technology Services) for professional-grade Greeks and IV calculations.

### News API Integration

**Current Implementation:** News aggregator with multiple providers

**Providers Configured:**
1. **Alpha Vantage** - General news + sentiment
2. **Polygon** - Market-moving news
3. **Finnhub** - Company-specific news

**Files:**
```
backend/app/services/news/
├── base_provider.py           # Abstract interface
├── alpha_vantage_provider.py  # Alpha Vantage API
├── polygon_provider.py         # Polygon.io API
├── finnhub_provider.py         # Finnhub API
└── news_aggregator.py          # Combines all sources
```

**API Keys Required:**
```python
ALPHA_VANTAGE_API_KEY=V9EG1Z3TPETGAJO9
POLYGON_API_KEY=bOg6WM_KKgATQvpN_DLrdm8RHqxImrvE
FINNHUB_API_KEY=d3jv3d9r01qtciv0n8jgd3jv3d9r01qtciv0n8k0
```

---

## Cost Analysis

### Monthly Operating Costs

| Tier | Configuration | Monthly Cost | Annual Cost | Notes |
|------|---------------|--------------|-------------|-------|
| **Paper (Dev)** | Alpaca Paper + IEX | $0 | $0 | Free forever |
| **Live (Current)** | Tradier Pro | $10 | $120 | Best value for options |
| **Live (Premium)** | Tradier + Alpaca SIP | $109 | $1,308 | Only if need HFT data |
| **Dual-Broker** | Tradier + TD | $10+ | $120+ | Redundancy/failover |

### Transaction Costs (Live Trading)

**Tradier Pro:**
```
Stock/ETF Options: $0 commission
Regulatory Fees: ~$0.05-0.08 per contract (unavoidable)

Example Trade:
- Open 4-leg iron condor (SPY) = 4 contracts
- Close same condor = 4 contracts
- Total: 8 contracts × $0.065 avg = $0.52

Monthly (50 iron condors):
50 strategies × 8 contracts × $0.065 = $26 in regulatory fees
Plus $10 subscription = $36/month total

Annual: $432
```

**Index Options (SPX/NDX) Cost More:**
```
SPX Options (via Tradier):
- Commission: $0.35/contract
- Regulatory fees: ~$0.60/contract
- Total: ~$0.95/contract

Example SPX Iron Condor:
- 4 legs to open × $0.95 = $3.80
- 4 legs to close × $0.95 = $3.80
- Total per round trip: $7.60

For comparison:
- Stock options: $0.52 per iron condor
- Index options: $7.60 per iron condor
= 14.6x more expensive!

Recommendation: Stick to SPY/QQQ (stock options) instead of SPX/NDX
```

### ROI Breakeven Analysis

**To justify costs, need to beat:**
```
Tradier Pro: $10/month = 0.083% of $12,000 account
                       = 1% annual return

If trading with $12,000:
- Need to make >$120/year to break even
- That's $10/month profit minimum

Regulatory fees (at 50 trades/month):
- $26/month = $312/year
- On $12,000 = 2.6% annual return needed
- Total needed: 3.6% annual return to break even
```

**Conclusion:** Extremely low bar for profitability. Any positive-expectancy strategy will easily cover costs.

---

## Security & API Key Management

### Current API Keys Inventory

| Service | Key Type | Value (Masked) | Location | Expiration |
|---------|----------|----------------|----------|------------|
| **Tradier** | Production | `1tIR8iQL...pjkf` | Render env | Never |
| **Anthropic** | Production | `sk-ant-api03-gPJ...AAA` | Render + Vercel env | Never |
| **PaiiD API** | Internal | `tuGlKvrY...6lVo` | Render + Vercel env | Quarterly |
| **Alpha Vantage** | Free Tier | `V9EG1Z3T...AJO9` | Render env | Never |
| **Polygon** | Free Tier | `bOg6WM_K...mrvE` | Render env | Never |
| **Finnhub** | Free Tier | `d3jv3d9r...n8k0` | Render env | Never |

### Key Rotation Schedule

**Recommended Rotation:**

| Key Type | Frequency | Priority | Next Rotation |
|----------|-----------|----------|---------------|
| **Live Trading Keys** | Every 3 months | CRITICAL | January 2026 |
| **Paper Trading Keys** | Every 6 months | MEDIUM | April 2026 |
| **Internal API Token** | Every 3 months | HIGH | January 2026 |
| **News API Keys** | Annually | LOW | October 2026 |

**Event-Triggered Rotation (Immediate):**
- Employee/contractor departure
- Suspected compromise
- Keys accidentally committed to Git
- Security incident at provider
- Major infrastructure changes

### Storage Best Practices

**NEVER DO:**
- ❌ Hardcode in source code
- ❌ Commit to Git (even private repos)
- ❌ Store in plaintext files
- ❌ Share via email/Slack
- ❌ Use same keys across environments

**CURRENT (Acceptable for Development):**
- ✅ `.env` files (gitignored)
- ✅ Render environment variables (encrypted)
- ✅ Vercel environment variables (encrypted)

**PRODUCTION STANDARD (For Live Trading):**
- ✅ AWS Secrets Manager
- ✅ HashiCorp Vault
- ✅ Google Cloud Secret Manager
- ✅ Azure Key Vault

**Example AWS Secrets Manager Integration:**
```python
import boto3
import json

def get_secret(secret_name: str) -> dict:
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='us-east-1'
    )

    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage:
tradier_creds = get_secret('paiid/production/tradier')
api_key = tradier_creds['api_key']
account_id = tradier_creds['account_id']
```

### Security Monitoring

**Implement Automated Alerts:**
```python
class APIKeyMonitor:
    def detect_anomalies(self):
        current = self.get_current_metrics()
        baseline = self.baseline_metrics

        # Alert triggers:
        if current['request_rate'] > 2 * baseline['request_rate']:
            self.alert("Unusual API request rate")

        if current['failed_auth'] > 5:
            self.alert("Multiple failed authentication attempts")

        if current['geographic_anomaly']:
            self.alert("API access from unexpected location")

        if not self.is_market_hours() and current['trading_activity']:
            self.alert("Trading activity outside market hours")
```

**Quarterly Security Checklist:**
- [ ] Rotate production API keys
- [ ] Review API usage logs
- [ ] Verify keys in approved secret managers
- [ ] Scan repositories for accidental commits (GitGuardian)
- [ ] Update key rotation documentation
- [ ] Test emergency key revocation procedure
- [ ] Review access logs for anomalies

---

## Implementation Roadmap

### Phase 1: Current State (✅ COMPLETE)

**Status:** ✅ LIVE as of October 2025

**Implemented:**
- ✅ Tradier API client (`tradier_client.py`)
- ✅ Account data endpoint
- ✅ Positions endpoint
- ✅ Order execution
- ✅ Market data + options chain
- ✅ Real-time consolidated data
- ✅ Options Greeks via ORATS

**Configuration:**
```python
TRADING_MODE=paper
LIVE_BROKER=tradier
TRADIER_API_KEY=1tIR8iQL9epAwNcc7HSXPuCypjkf
TRADIER_ACCOUNT_ID=6YB64299
```

**Cost:** $10/month

---

### Phase 2: PDT Tracking (Next - 1 week)

**Goal:** Implement day trade counting for Tradier (doesn't provide via API)

**Tasks:**
1. Create `backend/app/services/pdt_tracker.py`
2. Implement business day calendar (NYSE holidays)
3. Implement day trade detection algorithm
4. Add `get_day_trade_count()` to Tradier client
5. Add `is_pdt_flagged()` to Tradier client
6. Create frontend warning UI when approaching limit
7. Add endpoint: `GET /api/account/pdt-status`

**Deliverables:**
- PDT tracking working for Tradier
- UI shows day trade count
- Warnings when approaching 4 trades

**Testing:**
```bash
curl -H "Authorization: Bearer <token>" \
  https://ai-trader-86a1.onrender.com/api/account/pdt-status

# Expected:
{
  "day_trade_count": 2,
  "is_pdt_flagged": false,
  "remaining_trades": 1,
  "window_start": "2025-10-06",
  "window_end": "2025-10-12"
}
```

---

### Phase 3: Broker Abstraction Layer (2-3 weeks)

**Goal:** Create flexible broker switching architecture

**Tasks:**
1. Create `backend/app/services/brokers/` directory
2. Define `BrokerInterface` abstract class
3. Refactor existing `TradierClient` to implement interface
4. Create `AlpacaBroker` for paper trading
5. Create `TDAmeritradeBroker` stub
6. Create `BrokerFactory` for runtime selection
7. Update all routers to use factory
8. Add configuration toggle in Settings UI

**Deliverables:**
- Can switch between Alpaca Paper and Tradier Live via config
- TD stub ready for when credentials available
- All existing functionality preserved

**Configuration:**
```python
# Paper trading
TRADING_MODE=paper
PAPER_BROKER=alpaca  # Uses Alpaca automatically

# Live trading
TRADING_MODE=live
LIVE_BROKER=tradier  # or "alpaca" or "tdameritrade"
```

---

### Phase 4: Alpaca Paper Integration (1 week)

**Goal:** Add free paper trading tier for development

**Tasks:**
1. Install `alpaca-py` package
2. Implement `AlpacaBroker` class
3. Add Alpaca credentials to `.env`
4. Test all methods (account, positions, orders, quotes)
5. Verify PDT status endpoints work
6. Create comparison tests (Alpaca Paper vs Tradier)

**Deliverables:**
- Working Alpaca Paper integration
- Can develop strategies for free
- PDT tracking works automatically (Alpaca provides it)

**Configuration:**
```python
# .env additions
ALPACA_PAPER_KEY=<your-key>
ALPACA_PAPER_SECRET=<your-secret>
ALPACA_API_BASE_URL=https://paper-api.alpaca.markets
```

---

### Phase 5: TD Ameritrade Integration (When Access Granted)

**Goal:** Add third broker for redundancy

**Tasks:**
1. Obtain TD Ameritrade/Schwab API credentials
2. Implement OAuth 2.0 refresh token flow
3. Implement `TDAmeritradeBroker` class
4. Test all methods
5. Add to broker factory
6. Update Settings UI to show 3 broker options

**Deliverables:**
- Runtime broker switching: Tradier ↔ TD
- Failover capability if one broker down
- Compare execution quality

**Configuration:**
```python
# When available
TD_CLIENT_ID=<your-client-id>
TD_REFRESH_TOKEN=<your-refresh-token>
TD_API_BASE_URL=https://api.tdameritrade.com/v1
```

---

### Phase 6: Advanced Features (Ongoing)

**Multi-Broker Portfolio Aggregation:**
- View positions across multiple brokers
- Unified P&L calculation
- Combined risk metrics

**Broker Health Monitoring:**
- Real-time status checks
- Automatic failover if primary broker down
- Alert notifications

**Execution Quality Comparison:**
- Track fill prices across brokers
- Measure slippage
- Optimize routing based on historical performance

---

## Summary & Quick Reference

### Current Production Configuration

```python
# Backend .env (Render)
TRADING_MODE=paper
LIVE_BROKER=tradier
TRADIER_API_KEY=1tIR8iQL9epAwNcc7HSXPuCypjkf
TRADIER_ACCOUNT_ID=6YB64299
TRADIER_USE_SANDBOX=false
TRADIER_API_BASE_URL=https://api.tradier.com/v1
```

**Status:** ✅ WORKING (verified October 12, 2025)

### Recommended Actions

**Immediate (Next Week):**
1. ✅ Verify Tradier integration working end-to-end
2. 🔄 Implement PDT tracking for Tradier
3. 🔄 Add day trade warning UI

**Short-term (Next Month):**
1. Create broker abstraction layer
2. Add Alpaca Paper for free development
3. Test broker switching

**Long-term (When Ready):**
1. Add TD Ameritrade when credentials available
2. Implement multi-broker portfolio view
3. Add execution quality comparison

### Key Contacts & Resources

**Tradier Support:**
- Email: techsupport@tradier.com
- API Docs: https://documentation.tradier.com
- Dashboard: https://dash.tradier.com

**Alpaca Support:**
- Docs: https://alpaca.markets/docs
- Forum: https://forum.alpaca.markets
- Status: https://status.alpaca.markets

**TD Ameritrade:**
- API: https://developer.tdameritrade.com
- Note: Migrating to Schwab platform (unified API coming)

---

**Document Version:** 1.0
**Last Updated:** October 12, 2025
**Next Review:** January 2026 (with API key rotation)

---

**END OF TRADING ARCHITECTURE GUIDE**
