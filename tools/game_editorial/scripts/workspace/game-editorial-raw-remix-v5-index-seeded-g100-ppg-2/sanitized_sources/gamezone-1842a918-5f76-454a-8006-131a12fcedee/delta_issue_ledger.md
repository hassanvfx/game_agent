# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` / audio safety / looping background music
2. **Static evidence** - The `bgm` audio element volume was initialized to `0.28`, which exceeds the node's hard cap for looping or long-running audio.
3. **Browser evidence** - The bounded Playwright pass successfully entered gameplay, confirming the looping track is part of the active runtime path after start.
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - The audio safety guardrail explicitly requires looping audio to be `20%` volume or lower.

## Candidate 2
1. **Observed area** - `index.html` / canvas rendering
2. **Static evidence** - Multiple canvas gradient calls exist in the render path, but the bounded pass did not capture a reliable stack frame to isolate which inputs became non-finite.
3. **Browser evidence** - Playwright recorded `TypeError: Failed to execute 'createLinearGradient' on 'CanvasRenderingContext2D': The provided double value is non-finite.`
4. **Confidence classification** - `likely`
5. **Proposed action** - `monitor_only`
6. **Why** - Runtime evidence suggests a rendering defect, but the localization evidence was not strong enough for a minimal conservative patch in this node.

## Candidate 3
1. **Observed area** - remote media/font/resource loading
2. **Static evidence** - The page depends on several remote resources for fonts, audio, and GIF feedback.
3. **Browser evidence** - Playwright recorded three `404` resource failures, but the failing URLs were not identified during the bounded pass.
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `leave_as_is`
6. **Why** - The evidence is insufficient to determine which resource failed and whether a safe replacement is justified within this conservative pass.

## Candidate 4
1. **Observed area** - start/jump mobile interaction flow
2. **Static evidence** - Canvas pointer input and explicit start/restart button click handlers are present in source.
3. **Browser evidence** - Start worked in mobile Playwright, while a single bounded gameplay tap did not confirm a missed jump or dead interaction.
4. **Confidence classification** - `uncertain`
5. **Proposed action** - `leave_as_is`
6. **Why** - The bounded pass did not produce strong evidence of a gameplay interaction defect.