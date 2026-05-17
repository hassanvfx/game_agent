const fs = require('fs');
const { chromium, devices } = require('playwright');

(async () => {
  const port = 55971;
  const url = `http://127.0.0.1:${port}/index.html`;
  const device = {
    ...devices['Pixel 5'],
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    isMobile: true,
    hasTouch: true,
    userAgent:
      'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
  };

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext(device);
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

  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });

    const title = await page.title();
    const heading = await page.locator('#start-screen .screen-title').textContent().catch(() => null);
    const identityPassed = title === 'Clean Sweep Bot' && heading && heading.includes('Clean Sweep Bot');

    await page.screenshot({ path: 'playwright_initial.png', fullPage: true });
    shots.push({
      path: 'playwright_initial.png',
      step: 'initial_state',
      status: identityPassed ? 'neutral' : 'issues',
      observed: identityPassed
        ? 'start screen with Clean Sweep Bot title visible'
        : 'runtime identity verification failed'
    });

    if (identityPassed) {
      await page.locator('#start-btn').click();
      await page.waitForTimeout(1200);

      await page.screenshot({ path: 'playwright_after_start.png', fullPage: true });
      const hudText = await page.locator('#score').textContent().catch(() => null);
      shots.push({
        path: 'playwright_after_start.png',
        step: 'after_start',
        status: 'neutral',
        observed: `canvas gameplay active with HUD score ${hudText}`
      });

      await page.locator('#gameCanvas').click({ position: { x: 340, y: 620 } });
      await page.waitForTimeout(2200);

      await page.screenshot({ path: 'playwright_after_interaction.png', fullPage: true });
      const gameOverVisible = await page
        .locator('#game-over-screen')
        .evaluate((el) => !el.classList.contains('hidden'))
        .catch(() => false);
      const scoreNow = await page.locator('#score').textContent().catch(() => null);

      shots.push({
        path: 'playwright_after_interaction.png',
        step: 'bounded_interaction',
        status: gameOverVisible ? 'issues' : 'neutral',
        observed: gameOverVisible
          ? 'game over screen appeared during bounded mobile tap interaction'
          : `mobile tap-guided run remained active; HUD score ${scoreNow}`
      });
    }

    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(shots, null, 2));

    if (consoleErrors.length) {
      fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
    }

    const observation = [
      '# Playwright Observation Log',
      '',
      '- Launch method: dedicated local HTTP server via `python3 -m http.server 55971 --bind 127.0.0.1` rooted at workspace',
      '- Host: `127.0.0.1`',
      '- Port: `55971`',
      `- Served entry URL: \`${url}\``,
      '- Mobile context: viewport 400x700, screen 400x700, touch enabled, Android-style user agent, isolated Chromium context',
      `- Runtime identity verification: ${shots[0]?.status === 'neutral' ? 'passed' : 'failed'}`,
      '- Interaction steps attempted: load start screen; capture initial state; tap Start Run; wait for gameplay; perform bounded mobile tap interaction on canvas; capture results',
      `- Screenshots captured: ${shots.map((s) => `\`${s.path}\``).join(', ')}`,
      '- Expected: Clean Sweep Bot start screen should load, Start Run should begin gameplay, mobile tap guidance should keep the game playable on mobile, no runtime errors should appear during bounded pass',
      `- Actual: ${shots.map((s) => `${s.step}: ${s.observed}`).join(' | ')}`,
      `- Bug hypothesis support: ${
        consoleErrors.length
          ? 'weakly suggests an issue because runtime errors were observed'
          : 'fails to support a bug hypothesis in this bounded pass'
      }`
    ];

    fs.writeFileSync('playwright_observation_log.md', observation.join('\n'));
    await browser.close();
  } catch (err) {
    try {
      fs.writeFileSync('playwright_screenshots.json', JSON.stringify(shots, null, 2));
    } catch {}

    if (consoleErrors.length) {
      try {
        fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
      } catch {}
    }

    fs.writeFileSync(
      'playwright_observation_log.md',
      [
        '# Playwright Observation Log',
        '',
        '- Launch method: dedicated local HTTP server via `python3 -m http.server 55971 --bind 127.0.0.1` rooted at workspace',
        '- Host: `127.0.0.1`',
        '- Port: `55971`',
        `- Served entry URL: \`${url}\``,
        '- Mobile context: viewport 400x700, screen 400x700, touch enabled, Android-style user agent, isolated Chromium context',
        '- Runtime identity verification: failed due to browser automation error',
        '- Interaction steps attempted: page load only',
        `- Actual: ${String(err).replace(/\n/g, ' ')}`,
        '- Bug hypothesis support: fails to support a bug hypothesis because the browser pass did not complete reliably'
      ].join('\n')
    );

    await browser.close().catch(() => {});
    process.exit(1);
  }
})();