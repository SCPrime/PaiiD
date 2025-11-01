/**
 * Argos Visual Regression Tests
 * Cloud-hosted baselines with GitHub PR integration
 *
 * Provides full-page snapshots, approval workflows, and intelligent diffing
 */

import { test } from '@playwright/test';
import { argosScreenshot } from '@argos-ci/playwright';

test.describe('Argos Visual Regression - Full Application', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]', { timeout: 10000 });
  });

  test('homepage with radial menu', async ({ page }) => {
    await argosScreenshot(page, 'homepage-radial-menu', {
      fullPage: true,
    });
  });

  test('PaiiD logo branding', async ({ page }) => {
    const logo = page.locator('text=PaiiD').first();
    await argosScreenshot(page, 'paiid-logo-branding');
  });
});

test.describe('Argos Visual Regression - All 10 Radial Wedges', () => {
  const wedges = [
    { id: 'morning-routine', name: 'Morning Routine' },
    { id: 'news-review', name: 'News Review' },
    { id: 'proposals', name: 'Proposals' },
    { id: 'active-positions', name: 'Active Positions' },
    { id: 'my-account', name: 'My Account' },
    { id: 'strategy-builder', name: 'Strategy Builder' },
    { id: 'backtesting', name: 'Backtesting' },
    { id: 'execute', name: 'Execute Trade' },
    { id: 'dev-progress', name: 'Dev Progress' },
    { id: 'ml-intelligence', name: 'ML Intelligence' },
  ];

  for (const wedge of wedges) {
    test(`wedge workflow: ${wedge.name}`, async ({ page }) => {
      await page.goto('/');
      await page.waitForSelector('[data-testid="radial-menu"]');

      // Click wedge to activate split-screen
      const wedgeElement = page.locator(`[data-testid="wedge-${wedge.id}"]`);
      await wedgeElement.click();
      await page.waitForTimeout(500); // Wait for transition

      // Full-page snapshot of split-screen layout
      await argosScreenshot(page, `wedge-${wedge.id}-workflow`, {
        fullPage: true,
      });
    });
  }
});

test.describe('Argos Visual Regression - Responsive Breakpoints', () => {
  const viewports = [
    { name: 'desktop-4k', width: 3840, height: 2160 },
    { name: 'desktop-fhd', width: 1920, height: 1080 },
    { name: 'laptop', width: 1366, height: 768 },
    { name: 'tablet-landscape', width: 1024, height: 768 },
    { name: 'tablet-portrait', width: 768, height: 1024 },
    { name: 'mobile-large', width: 414, height: 896 }, // iPhone XR/11
    { name: 'mobile-standard', width: 375, height: 667 }, // iPhone SE
  ];

  for (const viewport of viewports) {
    test(`responsive layout at ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/');
      await page.waitForSelector('[data-testid="radial-menu"]');

      await argosScreenshot(page, `responsive-${viewport.name}`, {
        fullPage: true,
      });
    });
  }
});

test.describe('Argos Visual Regression - Interactive States', () => {
  test('wedge hover states', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]');

    // Hover over morning routine wedge
    const wedge = page.locator('[data-testid="wedge-morning-routine"]');
    await wedge.hover();
    await page.waitForTimeout(300);

    await argosScreenshot(page, 'wedge-hover-state');
  });

  test('focus states for keyboard navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]');

    // Tab to first interactive element
    await page.keyboard.press('Tab');
    await page.waitForTimeout(200);

    await argosScreenshot(page, 'keyboard-focus-state');
  });

  test('split-screen resizable panel', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]');

    // Activate split-screen
    await page.click('[data-testid="wedge-active-positions"]');
    await page.waitForTimeout(500);

    await argosScreenshot(page, 'split-screen-layout', {
      fullPage: true,
    });
  });
});

test.describe('Argos Visual Regression - Error States', () => {
  test('empty portfolio state', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="wedge-active-positions"]');
    await page.waitForTimeout(1000);

    // Screenshot empty state (if no positions exist)
    await argosScreenshot(page, 'empty-portfolio-state', {
      fullPage: true,
    });
  });

  test('loading skeleton screens', async ({ page }) => {
    // Intercept API calls to simulate loading state
    await page.route('**/api/proxy/api/**', (route) => {
      // Delay response to capture loading state
      setTimeout(() => route.continue(), 5000);
    });

    await page.goto('/');
    await page.click('[data-testid="wedge-news-review"]');

    // Capture loading state before timeout
    await page.waitForTimeout(200);
    await argosScreenshot(page, 'loading-skeleton-state');
  });
});

test.describe('Argos Visual Regression - Design DNA Compliance', () => {
  test('glassmorphic card styling', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="wedge-active-positions"]');
    await page.waitForTimeout(500);

    // Find glassmorphic card element
    const card = page.locator('[style*="backdrop-filter"]').first();
    if (await card.count() > 0) {
      await argosScreenshot(page, 'glassmorphic-card-design');
    }
  });

  test('teal brand color consistency', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]');

    // Screenshot areas with teal branding
    await argosScreenshot(page, 'teal-brand-colors');
  });

  test('dark theme glassmorphism', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]');

    // Full page to capture dark background + glass overlays
    await argosScreenshot(page, 'dark-theme-glassmorphism', {
      fullPage: true,
    });
  });
});

test.describe('Argos Visual Regression - Live Data Components', () => {
  test('center market indicators (SPY/QQQ)', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]');

    // Wait for live data to load
    await page.waitForTimeout(2000);

    // Screenshot radial menu center (with live market data)
    const radialMenu = page.locator('[data-testid="radial-menu"]');
    await argosScreenshot(page, 'live-market-indicators');
  });
});
