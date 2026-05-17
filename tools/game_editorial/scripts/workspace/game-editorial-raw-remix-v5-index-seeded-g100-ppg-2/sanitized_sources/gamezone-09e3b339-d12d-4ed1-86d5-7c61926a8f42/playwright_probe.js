const fs = require('fs');

(async () => {
  const url = 'http://127.0.0.1:56068/index.html';
  let pw;
  try {
    pw = require('playwright');
  } catch (e1) {
    try {
      pw = require('/usr/local/lib/node_modules/playwright');
    } catch (e2) {
      try {
        pw = require('/opt/homebrew/lib/node_modules/playwright');
      } catch (e3) {
        console.error('PLAYWRIGHT_UNAVAILABLE');
        process.exit(2);
      }
    }
  }

  const { chromium, devices } = pw;
  const device = devices['Pixel 5'] || {};
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    ...device,
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    isMobile: true,
    hasTouch: true,
    userAgent:
      'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const shots = [];

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push({ type: 'console', text: msg.text() });
    }
  });

  page.on('pageerror', (err) => {
    consoleErrors.push({ type: 'pageerror', text: String(err) });
  });

  await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

  const title = await page.title();
  const startText = await page.locator('#start-screen').innerText().catch(() => '');
  const identityPass =
    title === 'Midnight Street Chef' &&
    /STREET CHEF/.test(startText) &&
    /OPEN SHOP/.test(startText);

  await page.screenshot({ path: 'playwright_initial.png' });
  shots.push({
    path: 'playwright_initial.png',
    step: 'initial_state',
    status: identityPass ? 'neutral' : 'issues',
    observed: identityPass
      ? 'start screen visible with expected title and open shop CTA'
      : 'runtime identity mismatch at start'
  });

  if (!identityPass) {
    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(shots, null, 2));
    fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
    fs.writeFileSync(
      'playwright_run_data.json',
      JSON.stringify({ url, title, startText, identityPass, shots }, null, 2)
    );
    await browser.close();
    process.exit(3);
  }

  await page.locator('#start-btn').click({ force: true });
  await page.waitForTimeout(1200);

  await page.screenshot({ path: 'playwright_after_start.png' });
  const cookVisible = await page.locator('#cookBtn').isVisible();
  const cash = await page.locator('#scoreVal').innerText();
  const stock = await page.locator('#stockVal').innerText();
  shots.push({
    path: 'playwright_after_start.png',
    step: 'after_start',
    status: cookVisible ? 'neutral' : 'issues',
    observed: cookVisible
      ? 'play state visible with cash ' + cash + ' and stock ' + stock
      : 'cook button missing after start'
  });

  const cookBtn = page.locator('#cookBtn');
  for (let i = 0; i < 5; i++) {
    await cookBtn.dispatchEvent('pointerdown');
    await page.waitForTimeout(90);
  }

  await page.waitForTimeout(400);
  await page.screenshot({ path: 'playwright_after_cook_attempt.png' });
  const stockAfter5 = await page.locator('#stockVal').innerText();
  shots.push({
    path: 'playwright_after_cook_attempt.png',
    step: 'after_cook_attempt',
    status: Number(stockAfter5) > 0 ? 'neutral' : 'issues',
    observed: 'stock after 5 taps: ' + stockAfter5
  });

  await page.waitForTimeout(3500);
  await page.screenshot({ path: 'playwright_customer_flow.png' });
  const cashLater = await page.locator('#scoreVal').innerText();
  shots.push({
    path: 'playwright_customer_flow.png',
    step: 'customer_flow',
    status: Number(cashLater) > 0 ? 'neutral' : 'issues',
    observed: 'cash after bounded wait: ' + cashLater
  });

  fs.writeFileSync('playwright_screenshots.json', JSON.stringify(shots, null, 2));
  fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
  fs.writeFileSync(
    'playwright_run_data.json',
    JSON.stringify(
      { url, title, startText, identityPass, cookVisible, cash, stock, stockAfter5, cashLater, consoleErrorsCount: consoleErrors.length },
      null,
      2
    )
  );

  await browser.close();
})().catch((err) => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});