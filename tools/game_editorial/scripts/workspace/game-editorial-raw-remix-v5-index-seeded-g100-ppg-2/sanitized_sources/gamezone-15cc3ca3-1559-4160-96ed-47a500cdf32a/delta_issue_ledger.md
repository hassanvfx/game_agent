# Delta Issue Ledger

## Candidate 1
1. **Observed area** - index.html / UI audio / start and game-over SFX
2. **Static evidence** - `sfx_start` and `sfx_gameover` were wired to remote *_02 UI audio URLs.
3. **Browser evidence** - Playwright recorded 404 responses for https://gamezone-virid.vercel.app/assets/audios/ui/start_game_02.mp3 and https://gamezone-virid.vercel.app/assets/audios/ui/game_over_02.mp3 during the bounded mobile pass.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - Replace broken approved remote URLs with approved alternates that resolve.

## Candidate 2
1. **Observed area** - gameplay interaction / mobile HUD and aim flow
2. **Static evidence** - touch canvas and HUD logic appear internally consistent; looped BGM volume is 0.16 which remains within the 20% cap.
3. **Browser evidence** - Runtime identity passed, HUD and dock appeared after start, and bounded touch interaction completed without gameplay-specific console exceptions.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - No clear defect was confirmed in the bounded pass.
