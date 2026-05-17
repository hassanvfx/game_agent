# Delta Issue Ledger

## Candidate 1
1. **Observed area** - `index.html` audio preload and interaction sound setup
2. **Static evidence** - `sfx_notify` and `sfx_start` originally referenced remote audio files that returned 404
3. **Browser evidence** - initial bounded Playwright pass showed failed resource loads during runtime
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `fix`
6. **Why** - broken remote audio fetches were a real runtime defect and were fixable with a minimal URL substitution

## Candidate 2
1. **Observed area** - `index.html` flux toggle SVG markup
2. **Static evidence** - the SVG `xmlns` attribute originally pointed to `assets/www.w3.org/2000/svg.html` instead of the standard SVG namespace
3. **Browser evidence** - gameplay still loaded, but the malformed namespace was a clear invalid markup issue discovered during the evidence pass
4. **Confidence classification** - `likely`
5. **Proposed action** - `fix`
6. **Why** - the one-line correction was low risk and removed clearly incorrect markup

## Candidate 3
1. **Observed area** - start flow, snack scoring, and flux toggle on mobile
2. **Static evidence** - input handling, score updates, and flux mode state changes were internally consistent
3. **Browser evidence** - the bounded mobile pass successfully started the game, increased score to 10 on snack tap, and toggled flux mode
4. **Confidence classification** - `confirmed`
5. **Proposed action** - `leave_as_is`
6. **Why** - no gameplay defect was reproduced in the verified flow