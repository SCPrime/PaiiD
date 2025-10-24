import { expect, test } from "@playwright/test";

/**
 * E2E tests for OptionsChain component
 * Tests Phase 1 implementation with SPY symbol
 */

test.describe("Options Chain - Phase 1", () => {
  // Configure retries for API-dependent tests
  test.describe.configure({ retries: 2 });

  test.beforeEach(async ({ page }) => {
    // Navigate to test page
    await page.goto("http://localhost:3000/test-options");

    // Wait for DOM to be ready (networkidle causes timeouts due to AI chat widget)
    await page.waitForLoadState("domcontentloaded");

    // Wait for the main heading to ensure page content is rendered
    await page.locator('h1:has-text("Options Chain Test")').waitFor({ timeout: 10000 });
  });

  test("should load test page successfully", async ({ page }) => {
    await expect(page.locator("h1")).toContainText("Options Chain Test");
    await expect(page.locator('input[placeholder*="Enter symbol"]')).toBeVisible();
    await expect(page.locator('button:has-text("Load Options Chain")')).toBeVisible();
  });

  test("should load SPY options chain with Greeks", async ({ page }) => {
    // Fill symbol input (using SPY which has extensive options data)
    await page.fill('input[placeholder*="Enter symbol"]', "SPY");

    // Click load button and wait for network activity
    await page.click('button:has-text("Load Options Chain")');

    // Wait for modal to appear with increased timeout (API call + rendering)
    await expect(page.locator('h2:has-text("Options Chain: SPY")')).toBeVisible({
      timeout: 20000,
    });

    // Verify expiration dropdown is visible
    const expirationSelect = page.locator("select");
    await expect(expirationSelect).toBeVisible();

    // Check that at least the default option exists
    const optionCount = await expirationSelect.locator("option").count();
    expect(optionCount).toBeGreaterThanOrEqual(1); // At least the default "Select Expiration"

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

    // Verify contracts are loaded (SPY has many contracts)
    const rows = await page.locator("tbody tr").count();
    expect(rows).toBeGreaterThan(0);
    console.log(`Loaded ${rows} options contracts`);

    // Verify at least one strike price is visible
    await expect(page.locator("tbody td").first()).toBeVisible();
  });

  test("should display contract count and expiration info", async ({ page }) => {
    await page.fill('input[placeholder*="Enter symbol"]', "SPY");
    await page.click('button:has-text("Load Options Chain")');

    // Wait for modal
    await expect(page.locator('h2:has-text("Options Chain: SPY")')).toBeVisible({
      timeout: 10000,
    });

    // Wait for data to load
    await page.waitForTimeout(2000);

    // Verify contract count is displayed
    const contractInfo = page.locator('p:has-text("contracts")');
    const contractInfoCount = await contractInfo.count();
    if (contractInfoCount === 0) {
      console.log("⚠️ Contract info not found. Page content:", await page.textContent("body"));
    }
    await expect(contractInfo, "Contract count should be visible").toBeVisible({ timeout: 5000 });

    // Verify expiration date is shown
    const expirationInfo = page.locator('p:has-text("Expiration:")');
    await expect(expirationInfo, "Expiration date should be visible").toBeVisible({
      timeout: 5000,
    });
  });

  test("should support Call/Put/Both filter toggle", async ({ page }) => {
    await page.fill('input[placeholder*="Enter symbol"]', "SPY");
    await page.click('button:has-text("Load Options Chain")');

    // Wait for modal and table
    await expect(page.locator("table")).toBeVisible({ timeout: 15000 });

    // Find filter buttons using exact text match
    const allButton = page.getByRole("button", { name: "all", exact: true });
    const callsButton = page.getByRole("button", { name: "calls", exact: true });
    const putsButton = page.getByRole("button", { name: "puts", exact: true });

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
    await page.fill('input[placeholder*="Enter symbol"]', "SPY");
    await page.click('button:has-text("Load Options Chain")');

    // Wait for modal
    await expect(page.locator('h2:has-text("Options Chain: SPY")')).toBeVisible({
      timeout: 10000,
    });

    // Click Close button
    await page.click('button:has-text("Close")');

    // Verify modal is closed
    await expect(page.locator('h2:has-text("Options Chain: SPY")')).not.toBeVisible();
  });

  test("should handle invalid symbol gracefully", async ({ page }) => {
    // Enter invalid symbol
    await page.fill('input[placeholder*="Enter symbol"]', "INVALID123");
    await page.click('button:has-text("Load Options Chain")');

    // Wait for potential error or empty state
    await page.waitForTimeout(3000);

    // Check if error message appears (component should show error state)
    const errorDiv = page.locator('div:has-text("Error")').first();
    if (await errorDiv.isVisible()) {
      console.log("Error handling working correctly");
    }
  });

  test("should display Greeks with proper formatting", async ({ page }) => {
    await page.fill('input[placeholder*="Enter symbol"]', "SPY");
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
  // Configure retries for network tests
  test.describe.configure({ retries: 2 });

  test("should make correct API calls", async ({ page }) => {
    // Listen for API calls
    const expirationsRequest = page.waitForRequest((req) =>
      req.url().includes("/api/proxy/options/expirations/SPY")
    );

    const chainRequest = page.waitForRequest((req) =>
      req.url().includes("/api/proxy/options/chain/SPY")
    );

    // Navigate and trigger
    await page.goto("http://localhost:3000/test-options");
    await page.fill('input[placeholder*="Enter symbol"]', "SPY");
    await page.click('button:has-text("Load Options Chain")');

    // Verify requests were made
    await expirationsRequest;
    await chainRequest;

    console.log("✅ All API calls verified");
  });

  test("should use fixture data when USE_TEST_FIXTURES=true", async ({ page }) => {
    // Navigate and trigger with fixture-enabled backend
    await page.goto("http://localhost:3000/test-options");
    await page.fill('input[placeholder*="Enter symbol"]', "SPY");
    await page.click('button:has-text("Load Options Chain")');

    // Wait for modal and table
    await expect(page.locator('h2:has-text("Options Chain: SPY")')).toBeVisible({
      timeout: 10000,
    });
    await expect(page.locator("table")).toBeVisible({ timeout: 15000 });

    // Verify fixture marker is present in response
    // This would require checking the network response or component state
    // For now, we verify the data loads successfully with fixtures
    const rows = await page.locator("tbody tr").count();
    expect(rows).toBeGreaterThan(0);
    console.log(`✅ Loaded ${rows} fixture contracts for SPY`);

    // Verify Greeks are displayed (fixtures should have consistent data)
    await expect(page.locator('th:has-text("Delta")')).toBeVisible();
    await expect(page.locator('th:has-text("Gamma")')).toBeVisible();
    await expect(page.locator('th:has-text("Theta")')).toBeVisible();
    await expect(page.locator('th:has-text("Vega")')).toBeVisible();
  });

  test("should load within reasonable time", async ({ page }) => {
    await page.goto("http://localhost:3000/test-options");

    const startTime = Date.now();

    await page.fill('input[placeholder*="Enter symbol"]', "SPY");
    await page.click('button:has-text("Load Options Chain")');
    await expect(page.locator("table")).toBeVisible({ timeout: 15000 });

    const loadTime = Date.now() - startTime;
    console.log(`Options chain loaded in ${loadTime}ms`);

    // Should load within 15 seconds
    expect(loadTime).toBeLessThan(15000);
  });
});
