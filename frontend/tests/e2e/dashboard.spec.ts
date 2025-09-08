import { test, expect } from '@playwright/test';

test.describe('Qualitative Edge Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the dashboard homepage', async ({ page }) => {
    // Check that the main elements are present
    await expect(page.locator('h1')).toContainText('Qualitative Edge');
    await expect(page.locator('input[placeholder*="ticker"]')).toBeVisible();
  });

  test('should perform company search and analysis', async ({ page }) => {
    // Enter a ticker symbol
    const tickerInput = page.locator('input[placeholder*="ticker"]');
    await tickerInput.fill('RELIANCE');
    await tickerInput.press('Enter');

    // Wait for the analysis to load
    await page.waitForTimeout(5000); // Give API time to respond

    // Check that company information is displayed
    await expect(page.locator('text=RELIANCE')).toBeVisible();
    
    // Check that the main sections are present
    await expect(page.locator('text=Company Overview')).toBeVisible();
    await expect(page.locator('text=Stock Price')).toBeVisible();
    await expect(page.locator('text=SWOT Analysis')).toBeVisible();
    await expect(page.locator('text=DCF Valuation')).toBeVisible();
  });

  test('should display SWOT analysis cards', async ({ page }) => {
    // Search for a company
    await page.locator('input[placeholder*="ticker"]').fill('RELIANCE');
    await page.locator('input[placeholder*="ticker"]').press('Enter');
    
    await page.waitForTimeout(5000);

    // Check SWOT sections
    await expect(page.locator('text=Strengths')).toBeVisible();
    await expect(page.locator('text=Weaknesses')).toBeVisible();
    await expect(page.locator('text=Opportunities')).toBeVisible();
    await expect(page.locator('text=Threats')).toBeVisible();
  });

  test('should show DCF valuation with interactive controls', async ({ page }) => {
    // Search for a company
    await page.locator('input[placeholder*="ticker"]').fill('RELIANCE');
    await page.locator('input[placeholder*="ticker"]').press('Enter');
    
    await page.waitForTimeout(5000);

    // Check DCF section
    await expect(page.locator('text=DCF Valuation')).toBeVisible();
    await expect(page.locator('text=Intrinsic Value')).toBeVisible();
    
    // Check for assumption controls (sliders)
    await expect(page.locator('text=Revenue Growth Rate')).toBeVisible();
    await expect(page.locator('text=EBITDA Margin')).toBeVisible();
    await expect(page.locator('text=WACC')).toBeVisible();
  });

  test('should handle invalid ticker gracefully', async ({ page }) => {
    // Enter an invalid ticker
    await page.locator('input[placeholder*="ticker"]').fill('INVALID_TICKER');
    await page.locator('input[placeholder*="ticker"]').press('Enter');
    
    await page.waitForTimeout(3000);

    // Should show error message or no results
    const errorElements = page.locator('text=not found, text=error, text=invalid');
    await expect(errorElements.first()).toBeVisible({ timeout: 10000 });
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that the search input is still visible and usable
    const tickerInput = page.locator('input[placeholder*="ticker"]');
    await expect(tickerInput).toBeVisible();
    
    // Perform a search
    await tickerInput.fill('TCS');
    await tickerInput.press('Enter');
    
    await page.waitForTimeout(5000);
    
    // Check that content is displayed properly on mobile
    await expect(page.locator('text=TCS')).toBeVisible();
  });

  test('should update DCF valuation when assumptions change', async ({ page }) => {
    // Search for a company
    await page.locator('input[placeholder*="ticker"]').fill('RELIANCE');
    await page.locator('input[placeholder*="ticker"]').press('Enter');
    
    await page.waitForTimeout(5000);

    // Get initial intrinsic value
    const intrinsicValueElement = page.locator('text=Intrinsic Value').locator('..').locator('text=₹');
    const initialValue = await intrinsicValueElement.textContent();

    // Change an assumption (if sliders are present)
    const slider = page.locator('input[type="range"]').first();
    if (await slider.isVisible()) {
      await slider.fill('15'); // Change value
      
      await page.waitForTimeout(2000); // Wait for recalculation
      
      // Check that the value updated
      const newValue = await intrinsicValueElement.textContent();
      expect(newValue).not.toBe(initialValue);
    }
  });

  test('should display news sentiment analysis', async ({ page }) => {
    // Search for a company
    await page.locator('input[placeholder*="ticker"]').fill('RELIANCE');
    await page.locator('input[placeholder*="ticker"]').press('Enter');
    
    await page.waitForTimeout(5000);

    // Check for news sentiment section
    await expect(page.locator('text=News Sentiment')).toBeVisible();
    await expect(page.locator('text=Sentiment Score')).toBeVisible();
  });

  test('should show market landscape and competitors', async ({ page }) => {
    // Search for a company
    await page.locator('input[placeholder*="ticker"]').fill('RELIANCE');
    await page.locator('input[placeholder*="ticker"]').press('Enter');
    
    await page.waitForTimeout(5000);

    // Check for market landscape section
    await expect(page.locator('text=Market Landscape')).toBeVisible();
    await expect(page.locator('text=Competitors')).toBeVisible();
  });

  test('should display employee sentiment data', async ({ page }) => {
    // Search for a company
    await page.locator('input[placeholder*="ticker"]').fill('RELIANCE');
    await page.locator('input[placeholder*="ticker"]').press('Enter');
    
    await page.waitForTimeout(5000);

    // Check for employee sentiment section
    await expect(page.locator('text=Employee Sentiment')).toBeVisible();
    await expect(page.locator('text=Rating')).toBeVisible();
  });
});