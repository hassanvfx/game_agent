# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / audio system / restart and death SFX sources
2. **Static evidence** - `#sfx_restart` points to `https://gamezone-virid.vercel.app/assets/audios/ui/start_game_01.mp3` and `#sfx_death` points to `https://gamezone-virid.vercel.app/assets/audios/ui/game_over_01.mp3`
3. **Browser evidence** - `playwright_console_errors.json` captured 404 load failures for both URLs during the bounded mobile pass; direct HEAD checks also returned `404`
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - Broken remote sources prevent two intended UI/gameplay sounds from loading

## Candidate 2
1. **Observed area** - `index.html` / audio system / looping background music volume
2. **Static evidence** - `AudioSys.init()` sets `this.bgm.volume = 0.22`
3. **Browser evidence** - `playwright_observation_log.md` recorded `bgmVolume: 0.22` during the mobile runtime
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - The looped background track exceeds the required 20% maximum volume cap

## Candidate 3
1. **Observed area** - `index.html` / mobile gameplay flow
2. **Static evidence** - Pointer handlers, HUD, canvas sizing, and state transitions are internally consistent in the inspected code
3. **Browser evidence** - The bounded mobile pass kept the run active, advanced score, showed status feedback, and did not reveal layout or interaction breakage in the captured screenshots
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `leave_as_is`
6. **Why** - The browser evidence failed to support any gameplay or layout bug beyond the confirmed audio issues