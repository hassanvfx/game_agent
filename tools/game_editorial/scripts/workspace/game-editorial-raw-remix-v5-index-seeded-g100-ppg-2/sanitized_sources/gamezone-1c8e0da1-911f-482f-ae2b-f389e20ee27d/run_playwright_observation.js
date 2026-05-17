const fs = require('fs');
const path = require('path');
const http = require('http');
const { chromium, devices } = require('playwright');

const root = process.cwd();
const host = '127.0.0.1';

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = http.createServer();
    server.listen(0, host, () => {
      const address = server.address();
      const port = address && address.port;
      server.close(err => {
        if (err) reject(err);
        else resolve(port);
      });
    });
    server.on('error', reject);
  });
}

function startServer(port) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      const reqPath = decodeURIComponent((req.url || '/').split('?')[0]);
      let filePath = path.join(root, reqPath === '/' ? 'index.html' : reqPath.replace(/^\/+/, ''));
      if (!filePath.startsWith(root)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
      }
      fs.stat(filePath, (err, stats) => {
        if (!err && stats.isDirectory()) {
          filePath = path.join(filePath, 'index.html');
        }
        fs.readFile(filePath, (readErr, data) => {
          if (readErr) {
            res.writeHead(404);
            res.end('Not found');
            return;
          }
          const ext = path.extname(filePath).toLowerCase();
          const types = {
            '.html': 'text/html; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.json': 'application/json; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.mp3': 'audio/mpeg',
            '.ttf': 'font/ttf'
          };
          res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
          res.end(data);
        });
      });
    });
    server.listen(port, host, () => resolve(server));
    server.on('error', reject);
  });
}

async function verifyReachable(url) {
  return await new Promise(resolve => {
    const req = http.get(url, res => {
      resolve(res.statusCode === 200);
      res.resume();
    });
    req.on('error', () => resolve(false));
  });
}

(async () => {
  const port = await getFreePort();
  const server = await startServer(port);
  const entryUrl = `http://${host}:${port}/index.html`;
  const serverReachable = await verifyReachable(entryUrl);
  const screenshots = [];
  const consoleErrors = [];
  const steps = [];
  const mobileDevice = devices['Pixel 5'];

  let browser;
  let context;
  let page;
  let identityPassed = false;
  let runtimeIdentityDetail = '';
  let overall = 'fails_to_support_bug_hypothesis';

  function pushShot(file, step, status, observed) {
    screenshots.push({ path: file, step, status, observed });
  }

  try {
    if (!serverReachable) {
      throw new Error('Dedicated local server was not reachable.');
    }

    browser = await chromium.launch({ headless: true });
    context = await browser.newContext({
      ...mobileDevice,
      viewport: { width: 400, height: 700 },
      screen: { width: 400, height: 700 },
      isMobile: true,
      hasTouch: true,
      userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    });

    page = await context.newPage();
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push({ text: msg.text(), location: msg.location() });
      }
    });
    page.on('pageerror', err => {
      consoleErrors.push({ text: String(err) });
    });

    await page.goto(entryUrl, { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);

    const identity = await page.evaluate(() => ({
      title: document.title,
      scoreText: document.getElementById('score-display')?.textContent || '',
      difficultyText: document.getElementById('difficulty-display')?.textContent || '',
      restartLabel: document.getElementById('restart-btn')?.textContent || '',
      hasCanvas: !!document.getElementById('gameCanvas')
    }));

    identityPassed = identity.title === 'Neon Descent'
      && identity.scoreText.includes('DISTANCE')
      && identity.difficultyText.includes('ZONE')
      && identity.hasCanvas;

    runtimeIdentityDetail = JSON.stringify(identity);

    await page.screenshot({ path: path.join(root, 'playwright_initial.png') });
    pushShot('playwright_initial.png', 'initial_state', 'neutral', `identity=${identityPassed}; overlay hidden with active HUD`);

    steps.push({
      step: 'initial_state',
      expected: 'Game title identity and active HUD for a live survival run are visible.',
      actual: `Identity detail: ${runtimeIdentityDetail}`,
      classification: identityPassed ? 'supports_expected_runtime' : 'runtime_environment_mismatch'
    });

    if (!identityPassed) {
      overall = 'runtime_environment_mismatch';
      throw new Error('Runtime identity verification failed.');
    }

    await page.dispatchEvent('canvas', 'pointerdown', { clientX: 320, clientY: 620, pointerType: 'touch', isPrimary: true, button: 0 });
    await page.waitForTimeout(150);
    await page.dispatchEvent('canvas', 'pointermove', { clientX: 320, clientY: 620, pointerType: 'touch', isPrimary: true, buttons: 1 });
    await page.waitForTimeout(1500);

    const afterMove = await page.evaluate(() => {
      const chip = document.getElementById('status-chip');
      return {
        scoreText: document.getElementById('score-display')?.textContent || '',
        difficultyText: document.getElementById('difficulty-display')?.textContent || '',
        statusVisible: chip ? !chip.classList.contains('hidden') : false,
        statusText: document.getElementById('status-text')?.textContent || '',
        overlayVisible: !document.getElementById('game-over-screen')?.classList.contains('hidden')
      };
    });

    await page.screenshot({ path: path.join(root, 'playwright_after_move.png') });
    pushShot('playwright_after_move.png', 'after_first_action', 'neutral', `score=${afterMove.scoreText}; overlay=${afterMove.overlayVisible}; statusVisible=${afterMove.statusVisible}`);

    steps.push({
      step: 'after_first_action',
      expected: 'Touch input should keep the run active and permit horizontal repositioning without layout breakage.',
      actual: JSON.stringify(afterMove),
      classification: !afterMove.overlayVisible ? 'supports_expected_runtime' : 'suggests_problem'
    });

    await page.waitForTimeout(9000);

    const finalState = await page.evaluate(() => {
      const chip = document.getElementById('status-chip');
      const overlay = document.getElementById('game-over-screen');
      const bgm = document.getElementById('bgm_main');
      return {
        scoreText: document.getElementById('score-display')?.textContent || '',
        difficultyText: document.getElementById('difficulty-display')?.textContent || '',
        statusVisible: chip ? !chip.classList.contains('hidden') : false,
        gameOverVisible: overlay ? !overlay.classList.contains('hidden') : false,
        finalScore: document.getElementById('final-score')?.textContent || '',
        bgmVolume: bgm ? bgm.volume : null
      };
    });

    const finalShot = finalState.gameOverVisible ? 'playwright_broken_state.png' : 'playwright_followup.png';
    await page.screenshot({ path: path.join(root, finalShot) });
    pushShot(finalShot, finalState.gameOverVisible ? 'confirmed_broken_state' : 'followup_state', finalState.gameOverVisible ? 'issue' : 'neutral', JSON.stringify(finalState));

    steps.push({
      step: 'followup_state',
      expected: 'Short bounded mobile play should continue cleanly unless a confirmed gameplay fault appears.',
      actual: JSON.stringify(finalState),
      classification: finalState.gameOverVisible ? 'weakly_suggests_bug_hypothesis' : 'fails_to_support_bug_hypothesis'
    });

    overall = finalState.gameOverVisible ? 'weakly_suggests_bug_hypothesis' : 'fails_to_support_bug_hypothesis';

    const observationLog = [
      '# Playwright Observation Log',
      '',
      '## Launch',
      `- Dedicated local server rooted at workspace: \`${root}\``,
      `- Host: \`${host}\``,
      `- Port: \`${port}\``,
      `- Served entry URL: \`${entryUrl}\``,
      `- Reachability verified before browser pass: \`${serverReachable}\``,
      '',
      '## Mobile context settings',
      '- Browser: Chromium via Playwright',
      '- Device profile basis: `Pixel 5`',
      '- Viewport: `400 x 700`',
      '- Screen: `400 x 700`',
      '- Touch: enabled',
      '- Mobile: enabled',
      '- User agent: `Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36`',
      '',
      '## Runtime identity verification',
      `- Passed: \`${identityPassed}\``,
      `- Evidence: \`${runtimeIdentityDetail}\``,
      '',
      '## Interaction steps',
      ...steps.map(s => [
        `### ${s.step}`,
        `- Expected: ${s.expected}`,
        `- Actual: ${s.actual}`,
        `- Result: ${s.classification}`
      ].join('\n')),
      '',
      '## Screenshots captured',
      ...screenshots.map(s => `- \`${s.path}\` | step=\`${s.step}\` | status=\`${s.status}\` | observed=${s.observed}`),
      '',
      '## Outcome',
      `- Overall browser evidence classification: \`${overall}\``,
      `- Console/runtime errors observed: \`${consoleErrors.length}\``
    ].join('\n');

    fs.writeFileSync(path.join(root, 'playwright_observation_log.md'), observationLog);
    fs.writeFileSync(path.join(root, 'playwright_screenshots.json'), JSON.stringify(screenshots, null, 2));

    if (consoleErrors.length) {
      fs.writeFileSync(path.join(root, 'playwright_console_errors.json'), JSON.stringify(consoleErrors, null, 2));
    }
  } catch (error) {
    const observationLog = [
      '# Playwright Observation Log',
      '',
      '## Launch',
      `- Dedicated local server rooted at workspace: \`${root}\``,
      `- Host: \`${host}\``,
      `- Port: \`${port}\``,
      `- Served entry URL: \`${entryUrl}\``,
      `- Reachability verified before browser pass: \`${serverReachable}\``,
      '',
      '## Mobile context settings',
      '- Browser: Chromium via Playwright',
      '- Viewport: `400 x 700`',
      '- Screen: `400 x 700`',
      '- Touch: enabled',
      '- Mobile: enabled',
      '',
      '## Runtime identity verification',
      `- Passed: \`${identityPassed}\``,
      `- Evidence: \`${runtimeIdentityDetail}\``,
      '',
      '## Failure',
      `- Error: ${String(error)}`,
      '',
      '## Screenshots captured',
      ...screenshots.map(s => `- \`${s.path}\` | step=\`${s.step}\` | status=\`${s.status}\` | observed=${s.observed}`),
      '',
      `- Console/runtime errors observed: \`${consoleErrors.length}\``
    ].join('\n');
    fs.writeFileSync(path.join(root, 'playwright_observation_log.md'), observationLog);
    fs.writeFileSync(path.join(root, 'playwright_screenshots.json'), JSON.stringify(screenshots, null, 2));
    if (consoleErrors.length) {
      fs.writeFileSync(path.join(root, 'playwright_console_errors.json'), JSON.stringify(consoleErrors, null, 2));
    }
    throw error;
  } finally {
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
    await new Promise(resolve => server.close(resolve));
  }
})().catch(err => {
  console.error(String(err && err.stack || err));
  process.exit(1);
});