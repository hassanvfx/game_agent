# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / audio manager / looping background music
2. **Static evidence** - `AudioManager.preload()` set `bgm` to `audio.volume = 0.3` while also enabling `audio.loop = true`
3. **Browser evidence** - bounded Playwright pass showed the game loads, starts, and remains responsive; this issue is policy-confirmed by code inspection rather than visual breakage
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - looping audio must not exceed 20% volume

## Candidate 2
1. **Observed area** - start flow, HUD visibility, first shot interaction
2. **Static evidence** - start button hides the start screen, shows the HUD, initializes the game, and input handlers are wired for play
3. **Browser evidence** - `playwright_initial.png`, `playwright_after_start.png`, and `playwright_after_shot.png` showed correct runtime identity and a responsive bounded play flow
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `leave_as_is`
6. **Why** - no confirmed breakage was observed in the bounded pass
