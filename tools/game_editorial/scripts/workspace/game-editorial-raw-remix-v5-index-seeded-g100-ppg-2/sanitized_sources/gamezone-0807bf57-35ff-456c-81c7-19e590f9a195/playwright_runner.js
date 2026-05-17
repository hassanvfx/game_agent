
const fs = require('fs');
const { chromium, devices } = require('playwright');
(async() => {
  const entryUrl = 'http://127.0.0.1:55330/index.html';
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    ...devices['Pixel 5'],
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const networkFailures = [];
  const screenshots = [];
  const steps = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push({ type: 'console', text: msg.text() });
  });
  page.on('pageerror', err => consoleErrors.push({ type: 'pageerror', text: String(err) }));
  page.on('response', response => {
    if (response.status() >= 400) networkFailures.push({ url: response.url(), status: response.status() });
  });

  await page.goto(entryUrl, { waitUntil: 'networkidle' });
  const title = await page.title();
  const startTitle = await page.locator('.start-title').textContent().catch(() => null);
  const startButton = await page.locator('#start-btn').textContent().catch(() => null);
  const identityPassed = title === 'Neon Courier 3D' && /Neon Courier/i.test(startTitle || '') && /Start Route/i.test(startButton || '');
  await page.screenshot({ path: 'playwright_initial.png', fullPage: true });
  screenshots.push({ path: 'playwright_initial.png', step: 'initial_state', status: 'neutral', observed: 'start card visible before play' });
  steps.push({ step: 'identity_check', expected: 'Neon Courier 3D start screen from this workspace', actual: `title=${title}; startTitle=${startTitle}; startButton=${startButton}`, result: identityPassed ? 'passed' : 'failed' });

  if (identityPassed) {
    await page.locator('#start-btn').click();
    await page.waitForTimeout(1200);
    const hudVisible = await page.locator('#hud').evaluate(el => !el.classList.contains('hidden'));
    const scoreText = await page.locator('#score').textContent();
    await page.screenshot({ path: 'playwright_after_start.png', fullPage: true });
    screenshots.push({ path: 'playwright_after_start.png', step: 'after_start', status: hudVisible ? 'ok' : 'broken', observed: `hudVisible=${hudVisible}, score=${scoreText}` });
    steps.push({ step: 'start_game', expected: 'HUD visible and render loop active after start', actual: `hudVisible=${hudVisible}, score=${scoreText}`, result: hudVisible ? 'passed' : 'failed' });

    if (hudVisible) {
      await page.locator('#quality-btn').click();
      await page.waitForTimeout(400);
      const qualityText = await page.locator('#quality-btn span:last-child').textContent();
      await page.locator('#cam-btn').click();
      await page.waitForTimeout(400);
      const camText = await page.locator('#cam-btn span:last-child').textContent();
      await page.screenshot({ path: 'playwright_toggles.png', fullPage: true });
      screenshots.push({ path: 'playwright_toggles.png', step: 'toggle_controls', status: /LOW/i.test(qualityText || '') && /TOP/i.test(camText || '') ? 'ok' : 'broken', observed: `quality=${qualityText}, cam=${camText}` });
      steps.push({ step: 'toggle_controls', expected: 'Quality and camera labels update after taps', actual: `quality=${qualityText}, cam=${camText}`, result: /LOW/i.test(qualityText || '') && /TOP/i.test(camText || '') ? 'passed' : 'failed' });

      await page.screenshot({ path: 'playwright_mobile_ingame.png', fullPage: true });
      screenshots.push({ path: 'playwright_mobile_ingame.png', step: 'mobile_ingame', status: 'neutral', observed: 'mobile HUD and joystick remain visible in-game' });
      const joyVisible = await page.locator('#joystick-zone').isVisible().catch(() => false);
      steps.push({ step: 'mobile_layout', expected: 'Joystick visible in mobile context', actual: `joystickVisible=${joyVisible}`, result: joyVisible ? 'passed' : 'failed' });
    }
  }

  fs.writeFileSync('playwright_eval.json', JSON.stringify({
    host: '127.0.0.1',
    port: 55330,
    entryUrl,
    mobileContext: {
      viewport: { width: 400, height: 700 },
      screen: { width: 400, height: 700 },
      hasTouch: true,
      userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    },
    identityPassed,
    screenshots,
    steps,
    consoleErrors,
    networkFailures
  }, null, 2));
  if (consoleErrors.length) {
    fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
  }
  fs.writeFileSync('playwright_screenshots.json', JSON.stringify(screenshots, null, 2));
  await context.close();
  await browser.close();
})().catch(err => {
  fs.writeFileSync('playwright_eval.json', JSON.stringify({ fatal: String(err && err.stack || err) }, null, 2));
  process.exit(1);
});
