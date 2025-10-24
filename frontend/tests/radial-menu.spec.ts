import { expect, test } from "@playwright/test";

import { goto } from "./helpers/navigation";

test.describe("Radial workflow smoke tests", () => {
  test.beforeEach(async ({ page }) => {
    await goto(page, "/test-radial");
  });

  test("renders navigation shell", async ({ page }) => {
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(/AI Trading Platform/);
    await expect(page.getByText("System Status")).toBeVisible();
    await expect(page.getByText("Hover for descriptions", { exact: false })).toBeVisible();
  });

  test("shows all workflow segments and activates selection", async ({ page }) => {
    const segments = page.locator("svg g.segment");
    await expect(segments).toHaveCount(10);

    await segments.first().click();
    await expect(page.getByText("Workflow loaded and ready")).toBeVisible();
    await expect(page.getByText("- Activated")).toBeVisible();
  });

  test("reveals workflow details on hover", async ({ page }) => {
    const segments = page.locator("svg g.segment");
    await segments.nth(2).hover();
    await expect(
      page.getByText("Review AI-generated trading recommendations", { exact: false })
    ).toBeVisible();
  });
});
