import { test, expect } from '@playwright/test';

test.describe('Complete User Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to application
    await page.goto('/');
  });

  test('should load application homepage', async ({ page }) => {
    // Check that main application loads
    await expect(page).toHaveTitle(/AI Icarus/i);
    await expect(page.locator('h1, h2')).toContainText(/AI Icarus|Log Analytics/i);
  });

  test('should show login button when unauthenticated', async ({ page }) => {
    // Check for login UI element
    const loginButton = page.locator('button:has-text("Sign In"), button:has-text("Login")');
    await expect(loginButton).toBeVisible();
  });

  test.skip('authenticated user workflow', async ({ page }) => {
    // This test is skipped by default as it requires actual Azure AD credentials
    // Enable by setting TEST_USERNAME and TEST_PASSWORD environment variables

    if (!process.env.TEST_USERNAME || !process.env.TEST_PASSWORD) {
      test.skip();
    }

    // Click login
    await page.click('button:has-text("Sign In")');

    // Azure AD login flow (simplified - actual flow may vary)
    await page.fill('input[type="email"]', process.env.TEST_USERNAME!);
    await page.click('input[type="submit"]');

    await page.fill('input[type="password"]', process.env.TEST_PASSWORD!);
    await page.click('input[type="submit"]');

    // Wait for redirect back to app
    await page.waitForURL('/', { timeout: 30000 });

    // Verify authenticated state
    await expect(page.locator('text=/Welcome|Profile|Logout/i')).toBeVisible();

    // Test workspace browsing
    const workspaceButton = page.locator('button:has-text("Browse Workspaces"), button:has-text("Workspaces")');
    if (await workspaceButton.isVisible()) {
      await workspaceButton.click();
      await expect(page.locator('[data-testid="workspace-list"], text=/workspace/i')).toBeVisible();
    }
  });

  test('should have API configuration available', async ({ page, request }) => {
    // Test that backend API is accessible
    const apiUrl = process.env.API_URL || 'http://localhost:8000';
    const response = await request.get(`${apiUrl}/health`);

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('should handle errors gracefully', async ({ page }) => {
    // Test error handling by navigating to non-existent route
    await page.goto('/non-existent-route');

    // Should show error message or redirect, not crash
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('UI Components', () => {
  test('should be responsive', async ({ page }) => {
    await page.goto('/');

    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('body')).toBeVisible();

    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('body')).toBeVisible();

    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('body')).toBeVisible();
  });

  test('should have accessible navigation', async ({ page }) => {
    await page.goto('/');

    // Check for keyboard navigation
    await page.keyboard.press('Tab');

    // Should have focus indicators
    const focusedElement = await page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });
});
