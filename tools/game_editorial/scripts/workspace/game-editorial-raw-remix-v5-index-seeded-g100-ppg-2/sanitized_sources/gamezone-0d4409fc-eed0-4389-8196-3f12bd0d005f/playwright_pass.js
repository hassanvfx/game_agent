const fs = require('fs');

(async () => {
  const url = 'http://127.0.0.1:60518/index.html';
  let pw;
  try {
    pw = require('playwright');
  } catch (e) {
    console.error('PLAYWRIGHT_REQUIRE_FAILED');
    console.error(String((e && e.stack) || e));
    process.exit(2);
  }

  const { chromium, devices } = pw;
  const browser = await chromium.launch({ headless: true });
  const device = devices['Pixel 5'] || {};

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
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push({ type: 'console', text: msg.text() });
    }
  });
  page.on('pageerror', (err) => {
    consoleErrors.push({ type: 'pageerror', text: String((err && err.stack) || err) });
  });

  const shots = [];
  const observation = {
    host: '127.0.0.1',
    port: 60518,
    entryUrl: url,
    mobileContext: {
      viewport: '400x700',
      screen: '400x700',
      touch: true,
      userAgent: 'Android-style custom UA'
    },
    identity: { passed: false, signals: [] },
    steps: []
  };

  try {
    await page.goto(url, { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(1200);

    const initialTitle = await page.title();
    const startTitle = await page.locator('#start-screen h1').innerText().catch(() => null);
    const missionText = await page.locator('#start-screen .story-card').innerText().catch(() => null);

    if (initialTitle === 'Cherryton: Classrooms & Chats') {
      observation.identity.signals.push('document title matched Cherryton: Classrooms & Chats');
    }
    if (startTitle === 'SNACK SCOUT') {
      observation.identity.signals.push('start heading matched SNACK SCOUT');
    }
    if (missionText && missionText.includes('Collect 5 lunches')) {
      observation.identity.signals.push('mission text includes Collect 5 lunches');
    }

    observation.identity.passed = observation.identity.signals.length >= 2;

    await page.screenshot({ path: 'playwright_initial.png' });
    shots.push({
      path: 'playwright_initial.png',
      step: 'initial_state',
      status: observation.identity.passed ? 'neutral' : 'mismatch',
      observed: `title=${initialTitle}; heading=${startTitle}`
    });
    observation.steps.push({
      step: 'initial_state',
      expected: 'Start screen for Snack Scout-style lunch collection game is visible.',
      actual: `title=${initialTitle}; heading=${startTitle}; identityPassed=${observation.identity.passed}`
    });

    if (!observation.identity.passed) {
      throw new Error('RUNTIME_IDENTITY_MISMATCH');
    }

    await page.locator('#start-btn').click();
    await page.waitForTimeout(1000);

    await page.screenshot({ path: 'playwright_after_start.png' });
    const hudScore = await page.locator('#score-display').innerText().catch(() => null);
    const hudChar = await page.locator('#char-name').innerText().catch(() => null);
    const joystickVisible = await page
      .locator('#joystick-zone')
      .evaluate((el) => getComputedStyle(el).opacity)
      .catch(() => null);

    shots.push({
      path: 'playwright_after_start.png',
      step: 'after_start',
      status: 'neutral',
      observed: `score=${hudScore}; char=${hudChar}; joystickOpacity=${joystickVisible}`
    });
    observation.steps.push({
      step: 'after_start',
      expected: 'HUD becomes visible, joystick appears, game starts at 0/5.',
      actual: `score=${hudScore}; char=${hudChar}; joystickOpacity=${joystickVisible}`
    });

    const box = await page.locator('#joystick-zone').boundingBox();
    if (box) {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      await page.mouse.move(box.x + box.width / 2, box.y + 30, { steps: 8 });
      await page.waitForTimeout(1200);
      await page.mouse.up();
    }

    await page.waitForTimeout(400);
    await page.screenshot({ path: 'playwright_after_move.png' });
    const dialogueOpacity = await page
      .locator('#dialogue-container')
      .evaluate((el) => getComputedStyle(el).opacity)
      .catch(() => null);
    const winHidden = await page
      .locator('#win-screen')
      .evaluate((el) => el.classList.contains('hidden'))
      .catch(() => null);

    shots.push({
      path: 'playwright_after_move.png',
      step: 'after_move',
      status: 'neutral',
      observed: `dialogueOpacity=${dialogueOpacity}; winHidden=${winHidden}`
    });
    observation.steps.push({
      step: 'after_move',
      expected: 'Player can move via virtual joystick without layout breakage or crash.',
      actual: `dialogueOpacity=${dialogueOpacity}; winHidden=${winHidden}`
    });

    await page.locator('#switch-btn').click();
    await page.waitForTimeout(500);

    await page.screenshot({ path: 'playwright_after_switch.png' });
    const switchedChar = await page.locator('#char-name').innerText().catch(() => null);
    const dialogueSpeaker = await page.locator('#dialogue-speaker').innerText().catch(() => null);
    const dialogueText = await page.locator('#dialogue-text').innerText().catch(() => null);

    shots.push({
      path: 'playwright_after_switch.png',
      step: 'after_switch',
      status: 'neutral',
      observed: `char=${switchedChar}; speaker=${dialogueSpeaker}`
    });
    observation.steps.push({
      step: 'after_switch',
      expected: 'Switch button cycles character and shows flavor dialogue.',
      actual: `char=${switchedChar}; speaker=${dialogueSpeaker}; text=${dialogueText}`
    });
  } finally {
    if (consoleErrors.length) {
      fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
    }

    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(shots, null, 2));

    const lines = [
      '# Playwright Observation Log',
      '',
      '- Launch method: python3 -m http.server 60518 --bind 127.0.0.1',
      `- Host: ${observation.host}`,
      `- Port: ${observation.port}`,
      `- Served entry URL: ${observation.entryUrl}`,
      '- Mobile context: viewport 400x700, screen 400x700, touch enabled, Android-style user agent',
      '',
      `- Runtime identity verification: ${observation.identity.passed ? 'passed' : 'failed'}`,
      ...observation.identity.signals.map((s) => `  - ${s}`),
      '',
      '## Interaction Steps',
      ...observation.steps.map(
        (s) => `- **${s.step}**\n  - Expected: ${s.expected}\n  - Actual: ${s.actual}`
      ),
      '',
      '## Screenshots',
      ...shots.map((s) => `- ${s.path} | ${s.step} | ${s.status} | ${s.observed}`),
      '',
      `- Bug hypothesis support: ${
        consoleErrors.length
          ? 'weakly suggests runtime issues due to observed console/page errors'
          : 'fails to support a bug hypothesis from the bounded pass'
      }`
    ];

    fs.writeFileSync('playwright_observation_log.md', lines.join('\n'));

    await context.close();
    await browser.close();
  }
})().catch((err) => {
  console.error(String((err && err.stack) || err));
  process.exit(1);
});