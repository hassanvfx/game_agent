import http.server
import socket
import socketserver
import subprocess
import sys
import threading
import time
import os
from functools import partial
from pathlib import Path

root = Path('.').resolve()

with socket.socket() as s:
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]

handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
httpd = socketserver.TCPServer(('127.0.0.1', port), handler)
thread = threading.Thread(target=httpd.serve_forever, daemon=True)
thread.start()
time.sleep(0.5)

node_script = r"""
const fs = require('fs');
(async () => {
  const port = process.env.PW_PORT;
  const url = `http://127.0.0.1:${port}/index.html`;
  let playwright;
  try {
    playwright = require('playwright');
  } catch (e) {
    try {
      playwright = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
    } catch (e2) {
      console.error('PLAYWRIGHT_LOAD_FAILED');
      process.exit(42);
    }
  }

  const { chromium, devices } = playwright;
  const browser = await chromium.launch({ headless: true });
  const pixel = devices['Pixel 5'] || {};
  const context = await browser.newContext({
    ...pixel,
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36'
  });
  const page = await context.newPage();
  const consoleErrors = [];
  page.on('pageerror', err => consoleErrors.push({ type: 'pageerror', message: String(err) }));
  page.on('console', msg => {
    if (['error', 'warning'].includes(msg.type())) {
      consoleErrors.push({ type: msg.type(), message: msg.text() });
    }
  });

  const shots = [];
  const shot = async (name, step, status, observed) => {
    await page.screenshot({ path: name, fullPage: true });
    shots.push({ path: name, step, status, observed });
  };

  const expectedInitial = 'Title Neon Quota Rush, HUD with Shift/ROUTE QUOTA/Scans, SCAN button visible.';
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);

  const title = await page.title();
  const spinVisible = await page.locator('#spin-btn').isVisible().catch(() => false);
  const quotaText = await page.locator('#progress-text').textContent().catch(() => '');
  const identityPassed = title === 'Neon Quota Rush' && spinVisible && /\$0\s*\/\s*\$100/.test(quotaText || '');
  await shot('playwright_initial.png', 'initial_state', identityPassed ? 'neutral' : 'failed', `title=${title}; progress=${quotaText}; spinVisible=${spinVisible}`);

  if (!identityPassed) {
    fs.writeFileSync('playwright_screenshots.json', JSON.stringify(shots, null, 2));
    if (consoleErrors.length) fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
    fs.writeFileSync('playwright_observation_log.md', `# Playwright Observation Log

- Launch method: local static HTTP server from workspace root
- Host: 127.0.0.1
- Port: ${port}
- Served entry URL: ${url}
- Mobile context: viewport 400x700, screen 400x700, touch enabled, Android-style UA
- Runtime identity verification: failed

## Interaction steps
1. Open initial game state
   - Expected: ${expectedInitial}
   - Actual: title=${title}; progress=${quotaText}; spinVisible=${spinVisible}
   - Classification: fails to support bug hypothesis due to runtime-environment mismatch

## Screenshots captured
- playwright_initial.png

## Conclusion
- Browser pass result: runtime-environment mismatch; no gameplay edits justified.
`);
    fs.writeFileSync('delta_issue_ledger.md', `# Delta Issue Ledger

| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |
| --- | --- | --- | --- | --- | --- |
| Runtime identity / launch flow | index.html title and HUD expected Neon Quota Rush with quota text | Loaded runtime signals did not match expected identity strongly enough | uncertain | leave_as_is | Browser evidence not trustworthy for code edits |
`);
    await browser.close();
    process.exit(2);
  }

  await page.locator('#spin-btn').click();
  await page.waitForTimeout(2800);
  const scansText = await page.locator('#spins-display').textContent().catch(() => '');
  const buttonText = await page.locator('#spin-btn').textContent().catch(() => '');
  const moneyText = await page.locator('#money-display').textContent().catch(() => '');
  await shot('playwright_after_first_scan.png', 'after_first_scan', 'neutral', `scans=${scansText}; button=${buttonText}; money=${moneyText}`);

  await page.locator('#shop-btn').click();
  await page.waitForTimeout(300);
  const shopVisible = await page.locator('#shop-modal').isVisible().catch(() => false);
  await shot('playwright_shop_open.png', 'shop_open', shopVisible ? 'neutral' : 'failed', `shopVisible=${shopVisible}`);

  fs.writeFileSync('playwright_screenshots.json', JSON.stringify(shots, null, 2));
  if (consoleErrors.length) fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));

  fs.writeFileSync('playwright_observation_log.md', `# Playwright Observation Log

- Launch method: local static HTTP server from workspace root
- Host: 127.0.0.1
- Port: ${port}
- Served entry URL: ${url}
- Mobile context: viewport 400x700, screen 400x700, touch enabled, Android-style UA
- Runtime identity verification: passed

## Interaction steps
1. Open initial game state
   - Expected: ${expectedInitial}
   - Actual: title=${title}; progress=${quotaText}; spinVisible=${spinVisible}
   - Classification: confirms expected initial runtime identity
2. Tap SCAN once
   - Expected: one scan consumed, reel spin resolves, UI returns to idle state
   - Actual: scans=${scansText}; button=${buttonText}; money=${moneyText}
   - Classification: ${/9/.test(scansText || '') && /SCAN/.test(buttonText || '') ? 'confirms expected behavior' : 'weakly suggests a UI/input issue'}
3. Tap Rig Bay
   - Expected: shop modal becomes visible
   - Actual: shopVisible=${shopVisible}
   - Classification: ${shopVisible ? 'confirms expected behavior' : 'confirms bug hypothesis'}

## Screenshots captured
- playwright_initial.png
- playwright_after_first_scan.png
- playwright_shop_open.png

## Conclusion
- Browser pass result: ${shopVisible ? 'bounded pass did not confirm a gameplay/application bug' : 'bounded pass confirmed a shop interaction defect'}.
`);

  fs.writeFileSync('delta_issue_ledger.md', `# Delta Issue Ledger

| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |
| --- | --- | --- | --- | --- | --- |
| Looping background audio volume | AudioManager.init sets bgm volume to 0.35, above the 20% safety cap for looping audio | Browser pass not needed for this safety rule; source confirms continuous loop volume exceeds cap | confirmed | fix | Must comply with audio safety guardrail |
| Shop open interaction | handleGlobalInput checks e.target.id === 'shop-btn', which can miss taps on button descendants if markup changes; current bounded pass showed shopVisible=${shopVisible} | Screenshot/state after tapping Rig Bay: shopVisible=${shopVisible} | ${shopVisible ? 'uncertain' : 'confirmed'} | ${shopVisible ? 'leave_as_is' : 'fix'} | ${shopVisible ? 'Observed working in browser pass' : 'Interaction failed in browser pass'} |
`);

  await browser.close();
})();
"""

try:
    result = subprocess.run(
        ['node', '-e', node_script],
        env={**os.environ, 'PW_PORT': str(port)},
        capture_output=True,
        text=True
    )
    print(f"PORT={port}")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)
finally:
    httpd.shutdown()
    httpd.server_close()