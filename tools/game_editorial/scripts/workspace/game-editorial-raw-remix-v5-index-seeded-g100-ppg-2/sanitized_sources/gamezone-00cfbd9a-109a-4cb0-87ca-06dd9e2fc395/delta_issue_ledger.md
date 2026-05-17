# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / audio loop safety
2. **Static evidence** - `configureAudio()` set `bgm_main` loop volume to `0.22`, above the required 20% cap for looping audio.
3. **Browser evidence** - The bounded mobile Playwright pass reached live runtime playback initialization paths after pressing **Start Scene**; this issue is governed by direct code inspection rather than a visual symptom.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - The policy requires looping background audio to stay at 20% volume or lower.

## Candidate 2
1. **Observed area** - `index.html` / first choice progression in the bounded interaction script
2. **Static evidence** - Story flow and `SCENE_GRAPH` indicate the first choice should appear after advancing from `start` to `meet_leo` to `leo_intro` to `choice_1`.
3. **Browser evidence** - In the short mobile pass, the first choice overlay was not reached within the scripted taps and the final screenshot shows no choice buttons.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - The pass may have stopped before enough dialogue-advance taps completed, so the evidence does not clearly prove a gameplay defect.

## Candidate 3
1. **Observed area** - remote media loading
2. **Static evidence** - The page references several remote image/audio/GIF assets.
3. **Browser evidence** - Four generic 404 console errors were observed during the bounded pass, but the captured UI still rendered and the exact missing resources were not isolated in this run.
4. **Confidence classification** - uncertain
5. **Proposed action** - monitor_only
6. **Why** - The current evidence is insufficient to justify replacing or rewriting media references conservatively.