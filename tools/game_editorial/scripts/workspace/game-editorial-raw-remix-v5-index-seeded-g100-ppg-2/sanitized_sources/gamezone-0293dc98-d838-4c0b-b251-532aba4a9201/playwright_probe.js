const fs = require('fs');

(async () => {
  const mod = require('playwright');
  const chromium = mod.chromium || (mod.default && mod.default.chromium);
  if (!chromium) throw new Error('Playwright chromium not available');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
  });

  const page = await context.newPage();
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push({ type: 'console', text: msg.text() });
  });
  page.on('pageerror', err => {
    consoleErrors.push({ type: 'pageerror', text: String(err) });
  });

  const screenshots = [];
  const url = 'http://127.0.0.1:50903/index.html';

  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);

  const title = await page.title();
  const heading = (await page.locator('h1').first().textContent().catch(() => '')) || '';
  const runtimeIdentityPassed = title.includes('Quiet Shift') && heading.includes('QUIET') && heading.includes('SHIFT');

  await page.screenshot({ path: 'playwright_initial.png', fullPage: true });
  screenshots.push({
    path: 'playwright_initial.png',
    step: 'initial_state',
    status: runtimeIdentityPassed ? 'neutral' : 'mismatch',
    observed: `title=${title}; heading=${heading.trim()}`
  });

  if (!runtimeIdentityPassed) {
    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(screenshots, null, 2));
    if (consoleErrors.length) fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
    await browser.close();
    throw new Error('runtime-environment mismatch');
  }

  await page.locator('#btn-start').click();
  await page.waitForTimeout(1000);

  await page.screenshot({ path: 'playwright_after_start.png', fullPage: true });
  const levelText = (await page.locator('#level-display').textContent().catch(() => '')) || '';
  screenshots.push({
    path: 'playwright_after_start.png',
    step: 'after_start',
    status: 'neutral',
    observed: `level display=${levelText.trim()}`
  });

  const canvas = page.locator('#gameCanvas');
  await canvas.dispatchEvent('pointerdown', { clientX: 90, clientY: 560, pointerType: 'touch', isPrimary: true, button: 0, buttons: 1 });
  await page.waitForTimeout(1800);
  await canvas.dispatchEvent('pointerup', { clientX: 90, clientY: 560, pointerType: 'touch', isPrimary: true, button: 0, buttons: 0 });
  await page.waitForTimeout(500);

  await page.screenshot({ path: 'playwright_after_pet.png', fullPage: true });
  const loveWidth = await page.locator('#love-bar').evaluate(el => getComputedStyle(el).width).catch(() => 'unknown');
  screenshots.push({
    path: 'playwright_after_pet.png',
    step: 'after_first_action',
    status: 'neutral',
    observed: `love bar width=${loveWidth}`
  });

  const resultVisible = await page.locator('#result-screen').evaluate(el => !el.classList.contains('hidden')).catch(() => false);
  if (resultVisible) {
    await page.screenshot({ path: 'playwright_broken_state.png', fullPage: true });
    const desc = (await page.locator('#res-desc').textContent().catch(() => '')) || '';
    screenshots.push({
      path: 'playwright_broken_state.png',
      step: 'broken_state',
      status: 'issue',
      observed: desc.trim()
    });
  }

  fs.writeFileSync('playwright_screenshots.json', JSON.stringify(screenshots, null, 2));
  if (consoleErrors.length) fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));

  await browser.close();
  console.log(JSON.stringify({
    url,
    title,
    heading: heading.trim(),
    runtimeIdentityPassed,
    levelText: levelText.trim(),
    resultVisible,
    consoleErrors: consoleErrors.length,
    screenshots: screenshots.map(s => s.path)
  }, null, 2));
})().catch(err => {
  console.error(err && err.stack || String(err));
  process.exit(1);
});
