# Delta Issue Ledger

## Issue 1
- **Observed area**: `index.html` audio asset mapping for start and win one-shot SFX
- **Static evidence**: `ASSETS.sfx.start` and `ASSETS.sfx.win` referenced remote UI audio files that were configured in code but failed when exercised.
- **Browser evidence**: initial Playwright pass captured HTTP 404s for `https://gamezone-virid.vercel.app/assets/audios/ui/start_game_02.mp3` and `https://gamezone-virid.vercel.app/assets/audios/ui/level_complete_02.mp3`; follow-up checks also showed the `_01` variants were 404, while `menu_open_01.mp3` and `menu_close_01.mp3` returned 200 and final Playwright verification completed with zero errors.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: broken one-shot audio requests were directly observed in the browser and resolved with a minimal approved-URL swap.

## Issue 2
- **Observed area**: `index.html` looping background and victory audio volume
- **Static evidence**: `this.bgm.volume = 0.26` and `this.victoryLoop.volume = 0.3` exceeded the required 20% cap for looping audio.
- **Browser evidence**: Playwright runtime established the page/audio system was active and suitable for enforcing the audio safety guardrail; this issue was confirmed by source inspection against the stated rule.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: the node explicitly requires looped audio to be at or below 20%, so the over-cap values needed a minimal adjustment.

## Issue 3
- **Observed area**: opening gameplay flow / first-turn interaction
- **Static evidence**: move validation, blocked-turn handling, and automatic AI turn-switch logic were internally consistent for a non-six opening roll.
- **Browser evidence**: the bounded mobile pass showed `No launch vector` on a die roll of `3`, then safely advanced to the AI turn without layout breakage or runtime errors.
- **Confidence classification**: uncertain
- **Proposed action**: leave_as_is
- **Why**: the browser pass did not confirm a gameplay defect, so no mechanics patch was justified.