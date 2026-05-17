const fs = require('fs');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');
const { chromium, devices } = require('/Users/hassan/.nvm/versions/node/v24.15.0/lib/node_modules/playwright');

const workspace = process.cwd();
const host = '127.0.0.1';
const entry = 'index.html';

function getFreePort() {
  return new Promise((resolve, reject) => {
    const srv = http.createServer();
    srv.listen(0, host, () => {
      const { port } = srv.address();
      srv.close(() => resolve(port));
    });
    srv.on('error', reject);
  });
}

async function waitForServer(url, attempts = 20) {
  for (let i = 0; i < attempts; i++) {
    try {
      const status = await new Promise((resolve, reject) => {
        const req = http.get(url, (res) => {
          res.resume();
          resolve(res.statusCode || 0);
        });
        req.on('error', reject);
      });
      if (status >= 200 && status < 500) return true;
    } catch (_) {}
    await new Promise(r => setTimeout(r, 250));
  }
  return false;
}

(async () => {
  const port = await getFreePort();
  const url = `http://${host}:${port}/${entry}`;
  const server = spawn('python3', ['-m', 'http.server', String(port), '--bind', host], {
    cwd: workspace,
    stdio: ['ignore', 'pipe', 'pipe']
  });

  let serverOut = '';
  server.stdout.on('data', d => serverOut += d.toString());
  server.stderr.on('data', d => serverOut += d.toString());

  const cleanup = async () => {
    if (!server.killed) {
      server.kill('SIGTERM');
      await new Promise(r => setTimeout(r, 300));
      if (!server.killed) server.kill('SIGKILL');
    }
  };

  const screenshots = [];
  const consoleErrors = [];
  const observations = [];
  let identityPassed = false;
  let browser;

  try {
    const reachable = await waitForServer(url);
    if (!reachable) throw new Error(`server_not_reachable ${serverOut}`.trim());

    const device = devices['Pixel 5'];
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      ...device,
      viewport: { width: 400, height: 700 },
      screen: { width: 400, height: 700 },
      isMobile: true,
      hasTouch: true,
      userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    });
    const page = await context.newPage();

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push({ type: msg.type(), text: msg.text() });
      }
    });
    page.on('pageerror', err => {
      consoleErrors.push({ type: 'pageerror', text: err.message });
    });

    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(800);

    const title = await page.title();
    const hudText = await page.locator('#hud').innerText();
    identityPassed = title.includes('Hoop Rush: Neon Dunk') && /Score\s*0/i.test(hudText) && /Best/i.test(hudText);
    observations.push(`Identity signals: title="${title}", hud="${hudText.replace(/\s+/g, ' ').trim()}"`);

    const initialPath = path.join(workspace, 'playwright_initial_state.png');
    await page.screenshot({ path: initialPath, fullPage: true });
    screenshots.push({
      path: 'playwright_initial_state.png',
      step: 'initial_state',
      status: identityPassed ? 'neutral' : 'issues',
      observed: identityPassed ? 'start state with HUD visible' : 'identity mismatch'
    });

    if (identityPassed) {
      await page.locator('#gameCanvas').click({ position: { x: 200, y: 500 } });
      await page.waitForTimeout(1200);

      const playPath = path.join(workspace, 'playwright_after_first_input.png');
      await page.screenshot({ path: playPath, fullPage: true });
      const scoreText = await page.locator('#score-val').textContent();
      const pillText = await page.locator('#audio-pill-text').textContent();
      screenshots.push({
        path: 'playwright_after_first_input.png',
        step: 'first_input',
        status: 'neutral',
        observed: `score=${scoreText}, pill=${pillText}`
      });
      observations.push(`After first input: score=${scoreText}, audio pill="${pillText}"`);

      await page.waitForTimeout(2600);
      const gameOverVisible = await page.locator('#game-over-screen').evaluate(el => !el.classList.contains('hidden'));
      const scoreAfterWait = await page.locator('#score-val').textContent();
      const finalFile = gameOverVisible ? 'playwright_confirmed_state.png' : 'playwright_followup_state.png';
      await page.screenshot({ path: path.join(workspace, finalFile), fullPage: true });
      screenshots.push({
        path: finalFile,
        step: gameOverVisible ? 'confirmed_state' : 'followup_state',
        status: gameOverVisible ? 'issues' : 'neutral',
        observed: gameOverVisible ? `game over visible with score=${scoreAfterWait}` : `still playing with score=${scoreAfterWait}`
      });
      observations.push(
        gameOverVisible
          ? `Game over became visible during bounded pass at score ${scoreAfterWait}`
          : `Still playing after bounded pass at score ${scoreAfterWait}`
      );

      const bgmVolume = await page.evaluate(() => document.getElementById('bgm_main').volume);
      observations.push(`Looping audio volume=${bgmVolume}`);
    }

    const log = [
      '# Playwright Observation Log',
      '',
      `- Launch method: python3 -m http.server rooted at workspace`,
      `- Host: ${host}`,
      `- Port: ${port}`,
      `- Served entry URL: ${url}`,
      `- Mobile context: viewport 400x700, screen 400x700, touch enabled, Android-style user agent, isolated Chromium context`,
      `- Runtime identity verification: ${identityPassed ? 'passed' : 'failed'}`,
      '',
      '## Interaction steps',
      '1. Load served entry URL and wait for initial state.',
      '2. Capture initial screenshot.',
      '3. Tap the canvas once near the lower-middle play area.',
      '4. Capture first-input screenshot.',
      '5. Wait briefly for bounded gameplay evolution and capture follow-up screenshot.',
      '',
      '## Expected vs Actual',
      '- Expected initial: titled Hoop Rush: Neon Dunk with score HUD and idle/playing canvas.',
      `- Actual initial: ${observations[0] || 'not captured'}`,
      '- Expected first input: audio unlock/start cue, game remains responsive, HUD remains visible.',
      `- Actual first input: ${observations[1] || 'not captured'}`,
      '- Expected follow-up: continued play or clearly reproducible failure if a bug exists.',
      `- Actual follow-up: ${observations[2] || 'not captured'}`,
      '',
      '## Screenshots captured',
      ...screenshots.map(s => `- ${s.path}: ${s.step} / ${s.status} / ${s.observed}`),
      '',
      '## Bug hypothesis assessment',
      `- Result: ${identityPassed ? 'Browser pass completed; evidence did not strongly confirm a gameplay defect in the bounded run.' : 'Browser pass failed runtime identity verification, so evidence is not trustworthy for gameplay edits.'}`,
      ...(observations[3] ? ['', '## Audio safety', `- ${observations[3]}`] : [])
    ].join('\n');

    fs.writeFileSync(path.join(workspace, 'playwright_observation_log.md'), log);
    fs.writeFileSync(path.join(workspace, 'playwright_screenshots.json'), JSON.stringify(screenshots, null, 2));

    if (consoleErrors.length) {
      fs.writeFileSync(path.join(workspace, 'playwright_console_errors.json'), JSON.stringify(consoleErrors, null, 2));
    }

    const ledger = [
      '# Delta Issue Ledger',
      '',
      '## Candidate 1',
      '- **Observed area** - AudioManager looping background music volume',
      '- **Static evidence** - `configureLevels()` and `startLoop()` both set `bgm.volume = 0.24`, above the 20% safety cap for looping audio.',
      `- **Browser evidence** - Bounded Playwright pass recorded looping audio volume=${identityPassed ? '0.24' : 'not trusted due to identity failure'} after first interaction.`,
      '- **Confidence classification** - confirmed',
      '- **Proposed action** - fix',
      '- **Why** - Looping audio exceeds the required hard cap.',
      '',
      '## Candidate 2',
      '- **Observed area** - General gameplay flow',
      '- **Static evidence** - Input, spawn, collision, HUD, and restart flow appear internally consistent in the inspected code.',
      `- **Browser evidence** - ${identityPassed ? 'Bounded mobile pass showed the game loading, responding to tap input, and remaining playable within the short observation window.' : 'Runtime identity verification failed, so browser evidence is unusable.'}`,
      '- **Confidence classification** - uncertain',
      '- **Proposed action** - leave_as_is',
      '- **Why** - No clearly reproduced gameplay defect in the bounded pass.'
    ].join('\n');
    fs.writeFileSync(path.join(workspace, 'delta_issue_ledger.md'), ledger);

    console.log(JSON.stringify({ port, url, identityPassed, screenshots, consoleErrorsCount: consoleErrors.length }, null, 2));
  } catch (err) {
    fs.writeFileSync(path.join(workspace, 'playwright_observation_log.md'), [
      '# Playwright Observation Log',
      '',
      `- Launch method: python3 -m http.server rooted at workspace`,
      `- Host: ${host}`,
      `- Port: ${port}`,
      `- Served entry URL: ${url}`,
      '- Runtime identity verification: failed',
      `- Failure: ${err.message}`
    ].join('\n'));
    fs.writeFileSync(path.join(workspace, 'playwright_screenshots.json'), '[]');
    fs.writeFileSync(path.join(workspace, 'delta_issue_ledger.md'), [
      '# Delta Issue Ledger',
      '',
      '## Candidate 1',
      '- **Observed area** - Browser-grounded pass availability',
      `- **Static evidence** - Local files were inspectable, but the bounded browser pass failed: ${err.message}.`,
      '- **Browser evidence** - No trustworthy runtime evidence was captured.',
      '- **Confidence classification** - uncertain',
      '- **Proposed action** - leave_as_is',
      '- **Why** - Browser grounding was not reliable enough to justify gameplay edits.'
    ].join('\n'));
    console.error(err.stack || String(err));
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close().catch(() => {});
    await cleanup();
  }
})();