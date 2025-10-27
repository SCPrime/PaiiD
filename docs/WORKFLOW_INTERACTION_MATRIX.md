# Workflow Interaction Matrix

**Generated:** 2025-10-27
**Purpose:** Comprehensive catalog of all interaction points across 10 radial menu workflows for UX audit and testing.

---

## 1. Morning Routine AI (`MorningRoutineAI.tsx`)

**Component Path:** `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend\components\MorningRoutineAI.tsx`
**Total Lines:** 1634
**Workflow Color:** `theme.workflow.morningRoutine` (Teal)

### Interaction Points (Total: 18)

#### View Toggle (P0 - Critical)
- **Dashboard View** (lines 639-1226) - Default landing view
- **Scheduler View** (lines 1228-1632) - Schedule automation

#### Dashboard View Interactions (9)
1. **Run Now Button** (lines 717-741)
   - Executes Under-$4 Multileg Workflow
   - Shows execution log modal
   - Calls `handleRunNow()` async function
   - **State:** `isRunning`, `executionLog`, `showExecutionLog`

2. **Schedule Button** (lines 743-751)
   - Switches to scheduler view
   - **State:** `setView('scheduler')`

3. **Refresh Live Data** (lines 848-859)
   - Manual refresh of market scan
   - **API:** `/api/market/scanner/under4`
   - **State:** `isLoadingLiveData`

4. **Run System Checks** (lines 1115-1121)
   - Manual trigger for health checks
   - 2-second mock delay
   - **State:** `loading`

5. **Live Data Preview** (lines 825-1016)
   - Under $4 scanner results
   - Auto-loads on mount
   - **API:** `fetchUnder4Scanner()`
   - Shows top 3 candidates

6. **Portfolio Metrics** (lines 1018-1098)
   - Loads from `/api/account` or user profile
   - Auto-refresh on mount
   - **State:** `portfolio`

7. **Market Status Widget** (lines 803-823)
   - Real-time market open/closed
   - Next event calculation

8. **Today's News** (lines 1177-1222)
   - Static news items (mock)
   - Impact badges (high/medium/low)

9. **Execution Log Panel** (lines 756-801)
   - Collapsible log viewer
   - Real-time AI analysis output
   - **State:** `showExecutionLog`

#### Scheduler View Interactions (9)
1. **Back to Dashboard** (lines 1297-1303)
   - Returns to dashboard view

2. **Enable Toggle** (lines 1324-1350)
   - Enable/disable morning routine
   - **State:** `scheduleEnabled`
   - Saves to localStorage

3. **Time Picker** (lines 1367-1383)
   - HTML time input
   - **State:** `scheduleTime`

4. **Frequency Selector** (lines 1386-1426)
   - Daily/Weekdays/Custom radio buttons
   - **State:** `scheduleFrequency`

5. **AI Builder Toggle** (lines 1448-1456)
   - Shows/hides AI routine builder
   - **State:** `showAIBuilder`

6. **AI Routine Input** (lines 1476-1527)
   - Textarea for natural language input
   - "Generate Routine" button
   - **API:** `claudeAI.generateMorningRoutine()`
   - **State:** `aiInput`, `isGenerating`, `error`

7. **Step Selection** (lines 1529-1566)
   - 6 available steps (checkboxes)
   - **State:** `selectedSteps[]`

8. **Preview Panel** (lines 1568-1621)
   - Shows selected steps preview
   - Morning briefing format

9. **Save Schedule** (lines 1624-1627)
   - Persists to localStorage
   - Updates user profile
   - **Function:** `handleSaveSchedule()`

### API Dependencies
- `/api/market/scanner/under4` (live market scan)
- `/api/account` (portfolio data)
- `claudeAI.generateMorningRoutine()` (AI generation)
- `claudeAI.chat()` (AI analysis)
- `fetchUnder4Scanner()` (market data service)

### State Management
- 14 useState hooks
- localStorage persistence for schedule
- User profile integration

### Known Issues
- None detected

---

## 2. Active Positions (`ActivePositions.tsx`)

**Component Path:** `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend\components\ActivePositions.tsx`
**Total Lines:** 1068

### Interaction Points (Total: 12)

#### Primary Actions (P0)
1. **Refresh Button** (lines 386-396)
   - Manual refresh positions
   - **Function:** `loadPositions()`

2. **Sort Controls** (lines 470-506)
   - 4 sort options: Symbol, P&L, P&L %, Value
   - **State:** `sortBy`

3. **Close Position Button** (lines 989-1007)
   - Per-position close action
   - Confirmation dialog
   - **API:** `alpaca.closePosition(symbol)`

4. **AI Insights Toggle** (lines 663-685)
   - Expand/collapse AI analysis per position
   - **State:** `expandedPositions` (Set)
   - **Function:** `toggleAIAnalysis()`

#### AI Analysis Panel (P1)
5. **AI Analysis Fetch** (lines 169-219)
   - Fetches on first expand
   - **API:** `/api/ai/analyze-symbol/${symbol}`
   - **State:** `aiAnalysisMap`, `aiLoadingMap`, `aiErrorMap`

6. **AI Metrics Display** (lines 737-984)
   - Recommendation badge (HOLD/ADD/TRIM/EXIT)
   - Confidence score
   - Risk level
   - Sentiment
   - Exit strategy (profit target, stop loss)

#### Real-Time Updates (P1)
7. **Auto-Refresh Polling** (lines 95-101)
   - REST API polling every 5 seconds
   - **Note:** SSE disabled (lines 73-92)

#### Data Display (P0)
8. **Portfolio Metrics Cards** (lines 421-467)
   - Total Value, Buying Power, Total P&L, Day P&L
   - Auto-calculated from positions

9. **Position Cards** (lines 523-1008)
   - Symbol, qty, entry price, current price
   - Unrealized P&L with color coding
   - Market value, return %

#### Empty States (P2)
10. **No Positions State** (lines 509-520)
    - Empty state with CTA
    - Navigate to execute workflow
    - Custom event dispatch

#### Loading States (P1)
11. **Skeleton Screens** (lines 410-418)
    - Loading state for initial load

12. **Error State** (lines 401-407)
    - Retry functionality
    - **Component:** `ErrorState`

### API Dependencies
- `/api/positions` (Alpaca positions)
- `/api/account` (account data)
- `/api/ai/analyze-symbol/${symbol}` (AI analysis)
- `alpaca.closePosition()` (close action)

### State Management
- 8 useState hooks
- REST polling (5s interval)
- Calculated metrics from positions array

### Known Issues
- SSE/WebSocket disabled (not reliable)

---

## 3. Execute Trade Form (`ExecuteTradeForm.tsx`)

**Component Path:** `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend\components\ExecuteTradeForm.tsx`
**Total Lines:** 1899

### Interaction Points (Total: 28)

#### Form Inputs (P0)
1. **Symbol Input** (lines 948-966)
   - Text input with uppercase transform
   - **State:** `symbol`

2. **Side Selector** (lines 1334-1365)
   - Buy/Sell dropdown
   - **State:** `side`

3. **Quantity Input** (lines 1368-1400)
   - Number input (min: 1)
   - **State:** `qty`

4. **Order Type** (lines 1402-1434)
   - Market/Limit dropdown
   - **State:** `orderType`

5. **Limit Price** (lines 1558-1593)
   - Conditional on limit order type
   - **State:** `limitPrice`

#### Asset Class Toggle (P0)
6. **Stock/Options Toggle** (lines 859-919)
   - Switch between asset classes
   - **State:** `assetClass`

#### Options Trading (P1)
7. **Option Type** (lines 1439-1471)
   - Call/Put selector
   - **State:** `optionType`

8. **Expiration Date** (lines 1473-1512)
   - Dropdown populated from API
   - **API:** `/api/options/chain?symbol=...`
   - **State:** `expirationDate`, `availableExpirations`

9. **Strike Price** (lines 1515-1554)
   - Dropdown populated from API
   - Auto-selects ATM strike
   - **State:** `strikePrice`, `availableStrikes`

10. **Options Greeks Display** (lines 1597-1625)
    - Live Greeks preview
    - **Component:** `OptionsGreeksDisplay`

11. **Risk Calculator** (lines 1628-1643)
    - Options-only risk analysis
    - **Component:** `RiskCalculator`

#### AI Analysis (P1)
12. **Auto AI Analysis** (lines 254-269)
    - Debounced symbol change (800ms)
    - **API:** `/api/ai/analyze-symbol/${symbol}`
    - **State:** `aiAnalysis`, `aiLoading`, `aiError`

13. **AI Metrics Panel** (lines 991-1331)
    - Confidence score badge
    - Summary, momentum, trend
    - Risk assessment
    - Support/resistance levels
    - Entry suggestion, stop loss, take profit

#### Stock Research (P1)
14. **Research Button** (lines 967-988)
    - Opens StockLookup panel
    - **State:** `showStockLookup`

15. **StockLookup Panel** (lines 1831-1879)
    - Full research interface
    - **Component:** `StockLookup`

#### Order Templates (P1)
16. **Template Selector** (lines 757-788)
    - Load saved order templates
    - **API:** `/api/order-templates`
    - **State:** `templates`, `selectedTemplateId`

17. **Save Template Button** (lines 748-754)
    - Opens save modal
    - **State:** `showSaveTemplate`

18. **Save Template Form** (lines 791-856)
    - Name and description inputs
    - **API:** `POST /api/order-templates`

19. **Delete Template** (lines 779-786)
    - Per-template delete action
    - **API:** `DELETE /api/order-templates/${id}`

#### Order Execution (P0)
20. **Submit Order** (lines 1646-1656)
    - Form validation
    - Opens confirmation dialog
    - **Function:** `handleSubmit()`

21. **Confirm Dialog** (lines 613-625, 1883-1895)
    - Order details review
    - Risk warning
    - **Component:** `ConfirmDialog`
    - **State:** `showConfirmDialog`, `pendingOrder`

22. **Execute Order** (lines 443-501)
    - POST to trading API
    - Duplicate detection
    - **API:** `/api/proxy/trading/execute`
    - **Function:** `executeOrder()`

23. **Test Duplicate** (lines 1651-1654)
    - Re-submit with same requestId
    - **Function:** `testDuplicate()`

#### Order Response (P1)
24. **Success Display** (lines 1677-1733)
    - Accepted/Duplicate badge
    - Dry-run indicator
    - Raw JSON toggle

25. **Error Display** (lines 1791-1828)
    - Error banner with icon
    - Error message

26. **Toast Notifications** (multiple)
    - Success: "Order accepted"
    - Warning: "Duplicate detected"
    - Error: "Order failed"

#### Pre-fill from Navigation (P1)
27. **Workflow Context** (lines 135-174)
    - Pre-fill from AI recommendations
    - **Context:** `useWorkflow()`
    - **State:** `pendingNavigation`

28. **Order History** (lines 484-492)
    - Add to history on execute
    - **Function:** `addOrderToHistory()`

### API Dependencies
- `/api/proxy/api/ai/analyze-symbol/${symbol}` (AI)
- `/api/options/chain` (options data)
- `/api/proxy/trading/execute` (order submission)
- `/api/order-templates` (CRUD operations)

### State Management
- 22 useState hooks
- WorkflowContext for pre-fill
- Form validation before submit

### Known Issues
- None detected

---

## 4. Market Scanner (`MarketScanner.tsx`)

**Component Path:** `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend\components\MarketScanner.tsx`
**Total Lines:** 704

### Interaction Points (Total: 14)

#### Search & Filters (P0)
1. **Symbol Search** (lines 298-310)
   - Text input with uppercase
   - Enter key trigger
   - **State:** `selectedSymbol`
   - **Function:** `handleSearch()`

2. **Search Button** (lines 310-325)
   - Execute search
   - Clears on empty

3. **Clear Search** (lines 514-532)
   - Reset to market scan
   - **State:** `setSelectedSymbol('')`

4. **Scan Type Buttons** (lines 348-359)
   - 4 types: Momentum, Breakout, Reversal, Custom
   - **State:** `scanType`
   - Triggers `runScan()` on change

5. **Price Filters** (lines 370-387)
   - Min/Max price inputs
   - **State:** `filter.minPrice`, `filter.maxPrice`

6. **Volume Filter** (lines 388-395)
   - Min volume input
   - **State:** `filter.minVolume`

7. **Signal Filter** (lines 396-409)
   - All/Buy/Sell dropdown
   - **State:** `filter.signalType`

8. **Scan Market Button** (lines 270-281)
   - Manual scan trigger
   - **Function:** `runScan()`
   - **State:** `loading`

#### Results Display (P0)
9. **Scan Results** (lines 442-601)
   - Card per result
   - Signal badges (color-coded)
   - Pattern tags
   - Technical indicators

10. **Research Button** (lines 523-533)
    - Opens StockLookup per result
    - **State:** `showResearch`, `selectedSymbol`

11. **Trade Button** (lines 534-544)
    - Navigate to execute trade
    - Alert placeholder

#### Stock Research Panel (P1)
12. **StockLookup Section** (lines 605-650)
    - Full research interface
    - Close button
    - **Component:** `StockLookup`
    - **State:** `showResearch`

#### Auto-Scan (P1)
13. **Initial Scan** (lines 114-116)
    - Auto-scan on mount and scanType change
    - **useEffect** with runScan callback

#### Empty/Loading States (P2)
14. **Empty State** (lines 429-440)
    - "No opportunities found" message

### API Dependencies
- `/api/proxy/screening/opportunities` (scan results)
- Query params: minPrice, maxPrice, minVolume, signalType, scanType

### State Management
- 5 useState hooks
- Auto-scan on filter/type change
- Debounced API calls

### Known Issues
- Trade button shows alert (not implemented)

---

## 5. AI Recommendations (`AIRecommendations.tsx`)

**Component Path:** `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend\components\AIRecommendations.tsx`
**Total Lines:** 307

### Interaction Points (Total: 5)

#### Data Refresh (P0)
1. **Refresh Button** (lines 252-258)
   - Manual refresh recommendations
   - **Function:** `fetchRecommendations()`
   - **State:** `isLoading`

2. **Auto-Refresh** (lines 93-99)
   - 5-minute interval
   - **useEffect** cleanup on unmount

#### Recommendation Cards (P0)
3. **Recommendation Display** (lines 232-285)
   - Grid of cards (buy/sell/hold)
   - Action badges (color-coded)
   - Confidence score
   - Risk level
   - Time horizon
   - Price target
   - Reasoning text

#### Status Indicators (P1)
4. **WebSocket Status** (lines 48-52, 243)
   - Connection indicator
   - **Hook:** `useWebSocket`
   - **State:** `isConnected`

5. **Market Outlook** (lines 263-274)
   - Overall market sentiment
   - Risk level summary

#### Error States (P2)
- **Error Display** (lines 192-207)
  - Retry button
  - **Component:** `EnhancedCard`

- **Loading State** (lines 209-218)
  - Spinner with message

- **Empty State** (lines 220-229)
  - "No recommendations available"

### API Dependencies
- `/api/ai/recommendations` (POST with symbols array)
- WebSocket: `process.env.NEXT_PUBLIC_WS_URL`

### State Management
- 5 useState hooks
- WebSocket hook
- Auto-refresh timer

### Known Issues
- Tailwind CSS classes used (inconsistent with project style)

---

## 6. Analytics Dashboard (`Analytics.tsx`)

**Component Path:** `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend\components\Analytics.tsx`
**Total Lines:** 1373

### Interaction Points (Total: 11)

#### Timeframe Selection (P0)
1. **Timeframe Buttons** (lines 672-682)
   - 5 options: 1W, 1M, 3M, 1Y, ALL
   - **State:** `timeframe`
   - Triggers `loadAnalytics()` on change

#### Portfolio Analysis (P0)
2. **AI Portfolio Health Check** (lines 689-711)
   - Opens AI analysis panel
   - **Function:** `fetchAIPortfolioAnalysis()`
   - **API:** `/api/ai/analyze-portfolio`
   - **State:** `aiLoading`, `aiAnalysis`, `showAiPanel`

3. **AI Analysis Panel** (lines 714-960)
   - Health score, risk level, diversification
   - AI summary, recommendations, risk factors
   - Opportunities
   - Close button
   - **State:** `showAiPanel`

#### Chart Export (P1)
4. **Export Equity Chart** (lines 1046-1065)
   - PNG export with html2canvas
   - Mobile-optimized
   - **Function:** `exportChartAsPNG()`
   - **State:** `exportingChart`

5. **Export P&L Chart** (lines 1123-1142)
   - PNG export with html2canvas
   - Mobile-optimized

#### Performance Metrics (P0)
6. **Metrics Display** (lines 979-1031)
   - 6 metric cards: Total Return, Annualized Return, Sharpe, Max Drawdown, Win Rate, Profit Factor
   - Color-coded values

7. **Portfolio Summary** (lines 64-288)
   - Total value, cash, buying power
   - Total/Day P&L
   - Position counts
   - Largest winner/loser
   - **API:** `/api/portfolio/summary`
   - **Component:** `PortfolioSummaryCard`

#### Charts (P0)
8. **Equity Curve** (lines 1034-1110)
   - Bar chart visualization
   - Sampled data points
   - Tooltip on hover

9. **Daily P&L Chart** (lines 1112-1193)
   - Bar chart (positive/negative)
   - Sampled data points

10. **Monthly Performance** (lines 1195-1242)
    - Grid of monthly stats
    - Profit, trades, win rate

#### TradingView Widget (P1)
11. **TradingView Chart** (lines 1244-1247)
    - Embedded $DJI chart
    - **Component:** `TradingViewChart`

#### Data Loading (P0)
- **Load Analytics** (lines 422-480)
  - **API:** `/api/analytics/performance?period=${timeframe}`
  - **API:** `/api/portfolio/history?period=${timeframe}`
  - Transforms backend data

### API Dependencies
- `/api/analytics/performance` (metrics)
- `/api/portfolio/history` (equity curve)
- `/api/portfolio/summary` (portfolio snapshot)
- `/api/ai/analyze-portfolio` (AI analysis)

### State Management
- 9 useState hooks
- Chart refs for export
- Auto-load on timeframe change

### Known Issues
- Monthly stats use placeholder function (backend TODO)

---

## 7. News Review (`NewsReview.tsx`)

**Component Path:** `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend\components\NewsReview.tsx`
**Total Lines:** 1321

### Interaction Points (Total: 18)

#### Search & Filters (P0)
1. **Symbol Search** (lines 482-498)
   - Text input with Enter key support
   - **State:** `searchSymbol`

2. **Search Button** (lines 499-513)
   - Execute symbol-specific search
   - **Function:** `handleSearch()`

3. **Clear Search** (lines 514-532)
   - Reset to market news
   - **Function:** `fetchNews()`

4. **Sentiment Filter** (lines 536-563)
   - 4 buttons: All, Bullish, Neutral, Bearish
   - **State:** `filter`
   - Color-coded badges

5. **Provider Filter** (lines 565-589)
   - Dropdown of news providers
   - **State:** `selectedProvider`
   - Fetched from `/api/news/providers`

6. **Refresh Button** (lines 592-607)
   - Manual refresh
   - **State:** `loading`

#### News Display (P0)
7. **Article Cards** (lines 650-843)
   - Title, summary, source, timestamp
   - Sentiment badge
   - Provider tag
   - Image (if available)
   - Click to open URL

8. **Symbol Tags** (lines 737-771)
   - Clickable stock symbols
   - Opens StockLookup
   - **State:** `selectedSymbol`, `showStockLookup`

9. **AI Analysis Button** (lines 808-829)
   - Per-article AI analysis
   - **Function:** `analyzeNewsWithAI()`
   - **State:** `aiLoading`

#### AI Analysis Panel (P1)
10. **AI Analysis Modal** (lines 876-1211)
    - Sentiment, confidence, portfolio impact, urgency
    - Tickers mentioned, affected positions
    - AI summary, key points, trading implications
    - Close button and background overlay
    - **State:** `showAiPanel`, `aiAnalysis`
    - **API:** `/api/ai/analyze-news` (POST)

#### Market Sentiment Widget (P0)
11. **Market Sentiment** (lines 416-469)
    - Overall sentiment (bullish/bearish/neutral)
    - Distribution percentages
    - Total articles count
    - **API:** `/api/news/sentiment/market`
    - **State:** `marketSentiment`

#### Stock Research (P1)
12. **StockLookup Section** (lines 1246-1315)
    - Full research interface
    - Close button
    - **Component:** `StockLookup`
    - **State:** `showStockLookup`

#### Pagination (P1)
13. **Load More** (lines 846-871)
    - Load next page
    - **State:** `page`, `hasMore`
    - **Function:** `fetchNews(symbol, true)`

#### Auto-Refresh (P1)
14. **5-Minute Refresh** (lines 162-178)
    - Auto-refresh timer
    - Refreshes news and sentiment
    - **useEffect** cleanup

#### Data Providers (P0)
15. **Provider Stats** (lines 405-412)
    - Count and list of providers
    - Last updated timestamp

#### Time Formatting (P2)
16. **Relative Timestamps** (lines 230-265)
    - "Just now", "5m ago", "2h ago"
    - **Function:** `formatDate()`
    - Error handling for malformed dates

#### Empty/Error States (P2)
17. **Empty State** (lines 637-648)
    - "No articles found" message

18. **Error State** (lines 611-624)
    - Error banner display

### API Dependencies
- `/api/news/market` (market news)
- `/api/news/company/${symbol}` (company news)
- `/api/news/sentiment/market` (market sentiment)
- `/api/news/providers` (news sources)
- `/api/ai/analyze-news` (AI analysis)

### State Management
- 14 useState hooks
- Auto-refresh timer
- Filter change triggers fetch

### Known Issues
- None detected

---

## 8. Strategy Builder AI (`StrategyBuilderAI.tsx`)

**Component Path:** `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend\components\StrategyBuilderAI.tsx`
**Total Lines:** 1289

### Interaction Points (Total: 22)

#### View Toggle (P0)
1. **Library/Create Tabs** (lines 356-372)
   - Toggle between views
   - **State:** `view`

#### Create View - AI Generation (P0)
2. **Natural Language Input** (lines 421-442)
   - Textarea with example placeholder
   - **State:** `nlInput`

3. **Generate Strategy** (lines 443-474)
   - AI strategy generation
   - **Function:** `handleGenerateStrategy()`
   - **API:** `claudeAI.generateStrategy()`
   - **State:** `isGenerating`, `error`

4. **Save Strategy** (lines 465-474)
   - Save to localStorage
   - **Function:** `handleSaveStrategy()`

#### Stock Research (P1)
5. **Research Symbol Input** (lines 506-528)
   - Text input with uppercase
   - **State:** `researchSymbol`

6. **Research Button** (lines 529-544)
   - Opens StockLookup
   - **State:** `showStockLookup`

7. **StockLookup Panel** (lines 547-568)
   - Full research interface
   - **Component:** `StockLookup`

#### Strategy Preview (P0)
8. **Strategy Display** (lines 571-752)
   - Name and status badge
   - Entry rules grid
   - Exit rules grid
   - Position sizing and risk metrics

#### Library View - Templates (P0)
9. **Template Gallery** (lines 760-1048)
   - Template cards with metrics
   - Compatibility score badge
   - Risk level badge
   - Performance stats (win rate, avg return, max DD)
   - Recommended for tags

10. **Quick Clone** (lines 1022-1029)
    - Clone template with default name
    - **Function:** `handleCloneTemplate()`
    - **API:** `POST /api/strategies/templates/${id}/clone`

11. **Customize Template** (lines 1030-1042)
    - Opens customization modal
    - **State:** `selectedTemplate`, `showCustomizationModal`

12. **Template Customization Modal** (lines 1274-1285)
    - **Component:** `TemplateCustomizationModal`
    - **Props:** template, onClose, onCloneSuccess

#### Library View - My Strategies (P0)
13. **Strategy Cards** (lines 1099-1267)
    - Name, status, created date
    - AI prompt preview
    - Entry/exit rule counts
    - Backtest results (if available)

14. **Edit Strategy** (lines 1240-1247)
    - Load into create view
    - **Function:** `handleEditStrategy()`

15. **Activate/Pause** (lines 1248-1256)
    - Toggle strategy status
    - **Function:** `handleActivateStrategy()`
    - **State:** `savedStrategies`

16. **Delete Strategy** (lines 1257-1262)
    - Confirmation dialog
    - **Function:** `handleDeleteStrategy()`

#### Data Loading (P1)
17. **Fetch Templates** (lines 144-181)
    - On library view open
    - **API:** `/api/strategies/templates`
    - **State:** `templates`, `isLoadingTemplates`, `templatesError`

18. **Load Saved Strategies** (lines 124-134)
    - From localStorage on mount
    - **State:** `savedStrategies`

19. **Save to localStorage** (lines 136-142)
    - Auto-save on strategies change

#### Empty States (P2)
20. **No Strategies** (lines 1073-1097)
    - Empty state with CTA
    - "Create Strategy" button

#### Loading States (P1)
21. **Template Loading** (lines 792-809)
    - Spinner with message

22. **Template Error** (lines 812-826)
    - Error banner with retry option

### API Dependencies
- `/api/strategies/templates` (template list)
- `/api/strategies/templates/${id}/clone` (clone template)
- `claudeAI.generateStrategy()` (AI generation)

### State Management
- 11 useState hooks
- localStorage persistence
- Template fetch on view change

### Known Issues
- TypeScript checking disabled (line 4 comment)

---

## 9. Backtesting (`Backtesting.tsx`)

**Component Path:** `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend\components\Backtesting.tsx`
**Total Lines:** 628

### Interaction Points (Total: 9)

#### Configuration (P0)
1. **Strategy Selector** (lines 201-211)
   - 4 strategies: RSI Reversal, MA Crossover, Breakout
   - **State:** `config.strategyName`

2. **Symbol Input** (lines 212-216)
   - Text input with uppercase
   - **State:** `config.symbol`

3. **Start Date** (lines 217-222)
   - Date picker
   - **State:** `config.startDate`

4. **End Date** (lines 223-228)
   - Date picker
   - **State:** `config.endDate`

5. **Initial Capital** (lines 229-235)
   - Number input
   - **State:** `config.initialCapital`

#### Execution (P0)
6. **Run Backtest** (lines 236-251)
   - Submit configuration
   - **Function:** `runBacktest()`
   - **API:** `POST /api/backtesting/run`
   - **State:** `isRunning`

#### Results Display (P0)
7. **Performance Metrics** (lines 274-325)
   - 6 metric cards: Total Return, Annualized, Sharpe, Max DD, Win Rate, Profit Factor
   - Color-coded values

8. **Equity Curve Chart** (lines 328-369)
   - Bar chart visualization
   - Sampled data (every 10th point)
   - Tooltip with date and value

9. **Trade History Table** (lines 416-553)
   - Date, type, price, quantity, P&L
   - Scrollable table
   - Color-coded buy/sell badges

#### Trade Statistics (P1)
- **Stats Grid** (lines 372-414)
  - Total trades, winning, losing
  - Avg win, avg loss
  - **Component:** `StatItem`

#### Loading State (P2)
- **Skeleton Loader** (lines 255-270)
  - While backtest running

### API Dependencies
- `POST /api/backtesting/run` (execute backtest)

### State Management
- 3 useState hooks
- Results cached until new run

### Known Issues
- Mock data generation functions commented out (lines 84-119)

---

## 10. Settings (`Settings.tsx`)

**Component Path:** `C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD\frontend\components\Settings.tsx`
**Total Lines:** 1738

### Interaction Points (Total: 45+)

#### Modal Control (P0)
1. **Close Button** (lines 641-653)
   - Close settings modal
   - **Props:** `onClose()`

#### Tab Navigation (P0)
2. **Tab Selector** (lines 674-710)
   - 19 tabs total (13 always visible, 6 admin-only)
   - **State:** `activeTab`

#### Personal Settings Tab (13 interactions)
3. **User Info Display** (lines 724-788)
   - Display name, email, account age, total sessions
   - **Function:** `getCurrentUser()`, `getUserAnalytics()`

4. **Clear User Data** (lines 772-786)
   - Confirmation dialog
   - **Function:** `clearUserData()`
   - Reloads page

5. **Execution Mode Radio** (lines 798-833)
   - Requires Approval vs Autopilot
   - **State:** `settings.defaultExecutionMode`

6. **Theme Toggle** (lines 843-878)
   - Dark/Light mode switcher
   - **Context:** `useTheme()`
   - **Function:** `toggleTheme()`

7. **Theme Preview** (lines 882-923)
   - Visual preview of theme

8. **SMS Alerts** (lines 933-967)
   - Checkbox toggle
   - **State:** `settings.enableSMSAlerts`

9. **Email Alerts** (lines 933-967)
   - Checkbox toggle
   - **State:** `settings.enableEmailAlerts`

10. **Push Notifications** (lines 933-967)
    - Checkbox toggle
    - **State:** `settings.enablePushNotifications`

11. **Paper Account Balance** (lines 969-1069)
    - Number input ($1K-$10M)
    - Update button
    - Validation with error display
    - Current account info display
    - **API:** `PATCH /users/preferences`
    - **State:** `paperAccountBalance`, `accountInfo`, `isLoadingBalance`, `balanceError`

12. **Slippage Budget** (lines 1078-1093)
    - Number input (0-1%)
    - **State:** `settings.defaultSlippageBudget`

13. **Max Reprices** (lines 1095-1108)
    - Number input (1-10)
    - **State:** `settings.defaultMaxReprices`

14. **Risk Tolerance Slider** (lines 1112-1234)
    - 0-100% slider with color-coded zones
    - Auto-updates on mouseup/touchend
    - Displays risk category, position limits
    - **API:** `PATCH /users/preferences` (risk_tolerance)
    - **API:** `GET /users/risk-limits`
    - **State:** `riskTolerance`, `riskLimits`, `isLoadingRisk`

#### Subscription Tab (P0)
15. **Subscription Manager** (line 1238)
    - **Component:** `SubscriptionManager`

#### Journal Tab (P0)
16. **Trading Journal** (line 1239)
    - **Component:** `TradingJournal`

#### Risk Tab (P0)
17. **Risk Dashboard** (line 1240)
    - **Component:** `RiskDashboard`

#### ML Training Tab (P0)
18. **ML Training Dashboard** (lines 1241-1245)
    - **Component:** `MLTrainingDashboard`

#### Pattern Backtest Tab (P0)
19. **Pattern Backtest Dashboard** (lines 1246-1250)
    - **Component:** `PatternBacktestDashboard`

#### ML Models Tab (P0)
20. **ML Model Management** (lines 1251-1255)
    - **Component:** `MLModelManagement`

#### ML Analytics Tab (P0)
21. **ML Analytics Dashboard** (lines 1256-1260)
    - **Component:** `MLAnalyticsDashboard`

#### Portfolio Optimizer Tab (P0)
22. **Portfolio Optimizer** (lines 1261-1265)
    - **Component:** `PortfolioOptimizer`

#### Sentiment Tab (P0)
23. **Sentiment Dashboard** (lines 1266-1270)
    - **Component:** `SentimentDashboard`

#### AI Chat Tab (P0)
24. **Claude AI Chat** (lines 1271-1275)
    - **Component:** `ClaudeAIChat`

#### Automation Tab (P0)
25. **Scheduler Settings** (lines 1276-1280)
    - **Component:** `SchedulerSettings`

#### Approvals Tab (P0)
26. **Approval Queue** (lines 1281-1285)
    - **Component:** `ApprovalQueue`

#### User Management Tab (Admin Only)
27. **User Cards** (lines 1411-1491)
    - User list with status badges
    - Suspend/Activate button
    - **Component:** `UserManagementTab`
    - **State:** `users`

#### Theme Tab (Admin Only)
28. **Color Pickers** (lines 1494-1538)
    - 6 theme colors with hex inputs
    - **Component:** `ThemeCustomizationTab`
    - **State:** `themeCustom`

#### Permissions Tab (Admin Only)
29. **Permission Checkboxes** (lines 1541-1585)
    - Per-user permission grid
    - **Component:** `PermissionsTab`
    - **Function:** `updateUserPermission()`

#### Telemetry Tab (Admin Only)
30. **Telemetry Toggle** (lines 1588-1657)
    - Enable/disable tracking
    - **Component:** `TelemetryTab`
    - **State:** `telemetryEnabled`

31. **Telemetry Table** (lines 1610-1645)
    - Event log display
    - **API:** `/api/telemetry/events`

32. **Export Report** (lines 1647-1654)
    - Download JSON report
    - **Function:** `exportTelemetryReport()`

#### Trading Control Tab (Admin Only)
33. **Kill Switch** (lines 1664-1670)
    - **Component:** `KillSwitchToggle`

34. **Trading Mode Toggle** (lines 1672-1734)
    - Paper vs Live per user
    - Owner-only control
    - **Component:** `TradingControlTab`
    - **Function:** `toggleTradingMode()`

#### Performance Tab (Admin Only)
35. **Performance Dashboard** (line 1333)
    - **Component:** `PerformanceDashboard`

#### GitHub Monitor Tab (Admin Only)
36. **GitHub Actions Monitor** (lines 1335-1339)
    - **Component:** `GitHubActionsMonitor`

#### Footer Actions (P0)
37. **Reset to Defaults** (lines 1353-1366)
    - Reset all settings
    - **Function:** `handleReset()`

38. **Cancel** (lines 1369-1381)
    - Close modal without saving

39. **Save Changes** (lines 1383-1403)
    - Persist to localStorage
    - **Function:** `handleSaveSettings()`
    - **State:** `isSaving`, `hasUnsavedChanges`, `saveMessage`

#### Auto-Load (P1)
40. **Load on Open** (lines 218-238)
    - Fetch settings from localStorage
    - Fetch risk tolerance and account balance from backend
    - Load mock users (admin)
    - Load telemetry (admin)

### API Dependencies
- `/users/preferences` (GET/PATCH - risk tolerance, paper balance)
- `/users/risk-limits` (GET)
- `/api/account` (GET - account info)
- `/api/telemetry/events` (GET)

### State Management
- 19 useState hooks
- ThemeContext
- localStorage persistence
- Multiple child components with props

### Known Issues
- Tailwind CSS classes used extensively (inconsistent with project style)

---

## Summary Statistics

| Workflow | Component | Total Lines | Interactions | P0 (Critical) | P1 (Important) | P2 (Nice) | API Endpoints |
|----------|-----------|-------------|--------------|---------------|----------------|-----------|---------------|
| 1 | MorningRoutineAI | 1634 | 18 | 12 | 5 | 1 | 4 |
| 2 | ActivePositions | 1068 | 12 | 6 | 4 | 2 | 3 |
| 3 | ExecuteTradeForm | 1899 | 28 | 10 | 14 | 4 | 4 |
| 4 | MarketScanner | 704 | 14 | 11 | 2 | 1 | 1 |
| 5 | AIRecommendations | 307 | 5 | 3 | 1 | 1 | 2 |
| 6 | Analytics | 1373 | 11 | 7 | 3 | 1 | 4 |
| 7 | NewsReview | 1321 | 18 | 9 | 5 | 4 | 5 |
| 8 | StrategyBuilderAI | 1289 | 22 | 14 | 6 | 2 | 2 |
| 9 | Backtesting | 628 | 9 | 7 | 1 | 1 | 1 |
| 10 | Settings | 1738 | 45+ | 30+ | 10+ | 5+ | 4 |
| **TOTAL** | **10 workflows** | **11,961** | **182+** | **109+** | **51+** | **22+** | **30+** |

## Priority Distribution

### P0 - Must Test (Critical Paths)
- **109+ interactions** requiring full testing coverage
- Includes all form submissions, data loads, primary actions
- **Failure impact:** Feature unusable or data loss

### P1 - Should Test (Important Features)
- **51+ interactions** requiring high testing priority
- Includes AI features, advanced filters, secondary workflows
- **Failure impact:** Degraded UX, workarounds needed

### P2 - Nice to Test (Edge Cases)
- **22+ interactions** for completeness testing
- Includes empty states, error handling, edge cases
- **Failure impact:** Minor UX issues

---

**Document Status:** COMPLETE
**Next Steps:** Create WORKFLOW_TEST_PLAN.md with detailed test procedures
