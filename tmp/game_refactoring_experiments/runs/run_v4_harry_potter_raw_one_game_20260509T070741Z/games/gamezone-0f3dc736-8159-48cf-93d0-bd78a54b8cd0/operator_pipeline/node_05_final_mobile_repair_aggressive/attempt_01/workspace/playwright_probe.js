const { chromium, devices } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ ...devices['iPhone 8'] });
  const page = await context.newPage();
  const logs = [];

  page.on('console', (msg) => logs.push(`[console:${msg.type()}] ${msg.text()}`));
  page.on('pageerror', (err) => logs.push(`[pageerror] ${err.message}`));
  page.on('requestfailed', (req) => {
    const failure = req.failure();
    logs.push(`[requestfailed] ${req.url()} :: ${failure ? failure.errorText : 'unknown'}`);
  });
  page.on('response', (response) => {
    if (response.status() >= 400) {
      logs.push(`[response:${response.status()}] ${response.url()}`);
    }
  });

  await page.goto('http://127.0.0.1:43108/', { waitUntil: 'load' });
  await page.screenshot({ path: 'screens_01_title_or_entry.png' });

  await page.click('#startBtn');
  await page.waitForTimeout(1200);
  await page.screenshot({ path: 'screens_02_live_play.png' });

  const box = await page.locator('canvas').boundingBox();
  if (box) {
    await page.mouse.move(box.x + box.width / 2, box.y + box.height - 80);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width / 2 + 60, box.y + box.height - 220, { steps: 8 });
    await page.mouse.up();
    await page.waitForTimeout(1500);
  }

  await page.screenshot({ path: 'screens_probe_after_shot.png' });

  await page.click('#muteBtn');
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'screens_03_controls_or_audio.png' });

  await page.evaluate(() => {
    if (typeof gameOver === 'function') {
      gameOver();
    }
  });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'screens_04_fail_or_win.png' });

  fs.writeFileSync('runtime_baseline.log', logs.join('\n'));
  await browser.close();
})().catch((err) => {
  console.error(err);
  process.exit(1);
});