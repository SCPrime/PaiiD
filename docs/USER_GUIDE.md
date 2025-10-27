# PaiiD User Guide

**Personal Artificial Intelligence Investment Dashboard**

Welcome to PaiiD - your AI-powered trading platform with an intuitive 10-stage radial workflow interface. This guide will help you navigate the platform and make the most of its powerful features.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [10-Stage Workflow](#10-stage-workflow)
   - [1. Morning Routine](#1-morning-routine)
   - [2. Active Positions](#2-active-positions)
   - [3. Execute Trade](#3-execute-trade)
   - [4. Research](#4-research)
   - [5. AI Recommendations](#5-ai-recommendations)
   - [6. P&L Dashboard](#6-pl-dashboard)
   - [7. News Review](#7-news-review)
   - [8. Strategy Builder](#8-strategy-builder)
   - [9. Backtesting](#9-backtesting)
   - [10. Settings](#10-settings)
4. [Key Features](#key-features)
5. [FAQ](#faq)
6. [Troubleshooting](#troubleshooting)
7. [Support](#support)

---

## Getting Started

### Account Setup

1. **Visit the Platform:**
   - Production: https://paiid-frontend.onrender.com
   - Or run locally (see Developer Guide)

2. **First-Time Setup:**
   - Click "Get Started" on the welcome screen
   - You'll be guided through AI-powered onboarding
   - Answer questions about your trading experience and preferences
   - No personal information is collected (privacy-first design)

3. **What Gets Stored:**
   - Trading preferences (risk tolerance, strategies)
   - Watchlist symbols
   - Custom settings
   - All data stored locally in your browser

4. **No Account Required:**
   - PaiiD is designed for single-user operation
   - No email, password, or personal data required
   - Your trading preferences stay on your device

### System Requirements

**Supported Browsers:**
- Chrome 90+ (recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

**Screen Resolution:**
- Minimum: 1024x768
- Recommended: 1920x1080 or higher
- Mobile: Responsive design works on tablets (iPad, Android)

**Internet Connection:**
- Stable internet connection required for real-time data
- Minimum 5 Mbps for smooth streaming

---

## Dashboard Overview

### Main Interface

The PaiiD dashboard features a unique radial menu design that organizes your trading workflow into 10 intuitive stages.

**Layout Components:**

1. **Header Bar** (Top)
   - PaiiD logo with live market data (SPY/QQQ)
   - System status indicator (green = healthy)
   - Current time and market hours

2. **Radial Menu** (Center)
   - 10 pie-wedge segments representing each workflow stage
   - Hover to preview each stage
   - Click to activate a workflow
   - Color-coded for easy navigation:
     - Green: Active workflow
     - Teal: Available workflows
     - Gray: Disabled workflows

3. **Workflow Content Area** (Right)
   - Displays content for selected workflow
   - Real-time data updates
   - Interactive charts and tables

4. **Split-Screen Mode**
   - Activated when you select a workflow
   - Left: Scaled radial menu (50% size)
   - Right: Full workflow interface
   - Draggable divider to adjust split

### Navigation

**Keyboard Shortcuts:**
- `1-9, 0`: Jump to workflow 1-10
- `Esc`: Return to full radial menu
- `Space`: Refresh current workflow data
- `?`: Show help overlay

**Mouse Navigation:**
- Hover over segments to preview
- Click segment to activate
- Scroll within workflow content
- Drag split divider to resize panels

---

## 10-Stage Workflow

### 1. Morning Routine

**Purpose:** Start your trading day with AI-powered briefings and system health checks.

**Features:**

- **Market Summary**
  - Pre-market movers (top gainers/losers)
  - Major indices (SPY, QQQ, DIA) performance
  - Overnight news highlights
  - Economic calendar events for the day

- **System Health Checks**
  - Backend API status
  - Market data connectivity (Tradier)
  - Trade execution readiness (Alpaca)
  - Real-time streaming status

- **Portfolio Overview**
  - Open positions summary
  - Overnight P&L changes
  - Upcoming earnings in your portfolio
  - Margin usage and buying power

- **AI Daily Brief**
  - Market regime assessment (bullish/bearish/neutral)
  - Recommended focus areas for the day
  - Risk alerts for your positions
  - Suggested watchlist additions

**How to Use:**

1. Open Morning Routine at market open (9:30 AM ET)
2. Review system health - ensure all systems are green
3. Read AI brief for market context
4. Check your positions for overnight gaps
5. Review economic calendar for potential catalysts
6. Set alerts for key levels

**Best Practices:**
- Run this workflow before placing any trades
- Check back after major news events
- Review at market close for end-of-day summary

---

### 2. Active Positions

**Purpose:** Monitor and manage your open positions in real-time.

**Features:**

- **Positions Table**
  - Symbol, quantity, entry price
  - Current price (real-time updates)
  - Market value and cost basis
  - Unrealized P&L ($ and %)
  - Side (long/short)
  - Quick actions (close position, add to watchlist)

- **Summary Cards** (Top of screen)
  - Total P&L: Combined unrealized profit/loss
  - Cost Basis: Total capital deployed
  - Market Value: Current portfolio value
  - Color-coded: Green (profit), Red (loss)

- **Position Details** (Click any row)
  - Trade history for that position
  - Average entry price breakdown
  - Real-time quote with bid/ask
  - Technical chart with entry points
  - Exit strategy suggestions

- **Auto-Refresh**
  - Updates every 30 seconds during market hours
  - Pause button to freeze data
  - Manual refresh button

**How to Use:**

1. **Monitor Positions:**
   - Watch P&L changes in real-time
   - Identify winners and losers
   - Check if positions are near stop-loss levels

2. **Close Position:**
   - Click row to expand details
   - Click "Close Position" button
   - Confirm order type (market/limit)
   - Order submitted to Alpaca Paper Trading

3. **Add Stop-Loss:**
   - Click position row
   - Select "Add Stop-Loss"
   - Set trigger price
   - Choose order type

4. **View Trade History:**
   - Click position to expand
   - See all entries/exits for that symbol
   - Calculate cost basis

**Example Scenario:**

You bought 100 shares of AAPL at $150.00 yesterday. Current price is $155.00.

```
| Symbol | Qty | Entry  | Current | Mkt Value | Cost   | P&L    | P&L %  | Side |
|--------|-----|--------|---------|-----------|--------|--------|--------|------|
| AAPL   | 100 | $150.00| $155.00 | $15,500   | $15,000| +$500  | +3.33% | Long |
```

Summary cards show:
- Total P&L: **+$500** (green)
- Cost Basis: **$15,000**
- Market Value: **$15,500**

---

### 3. Execute Trade

**Purpose:** Place buy and sell orders with real-time market data and intelligent order validation.

**Features:**

- **Order Entry Form**
  - Symbol input with auto-complete
  - Quantity selector
  - Side: Buy or Sell
  - Order type: Market, Limit, Stop, Stop-Limit
  - Time-in-force: Day, GTC, IOC, FOK
  - Real-time price quote display

- **Order Types Explained**

  **Market Order:**
  - Executes immediately at best available price
  - Guaranteed fill, price not guaranteed
  - Best for liquid stocks with tight spreads
  - Example: "Buy 10 AAPL at market"

  **Limit Order:**
  - Executes only at specified price or better
  - Price guaranteed, fill not guaranteed
  - Best for illiquid stocks or specific entry points
  - Example: "Buy 10 AAPL at $150.00 or lower"

  **Stop Order:**
  - Becomes market order when trigger price hit
  - Used for stop-losses or breakout entries
  - Example: "Sell 10 AAPL if price drops to $145.00"

  **Stop-Limit Order:**
  - Becomes limit order when trigger price hit
  - More control but risk of no fill
  - Example: "Sell 10 AAPL between $145-$144"

- **Pre-Trade Validation**
  - Buying power check
  - Position size warnings
  - Risk assessment (% of portfolio)
  - Duplicate order detection

- **Order Templates** (Coming Soon)
  - Save frequently used orders
  - One-click execution
  - Multi-symbol orders

**How to Use:**

1. **Place Market Order (Fastest):**
   ```
   Symbol: AAPL
   Quantity: 10
   Side: Buy
   Type: Market
   Time-in-Force: Day
   ```
   - Click "Submit Order"
   - Confirm execution
   - Order sent to Alpaca Paper Trading

2. **Place Limit Order (Price Control):**
   ```
   Symbol: AAPL
   Quantity: 10
   Side: Buy
   Type: Limit
   Limit Price: $150.00
   Time-in-Force: GTC (Good-til-Canceled)
   ```
   - Order will only fill at $150.00 or better
   - Remains open until filled or canceled

3. **Set Stop-Loss (Risk Management):**
   ```
   Symbol: AAPL (you own 10 shares at $150)
   Quantity: 10
   Side: Sell
   Type: Stop
   Stop Price: $145.00
   ```
   - If AAPL drops to $145, order triggers
   - Becomes market sell order
   - Limits loss to $5/share = $50 total

**Order Status:**
- **Submitted:** Order sent to broker
- **Pending:** Awaiting execution
- **Filled:** Order executed
- **Partially Filled:** Some shares filled
- **Canceled:** Order canceled
- **Rejected:** Order rejected (insufficient funds, invalid symbol, etc.)

**Best Practices:**
- Always check buying power before placing orders
- Use limit orders for illiquid stocks
- Set stop-losses for risk management
- Review order before submitting
- Monitor order status in Active Positions

**Example Trade Flow:**

1. Research shows AAPL bullish setup
2. Open Execute Trade workflow
3. Enter: Symbol=AAPL, Qty=10, Side=Buy, Type=Limit, Price=$150
4. System shows: "Buying power: $100,000 available"
5. Submit order
6. Order appears in Active Positions as "Pending"
7. When filled, position shows in positions table

---

### 4. Research

**Purpose:** Analyze stocks using real-time market data, technical indicators, and AI-powered insights.

**Features:**

- **Market Scanner**
  - Filter stocks by criteria:
    - Volume: > 1M, > 5M, > 10M shares
    - Price: $0-$10, $10-$50, $50-$200, $200+
    - % Change: > +5%, > +10%, < -5%, < -10%
    - Sector: Technology, Healthcare, Finance, etc.
  - Results update in real-time
  - Click symbol to view detailed analysis

- **Technical Analysis**
  - Interactive price charts (1m, 5m, 15m, 1h, 1d timeframes)
  - Technical indicators:
    - Moving Averages (SMA, EMA)
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Bollinger Bands
    - Volume analysis
  - Pattern recognition (AI-powered):
    - Head and shoulders
    - Double top/bottom
    - Triangles (ascending, descending, symmetric)
    - Flags and pennants
    - Cup and handle

- **Fundamental Data**
  - Market cap and volume
  - P/E ratio and EPS
  - Revenue and earnings growth
  - Analyst ratings and price targets
  - Earnings calendar

- **Sentiment Analysis**
  - Social media sentiment score
  - News sentiment (bullish/bearish/neutral)
  - Analyst sentiment distribution
  - Institutional ownership trends

- **Watchlist Management**
  - Add symbols to watchlist
  - Organize by custom categories
  - Set price alerts
  - Export watchlist

**How to Use:**

1. **Find Opportunities with Scanner:**
   ```
   Filters:
   - Volume: > 5M shares
   - % Change: > +5%
   - Sector: Technology
   ```
   - Click "Scan"
   - Review results sorted by % change
   - Click promising symbols for details

2. **Analyze a Stock:**
   - Enter symbol (e.g., AAPL)
   - View chart with indicators
   - Check RSI: > 70 = overbought, < 30 = oversold
   - Review MACD for trend direction
   - Read AI pattern detection results

3. **Set Price Alert:**
   - Click "Add Alert" on chart
   - Set price level (e.g., $160.00)
   - Choose notification method
   - Alert triggers when price reached

4. **Add to Watchlist:**
   - Click "Add to Watchlist"
   - Choose category (e.g., "Tech Stocks")
   - Symbol saved for monitoring

**Example Research Workflow:**

1. Run scanner for high-volume gainers
2. Found: NVDA +8.5% on 50M volume
3. Open NVDA chart, see ascending triangle pattern
4. AI confirms: "Bullish ascending triangle, 82% confidence"
5. RSI at 65 (not overbought yet)
6. MACD showing bullish cross
7. Add to watchlist, set alert at breakout level ($500)
8. Decision: Prepare limit buy order at $495

**Technical Indicator Guide:**

- **RSI (14-period):**
  - > 70: Overbought (potential reversal)
  - 30-70: Normal range
  - < 30: Oversold (potential bounce)

- **MACD:**
  - Line above signal: Bullish
  - Line below signal: Bearish
  - Crossovers: Trend change signals

- **Moving Averages:**
  - Price above 50-day MA: Bullish
  - Price below 50-day MA: Bearish
  - Golden cross (50 > 200): Very bullish
  - Death cross (50 < 200): Very bearish

---

### 5. AI Recommendations

**Purpose:** Get AI-powered trading suggestions based on machine learning analysis of market data.

**Features:**

- **Recommendation Feed**
  - Real-time AI-generated trade ideas
  - Confidence score (0-100%)
  - Action: Buy, Sell, Hold
  - Entry price and quantity suggestions
  - Target price (take-profit level)
  - Stop-loss price (risk management)
  - Rationale explanation
  - Risk rating: Low, Moderate, High

- **Recommendation Details**
  - Technical analysis summary
  - Sentiment analysis results
  - Pattern recognition findings
  - Market regime context
  - Similar historical setups
  - Probability of profit estimate

- **Filtering Options**
  - Risk level: Show only low/moderate/high risk
  - Confidence: Minimum confidence threshold
  - Action: Buy only, Sell only, or All
  - Watchlist: Only symbols in your watchlist

- **One-Click Execution** (Coming Soon)
  - Accept recommendation
  - Auto-fill order form
  - Review and submit

**How to Use:**

1. **Review Recommendations:**
   - Open AI Recommendations workflow
   - See list of current suggestions
   - Sorted by confidence score (highest first)

2. **Analyze a Recommendation:**
   - Click recommendation card to expand
   - Read rationale and technical details
   - Check confidence score and risk rating
   - Review entry, target, and stop-loss prices

3. **Act on Recommendation:**
   - If confident, click "Execute"
   - Review pre-filled order form
   - Adjust quantity if needed
   - Submit order

4. **Track Performance:**
   - Save recommendation for later review
   - Track actual vs predicted performance
   - Learn which recommendation types work best

**Example Recommendation:**

```
Symbol: AAPL
Action: BUY
Confidence: 85%
Risk Rating: Moderate

Entry: $155.00
Target: $162.00 (+4.5%)
Stop-Loss: $150.00 (-3.2%)

Rationale:
"Strong bullish divergence on RSI while price consolidating.
Volume increasing on up days. MACD showing bullish cross.
Price broke above 50-day moving average with confirmation.
Similar setups in AAPL history resulted in 72% win rate."

Technical Indicators:
- RSI: 62 (bullish momentum)
- MACD: Bullish cross confirmed
- Volume: +35% above 20-day average
- Pattern: Ascending triangle (breakout imminent)

Sentiment:
- News: 78% positive (earnings beat)
- Social: 65% bullish mentions
- Analyst: 85% buy ratings
```

**Understanding Confidence Scores:**

- **90-100%:** Very High Confidence
  - Strong technical and sentiment alignment
  - Multiple confirming signals
  - Historical success rate > 75%

- **75-89%:** High Confidence
  - Good technical setup
  - Positive sentiment
  - Historical success rate 60-75%

- **60-74%:** Moderate Confidence
  - Decent setup with some risks
  - Mixed sentiment
  - Historical success rate 50-60%

- **< 60%:** Low Confidence
  - Weak setup or conflicting signals
  - Not recommended for most traders

**Best Practices:**
- Only act on recommendations with 75%+ confidence
- Always set stop-losses as recommended
- Don't chase after price runs past entry level
- Review past recommendations to calibrate AI
- Use as one input in your decision process

---

### 6. P&L Dashboard

**Purpose:** Track your trading performance with detailed analytics and historical data.

**Features:**

- **Performance Summary**
  - Total P&L (all-time)
  - Daily P&L
  - Weekly P&L
  - Monthly P&L
  - Year-to-date P&L
  - Color-coded: Green (profit), Red (loss)

- **Key Metrics**
  - Win Rate: % of profitable trades
  - Average Win: Average profit per winning trade
  - Average Loss: Average loss per losing trade
  - Profit Factor: Gross profit / Gross loss
  - Sharpe Ratio: Risk-adjusted returns
  - Max Drawdown: Largest peak-to-trough decline
  - Recovery Factor: Net profit / Max drawdown

- **Equity Curve Chart**
  - Interactive chart showing account value over time
  - Overlay trade markers (wins/losses)
  - Zoom to specific date ranges
  - Compare to benchmark (SPY)

- **Trade History Table**
  - All closed trades
  - Symbol, entry/exit dates, P&L
  - Hold time, % return
  - Tags (strategy used)
  - Filter by date, symbol, strategy

- **Performance by Strategy**
  - Compare different trading strategies
  - Win rate and profitability by strategy
  - Identify best-performing approaches

- **Performance by Symbol**
  - Which stocks are most profitable
  - Which stocks are consistent losers
  - Win rate by symbol

- **Calendar View**
  - Daily P&L heat map
  - Best trading days of week
  - Identify patterns in performance

**How to Use:**

1. **Check Today's Performance:**
   - Daily P&L card shows: **+$1,250 (+1.25%)**
   - Green indicates profitable day
   - Click to see breakdown by trade

2. **Analyze Win Rate:**
   - Win Rate: **62%** (35 wins / 21 losses)
   - Target: Maintain above 50%
   - If below 50%, review losing trades

3. **Review Equity Curve:**
   - Smooth upward slope = consistent gains
   - Sharp drops = need better risk management
   - Compare to SPY to see if outperforming

4. **Identify Best Strategy:**
   ```
   Strategy Performance:
   - Momentum Breakout: 68% win rate, +$5,000
   - Mean Reversion: 55% win rate, +$2,000
   - AI Recommendations: 72% win rate, +$8,000
   ```
   - Focus on AI Recommendations (best performer)

5. **Find Problem Areas:**
   - Losses on Fridays? Avoid trading Fridays
   - Losses on specific symbols? Avoid those stocks
   - Large drawdown in September? Review what went wrong

**Example Dashboard View:**

```
PERFORMANCE SUMMARY
┌─────────────────────────────────────────────────────┐
│ Total P&L:      +$15,000 (+15.0%) ✓                │
│ Daily P&L:      +$1,250  (+1.25%) ✓                │
│ Weekly P&L:     +$3,500  (+3.50%) ✓                │
│ Monthly P&L:    +$8,000  (+8.00%) ✓                │
└─────────────────────────────────────────────────────┘

KEY METRICS
┌─────────────────────────────────────────────────────┐
│ Win Rate:         62% (35W / 21L)                   │
│ Avg Win:          $450                              │
│ Avg Loss:         -$280                             │
│ Profit Factor:    1.85                              │
│ Sharpe Ratio:     1.72                              │
│ Max Drawdown:     -8.5% (-$8,500)                   │
└─────────────────────────────────────────────────────┘

RECENT TRADES
┌────────┬──────────┬──────────┬─────────┬─────────┐
│ Symbol │ Entry    │ Exit     │ Hold    │ P&L     │
├────────┼──────────┼──────────┼─────────┼─────────┤
│ AAPL   │ $150.00  │ $155.00  │ 2 days  │ +$500   │
│ MSFT   │ $300.00  │ $308.00  │ 3 days  │ +$400   │
│ TSLA   │ $245.00  │ $240.00  │ 1 day   │ -$250   │
└────────┴──────────┴──────────┴─────────┴─────────┘
```

**Metric Definitions:**

- **Profit Factor:**
  - Gross profit / Gross loss
  - > 2.0 = Excellent
  - 1.5-2.0 = Good
  - 1.0-1.5 = Acceptable
  - < 1.0 = Losing system

- **Sharpe Ratio:**
  - Risk-adjusted return metric
  - > 2.0 = Excellent
  - 1.0-2.0 = Good
  - 0.5-1.0 = Acceptable
  - < 0.5 = Poor

- **Max Drawdown:**
  - Largest peak-to-trough decline
  - Lower is better
  - > -20% = Need better risk management
  - -10% to -20% = Acceptable
  - < -10% = Excellent

**Best Practices:**
- Review P&L daily to stay aware of performance
- Aim for 55%+ win rate (compensate with good R:R)
- Track performance by strategy to optimize
- Use drawdowns as learning opportunities
- Compare to SPY to measure skill vs market

---

### 7. News Review

**Purpose:** Stay informed with AI-curated market news and sentiment analysis.

**Features:**

- **News Feed**
  - Latest market news articles
  - Filter by symbol, sector, or topic
  - Sorted by relevance and recency
  - Source credibility indicators
  - Article summaries

- **Sentiment Analysis**
  - AI-powered sentiment: Bullish, Bearish, Neutral
  - Sentiment score: -100 (very bearish) to +100 (very bullish)
  - Key topics extracted
  - Impact assessment: High, Medium, Low

- **News Alerts**
  - Breaking news notifications
  - Earnings announcements
  - SEC filings
  - Analyst upgrades/downgrades
  - Economic data releases

- **Trending Topics**
  - Most discussed topics today
  - Trending stocks in news
  - Sector rotation themes
  - Macro trends

- **Personalized Feed**
  - News for your watchlist symbols
  - News for your open positions
  - Topics matching your preferences

**How to Use:**

1. **Read Latest News:**
   - Open News Review workflow
   - Scan headlines and summaries
   - Click article for full content
   - Check sentiment score

2. **Filter by Symbol:**
   - Enter symbol (e.g., AAPL)
   - See all news mentioning AAPL
   - Review sentiment trend over time

3. **Identify Market Themes:**
   - Check "Trending Topics"
   - See: "AI Technology" trending (+45 articles)
   - Related symbols: NVDA, MSFT, GOOGL
   - Consider sector rotation opportunity

4. **Set News Alerts:**
   - Click "Alerts" button
   - Choose: "Alert me for AAPL earnings"
   - Notification sent when news published

**Example News Article:**

```
TITLE:
"Apple Announces Record Quarterly Earnings, Beats Estimates"

SUMMARY:
Apple reported Q3 earnings of $1.52/share vs $1.41 expected,
driven by strong iPhone sales and services revenue growth.
Revenue up 8% year-over-year. Stock up 3% after-hours.

SENTIMENT: Bullish (85/100) ✓
SOURCE: Reuters (A+ credibility)
PUBLISHED: 2025-10-27 16:05 ET
SYMBOLS: AAPL, suppliers (AAPL ecosystem)

KEY TOPICS:
- Earnings beat
- iPhone demand
- Services growth
- Guidance raised

IMPACT: HIGH
Likely to drive AAPL higher tomorrow. Consider related stocks.
```

**Interpreting Sentiment:**

- **Very Bullish (75-100):**
  - Strongly positive news
  - Likely near-term price increase
  - Consider long positions

- **Bullish (50-74):**
  - Positive news
  - Mild upward pressure
  - Monitor for confirmation

- **Neutral (25-49):**
  - Mixed or factual news
  - No clear directional bias
  - Wait for clarity

- **Bearish (-50 to -74):**
  - Negative news
  - Mild downward pressure
  - Consider reducing exposure

- **Very Bearish (-75 to -100):**
  - Strongly negative news
  - Likely near-term price decrease
  - Consider short positions or exit longs

**Best Practices:**
- Check news feed before placing trades
- Don't trade on headlines alone - verify with technicals
- Pay attention to news source credibility
- Look for confirmation across multiple sources
- Use sentiment as one factor in decision process

---

### 8. Strategy Builder

**Purpose:** Create, test, and deploy custom trading strategies using a visual rule builder.

**Features:**

- **Visual Rule Builder**
  - Drag-and-drop interface
  - No coding required
  - Build complex strategies with simple rules
  - Real-time validation

- **Rule Components**
  - **Indicators:** RSI, MACD, Moving Averages, Bollinger Bands
  - **Conditions:** Greater than, Less than, Crosses above/below
  - **Values:** Numbers, Other indicators, Dynamic values
  - **Logic:** AND, OR, NOT operators

- **Entry/Exit Rules**
  - Define entry conditions
  - Set exit conditions (profit target, stop-loss, time-based)
  - Position sizing rules
  - Risk management parameters

- **Strategy Templates**
  - Pre-built strategy templates:
    - Momentum Breakout
    - Mean Reversion
    - Trend Following
    - Support/Resistance
    - Moving Average Crossover
  - Customize templates to your needs

- **Live Validation**
  - Test strategy on historical data
  - See performance metrics before deploying
  - Identify issues before going live

**How to Use:**

1. **Create New Strategy:**
   - Click "New Strategy"
   - Name it: "My Momentum Strategy"
   - Choose strategy type: "Technical"

2. **Define Entry Rules:**
   ```
   Entry when ALL conditions met:
   - RSI(14) > 60
   - Price crosses above 50-day SMA
   - Volume > 1.5x average volume
   ```
   - Drag RSI indicator to canvas
   - Set condition: "Greater than 60"
   - Add more conditions with AND operator

3. **Define Exit Rules:**
   ```
   Exit when ANY condition met:
   - Profit target: +5%
   - Stop-loss: -2%
   - Time: Hold max 5 days
   - RSI < 40 (momentum fading)
   ```
   - Set profit target and stop-loss
   - Add time-based exit
   - Add indicator-based exit

4. **Set Position Sizing:**
   ```
   Position Size:
   - Max 10% of portfolio per trade
   - Risk max 2% of portfolio per trade
   - Auto-calculate shares based on stop-loss
   ```

5. **Backtest Strategy:**
   - Click "Backtest"
   - Select date range: 2024-01-01 to 2025-10-27
   - View results:
     - Win rate: 68%
     - Sharpe ratio: 1.85
     - Max drawdown: -8.5%
   - If satisfied, save and deploy

6. **Deploy Strategy:**
   - Click "Activate"
   - Strategy runs in background
   - Generates trade signals automatically
   - Review signals before execution

**Example Strategy - Momentum Breakout:**

```
STRATEGY NAME: Momentum Breakout
TYPE: Technical
ACTIVE: Yes

ENTRY RULES (ALL must be true):
┌──────────────────────────────────────────────────┐
│ 1. RSI(14) > 60                                  │
│    └─ Momentum building                          │
│                                                   │
│ 2. Price crosses above 50-day SMA                │
│    └─ Uptrend confirmed                          │
│                                                   │
│ 3. Volume > 1.5x 20-day average                  │
│    └─ Institutional buying                       │
│                                                   │
│ 4. MACD line > Signal line                       │
│    └─ Bullish momentum confirmed                 │
└──────────────────────────────────────────────────┘

EXIT RULES (ANY can trigger):
┌──────────────────────────────────────────────────┐
│ 1. Profit Target: +5%                            │
│    └─ Take profit when hit                       │
│                                                   │
│ 2. Stop-Loss: -2%                                │
│    └─ Limit losses                               │
│                                                   │
│ 3. Time Exit: 5 days                             │
│    └─ Don't hold too long                        │
│                                                   │
│ 4. RSI(14) < 40                                  │
│    └─ Momentum fading, exit                      │
└──────────────────────────────────────────────────┘

POSITION SIZING:
- Max 10% of portfolio per trade
- Risk 2% of portfolio (stop-loss based)

BACKTEST RESULTS (2024-2025):
┌──────────────────────────────────────────────────┐
│ Total Trades:     45                             │
│ Win Rate:         68% (31W / 14L)                │
│ Avg Win:          +5.2%                          │
│ Avg Loss:         -2.1%                          │
│ Profit Factor:    2.15                           │
│ Sharpe Ratio:     1.85                           │
│ Max Drawdown:     -8.5%                          │
│ Total Return:     +24.5%                         │
└──────────────────────────────────────────────────┘
```

**Strategy Types:**

- **Momentum:**
  - Buy strength, sell weakness
  - Follow trends
  - Examples: Breakouts, new highs

- **Mean Reversion:**
  - Buy oversold, sell overbought
  - Expect return to average
  - Examples: RSI < 30, Bollinger Band bounces

- **Trend Following:**
  - Identify and follow strong trends
  - Stay in trades longer
  - Examples: Moving average crossovers

- **Volatility:**
  - Trade based on volatility expansion/contraction
  - Examples: Bollinger Band squeezes

**Best Practices:**
- Start with simple strategies (3-5 rules max)
- Always backtest before deploying live
- Use appropriate position sizing (2% risk max)
- Monitor strategy performance weekly
- Disable strategies during drawdowns
- Combine multiple strategies for diversification

---

### 9. Backtesting

**Purpose:** Test trading strategies on historical data to evaluate performance before risking real capital.

**Features:**

- **Historical Data**
  - Access years of market data
  - Minute, hourly, daily bars
  - Includes splits, dividends
  - Real bid/ask spreads for accuracy

- **Realistic Simulation**
  - Slippage modeling
  - Commission costs
  - Realistic fill prices
  - Proper position sizing
  - Margin calculations

- **Performance Metrics**
  - Total return (% and $)
  - Sharpe ratio
  - Sortino ratio
  - Max drawdown
  - Win rate
  - Profit factor
  - Average trade duration
  - Risk-adjusted returns

- **Equity Curve**
  - Visual representation of account growth
  - Drawdown visualization
  - Trade markers (wins/losses)
  - Benchmark comparison (SPY)

- **Trade-by-Trade Analysis**
  - See every simulated trade
  - Entry/exit prices and dates
  - P&L per trade
  - Hold time
  - Why trade was entered/exited

- **Optimization** (Advanced)
  - Find best parameter combinations
  - Walk-forward analysis
  - Out-of-sample testing
  - Prevent overfitting

**How to Use:**

1. **Select Strategy to Test:**
   - Choose existing strategy from list
   - Or create new strategy in Strategy Builder

2. **Configure Backtest:**
   ```
   Configuration:
   - Strategy: Momentum Breakout
   - Symbols: AAPL, MSFT, GOOGL, TSLA
   - Date Range: 2024-01-01 to 2025-10-27
   - Initial Capital: $100,000
   - Commission: $0/trade (paper trading)
   - Slippage: 0.05% (realistic)
   ```

3. **Run Backtest:**
   - Click "Run Backtest"
   - Wait 5-30 seconds for completion
   - View results

4. **Analyze Results:**
   ```
   BACKTEST RESULTS
   ────────────────────────────────────────
   Initial Capital:    $100,000
   Final Equity:       $124,500
   Total Return:       +24.5%
   Total Trades:       45
   Win Rate:           68%
   Profit Factor:      2.15
   Sharpe Ratio:       1.85
   Max Drawdown:       -8.5%
   Avg Trade:          +$544
   Avg Win:            +$780
   Avg Loss:           -$315
   ```

5. **Review Equity Curve:**
   - Smooth curve = consistent strategy
   - Sharp drops = need better risk management
   - Compare to SPY benchmark:
     - Strategy: +24.5%
     - SPY: +15.2%
     - **Outperformance: +9.3%** ✓

6. **Examine Individual Trades:**
   ```
   Trade #1:
   - Symbol: AAPL
   - Entry: 2024-01-15 @ $150.00 (RSI=62, price above SMA)
   - Exit:  2024-01-20 @ $157.50 (5-day time exit)
   - Hold:  5 days
   - P&L:   +$750 (+5.0%)

   Trade #2:
   - Symbol: MSFT
   - Entry: 2024-02-01 @ $300.00 (RSI=65, volume spike)
   - Exit:  2024-02-02 @ $294.00 (stop-loss hit)
   - Hold:  1 day
   - P&L:   -$300 (-2.0%)
   ```

7. **Decision:**
   - Results look good? Deploy strategy live
   - Results poor? Refine strategy and re-test
   - Mixed results? Test on more symbols or longer timeframe

**Interpreting Results:**

**Good Backtest:**
- Win rate > 55%
- Sharpe ratio > 1.5
- Max drawdown < -15%
- Profit factor > 1.75
- Smooth equity curve
- Outperforms benchmark

**Poor Backtest:**
- Win rate < 45%
- Sharpe ratio < 1.0
- Max drawdown > -25%
- Profit factor < 1.25
- Erratic equity curve
- Underperforms benchmark

**Warning Signs (Overfitting):**
- Win rate > 90% (too good to be true)
- Very few trades (not enough data)
- Strategy only works on specific symbols
- Performance degrades on out-of-sample data

**Best Practices:**
- Test on at least 100 trades for statistical significance
- Use realistic commission and slippage
- Test on multiple symbols and timeframes
- Walk-forward analysis (test on future data)
- Don't optimize until perfect - accept some losses
- Paper trade strategy before going live
- Monitor live performance vs backtest regularly

**Example Backtest Comparison:**

```
Strategy A: Momentum Breakout
- Return: +24.5%
- Sharpe: 1.85
- Max DD: -8.5%
- Win Rate: 68%
- Verdict: GOOD - Deploy ✓

Strategy B: Mean Reversion
- Return: +12.0%
- Sharpe: 1.20
- Max DD: -18.5%
- Win Rate: 52%
- Verdict: ACCEPTABLE - Paper trade first

Strategy C: Random Entry
- Return: -5.5%
- Sharpe: 0.45
- Max DD: -25.0%
- Win Rate: 42%
- Verdict: POOR - Do not deploy ✗
```

---

### 10. Settings

**Purpose:** Configure platform preferences, trading parameters, and account settings.

**Features:**

- **Trading Preferences**
  - Default order type (market/limit)
  - Default time-in-force (day/GTC)
  - Risk tolerance level
  - Max position size (% of portfolio)
  - Max loss per trade (% or $)

- **Risk Management**
  - Portfolio-level stop-loss
  - Position-level stop-loss defaults
  - Max drawdown threshold
  - Auto-liquidation settings
  - Daily loss limit

- **Notification Settings**
  - Order fill notifications
  - Price alerts
  - News alerts
  - AI recommendation alerts
  - Email, SMS, or in-app

- **Display Preferences**
  - Theme: Dark mode (default) or Light mode
  - Chart timeframe defaults
  - Table column customization
  - Decimal places for prices
  - Currency format

- **Data & Privacy**
  - Clear local storage
  - Export trading data
  - Delete account data
  - Privacy preferences

- **API Connections**
  - Tradier API status
  - Alpaca API status
  - Re-authenticate if needed
  - Test connections

- **Help & Support**
  - User guide (this document)
  - Video tutorials
  - Keyboard shortcuts
  - Contact support

**How to Use:**

1. **Set Risk Parameters:**
   ```
   Risk Management:
   - Max Position Size: 10% of portfolio
   - Max Loss Per Trade: 2% of portfolio
   - Daily Loss Limit: $1,000
   - Auto-liquidate at: -20% portfolio drawdown
   ```
   - These protect you from catastrophic losses

2. **Configure Default Orders:**
   ```
   Default Order Settings:
   - Order Type: Limit (safer)
   - Time-in-Force: Day (don't hold overnight)
   - Limit Offset: -0.02% (slight discount)
   ```
   - Saves time when placing orders

3. **Enable Notifications:**
   ```
   Notifications:
   ✓ Order fills (immediate)
   ✓ AI recommendations (daily digest)
   ✓ Price alerts (when triggered)
   ✗ News alerts (too noisy)
   ```

4. **Customize Display:**
   ```
   Display Settings:
   - Theme: Dark mode ✓
   - Default Chart: 1-day bars
   - Positions Table: Show P&L %, Hide fees
   - Price Format: 2 decimal places
   ```

5. **Export Data:**
   - Click "Export Trading Data"
   - Choose format: CSV or JSON
   - Select date range
   - Download file
   - Use for tax reporting or external analysis

**Recommended Settings for New Users:**

```
RISK MANAGEMENT (Conservative)
- Risk Tolerance: Moderate
- Max Position Size: 5% of portfolio
- Max Loss Per Trade: 1% of portfolio
- Daily Loss Limit: $500
- Auto-stop at: -10% drawdown

DEFAULT ORDERS
- Order Type: Limit
- Time-in-Force: Day
- Always review before submit: ✓

NOTIFICATIONS
- Order fills: ✓
- AI recommendations: ✓ (confidence > 75%)
- Price alerts: ✓
- News alerts: ✗

DISPLAY
- Theme: Dark mode
- Chart: 1-day candlesticks
- Auto-refresh: Every 30 seconds
```

**Recommended Settings for Experienced Traders:**

```
RISK MANAGEMENT (Moderate)
- Risk Tolerance: Aggressive
- Max Position Size: 10% of portfolio
- Max Loss Per Trade: 2% of portfolio
- Daily Loss Limit: $2,000
- Auto-stop at: -20% drawdown

DEFAULT ORDERS
- Order Type: Market (faster execution)
- Time-in-Force: GTC
- Review before submit: ✗ (one-click execution)

NOTIFICATIONS
- Order fills: ✓
- AI recommendations: ✓ (confidence > 80%)
- Price alerts: ✓
- News alerts: ✓ (high impact only)

DISPLAY
- Theme: Dark mode
- Chart: 5-minute bars (day trading)
- Auto-refresh: Every 5 seconds
```

---

## Key Features

### Real-Time Market Data

- **Source:** Tradier API (NO delay)
- **Data Types:**
  - Real-time quotes (bid, ask, last, volume)
  - Historical bars (1m, 5m, 15m, 1h, 1d)
  - Options chains with Greeks
  - Market indices (SPY, QQQ, DIA)
  - News and earnings data

- **Update Frequency:**
  - Quotes: Real-time (sub-second during market hours)
  - Positions: 30-second auto-refresh
  - Charts: On-demand or streaming

### Paper Trading

- **Broker:** Alpaca Paper Trading API
- **Account Type:** Paper (simulated, NO real money)
- **Features:**
  - Realistic order execution
  - Simulated fills based on real market prices
  - Track P&L as if trading real money
  - Practice without financial risk

- **Limitations:**
  - Cannot withdraw funds (it's simulated)
  - Some advanced order types unavailable
  - No real broker fees or commissions

### AI-Powered Intelligence

- **Technology:** Anthropic Claude API
- **Capabilities:**
  - Market sentiment analysis
  - News article summarization
  - Trade idea generation
  - Portfolio risk assessment
  - Pattern recognition in charts
  - Natural language queries

- **Machine Learning:**
  - Chart pattern detection (head & shoulders, triangles, etc.)
  - Market regime classification (bullish, bearish, neutral)
  - Predictive analytics (price forecasting)
  - Ensemble models for robust predictions

### Security & Privacy

- **No Personal Data:**
  - No email, password, or name required
  - No financial information stored remotely
  - All preferences stored locally in browser

- **API Security:**
  - JWT token authentication
  - CSRF protection on state-changing operations
  - Rate limiting to prevent abuse
  - Secure HTTPS connections

- **Data Privacy:**
  - Trade data never shared with third parties
  - Anonymous usage analytics only
  - Full control over data deletion

---

## FAQ

### General Questions

**Q: Do I need to create an account?**
A: No. PaiiD is designed for single-user operation with no account required. All settings are stored locally in your browser.

**Q: Is my data safe?**
A: Yes. No personal information is collected. Trading preferences are stored locally in your browser only.

**Q: Is this real money or paper trading?**
A: PaiiD uses Alpaca Paper Trading API, so all trades are simulated with NO real money. Perfect for learning and testing strategies.

**Q: Can I connect my real brokerage account?**
A: Not currently. PaiiD is designed for paper trading only. Real brokerage integration may come in future releases.

**Q: What market data sources are used?**
A: Market data comes from Tradier API (real-time, NO delay). Trade execution through Alpaca Paper Trading API.

### Technical Questions

**Q: Which browsers are supported?**
A: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+. Chrome is recommended for best performance.

**Q: Does PaiiD work on mobile?**
A: The platform is responsive and works on tablets (iPad, Android). Phone screens are too small for optimal experience.

**Q: Why isn't real-time data updating?**
A: Check your internet connection. Ensure backend is healthy (green indicator in header). Try refreshing the page.

**Q: How do I reset my settings?**
A: Go to Settings → Data & Privacy → "Clear All Data". This will reset the platform to default state.

**Q: Can I export my trading history?**
A: Yes. Go to Settings → Data & Privacy → "Export Trading Data". Choose CSV or JSON format.

### Trading Questions

**Q: What order types are supported?**
A: Market, Limit, Stop, and Stop-Limit orders. Time-in-force: Day, GTC, IOC, FOK.

**Q: How long does it take for orders to fill?**
A: Paper orders typically fill within seconds during market hours, simulating real market conditions.

**Q: Why was my order rejected?**
A: Common reasons:
- Insufficient buying power
- Invalid symbol
- Market closed (if Day order)
- Invalid price (e.g., limit price too far from market)

**Q: How do I set a stop-loss?**
A: In Active Positions, click on a position, then "Add Stop-Loss". Set trigger price and order type.

**Q: What's the difference between Stop and Stop-Limit orders?**
A: Stop becomes market order when triggered (guaranteed fill, price not guaranteed). Stop-Limit becomes limit order (price guaranteed, fill not guaranteed).

### AI & Strategy Questions

**Q: How accurate are AI recommendations?**
A: Accuracy varies. Recommendations with 75%+ confidence have historically 60-75% win rate. Always use as one input in your decision process.

**Q: Can I create my own trading strategies?**
A: Yes! Use the Strategy Builder workflow to create custom strategies with no coding required.

**Q: How do I backtest a strategy?**
A: Create strategy in Strategy Builder, then go to Backtesting workflow. Select strategy, configure parameters, and run backtest.

**Q: What's a good Sharpe ratio?**
A:
- > 2.0 = Excellent
- 1.0-2.0 = Good
- 0.5-1.0 = Acceptable
- < 0.5 = Poor

**Q: How many trades do I need for a valid backtest?**
A: Minimum 30 trades for basic validity. 100+ trades preferred for statistical significance.

---

## Troubleshooting

### Login & Access Issues

**Problem:** Page won't load
- **Solution:** Check internet connection. Try refreshing page. Clear browser cache (Ctrl+Shift+Delete).

**Problem:** "Backend unavailable" error
- **Solution:** Backend server may be restarting. Wait 1-2 minutes and refresh. Check status at https://paiid-backend.onrender.com/api/health

**Problem:** Lost all my settings
- **Solution:** Settings are stored in browser localStorage. If you cleared browser data, settings are lost. This is by design for privacy.

### Data & Display Issues

**Problem:** Market data not updating
- **Solution:**
  1. Check internet connection
  2. Verify market is open (9:30 AM - 4:00 PM ET, Mon-Fri)
  3. Click manual refresh button
  4. Check backend health indicator (should be green)

**Problem:** Positions showing wrong P&L
- **Solution:** Refresh the page. Check that market data is current. If persists, report bug.

**Problem:** Charts not rendering
- **Solution:**
  1. Refresh page
  2. Try different browser
  3. Disable browser extensions (ad blockers can interfere)
  4. Check console for errors (F12 → Console)

**Problem:** Radial menu not responding
- **Solution:**
  1. Hard refresh (Ctrl+Shift+R)
  2. Clear browser cache
  3. Try different browser
  4. Ensure JavaScript is enabled

### Trading Issues

**Problem:** Order rejected
- **Possible Causes:**
  1. Insufficient buying power → Reduce quantity
  2. Market closed → Wait for market open or use GTC order
  3. Invalid symbol → Verify symbol is correct
  4. Invalid price → Check limit price is near market price

**Problem:** Order not filling (limit order)
- **Solution:** Limit price may be too far from market. Cancel and re-submit at current market price, or use market order.

**Problem:** Position not appearing after order filled
- **Solution:** Refresh Active Positions. Allow 30 seconds for update. Check order status in Execute Trade.

**Problem:** Can't close position
- **Solution:**
  1. Verify you have enough buying power to close short position
  2. Try market order instead of limit
  3. Check order status - may be pending

### Performance Issues

**Problem:** Platform running slowly
- **Solution:**
  1. Close unused browser tabs
  2. Disable auto-refresh temporarily
  3. Clear browser cache
  4. Restart browser
  5. Try Chrome for best performance

**Problem:** High data usage
- **Solution:**
  1. Disable real-time streaming when not actively trading
  2. Reduce auto-refresh frequency in Settings
  3. Close unused workflows

---

## Support

### Getting Help

**In-App Help:**
- Press `?` key for keyboard shortcuts overlay
- Click help icon in any workflow for context-sensitive help
- Visit Settings → Help & Support for tutorials

**Documentation:**
- User Guide (this document)
- Developer Guide (for technical users)
- API Reference (for developers)

**Bug Reports:**
- GitHub Issues: https://github.com/your-repo/paiid/issues
- Include: Browser version, screenshot, steps to reproduce
- Check existing issues before creating new one

**Feature Requests:**
- GitHub Issues with "enhancement" label
- Describe use case and benefits
- Community upvoting helps prioritize

**Contact:**
- Email: support@paiid.com
- Response time: 24-48 hours
- For urgent issues, mark as "URGENT" in subject

---

## Tips for Success

### Best Practices

1. **Start Small:**
   - Begin with small position sizes while learning
   - Gradually increase as you gain confidence
   - Never risk more than 1-2% per trade

2. **Use Stop-Losses:**
   - ALWAYS set stop-losses on every trade
   - Determine stop-loss BEFORE entering trade
   - Never move stop-loss further away (only closer/tighter)

3. **Keep a Trading Journal:**
   - Export your trading data regularly
   - Review what worked and what didn't
   - Learn from both wins and losses

4. **Follow Your Plan:**
   - Create a trading plan and stick to it
   - Don't deviate based on emotions
   - If plan isn't working, revise it (don't abandon it)

5. **Manage Risk:**
   - Never risk more than you can afford to lose (paper trading!)
   - Diversify across multiple positions
   - Don't put all capital in one trade

6. **Stay Informed:**
   - Check Morning Routine daily
   - Review news before trading
   - Stay aware of economic calendar events

7. **Learn Continuously:**
   - Review P&L Dashboard weekly
   - Analyze losing trades for lessons
   - Test new strategies in Backtesting first

### Common Beginner Mistakes

1. **Over-trading:**
   - Making too many trades leads to losses
   - Quality over quantity
   - Wait for high-probability setups

2. **Chasing Trades:**
   - Don't chase after price runs away
   - Wait for pullback or next opportunity
   - FOMO (fear of missing out) is expensive

3. **Ignoring Risk Management:**
   - Not using stop-losses
   - Position sizes too large
   - Risking too much per trade

4. **Trading Without a Plan:**
   - Random entries based on emotions
   - No clear exit strategy
   - Inconsistent decision-making

5. **Overconfidence After Wins:**
   - One good trade doesn't make you an expert
   - Stay humble and disciplined
   - Consistent results come from consistent process

### Advanced Tips

1. **Use Multiple Timeframes:**
   - Check daily chart for trend
   - Use 1-hour chart for entry timing
   - Align timeframes for best setups

2. **Combine Indicators:**
   - Don't rely on single indicator
   - Use 2-3 confirming indicators
   - Example: RSI + MACD + Volume

3. **Watch Market Regime:**
   - Bull market: Focus on long setups
   - Bear market: Focus on short setups
   - Choppy market: Reduce trading or use mean reversion

4. **Optimize Position Sizing:**
   - Larger positions for high-confidence setups
   - Smaller positions for lower-confidence
   - Scale in/out of positions

5. **Leverage AI Wisely:**
   - Use AI recommendations as screening tool
   - Confirm with your own analysis
   - Track AI accuracy over time

---

**Document Version:** 1.0.0
**Last Updated:** October 27, 2025
**Platform Version:** 1.0.0

Happy Trading! Remember: This is paper trading - perfect for learning without financial risk. Practice good habits here, and they'll serve you well if you ever trade with real money.

For additional help, visit our documentation at https://docs.paiid.com or contact support@paiid.com.
