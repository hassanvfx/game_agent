const { chromium, devices } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    ...devices['Pixel 5'],
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 }
  });
  const page = await context.newPage();
  const logs = [];
  const errors = [];

  page.on('console', (msg) => logs.push({ type: msg.type(), text: msg.text() }));
  page.on('pageerror', (err) => errors.push({ type: 'pageerror', text: String(err) }));

  await page.goto('http://127.0.0.1:43100/index.html', { waitUntil: 'networkidle' });
  await page.screenshot({ path: 'previsual_screen_01_title_or_entry.png' });

  const title = await page.title();
  const bodyText = await page.locator('body').innerText();

  await page.click('#btn-start');
  await page.waitForTimeout(1200);
  await page.screenshot({ path: 'previsual_screen_02_live_play.png' });

  await page.mouse.move(200, 500);
  await page.mouse.down();
  await page.mouse.move(260, 420, { steps: 8 });
  await page.mouse.up();
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'previsual_screen_03_menu_or_modal.png' });

  fs.writeFileSync(
    'previsual_runtime_observation.json',
    JSON.stringify({ title, bodySnippet: bodyText.slice(0, 400), logs, errors }, null, 2)
  );

  await browser.close();
})().catch((err) => {
  console.error(err);
  process.exit(1);
});