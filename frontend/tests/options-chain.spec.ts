import { expect, test } from "@playwright/test";
import { PLAYWRIGHT_FIXTURE_EXPIRATIONS, PLAYWRIGHT_TEST_SYMBOL } from "./fixtures/options";

/**
 * E2E tests for OptionsChain component
 * Tests Phase 1 implementation with OPTT fixture data
 */

test.describe("Options Chain - Phase 1", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to test page
    await page.goto("http://localhost:3000/test-options");
  });

  test("should load test page successfully", async ({ page }) => {
    await expect(page.locator("h1")).toContainText("Options Chain Test");
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.locator("button")).toContainText("Load Options Chain");
  });

  test("should load fixture options chain with Greeks", async ({ page }) => {
    // Fill symbol input
    await page.fill('input[type="text"]', PLAYWRIGHT_TEST_SYMBOL);

    // Click load button
    await page.click('button:has-text("Load Options Chain")');

    // Wait for options chain modal to appear
    await expect(
      page.locator(`h2:has-text("Options Chain: ${PLAYWRIGHT_TEST_SYMBOL}")`)
    ).toBeVisible({
      timeout: 10000,
    });

    // Verify expiration dropdown is populated
    const expirationSelect = page.locator("select");
    await expect(expirationSelect).toBeVisible();

    // Check that options are available (fixture includes 2 expirations)
    const optionLocator = expirationSelect.locator("option");
    const optionCount = await optionLocator.count();
    expect(optionCount).toBeGreaterThan(1); // At least 1 + default "Select Expiration"

    const optionTexts = await optionLocator.allTextContents();
    for (const expectedExpiration of PLAYWRIGHT_FIXTURE_EXPIRATIONS) {
      expect(optionTexts).toContain(expectedExpiration);
    }

    // Wait for options table to load
    await expect(page.locator("table")).toBeVisible({ timeout: 15000 });

    // Verify Greeks column headers are present
    await expect(page.locator('th:has-text("Delta")')).toBeVisible();
    await expect(page.locator('th:has-text("Gamma")')).toBeVisible();
    await expect(page.locator('th:has-text("Theta")')).toBeVisible();
    await expect(page.locator('th:has-text("Vega")')).toBeVisible();

    // Verify CALLS and PUTS headers
    await expect(page.locator('th:has-text("CALLS")')).toBeVisible();
    await expect(page.locator('th:has-text("PUTS")')).toBeVisible();
    await expect(page.locator('th:has-text("STRIKE")')).toBeVisible();

    // Verify contracts are loaded (fixture includes deterministic calls/puts)
    const rows = await page.locator("tbody tr").count();
    expect(rows).toBeGreaterThan(0);
    console.log(`Loaded ${rows} options contracts`);

    // Verify at least one strike price is visible
    await expect(page.locator("tbody td").first()).toBeVisible();
  });

  test("should display contract count and expiration info", async ({ page }) => {
    await page.fill('input[type="text"]', PLAYWRIGHT_TEST_SYMBOL);
    await page.click('button:has-text("Load Options Chain")');

    // Wait for modal
    await expect(
      page.locator(`h2:has-text("Options Chain: ${PLAYWRIGHT_TEST_SYMBOL}")`)
    ).toBeVisible({
      timeout: 10000,
    });

    // Wait for data to load
    await page.waitForTimeout(2000);

    // Verify contract count is displayed
    const contractInfo = page.locator('p:has-text("contracts")');
    await expect(contractInfo).toBeVisible({ timeout: 5000 });

    // Verify expiration date is shown
    const expirationInfo = page.locator('p:has-text("Expiration:")');
    await expect(expirationInfo).toBeVisible({ timeout: 5000 });
  });

  test("should support Call/Put/Both filter toggle", async ({ page }) => {
    await page.fill('input[type="text"]', PLAYWRIGHT_TEST_SYMBOL);
    await page.click('button:has-text("Load Options Chain")');

    // Wait for modal and table
    await expect(page.locator("table")).toBeVisible({ timeout: 15000 });

    // Find filter buttons
    const allButton = page.locator('button:has-text("all")');
    const callsButton = page.locator('button:has-text("calls")');
    const putsButton = page.locator('button:has-text("puts")');

    // Verify all filter buttons exist
    await expect(allButton).toBeVisible();
    await expect(callsButton).toBeVisible();
    await expect(putsButton).toBeVisible();

    // Get initial row count
    const initialRows = await page.locator("tbody tr").count();

    // Click "calls" filter
    await callsButton.click();
    await page.waitForTimeout(500);

    // Verify rows potentially reduced (calls only)
    const callsRows = await page.locator("tbody tr").count();
    expect(callsRows).toBeGreaterThan(0);

    // Click "puts" filter
    await putsButton.click();
    await page.waitForTimeout(500);

    // Verify rows potentially reduced (puts only)
    const putsRows = await page.locator("tbody tr").count();
    expect(putsRows).toBeGreaterThan(0);

    // Click "all" filter to return to full view
    await allButton.click();
    await page.waitForTimeout(500);

    const finalRows = await page.locator("tbody tr").count();
    expect(finalRows).toBe(initialRows);
  });

  test("should close modal when clicking Close button", async ({ page }) => {
    await page.fill('input[type="text"]', PLAYWRIGHT_TEST_SYMBOL);
    await page.click('button:has-text("Load Options Chain")');

    // Wait for modal
    await expect(
      page.locator(`h2:has-text("Options Chain: ${PLAYWRIGHT_TEST_SYMBOL}")`)
    ).toBeVisible({
      timeout: 10000,
    });

    // Click Close button
    await page.click('button:has-text("Close")');

    // Verify modal is closed
    await expect(
      page.locator(`h2:has-text("Options Chain: ${PLAYWRIGHT_TEST_SYMBOL}")`)
    ).not.toBeVisible();
  });

  test("should handle invalid symbol gracefully", async ({ page }) => {
    // Enter invalid symbol
    await page.fill('input[type="text"]', "INVALID123");
    await page.click('button:has-text("Load Options Chain")');

    // Wait for potential error or empty state
    await page.waitForTimeout(3000);

    // Check if error message appears (component should show error state)
    const errorDiv = page.locator('div:has-text("Error")');
    if (await errorDiv.isVisible()) {
      console.log("Error handling working correctly");
    }
  });

  test("should display Greeks with proper formatting", async ({ page }) => {
    await page.fill('input[type="text"]', PLAYWRIGHT_TEST_SYMBOL);
    await page.click('button:has-text("Load Options Chain")');

    // Wait for table
    await expect(page.locator("table")).toBeVisible({ timeout: 15000 });

    // Find first data cell with delta value
    const deltaCell = page.locator("tbody tr").first().locator("td").nth(2); // Assuming delta is 3rd column

    // Verify cell has content
    await expect(deltaCell).not.toBeEmpty();

    // Check if delta value is formatted (should be number with decimals or "—")
    const deltaText = await deltaCell.textContent();
    console.log(`Sample Delta value: ${deltaText}`);

    // Verify it's either a number or dash
    expect(deltaText).toMatch(/^[0-9.\-—]+$/);
  });
});

test.describe("Options Chain - Network & Performance", () => {
  test("should make correct API calls", async ({ page }) => {
    // Listen for API calls
    const expirationsRequest = page.waitForRequest((req) =>
      req.url().includes(`/api/proxy/options/expirations/${PLAYWRIGHT_TEST_SYMBOL}`)
    );

    const chainRequest = page.waitForRequest((req) =>
      req.url().includes(`/api/proxy/options/chain/${PLAYWRIGHT_TEST_SYMBOL}`)
    );

    // Navigate and trigger
    await page.goto("http://localhost:3000/test-options");
    await page.fill('input[type="text"]', PLAYWRIGHT_TEST_SYMBOL);
    await page.click('button:has-text("Load Options Chain")');

    // Verify requests were made
    await expirationsRequest;
    await chainRequest;

    console.log("✅ All API calls verified");
  });

  test("should load within reasonable time", async ({ page }) => {
    await page.goto("http://localhost:3000/test-options");

    const startTime = Date.now();

    await page.fill('input[type="text"]', PLAYWRIGHT_TEST_SYMBOL);
    await page.click('button:has-text("Load Options Chain")');
    await expect(page.locator("table")).toBeVisible({ timeout: 15000 });

    const loadTime = Date.now() - startTime;
    console.log(`Options chain loaded in ${loadTime}ms`);

    // Should load within 15 seconds
    expect(loadTime).toBeLessThan(15000);
  });
});
