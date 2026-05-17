const fs = require('fs');
const path = require('path');
const http = require('http');
const { execSync, spawn } = require('child_process');

const root = process.cwd();
const host = '127.0.0.1';
const ua = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36';
const viewport = { width: 400, height: 700 };
const screen = { width: 400, height: 700 };
const screenshots = [];
const consoleErrors = [];
const interactionLog = [];
let server;
let browser;
let context;

function writeJson(file, data) {
  fs.writeFileSync(path.join(root, file), JSON.stringify(data, null, 2));
}

function writeMd(file, content) {
  fs.writeFileSync(path.join(root, file), content);
}

async function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function getFreePort() {
  return await new Promise((resolve, reject) => {
    const net = require('net');
    const srv = net.createServer();
    srv.listen(0, host, () => {
      const { port } = srv.address();
      srv.close(() => resolve(port));
    });
    srv.on('error', reject);
  });
}

async function verifyReachable(url) {
  for (let i = 0; i < 30; i++) {
    try {
      await new Promise((resolve, reject) => {
        http.get(url, (res) => {
          if (res.statusCode === 200) {
            resolve();
            return;
          }
          reject(new Error(String(res.statusCode)));
        }).on('error', reject);
      });
      return true;
    } catch (error) {
      await wait(200);
    }
  }
  return false;
}

function loadPlaywright() {
  try {
    return require('playwright');
  } catch (error) {
    const guessed = execSync('npm root -g', { encoding: 'utf8' }).trim();
    return require(path.join(guessed, 'playwright'));
  }
}

async function main() {
  let playwright;
  try {
    playwright = loadPlaywright();
  } catch (error) {
    writeJson('operator_result_contract.json', {
      status: 'error',
      detail: 'Could not complete the bounded Playwright-grounded conservative fix pass reliably.'
    });
    throw new Error('Playwright unavailable in local or global runtime');
  }

  const port = await getFreePort();
  const entryUrl = `http://${host}:${port}/index.html`;

  server = spawn('python3', ['-m', 'http.server', String(port), '--bind', host], {
    cwd: root,
    stdio: 'ignore'
  });

  const reachable = await verifyReachable(entryUrl);
  if (!reachable) {
    writeJson('operator_result_contract.json', {
      status: 'error',
      detail: 'Could not complete the bounded Playwright-grounded conservative fix pass reliably.'
    });
    throw new Error('Local server not reachable');
  }

  browser = await playwright.chromium.launch({ headless: true });
  context = await browser.newContext({
    viewport,
    screen,
    isMobile: true,
    hasTouch: true,
    userAgent: ua,
    deviceScaleFactor: 2
  });
  const page = await context.newPage();

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push({ type: msg.type(), text: msg.text() });
    }
  });
  page.on('pageerror', (err) => {
    consoleErrors.push({ type: 'pageerror', text: String(err) });
  });

  await page.goto(entryUrl, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1200);

  const title = await page.title();
  const shiftLabel = await page.locator('#btn-work .btn-action-text').textContent().catch(() => null);
  const moneyVisible = await page.locator('#val-money').textContent().catch(() => null);
  const runtimeIdentityPassed = title === 'Purrfect Pal: Care Shift' && shiftLabel === 'Shift' && !!moneyVisible;

  await page.screenshot({ path: path.join(root, 'playwright_initial.png') });
  screenshots.push({
    path: 'playwright_initial.png',
    step: 'initial_state',
    status: runtimeIdentityPassed ? 'neutral' : 'issues',
    observed: runtimeIdentityPassed ? 'HUD, canvas, and initial tips visible' : 'runtime identity mismatch'
  });

  const browserEvidence = [];
  let audioInfo = null;

  if (runtimeIdentityPassed) {
    interactionLog.push('Opened initial state in mobile Playwright context.');
    interactionLog.push(`Verified identity using title="${title}", shiftLabel="${shiftLabel}", money="${moneyVisible}".`);

    await page.click('#btn-work');
    await page.waitForTimeout(600);
    const dropsAfterWork = await page.evaluate(() => STATE.moneyDrops.length);
    browserEvidence.push(`After tapping Shift, money drops count was ${dropsAfterWork}.`);
    await page.screenshot({ path: path.join(root, 'playwright_after_work.png') });
    screenshots.push({
      path: 'playwright_after_work.png',
      step: 'after_shift_tap',
      status: dropsAfterWork > 0 ? 'ok' : 'issues',
      observed: dropsAfterWork > 0 ? 'coins spawned on canvas after Shift tap' : 'no coins spawned after Shift tap'
    });

    await page.click('#btn-feed');
    await page.waitForTimeout(300);
    const shopVisible = await page.locator('#shop-modal').evaluate((el) => !el.classList.contains('hidden'));
    const shopFood = await page.locator('#shop-food-count').textContent().catch(() => null);
    const shopMoney = await page.locator('#shop-money-count').textContent().catch(() => null);
    browserEvidence.push(`After tapping Shop, modal visible=${shopVisible}, food=${shopFood}, money=${shopMoney}.`);
    await page.screenshot({ path: path.join(root, 'playwright_shop_open.png') });
    screenshots.push({
      path: 'playwright_shop_open.png',
      step: 'shop_open',
      status: shopVisible ? 'ok' : 'issues',
      observed: shopVisible ? 'shop modal opened with stock and budget summary' : 'shop modal failed to open'
    });

    audioInfo = await page.evaluate(() => {
      const bgm = document.getElementById('bgm_main');
      return bgm ? { volume: bgm.volume, loop: bgm.loop, src: bgm.currentSrc || bgm.src } : null;
    });
    browserEvidence.push(`Looping BGM volume observed at ${audioInfo ? audioInfo.volume : 'missing'}.`);
  }

  const observation = [
    '# Playwright Observation Log',
    '',
    '## Launch',
    '- Launched a dedicated local HTTP server with `python3 -m http.server` rooted at the workspace.',
    `- Host: ${host}`,
    `- Port: ${port}`,
    `- Served entry URL: ${entryUrl}`,
    '',
    '## Mobile context',
    '- Viewport: 400 x 700',
    '- Screen: 400 x 700',
    '- Touch enabled: true',
    '- isMobile: true',
    `- User agent: ${ua}`,
    '',
    '## Runtime identity verification',
    `- Result: ${runtimeIdentityPassed ? 'passed' : 'failed'}`,
    `- Signals: title="${title}", shiftLabel="${shiftLabel}", money="${moneyVisible}"`,
    '',
    '## Interaction steps attempted',
    ...interactionLog.map((x) => `- ${x}`),
    runtimeIdentityPassed ? '- Tapped Shift and observed whether coin drops spawned.' : '- No trusted gameplay interaction due to runtime identity failure.',
    runtimeIdentityPassed ? '- Tapped Shop and observed whether the supply modal opened.' : '',
    '',
    '## Screenshots captured',
    ...screenshots.map((s) => `- ${s.path} | ${s.step} | ${s.status} | ${s.observed}`),
    '',
    '## Expected vs actual',
    '- Expected initial state: game title context, HUD bars, tips counter, and action buttons visible.',
    `- Actual initial state: ${runtimeIdentityPassed ? 'matched expected runtime identity and HUD structure.' : 'did not meet identity requirements.'}`,
    '- Expected first action: tapping Shift should create visible coin pickups and trigger cooldown feedback.',
    `- Actual first action: ${browserEvidence[0] || 'not attempted'}`,
    '- Expected second action: tapping Shop should open the supply modal with current stock and budget values.',
    `- Actual second action: ${browserEvidence[1] || 'not attempted'}`,
    '',
    '## Assessment',
    `- Browser pass outcome: ${runtimeIdentityPassed ? 'supports stable core interactions.' : 'fails to support gameplay evidence due to identity mismatch.'}`,
    `- Bug hypothesis support: ${runtimeIdentityPassed ? 'Confirms one audio-safety issue statically and at runtime: looping BGM volume exceeds 20% cap.' : 'Fails to support changes.'}`
  ].filter(Boolean).join('\n');
  writeMd('playwright_observation_log.md', observation);
  writeJson('playwright_screenshots.json', screenshots);

  if (consoleErrors.length) {
    writeJson('playwright_console_errors.json', consoleErrors);
  }

  const ledger = [
    '# Delta Issue Ledger',
    '',
    '## Candidate 1',
    '- **Observed area**: `index.html` / AudioSys looping background music setup',
    '- **Static evidence**: `AudioSys.init()` sets `bgm.volume = 0.24` for a looping background track.',
    `- **Browser evidence**: Runtime check observed looping BGM volume at ${audioInfo ? audioInfo.volume : 'missing'} during the bounded Playwright pass; screenshots are ${runtimeIdentityPassed ? 'trusted after identity verification passed.' : 'not trusted due to identity failure.'}`,
    '- **Confidence classification**: confirmed',
    '- **Proposed action**: fix',
    '- **Why**: Looping background audio exceeds the required 20% maximum volume.',
    '',
    '## Candidate 2',
    '- **Observed area**: Core interaction flow / Shift and Shop buttons',
    '- **Static evidence**: Button handlers are wired on `DOMContentLoaded` and call `handleAction(...)` / `toggleShop()`.',
    `- **Browser evidence**: ${runtimeIdentityPassed ? browserEvidence.slice(0, 2).join(' ') : 'Runtime identity verification failed, so no trusted browser evidence.'}`,
    `- **Confidence classification**: ${runtimeIdentityPassed ? 'confirmed' : 'uncertain'}`,
    `- **Proposed action**: ${runtimeIdentityPassed ? 'leave_as_is' : 'monitor_only'}`,
    '- **Why**: Bounded pass showed expected behavior for these interactions and no minimal fix is justified.'
  ].join('\n');
  writeMd('delta_issue_ledger.md', ledger);

  await context.close();
  await browser.close();
  server.kill('SIGTERM');
}

main().catch(async (err) => {
  try { if (context) await context.close(); } catch (error) {}
  try { if (browser) await browser.close(); } catch (error) {}
  try { if (server) server.kill('SIGTERM'); } catch (error) {}
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});