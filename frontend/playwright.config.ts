import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright configuration for PaiiD E2E tests
 * Version 2.0 - With process management integration
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: "./tests",

  /* Global setup and teardown for process management */
  globalSetup: require.resolve("./tests/global-setup"),
  globalTeardown: require.resolve("./tests/global-teardown"),

  /* Run tests in files in parallel */
  fullyParallel: true,

  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,

  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,

  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,

  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: "html",

  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: "http://localhost:3000",

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: "on-first-retry",

    /* Screenshot on failure */
    screenshot: "only-on-failure",

    /* Video on failure */
    video: "retain-on-failure",
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        channel: "chrome", // Use system Chrome instead of downloading Chromium
      },
    },
  ],

  /* Run your local dev servers before starting the tests */
  webServer: [
    {
      command: "USE_TEST_FIXTURES=true python -m uvicorn app.main:app --port 8002",
      cwd: "../backend",
      url: "http://localhost:8002/api/health",
      timeout: 120000,
      reuseExistingServer: !process.env.CI, // On CI, always start fresh
    },
    {
      command: "npm run dev",
      url: "http://localhost:3000",
      reuseExistingServer: !process.env.CI, // On CI, always start fresh
      timeout: 120000,
    },
  ],
});
