
const fs = require('fs');
const { chromium, devices } = require('playwright');

(async() => {
  const host = process.env.HOST_ADDR;
  const port = process.env.PORT_NUM;
  const url = process.env.TARGET_URL;
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    ...devices['Pixel 5'],
    viewport: { width: 400, height: 700 },
    screen: { width: 400, height: 700 },
    hasTouch: true,
    isMobile: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
  });
  const page = await context.newPage();
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push({ type: 'console', text: msg.text() });
  });
  page.on('pageerror', err => consoleErrors.push({ type: 'pageerror', text: String(err) }));

  const shots = [];
  await page.goto(url, { waitUntil: 'networkidle' });

  const title = await page.title();
  const menuText = await page.locator('#screen-menu').innerText();
  const runtimeIdentityPassed = title === 'Orbit Sudoku Grid' && /SUDOKU\s+ORBIT GRID/.test(menuText);

  await page.screenshot({ path: 'playwright_initial_state.png' });
  shots.push({ path: 'playwright_initial_state.png', step: 'initial_state', status: runtimeIdentityPassed ? 'neutral' : 'issues', observed: runtimeIdentityPassed ? 'start menu visible with Orbit Sudoku Grid identity' : 'runtime identity mismatch at start menu' });

  await page.locator('button:has-text("EASY (10)")').click();
  await page.waitForTimeout(300);
  const levelTitle = await page.locator('#level-title').innerText();
  await page.screenshot({ path: 'playwright_level_select.png' });
  shots.push({ path: 'playwright_level_select.png', step: 'level_select', status: /Easy Orbit/.test(levelTitle) ? 'neutral' : 'issues', observed: `level select visible with title "${levelTitle}"` });

  await page.locator('#level-grid button').first().click();
  await page.waitForTimeout(900);
  const state1 = await page.evaluate(() => ({
    timer: document.getElementById('timer')?.innerText || null,
    errors: document.getElementById('errors')?.innerText || null,
    appState: window.app?.state,
    screenGameHidden: document.getElementById('screen-game')?.classList.contains('hidden'),
    modalHidden: document.getElementById('modal-overlay')?.classList.contains('hidden'),
    gridRect: window.app?.gridRect,
    numpadRect: window.app?.numpadRect
  }));
  await page.screenshot({ path: 'playwright_gameplay_initial.png' });
  shots.push({ path: 'playwright_gameplay_initial.png', step: 'gameplay_initial', status: state1.appState === 'GAME' ? 'neutral' : 'issues', observed: `gameplay entered with state ${state1.appState}` });

  const interaction = await page.evaluate(() => {
    const puzzle = Array.isArray(window.app?.puzzle) ? window.app.puzzle : [];
    const solution = Array.isArray(window.app?.solution) ? window.app.solution : [];
    let target = null;
    for (let r = 0; r < 9 && !target; r++) {
      const prow = Array.isArray(puzzle[r]) ? puzzle[r] : [];
      const srow = Array.isArray(solution[r]) ? solution[r] : [];
      for (let c = 0; c < 9; c++) {
        if (prow[c] === 0 && typeof srow[c] === 'number') {
          target = { r, c, correct: srow[c] };
          break;
        }
      }
    }
    if (!target || !window.app?.gridRect || !window.app?.numpadRect) return { found: false };
    const gr = window.app.gridRect;
    const nr = window.app.numpadRect;
    return {
      found: true,
      target,
      cellTap: { x: gr.x + (target.c + 0.5) * gr.cw, y: gr.y + (target.r + 0.5) * gr.ch },
      numTap: { x: nr.x + ((target.correct - 1) + 0.5) * (nr.w / 9), y: nr.y + nr.h / 2 }
    };
  });

  let placementObserved = 'no editable cell found';
  let placementConfirmed = false;
  if (interaction.found) {
    await page.touchscreen.tap(interaction.cellTap.x, interaction.cellTap.y);
    await page.waitForTimeout(150);
    await page.touchscreen.tap(interaction.numTap.x, interaction.numTap.y);
    await page.waitForTimeout(350);
    const post = await page.evaluate(({r,c,correct}) => ({
      value: Array.isArray(window.app?.puzzle?.[r]) ? window.app.puzzle[r][c] : null,
      errors: window.app?.errors,
      appState: window.app?.state,
      expected: correct
    }), interaction.target);
    placementConfirmed = post.value === interaction.target.correct;
    placementObserved = `placed value ${post.value} at r${interaction.target.r}c${interaction.target.c}; expected=${interaction.target.correct}; errors=${post.errors}; state=${post.appState}`;
  }

  await page.screenshot({ path: 'playwright_after_first_action.png' });
  shots.push({ path: 'playwright_after_first_action.png', step: 'first_action_result', status: placementConfirmed ? 'neutral' : 'issues', observed: placementObserved });

  await page.locator('#screen-game button.hud-icon-btn').click();
  await page.waitForTimeout(250);
  const paused = await page.evaluate(() => ({
    modalHidden: document.getElementById('modal-overlay')?.classList.contains('hidden'),
    modalTitle: document.getElementById('modal-title')?.innerText,
    appState: window.app?.state
  }));
  await page.screenshot({ path: 'playwright_pause_modal.png' });
  shots.push({ path: 'playwright_pause_modal.png', step: 'pause_modal', status: (!paused.modalHidden && paused.appState === 'PAUSED') ? 'neutral' : 'issues', observed: `pause modal title="${paused.modalTitle}" state=${paused.appState}` });

  const result = {
    host, port, url,
    mobileContext: {
      deviceBase: 'Pixel 5',
      viewport: { width: 400, height: 700 },
      screen: { width: 400, height: 700 },
      hasTouch: true,
      isMobile: true,
      userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
    },
    runtimeIdentityPassed,
    title,
    menuText,
    levelTitle,
    gameplayState: state1,
    placementObserved,
    placementConfirmed,
    pauseState: paused,
    consoleErrors,
    shots
  };

  fs.writeFileSync('playwright_eval_result.json', JSON.stringify(result, null, 2));
  fs.writeFileSync('playwright_screenshots.json', JSON.stringify(shots, null, 2));
  if (consoleErrors.length) {
    fs.writeFileSync('playwright_console_errors.json', JSON.stringify(consoleErrors, null, 2));
  } else if (fs.existsSync('playwright_console_errors.json')) {
    fs.unlinkSync('playwright_console_errors.json');
  }
  await browser.close();
})();
