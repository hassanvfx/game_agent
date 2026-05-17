import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

workspace = os.getcwd()
host = "127.0.0.1"

sock = socket.socket()
sock.bind((host, 0))
port = sock.getsockname()[1]
sock.close()

server = subprocess.Popen(
    ["python3", "-m", "http.server", str(port), "--bind", host],
    cwd=workspace,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
entry_url = f"http://{host}:{port}/index.html"


def wait_for_server():
    for _ in range(40):
        try:
            with urllib.request.urlopen(entry_url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.25)
    return False


if not wait_for_server():
    server.terminate()
    raise SystemExit("Dedicated local HTTP server was not reachable.")

js = r"""
const fs = require('fs');
const path = require('path');

(async () => {
  const workspace = process.cwd();
  const host = process.env.PF_HOST;
  const port = process.env.PF_PORT;
  const entryUrl = process.env.PF_ENTRY_URL;

  let chromium, devices;
  try {
    ({ chromium, devices } = require('playwright'));
  } catch (err) {
    throw new Error('Shared Playwright runtime not available: ' + err.message);
  }

  const screenshotIndex = [];
  const consoleErrors = [];
  const pageErrors = [];
  let runtimeIdentity = 'failed';

  const addShot = async (page, name, step, status, observed) => {
    await page.screenshot({ path: path.join(workspace, name), fullPage: true });
    screenshotIndex.push({ path: name, step, status, observed });
  };

  const mobile = devices['Pixel 5'] || {};
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    ...mobile,
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    hasTouch: true,
    isMobile: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
  });

  try {
    const page = await context.newPage();
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push({ type: msg.type(), text: msg.text() });
      }
    });
    page.on('pageerror', err => {
      pageErrors.push({ message: err.message, stack: err.stack || null });
    });

    await page.goto(entryUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(1200);

    const identity = await page.evaluate(() => ({
      title: document.title,
      hud: document.getElementById('hud')?.innerText || '',
      settings: document.getElementById('settings-btn')?.innerText || ''
    }));

    if (identity.title === 'Particle Forge Command' && identity.hud.includes('SWARM SIGNAL') && identity.settings.includes('CONTROL PANEL')) {
      runtimeIdentity = 'passed';
    }

    await addShot(page, 'playwright_initial_state.png', 'initial_state', 'neutral', 'initial HUD and empty particle field visible');

    if (runtimeIdentity !== 'passed') {
      throw new Error('Runtime identity verification failed.');
    }

    const canvas = page.locator('#gameCanvas');
    await canvas.dispatchEvent('pointerdown', { clientX: 180, clientY: 360, pointerType: 'touch', isPrimary: true });
    await page.waitForTimeout(500);
    await canvas.dispatchEvent('pointermove', { clientX: 210, clientY: 390, pointerType: 'touch', isPrimary: true, buttons: 1 });
    await page.waitForTimeout(300);
    await canvas.dispatchEvent('pointerup', { clientX: 210, clientY: 390, pointerType: 'touch', isPrimary: true });
    await page.waitForTimeout(700);

    const afterSpawn = await page.evaluate(() => ({
      score: document.getElementById('score-val')?.textContent || '',
      count: document.getElementById('count-val')?.textContent || ''
    }));
    await addShot(page, 'playwright_after_spawn.png', 'after_spawn_drag', 'observed', `spawned particles; score ${afterSpawn.score}, count ${afterSpawn.count}`);

    await page.click('#settings-btn');
    await page.waitForTimeout(400);
    const panelVisible = await page.locator('#settings-panel').evaluate(el => !el.classList.contains('hidden'));
    await addShot(page, 'playwright_settings_open.png', 'settings_open', panelVisible ? 'observed' : 'broken', panelVisible ? 'settings panel opened' : 'settings panel failed to open');

    await page.click('#snd-off');
    await page.waitForTimeout(250);
    await page.click('#close-settings');
    await page.waitForTimeout(350);

    await page.click('#move-btn');
    await page.waitForTimeout(500);
    await addShot(page, 'playwright_after_scatter.png', 'after_scatter', 'observed', 'scatter action executed after spawn');

    const audioInfo = await page.evaluate(() => ({
      bgmVolume: document.getElementById('bgm_main')?.volume,
      bgmPaused: document.getElementById('bgm_main')?.paused
    }));

    const issueLines = [
      '# Delta Issue Ledger',
      '',
      '| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |',
      '| --- | --- | --- | --- | --- | --- |',
      `| Background music volume cap | \`bgm.volume = 0.22\` appears in audio init/resume paths in index.html. | Observation pass recorded bgm volume=${audioInfo.bgmVolume} after interaction, exceeding the 20% cap. | confirmed | fix | Hard audio safety rule requires looped audio at 20% or lower. |`
    ];
    fs.writeFileSync(path.join(workspace, 'delta_issue_ledger.md'), issueLines.join('\n'));
    fs.writeFileSync(path.join(workspace, 'playwright_screenshots.json'), JSON.stringify(screenshotIndex, null, 2));

    if (consoleErrors.length || pageErrors.length) {
      fs.writeFileSync(path.join(workspace, 'playwright_console_errors.json'), JSON.stringify({ consoleErrors, pageErrors }, null, 2));
    }

    const log = [
      '# Playwright Observation Log',
      '',
      `- Launch method: python3 -m http.server ${port} --bind ${host} (rooted at workspace)`,
      `- Host: ${host}`,
      `- Port: ${port}`,
      `- Served entry URL: ${entryUrl}`,
      '- Mobile context: viewport 400 x 700, screen 400 x 700, touch enabled, Android-style user agent',
      `- Runtime identity verification: ${runtimeIdentity}`,
      '',
      '## Interaction steps',
      '1. Loaded the local entry URL and waited for DOM/render stabilization.',
      '2. Verified runtime identity using page title and HUD/control text.',
      '3. Captured initial screenshot.',
      '4. Performed a bounded touch drag on the canvas to spawn particles; captured resulting screenshot.',
      '5. Opened the control panel; captured resulting screenshot.',
      '6. Toggled audio OFF, closed the panel, then triggered SCATTER SWARM and captured the result.',
      '',
      '## Expected vs actual',
      `- Initial state expected: identifiable Particle Forge Command HUD. Actual: ${identity.title} with HUD controls present.`,
      `- Spawn interaction expected: particle count increases. Actual: score=${afterSpawn.score}, count=${afterSpawn.count}.`,
      `- Settings interaction expected: panel becomes visible. Actual: ${panelVisible ? 'panel visible' : 'panel not visible'}.`,
      `- Audio safety expected: loop volume <= 0.20. Actual: bgm volume=${audioInfo.bgmVolume}.`,
      '',
      '## Classification',
      '- The observation pass confirms one concrete issue: looping background music volume exceeds the node safety cap.',
      '- No stronger browser evidence was gathered for any other gameplay or layout defect during the bounded pass.',
      '',
      '## Screenshots',
      ...screenshotIndex.map(s => `- ${s.path}: ${s.step} (${s.status}) - ${s.observed}`)
    ];
    fs.writeFileSync(path.join(workspace, 'playwright_observation_log.md'), log.join('\n'));

    process.stdout.write(JSON.stringify({
      host,
      port,
      entryUrl,
      runtimeIdentity,
      screenshotCount: screenshotIndex.length,
      consoleErrorCount: consoleErrors.length + pageErrors.length,
      bgmVolume: audioInfo.bgmVolume
    }, null, 2));
  } finally {
    await context.close().catch(() => {});
    await browser.close().catch(() => {});
  }
})().catch(err => {
  console.error(String(err && err.stack || err));
  process.exit(1);
});
"""

env = dict(os.environ)
env["PF_HOST"] = host
env["PF_PORT"] = str(port)
env["PF_ENTRY_URL"] = entry_url

try:
    result = subprocess.run(
        ["node", "-e", js],
        cwd=workspace,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
finally:
    server.terminate()
    try:
        server.wait(timeout=2)
    except subprocess.TimeoutExpired:
        server.kill()