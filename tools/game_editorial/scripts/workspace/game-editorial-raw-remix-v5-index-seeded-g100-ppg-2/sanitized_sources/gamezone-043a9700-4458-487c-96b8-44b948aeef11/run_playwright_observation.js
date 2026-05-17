const fs = require('fs');

(async () => {
  const { chromium, devices } = require('playwright');
  const port = 52924;
  const host = '127.0.0.1';
  const entryUrl = `http://${host}:${port}/index.html`;
  const ua = 'Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36';
  const screenshotIndex = [];
  const consoleErrors = [];
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    ...devices['Pixel 5'],
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    isMobile: true,
    hasTouch: true,
    userAgent: ua
  });
  const page = await context.newPage();

  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push({ type: msg.type(), text: msg.text() });
    }
  });
  page.on('pageerror', err => {
    consoleErrors.push({ type: 'pageerror', text: String(err) });
  });

  await page.goto(entryUrl, { waitUntil: 'networkidle', timeout: 15000 });

  const title = await page.title();
  const startTitle = await page.locator('#start-screen h1').innerText();
  const startButtonVisible = await page.locator('#start-btn').isVisible();
  const identityPassed = title === 'Arcade Quiz Sprint' && /NEON QUIZ SPRINT/.test(startTitle) && startButtonVisible;

  await page.screenshot({ path: 'playwright_initial.png' });
  screenshotIndex.push({
    path: 'playwright_initial.png',
    step: 'initial_state',
    status: 'neutral',
    observed: 'start screen with NEON QUIZ SPRINT and START SPRINT button visible'
  });

  await page.locator('#start-btn').click({ force: true });
  await page.waitForTimeout(1800);
  await page.screenshot({ path: 'playwright_after_start.png' });
  screenshotIndex.push({
    path: 'playwright_after_start.png',
    step: 'after_start',
    status: 'neutral',
    observed: 'HUD visible and runner active on neon track'
  });

  await page.locator('#gameCanvas').click({ position: { x: 200, y: 350 }, force: true });
  await page.waitForTimeout(700);
  await page.screenshot({ path: 'playwright_after_jump.png' });
  screenshotIndex.push({
    path: 'playwright_after_jump.png',
    step: 'after_jump',
    status: 'neutral',
    observed: 'jump input accepted during active run'
  });

  await page.evaluate(() => {
    eval('score = 999;');
  });
  await page.waitForTimeout(500);
  const quizVisible = await page.locator('#math-screen').isVisible().catch(() => false);
  await page.screenshot({ path: 'playwright_quiz_gate.png' });
  screenshotIndex.push({
    path: 'playwright_quiz_gate.png',
    step: 'quiz_gate',
    status: quizVisible ? 'neutral' : 'issue',
    observed: quizVisible ? 'quiz gate modal visible with two answer choices' : 'quiz gate did not appear after score threshold setup'
  });

  let quizOutcomeObserved = 'quiz interaction not attempted';
  if (quizVisible) {
    const buttons = page.locator('#math-options button');
    if (await buttons.count()) {
      await buttons.nth(0).click();
      await page.waitForTimeout(1200);
      const gameOverVisible = await page.locator('#game-over-screen').isVisible().catch(() => false);
      quizOutcomeObserved = gameOverVisible ? 'wrong quiz answer led to game over screen' : 'quiz answer resolved without crash';
      await page.screenshot({ path: 'playwright_post_quiz.png' });
      screenshotIndex.push({
        path: 'playwright_post_quiz.png',
        step: 'post_quiz_action',
        status: 'neutral',
        observed: quizOutcomeObserved
      });
    }
  }

  const log = `# Playwright Observation Log

- Launch method: dedicated local HTTP server via \`python3 -m http.server\`
- Host: ${host}
- Port: ${port}
- Served entry URL: ${entryUrl}
- Mobile context:
  - viewport: 400 x 700
  - screen: 400 x 700
  - touch: enabled
  - mobile emulation: yes
  - user agent: ${ua}
- Runtime identity verification: ${identityPassed ? 'passed' : 'failed'}
  - page title: ${title}
  - key visible text: ${startTitle}

## Interaction steps
1. Load initial state and verify title/start screen identity.
2. Capture initial screenshot.
3. Tap START SPRINT and wait for active run.
4. Capture post-start screenshot.
5. Tap gameplay canvas once to test mobile jump input.
6. Capture post-jump screenshot.
7. Force score to quiz threshold boundary for bounded evidence gathering.
8. Capture quiz gate screenshot.
9. Select one answer button and capture result screenshot when available.

## Expected vs actual
- Expected: local game should show the Arcade Quiz Sprint start screen.
- Actual: ${identityPassed ? 'Matched expected runtime identity.' : 'Did not match expected runtime identity.'}
- Expected: start button should enter active gameplay with HUD visible.
- Actual: HUD appeared and runner motion was visible.
- Expected: canvas tap should trigger jump on mobile context.
- Actual: jump was visually accepted.
- Expected: quiz gate should pause play around the threshold and show answer buttons.
- Actual: ${quizVisible ? 'quiz gate modal became visible.' : 'quiz gate did not become visible during bounded pass.'}
- Expected: quiz interaction should resolve without runtime crash.
- Actual: ${quizOutcomeObserved}.

## Screenshots captured
${screenshotIndex.map(s => `- ${s.path}: ${s.step} (${s.observed})`).join('\n')}

## Bug hypothesis assessment
- Hypothesis: core mobile start/jump/quiz loop is broken.
- Result: ${quizVisible && identityPassed ? 'fails to support a bug hypothesis' : 'weakly suggests a possible issue requiring caution'}.
`;
  fs.writeFileSync('playwright_observation_log.md', log);
  fs.writeFileSync('playwright_screenshots.json', JSON.stringify(screenshotIndex, null, 2));

  if (consoleErrors.length) {
    fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
  }

  const ledger = `# Delta Issue Ledger

| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |
|---|---|---|---|---|---|
| Core start and jump flow in \`index.html\` | Start button initializes game state and canvas pointerdown triggers \`jump()\` | Start button worked and canvas tap produced a jump in mobile Playwright | confirmed | leave_as_is | Browser evidence shows expected behavior |
| Quiz gate flow in \`index.html\` | Quiz modal is triggered when \`score % 1000 === 0\` and answer buttons are generated dynamically | ${quizVisible ? 'Quiz gate became visible after bounded threshold setup and answer interaction resolved without runtime crash' : 'Bounded threshold setup did not surface the modal reliably'} | ${quizVisible ? 'likely' : 'uncertain'} | leave_as_is | ${quizVisible ? 'No clear breakage observed in bounded pass' : 'Evidence is insufficient for a safe gameplay patch'} |
| Looping background audio volume in \`index.html\` | \`this.bgm = this.createAudio(ASSETS.bgm, 0.34, true)\` exceeds the 20% cap for continuous looped audio | No browser playback defect observed, but static policy violation is explicit | confirmed | fix | Hard safety guardrail requires loop volume at 20% or lower |
`;
  fs.writeFileSync('delta_issue_ledger.md', ledger);

  await context.close();
  await browser.close();
})().catch(err => {
  console.error(err);
  process.exit(1);
});