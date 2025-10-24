import { expect, test } from "@playwright/test";

/**
 * E2E tests for Market Data with Fixtures
 * Tests deterministic market data loading when USE_TEST_FIXTURES=true
 */

test.describe("Market Data - Fixture Mode", () => {
  test.describe.configure({ retries: 2 });

  test.beforeEach(async ({ page }) => {
    // Navigate to test page
    await page.goto("http://localhost:3000/test-options");
    await page.waitForLoadState("domcontentloaded");
  });

  test("should load market quotes with fixture data", async ({ page }) => {
    // Test that market quotes endpoint returns fixture data
    const response = await page.request.get("http://localhost:8002/api/market/quote/SPY");
    expect(response.status()).toBe(200);

    const quoteData = await response.json();
    expect(quoteData.symbol).toBe("SPY");
    expect(quoteData.test_fixture).toBe(true); // Verify fixture marker
    expect(quoteData.bid).toBeDefined();
    expect(quoteData.ask).toBeDefined();
    expect(quoteData.last).toBeDefined();

    console.log("✅ Market quote fixture data verified:", quoteData);
  });

  test("should load multiple quotes with fixture data", async ({ page }) => {
    // Test multiple symbols endpoint
    const response = await page.request.get(
      "http://localhost:8002/api/market/quotes?symbols=SPY,QQQ,AAPL"
    );
    expect(response.status()).toBe(200);

    const quotesData = await response.json();
    expect(quotesData.SPY).toBeDefined();
    expect(quotesData.QQQ).toBeDefined();
    expect(quotesData.AAPL).toBeDefined();

    // Verify all quotes have fixture markers
    expect(quotesData.SPY.test_fixture).toBe(true);
    expect(quotesData.QQQ.test_fixture).toBe(true);
    expect(quotesData.AAPL.test_fixture).toBe(true);

    console.log("✅ Multiple quotes fixture data verified:", Object.keys(quotesData));
  });

  test("should load positions with fixture data", async ({ page }) => {
    // Test positions endpoint
    const response = await page.request.get("http://localhost:8002/api/positions");
    expect(response.status()).toBe(200);

    const positionsData = await response.json();
    expect(Array.isArray(positionsData)).toBe(true);
    expect(positionsData.length).toBeGreaterThan(0);

    // Verify first position has fixture data
    const firstPosition = positionsData[0];
    expect(firstPosition.symbol).toBeDefined();
    expect(firstPosition.quantity).toBeDefined();
    expect(firstPosition.entry_price).toBeDefined();
    expect(firstPosition.current_price).toBeDefined();
    expect(firstPosition.unrealized_pnl).toBeDefined();

    console.log("✅ Positions fixture data verified:", positionsData.length, "positions");
  });

  test("should verify no external API calls during fixture mode", async ({ page }) => {
    // Listen for any external API calls (should be none in fixture mode)
    const externalCalls: string[] = [];

    page.on("request", (request) => {
      const url = request.url();
      // Check for external API calls (not localhost)
      if (!url.includes("localhost") && !url.includes("127.0.0.1")) {
        externalCalls.push(url);
      }
    });

    // Navigate and trigger options chain load
    await page.fill('input[placeholder*="Enter symbol"]', "SPY");
    await page.click('button:has-text("Load Options Chain")');

    // Wait for data to load
    await expect(page.locator("table")).toBeVisible({ timeout: 15000 });

    // Verify no external API calls were made
    expect(externalCalls.length).toBe(0);
    console.log("✅ No external API calls detected in fixture mode");
  });

  test("should have consistent fixture data across requests", async ({ page }) => {
    // Make multiple requests to same endpoint
    const response1 = await page.request.get("http://localhost:8002/api/market/quote/SPY");
    const response2 = await page.request.get("http://localhost:8002/api/market/quote/SPY");

    expect(response1.status()).toBe(200);
    expect(response2.status()).toBe(200);

    const data1 = await response1.json();
    const data2 = await response2.json();

    // Verify data is consistent (fixtures should be deterministic)
    expect(data1.bid).toBe(data2.bid);
    expect(data1.ask).toBe(data2.ask);
    expect(data1.last).toBe(data2.last);

    console.log("✅ Fixture data consistency verified");
  });
});
