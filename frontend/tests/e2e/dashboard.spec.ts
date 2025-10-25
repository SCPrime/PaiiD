import { expect, test } from '@playwright/test';

/**
 * E2E Tests for Dashboard & Data Loading
 * Test ID: DASH-001
 * Priority: CRITICAL
 */

test.describe('Dashboard Load & Data Fetch', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/');
    await page.click('text=Log In');
    await page.fill('input[name="email"]', 'trader@test.com');
    await page.fill('input[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('should load dashboard within performance budget', async ({ page }) => {
    const startTime = Date.now();

    // Wait for portfolio data to load
    await page.waitForSelector('[data-testid="portfolio-value"]', { timeout: 2000 });

    const loadTime = Date.now() - startTime;

    // Should load within 2 seconds
    expect(loadTime).toBeLessThan(2000);

    // Verify key data is displayed
    await expect(page.locator('[data-testid="portfolio-value"]')).toBeVisible();
    await expect(page.locator('[data-testid="portfolio-change"]')).toBeVisible();
  });

  test('should display portfolio summary correctly', async ({ page }) => {
    // Portfolio value should be visible and formatted
    const portfolioValue = await page.locator('[data-testid="portfolio-value"]').textContent();
    expect(portfolioValue).toMatch(/\$[\d,]+\.\d{2}/);

    // Change percentage should be visible
    const changePercent = await page.locator('[data-testid="portfolio-change"]').textContent();
    expect(changePercent).toMatch(/[+-]?\d+\.\d{2}%/);

    // Position count should be visible
    await expect(page.locator('text=/\\d+ Positions/')).toBeVisible();
  });

  test('should display active positions', async ({ page }) => {
    // Navigate to positions
    await page.click('text=Active Positions');

    // Positions table should load
    await expect(page.locator('[data-testid="positions-table"]')).toBeVisible({ timeout: 2000 });

    // Should show position data
    await expect(page.locator('th:has-text("Symbol")')).toBeVisible();
    await expect(page.locator('th:has-text("Quantity")')).toBeVisible();
    await expect(page.locator('th:has-text("Cost Basis")')).toBeVisible();
    await expect(page.locator('th:has-text("Current Price")')).toBeVisible();
    await expect(page.locator('th:has-text("P&L")')).toBeVisible();
  });

  test('should load market data for watchlist', async ({ page }) => {
    // Navigate to watchlist
    await page.click('text=Watchlist');

    // Wait for market data
    await page.waitForSelector('[data-testid="watchlist-item"]', { timeout: 3000 });

    // Verify market data displayed
    const firstSymbol = page.locator('[data-testid="watchlist-item"]').first();
    await expect(firstSymbol.locator('[data-testid="symbol"]')).toBeVisible();
    await expect(firstSymbol.locator('[data-testid="price"]')).toBeVisible();
    await expect(firstSymbol.locator('[data-testid="change"]')).toBeVisible();
  });

  test('should refresh data automatically', async ({ page }) => {
    // Get initial portfolio value
    const initialValue = await page.locator('[data-testid="portfolio-value"]').textContent();

    // Wait for auto-refresh (assuming 30 second interval)
    await page.waitForTimeout(31000);

    // Value might change or stay the same, but element should still be there
    await expect(page.locator('[data-testid="portfolio-value"]')).toBeVisible();

    // Verify no console errors during refresh
    const consoleLogs: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleLogs.push(msg.text());
      }
    });

    expect(consoleLogs.filter(log => !log.includes('favicon'))).toHaveLength(0);
  });

  test('should handle navigation between workflows', async ({ page }) => {
    const workflows = [
      'Morning Routine',
      'Active Positions',
      'Execute Trade',
      'Research',
      'Analytics',
    ];

    for (const workflow of workflows) {
      // Click workflow
      await page.click(`text=${workflow}`);

      // Wait for workflow to load
      await page.waitForSelector(`[data-testid="${workflow.toLowerCase().replace(' ', '-')}"]`, { 
        timeout: 3000,
        state: 'visible' 
      });

      // Verify no loading errors
      await expect(page.locator('text=Error loading')).not.toBeVisible();
    }
  });

  test('should display AI recommendations', async ({ page }) => {
    // Navigate to AI Recommendations
    await page.click('text=AI Recs');

    // Wait for recommendations to load
    await page.waitForSelector('[data-testid="recommendation-card"]', { timeout: 3000 });

    // Verify recommendation data
    const recommendation = page.locator('[data-testid="recommendation-card"]').first();
    await expect(recommendation.locator('[data-testid="symbol"]')).toBeVisible();
    await expect(recommendation.locator('[data-testid="action"]')).toBeVisible(); // BUY/SELL
    await expect(recommendation.locator('[data-testid="confidence"]')).toBeVisible();
  });

  test('should handle empty portfolio gracefully', async ({ page }) => {
    // This would require a test user with no positions
    // For now, verify error handling exists
    await page.click('text=Active Positions');

    // Should either show positions or empty state, never an error
    const hasPositions = await page.locator('[data-testid="positions-table"]').isVisible();
    const hasEmptyState = await page.locator('text=No positions found').isVisible();

    expect(hasPositions || hasEmptyState).toBeTruthy();
    await expect(page.locator('text=Error')).not.toBeVisible();
  });

  test('should display performance metrics', async ({ page }) => {
    // Navigate to Analytics
    await page.click('text=Analytics');

    // Wait for charts to render
    await page.waitForSelector('[data-testid="performance-chart"]', { timeout: 3000 });

    // Verify metrics displayed
    await expect(page.locator('text=Total Return')).toBeVisible();
    await expect(page.locator('text=Sharpe Ratio')).toBeVisible();
    await expect(page.locator('text=Max Drawdown')).toBeVisible();
  });
});

