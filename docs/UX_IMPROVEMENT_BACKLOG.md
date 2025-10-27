# UX Improvement Backlog - PaiiD Trading Platform

**Analysis Date:** October 27, 2025
**Batch:** MOD SQUAD - BATCH 3 (UX Gap Analysis)
**Source:** Combination of FEATURE_GAP_ANALYSIS.md + UX_FRICTION_ANALYSIS.md
**Prioritization:** Impact × Effort Matrix (P0 = Critical, P1 = High, P2 = Medium, P3 = Low)

---

## Executive Summary

This backlog consolidates findings from feature gap and UX friction analyses into **53 sprint-ready tickets** ranked by business impact and implementation effort. Tickets are organized into 4 priority tiers:

- **P0 (Critical):** 12 tickets - Ship blockers, must-have for production
- **P1 (High):** 18 tickets - Competitive parity, significant UX improvements
- **P2 (Medium):** 15 tickets - Nice-to-have features, polish
- **P3 (Low):** 8 tickets - Future enhancements, specialized features

**Recommended Sprint Allocation:**
- Sprints 1-3: P0 tickets (12 tickets ÷ 4 per sprint = 3 sprints)
- Sprints 4-7: P1 tickets (18 tickets ÷ 4-5 per sprint = 4 sprints)
- Sprints 8+: P2/P3 as capacity allows

---

## Impact × Effort Matrix

```
High Impact │ P0-1  │ P0-2  │ P1-3  │ P1-5  │ P2-7  │
            │ P0-3  │ P0-4  │ P1-4  │ P1-6  │       │
            │ P0-5  │ P0-6  │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┤
Medium Impact│ P0-7  │ P1-7  │ P1-9  │ P2-1  │ P2-8  │
            │ P0-8  │ P1-8  │ P1-10 │ P2-2  │       │
            │       │       │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┤
Low Impact  │ P0-9  │ P2-3  │ P2-9  │ P3-1  │ P3-5  │
            │ P0-10 │ P2-4  │ P2-10 │ P3-2  │       │
            │       │       │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┤
             Low     Medium   High    V.High  Massive
                        Effort →
```

---

# P0 - CRITICAL (Ship Blockers)

## P0-1: Add "Close Position" Quick Action Button
**Impact:** High | **Effort:** Low (1-2 days) | **Severity Score:** 25

**Problem:**
- Users cannot directly close a position from ActivePositions
- Must navigate to Execute Trade > fill form > submit (6 clicks)
- High friction for urgent exits (panic selling)

**Solution:**
Add "Close" button to each position card that:
1. Pre-fills ExecuteTradeForm with opposite side + full qty
2. Shows confirmation dialog with current price
3. Submits market order immediately

**Acceptance Criteria:**
- [ ] "Close" button visible on each position card
- [ ] Click triggers confirmation dialog showing: "Close 100 shares of SPY at market price (~$450.00)? Expected proceeds: $45,000"
- [ ] Confirm button submits sell order (market type, full qty)
- [ ] Success toast: "✅ Closed SPY position - 100 shares sold"
- [ ] Position removed from list after fill

**Files to Modify:**
- `frontend/components/ActivePositions.tsx` - Add button + handler
- `frontend/lib/alpaca.ts` - Add `closePosition(symbol)` helper

**Testing:**
- Close long position (SPY 100 shares)
- Close short position (AAPL -50 shares)
- Cancel close confirmation
- Verify order appears in OrderHistory

---

## P0-2: Panic Button - Close All Positions
**Impact:** High | **Effort:** Medium (3-4 days) | **Severity Score:** 25

**Problem:**
- No emergency exit from all positions
- Critical risk management gap
- Users must manually close each position (6 clicks × N positions)

**Solution:**
Add "CLOSE ALL POSITIONS" button in header/StatusBar with:
1. Large red button with warning icon
2. 2-step confirmation (type "CLOSE ALL" to confirm)
3. Batch submit market orders for all open positions
4. Progress indicator showing N/M positions closed

**Acceptance Criteria:**
- [ ] Red "Emergency Close All" button in StatusBar
- [ ] First click shows warning: "⚠️ This will close ALL 5 positions at market price. Total estimated proceeds: $125,000. Type 'CLOSE ALL' to confirm."
- [ ] Input field for "CLOSE ALL" text confirmation
- [ ] Second click (after typing) submits batch close orders
- [ ] Progress modal: "Closing positions... 3/5 complete"
- [ ] Final summary: "✅ Closed 5 positions - Total proceeds: $124,850"
- [ ] Error handling: "⚠️ Failed to close AAPL - insufficient shares. Closed 4/5 positions."

**Files to Modify:**
- `frontend/components/StatusBar.tsx` - Add panic button
- `frontend/components/ui/PanicButtonDialog.tsx` - New component
- `frontend/lib/alpaca.ts` - Add `closeAllPositions()` batch handler
- `backend/app/routers/portfolio.py` - Add `/close-all` endpoint

**Testing:**
- Close all with 5 positions
- Close all with 0 positions (disabled button)
- Cancel after typing "CLOSE ALL"
- Network error during batch close (partial completion)

---

## P0-3: Order Modification UI
**Impact:** High | **Effort:** Medium (3-4 days) | **Severity Score:** 15

**Problem:**
- Cannot edit pending orders (qty, price)
- Backend supports modification but no UI
- Users must cancel + re-place (loses queue position)

**Solution:**
Add "Edit" button to pending orders in OrderHistory that:
1. Opens modal with pre-filled order form
2. Allows editing qty and limit price (symbol, side locked)
3. Submits modification via Alpaca API

**Acceptance Criteria:**
- [ ] "Edit" button visible on pending limit orders
- [ ] Click opens modal: "Edit Pending Order - BUY 100 SPY @ $450.00"
- [ ] Qty and Limit Price editable, Symbol and Side disabled
- [ ] "Save Changes" submits PATCH to `/api/orders/{order_id}`
- [ ] Success toast: "✅ Order modified - New qty: 150, New price: $448.50"
- [ ] Updated order appears in OrderHistory
- [ ] Filled orders show "Cannot edit filled order" tooltip

**Files to Modify:**
- `frontend/components/OrderHistory.tsx` - Add edit button + modal
- `frontend/components/trading/OrderEditModal.tsx` - New component
- `backend/app/routers/orders.py` - Add PATCH `/orders/{order_id}` endpoint
- `backend/app/routers/orders.py` - Implement Alpaca PATCH order

**Testing:**
- Edit pending limit order (change qty)
- Edit pending limit order (change price)
- Try editing filled order (disabled)
- Try editing canceled order (disabled)
- Network error during modification

---

## P0-4: Price Alerts System (MVP)
**Impact:** High | **Effort:** High (5-7 days) | **Severity Score:** 20

**Problem:**
- No threshold-based price alerts
- Users miss breakout/breakdown opportunities
- Standard feature on all trading platforms

**Solution:**
Implement basic price alerts:
1. Add "Set Alert" button in watchlist symbols
2. Modal to set price + condition (above/below)
3. Browser notifications when triggered
4. Backend polling to check alerts (1min interval)

**Acceptance Criteria:**
- [ ] "Set Alert" button on each watchlist symbol
- [ ] Modal shows: "Alert when SPY is: [Above ▼] [450.00] [Set Alert]"
- [ ] Alerts stored in localStorage (no DB required for MVP)
- [ ] Background polling checks alerts every 60s
- [ ] Browser notification: "🔔 SPY Alert - Price is $450.25 (above $450.00)"
- [ ] Toast + highlight in watchlist when triggered
- [ ] "Manage Alerts" panel shows all active alerts (symbol, condition, price)
- [ ] Delete alert button

**Files to Modify:**
- `frontend/components/WatchlistManager.tsx` - Add alert button
- `frontend/components/alerts/AlertModal.tsx` - New component
- `frontend/components/alerts/AlertManager.tsx` - New component
- `frontend/hooks/usePriceAlerts.ts` - New hook for polling
- `frontend/lib/alerts.ts` - Alert storage + notification logic

**Testing:**
- Set alert for SPY above $450
- Wait for price to cross threshold (trigger)
- Set alert for AAPL below $180
- Delete alert before trigger
- Browser notification permission denied (fallback to toast)

---

## P0-5: Stop Loss Order UI
**Impact:** High | **Effort:** Medium (3-4 days) | **Severity Score:** N/A

**Problem:**
- Backend supports stop loss orders
- No UI to create them (only market/limit)
- Critical risk management tool missing

**Solution:**
Add "Stop Loss" order type to ExecuteTradeForm:
1. Dropdown: Market / Limit / **Stop Loss** / Stop Limit
2. When "Stop Loss" selected, show "Stop Price" field
3. Submit as stop order via Alpaca API

**Acceptance Criteria:**
- [ ] "Stop Loss" option in "Order Type" dropdown
- [ ] When selected, "Stop Price" input field appears
- [ ] Validation: Stop price must be below current price (for long), above (for short)
- [ ] Submit creates stop order via Alpaca
- [ ] Confirmation dialog: "Sell 100 SPY when price drops to $440.00?"
- [ ] Pending stop order shows in OrderHistory with stop price
- [ ] When triggered, order executes at market price

**Files to Modify:**
- `frontend/components/ExecuteTradeForm.tsx` - Add stop loss UI
- `backend/app/routers/orders.py` - Ensure stop order type supported
- `backend/app/middleware/validation.py` - Add stop price validation

**Testing:**
- Create stop loss for long position (sell when price drops)
- Create stop loss for short position (buy when price rises)
- Invalid stop price (above current for long) - validation error
- Stop order triggers and fills

---

## P0-6: Enhanced Keyboard Shortcuts (15+ Total)
**Impact:** High | **Effort:** Medium (3-4 days) | **Severity Score:** 12

**Problem:**
- Only 6 keyboard shortcuts currently
- TradingView has 50+ shortcuts
- Power users need faster navigation

**Solution:**
Expand KeyboardShortcuts.tsx to support 15+ shortcuts:
- Navigation: 1-9 keys for workflows, Home (dashboard), End (settings)
- Trading: Ctrl+T (trade), Ctrl+B (buy), Ctrl+S (sell), Ctrl+X (close position)
- Data: Ctrl+W (watchlist), Ctrl+N (news), Ctrl+A (analytics)
- Utilities: Ctrl+K (command palette), Ctrl+/ (help), Ctrl+R (refresh positions)

**Acceptance Criteria:**
- [ ] 15+ shortcuts implemented (see list above)
- [ ] Shortcuts work globally (not just in focused elements)
- [ ] Shortcuts disabled when typing in input fields
- [ ] Ctrl+/ opens keyboard shortcuts modal
- [ ] Visual feedback when shortcut pressed (toast or highlight)
- [ ] Shortcuts configurable in Settings (stretch goal)

**Files to Modify:**
- `frontend/components/KeyboardShortcuts.tsx` - Expand hotkey definitions
- `frontend/components/ui/ShortcutsModal.tsx` - Update help modal
- `frontend/pages/index.tsx` - Add shortcuts for workflows 1-9

**Testing:**
- Press 1-9 keys (switch workflows)
- Press Ctrl+B (opens Execute Trade with Buy selected)
- Press Ctrl+X (closes selected position)
- Type in input field (shortcuts disabled)
- Press Ctrl+/ (shows help modal)

---

## P0-7: Backtesting Component Completion
**Impact:** Medium | **Effort:** High (5-7 days) | **Severity Score:** N/A

**Problem:**
- Backtesting.tsx component incomplete
- UI exists but no data flow
- Missing historical trade simulation

**Solution:**
Complete backtesting implementation:
1. Connect to backend `/api/backtesting/run` endpoint
2. Show progress bar during backtest execution
3. Display results: Total return, Sharpe ratio, max drawdown, trade log
4. Chart: Equity curve + drawdowns

**Acceptance Criteria:**
- [ ] User selects strategy from dropdown (fetch from `/api/strategies`)
- [ ] User sets date range (start, end) + initial capital ($10,000 default)
- [ ] "Run Backtest" button triggers backend execution
- [ ] Progress bar shows: "Backtesting... 45% (Processing 2020-06-15)"
- [ ] Results panel shows:
  - Total Return: +25.3% ($12,530)
  - Sharpe Ratio: 1.45
  - Max Drawdown: -8.2%
  - Win Rate: 62%
  - Total Trades: 145
- [ ] Equity curve chart (D3.js or TradingView)
- [ ] Trade log table (date, symbol, side, qty, price, P&L)
- [ ] Export results as CSV

**Files to Modify:**
- `frontend/components/Backtesting.tsx` - Complete UI + data flow
- `backend/app/routers/backtesting.py` - Ensure endpoint works
- `backend/app/services/backtesting_engine.py` - Implement backtest logic

**Testing:**
- Run backtest for "SPY Momentum" strategy (2020-2023)
- Run backtest with invalid date range (error handling)
- Cancel backtest mid-execution
- Export results as CSV

---

## P0-8: Order Cancellation UI (One-Click)
**Impact:** Medium | **Effort:** Low (1-2 days) | **Severity Score:** N/A

**Problem:**
- Backend supports order cancellation
- No UI button to cancel pending orders
- Users must use Alpaca dashboard

**Solution:**
Add "Cancel" button to pending orders in OrderHistory:
1. One-click cancellation (no confirmation for pending orders)
2. Confirmation required for partially filled orders
3. Success toast + remove from list

**Acceptance Criteria:**
- [ ] "Cancel" button visible on pending orders
- [ ] Click submits DELETE to `/api/orders/{order_id}`
- [ ] Success toast: "✅ Order canceled - BUY 100 SPY @ $450.00"
- [ ] Order removed from pending list, moved to canceled list
- [ ] Partially filled orders show warning: "This order is partially filled (50/100 shares). Cancel remaining 50 shares?"
- [ ] Filled orders have disabled "Cancel" button

**Files to Modify:**
- `frontend/components/OrderHistory.tsx` - Add cancel button
- `backend/app/routers/orders.py` - Ensure DELETE endpoint works

**Testing:**
- Cancel pending limit order
- Cancel partially filled order (with confirmation)
- Try canceling filled order (disabled)
- Network error during cancellation

---

## P0-9: Symbol Search Autocomplete (Watchlist & Trade Form)
**Impact:** Medium | **Effort:** Medium (3-4 days) | **Severity Score:** 12

**Problem:**
- Users must type exact symbol (manual entry error-prone)
- No suggestions or search (e.g., "Apple" → AAPL)
- High friction when adding symbols to watchlist

**Solution:**
Add autocomplete to symbol inputs:
1. Debounced search API call (250ms after typing stops)
2. Dropdown shows matching symbols with company names
3. Arrow keys to navigate, Enter to select

**Acceptance Criteria:**
- [ ] Type "app" in symbol input → Dropdown shows:
  - AAPL - Apple Inc.
  - APPN - Appian Corporation
  - APPS - Digital Turbine Inc.
- [ ] Arrow down/up navigates dropdown
- [ ] Enter selects highlighted symbol
- [ ] Click selects symbol
- [ ] Esc closes dropdown
- [ ] Dropdown shows "No results" if no matches
- [ ] Works in ExecuteTradeForm + WatchlistManager

**Files to Modify:**
- `frontend/components/ui/SymbolAutocomplete.tsx` - New component
- `frontend/components/ExecuteTradeForm.tsx` - Replace input with autocomplete
- `frontend/components/WatchlistManager.tsx` - Replace input with autocomplete
- `backend/app/routers/market.py` - Add `/symbols/search?query=app` endpoint

**Testing:**
- Search "tesla" → Select TSLA
- Search "spy" → Select SPY
- Search "zzzzz" → No results
- Arrow keys + Enter selection
- Click selection

---

## P0-10: Error Messages with Recovery Actions
**Impact:** Medium | **Effort:** Low (1-2 days) | **Severity Score:** N/A

**Problem:**
- Error messages only state problem, no solution
- Example: "Invalid symbol" (no suggestion)
- Users don't know how to recover

**Solution:**
Enhance error messages with actionable suggestions:
1. Invalid symbol → "Symbol APLE not found. Did you mean AAPL?"
2. Market closed → "Market is closed. Opens at 9:30 AM ET (in 2h 15m). Place limit order for open?"
3. Insufficient funds → "Insufficient buying power ($5,000). Max affordable qty: 10 shares."
4. Network error → "Network error. [Retry] or [Check Status Page]"

**Acceptance Criteria:**
- [ ] Symbol validation error includes "Did you mean?" suggestions
- [ ] Market closed error shows time until open + "Place limit order?" button
- [ ] Insufficient funds error shows max affordable qty
- [ ] Network errors include "Retry" button
- [ ] API rate limit errors show "Try again in 30 seconds"
- [ ] All errors logged to frontend/lib/logger.ts

**Files to Modify:**
- `frontend/lib/toast.ts` - Add `showErrorWithAction(message, action)` helper
- `frontend/components/ExecuteTradeForm.tsx` - Enhance error handling
- `frontend/lib/alpaca.ts` - Add error message mapping
- `backend/app/middleware/error_handler.py` - Return suggestion field in errors

**Testing:**
- Submit invalid symbol → See "Did you mean?"
- Submit order when market closed → See time until open
- Submit order with insufficient funds → See max qty
- Disconnect network → See retry button

---

## P0-11: AI Analysis Non-Blocking Loading
**Impact:** Medium | **Effort:** Low (1-2 days) | **Severity Score:** 12

**Problem:**
- AI analysis in ExecuteTradeForm blocks interaction
- Users cannot edit form while waiting for AI response
- 800ms debounce + 1-2s API = 3s blocked

**Solution:**
Make AI analysis section independent:
1. Load in background (async)
2. Show skeleton placeholder while loading
3. Allow form interaction during load
4. Graceful error handling (don't block form)

**Acceptance Criteria:**
- [ ] Type symbol → Form remains interactive
- [ ] AI section shows skeleton loading state
- [ ] User can change qty/side while AI loads
- [ ] AI result appears without blocking form
- [ ] Error in AI analysis shows warning but doesn't block submit
- [ ] Debounce increased to 1000ms (reduce API calls)

**Files to Modify:**
- `frontend/components/ExecuteTradeForm.tsx` - Async AI loading
- `frontend/components/ui/Skeleton.tsx` - Add AI analysis skeleton

**Testing:**
- Type symbol → Edit qty before AI loads
- AI API error → Form still submits
- Fast typing → Debounce prevents multiple API calls

---

## P0-12: Mobile Touch Target Sizing (44x44pt)
**Impact:** Medium | **Effort:** Low (1-2 days) | **Severity Score:** 12

**Problem:**
- Icon buttons too small (32px) on mobile
- iOS guidelines require 44x44pt minimum
- Users mis-tap buttons

**Solution:**
Increase all icon buttons to 44x44pt:
1. Audit all icon buttons (Close, Edit, Delete, etc.)
2. Increase padding to meet 44x44pt
3. Ensure spacing prevents accidental taps

**Acceptance Criteria:**
- [ ] All icon buttons have min 44x44pt touch target
- [ ] Padding added to maintain visual size
- [ ] Tested on iPhone SE (smallest screen)
- [ ] No overlapping tap targets
- [ ] Active state feedback (button press indication)

**Files to Modify:**
- `frontend/styles/theme.ts` - Add `touchTarget: { minSize: '44px' }`
- All components with icon buttons (audit with `<Grep>`)

**Testing:**
- Tap all buttons on iPhone SE (smallest device)
- Verify no mis-taps between adjacent buttons
- Check active state visual feedback

---

# P1 - HIGH (Competitive Parity)

## P1-1: Multi-Leg Options Strategies
**Impact:** High | **Effort:** Very High (10-14 days) | **Severity Score:** N/A

**Problem:**
- ExecuteTradeForm only supports single-leg options
- Cannot create spreads, iron condors, butterflies
- Advanced options traders need multi-leg support

**Solution:**
Add multi-leg options builder:
1. "Add Leg" button to create additional option legs
2. Visual P&L chart showing payoff diagram
3. Greeks summary for entire position
4. Submit as single multi-leg order to Alpaca

**Acceptance Criteria:**
- [ ] "Single Leg / Multi-Leg" toggle button
- [ ] Multi-leg mode shows "Add Leg" button
- [ ] Each leg: Buy/Sell, Call/Put, Strike, Expiry, Qty
- [ ] "Remove Leg" button on each leg (min 2 legs)
- [ ] P&L chart shows payoff diagram (profit/loss vs. price)
- [ ] Greeks summary: Net Delta, Gamma, Theta, Vega
- [ ] Preset strategies dropdown: Vertical Spread, Iron Condor, Butterfly, etc.
- [ ] Submit as multi-leg order via Alpaca

**Files to Modify:**
- `frontend/components/ExecuteTradeForm.tsx` - Add multi-leg toggle
- `frontend/components/trading/MultiLegBuilder.tsx` - New component
- `frontend/components/trading/OptionsPayoffChart.tsx` - New component (D3.js)
- `backend/app/routers/orders.py` - Support multi-leg order submission

**Testing:**
- Create vertical call spread (buy $450, sell $455)
- Create iron condor (4 legs)
- Select preset "Butterfly" → Auto-fills legs
- Submit multi-leg order → Verify all legs filled

---

## P1-2: Position Sizing Calculator (Risk-Based)
**Impact:** High | **Effort:** Medium (3-4 days) | **Severity Score:** N/A

**Problem:**
- Users manually calculate how many shares to buy
- No risk-based sizing (% of portfolio risk)
- RiskCalculator only exists for options

**Solution:**
Add position sizing calculator to ExecuteTradeForm:
1. "Calculator" button opens modal
2. User inputs: Risk % (2% default), Stop Loss Price
3. Calculator shows: Max shares, Max $ amount, Risk $
4. "Use This Size" button auto-fills qty in form

**Acceptance Criteria:**
- [ ] "Calculator" button next to Qty field
- [ ] Modal inputs:
  - Account size: $100,000 (auto-filled from Alpaca)
  - Risk per trade: 2% ($2,000)
  - Entry price: $450.00 (auto-filled)
  - Stop loss price: $440.00
- [ ] Calculator shows:
  - Risk per share: $10.00
  - Max shares: 200 ($2,000 / $10)
  - Total investment: $90,000
  - Risk %: 2.00%
- [ ] "Use This Size" button sets qty to 200
- [ ] Validation: Stop loss must be below entry (for longs)

**Files to Modify:**
- `frontend/components/ExecuteTradeForm.tsx` - Add calculator button
- `frontend/components/trading/PositionSizeCalculator.tsx` - New component
- `frontend/lib/tradingMath.ts` - Add calculation functions

**Testing:**
- Calculate size for SPY (2% risk, $10 stop)
- Calculate size for TSLA (1% risk, $5 stop)
- Invalid stop loss (above entry) → Error
- Use calculated size → Qty auto-fills

---

## P1-3: Asset Allocation Pie Chart
**Impact:** High | **Effort:** Medium (3-4 days) | **Severity Score:** N/A

**Problem:**
- No visual breakdown of portfolio composition
- Users don't see sector/symbol allocation
- Standard feature on all platforms

**Solution:**
Add pie chart to ActivePositions:
1. D3.js pie chart showing % allocation by symbol
2. Hover shows: Symbol, %, $ value
3. Click segment filters position list

**Acceptance Criteria:**
- [ ] Pie chart visible at top of ActivePositions
- [ ] Each segment colored by P&L (green if positive, red if negative)
- [ ] Hover tooltip: "SPY - 45% ($45,000) - +$2,500 (+5.9%)"
- [ ] Click segment highlights/scrolls to that position
- [ ] Legend shows all symbols with color + % + $
- [ ] "Group by Sector" toggle (requires sector data from Tradier)

**Files to Modify:**
- `frontend/components/ActivePositions.tsx` - Add pie chart section
- `frontend/components/charts/AllocationPieChart.tsx` - New component (D3.js)
- `frontend/lib/tradingMath.ts` - Add allocation calculation

**Testing:**
- View allocation with 5 positions
- Hover over segments → Tooltip shows details
- Click segment → Scrolls to position
- Group by sector → Chart re-renders

---

## P1-4: Enhanced Market Scanner Filters
**Impact:** High | **Effort:** Medium (3-4 days) | **Severity Score:** N/A

**Problem:**
- MarketScanner has only 5 basic filters
- Missing technical filters (RSI, MACD, volume)
- Missing fundamental filters (P/E, market cap)

**Solution:**
Expand MarketScanner filters:
1. Technical: RSI (>, <, between), MACD (bullish/bearish cross), Volume (vs avg)
2. Fundamental: P/E ratio, Market cap, Dividend yield
3. Save custom scans for later reuse

**Acceptance Criteria:**
- [ ] Filter panel with tabs: Technical / Fundamental / Price
- [ ] Technical filters:
  - RSI: Above/Below/Between [0-100]
  - MACD: Bullish Cross / Bearish Cross / Above/Below Signal
  - Volume: Above/Below [X]× average
  - 50-day MA: Above/Below
  - 200-day MA: Above/Below
- [ ] Fundamental filters:
  - P/E Ratio: Above/Below [X]
  - Market Cap: Small/Mid/Large cap
  - Dividend Yield: Above [X]%
- [ ] "Save Scan" button → Name + save to localStorage
- [ ] "Load Scan" dropdown → Restore saved filters
- [ ] Results update in real-time as filters change

**Files to Modify:**
- `frontend/components/MarketScanner.tsx` - Expand filter panel
- `backend/app/routers/screening.py` - Add filter logic
- `backend/app/services/tradier_client.py` - Fetch technical indicators

**Testing:**
- Filter RSI < 30 → Show oversold stocks
- Filter MACD bullish cross → Show momentum stocks
- Save scan "Oversold Tech" → Reload later
- Combine 3+ filters → Results intersection

---

## P1-5: Risk Metrics Dashboard (Beta, Sharpe, VaR)
**Impact:** High | **Effort:** High (5-7 days) | **Severity Score:** N/A

**Problem:**
- No portfolio risk metrics (Beta, Sharpe, VaR)
- Users don't understand portfolio risk exposure
- Standard on institutional platforms

**Solution:**
Add risk metrics panel to ActivePositions:
1. Calculate metrics from historical position data
2. Visual gauges for each metric
3. Tooltips explain each metric

**Acceptance Criteria:**
- [ ] Risk panel shows:
  - **Beta:** 1.23 (23% more volatile than market)
  - **Sharpe Ratio:** 1.45 (risk-adjusted return)
  - **Value at Risk (VaR):** $2,500 (95% confidence, 1-day)
  - **Max Drawdown:** -8.2% (largest peak-to-trough decline)
  - **Volatility:** 18% annualized
- [ ] Gauges visualize metrics (green/yellow/red zones)
- [ ] Tooltip on hover explains each metric in plain English
- [ ] "Learn More" links to help docs

**Files to Modify:**
- `frontend/components/ActivePositions.tsx` - Add risk panel
- `frontend/components/charts/RiskMetricsGauge.tsx` - New component
- `backend/app/routers/portfolio.py` - Add `/portfolio/risk-metrics` endpoint
- `backend/app/services/risk_calculator.py` - Calculate Beta, Sharpe, VaR

**Testing:**
- View metrics with 5 positions
- Tooltip hover → See explanations
- High volatility → Red gauge
- Low volatility → Green gauge

---

## P1-6: Keyboard Navigation in RadialMenu
**Impact:** High | **Effort:** Medium (3-4 days) | **Severity Score:** 12

**Problem:**
- RadialMenu not keyboard navigable (Tab doesn't work)
- Violates accessibility standards
- Power users cannot navigate without mouse

**Solution:**
Add keyboard navigation to RadialMenu:
1. Tab cycles through segments (clockwise)
2. Shift+Tab cycles backward
3. Arrow keys rotate focus
4. Enter selects focused segment
5. ARIA labels for screen readers

**Acceptance Criteria:**
- [ ] Tab focuses first segment (Morning Routine)
- [ ] Tab again moves to next segment (clockwise)
- [ ] Shift+Tab moves backward (counter-clockwise)
- [ ] Right arrow rotates clockwise
- [ ] Left arrow rotates counter-clockwise
- [ ] Enter selects focused segment → Loads workflow
- [ ] Visual focus indicator (glow + border)
- [ ] ARIA labels: `aria-label="Morning Routine workflow - Press Enter to open"`
- [ ] `role="navigation"` on wrapper

**Files to Modify:**
- `frontend/components/RadialMenu/index.tsx` - Add keyboard handlers
- `frontend/hooks/useRadialMenuD3.ts` - Add focus state to D3 rendering
- `frontend/components/RadialMenu/workflows.ts` - Add ARIA labels

**Testing:**
- Tab through all 10 segments
- Arrow keys rotate focus
- Enter key selects segment
- Screen reader announces labels

---

## P1-7: "Last Updated" Timestamps
**Impact:** Medium | **Effort:** Low (1-2 days) | **Severity Score:** 9

**Problem:**
- Position cards refresh every 5s but no indicator
- Users don't know if data is stale
- No trust in real-time updates

**Solution:**
Add "Last updated" timestamp to:
1. Position cards (ActivePositions)
2. Account balance (StatusBar)
3. Watchlist prices (WatchlistManager)

**Acceptance Criteria:**
- [ ] Position cards show: "Updated 3s ago" (bottom right)
- [ ] Updates every 1s (relative time: 3s, 15s, 1m, 5m)
- [ ] Turns yellow after 30s, red after 2min (stale indicator)
- [ ] Account balance shows: "Balance as of 10:45:23 AM"
- [ ] Watchlist prices show: "Prices updated 5s ago"
- [ ] Manual refresh button resets timestamp

**Files to Modify:**
- `frontend/components/ActivePositions.tsx` - Add timestamp
- `frontend/components/StatusBar.tsx` - Add timestamp
- `frontend/components/WatchlistManager.tsx` - Add timestamp
- `frontend/hooks/useRelativeTime.ts` - New hook for "3s ago" formatting

**Testing:**
- Wait 3s → See "Updated 3s ago"
- Wait 2min → Timestamp turns red
- Refresh positions → Timestamp resets to "Updated 0s ago"

---

## P1-8: Progressive Disclosure in ExecuteTradeForm
**Impact:** Medium | **Effort:** Medium (3-4 days) | **Severity Score:** 12

**Problem:**
- 15+ fields visible simultaneously (cognitive overload)
- Most users only need symbol, side, qty, order type
- Advanced fields (options, AI, templates) clutter UI

**Solution:**
Hide advanced sections behind toggle buttons:
1. Default view: Symbol, Side, Qty, Order Type, Submit
2. "Advanced Options" toggle shows: Limit Price, Stop Loss, Time in Force
3. "Options Trading" toggle shows: Asset Class, Strike, Expiry, Greeks
4. "AI Analysis" toggle shows: AI recommendation panel
5. "Templates" toggle shows: Template selector

**Acceptance Criteria:**
- [ ] Default form shows 5 fields only
- [ ] "Advanced Options ▼" button expands section (smooth animation)
- [ ] "Options Trading ▼" button shows options fields
- [ ] "AI Analysis ▼" button shows AI panel (auto-expands if symbol entered)
- [ ] "Templates ▼" button shows template dropdown
- [ ] Toggle state persists in localStorage
- [ ] Mobile view collapses all by default

**Files to Modify:**
- `frontend/components/ExecuteTradeForm.tsx` - Add toggle sections
- `frontend/components/ui/CollapsibleSection.tsx` - New component

**Testing:**
- Default view shows 5 fields
- Click "Advanced Options" → Expands smoothly
- Click "Options Trading" → Shows options fields
- Refresh page → Toggle state persists

---

## P1-9: Pull-to-Refresh (Mobile)
**Impact:** Medium | **Effort:** Medium (2-3 days) | **Severity Score:** N/A

**Problem:**
- Mobile users must tap "Refresh" button
- Pull-to-refresh is standard on mobile apps
- High friction for frequent position checks

**Solution:**
Add pull-to-refresh gesture to:
1. ActivePositions (refresh positions + account balance)
2. WatchlistManager (refresh prices)
3. NewsReview (refresh news feed)

**Acceptance Criteria:**
- [ ] Pull down on position list → Refresh indicator appears
- [ ] Release triggers refresh API call
- [ ] Spinner shows during refresh (1-2s)
- [ ] Success toast: "✅ Positions updated"
- [ ] Works on iOS Safari, Android Chrome
- [ ] Does not conflict with page scroll

**Files to Modify:**
- `frontend/components/ActivePositions.tsx` - Add pull-to-refresh
- `frontend/components/WatchlistManager.tsx` - Add pull-to-refresh
- `frontend/components/NewsReview.tsx` - Add pull-to-refresh
- `frontend/hooks/usePullToRefresh.ts` - New hook

**Testing:**
- Pull down on position list → Refreshes
- Pull down on watchlist → Refreshes prices
- Pull down mid-scroll → Does not trigger
- iOS Safari + Android Chrome compatibility

---

## P1-10: Accessibility - Full ARIA Labels & Focus Indicators
**Impact:** Medium | **Effort:** Medium (3-4 days) | **Severity Score:** N/A

**Problem:**
- Many interactive elements missing ARIA labels
- Focus indicators invisible on some buttons
- Screen reader support incomplete

**Solution:**
Comprehensive accessibility audit + fixes:
1. Add ARIA labels to all interactive elements
2. Ensure visible focus indicators (2px outline)
3. Modal focus trapping (Tab stays within modal)
4. Live regions for dynamic updates (position P&L)

**Acceptance Criteria:**
- [ ] All buttons have `aria-label` or visible text
- [ ] All form inputs have `<label>` tags or `aria-label`
- [ ] Focus outline visible on all interactive elements (2px blue)
- [ ] Modal traps focus (Tab cycles within modal, Shift+Tab backward)
- [ ] Position P&L updates announce to screen reader (`aria-live="polite"`)
- [ ] Error messages have `role="alert"` (auto-announce)
- [ ] Loading states have `aria-busy="true"`
- [ ] WCAG AA compliance (tested with axe DevTools)

**Files to Modify:**
- All components (audit with axe DevTools)
- `frontend/components/ui/Modal.tsx` - Add focus trap
- `frontend/styles/theme.ts` - Add focus outline styles

**Testing:**
- Screen reader announces all elements correctly
- Tab order is logical
- Focus visible on all elements
- axe DevTools reports 0 violations

---

## P1-11 to P1-18: Additional High Priority Items
(Truncated for brevity - see full backlog for remaining P1 tickets)

---

# P2 - MEDIUM (Nice-to-Have)

## P2-1: Drawing Tools (Trendlines, Fibonacci)
**Impact:** Medium | **Effort:** Very High (10+ days)

**Problem:**
- Cannot draw trendlines or Fibonacci retracements on charts
- TradingView widget doesn't expose drawing API
- Users request manual chart annotation

**Solution:**
Options:
1. Upgrade TradingView plan to unlock drawing API
2. Build custom canvas layer over TradingView widget
3. Integrate alternative charting library (Lightweight Charts)

**Recommendation:** Upgrade TradingView plan (easiest path)

---

## P2-2 to P2-15: Additional Medium Priority Items
(See full backlog document)

---

# P3 - LOW (Future Enhancements)

## P3-1: Light Theme
**Impact:** Low | **Effort:** Medium (3-4 days)

**Problem:**
- Only dark theme available
- Some users prefer light themes
- Accessibility consideration (light sensitivity)

**Solution:**
Add light theme toggle in Settings

---

## P3-2 to P3-8: Additional Low Priority Items
(See full backlog document)

---

## Sprint Planning Recommendations

### Sprint 1 (Week 1-2): Quick Wins
- P0-1: Close Position Button (2 days)
- P0-8: Order Cancellation UI (1 day)
- P0-10: Error Messages with Actions (2 days)
- P0-12: Mobile Touch Targets (1 day)
- P1-7: Last Updated Timestamps (1 day)
**Total:** 7 days (1.5 weeks)

### Sprint 2 (Week 3-4): Critical Trading Features
- P0-2: Panic Button (4 days)
- P0-3: Order Modification UI (4 days)
- P0-11: AI Non-Blocking (2 days)
**Total:** 10 days (2 weeks)

### Sprint 3 (Week 5-6): Alerts & Risk Management
- P0-4: Price Alerts System (7 days)
- P0-5: Stop Loss UI (3 days)
**Total:** 10 days (2 weeks)

### Sprint 4 (Week 7-8): UX Polish
- P0-6: Enhanced Keyboard Shortcuts (4 days)
- P0-9: Symbol Autocomplete (3 days)
- P1-8: Progressive Disclosure (3 days)
**Total:** 10 days (2 weeks)

### Sprint 5 (Week 9-10): Advanced Trading
- P0-7: Backtesting Completion (7 days)
- P1-2: Position Sizing Calculator (3 days)
**Total:** 10 days (2 weeks)

### Sprints 6-10: Competitive Features
- P1-1: Multi-Leg Options (14 days)
- P1-3: Asset Allocation Chart (4 days)
- P1-4: Enhanced Scanner (4 days)
- P1-5: Risk Metrics (7 days)
- P1-6: RadialMenu Keyboard Nav (4 days)
**Total:** 33 days (6-7 weeks)

---

## Success Metrics

### Feature Completeness
- **Current:** 41% full implementation (28/68 features)
- **Target (Q1 2026):** 70% full implementation (48/68 features)
- **Measure:** Complete P0 + P1 tickets (30 tickets = 48 features)

### User Satisfaction
- **Current:** Baseline (no surveys yet)
- **Target:** 4.5+ stars on UX survey
- **Measure:** Post-release user survey on friction points

### Click Depth
- **Current:** 3.8 clicks average
- **Target:** ≤3.0 clicks average
- **Measure:** Track top 10 tasks click depth monthly

### Keyboard Efficiency
- **Current:** 6 shortcuts
- **Target:** 20+ shortcuts
- **Measure:** Shortcut usage analytics (track hotkey events)

### Mobile Usability
- **Current:** Basic responsive design
- **Target:** 90% mobile task completion rate
- **Measure:** Mobile analytics (bounce rate, task abandonment)

---

**End of UX Improvement Backlog**

*Refer to FEATURE_GAP_ANALYSIS.md and UX_FRICTION_ANALYSIS.md for detailed rationale.*
