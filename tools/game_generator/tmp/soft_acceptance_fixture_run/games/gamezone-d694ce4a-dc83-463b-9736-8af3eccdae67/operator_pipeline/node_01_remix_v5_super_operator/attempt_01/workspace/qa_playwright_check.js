const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const rootUrl = 'http://127.0.0.1:43137/';
const out = p => path.join(__dirname, p);

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const evidence = { rootUrl, checks: {}, consoleErrors: [], screenshots: [] };
  page.on('console', msg => {
    if (msg.type() !== 'error') return;
    const text = msg.text();
    if (/Failed to load resource/.test(text)) {
      evidence.nonBlockingResourceNoise = evidence.nonBlockingResourceNoise || [];
      evidence.nonBlockingResourceNoise.push(text);
      return;
    }
    evidence.consoleErrors.push(text);
  });
  page.on('pageerror', err => evidence.consoleErrors.push(err.message));

  await page.goto(rootUrl + 'index_old.html', { waitUntil: 'networkidle', timeout: 30000 });
  await page.screenshot({ path: out('v5_before_index_trash.png'), fullPage: true });
  evidence.screenshots.push('v5_before_index_trash.png');
  evidence.beforeConsoleErrors = evidence.consoleErrors.slice();
  evidence.consoleErrors = [];

  await page.goto(rootUrl, { waitUntil: 'networkidle', timeout: 30000 });
  evidence.checks.boot_load = await page.locator('#intro-screen').isVisible();
  await page.screenshot({ path: out('v5_after_entry.png'), fullPage: true });
  evidence.screenshots.push('v5_after_entry.png');

  await page.evaluate(() => document.getElementById('intro-screen').click());
  await page.waitForTimeout(1200);
  evidence.checks.spawn_flow = await page.locator('canvas').isVisible();
  evidence.checks.hud_heat = (await page.locator('#wanted-text').innerText()).includes('HEAT');
  await page.screenshot({ path: out('v5_after_spawn.png'), fullPage: true });
  evidence.screenshots.push('v5_after_spawn.png');

  await page.locator('#btn-up').dispatchEvent('pointerdown');
  await page.waitForTimeout(250);
  await page.locator('#btn-up').dispatchEvent('pointerup');
  await page.locator('#shoot').dispatchEvent('pointerdown');
  await page.waitForTimeout(250);
  await page.locator('#camera').tap();
  await page.locator('#enterCar').tap();
  await page.waitForTimeout(600);
  evidence.checks.merge_flow = await page.locator('#ui-layer').isVisible();
  evidence.checks.mobile_viewport = await page.evaluate(() => window.innerWidth === 390 && window.innerHeight === 844);
  evidence.checks.controls_reachable = await page.locator('#shoot').isVisible() && await page.locator('#enterCar').isVisible();
  await page.screenshot({ path: out('v5_after_merge.png'), fullPage: true });
  evidence.screenshots.push('v5_after_merge.png');

  evidence.checks.console_errors = evidence.consoleErrors.length;
  fs.writeFileSync(out('runtime_evidence.json'), JSON.stringify(evidence, null, 2));
  await browser.close();
  if (!evidence.checks.boot_load || !evidence.checks.spawn_flow || evidence.consoleErrors.length) {
    console.error(JSON.stringify(evidence, null, 2));
    process.exit(1);
  }
  console.log(JSON.stringify(evidence, null, 2));
})();
