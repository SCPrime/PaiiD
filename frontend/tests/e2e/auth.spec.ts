import { expect, test } from '@playwright/test';

/**
 * E2E Tests for Authentication Flow
 * Test ID: AUTH-001
 * Priority: CRITICAL
 */

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test('should complete full registration flow', async ({ page }) => {
    // Click sign up button
    await page.click('text=Sign Up');

    // Fill registration form
    await page.fill('input[name="email"]', `test-${Date.now()}@example.com`);
    await page.fill('input[name="password"]', 'SecureP@ss123');
    await page.fill('input[name="name"]', 'Test User');
    
    // Select risk tolerance
    await page.selectOption('select[name="risk_tolerance"]', 'moderate');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Verify dashboard loaded
    await expect(page.locator('text=Dashboard')).toBeVisible();
    await expect(page.locator('text=Portfolio')).toBeVisible();
  });

  test('should login existing user', async ({ page }) => {
    // Click login button
    await page.click('text=Log In');

    // Fill login form
    await page.fill('input[name="email"]', 'trader@test.com');
    await page.fill('input[name="password"]', 'TestP@ss123');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for redirect
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Verify authenticated state
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('should handle login with invalid credentials', async ({ page }) => {
    await page.click('text=Log In');

    await page.fill('input[name="email"]', 'invalid@example.com');
    await page.fill('input[name="password"]', 'WrongPassword');

    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.locator('text=Invalid credentials')).toBeVisible({ timeout: 5000 });
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.click('text=Log In');
    await page.fill('input[name="email"]', 'trader@test.com');
    await page.fill('input[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');

    await page.waitForURL('**/dashboard');

    // Logout
    await page.click('button[aria-label="Settings"]');
    await page.click('text=Logout');

    // Should redirect to homepage
    await page.waitForURL('/');
    await expect(page.locator('text=Log In')).toBeVisible();
  });

  test('should maintain session on page reload', async ({ page }) => {
    // Login
    await page.click('text=Log In');
    await page.fill('input[name="email"]', 'trader@test.com');
    await page.fill('input[name="password"]', 'TestP@ss123');
    await page.click('button[type="submit"]');

    await page.waitForURL('**/dashboard');

    // Reload page
    await page.reload();

    // Should still be authenticated
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });
});

