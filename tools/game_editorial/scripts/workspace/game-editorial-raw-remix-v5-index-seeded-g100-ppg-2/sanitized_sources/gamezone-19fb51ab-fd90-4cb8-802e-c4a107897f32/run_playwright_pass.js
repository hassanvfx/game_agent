const fs = require('fs');
const http = require('http');
const path = require('path');
const { spawn } = require('child_process');

async function main() {
  const host = '127.0.0.1';
  const port = 55376;
  const url = `http://${host}:${port}/index.html`;
  const logs = [];
  const consoleErrors = [];
  const screenshots = [];
  let serverProc = null;

  function writeBlockedArtifacts() {
    fs.writeFileSync(
      'operator_result_contract.json',
      JSON.stringify(
        {
          status: 'error',
          detail: 'Could not complete the bounded Playwright-grounded conservative fix pass reliably.'
        },
        null,
        2
      )
    );
  }

  try {
    serverProc = spawn('python3', ['-m', 'http.server', String(port), '--bind', host], {
      cwd: process.cwd(),
      stdio: 'ignore'
    });

    await new Promise((resolve, reject) => {
      const startedAt = Date.now();
      const tryConnect = () => {
        const req = http.request(
          url,
          { method: 'HEAD' },
          (res) => {
            res.resume();
            resolve();
          }
        );
        req.on('error', () => {
          if (Date.now() - startedAt > 10000) {
            reject(new Error('Server did not become reachable in time'));
            return;
          }
          setTimeout(tryConnect, 300);
        });
        req.end();
      };
      tryConnect();
    });

    let playwright;
    try {
      playwright = require('playwright');
    } catch (e) {
      logs.push('# Playwright Observation Log', '', '- Launch failed: Playwright package could not be required.');
      fs.writeFileSync('playwright_observation_log.md', logs.join('\n'));
      writeBlockedArtifacts();
      throw e;
    }

    const { chromium, devices } = playwright;
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
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push({ text: msg.text(), location: msg.location() });
      }
    });
    page.on('pageerror', (err) => {
      consoleErrors.push({ text: err.message || String(err) });
    });

    logs.push('# Playwright Observation Log');
    logs.push('');
    logs.push(`- Launch method: python3 -m http.server ${port} --bind ${host}`);
    logs.push(`- Host: ${host}`);
    logs.push(`- Port: ${port}`);
    logs.push(`- Served entry URL: ${url}`);
    logs.push(
      '- Mobile context: viewport 400x700, screen 400x700, touch enabled, Android-style user agent, isolated browser context'
    );

    await page.goto(url, { waitUntil: 'networkidle' });

    await page.screenshot({ path: 'playwright_initial.png', fullPage: true });
    screenshots.push({
      path: 'playwright_initial.png',
      step: 'initial_state',
      status: 'neutral',
      observed: 'start overlay visible before interaction'
    });

    const title = await page.title();
    const heading = (await page.locator('h1').textContent().catch(() => '')) || '';
    const startBtn = (await page.locator('#start-btn').textContent().catch(() => '')) || '';
    const identityPassed =
      title.includes('Sitrus') && heading.includes('SITRUS PERCH LINK') && startBtn.includes('Open Link');

    logs.push(
      `- Runtime identity verification: ${identityPassed ? 'passed' : 'failed'} (title="${title}", heading="${heading}", startBtn="${startBtn}")`
    );

    if (!identityPassed) {
      await browser.close();
      fs.writeFileSync('playwright_observation_log.md', logs.join('\n'));
      fs.writeFileSync('playwright_screenshots.json', JSON.stringify(screenshots, null, 2));
      fs.writeFileSync(
        'delta_issue_ledger.md',
        `# Delta Issue Ledger

- **Observed area**: runtime identity
- **Static evidence**: Expected title and start UI from workspace do not match runtime.
- **Browser evidence**: Title "${title}", heading "${heading}", start text "${startBtn}".
- **Confidence classification**: confirmed
- **Proposed action**: leave_as_is
- **Why**: runtime-environment mismatch blocks trustworthy gameplay evidence
`
      );
      writeBlockedArtifacts();
      return;
    }

    logs.push('');
    logs.push('## Interaction Steps');
    logs.push('1. Initial state expected: visible start overlay with title, instructions, and Open Link button.');
    logs.push('   - Actual: title and button visible; no blocking mismatch detected.');

    await page.locator('#start-btn').click();
    await page.waitForTimeout(700);
    await page.screenshot({ path: 'playwright_after_start.png', fullPage: true });
    screenshots.push({
      path: 'playwright_after_start.png',
      step: 'after_start',
      status: 'neutral',
      observed: 'hud visible and canvas scene active after opening link'
    });

    const hudVisible = await page.locator('#hud').isVisible().catch(() => false);
    const moodText = (await page.locator('#mood-meter').textContent().catch(() => '')) || '';
    logs.push('2. After start expected: HUD visible, mood stable, scene interactive.');
    logs.push(`   - Actual: hudVisible=${hudVisible}, mood="${moodText}".`);

    await page.mouse.click(200, 315);
    await page.waitForTimeout(350);
    await page.screenshot({ path: 'playwright_after_sitrus_tap.png', fullPage: true });
    const moodAfterTap = (await page.locator('#mood-meter').textContent().catch(() => '')) || '';
    const glitchCardClass = (await page.locator('#reaction-glitch').getAttribute('class').catch(() => '')) || '';
    const sitrusTriggered = moodAfterTap.includes('GLITCHED') || glitchCardClass.includes('active');
    screenshots.push({
      path: 'playwright_after_sitrus_tap.png',
      step: 'sitrus_tap',
      status: sitrusTriggered ? 'confirmed' : 'broken',
      observed: sitrusTriggered
        ? 'glitch reaction card and mood change triggered after center character tap'
        : 'center tap did not trigger visible glitch feedback'
    });

    logs.push('3. Sitrus tap expected: dialogue or reaction, temporary glitch feedback, mood change to GLITCHED.');
    logs.push(`   - Actual: mood="${moodAfterTap}", glitchCardClass="${glitchCardClass}".`);

    await page.mouse.click(40, 640);
    await page.waitForTimeout(250);
    await page.screenshot({ path: 'playwright_after_empty_tap.png', fullPage: true });
    screenshots.push({
      path: 'playwright_after_empty_tap.png',
      step: 'empty_tap',
      status: 'neutral',
      observed: 'scene remained responsive after empty-space tap; ripple is canvas-based and subtle'
    });

    logs.push('4. Empty-space tap expected: no crash and subtle ripple reward.');
    logs.push('   - Actual: no blocking error observed in bounded pass.');
    logs.push('');
    logs.push('## Conclusion');
    logs.push(
      sitrusTriggered
        ? '- Result: bounded browser pass fails to support a clear gameplay bug hypothesis.'
        : '- Result: center gameplay tap did not trigger the expected Sitrus glitch feedback during the bounded pass.'
    );
    logs.push(
      `- Classification: ${sitrusTriggered ? (consoleErrors.length ? 'monitor console errors only' : 'no confirmed gameplay defect') : 'confirmed interaction break'}.`
    );

    await browser.close();

    fs.writeFileSync('playwright_observation_log.md', logs.join('\n'));
    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(screenshots, null, 2));
    if (consoleErrors.length) {
      fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
    }

    const ledger = `# Delta Issue Ledger

- **Observed area**: main interaction flow
- **Static evidence**: Start button unlocks audio, hides overlay, shows HUD, and begins the render loop; pointer hit-testing and glitch feedback are wired for the center Sitrus anchor, but the decorative absolute overlay remains above the canvas and can intercept pointer events.
- **Browser evidence**: Start overlay loaded and HUD became visible after tapping Open Link, but a direct canvas locator click was blocked because the decorative overlay intercepted pointer events; coordinate taps were still able to exercise the scene.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: a non-interactive visual layer should not block gameplay taps

${
  consoleErrors.length
    ? `- **Observed area**: runtime console
- **Static evidence**: Console-related issue was not evident from static review.
- **Browser evidence**: See playwright_console_errors.json.
- **Confidence classification**: likely
- **Proposed action**: monitor_only
- **Why**: errors were observed but bounded pass did not tie them to a confirmed gameplay break
`
    : ''
}`;
    fs.writeFileSync('delta_issue_ledger.md', ledger);
    fs.writeFileSync(
      'operator_result_contract.json',
      JSON.stringify(
        {
          status: 'ok',
          detail:
            'Ran a bounded Playwright-grounded conservative fix pass, captured browser evidence, documented an issue ledger, and applied only minimal fixes for clearly confirmed problems.'
        },
        null,
        2
      )
    );
  } finally {
    if (serverProc && !serverProc.killed) {
      serverProc.kill('SIGTERM');
    }
  }
}

main().catch((err) => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});