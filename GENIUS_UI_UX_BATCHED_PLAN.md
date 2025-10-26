# GENIUS UI/UX BATCHED PLAN

## Overview
This genius batched plan addresses the radial hub UX refinement with a focus on the locked iPi logo wrapper, AI chat box design, and elimination of clunky layout issues. All work follows the layered React implementation pattern established in the existing locked iPi logo components and maintains full consistency with the app's glassmorphic aesthetic.

---

## BATCH 1: INVENTORY CURRENT LAYERED IMPLEMENTATION AND IPI LOGO TOUCHPOINTS

### Objectives
- Map the complete layer hierarchy of the radial hub, locked iPi logo wrapper, and AI chat box
- Document all existing and planned iPi logo placements throughout the application
- Identify gaps and misalignments that prevent smooth investor workflows

### Tasks

#### 1.1 Audit Layer Hierarchy and Assets
- **Component Review**: Trace the composition and layer stack for:
  - `frontend/components/EnhancedRadialMenu.tsx`
  - `frontend/components/RadialMenu.tsx`
  - `frontend/components/RadialMenuNav.tsx`
  - `frontend/components/chat/*` (all chat-related components)
  - `frontend/public/radial-ui.html` (if applicable)

- **Context and State Mapping**: Document React context providers and state management:
  - `frontend/contexts/GlowStyleContext.tsx`
  - Glass/blur effect orchestration
  - Radial wedge data flow
  - Chat prompt state management

- **Z-Index and Animation Mapping**: Record all z-index values, animation triggers, and translucency tokens

#### 1.2 Catalog Present and Planned iPi Logo Placements
- **Current Placements**: Document every existing iPi logo usage in:
  - Radial hub center
  - Chat box header
  - Workflow dashboards
  - Modal overlays
  - Authentication screens

- **Future Requirements**: Coordinate with branding documentation:
  - Review `logo-audit.txt`
  - Review `LOGO_ABSOLUTE_PROTECTION.md`
  - Identify PaiiD-to-iPi swap points for premium promotion
  - Document onboarding screen insertions
  - Map promotional banner locations

#### 1.3 Review Layer Interactions
- Document how locked logo interacts with:
  - Wedge hover/active states
  - Chat box expansion/collapse
  - Split-screen transitions
  - Modal overlays

- Capture animation timing and easing functions
- Map focus trap and keyboard navigation flow

### Deliverables
- **Layer Stack Diagram**: Visual representation (Figma/Miro) showing:
  - Current logo layering
  - Wedge layering hierarchy
  - Chat box layer positioning
  - Interaction zones and touch targets

- **Gap Analysis Document**: List of:
  - Missing logo placements
  - Misaligned layer stacking
  - Broken interaction flows
  - Missing iPi promotion opportunities

---

## BATCH 2: DEFINE TARGET UX, LAYERED STATES, AND ALIGNMENT RULES

### Objectives
- Create a comprehensive state matrix for all interactive elements
- Establish future-proof iPi logo integration rules
- Map complete investor workflows to radial wedge responsibilities

### Tasks

#### 2.1 Create State Matrix for Radial Hub and Chat
- **Wedge States**: Define for each of 10 wedges:
  - Entry (initial render)
  - Hover (cursor over wedge)
  - Active (wedge selected)
  - Locked (in split-screen mode)
  - Transitional (animating between states)

- **Logo States**: Define for center iPi logo:
  - Idle (default with subtle pulse)
  - Hover (glow intensity increase)
  - Locked (PaiiD → iPi transformation)
  - Unlocked (iPi → PaiiD transformation)
  - Loading (spinner/progress indicator)

- **Chat States**: Define for AI chat box:
  - Collapsed (minimized state)
  - Expanding (slide-in animation)
  - Expanded (full chat interface)
  - Thinking (AI processing)
  - Responding (message streaming)

#### 2.2 Establish Future-Proof iPi Logo Rules
- **Usage Guidelines**: Document when iPi wrapped logo appears:
  - Premium feature access points
  - Authenticated session badge
  - Paid plan upsell triggers
  - Partner integrations

- **Lock/Unlock Behavior**: Define across layers:
  - Entry animation sequence
  - Click/tap interaction response
  - Long-press alternative actions
  - Keyboard accessibility (Enter/Space)

- **Cross-Layer Consistency**: Ensure rules support:
  - Trading partner overlays
  - Research tool integrations
  - Alert/notification systems
  - Multi-modal interactions

#### 2.3 Map Investor Workflows
- **Core Journey**: Research → Decision → Execution → Monitoring

- **Wedge Responsibilities** (10 stages):
  1. **Morning Routine**: Pre-market prep, AI briefing
  2. **Active Positions**: Portfolio overview, risk metrics
  3. **Execute Trade**: Order entry, limit/stop controls
  4. **Research**: Scanner, screener, fundamentals
  5. **AI Recommendations**: Claude-powered insights
  6. **P&L Dashboard**: Performance analytics, attribution
  7. **News Review**: Market events, sentiment analysis
  8. **Strategy Builder**: Rule creation, backtesting prep
  9. **Backtesting**: Historical simulation, optimization
  10. **Settings**: Preferences, API keys, alerts

- **iPi Logo Gateway Actions**: Define premium entry points:
  - Click logo → AI concierge summon
  - Long-press logo → Premium analytics unlock
  - Double-click logo → Account/billing modal

### Deliverables
- **UX Narrative Document**: Describes intended feel and style for:
  - Each wedge state transition
  - Logo interaction feedback
  - Chat box conversational flow
  - Premium upgrade pathways

- **Interaction Flowchart**: Updated diagram showing:
  - Current and future logo placements
  - State transitions with timing
  - Keyboard and touch navigation
  - Error/loading states

---

## BATCH 3: GEOMETRIC REFINEMENT AND LAYER-CONSISTENT LAYOUT TOKENS

### Objectives
- Eliminate clunky spacing and alignment issues in radial wedges
- Normalize styling tokens for consistent glassmorphism across layers
- Validate responsive behavior across all breakpoints

### Tasks

#### 3.1 Calibrate Wedge Geometry
- **Refine Calculations** in `EnhancedRadialMenu.tsx`:
  - Wedge angles (currently 360°/10 = 36° per wedge)
  - Inner radius (logo wrapper clearance)
  - Outer radius (responsive scaling)
  - Padding/margin between wedges

- **Parameterize for Scalability**:
  ```typescript
  interface RadialGeometry {
    wedgeCount: number;          // 10 (future-proof for 8-12 range)
    innerRadius: number;          // Logo wrapper clearance
    outerRadius: number;          // Container-relative
    gapAngle: number;             // Inter-wedge spacing
    centerOffset: { x: number; y: number }; // Viewport centering
  }
  ```

- **Center Logo Wrapper**: Ensure perfect centering:
  - At all viewport sizes (320px - 3840px width)
  - During split-screen transitions
  - With chat box overlay active

#### 3.2 Normalize Layer Tokens and Styling
- **Extract to Shared Utilities**:
  ```typescript
  // frontend/styles/layerTokens.ts
  export const LAYER_TOKENS = {
    glass: {
      background: 'rgba(15, 23, 42, 0.6)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
    },
    gradients: {
      teal: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
      green: 'rgba(16, 185, 129, 0.6)',
    },
    motion: {
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      duration: {
        fast: '150ms',
        normal: '300ms',
        slow: '500ms',
      },
    },
    zIndex: {
      radialHub: 10,
      logo: 20,
      chatBox: 30,
      modal: 40,
    },
  };
  ```

- **Synchronize Glow Effects**:
  - Radial hub wedge hover → Logo pulse intensity increase
  - Chat message sent → Logo acknowledgment flash
  - Trade executed → Green success glow (3s fade)

- **Update Components** to use shared tokens:
  - `EnhancedRadialMenu.tsx`
  - `RadialMenu.tsx`
  - `RadialMenuNav.tsx`
  - All chat box components
  - Logo wrapper component

#### 3.3 Responsive Layer Testing
- **Breakpoint Matrix**:
  - Mobile: 320px - 767px
  - Tablet: 768px - 1023px
  - Desktop: 1024px - 1919px
  - Ultra-wide: 1920px+

- **Test Scenarios**:
  - Logo wrapper stays centered
  - Wedges scale proportionally
  - Chat box doesn't overlap critical UI
  - Touch targets remain accessible (min 44x44px)

- **Validation Tools**:
  - Storybook component previews
  - Chrome DevTools responsive mode
  - Real device testing (iOS/Android)

### Deliverables
- **Design Tokens File**: `frontend/styles/layerTokens.ts` containing:
  - Geometry constants
  - Glass/gradient definitions
  - Animation timings
  - Z-index hierarchy

- **Before/After Comparison**:
  - Screenshots at each breakpoint
  - Measurement annotations showing spacing fixes
  - Layer depth visualization (side-view diagram)

---

## BATCH 4: POPULATE WEDGES AND CHAT HOOKS WITH INVESTOR-FOCUSED FEATURES

### Objectives
- Inventory current features and identify critical gaps
- Assign features to wedges with layer-awareness
- Update configuration schemas to support new features

### Tasks

#### 4.1 Audit Features and Gaps
- **Current Inventory** (per wedge):
  1. **Morning Routine**: AI briefing, market open countdown
  2. **Active Positions**: Holdings table, unrealized P&L
  3. **Execute Trade**: Stock/option order form, preview
  4. **Research**: Basic scanner, watch list
  5. **AI Recommendations**: Claude chat interface
  6. **P&L Dashboard**: Chart, performance metrics
  7. **News Review**: RSS feed aggregator
  8. **Strategy Builder**: Rule editor (partial)
  9. **Backtesting**: Historical replay (placeholder)
  10. **Settings**: API keys, preferences

- **Missing Features** (experienced investor requirements):
  - **Risk Controls**: Position size calculator, stop-loss suggestions
  - **Portfolio Analytics**: Sector allocation, correlation matrix
  - **Quick Actions**: One-click close position, double-down
  - **Alerts**: Price targets, volatility spikes, earnings
  - **Collaboration**: Share trades, notes, screenshots
  - **Advanced Orders**: Bracket, OCO, trailing stops
  - **Greeks Dashboard**: For options traders
  - **Sentiment Indicators**: Social volume, put/call ratio

#### 4.2 Place Features with Layer Awareness
- **Wedge Layer Assignments**:

  **Morning Routine** (Enhanced):
  - Layer 1 (Base): Market status indicators (SPY, QQQ, VIX)
  - Layer 2 (Interactive): Economic calendar, earnings today
  - Layer 3 (iPi Entry): "Get AI Briefing" button → Chat summon

  **Active Positions** (Enhanced):
  - Layer 1 (Base): Holdings grid with real-time updates
  - Layer 2 (Interactive): Quick action buttons (close, add, hedge)
  - Layer 3 (iPi Entry): "Optimize Portfolio" → Premium iPi tool

  **Execute Trade** (Enhanced):
  - Layer 1 (Base): Order entry form
  - Layer 2 (Interactive): Risk calculator overlay
  - Layer 3 (iPi Entry): "AI Position Sizing" → Chat context

  **Research** (Enhanced):
  - Layer 1 (Base): Scanner with filters
  - Layer 2 (Interactive): Chart overlay, fundamentals panel
  - Layer 3 (iPi Entry): "Deep Dive Analysis" → Premium research

  **AI Recommendations** (Enhanced):
  - Layer 1 (Base): Chat interface
  - Layer 2 (Interactive): Idea cards with backtest snapshots
  - Layer 3 (iPi Entry): "Advanced Strategies" → Upsell

  **P&L Dashboard** (Enhanced):
  - Layer 1 (Base): Performance chart
  - Layer 2 (Interactive): Attribution breakdown, filters
  - Layer 3 (iPi Entry): "Tax Loss Harvesting" → Premium

  **News Review** (Enhanced):
  - Layer 1 (Base): News feed
  - Layer 2 (Interactive): Sentiment heatmap, keyword alerts
  - Layer 3 (iPi Entry): "AI Summarization" → Chat feature

  **Strategy Builder** (Enhanced):
  - Layer 1 (Base): Rule editor
  - Layer 2 (Interactive): Condition library, templates
  - Layer 3 (iPi Entry): "Optimize Parameters" → Backtesting

  **Backtesting** (Enhanced):
  - Layer 1 (Base): Historical replay controls
  - Layer 2 (Interactive): Equity curve, trade log
  - Layer 3 (iPi Entry): "Walk-Forward Analysis" → Premium

  **Settings** (Enhanced):
  - Layer 1 (Base): Preferences form
  - Layer 2 (Interactive): API connection status
  - Layer 3 (iPi Entry): "Upgrade to iPi Pro" → Billing

- **iPi Logo Cross-Layer Shortcuts**:
  - Long-press logo anywhere → Context-aware AI chat
  - Double-click logo → Quick trade ticket (last symbol)
  - Alt+click logo → Emergency close all positions

#### 4.3 Plan Configuration Updates
- **Schema Definition**:
  ```typescript
  interface WedgeConfig {
    id: string;
    title: string;
    icon: string;
    layers: {
      base: ReactNode;        // Always visible
      interactive: ReactNode; // Hover/active only
      iPiEntry: {             // Premium gateway
        label: string;
        action: () => void;
        requiresAuth: boolean;
      };
    };
    chatHooks: {
      quickPrompt: string;    // Pre-filled message
      context: Record<string, any>; // Session data
    };
  }
  ```

- **Metadata Requirements**:
  - Icon asset paths (SVG)
  - Logo state mappings (PaiiD vs. iPi)
  - Chat prompt templates
  - Feature flag keys (for gradual rollout)

### Deliverables
- **Feature-to-Layer Mapping Sheet**: Spreadsheet with:
  - Wedge name
  - Feature description
  - Layer assignment (1/2/3)
  - Dependencies (API endpoints, components)
  - Priority (P0/P1/P2)

- **Copy and Iconography Lists**:
  - Button labels
  - Tooltip text
  - Error messages
  - Icon asset inventory (existing + needed)

- **Draft Configuration JSON**: Example wedge configs ready for implementation

---

## BATCH 5: IMPLEMENT LAYERED INTERACTION AND VISUAL CONSISTENCY

### Objectives
- Code layer-by-layer following git hygiene best practices
- Harmonize animations and focus management
- Establish comprehensive testing matrix

### Tasks

#### 5.1 Incremental Coding Strategy
- **Implementation Order**:
  1. **Core Geometry** (Batch 3 deliverables)
     - Update `layerTokens.ts`
     - Refactor `EnhancedRadialMenu.tsx` calculations
     - Commit: `refactor(radial): apply calibrated geometry tokens`

  2. **Logo Wrapper Alignment**
     - Center logo positioning
     - Z-index hierarchy enforcement
     - Commit: `fix(logo): ensure perfect centering across breakpoints`

  3. **Wedge Content Layers**
     - Implement base, interactive, iPi entry layers per wedge
     - Apply shared glass/gradient tokens
     - Commit per wedge: `feat(wedge-1): add layered morning routine features`

  4. **Chat Integration**
     - Chat hooks from logo and wedges
     - Context passing from wedge to chat
     - Commit: `feat(chat): integrate context-aware AI prompts`

  5. **Animation Synchronization**
     - Shared motion controllers
     - Glow pulse synchronization
     - Commit: `feat(animation): synchronize logo and wedge interactions`

#### 5.2 Harmonize Interactions
- **Shared Animation Controller** (Framer Motion):
  ```typescript
  // frontend/lib/animationController.ts
  import { AnimationControls, useAnimation } from 'framer-motion';

  export const useRadialAnimations = () => {
    const logoControls = useAnimation();
    const wedgeControls = useAnimation();
    const chatControls = useAnimation();

    const syncGlow = async () => {
      await Promise.all([
        logoControls.start({ opacity: [0.6, 1, 0.6] }),
        wedgeControls.start({ borderColor: '#10b981' }),
      ]);
    };

    return { logoControls, wedgeControls, chatControls, syncGlow };
  };
  ```

- **Focus Management**:
  - Tab order: Wedges (clockwise) → Logo → Chat
  - Focus rings: 2px solid teal with 4px blur shadow
  - Focus trap in modals (React Focus Lock)

- **Accessibility (ARIA)**:
  - `role="navigation"` on radial hub
  - `aria-label` for each wedge
  - `aria-expanded` for chat box
  - `aria-live="polite"` for AI responses

#### 5.3 Build Testing Matrix
- **Automated Tests** (Jest + Testing Library):
  ```typescript
  describe('RadialHub Layers', () => {
    it('renders 10 wedges with correct geometry', () => {});
    it('centers logo at all breakpoints', () => {});
    it('maintains z-index hierarchy', () => {});
    it('syncs glow on wedge hover', () => {});
    it('opens chat with context on logo long-press', () => {});
  });
  ```

- **Manual Test Scenarios**:
  - **Hover**: Each wedge shows interactive layer
  - **Click**: Wedge activates, logo locks to iPi state
  - **Drag**: (Future) Reorder wedges
  - **Touch**: Mobile long-press for context menus
  - **Chat Invocation**: Logo click, wedge "Ask AI" buttons

- **Logo Swap Verification**:
  - Free tier: PaiiD logo always visible
  - Paid tier: iPi logo on authentication
  - Upsell: PaiiD→iPi flash animation on premium CTA

### Deliverables
- **Pull Request Checklist**:
  - [ ] Updated tests passing (coverage >80%)
  - [ ] Visual diffs approved (Chromatic/Percy)
  - [ ] Accessibility audit passing (axe DevTools)
  - [ ] Mobile gestures tested (iOS Safari, Android Chrome)
  - [ ] High-contrast mode validated (WCAG AAA)

- **QA Playbook**: Document with:
  - Test scenario descriptions
  - Expected vs. actual behavior tables
  - Regression test suite (cross-layer interactions)
  - Performance benchmarks (FPS, interaction latency)

---

## BATCH 6: DOCUMENT AND OPERATIONALIZE THE LAYERED SYSTEM

### Objectives
- Update design system and engineering documentation
- Provide developer onboarding and QA resources
- Align roadmap with iPi-first branding strategy

### Tasks

#### 6.1 Update Documentation
- **Design System Refresh**:
  - File: `COMPONENT_ARCHITECTURE.md`
    - Add "Layered Radial Hub" section
    - Document layer responsibilities (base, interactive, iPi)
    - Include code examples

  - File: `RADIAL_MENU_GLASS_ENHANCEMENT.md`
    - Update with new geometry tokens
    - Add animation synchronization patterns
    - Document iPi logo integration points

  - New file: `LAYER_SYSTEM_GUIDE.md`
    - Philosophy: Why layers matter
    - Pattern library: Reusable layer compositions
    - Anti-patterns: What to avoid

- **Logo Usage Rules**:
  - File: `LOGO_ABSOLUTE_PROTECTION.md` (update)
    - Add iPi wrapped logo variants
    - Document lock/unlock states
    - Specify premium gateway usage

  - New file: `IPI_INTEGRATION_SPEC.md`
    - Complete inventory of placements
    - Animation specifications
    - A/B test criteria for PaiiD vs. iPi

#### 6.2 Provide Playbooks and Training
- **Developer Onboarding Guide**:
  - File: `frontend/docs/RADIAL_HUB_DEVELOPER_GUIDE.md`
    - Architecture overview
    - How to add a new wedge
    - How to add iPi logo touchpoint
    - Common pitfalls and solutions
    - Code walkthrough with annotations

- **QA Scripts and Dashboards**:
  - File: `frontend/tests/E2E_RADIAL_HUB_TESTS.md`
    - Automated Playwright/Cypress tests
    - Manual smoke test checklist
    - Regression test suite

  - Dashboard (Grafana/Datadog):
    - Layer render performance
    - Logo interaction analytics
    - Chat engagement metrics
    - Premium conversion funnel

#### 6.3 Align Governance and Roadmaps
- **Roadmap Synchronization**:
  - File: `PAIID_MIGRATION_STAGES.md` (update)
    - Add "Radial Hub Refinement" milestone
    - Link to Batch 1-6 deliverables
    - Define success metrics

  - File: `STRATEGIC_NEXT_BATCHES.md` (update)
    - Batch 7: Mobile gesture optimization
    - Batch 8: Advanced animations (parallax, micro-interactions)
    - Batch 9: Accessibility audit and WCAG AAA compliance
    - Batch 10: Performance optimization (lazy loading, code splitting)

- **iPi-First Branding Strategy**:
  - Ensure all new features default to iPi logo where appropriate
  - PaiiD logo reserved for free tier and legacy support
  - Premium features always gated by iPi touchpoints

### Deliverables
- **Consolidated Layered UX and Engineering Handbook**:
  - Single markdown file: `RADIAL_HUB_COMPLETE_GUIDE.md`
  - Combines design, engineering, and QA documentation
  - Ready for copy/paste distribution to team members

- **Backlog of Follow-On Tasks**:
  - Jira/Linear tickets tagged by layer:
    - `layer:geometry` - Layout refinements
    - `layer:logo` - iPi integration expansions
    - `layer:chat` - AI capabilities enhancements
    - `layer:feature` - New investor tools

  - Prioritized by:
    - P0: Critical for launch
    - P1: High-value, near-term
    - P2: Nice-to-have, future consideration

---

## IMPLEMENTATION TIMELINE

### Phase 1: Foundation (Batches 1-2)
- **Duration**: 1-2 weeks
- **Team**: 1 designer + 1 frontend engineer
- **Deliverables**: Layer diagrams, UX narrative, flowcharts

### Phase 2: Refinement (Batch 3)
- **Duration**: 1 week
- **Team**: 1 frontend engineer
- **Deliverables**: Geometry tokens, responsive validation

### Phase 3: Feature Population (Batch 4)
- **Duration**: 2-3 weeks
- **Team**: 2 frontend engineers + 1 product manager
- **Deliverables**: Feature mapping, configuration schemas

### Phase 4: Implementation (Batch 5)
- **Duration**: 3-4 weeks
- **Team**: 2-3 frontend engineers + 1 QA engineer
- **Deliverables**: Code commits, tests, QA playbook

### Phase 5: Documentation (Batch 6)
- **Duration**: 1 week
- **Team**: 1 technical writer + 1 frontend engineer
- **Deliverables**: Handbooks, dashboards, roadmap updates

**Total Estimated Duration**: 8-11 weeks

---

## SUCCESS METRICS

### User Experience
- **Interaction Latency**: <100ms from hover to visual feedback
- **Animation Smoothness**: 60 FPS on all interactions
- **Accessibility**: WCAG 2.1 Level AA compliance (target AAA)
- **Mobile Usability**: >4.5/5 score on touch target size and spacing

### Feature Adoption
- **Wedge Engagement**: >70% of users interact with ≥5 wedges per session
- **Chat Invocation**: >40% of users summon AI chat within first 3 minutes
- **iPi Touchpoint Clicks**: >25% click-through rate on premium CTAs

### Technical Performance
- **Bundle Size**: <500KB for radial hub module (gzipped)
- **First Contentful Paint**: <1.5s
- **Time to Interactive**: <3s
- **Lighthouse Score**: >90/100

### Business Impact
- **Premium Conversion**: >15% of free users upgrade after iPi touchpoint interaction
- **Retention**: >80% weekly active user retention (vs. current baseline)
- **NPS**: >50 (investor segment)

---

## RISK MITIGATION

### Technical Risks
- **Risk**: Geometry calculations break on edge-case screen sizes
  - **Mitigation**: Extensive responsive testing, CSS container queries

- **Risk**: Z-index conflicts with third-party embeds (TradingView, etc.)
  - **Mitigation**: Document z-index hierarchy, use CSS isolation

### UX Risks
- **Risk**: Users confused by layered interactions
  - **Mitigation**: Onboarding tooltips, progressive disclosure

- **Risk**: iPi logo change alienates existing users
  - **Mitigation**: A/B test, gradual rollout, user education

### Business Risks
- **Risk**: Premium features don't justify upgrade cost
  - **Mitigation**: User research, pricing experiments, feature bundling

---

## APPENDIX

### A. Referenced Files
- `frontend/components/EnhancedRadialMenu.tsx`
- `frontend/components/RadialMenu.tsx`
- `frontend/components/RadialMenuNav.tsx`
- `frontend/contexts/GlowStyleContext.tsx`
- `frontend/styles/layerTokens.ts` (new)
- `COMPONENT_ARCHITECTURE.md`
- `RADIAL_MENU_GLASS_ENHANCEMENT.md`
- `LOGO_ABSOLUTE_PROTECTION.md`
- `PAIID_MIGRATION_STAGES.md`
- `STRATEGIC_NEXT_BATCHES.md`

### B. Design Tokens Example
```typescript
export const LAYER_TOKENS = {
  glass: {
    background: 'rgba(15, 23, 42, 0.6)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
  },
  gradients: {
    teal: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
    green: 'rgba(16, 185, 129, 0.6)',
  },
  motion: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    duration: { fast: '150ms', normal: '300ms', slow: '500ms' },
  },
  zIndex: {
    radialHub: 10,
    logo: 20,
    chatBox: 30,
    modal: 40,
  },
};
```

### C. Wedge Configuration Schema
```typescript
interface WedgeConfig {
  id: string;
  title: string;
  icon: string;
  layers: {
    base: ReactNode;
    interactive: ReactNode;
    iPiEntry: {
      label: string;
      action: () => void;
      requiresAuth: boolean;
    };
  };
  chatHooks: {
    quickPrompt: string;
    context: Record<string, any>;
  };
}
```

---

## CONCLUSION

This comprehensive batched plan provides a methodical, layer-by-layer approach to refining the radial hub UX while strategically integrating the iPi wrapped logo throughout the application. By following this plan, the PaiiD platform will achieve:

1. **Consistent Visual Language**: All components share glassmorphic tokens and motion patterns
2. **Investor-Focused Workflows**: Each wedge provides essential tools with premium upgrade paths
3. **Strategic iPi Promotion**: Logo placements drive awareness and conversions
4. **Maintainable Codebase**: Layered architecture supports future enhancements without technical debt

The plan is designed for copy/paste distribution and can be executed by a cross-functional team over 8-11 weeks, with clear deliverables, success metrics, and risk mitigation strategies at every stage.
