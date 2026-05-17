# Delta Issue Ledger

## Candidate 1
1. **Observed area** - shell audio volume in `index.html`
2. **Static evidence** - looping background audio is configured as `bgm.volume = 0.22`, which exceeds the required 20% cap for looping audio.
3. **Browser evidence** - browser pass confirmed the shell initializes and accepts a first tap that unlocks ambience, so this looping audio path is active in runtime.
4. **Confidence classification** - confirmed
5. **Proposed action** - fix
6. **Why** - mandatory audio safety guardrail requires looped background audio at 20% volume or lower.

## Candidate 2
1. **Observed area** - missing Construct runtime assets referenced by `index.html`
2. **Static evidence** - `jquery-2.1.1.min.js` and `c2runtime.js` are referenced but not present in the workspace listing.
3. **Browser evidence** - page shell still loads, but runtime-dependent gameplay could not be fully validated from available files.
4. **Confidence classification** - uncertain
5. **Proposed action** - leave_as_is
6. **Why** - absent runtime files are a workspace limitation and not safely patchable here.
