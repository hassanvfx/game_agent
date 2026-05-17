const fs = require('fs');

(async () => {
  const host = '127.0.0.1';
  const port = 65286;
  const url = 'http://127.0.0.1:65286/index.html';

  let chromium;
  try {
    ({ chromium } = require('playwright'));
  } catch (e) {
    console.error('PLAYWRIGHT_REQUIRE_FAILED');
    console.error(e.message);
    process.exit(2);
  }

  const screenshots = [];
  const consoleErrors = [];
  const steps = [];
  let identityPassed = false;

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    isMobile: true,
    hasTouch: true,
    userAgent:
      'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36'
  });

  const page = await context.newPage();
  page.on('console', (msg) => {
    if (['error', 'warning'].includes(msg.type())) {
      consoleErrors.push({ type: msg.type(), text: msg.text() });
    }
  });
  page.on('pageerror', (err) => {
    consoleErrors.push({ type: 'pageerror', text: String(err) });
  });

  try {
    await page.goto(url, { waitUntil: 'load', timeout: 15000 });
    await page.screenshot({ path: 'playwright_initial.png', fullPage: true });

    const title = await page.title();
    const brand = await page.locator('.brand-title').textContent().catch(() => null);
    const subtitle = await page.locator('.brand-subtitle').textContent().catch(() => null);
    const strikes = await page.locator('#mistakes-display').textContent().catch(() => null);

    identityPassed =
      title === 'Zen Sudoku Flow' &&
      /ZEN GRID FLOW/.test(brand || '') &&
      /Pulse Sudoku/.test(subtitle || '') &&
      /0\/3/.test(strikes || '');

    screenshots.push({
      path: 'playwright_initial.png',
      step: 'initial_state',
      status: identityPassed ? 'neutral' : 'issues',
      observed: `title=${title}; brand=${brand}; subtitle=${subtitle}; strikes=${strikes}`
    });

    steps.push({
      step: 'initial_state',
      expected: 'Zen Sudoku Flow loads with title badge and HUD',
      actual: `title=${title}; brand=${brand}; subtitle=${subtitle}; strikes=${strikes}`
    });

    if (!identityPassed) {
      throw new Error('runtime-environment mismatch');
    }

    const canvas = page.locator('#gameCanvas');
    const box = await canvas.boundingBox();
    const tap1 = { x: box.x + 120, y: box.y + 180 };
    await page.mouse.click(tap1.x, tap1.y);
    await page.screenshot({ path: 'playwright_after_cell_select.png', fullPage: true });
    screenshots.push({
      path: 'playwright_after_cell_select.png',
      step: 'cell_selected',
      status: 'neutral',
      observed: 'grid tapped to reveal keypad'
    });

    const tap2 = { x: 36, y: 580 };
    await page.mouse.click(tap2.x, tap2.y);
    await page.waitForTimeout(300);
    await page.screenshot({ path: 'playwright_after_keypad_tap.png', fullPage: true });

    const mistakeText = await page.locator('#mistakes-display').textContent().catch(() => null);
    const resultVisible = await page
      .locator('#game-over-screen')
      .evaluate((el) => !el.classList.contains('hidden'))
      .catch(() => false);

    screenshots.push({
      path: 'playwright_after_keypad_tap.png',
      step: 'keypad_action',
      status: 'neutral',
      observed: `mistakes=${mistakeText}; gameOverVisible=${resultVisible}`
    });

    steps.push({
      step: 'select_cell',
      expected: 'tapping an editable cell should select it and allow keypad input',
      actual: 'input proceeded without crash'
    });

    steps.push({
      step: 'enter_digit',
      expected: 'tapping keypad should update selected cell or mistake count',
      actual: `mistakes=${mistakeText}; gameOverVisible=${resultVisible}`
    });
  } finally {
    await browser.close();
  }

  const lines = [];
  lines.push('# Playwright Observation Log', '');
  lines.push('- Launch method: dedicated local `python -m http.server` rooted at workspace');
  lines.push(`- Host: ${host}`);
  lines.push(`- Port: ${port}`);
  lines.push(`- Served entry URL: ${url}`);
  lines.push('- Mobile context: viewport 400x700, screen 400x700, touch enabled, mobile Android-style UA');
  lines.push(`- Runtime identity verification: ${identityPassed ? 'passed' : 'failed'}`);
  lines.push('', '## Interaction steps');
  for (const step of steps) {
    lines.push(`- **${step.step}**`);
    lines.push(`  - Expected: ${step.expected}`);
    lines.push(`  - Actual: ${step.actual}`);
  }

  lines.push('', '## Screenshots');
  for (const shot of screenshots) {
    lines.push(`- ${shot.path} | ${shot.step} | ${shot.status} | ${shot.observed}`);
  }

  lines.push('', '## Console/runtime observations');
  if (consoleErrors.length) {
    for (const entry of consoleErrors) {
      lines.push(`- ${entry.type}: ${entry.text}`);
    }
  } else {
    lines.push('- none observed');
  }

  lines.push('', '## Outcome');
  lines.push(`- Browser pass classification: ${identityPassed ? 'completed' : 'runtime-environment mismatch'}`);

  fs.writeFileSync('playwright_observation_log.md', lines.join('\n'));
  fs.writeFileSync('playwright_screenshots.json', JSON.stringify(screenshots, null, 2));
  if (consoleErrors.length) {
    fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
  }

  console.log(JSON.stringify({ identityPassed, screenshots: screenshots.length, consoleErrors: consoleErrors.length }));
})().catch((err) => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});