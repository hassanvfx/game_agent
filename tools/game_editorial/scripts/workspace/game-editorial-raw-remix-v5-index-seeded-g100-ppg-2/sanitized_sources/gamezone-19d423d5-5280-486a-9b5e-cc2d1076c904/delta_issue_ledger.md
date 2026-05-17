# Delta Issue Ledger

| Observed area | Static evidence | Browser evidence | Confidence classification | Proposed action | Why |
| --- | --- | --- | --- | --- | --- |
| Looping background audio volume | AudioManager.init sets bgm volume to 0.35, above the 20% safety cap for looping audio | Browser pass not needed for this safety rule; source confirms continuous loop volume exceeds cap | confirmed | fix | Must comply with audio safety guardrail |
| Shop open interaction | handleGlobalInput checks e.target.id === 'shop-btn', which can miss taps on button descendants if markup changes; current bounded pass showed shopVisible=true | Screenshot/state after tapping Rig Bay: shopVisible=true | uncertain | leave_as_is | Observed working in browser pass |
