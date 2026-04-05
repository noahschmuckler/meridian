const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.goto('/index-rendered.html');
  // Wait for app to finish loading (first module tab appears)
  await page.locator('.module-tab').first().waitFor({ timeout: 10000 });
});

test('page loads with header and first module', async ({ page }) => {
  await expect(page.locator('header h1')).not.toHaveText('Loading…');
  await expect(page.locator('.module-tab')).toHaveCount(1);
  await expect(page.locator('#module-container')).not.toBeEmpty();
});

test('search finds modules and opens one', async ({ page }) => {
  const search = page.locator('#module-search');
  await search.fill('benzo');
  await search.focus();
  // Trigger the input handler
  await search.dispatchEvent('input');
  const results = page.locator('.module-search-results');
  await expect(results).toHaveClass(/visible/);
  await expect(page.locator('.module-search-result')).toHaveCount(1);
  await expect(page.locator('.module-search-result-title')).toHaveText('Benzodiazepines');

  // Click to open
  await page.locator('.module-search-result').click();
  // Should now have 2 tabs
  await expect(page.locator('.module-tab')).toHaveCount(2);
});

test('checkbox toggles on click', async ({ page }) => {
  const checkbox = page.locator('.check-box').first();
  await expect(checkbox).toHaveAttribute('aria-checked', 'false');
  await checkbox.click();
  await expect(checkbox).toHaveAttribute('aria-checked', 'true');
  // Toggle back
  await checkbox.click();
  await expect(checkbox).toHaveAttribute('aria-checked', 'false');
});

test('expanded view renders sections', async ({ page }) => {
  await page.locator('#btn-expanded').click();
  // Expanded view should show section headers
  await expect(page.locator('.expanded-section-header').first()).toBeVisible();
  // Should have content beneath
  await expect(page.locator('.expanded-section-body').first()).toBeVisible();
});

test('FAQ accordion expands and collapses in expanded view', async ({ page }) => {
  await page.locator('#btn-expanded').click();
  const faq = page.locator('.expanded-faq-question').first();
  const answer = page.locator('.expanded-faq-answer').first();

  // Initially collapsed
  await expect(faq).toHaveAttribute('aria-expanded', 'false');
  await expect(answer).not.toBeVisible();

  // Expand
  await faq.click();
  await expect(faq).toHaveAttribute('aria-expanded', 'true');
  await expect(answer).toBeVisible();

  // Collapse
  await faq.click();
  await expect(faq).toHaveAttribute('aria-expanded', 'false');
});

test('PPTX download button exists in expanded view', async ({ page }) => {
  await page.locator('#btn-expanded').click();
  const pptxBtn = page.locator('#pptx-btn');
  await expect(pptxBtn).toBeVisible();
});

test('module JSON files are valid', async ({ page }) => {
  const indexResp = await page.request.get('/modules/index.json');
  expect(indexResp.ok()).toBe(true);
  const index = await indexResp.json();
  expect(index.modules.length).toBeGreaterThan(0);

  for (const mod of index.modules) {
    const resp = await page.request.get(`/modules/${mod.file}`);
    expect(resp.ok()).toBe(true);
    const data = await resp.json();
    expect(data.module_id).toBe(mod.module_id);
    expect(data.default_title).toBeTruthy();
    expect(data.checklist).toBeDefined();
    expect(data.checklist.length).toBeGreaterThan(0);
  }
});

test('download buttons appear in expanded view', async ({ page }) => {
  await page.locator('#btn-expanded').click();
  await expect(page.locator('#pptx-btn')).toBeVisible();
  await expect(page.locator('#pdf-btn')).toBeVisible();
  await expect(page.locator('#docx-btn')).toBeVisible();
});
