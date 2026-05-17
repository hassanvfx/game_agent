# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / `AudioManager.playBgm()` / looping background music volume
2. **Static evidence** - The looped `#bgm_main` track is played with `this.bgmNode.volume = 0.28`, which exceeds the required 20% maximum for continuous looping audio.
3. **Browser evidence** - The bounded mobile Playwright pass successfully launched the game and did not reveal other confirmed gameplay defects; audio volume compliance was not directly measurable from screenshots, so browser evidence is neutral rather than contradictory.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - The looped BGM volume violates the explicit audio safety cap and can be corrected with a one-line minimal patch.

## Candidate 2
1. **Observed area** - Gameplay flow / start screen / action buttons
2. **Static evidence** - `startGame()`, HUD toggling, spawning, and input handling are wired coherently in `index.html`.
3. **Browser evidence** - Runtime identity verification passed, the start screen rendered, starting the run showed the HUD, and a button tap did not produce immediate breakage.
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `leave_as_is`
6. **Why** - The bounded pass did not confirm a gameplay or layout defect that would justify further code edits.