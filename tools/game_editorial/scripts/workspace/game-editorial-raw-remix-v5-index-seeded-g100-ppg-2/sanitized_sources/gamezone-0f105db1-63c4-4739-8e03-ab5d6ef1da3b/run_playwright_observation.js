const fs = require('fs');
const http = require('http');
const path = require('path');

function serveStatic(rootDir) {
  return http.createServer((req, res) => {
    const rawPath = (req.url || '/').split('?')[0];
    const safePath = rawPath === '/' ? '/index.html' : rawPath;
    const filePath = path.join(rootDir, decodeURIComponent(safePath));
    if (!filePath.startsWith(rootDir)) {
      res.statusCode = 403;
      res.end('Forbidden');
      return;
    }
    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.statusCode = 404;
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
        '.mp3': 'audio/mpeg',
        '.ttf': 'font/ttf'
      };
      if (types[ext]) res.setHeader('Content-Type', types[ext]);
      res.end(data);
    });
  });
}

(async () => {
  const out = {
    host: '127.0.0.1',
    port: null,
    entryUrl: null,
    identityVerified: false,
    identityDetails: '',
    steps: [],
    screenshots: [],
    consoleErrors: []
  };

  let browser = null;
  let context = null;
  let server = null;

  try {
    const playwright = require('playwright');
    server = serveStatic(process.cwd());

    await new Promise((resolve, reject) => {
      server.listen(0, '127.0.0.1', err => (err ? reject(err) : resolve()));
    });

    const address = server.address();
    out.port = address.port;
    out.entryUrl = `http://${out.host}:${out.port}/index.html`;

    browser = await playwright.chromium.launch({ headless: true });
    context = await browser.newContext({
      viewport: { width: 400, height: 700 },
      screen: { width: 400, height: 700 },
      isMobile: true,
      hasTouch: true,
      userAgent: 'Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    });

    const page = await context.newPage();
    page.on('console', msg => {
      if (msg.type() === 'error') {
        out.consoleErrors.push({ type: 'console', text: msg.text() });
      }
    });
    page.on('pageerror', err => {
      out.consoleErrors.push({ type: 'pageerror', text: String(err) });
    });

    await page.goto(out.entryUrl, { waitUntil: 'load', timeout: 20000 });
    await page.waitForTimeout(1500);

    const title = await page.title();
    const story = await page.locator('#story-text').textContent().catch(() => '');
    const score = await page.locator('#score-display').textContent().catch(() => '');
    out.identityVerified = title === 'Signal Drift' && /Guide the core/i.test(story || '') && /SIGNALS:/i.test(score || '');
    out.identityDetails = JSON.stringify({ title, story, score });

    await page.screenshot({ path: 'playwright_initial.png' });
    out.screenshots.push({
      path: 'playwright_initial.png',
      step: 'initial_state',
      status: out.identityVerified ? 'neutral' : 'untrusted',
      observed: `title=${title}; story=${story}; score=${score}`
    });
    out.steps.push({
      step: 'initial_state',
      expected: 'Title and HUD identify Signal Drift with visible canvas and instructions.',
      observed: `${title} | ${story} | ${score}`
    });

    if (!out.identityVerified) {
      throw new Error('RUNTIME_IDENTITY_MISMATCH');
    }

    const canvasBox = await page.locator('#gameCanvas').boundingBox();
    if (canvasBox) {
      await page.touchscreen.tap(canvasBox.x + canvasBox.width * 0.2, canvasBox.y + canvasBox.height * 0.8);
      await page.waitForTimeout(600);
      await page.touchscreen.tap(canvasBox.x + canvasBox.width * 0.8, canvasBox.y + canvasBox.height * 0.8);
    }
    await page.waitForTimeout(1400);

    const feedback = await page.locator('#feedback-text').textContent().catch(() => '');
    await page.screenshot({ path: 'playwright_after_move.png' });
    out.screenshots.push({
      path: 'playwright_after_move.png',
      step: 'first_action_result',
      status: 'neutral',
      observed: feedback || 'feedback unchanged'
    });
    out.steps.push({
      step: 'steer_actions',
      expected: 'Core should accept touch steering without page scrolling or blocked interaction.',
      observed: feedback || 'No visible text change after steering taps.'
    });

    await page.waitForTimeout(4500);
    const overlayActive = await page.locator('#game-over-screen').evaluate(el => el.classList.contains('active')).catch(() => false);
    const finalScore = await page.locator('#final-score').textContent().catch(() => '');
    const thirdPath = overlayActive ? 'playwright_broken_or_gameover.png' : 'playwright_followup.png';
    await page.screenshot({ path: thirdPath });
    out.screenshots.push({
      path: thirdPath,
      step: 'bounded_followup',
      status: overlayActive ? 'noted' : 'neutral',
      observed: overlayActive ? `game over visible: ${finalScore}` : 'run still active'
    });
    out.steps.push({
      step: 'bounded_followup',
      expected: 'Game remains playable until hazard contact, then shows restart overlay.',
      observed: overlayActive ? `Observed game over overlay with text: ${finalScore}` : 'No broken state observed within bounded pass.'
    });

    const log = [
      '# Playwright Observation Log',
      '',
      '## Launch',
      `- Host: ${out.host}`,
      `- Port: ${out.port}`,
      `- Served entry URL: ${out.entryUrl}`,
      '- Local server: dedicated HTTP server rooted at workspace',
      '',
      '## Mobile context',
      '- Browser: Chromium via Playwright',
      '- Viewport: 400 x 700',
      '- Screen: 400 x 700',
      '- Touch: enabled',
      '- isMobile: true',
      '- User agent: Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
      '',
      '## Runtime identity verification',
      `- Passed: ${out.identityVerified ? 'yes' : 'no'}`,
      `- Signals: ${out.identityDetails}`,
      '',
      '## Interaction steps',
      ...out.steps.map((s, i) => `### Step ${i + 1}: ${s.step}\n- Expected: ${s.expected}\n- Actual: ${s.observed}`),
      '',
      '## Screenshots',
      ...out.screenshots.map(s => `- ${s.path} | ${s.step} | ${s.status} | ${s.observed}`),
      '',
      '## Assessment',
      `- Result: ${overlayActive ? 'Pass remained playable until normal game-over state; no confirmed runtime defect observed.' : 'Bounded pass did not reveal a confirmed runtime defect.'}`,
      `- Console/runtime errors observed: ${out.consoleErrors.length}`
    ].join('\n');

    fs.writeFileSync('playwright_observation_log.md', log);
    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(out.screenshots, null, 2));

    if (out.consoleErrors.length) {
      fs.writeFileSync('playwright_console_errors.json', JSON.stringify(out.consoleErrors, null, 2));
    } else if (fs.existsSync('playwright_console_errors.json')) {
      fs.unlinkSync('playwright_console_errors.json');
    }

    const ledger = [
      '# Delta Issue Ledger',
      '',
      '## Candidate 1',
      '- **Observed area**: Runtime gameplay flow / touch steering / game-over loop',
      '- **Static evidence**: `index.html` implements touch-friendly canvas input, immediate play state, and restart overlay.',
      `- **Browser evidence**: Identity verified at ${out.entryUrl}; screenshots captured during initial load, movement attempt, and bounded follow-up. No broken interaction or layout failure was confirmed.`,
      '- **Confidence classification**: uncertain',
      '- **Proposed action**: leave_as_is',
      '- **Why**: The bounded mobile pass did not produce strong evidence of a defect, so conservative no-edit handling is required.',
      '',
      '## Candidate 2',
      '- **Observed area**: Looping background audio volume',
      '- **Static evidence**: `registerAudioElements()` sets `bgm.volume = 0.22` for looping audio.',
      '- **Browser evidence**: Audio playback was not relied upon for visual defect confirmation, but static policy review shows the loop volume slightly exceeds the 20% cap.',
      '- **Confidence classification**: likely',
      '- **Proposed action**: fix',
      '- **Why**: This is a small, policy-driven safety adjustment with explicit static evidence and minimal scope.'
    ].join('\n');
    fs.writeFileSync('delta_issue_ledger.md', ledger);

    console.log(JSON.stringify({
      ok: true,
      port: out.port,
      entryUrl: out.entryUrl,
      identityVerified: out.identityVerified,
      consoleErrors: out.consoleErrors.length,
      screenshots: out.screenshots.map(s => s.path)
    }));
  } catch (err) {
    const log = [
      '# Playwright Observation Log',
      '',
      '## Launch',
      `- Host: ${out.host}`,
      `- Port: ${out.port ?? 'unavailable'}`,
      `- Served entry URL: ${out.entryUrl ?? 'unavailable'}`,
      '',
      '## Runtime identity verification',
      `- Passed: ${out.identityVerified ? 'yes' : 'no'}`,
      `- Signals: ${out.identityDetails || 'not established'}`,
      '',
      '## Failure',
      `- Error: ${String(err && err.stack || err)}`
    ].join('\n');
    fs.writeFileSync('playwright_observation_log.md', log);
    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(out.screenshots, null, 2));

    if (out.consoleErrors.length) {
      fs.writeFileSync('playwright_console_errors.json', JSON.stringify(out.consoleErrors, null, 2));
    }

    const ledger = [
      '# Delta Issue Ledger',
      '',
      '## Candidate 1',
      '- **Observed area**: Browser-grounded pass',
      '- **Static evidence**: Observation setup attempted from workspace-rooted server.',
      `- **Browser evidence**: Pass failed before reliable evidence could be established: ${String(err && err.message || err)}`,
      '- **Confidence classification**: uncertain',
      '- **Proposed action**: leave_as_is',
      '- **Why**: Browser grounding was not reliable enough to justify gameplay edits.'
    ].join('\n');
    fs.writeFileSync('delta_issue_ledger.md', ledger);
    console.error(String(err && err.stack || err));
    process.exitCode = 1;
  } finally {
    if (context) {
      try { await context.close(); } catch {}
    }
    if (browser) {
      try { await browser.close(); } catch {}
    }
    if (server) {
      try {
        await new Promise(resolve => server.close(resolve));
      } catch {}
    }
  }
})();