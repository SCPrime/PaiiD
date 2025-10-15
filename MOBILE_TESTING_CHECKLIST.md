# PaiiD - MOBILE TESTING CHECKLIST

**Document Version:** 1.0
**Last Updated:** October 15, 2025
**Status:** Ready for Device Testing
**Test Coverage:** 10 workflows × 2 platforms = 20 test scenarios

---

## 📱 TESTING SCOPE

### Platforms to Test
- **iOS:** Safari (iPhone 12, 13, 14, 15 models)
- **Android:** Chrome (Samsung Galaxy S21+, Google Pixel 6+)

### Screen Sizes
- **Mobile Portrait:** 375px - 430px width (primary focus)
- **Mobile Landscape:** 667px - 932px width (secondary)
- **Tablet:** 768px - 1024px width (bonus coverage)

### Browser Compatibility
- **iOS:** Safari 15+ (primary), Chrome 100+ (secondary)
- **Android:** Chrome 100+ (primary), Firefox 100+ (secondary)

---

## 🎯 TESTING CRITERIA

### 1. Layout & Typography
- [ ] All text readable without horizontal scrolling
- [ ] Font sizes appropriate for mobile (minimum 14px body text)
- [ ] Headers properly scaled (reduced on mobile)
- [ ] No overlapping elements
- [ ] Grid layouts stack correctly (1 column mobile)
- [ ] Spacing appropriate (not too cramped)

### 2. Touch Interactions
- [ ] Buttons have minimum 44×44px touch targets
- [ ] All clickable elements respond to touch
- [ ] No accidental clicks on nearby elements
- [ ] Hover states replaced with active/focus states
- [ ] Form inputs keyboard-accessible
- [ ] Dropdowns work on mobile browsers

### 3. Forms & Inputs
- [ ] Forms stack vertically on mobile
- [ ] Input fields full-width or properly sized
- [ ] Number inputs work with mobile keyboards
- [ ] Dropdowns open native mobile pickers
- [ ] Labels visible and aligned
- [ ] Validation messages visible

### 4. Charts & Visualizations
- [ ] Charts render at appropriate size
- [ ] Chart heights reduced for mobile (200-400px)
- [ ] Chart export buttons work on mobile
- [ ] No chart overflow or horizontal scroll
- [ ] Tooltips accessible on touch
- [ ] TradingView widget responsive

### 5. Navigation & Modals
- [ ] Radial menu accessible on mobile
- [ ] Modal widths responsive (95vw mobile)
- [ ] Modal content scrollable
- [ ] Close buttons easy to tap
- [ ] Workflow selection works on touch
- [ ] Back navigation functional

### 6. Performance
- [ ] Page load under 3 seconds on 4G
- [ ] Smooth scrolling (no janky animations)
- [ ] No layout shifts during load
- [ ] Images optimized for mobile
- [ ] API calls don't block UI
- [ ] Real-time updates work on mobile

---

## 🔬 WORKFLOW-SPECIFIC TEST SCENARIOS

### 1. Morning Routine AI (MorningRoutineAI.tsx)

**Layout Tests:**
- [ ] Dashboard header stacks vertically on mobile
- [ ] Icon size: 32px → 24px (scaled down)
- [ ] Title size: 28px → 20px (scaled down)
- [ ] Portfolio grid: 4 columns → 2 columns mobile
- [ ] Frequency grid: 3 columns → 1 column mobile
- [ ] Routine steps grid: 2 columns → 1 column mobile

**Interaction Tests:**
- [ ] "Generate Routine" button full-width mobile
- [ ] "Save Schedule" button full-width mobile
- [ ] Time picker works on mobile browsers
- [ ] Frequency selector buttons tap-friendly
- [ ] Routine step cards readable and accessible

**Data Tests:**
- [ ] Portfolio metrics display correctly
- [ ] AI-generated routines render properly
- [ ] Schedule saves successfully on mobile
- [ ] Real-time market data loads

---

### 2. Active Positions (ActivePositions.tsx)

**Layout Tests:**
- [ ] Header: row → column layout mobile
- [ ] Logo size: 42px → 28px (scaled down)
- [ ] Title size: 32px → 24px (scaled down)
- [ ] Portfolio metrics: auto-fit → 1 column mobile
- [ ] Position cards stack vertically
- [ ] Root padding reduced on mobile

**Interaction Tests:**
- [ ] Connection status indicator visible
- [ ] WiFi icon shows Live/Connecting/Offline
- [ ] Position cards tap to expand details
- [ ] Refresh button works on mobile
- [ ] Real-time SSE updates functional

**Data Tests:**
- [ ] Positions load from Alpaca API
- [ ] P&L calculations accurate
- [ ] Real-time price updates via SSE
- [ ] Connection status reflects actual state
- [ ] Fallback polling works when SSE disconnects

---

### 3. Execute Trade (ExecuteTradeForm.tsx)

**Layout Tests:**
- [ ] Form fields stack vertically
- [ ] Symbol input full-width
- [ ] Quantity/Price inputs appropriately sized
- [ ] Order type dropdown full-width
- [ ] Stop loss/Take profit side-by-side → stacked mobile
- [ ] Submit button full-width mobile

**Interaction Tests:**
- [ ] Symbol autocomplete works on mobile
- [ ] Number inputs trigger numeric keyboard
- [ ] Order type selector tap-friendly
- [ ] Research button accessible
- [ ] Template selector dropdown works
- [ ] "Save as Template" button functional

**Data Tests:**
- [ ] Pre-fill from AI analysis works
- [ ] Order validation before submission
- [ ] Success/error toasts visible on mobile
- [ ] Order templates load and save

---

### 4. Market Scanner (MarketScanner.tsx)

**Layout Tests:**
- [ ] Header stacks vertically on mobile
- [ ] Icon/title scaled down
- [ ] Scanner results grid: auto-fit → 1 column mobile
- [ ] Filter grid: auto-fit → 1 column mobile
- [ ] Action buttons stack and full-width mobile
- [ ] Indicators grid: auto-fit → 2 columns mobile

**Interaction Tests:**
- [ ] "Scan Now" button full-width mobile
- [ ] Filter inputs tap-friendly
- [ ] Scan results cards tappable
- [ ] "Research" button on each result works
- [ ] Sort/filter controls accessible

**Data Tests:**
- [ ] Scanner fetches real market data
- [ ] Filters apply correctly
- [ ] Results update in real-time
- [ ] Technical indicators display

---

### 5. AI Recommendations (AIRecommendations.tsx)

**Layout Tests:**
- [ ] Header stacks on mobile
- [ ] Portfolio analysis: 3 → 1 columns
- [ ] Recommendation headers: grid → flex column
- [ ] Entry/Exit details: 4 → 1 columns
- [ ] Technical indicators: 2 → 1 columns
- [ ] Badges wrap properly

**Interaction Tests:**
- [ ] "Get Recommendations" button full-width
- [ ] Recommendation cards tap to expand
- [ ] "Research" button on each recommendation works
- [ ] Badge tooltips accessible on touch
- [ ] Market context banner readable

**Data Tests:**
- [ ] AI recommendations load from backend
- [ ] Volatility and sector data display
- [ ] Momentum/volume badges accurate
- [ ] Scoring system functional
- [ ] Real market data integrated

---

### 6. P&L Dashboard (Analytics.tsx)

**Layout Tests:**
- [ ] Portfolio summary grid: 2 → 1 columns mobile
- [ ] Equity curve height: 300 → 200px mobile
- [ ] Daily P&L chart: 200 → 150px mobile
- [ ] TradingView chart: 600 → 400px mobile
- [ ] Metrics cards stack vertically

**Interaction Tests:**
- [ ] Chart export buttons work (icon-only on mobile)
- [ ] Export triggers PNG download on mobile
- [ ] TradingView controls tap-friendly
- [ ] Chart tooltips accessible on touch
- [ ] Timeframe selector works on mobile

**Data Tests:**
- [ ] Real P&L data from Alpaca
- [ ] Equity curve renders correctly
- [ ] Daily P&L calculations accurate
- [ ] TradingView symbol updates
- [ ] Chart exports preserve styling

---

### 7. News Review (NewsReview.tsx)

**Layout Tests:**
- [ ] Market sentiment stacks vertically
- [ ] Article images hidden on mobile (bandwidth optimization)
- [ ] Stock research section responsive
- [ ] Article cards full-width
- [ ] Symbol badges wrap properly

**Interaction Tests:**
- [ ] Articles tap to open in new tab
- [ ] Symbol badges tap to research
- [ ] Filter controls accessible
- [ ] Infinite scroll works on mobile
- [ ] Pull-to-refresh (if implemented)

**Data Tests:**
- [ ] News loads from aggregators
- [ ] Symbol filtering works
- [ ] Date range filtering functional
- [ ] Images load (or hidden on mobile)
- [ ] Cache system functional

---

### 8. Strategy Builder AI (StrategyBuilderAI.tsx)

**Layout Tests:**
- [ ] Strategy preview: 2 → 1 columns
- [ ] Template gallery: auto-fill → 1 column mobile
- [ ] Performance metrics: 3 → 1 columns
- [ ] Entry/Exit rules: 2 → 1 columns
- [ ] Template cards stack vertically

**Interaction Tests:**
- [ ] Template cards tap to expand
- [ ] "Quick Clone" button works
- [ ] "Customize" button opens modal
- [ ] Modal responsive (700px → 95vw mobile)
- [ ] Form inputs keyboard-accessible

**Data Tests:**
- [ ] Templates load from backend
- [ ] Compatibility scores calculate
- [ ] Risk tolerance integration works
- [ ] Template cloning functional
- [ ] Customization saves correctly

---

### 9. Backtesting (Backtesting.tsx)

**Layout Tests:**
- [ ] Header wraps on mobile, logo/title scaled down
- [ ] Configuration grid: auto-fit → 1 column mobile
- [ ] Run Backtest button: full-width mobile
- [ ] Metrics grid: auto-fit → 1 column mobile
- [ ] Equity curve height: 300px → 200px mobile
- [ ] Trade statistics: auto-fit → 2 columns mobile

**Interaction Tests:**
- [ ] Date pickers work on mobile
- [ ] Strategy selector dropdown accessible
- [ ] "Run Backtest" button tap-friendly
- [ ] Results table scrollable horizontally
- [ ] Chart interactive on touch

**Data Tests:**
- [ ] Backtesting engine runs correctly
- [ ] Historical data loads
- [ ] Results calculate accurately
- [ ] Equity curve renders
- [ ] Trade log displays

---

### 10. Settings (Settings.tsx)

**Layout Tests:**
- [ ] Modal width: 1200px → 95vw mobile
- [ ] Account analytics grid: 2 → 1 columns
- [ ] Risk limits grid: 2 → 1 columns
- [ ] Theme/Permissions/User grids mobile-responsive
- [ ] Tab navigation touch-friendly

**Interaction Tests:**
- [ ] Tab switching works on mobile
- [ ] Risk tolerance slider touch-responsive
- [ ] Toggle switches tap-friendly
- [ ] Save buttons full-width mobile
- [ ] Kill-switch confirmation modal works

**Data Tests:**
- [ ] User preferences load
- [ ] Settings save successfully
- [ ] API token validation works
- [ ] Theme changes apply immediately
- [ ] Permissions update correctly

---

### 11. Template Customization Modal (TemplateCustomizationModal.tsx)

**Layout Tests:**
- [ ] Modal width: 700px → 95vw mobile
- [ ] Template info banner: 4 → 2 columns mobile
- [ ] Stop Loss/Take Profit grid: side-by-side → stacked
- [ ] Action buttons: horizontal → vertical mobile
- [ ] Preview section readable on mobile

**Interaction Tests:**
- [ ] Close button easy to tap
- [ ] Input fields keyboard-accessible
- [ ] Slider controls touch-responsive
- [ ] "Clone Strategy" button full-width
- [ ] Parameter changes update preview

**Data Tests:**
- [ ] Template data loads correctly
- [ ] Parameter overrides apply
- [ ] Preview calculations accurate
- [ ] Clone creates new strategy
- [ ] Toast notifications visible

---

## ✅ SIGN-OFF CRITERIA

### Critical Issues (Must Fix Before Launch)
- No layout breaking issues on primary devices
- All forms functional on mobile
- No critical touch target issues
- Charts render correctly
- Real-time updates work on mobile

### High Priority (Fix Before Public Launch)
- All 10 workflows tested on iOS Safari and Android Chrome
- Performance acceptable on 4G networks
- No accessibility blockers
- Navigation smooth and intuitive
- Modal interactions work perfectly

### Medium Priority (Post-Launch if Needed)
- Landscape mode optimization
- Tablet optimization
- Secondary browser compatibility (Firefox, Edge mobile)
- Advanced touch gestures (swipe, pinch-to-zoom)
- Offline mode functionality

---

## 📊 TESTING PROGRESS TRACKER

### iOS Safari Testing
- [ ] Morning Routine AI
- [ ] Active Positions
- [ ] Execute Trade
- [ ] Market Scanner
- [ ] AI Recommendations
- [ ] P&L Dashboard (Analytics)
- [ ] News Review
- [ ] Strategy Builder AI
- [ ] Backtesting
- [ ] Settings
- [ ] Template Customization Modal

### Android Chrome Testing
- [ ] Morning Routine AI
- [ ] Active Positions
- [ ] Execute Trade
- [ ] Market Scanner
- [ ] AI Recommendations
- [ ] P&L Dashboard (Analytics)
- [ ] News Review
- [ ] Strategy Builder AI
- [ ] Backtesting
- [ ] Settings
- [ ] Template Customization Modal

---

## 🐛 ISSUES LOG

### Critical Issues (P0)
*No issues currently logged*

### High Priority (P1)
*No issues currently logged*

### Medium Priority (P2)
*No issues currently logged*

### Low Priority (P3)
*No issues currently logged*

---

## 📝 TESTING NOTES

**Code Implementation:**
- All 10 workflows enhanced with `useIsMobile()` hook
- 76 successful edits across 10 files
- 0 compilation errors
- Production build verified (0 TypeScript errors)
- Systematic pattern: `gridTemplateColumns: isMobile ? '1fr' : 'repeat(N, 1fr)'`

**Expected Behavior:**
- Grids should collapse to 1-2 columns on mobile
- Font sizes should scale down (e.g., 32px → 24px)
- Buttons should become full-width on mobile
- Modals should expand to 95vw on mobile
- Charts should reduce height (e.g., 600px → 400px)
- Images may be hidden on mobile for bandwidth optimization

**Known Limitations:**
- TradingView widget has its own responsive behavior (not fully customizable)
- Some third-party libraries (react-hot-toast) have fixed mobile positioning
- Browser-specific behavior for date/time pickers
- Native mobile scrolling may differ from desktop

---

## 🚀 NEXT STEPS

1. **Immediate:** Test on primary devices (iPhone 13 + Samsung Galaxy S21)
2. **Within 24h:** Test all critical workflows (Morning Routine, Active Positions, Execute Trade)
3. **Within 48h:** Complete full test matrix (10 workflows × 2 platforms)
4. **Within 72h:** Fix critical issues (P0) and high priority (P1)
5. **Before launch:** Retest all fixed issues and sign off

---

**Testing Lead:** [To be assigned]
**Start Date:** [To be scheduled]
**Target Completion:** [To be scheduled]
**Status:** ⏳ Ready for device testing

---

_Last updated: October 15, 2025 - Mobile UI implementation complete, ready for physical device testing_
