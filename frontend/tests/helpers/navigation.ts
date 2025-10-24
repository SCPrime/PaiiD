import type { Page } from "@playwright/test";

export async function goto(page: Page, path: string): Promise<void> {
  await page.goto(path, { waitUntil: "networkidle" });
}
