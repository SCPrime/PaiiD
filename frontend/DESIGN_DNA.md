# PaiiD Design DNA – Brand Guidelines (LOCKED)

**Version:** 1.0.0  
**Status:** 🔒 LOCKED – All UI changes must comply with this document  
**Validator:** `scripts/design-dna-validator.py`  
**Last Updated:** October 30, 2025

---

## Color Palette (Immutable)

### Primary Colors
- **Teal Primary:** `#16a394` (main CTA, accent elements)
- **Teal Secondary:** `#00ACC1` (workflow Morning Routine)
- **Purple Accent:** `#7E57C2` (workflow News Review, AI branding)
- **AI Glow Cyan:** `#45f0c0` (logo glow, AI assistant highlights)

### Workflow-Specific Colors (Radial Menu)
- Morning Routine: `#00ACC1` (teal)
- News Review: `#7E57C2` (purple)
- Proposals: `#0097A7` (dark teal)
- Active Positions: `#00C851` (green)
- P&L Dashboard: `#FF8800` (orange)
- Strategy Builder: `#5E35B1` (deep purple)
- Backtesting: `#00BCD4` (cyan)
- Execute Trade: `#FF4444` (red)
- Research: `#F97316` (orange)
- Settings: `#64748b` (slate gray)

### Background System
- **Base Dark:** `#0f172a` (primary background)
- **Card Background:** `rgba(30, 41, 59, 0.8)` (glassmorphic cards)
- **Card Hover:** `rgba(30, 41, 59, 0.95)` (on hover state)
- **Input Background:** `rgba(15, 24, 40, 0.9)` (form inputs)

### Text Colors
- **Primary Text:** `#f1f5f9` (bright, high contrast)
- **Muted Text:** `#cbd5e1` (secondary information)
- **Border Default:** `rgba(22, 163, 148, 0.3)` (teal with transparency)
- **Border Hover:** `rgba(22, 163, 148, 0.6)` (teal intensified)

### Status Colors
- **Success/Profit:** `#00C851` (green)
- **Warning:** `#FF8800` (orange)
- **Danger/Loss:** `#FF4444` (red)
- **Info:** `#00BCD4` (cyan)

---

## Glassmorphic System (Required)

### Backdrop Blur
**Rule:** All card/modal components MUST include `backdrop-filter: blur(...)` or Tailwind `backdrop-blur-*` classes.

- **Light Blur:** `blur(10px)` or `backdrop-blur-sm` (tooltips, popovers)
- **Medium Blur:** `blur(20px)` or `backdrop-blur-md` (cards, modals)
- **Heavy Blur:** `blur(30px)` or `backdrop-blur-lg` (full-screen overlays)

### Transparency Requirements
- Cards: 70-90% opacity (`rgba(30, 41, 59, 0.8)`)
- Overlays: 50% opacity (`bg-black/50`)
- Borders: 20-30% opacity (`rgba(255, 255, 255, 0.2)`)

### Glow Effects
All interactive elements use soft box-shadow glows (no hard shadows):

- **Green Glow:** `0 0 20px rgba(22, 163, 148, 0.3), 0 0 40px rgba(22, 163, 148, 0.15)`
- **Purple Glow:** `0 0 20px rgba(126, 87, 194, 0.3), 0 0 40px rgba(126, 87, 194, 0.15)`
- **Red Glow:** `0 0 20px rgba(255, 68, 68, 0.3), 0 0 40px rgba(255, 68, 68, 0.15)`
- **AI Glow:** `0 0 15px rgba(69, 240, 192, 0.8), 0 0 25px rgba(88, 255, 218, 0.5)`

**Banned:** Hard shadows (`box-shadow: 0 4px 6px rgba(0,0,0,0.1)`)

---

## Spacing System (Tailwind Tokens Only)

**Rule:** No arbitrary padding/margin values. Use Tailwind spacing scale only.

- **xs:** `4px` → `space-1` or `p-1`
- **sm:** `8px` → `space-2` or `p-2`
- **md:** `16px` → `space-4` or `p-4`
- **lg:** `24px` → `space-6` or `p-6`
- **xl:** `32px` → `space-8` or `p-8`

**Banned Examples:**
- `padding: 13px` (use `p-3` = 12px or `p-4` = 16px)
- `margin: 22px` (use `m-5` = 20px or `m-6` = 24px)

---

## Typography System

### Font Sizes
- **Headings:** `16px`, `18px`, `20px`, `24px` (Tailwind: `text-base`, `text-lg`, `text-xl`, `text-2xl`)
- **Body:** `14px` (Tailwind: `text-sm`)
- **Small:** `12px`, `13px` (Tailwind: `text-xs`)

**Minimum Touch-Target Font:** 16px (prevents iOS zoom on input focus)

### Font Weights
- **Regular:** `400` (body text)
- **Medium:** `500` (labels)
- **Semibold:** `600` (buttons, headings)
- **Bold:** `700` (primary CTAs only)

---

## Border Radius System

- **Small:** `6px` → `rounded-md`
- **Medium:** `12px` → `rounded-xl`
- **Large:** `16px` → `rounded-2xl`
- **Extra Large:** `20px` → `rounded-3xl`

**Cards:** Use `rounded-xl` (12px) as default  
**Buttons:** Use `rounded-md` (6px) as default  
**Modals:** Use `rounded-2xl` (16px) for top-level containers

---

## Animation Philosophy

### Timing
- **Fast:** `0.15s ease` (micro-interactions: button hover)
- **Normal:** `0.3s ease` (modal open/close, page transitions)
- **Slow:** `0.5s ease` (radial menu segment expansion)

**Rule:** All transitions use `ease` or `ease-in-out` (no `linear` or `ease-out` alone)

### Transform Interactions
- **Hover Lift:** `transform: translateY(-2px)` (buttons, cards)
- **Active Press:** `transform: scale(0.98)` (buttons on click)
- **Expand:** `transform: scale(1.05)` (radial menu segments)

**Banned:** Excessive transforms (>5px translate, >1.1 scale)

---

## Accessibility Requirements

### Minimum Standards (Auto-Enforced by axe-core)
- **Color Contrast:** 7:1 for normal text, 4.5:1 for large text (WCAG AA)
- **Touch Targets:** 40x40px minimum (44x44px preferred for primary CTAs)
- **Keyboard Navigation:** All interactive elements must be tabbable and have visible focus state
- **ARIA Labels:** All icons, custom controls, and D3.js visualizations must have `aria-label`

### Focus Indicators
- **Default:** `outline: 2px solid #16a394` (teal outline)
- **Offset:** `outline-offset: 2px`
- **Ring Alternative:** `ring-2 ring-teal-500 ring-offset-2` (Tailwind)

---

## Component Patterns (shadcn/ui Customization)

### Glass Variant (Required for All shadcn Components)

```tsx
// lib/utils.ts
export const glassVariants = {
  card: "bg-slate-800/80 backdrop-blur-md border border-white/10",
  dialog: "bg-slate-900/90 backdrop-blur-lg border border-teal-500/30",
  popover: "bg-slate-800/90 backdrop-blur-sm border border-white/20",
}
```

### Button Variants
- **Primary:** Teal background + green glow (CTAs)
- **Secondary:** Transparent + teal border (cancel, secondary actions)
- **Danger:** Red background + red glow (delete, close positions)
- **Ghost:** No background, teal text (tertiary actions)

### Card Variants
- **Default:** `bg-slate-800/80 backdrop-blur-md` (standard cards)
- **Elevated:** `bg-slate-800/95 backdrop-blur-md shadow-2xl` (modals, important content)
- **Glass:** `bg-white/5 backdrop-blur-md border border-white/10` (overlays)

---

## Banned Patterns

### Visual
- ❌ Solid backgrounds without transparency (breaks glassmorphic aesthetic)
- ❌ Hard drop shadows (use glow effects only)
- ❌ Gradients on text (use solid colors for readability)
- ❌ Colors outside approved palette (no random hex codes)

### Layout
- ❌ Arbitrary spacing values (use Tailwind scale)
- ❌ Inline styles in new components (use Tailwind classes)
- ❌ Fixed pixel widths >600px (use responsive units)
- ❌ Text overflow without ellipsis truncation

### Interaction
- ❌ Disabled buttons without visual indicator (must show opacity 0.6)
- ❌ Clickable elements without hover state
- ❌ Forms without loading states during submission
- ❌ Modals without Escape key handler

---

## Validation Rules (Automated)

### Pre-Commit Checks
1. No hex codes outside approved palette
2. No `padding:` or `margin:` with px values (use Tailwind)
3. No `background:` without `backdrop-filter:`
4. No buttons <40px height
5. All interactive elements have `aria-label` or child text

### CI/CD Checks
1. Percy visual diff <5% from baseline
2. axe-core accessibility score ≥90%
3. Lighthouse performance ≥85
4. Bundle size increase <10% per PR
5. No console errors in Playwright tests

---

## Locked Components (Do Not Modify Without Approval)

- `frontend/components/CompletePaiiDLogo.tsx` (🔒 LOCKED FINAL)
- `frontend/components/RadialMenu.tsx` (D3.js core logic locked; styling only)
- `frontend/styles/theme.ts` (color/spacing values locked; can add new keys)

---

## Version History

- **v1.0.0 (2025-10-30):** Initial DNA codification from existing theme.ts + UX friction analysis

