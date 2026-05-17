# Delta Issue Ledger

## Candidate 1
1. **Observed area** - looping background music volume
2. **Static evidence** - `sounds.bgm.volume = 0.22` is set in both `unlockAudio()` and `playSound('bgm')`
3. **Browser evidence** - bounded mobile run started the gameplay session that triggers looping BGM, validating that this configured loop path is active at runtime
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - looping audio exceeds the 20% safety cap

## Candidate 2
1. **Observed area** - start flow and primary pan interaction
2. **Static evidence** - start button calls `startGame()`; canvas listens for `pointerdown` and pan hit testing
3. **Browser evidence** - start overlay transitioned to gameplay HUD and bounded pan tap did not produce a confirmed break
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - bounded pass did not confirm a defect
