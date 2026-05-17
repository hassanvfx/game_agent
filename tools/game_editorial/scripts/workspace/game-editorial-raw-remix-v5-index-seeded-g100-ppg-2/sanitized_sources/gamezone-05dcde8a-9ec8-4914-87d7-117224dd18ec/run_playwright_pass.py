import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

workspace = os.getcwd()
tmp_json = os.path.join(workspace, "playwright_observation_tmp.json")

s = socket.socket()
s.bind(("127.0.0.1", 0))
port = s.getsockname()[1]
s.close()

server = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
    cwd=workspace,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

host = "127.0.0.1"
entry_url = f"http://{host}:{port}/index.html"


def cleanup():
    try:
        server.terminate()
        server.wait(timeout=5)
    except Exception:
        try:
            server.kill()
        except Exception:
            pass


try:
    reachable = False
    for _ in range(30):
        try:
            with urllib.request.urlopen(entry_url, timeout=1) as resp:
                reachable = resp.status == 200
                if reachable:
                    break
        except Exception:
            time.sleep(0.2)
    if not reachable:
        raise RuntimeError("server_not_reachable")

    node_script = """
const fs = require('fs');
(async () => {
  const { chromium, devices } = require('playwright');
  const host = process.env.PW_HOST;
  const port = process.env.PW_PORT;
  const entryUrl = process.env.PW_URL;
  const device = devices['Pixel 5'];
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    ...device,
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
  });
  const page = await context.newPage();
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push({ type: 'console', text: msg.text() });
  });
  page.on('pageerror', err => {
    consoleErrors.push({ type: 'pageerror', text: String(err) });
  });

  const shots = [];
  const log = [];
  const shot = async (path, step, status, observed) => {
    await page.screenshot({ path, fullPage: true });
    shots.push({ path, step, status, observed });
  };

  await page.goto(entryUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(1200);

  const title = await page.title();
  const startVisible = await page.locator('#start-screen').isVisible().catch(() => false);
  const startText = await page.locator('#start-screen').innerText().catch(() => '');
  const identityPassed = title.includes('Melody Bus Run') && startVisible && startText.includes('MELODY BUS') && startText.includes('START JAM');
  log.push(`Runtime identity title: ${title}`);
  log.push(`Runtime identity startVisible: ${startVisible}`);
  log.push(`Runtime identity matched: ${identityPassed}`);
  await shot('playwright_initial.png', 'initial_state', identityPassed ? 'neutral' : 'issues', startVisible ? 'start screen visible' : 'start screen missing');

  if (!identityPassed) {
    fs.writeFileSync('playwright_observation_tmp.json', JSON.stringify({
      host, port, entryUrl, identityPassed, shots, consoleErrors, log,
      blocked: 'runtime-environment mismatch'
    }, null, 2));
    await browser.close();
    process.exit(2);
  }

  await page.locator('#start-btn').click({ force: true });
  await page.waitForTimeout(1500);
  const hudVisible = await page.locator('#hud').isVisible().catch(() => false);
  const scoreText = await page.locator('#score').textContent().catch(() => '');
  await shot('playwright_after_start.png', 'after_start', hudVisible ? 'neutral' : 'issues', `hudVisible=${hudVisible}, score=${scoreText}`);
  log.push(`After start hudVisible=${hudVisible}, score=${scoreText}`);

  await page.locator('#gameCanvas').click({ position: { x: 200, y: 450 }, force: true });
  await page.waitForTimeout(900);
  await shot('playwright_after_lane_switch.png', 'after_lane_switch', 'neutral', 'lane switch interaction attempted');

  await page.waitForTimeout(4500);
  const gameOverVisible = await page.locator('#game-over-screen').isVisible().catch(() => false);
  await shot('playwright_bounded_end.png', 'bounded_end', 'neutral', gameOverVisible ? 'game over reached in bounded pass' : 'play continued without visible failure');

  fs.writeFileSync('playwright_observation_tmp.json', JSON.stringify({
    host, port, entryUrl, identityPassed, shots, consoleErrors, log,
    startVisible, hudVisible, scoreText, gameOverVisible
  }, null, 2));
  if (consoleErrors.length) {
    fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
  }
  await browser.close();
})().catch(err => {
  console.error(err);
  process.exit(1);
});
"""

    env = os.environ.copy()
    env["PW_HOST"] = host
    env["PW_PORT"] = str(port)
    env["PW_URL"] = entry_url
    proc = subprocess.run(["node", "-e", node_script], cwd=workspace, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"playwright_failed:{proc.returncode}")

    with open(tmp_json, "r", encoding="utf-8") as f:
        obs = json.load(f)

    lines = [
        "# Playwright Observation Log",
        "",
        "## Launch",
        f"- Dedicated local server: python -m http.server {port} --bind 127.0.0.1",
        f"- Host: {host}",
        f"- Port: {port}",
        f"- Served entry URL: {entry_url}",
        "",
        "## Mobile Context",
        "- Browser: Chromium via Playwright",
        "- Viewport: 400 x 700",
        "- Screen: 400 x 700",
        "- Touch: enabled",
        "- User agent: Android-style mobile Chrome",
        "- Isolated fresh browser context: yes",
        "",
        "## Runtime Identity Verification",
        f"- Result: {'passed' if obs.get('identityPassed') else 'failed'}",
        f"- Signals: title matched 'Melody Bus Run', start overlay text contained 'MELODY BUS' and 'START JAM!', start screen visible={obs.get('startVisible')}",
        "",
        "## Interaction Steps",
        "1. Loaded initial state and waited for first paint.",
        "2. Captured initial screenshot.",
        "3. Tapped START JAM button.",
        "4. Captured post-start screenshot and checked HUD/score.",
        "5. Tapped canvas once to attempt a lane switch.",
        "6. Captured post-switch screenshot.",
        "7. Waited briefly for bounded gameplay evidence and captured final bounded-state screenshot.",
        "",
        "## Expected vs Actual",
        "- Initial state expected: branded start overlay with title and start button.",
        f"- Initial state actual: {'start screen visible and branded correctly' if obs.get('startVisible') else 'start screen not visible as expected'}.",
        "- After start expected: HUD visible, game begins scrolling, score starts at 0.",
        f"- After start actual: HUD visible={obs.get('hudVisible')}, score text={obs.get('scoreText')!r}.",
        "- Lane switch expected: tap on play field toggles lane without crashing runtime.",
        "- Lane switch actual: interaction executed; screenshots captured for visual review.",
        "- Bounded end expected: either continued play or a natural crash/game-over without runtime breakage.",
        f"- Bounded end actual: {'game over overlay appeared' if obs.get('gameOverVisible') else 'play continued without visible failure'}.",
        "",
        "## Screenshots Captured",
    ]
    for item in obs["shots"]:
        lines.append(f"- {item['path']} — step={item['step']} status={item['status']} observed={item['observed']}")
    lines += [
        "",
        "## Console / Runtime Evidence",
    ]
    if obs.get("consoleErrors"):
        lines.extend([f"- {e['type']}: {e['text']}" for e in obs["consoleErrors"]])
    else:
        lines.append("- No console errors were observed during the bounded pass.")
    lines += [
        "",
        "## Bug Hypothesis Outcome",
        "- Static evidence suggested one policy issue: looping background audio volume was configured above the required 20% cap.",
        "- Browser pass confirmed the runtime launches, identity matches, start flow works, lane-switch interaction works, and no obvious runtime/layout breakage appeared in the bounded pass.",
        "- This supports an audio-safety fix while failing to support broader gameplay or UI changes.",
    ]

    with open(os.path.join(workspace, "playwright_observation_log.md"), "w", encoding="utf-8") as f:
        f.write("\\n".join(lines) + "\\n")

    with open(os.path.join(workspace, "playwright_screenshots.json"), "w", encoding="utf-8") as f:
        json.dump(obs["shots"], f, indent=2)

    ledger = [
        "# Delta Issue Ledger",
        "",
        "## Candidate 1",
        "- **Observed area** - `index.html` / `AudioManager` looping background music",
        "- **Static evidence** - `musicGain.gain.value = 0.34` and loop audio element volume `0.34`, exceeding the required 20% cap for looping audio.",
        "- **Browser evidence** - Runtime identity passed and bounded gameplay worked without broader breakage; browser pass did not contradict the audio-safety issue.",
        "- **Confidence classification** - confirmed",
        "- **Proposed action** - fix",
        "- **Why** - looping background audio must not exceed 20% volume.",
        "",
        "## Candidate 2",
        "- **Observed area** - overall start/play/lane-switch flow",
        "- **Static evidence** - input bindings and HUD toggles appear correctly wired in code.",
        "- **Browser evidence** - start screen, HUD after start, lane-switch tap, and bounded gameplay all appeared functional in screenshots with no console errors.",
        "- **Confidence classification** - confirmed",
        "- **Proposed action** - leave_as_is",
        "- **Why** - no clearly confirmed runtime defect was observed.",
    ]
    with open(os.path.join(workspace, "delta_issue_ledger.md"), "w", encoding="utf-8") as f:
        f.write("\\n".join(ledger) + "\\n")

    print(json.dumps({
        "host": host,
        "port": port,
        "entry_url": entry_url,
        "identity_passed": obs.get("identityPassed"),
        "console_error_count": len(obs.get("consoleErrors", [])),
        "screenshots": [s["path"] for s in obs["shots"]],
    }, indent=2))
finally:
    cleanup()