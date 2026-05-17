# Playwright Observation Log

## Launch
- Local server rooted at workspace via `python3 -m http.server 55330 --bind 127.0.0.1`
- Host: `127.0.0.1`
- Port: `55330`
- Served entry URL: `http://127.0.0.1:55330/index.html`

## Mobile context
- Device basis: `Pixel 5`
- Viewport: `400 x 700`
- Screen: `400 x 700`
- Touch: enabled
- User agent: `Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36`

## Runtime identity verification
- Result: passed
- Evidence: title=Neon Courier 3D; startTitle=Neon Courier; startButton=Start Route

## Interaction steps
### identity_check
- Expected: Neon Courier 3D start screen from this workspace
- Actual: title=Neon Courier 3D; startTitle=Neon Courier; startButton=Start Route
- Result: passed

### start_game
- Expected: HUD visible and render loop active after start
- Actual: hudVisible=true, score=2
- Result: passed

### toggle_controls
- Expected: Quality and camera labels update after taps
- Actual: quality=Quality: LOW, cam=Cam: Top
- Result: passed

### mobile_layout
- Expected: Joystick visible in mobile context
- Actual: joystickVisible=true
- Result: passed

## Screenshots captured
- `playwright_initial.png` — initial_state — neutral — start card visible before play
- `playwright_after_start.png` — after_start — ok — hudVisible=true, score=2
- `playwright_toggles.png` — toggle_controls — ok — quality=Quality: LOW, cam=Cam: Top
- `playwright_mobile_ingame.png` — mobile_ingame — neutral — mobile HUD and joystick remain visible in-game

## Runtime evidence
- Console/runtime error count: 7
- Network failure count: 7
- Console/runtime: Failed to load resource: the server responded with a status of 404 ()
- Console/runtime: Failed to load resource: the server responded with a status of 404 ()
- Console/runtime: Failed to load resource: the server responded with a status of 404 ()
- Console/runtime: Failed to load resource: the server responded with a status of 404 ()
- Console/runtime: Failed to load resource: the server responded with a status of 404 ()
- Console/runtime: Failed to load resource: the server responded with a status of 404 ()
- Console/runtime: Failed to load resource: the server responded with a status of 404 ()
- Network failure: 404 https://gamezone-virid.vercel.app/assets/audios/ui/success_02.mp3
- Network failure: 404 https://gamezone-virid.vercel.app/assets/audios/music/music_loop_02.mp3
- Network failure: 404 https://gamezone-virid.vercel.app/assets/audios/ui/success_02.mp3
- Network failure: 404 https://gamezone-virid.vercel.app/assets/audios/ui/success_02.mp3
- Network failure: 404 https://gamezone-virid.vercel.app/assets/audios/ui/success_02.mp3
- Network failure: 404 https://gamezone-virid.vercel.app/assets/audios/ui/success_02.mp3
- Network failure: 404 https://gamezone-virid.vercel.app/assets/audios/ui/success_02.mp3

## Assessment
- Final bounded pass weakly suggests remaining external-media/network issues only; gameplay-blocking startup failure was addressed.
