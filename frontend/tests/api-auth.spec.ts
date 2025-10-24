import { expect, test } from "@playwright/test";

const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL;
const apiEmail = process.env.PLAYWRIGHT_TEST_EMAIL;
const apiPassword = process.env.PLAYWRIGHT_TEST_PASSWORD;

const shouldSkip = !apiBaseUrl || !apiEmail || !apiPassword;

test.describe("Backend API authentication", () => {
  test.skip(
    shouldSkip,
    "PLAYWRIGHT_API_BASE_URL, PLAYWRIGHT_TEST_EMAIL, and PLAYWRIGHT_TEST_PASSWORD must be configured"
  );

  test("refresh token returns a new access token", async ({ request }) => {
    const loginResponse = await request.post(`${apiBaseUrl}/auth/login`, {
      data: { email: apiEmail, password: apiPassword },
    });
    expect(loginResponse.ok()).toBeTruthy();
    const loginBody = await loginResponse.json();

    const refreshResponse = await request.post(`${apiBaseUrl}/auth/refresh`, {
      data: { refresh_token: loginBody.refresh_token },
    });
    expect(refreshResponse.ok()).toBeTruthy();
    const refreshBody = await refreshResponse.json();

    expect(refreshBody.access_token).not.toBe(loginBody.access_token);
    expect(refreshBody.refresh_token).not.toBe(loginBody.refresh_token);
  });

  test("options chains include source metadata", async ({ request }) => {
    const loginResponse = await request.post(`${apiBaseUrl}/auth/login`, {
      data: { email: apiEmail, password: apiPassword },
    });
    expect(loginResponse.ok()).toBeTruthy();
    const loginBody = await loginResponse.json();

    const chainResponse = await request.get(`${apiBaseUrl}/options/chains/SPY`, {
      headers: { Authorization: `Bearer ${loginBody.access_token}` },
    });

    expect(chainResponse.ok()).toBeTruthy();
    const chainBody = await chainResponse.json();
    expect(chainBody.source).toBeDefined();
    expect(chainBody.total_contracts).toBeGreaterThanOrEqual(0);
  });

  test("options chains surface upstream failures", async ({ request }) => {
    const loginResponse = await request.post(`${apiBaseUrl}/auth/login`, {
      data: { email: apiEmail, password: apiPassword },
    });
    expect(loginResponse.ok()).toBeTruthy();
    const loginBody = await loginResponse.json();

    const errorResponse = await request.get(`${apiBaseUrl}/options/chains/INVALID`, {
      headers: { Authorization: `Bearer ${loginBody.access_token}` },
    });

    expect(errorResponse.status()).toBeGreaterThanOrEqual(400);
    const body = await errorResponse.json();
    if (errorResponse.status() >= 500 && typeof body.detail === "string") {
      expect(body.detail).toContain("Error fetching options chain");
    }
  });
});
