import { expect, test } from '@playwright/test';

/**
 * E2E Tests for Trading Flow
 * Test ID: TRADE-001
 * Priority: CRITICAL
 */

test.describe('Trade Execution Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/');
    await page.click('text=Log In');
    await page.fill('input[name="email"]', 'trader@test.com');
    await page.fill('input[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('should execute market buy order', async ({ page }) => {
    // Navigate to trade execution
    await page.click('text=Execute Trade');

    // Fill order form
    await page.fill('input[name="symbol"]', 'AAPL');
    await page.fill('input[name="quantity"]', '10');
    await page.selectOption('select[name="side"]', 'buy');
    await page.selectOption('select[name="order_type"]', 'market');

    // Preview order
    await page.click('button:has-text("Preview Order")');

    // Wait for validation
    await expect(page.locator('text=Order Preview')).toBeVisible({ timeout: 3000 });

    // Confirm order
    await page.click('button:has-text("Confirm Trade")');

    // Wait for success message
    await expect(page.locator('text=Order executed successfully')).toBeVisible({ timeout: 5000 });

    // Verify position created
    await page.click('text=Active Positions');
    await expect(page.locator('text=AAPL')).toBeVisible();
    await expect(page.locator('text=10 shares')).toBeVisible();
  });

  test('should execute limit sell order', async ({ page }) => {
    // Navigate to trade execution
    await page.click('text=Execute Trade');

    // Fill limit sell order
    await page.fill('input[name="symbol"]', 'AAPL');
    await page.fill('input[name="quantity"]', '5');
    await page.selectOption('select[name="side"]', 'sell');
    await page.selectOption('select[name="order_type"]', 'limit');
    await page.fill('input[name="limit_price"]', '160.00');

    // Preview and confirm
    await page.click('button:has-text("Preview Order")');
    await expect(page.locator('text=Limit')).toBeVisible();
    await expect(page.locator('text=$160.00')).toBeVisible();

    await page.click('button:has-text("Confirm Trade")');

    // Wait for success
    await expect(page.locator('text=Order submitted successfully')).toBeVisible({ timeout: 5000 });
  });

  test('should validate insufficient balance', async ({ page }) => {
    await page.click('text=Execute Trade');

    // Try to buy more than balance allows
    await page.fill('input[name="symbol"]', 'AAPL');
    await page.fill('input[name="quantity"]', '100000');
    await page.selectOption('select[name="side"]', 'buy');

    await page.click('button:has-text("Preview Order")');

    // Should show error
    await expect(page.locator('text=Insufficient balance')).toBeVisible({ timeout: 3000 });
  });

  test('should validate invalid symbol', async ({ page }) => {
    await page.click('text=Execute Trade');

    await page.fill('input[name="symbol"]', 'INVALIDSTOCK');
    await page.fill('input[name="quantity"]', '10');
    await page.selectOption('select[name="side"]', 'buy');

    await page.click('button:has-text("Preview Order")');

    // Should show error
    await expect(page.locator('text=Invalid symbol')).toBeVisible({ timeout: 3000 });
  });

  test('should cancel pending order', async ({ page }) => {
    // Create a limit order first
    await page.click('text=Execute Trade');
    await page.fill('input[name="symbol"]', 'MSFT');
    await page.fill('input[name="quantity"]', '5');
    await page.selectOption('select[name="side"]', 'buy');
    await page.selectOption('select[name="order_type"]', 'limit');
    await page.fill('input[name="limit_price"]', '200.00');

    await page.click('button:has-text("Preview Order")');
    await page.click('button:has-text("Confirm Trade")');

    // Navigate to orders
    await page.click('text=Orders');

    // Find and cancel order
    await page.click('button[aria-label="Cancel order"]');
    await page.click('button:has-text("Confirm Cancel")');

    // Verify cancellation
    await expect(page.locator('text=Order cancelled')).toBeVisible({ timeout: 5000 });
  });

  test('should display trade history', async ({ page }) => {
    await page.click('text=Trade History');

    // Should show recent trades
    await expect(page.locator('table')).toBeVisible();
    await expect(page.locator('th:has-text("Symbol")')).toBeVisible();
    await expect(page.locator('th:has-text("Date")')).toBeVisible();
    await expect(page.locator('th:has-text("Side")')).toBeVisible();
    await expect(page.locator('th:has-text("Quantity")')).toBeVisible();
    await expect(page.locator('th:has-text("Price")')).toBeVisible();
  });
});

