# Delta Issue Ledger

## Candidate 1
1. **Observed area** - Core gameplay flow / menu → level select → gameplay → pause
2. **Static evidence** - HTML and JS wire the relevant screens, canvas input, HUD, and pause modal consistently.
3. **Browser evidence** - Runtime identity passed; initial menu, Easy level select, gameplay entry, a correct placement, and pause modal all worked in the bounded mobile Playwright pass.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - No clear breakage was confirmed, so a conservative no-edit response for gameplay behavior was required.

## Candidate 2
1. **Observed area** - Looping background audio volume
2. **Static evidence** - `AudioManager` set `this.bgm.volume = 0.22`, above the required 20% cap for looping audio.
3. **Browser evidence** - The bounded browser pass established runtime identity and normal flow; the audio cap issue remained directly confirmed by deterministic source inspection.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - The looped BGM volume exceeded the hard safety cap by a small, isolated amount and was corrected with a one-line patch.
