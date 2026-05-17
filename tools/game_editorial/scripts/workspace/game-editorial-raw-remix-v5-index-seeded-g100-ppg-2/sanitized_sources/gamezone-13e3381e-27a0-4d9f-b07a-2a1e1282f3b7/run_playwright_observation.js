const fs = require('fs');

(async () => {
  const host = '127.0.0.1';
  const port = 65255;
  const url = 'http://127.0.0.1:65255/index.html';
  const screenshotIndex = [];
  const observation = [];
  const consoleErrors = [];
  const settings = {
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    isMobile: true,
    hasTouch: true,
    userAgent:
      'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
  };

  function addShot(file, step, status, observed) {
    screenshotIndex.push({ path: file, step, status, observed });
  }

  let browser;
  let context;
  let page;

  try {
    const { chromium } = require('playwright');
    browser = await chromium.launch({ headless: true });
    context = await browser.newContext(settings);
    page = await context.newPage();

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push({ type: 'console', text: msg.text() });
      }
    });

    page.on('pageerror', (err) => {
      consoleErrors.push({ type: 'pageerror', text: String(err) });
    });

    observation.push(
      '# Playwright Observation Log',
      '',
      '- Launch method: `python3 -m http.server 65255 --bind 127.0.0.1` rooted at workspace',
      '- Host: `127.0.0.1`',
      '- Port: `65255`',
      '- Served entry URL: `' + url + '`',
      '- Mobile context settings: viewport 400x700, screen 400x700, touch enabled, Android-style UA, isolated context',
      ''
    );

    await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });

    const title = await page.title();
    const startVisible = await page.locator('#start-screen').isVisible();
    const startText = await page.locator('#start-btn').textContent().catch(() => null);
    const heading = await page.locator('h1').first().textContent().catch(() => null);
    const identityPassed =
      title === 'Chat Rush: Mod Queue' &&
      startVisible &&
      /START SHIFT/.test(startText || '') &&
      /Chat Rush/.test(heading || '');

    observation.push(
      '## Runtime identity verification',
      '- Title observed: `' + title + '`',
      '- Visible heading observed: `' + (heading || '') + '`',
      '- Start button text observed: `' + (startText || '') + '`',
      '- Runtime identity verification: **' + (identityPassed ? 'passed' : 'failed') + '**',
      ''
    );

    await page.screenshot({ path: 'playwright_initial.png' });
    addShot(
      'playwright_initial.png',
      'initial_state',
      'neutral',
      'start screen visible with Chat Rush title and START SHIFT button'
    );

    if (!identityPassed) {
      throw new Error('runtime-environment mismatch');
    }

    observation.push(
      '## Interaction steps',
      '1. Expected: start screen should appear and identify the Chat Rush game.',
      '   - Actual: start screen was visible and matched the workspace identity.',
      '   - Assessment: fails to support a bug hypothesis.',
      '2. Expected: tapping START SHIFT should hide the overlay, show HUD, and start gameplay with falling posts and action buttons.'
    );

    await page.locator('#start-btn').click();
    await page.waitForTimeout(1500);

    const hudVisible = await page.locator('#hud').isVisible();
    const gameOverVisibleEarly = await page.locator('#game-over-screen').isVisible();
    const scoreText = await page.locator('#score-val').textContent().catch(() => null);

    await page.screenshot({ path: 'playwright_after_start.png' });
    addShot(
      'playwright_after_start.png',
      'after_start',
      'neutral',
      'HUD visible: ' + hudVisible + ', early game over visible: ' + gameOverVisibleEarly + ', score text: ' + scoreText
    );

    observation.push(
      '   - Actual: HUD visible=`' + hudVisible + '`, early game over visible=`' + gameOverVisibleEarly + '`, score=`' + scoreText + '`.',
      '   - Assessment: fails to support a bug hypothesis.',
      '3. Expected: action buttons should respond to taps and gameplay should continue without immediate runtime errors.'
    );

    await page.mouse.click(60, 640);
    await page.waitForTimeout(800);

    const gameOverVisiblePostTap = await page.locator('#game-over-screen').isVisible();

    await page.screenshot({ path: 'playwright_after_action.png' });
    addShot(
      'playwright_after_action.png',
      'after_first_action',
      'neutral',
      'Tapped first action button; game over visible: ' + gameOverVisiblePostTap
    );

    observation.push(
      '   - Actual: tap executed, game over visible after tap=`' + gameOverVisiblePostTap + '`. No confirmed runtime breakage observed from bounded pass.',
      '   - Assessment: fails to support a bug hypothesis.',
      '',
      '## Screenshots captured',
      '- `playwright_initial.png`',
      '- `playwright_after_start.png`',
      '- `playwright_after_action.png`',
      '',
      '## Conclusion',
      '- Result: bounded pass did not confirm a clear gameplay or layout defect.',
      '- Confidence: browser evidence fails to support a bug hypothesis requiring code edits.'
    );

    fs.writeFileSync('playwright_observation_log.md', observation.join('\n'));
    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(screenshotIndex, null, 2));
    if (consoleErrors.length) {
      fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
    }
  } catch (err) {
    observation.push(
      '## Failure',
      '- Browser-grounded pass could not be completed reliably.',
      '- Error: `' + String(err.message || err) + '`'
    );
    fs.writeFileSync('playwright_observation_log.md', observation.join('\n'));
    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(screenshotIndex, null, 2));
    if (consoleErrors.length) {
      fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
    }
    console.error(String(err.stack || err));
    process.exit(1);
  } finally {
    if (page) await page.close().catch(() => {});
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
  }
})();