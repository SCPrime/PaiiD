# Mobile Responsive QA Checklist

## Environment
- App version: current development branch
- Test date: 2025-10-24
- Tester: Automated AI QA pass

## Device Viewports

### iOS (Safari emulation)
- [x] iPhone 15 Pro (390×844)
  - Radial menu loads without horizontal scroll; bottom info bar stacks vertically.
  - Swipe left/right on workflow content advances between workflows or returns to the menu.
  - Execute Trade form inputs render in a single column with full-width buttons and no clipped controls.

### Android (Chrome emulation)
- [x] Pixel 7 (412×915)
  - Morning Routine dashboards collapse to a single-column grid with readable cards.
  - Quick action buttons stretch to full width with consistent spacing.
  - Vertical scrolling preserved for long forms and AI analysis blocks.

## Regressions Checked
- [x] Desktop (1440×900) layout unaffected; split-pane view remains operational.
- [x] Keyboard shortcuts still navigate to Execute workflow on desktop.
- [x] Toast notifications and modals remain centered across breakpoints.

## Notes
- Swipe gestures require a horizontal movement (>60px) with minimal vertical drift to trigger navigation.
- Returning to the radial menu via swipe is available when swiping right on the first workflow panel.
