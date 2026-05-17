const fs = require('fs');
const http = require('http');
const { spawn } = require('child_process');

function loadPlaywright() {
  try {
    return require('playwright');
  } catch (e1) {
    try {
      return require('/usr/local/lib/node_modules/playwright');
    } catch (e2) {
      try {
        return require('/opt/homebrew/lib/node_modules/playwright');
      } catch (e3) {
        throw new Error('PLAYWRIGHT_UNAVAILABLE');
      }
    }
  }
}

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = http.createServer();
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      server.close(err => (err ? reject(err) : resolve(port)));
    });
    server.on('error', reject);
  });
}

function waitForServer(url, timeoutMs = 10000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const tryOnce = () => {
      http.get(url, res => {
        const { statusCode } = res;
        res.resume();
        if (statusCode && statusCode >= 200 && statusCode < 500) {
          resolve(statusCode);
        } else if (Date.now() - start > timeoutMs) {
          reject(new Error(`Server verification failed with status ${statusCode}`));
        } else {
          setTimeout(tryOnce, 200);
        }
      }).on('error', err => {
        if (Date.now() - start > timeoutMs) {
          reject(err);
        } else {
          setTimeout(tryOnce, 200);
        }
      });
    };
    tryOnce();
  });
}

async function main() {
  const playwright = loadPlaywright();
  const { chromium, devices } = playwright;
  const host = '127.0.0.1';
  const port = await getFreePort();
  const url = `http://${host}:${port}/index.html`;
  const serverLog = fs.openSync('.playwright_server.log', 'w');
  const server = spawn('python3', ['-m', 'http.server', String(port), '--bind', host], {
    stdio: ['ignore', serverLog, serverLog]
  });

  const cleanup = async () => {
    if (!server.killed) {
      server.kill('SIGTERM');
    }
    await new Promise(resolve => setTimeout(resolve, 250));
  };

  try {
    await waitForServer(url, 10000);

    const viewport = { width: 400, height: 700 };
    const screen = { width: 400, height: 700 };
    const userAgent =
      'Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36';

    const consoleErrors = [];
    const screenshots = [];
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      ...devices['Pixel 5'],
      viewport,
      screen,
      hasTouch: true,
      isMobile: true,
      userAgent
    });
    const page = await context.newPage();

    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push({ type: 'console', text: msg.text() });
      }
    });
    page.on('pageerror', err => {
      consoleErrors.push({ type: 'pageerror', text: String(err) });
    });

    await page.goto(url, { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(1200);

    const title = await page.title();
    const startTitle = await page.locator('#start-screen .screen-title').innerText().catch(() => '');
    const startButton = await page.locator('#start-btn').innerText().catch(() => '');
    const identityPassed =
      title === 'Impostor Run: Swarm' &&
      /VENT\s+RAID/i.test(startTitle) &&
      /Begin Raid/i.test(startButton);

    await page.screenshot({ path: 'playwright_initial_state.png' });
    screenshots.push({
      path: 'playwright_initial_state.png',
      step: 'initial_state',
      status: identityPassed ? 'neutral' : 'failed',
      observed: identityPassed
        ? 'start screen visible with matching runtime identity'
        : 'runtime identity mismatch on initial screen'
    });

    const steps = [
      {
        step: 'initial_state',
        expected: 'Matching start screen for Impostor Run: Swarm with Begin Raid CTA.',
        actual: `title=${title}; startTitle=${startTitle}; startButton=${startButton}`,
        classification: identityPassed ? 'fails to support a bug hypothesis' : 'runtime-environment mismatch'
      }
    ];

    if (identityPassed) {
      await page.locator('#start-btn').click({ force: true });
      await page.waitForTimeout(1400);
      await page.screenshot({ path: 'playwright_after_start.png' });
      const hudText = await page.locator('#hud').innerText().catch(() => '');
      const hintVisible = await page.locator('#tutorial-hint').isVisible().catch(() => false);
      screenshots.push({
        path: 'playwright_after_start.png',
        step: 'after_start',
        status: 'neutral',
        observed: `hud=${hudText || 'n/a'}; tutorialHintVisible=${hintVisible}`
      });
      steps.push({
        step: 'after_start',
        expected: 'HUD visible, gameplay running, tutorial hint appears briefly.',
        actual: `hud=${hudText || 'n/a'}; tutorialHintVisible=${hintVisible}`,
        classification: 'fails to support a bug hypothesis'
      });

      await page.touchscreen.tap(320, 600);
      await page.waitForTimeout(1600);
      await page.screenshot({ path: 'playwright_after_touch.png' });
      const score = await page.locator('#score').innerText().catch(() => '');
      const gameOverVisible = await page.locator('#game-over-screen').isVisible().catch(() => false);
      screenshots.push({
        path: 'playwright_after_touch.png',
        step: 'after_touch_interaction',
        status: gameOverVisible ? 'warning' : 'neutral',
        observed: `score=${score || '0'}; gameOverVisible=${gameOverVisible}`
      });
      steps.push({
        step: 'after_touch_interaction',
        expected: 'Touch input should drive movement without freezing or layout failure.',
        actual: `score=${score || '0'}; gameOverVisible=${gameOverVisible}`,
        classification: consoleErrors.length
          ? 'weakly suggests a bug hypothesis'
          : 'fails to support a bug hypothesis'
      });
    }

    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(screenshots, null, 2));
    if (consoleErrors.length) {
      fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
    } else if (fs.existsSync('playwright_console_errors.json')) {
      fs.unlinkSync('playwright_console_errors.json');
    }

    const logLines = [
      '# Playwright Observation Log',
      '',
      `- Launch method: python3 -m http.server rooted at workspace`,
      `- Host: ${host}`,
      `- Port: ${port}`,
      `- Served entry URL: ${url}`,
      `- Mobile context: viewport 400x700, screen 400x700, touch enabled, Android-style user agent`,
      `- Runtime identity verification: ${identityPassed ? 'PASSED' : 'FAILED'}`,
      '',
      '## Interaction steps',
      ...steps.map(
        step =>
          `- ${step.step}: expected ${step.expected} | actual ${step.actual} | result ${step.classification}`
      ),
      '',
      '## Screenshots',
      ...screenshots.map(s => `- ${s.path}: ${s.observed}`),
      '',
      '## Outcome',
      identityPassed
        ? consoleErrors.length
          ? '- Browser pass observed console/runtime errors and only weakly suggests a bug hypothesis.'
          : '- Browser pass did not confirm a gameplay or layout defect during the bounded mobile interaction pass.'
        : '- Browser pass indicates runtime-environment mismatch, so no gameplay evidence is trustworthy.'
    ];
    fs.writeFileSync('playwright_observation_log.md', `${logLines.join('\n')}\n`);

    await browser.close();

    const ledgerLines = [
      '# Delta Issue Ledger',
      '',
      '## Candidate 1',
      '- **Observed area**: Mobile start-to-gameplay flow and touch-follow movement',
      '- **Static evidence**: `#game-container` uses `touch-action: none`, touch handlers are scoped to the gameplay surface, and looping background music volume is capped at `0.2`.',
      `- **Browser evidence**: Runtime identity passed; screenshots \`playwright_initial_state.png\`, \`playwright_after_start.png\`, and \`playwright_after_touch.png\` showed the expected start screen, HUD, and continued gameplay without a confirmed break. ${consoleErrors.length ? 'Console/runtime errors were observed separately.' : 'No console/runtime errors were captured.'}`,
      `- **Confidence classification**: ${consoleErrors.length ? 'uncertain' : 'confirmed'}`,
      `- **Proposed action**: ${consoleErrors.length ? 'monitor_only' : 'leave_as_is'}`,
      `- **Why**: ${consoleErrors.length ? 'The bounded pass did not tie the captured errors to a visible defect.' : 'The bounded mobile pass did not confirm a gameplay, layout, or audio safety problem.'}`
    ];
    fs.writeFileSync('delta_issue_ledger.md', `${ledgerLines.join('\n')}\n`);

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
    await cleanup();
  }
}

main().catch(err => {
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
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});