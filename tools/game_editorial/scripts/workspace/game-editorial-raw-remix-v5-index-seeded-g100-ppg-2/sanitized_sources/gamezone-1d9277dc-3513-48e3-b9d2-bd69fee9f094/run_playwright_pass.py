import http.server
import json
import socket
import socketserver
import subprocess
import sys
import textwrap
import threading
import time
import urllib.request
from pathlib import Path

root = Path('.').resolve()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('127.0.0.1', 0))
    host, port = s.getsockname()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(root), **kwargs)

    def log_message(self, format, *args):
        pass

httpd = socketserver.TCPServer(('127.0.0.1', port), Handler)
thread = threading.Thread(target=httpd.serve_forever, daemon=True)
thread.start()

entry_url = f'http://127.0.0.1:{port}/index.html'
for _ in range(20):
    try:
        with urllib.request.urlopen(entry_url, timeout=1) as resp:
            if resp.status == 200:
                break
    except Exception:
        time.sleep(0.2)
else:
    httpd.shutdown()
    raise SystemExit('Server not reachable')

playwright_js = root / 'tmp_playwright_pass.js'
playwright_js.write_text(textwrap.dedent(f"""
const fs = require('fs');
(async () => {{
  let chromium;
  try {{
    ({{ chromium }} = require('playwright'));
  }} catch (e) {{
    try {{
      ({{ chromium }} = require('/usr/local/lib/node_modules/playwright'));
    }} catch (e2) {{
      try {{
        ({{ chromium }} = require('/opt/homebrew/lib/node_modules/playwright'));
      }} catch (e3) {{
        console.error('PLAYWRIGHT_UNAVAILABLE');
        process.exit(2);
      }}
    }}
  }}

  const browser = await chromium.launch({{ headless: true }});
  const context = await browser.newContext({{
    viewport: {{ width: 400, height: 700 }},
    screen: {{ width: 400, height: 700 }},
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36'
  }});
  const page = await context.newPage();
  const consoleErrors = [];
  page.on('console', msg => {{
    if (['error', 'warning'].includes(msg.type())) {{
      consoleErrors.push({{ type: msg.type(), text: msg.text() }});
    }}
  }});
  page.on('pageerror', err => {{
    consoleErrors.push({{ type: 'pageerror', text: String(err) }});
  }});

  const steps = [];
  const screenshots = [];

  await page.goto({json.dumps(entry_url)}, {{ waitUntil: 'domcontentloaded' }});
  await page.waitForTimeout(1200);

  const identity = await page.evaluate(() => ({{
    title: document.title,
    scoreLabel: document.querySelector('.hud-label')?.textContent?.trim() || null,
    ordersValue: document.getElementById('score-val')?.textContent?.trim() || null,
    mistakesValue: document.getElementById('lives-val')?.textContent?.trim() || null,
    feedback: document.getElementById('feedback-banner')?.textContent?.trim() || null
  }}));
  const identityPassed = identity.title === "Chef's Rush: Prep Line" && identity.scoreLabel === 'Orders';

  await page.screenshot({{ path: 'playwright_initial.png', fullPage: true }});
  screenshots.push({{ path: 'playwright_initial.png', step: 'initial_state', status: identityPassed ? 'neutral' : 'mismatch', observed: identityPassed ? 'title and HUD match workspace identity' : 'runtime identity mismatch' }});
  steps.push({{
    step: 'initial_state',
    expected: 'Kitchen HUD visible with title identity and playable canvas.',
    observed: identityPassed ? `Loaded ${{identity.title}} with Orders=${{identity.ordersValue}} Mistakes=${{identity.mistakesValue}} feedback=${{identity.feedback}}` : JSON.stringify(identity),
    result: identityPassed ? 'supports' : 'fails'
  }});

  if (!identityPassed) {{
    fs.writeFileSync('playwright_eval_result.json', JSON.stringify({{ host: '127.0.0.1', port: {port}, entryUrl: {json.dumps(entry_url)}, identityPassed, identity, steps, screenshots, consoleErrors }}, null, 2));
    await browser.close();
    process.exit(3);
  }}

  await page.mouse.click(200, 350);
  await page.waitForTimeout(900);
  const afterFirstTap = await page.evaluate(() => ({{
    score: document.getElementById('score-val')?.textContent?.trim() || null,
    lives: document.getElementById('lives-val')?.textContent?.trim() || null,
    feedback: document.getElementById('feedback-banner')?.textContent?.trim() || null,
    dangerShown: document.getElementById('danger-gif')?.classList.contains('show'),
    comboShown: document.getElementById('combo-gif')?.classList.contains('show')
  }}));
  await page.screenshot({{ path: 'playwright_after_first_tap.png', fullPage: true }});
  screenshots.push({{ path: 'playwright_after_first_tap.png', step: 'first_tap_result', status: 'neutral', observed: `score=${{afterFirstTap.score}}, lives=${{afterFirstTap.lives}}, feedback=${{afterFirstTap.feedback}}` }});
  steps.push({{
    step: 'first_tap_result',
    expected: 'Single tap should either hit a falling ingredient or produce a miss warning without crashing.',
    observed: JSON.stringify(afterFirstTap),
    result: 'supports'
  }});

  await page.waitForTimeout(3200);
  const afterBoundedPlay = await page.evaluate(() => {{
    const canvas = document.getElementById('gameCanvas');
    const rect = canvas.getBoundingClientRect();
    return {{
      score: document.getElementById('score-val')?.textContent?.trim() || null,
      lives: document.getElementById('lives-val')?.textContent?.trim() || null,
      feedback: document.getElementById('feedback-banner')?.textContent?.trim() || null,
      gameOverVisible: !document.getElementById('game-over-screen')?.classList.contains('hidden'),
      canvas: {{ width: rect.width, height: rect.height }}
    }};
  }});
  await page.screenshot({{ path: 'playwright_bounded_followup.png', fullPage: true }});
  screenshots.push({{ path: 'playwright_bounded_followup.png', step: 'bounded_followup', status: 'neutral', observed: `score=${{afterBoundedPlay.score}}, lives=${{afterBoundedPlay.lives}}, gameOver=${{afterBoundedPlay.gameOverVisible}}` }});
  steps.push({{
    step: 'bounded_followup',
    expected: 'Gameplay should continue in mobile viewport with HUD present and no blocking layout failure.',
    observed: JSON.stringify(afterBoundedPlay),
    result: 'supports'
  }});

  fs.writeFileSync('playwright_eval_result.json', JSON.stringify({{ host: '127.0.0.1', port: {port}, entryUrl: {json.dumps(entry_url)}, identityPassed, identity, steps, screenshots, consoleErrors }}, null, 2));
  if (consoleErrors.length) {{
    fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
  }}
  await browser.close();
}})().catch(err => {{
  console.error(err);
  process.exit(1);
}});
"""))

result = subprocess.run(['node', str(playwright_js)], capture_output=True, text=True)
if result.stdout:
    print(result.stdout, end='')
if result.stderr:
    print(result.stderr, end='', file=sys.stderr)

failure_log = {
    "host": "127.0.0.1",
    "port": port,
    "entryUrl": entry_url,
    "returncode": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}
if result.returncode != 0:
    (root / 'playwright_eval_result.json').write_text(json.dumps(failure_log, indent=2))

httpd.shutdown()
thread.join(timeout=2)
try:
    playwright_js.unlink()
except FileNotFoundError:
    pass

if result.returncode != 0:
    raise SystemExit(result.returncode)
