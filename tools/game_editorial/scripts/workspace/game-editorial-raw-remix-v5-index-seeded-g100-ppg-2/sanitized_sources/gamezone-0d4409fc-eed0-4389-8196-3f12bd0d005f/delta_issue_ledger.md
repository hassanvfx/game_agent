# Delta Issue Ledger

1. **Observed area** - `index.html` start screen / joystick overlay interaction
   - **Static evidence** - `#joystick-zone` was present from first paint with `z-index: 50` and no `pointer-events: none`, even while hidden with `opacity-0`.
   - **Browser evidence** - Initial Playwright run could not click `#start-btn`; Playwright reported `#joystick-zone` / `.joystick-base` intercepting pointer events before gameplay began.
   - **Confidence classification** - confirmed
   - **Proposed action** - fix
   - **Why** - Hidden control overlay blocked the primary start action on mobile.

2. **Observed area** - `index.html` runtime asset loading
   - **Static evidence** - The page references remote assets, and the bounded pass logged three generic 404 resource failures without breaking the main flow.
   - **Browser evidence** - Post-fix Playwright pass completed the start, movement, and character switch flow successfully despite the logged 404 console errors.
   - **Confidence classification** - uncertain
   - **Proposed action** - monitor_only
   - **Why** - The exact missing resources were not isolated during the bounded pass and did not justify broader code edits.