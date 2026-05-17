# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` audio asset configuration
2. **Static evidence** - The start and success SFX were mapped to catalog-listed `*_02` URLs that returned 404 during runtime; looped BGM volume was set to `0.23`, above the 20% cap.
3. **Browser evidence** - Initial Playwright pass logged repeated 404 responses for `https://gamezone-virid.vercel.app/assets/audios/ui/start_game_02.mp3` and `https://gamezone-virid.vercel.app/assets/audios/ui/success_02.mp3`. Post-fix pass showed no network failures.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - Broken approved audio URLs caused runtime fetch failures, and the looped music volume exceeded the node's audio safety guardrail.

## Candidate 2
1. **Observed area** - start / scan / decision mobile gameplay flow
2. **Static evidence** - Touch handlers are present for scan hold, and decision buttons remain single-tap actions.
3. **Browser evidence** - The mobile Playwright pass loaded the correct game, showed the start overlay, allowed scan hold with overlay opacity 1, and accepted a clear decision with score advancement.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - The bounded browser pass did not confirm a mechanics, layout, or input regression in this flow.
