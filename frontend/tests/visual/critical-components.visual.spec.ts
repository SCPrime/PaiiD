/**
 * Playwright Native Visual Regression Tests
 * Critical components for DESIGN_DNA compliance
 *
 * Tests logo branding, radial menu, glassmorphic styling, and all 10 wedges
 */

import { test, expect } from '@playwright/test';

test.describe('Visual Regression - Critical Components', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page before each test
    await page.goto('/');
    // Wait for radial menu to render
    await page.waitForSelector('[data-testid="radial-menu"]', { timeout: 10000 });
  });

  test('PaiiD logo matches DESIGN_DNA colors', async ({ page }) => {
    // CRITICAL: All letters use teal (#1a7560) + green glow (#10b981)
    const logo = page.locator('text=PaiiD').first();

    await expect(logo).toHaveScreenshot('paiid-logo.png', {
      maxDiffPixelRatio: 0.05, // 5% threshold
    });
  });

  test('Radial menu full view matches baseline', async ({ page }) => {
    const radialMenu = page.locator('[data-testid="radial-menu"]');

    // Mask dynamic content (portfolio values, timestamps, live market data)
    await expect(page).toHaveScreenshot('radial-menu-full.png', {
      mask: [
        page.locator('text=/\\$[0-9,]+\\.[0-9]{2}/'), // Dollar amounts
        page.locator('text=/[0-9]{1,2}:[0-9]{2}/'), // Timestamps
        page.locator('text=/[+-][0-9.]+%/'), // Percentage changes
      ],
      maxDiffPixelRatio: 0.05,
    });
  });

  test('Radial menu center logo and live data', async ({ page }) => {
    const centerLogo = page.locator('[data-testid="radial-menu"]').locator('svg').first();

    await expect(centerLogo).toHaveScreenshot('radial-center-logo.png', {
      mask: [
        page.locator('text=/SPY|QQQ/').locator('..'), // Mask live ticker data
      ],
      maxDiffPixels: 100,
    });
  });
});

test.describe('Visual Regression - Radial Menu Wedges', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]');
  });

  const wedges = [
    { id: 'morning-routine', name: 'Morning Routine', color: '#00ACC1' },
    { id: 'news-review', name: 'News Review', color: '#7E57C2' },
    { id: 'proposals', name: 'Proposals', color: '#FF9800' },
    { id: 'active-positions', name: 'Active Positions', color: '#4CAF50' },
    { id: 'my-account', name: 'My Account', color: '#2196F3' },
    { id: 'strategy-builder', name: 'Strategy Builder', color: '#9C27B0' },
    { id: 'backtesting', name: 'Backtesting', color: '#FF5722' },
    { id: 'execute', name: 'Execute Trade', color: '#FF4444' },
    { id: 'dev-progress', name: 'Dev Progress', color: '#607D8B' },
    { id: 'ml-intelligence', name: 'ML Intelligence', color: '#00BCD4' },
  ];

  for (const wedge of wedges) {
    test(`wedge ${wedge.name} hover state`, async ({ page }) => {
      const wedgeElement = page.locator(`[data-testid="wedge-${wedge.id}"]`);

      // Hover over wedge
      await wedgeElement.hover();
      await page.waitForTimeout(300); // Wait for hover animation

      await expect(wedgeElement).toHaveScreenshot(`wedge-${wedge.id}-hover.png`, {
        maxDiffPixels: 150,
      });
    });

    test(`wedge ${wedge.name} active state`, async ({ page }) => {
      const wedgeElement = page.locator(`[data-testid="wedge-${wedge.id}"]`);

      // Click wedge to activate
      await wedgeElement.click();
      await page.waitForTimeout(500); // Wait for split-screen transition

      // Screenshot the full split-screen view
      await expect(page).toHaveScreenshot(`wedge-${wedge.id}-active.png`, {
        mask: [
          page.locator('text=/\\$[0-9,]+\\.[0-9]{2}/'),
          page.locator('text=/[0-9]{1,2}:[0-9]{2}/'),
          page.locator('text=/[+-][0-9.]+%/'),
        ],
        maxDiffPixelRatio: 0.05,
        fullPage: true,
      });
    });
  }
});

test.describe('Visual Regression - Glassmorphic Styling', () => {
  test('glassmorphic card with backdrop-blur', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]');

    // Click Active Positions wedge to show glassmorphic cards
    await page.click('[data-testid="wedge-active-positions"]');
    await page.waitForTimeout(500);

    // Find first glassmorphic card
    const card = page.locator('[style*="backdrop-filter"]').first();

    if (await card.count() > 0) {
      await expect(card).toHaveScreenshot('glassmorphic-card.png', {
        maxDiffPixels: 100,
      });
    }
  });
});

test.describe('Visual Regression - Responsive Design', () => {
  const viewports = [
    { name: 'desktop', width: 1920, height: 1080 },
    { name: 'laptop', width: 1366, height: 768 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 667 },
  ];

  for (const viewport of viewports) {
    test(`radial menu at ${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/');
      await page.waitForSelector('[data-testid="radial-menu"]');

      await expect(page).toHaveScreenshot(`radial-menu-${viewport.name}.png`, {
        mask: [
          page.locator('text=/\\$[0-9,]+\\.[0-9]{2}/'),
          page.locator('text=/[+-][0-9.]+%/'),
        ],
        maxDiffPixelRatio: 0.05,
        fullPage: true,
      });
    });
  }
});

test.describe('Visual Regression - Accessibility Focus States', () => {
  test('focus indicator matches DESIGN_DNA (teal outline)', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]');

    // Tab to first interactive element
    await page.keyboard.press('Tab');
    await page.waitForTimeout(200);

    // Screenshot focused element
    const focused = page.locator(':focus');
    await expect(focused).toHaveScreenshot('focus-state.png', {
      maxDiffPixels: 50,
    });
  });

  test('keyboard navigation through wedges', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="radial-menu"]');

    // Tab through multiple elements
    for (let i = 0; i < 3; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(100);
    }

    await expect(page).toHaveScreenshot('keyboard-navigation.png', {
      maxDiffPixelRatio: 0.05,
    });
  });
});
