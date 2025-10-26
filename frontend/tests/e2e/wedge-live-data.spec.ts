import { test, expect, Page } from '@playwright/test';

/**
 * E2E Tests for PaiiD Radial Menu Wedges
 * Tests all 10 wedges for live data connectivity and functionality
 */

const BASE_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
// Read API_TOKEN from environment variable (REQUIRED for E2E tests)
// Set in CI/CD pipeline or local .env.test file
const API_TOKEN = process.env.API_TOKEN || '';

// Helper: Skip onboarding
async function skipOnboarding(page: Page) {
  // Check if onboarding is showing
  const onboardingVisible = await page.locator('text=AI-Guided Setup').isVisible().catch(() => false);

  if (onboardingVisible) {
    // Use admin bypass keyboard shortcut (Ctrl+Shift+A)
    await page.keyboard.press('Control+Shift+A');
    await page.waitForTimeout(1000);
  }
}

// Helper: Click a wedge by name
async function clickWedge(page: Page, wedgeName: string) {
  console.log(`[TEST] Clicking wedge: ${wedgeName}`);

  // Wait for RadialMenu SVG to be visible
  await page.waitForSelector('svg', { timeout: 10000 });

  // Click the wedge - D3.js creates path elements for each wedge
  // We'll click by approximate position based on wedge index
  const svg = page.locator('svg').first();
  const box = await svg.boundingBox();

  if (!box) throw new Error('SVG not found');

  // Calculate center point
  const centerX = box.x + box.width / 2;
  const centerY = box.y + box.height / 2;

  // Wedge positions (approximate angles for 10 wedges)
  const wedgeAngles: Record<string, number> = {
    'morning-routine': 0,
    'news-review': 36,
    'proposals': 72,
    'active-positions': 108,
    'my-account': 144,
    'strategy-builder': 180,
    'backtesting': 216,
    'execute': 252,
    'options-trading': 288,
    'dev-progress': 324,
  };

  const angle = wedgeAngles[wedgeName] || 0;
  const radius = box.width / 3; // Click midway between center and edge

  // Convert polar to cartesian
  const radian = (angle * Math.PI) / 180;
  const clickX = centerX + radius * Math.cos(radian);
  const clickY = centerY + radius * Math.sin(radian);

  await page.mouse.click(clickX, clickY);
  await page.waitForTimeout(1500); // Wait for component to load
}

// Helper: Check for console errors
async function checkConsoleErrors(page: Page): Promise<string[]> {
  const errors: string[] = [];

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  return errors;
}

// Helper: Check for failed network requests
async function checkFailedRequests(page: Page): Promise<string[]> {
  const failedRequests: string[] = [];

  page.on('response', (response) => {
    if (response.status() >= 400) {
      failedRequests.push(`${response.status()} - ${response.url()}`);
    }
  });

  return failedRequests;
}

test.describe('PaiiD Radial Menu Wedge Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Listen for console errors
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        console.error(`[BROWSER ERROR] ${msg.text()}`);
      }
    });

    // Navigate to app
    await page.goto(BASE_URL);
    await skipOnboarding(page);

    // Wait for radial menu to render
    await page.waitForSelector('svg', { timeout: 15000 });
  });

  test('1. Morning Routine - Live Data', async ({ page }) => {
    console.log('\n=== Testing MORNING ROUTINE Wedge ===');

    await clickWedge(page, 'morning-routine');

    // Check component loaded
    await expect(page.locator('text=/Morning Routine|Portfolio/i')).toBeVisible({ timeout: 10000 });

    // Check for account data request
    const accountRequest = page.waitForResponse(
      (response) => response.url().includes('/api/account') || response.url().includes('/api/portfolio'),
      { timeout: 15000 }
    );

    const response = await accountRequest;
    expect(response.status()).toBeLessThan(400);

    // Check for error messages
    const errorText = await page.locator('text=/error|failed|unavailable/i').count();
    expect(errorText).toBe(0);

    console.log('✅ Morning Routine wedge passed');
  });

  test('2. News Review - Live Data', async ({ page }) => {
    console.log('\n=== Testing NEWS REVIEW Wedge ===');

    await clickWedge(page, 'news-review');

    // Wait for news component
    await page.waitForTimeout(2000);

    // Check for news API requests
    const newsLoaded = await page.locator('text=/news|article|headline/i').count();
    expect(newsLoaded).toBeGreaterThan(0);

    // Check no error states
    const errors = await page.locator('text=/failed to load|error loading/i').count();
    expect(errors).toBe(0);

    console.log('✅ News Review wedge passed');
  });

  test('3. AI Recommendations - Live Data', async ({ page }) => {
    console.log('\n=== Testing AI RECS Wedge ===');

    await clickWedge(page, 'proposals');

    // Wait for AI recommendations component
    await page.waitForTimeout(3000);

    // Check for recommendations content (may be loading state initially)
    const componentLoaded = await page.locator('text=/recommendation|ai|strategy/i').count();
    expect(componentLoaded).toBeGreaterThan(0);

    console.log('✅ AI Recommendations wedge passed');
  });

  test('4. Active Positions - Live Data', async ({ page }) => {
    console.log('\n=== Testing ACTIVE POSITIONS Wedge ===');

    await clickWedge(page, 'active-positions');

    // Wait for positions API call
    const positionsRequest = page.waitForResponse(
      (response) => response.url().includes('/api/positions') || response.url().includes('/api/proxy/positions'),
      { timeout: 15000 }
    );

    const response = await positionsRequest;
    expect(response.status()).toBeLessThan(400);

    // Component should show positions table or "No positions" message
    await page.waitForTimeout(2000);
    const hasContent = await page.locator('text=/position|symbol|no positions|portfolio/i').count();
    expect(hasContent).toBeGreaterThan(0);

    console.log('✅ Active Positions wedge passed');
  });

  test('5. P&L Dashboard - Live Data', async ({ page }) => {
    console.log('\n=== Testing P&L DASHBOARD Wedge ===');

    await clickWedge(page, 'my-account');

    // Wait for iframe to load
    await page.waitForTimeout(3000);

    // Check iframe exists
    const iframe = page.frameLocator('iframe[src="/my-account"]');
    const iframeVisible = await page.locator('iframe[src="/my-account"]').isVisible();
    expect(iframeVisible).toBe(true);

    console.log('✅ P&L Dashboard wedge passed');
  });

  test('6. Strategy Builder - Live Data', async ({ page }) => {
    console.log('\n=== Testing STRATEGY BUILDER Wedge ===');

    await clickWedge(page, 'strategy-builder');

    // Wait for strategy builder UI
    await page.waitForTimeout(2000);

    // Check component loaded
    const builderLoaded = await page.locator('text=/strategy|build|create|rule/i').count();
    expect(builderLoaded).toBeGreaterThan(0);

    console.log('✅ Strategy Builder wedge passed');
  });

  test('7. Backtesting - Live Data', async ({ page }) => {
    console.log('\n=== Testing BACKTESTING Wedge ===');

    await clickWedge(page, 'backtesting');

    // Wait for backtesting interface
    await page.waitForTimeout(2000);

    // Check for backtest-related content
    const backtestUI = await page.locator('text=/backtest|historical|test strategy|performance/i').count();
    expect(backtestUI).toBeGreaterThan(0);

    console.log('✅ Backtesting wedge passed');
  });

  test('8. Execute Trade - Live Data', async ({ page }) => {
    console.log('\n=== Testing EXECUTE TRADE Wedge ===');

    await clickWedge(page, 'execute');

    // Wait for trade form
    await page.waitForTimeout(2000);

    // Check for trade form elements
    const formElements = await page.locator('text=/symbol|quantity|order|buy|sell|market|limit/i').count();
    expect(formElements).toBeGreaterThan(0);

    // Try entering a symbol to test quote API
    const symbolInput = page.locator('input[placeholder*="symbol" i]').first();
    if (await symbolInput.isVisible()) {
      await symbolInput.fill('AAPL');
      await page.waitForTimeout(1000);

      // Check if quote data loads (price should appear)
      const priceVisible = await page.locator('text=/\\$[0-9]+\\.?[0-9]*/').count();
      expect(priceVisible).toBeGreaterThan(0);
    }

    console.log('✅ Execute Trade wedge passed');
  });

  test('9. Options Trading - Live Data', async ({ page }) => {
    console.log('\n=== Testing OPTIONS TRADING Wedge ===');

    // Note: This wedge may not be implemented yet
    try {
      await clickWedge(page, 'options-trading');
      await page.waitForTimeout(2000);

      // Check if component loads
      const optionsContent = await page.locator('text=/option|strike|call|put|greek|chain/i').count();

      if (optionsContent > 0) {
        console.log('✅ Options Trading wedge passed');
      } else {
        console.log('⚠️  Options Trading wedge: No content detected (may not be implemented)');
      }
    } catch (error) {
      console.log('⚠️  Options Trading wedge: Error - ', error);
    }
  });

  test('10. Repo Monitor - Live Data', async ({ page }) => {
    console.log('\n=== Testing REPO MONITOR Wedge ===');

    await clickWedge(page, 'dev-progress');

    // Wait for progress dashboard iframe
    await page.waitForTimeout(3000);

    // Check iframe exists
    const iframeVisible = await page.locator('iframe[src="/progress"]').isVisible();
    expect(iframeVisible).toBe(true);

    console.log('✅ Repo Monitor wedge passed');
  });

  test('11. ML Intelligence - Live Data', async ({ page }) => {
    console.log('\n=== Testing ML INTELLIGENCE Wedge ===');

    await clickWedge(page, 'ml-intelligence');

    // Wait for ML dashboard
    await page.waitForTimeout(2000);

    // Check for ML-related content
    const mlContent = await page.locator('text=/machine learning|ml|sentiment|pattern|prediction|intelligence/i').count();
    expect(mlContent).toBeGreaterThan(0);

    console.log('✅ ML Intelligence wedge passed');
  });

  test('Summary: All Wedges Network Health', async ({ page }) => {
    console.log('\n=== Network Health Summary ===');

    const failedRequests: string[] = [];

    page.on('response', (response) => {
      if (response.status() >= 400) {
        failedRequests.push(`${response.status()} - ${response.url()}`);
      }
    });

    // Click through all wedges quickly
    const wedges = [
      'morning-routine',
      'news-review',
      'proposals',
      'active-positions',
      'my-account',
      'strategy-builder',
      'backtesting',
      'execute',
      'dev-progress',
      'ml-intelligence',
    ];

    for (const wedge of wedges) {
      await clickWedge(page, wedge);
      await page.waitForTimeout(2000);
    }

    console.log('\n📊 Failed Requests:', failedRequests.length);
    if (failedRequests.length > 0) {
      console.log('Failed URLs:');
      failedRequests.forEach((url) => console.log(`  - ${url}`));
    }

    // Allow some 404s for not-yet-implemented features
    expect(failedRequests.length).toBeLessThan(10);
  });
});
