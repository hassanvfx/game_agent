# Delta Issue Ledger

- **Observed area**: main interaction flow
- **Static evidence**: Start button unlocks audio, hides overlay, shows HUD, and begins the render loop; pointer hit-testing and glitch feedback are wired for the center Sitrus anchor, but the decorative absolute overlay remains above the canvas and can intercept pointer events.
- **Browser evidence**: Start overlay loaded and HUD became visible after tapping Open Link, but a direct canvas locator click was blocked because the decorative overlay intercepted pointer events; coordinate taps were still able to exercise the scene.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: a non-interactive visual layer should not block gameplay taps

- **Observed area**: runtime console
- **Static evidence**: Console-related issue was not evident from static review.
- **Browser evidence**: See playwright_console_errors.json.
- **Confidence classification**: likely
- **Proposed action**: monitor_only
- **Why**: errors were observed but bounded pass did not tie them to a confirmed gameplay break
