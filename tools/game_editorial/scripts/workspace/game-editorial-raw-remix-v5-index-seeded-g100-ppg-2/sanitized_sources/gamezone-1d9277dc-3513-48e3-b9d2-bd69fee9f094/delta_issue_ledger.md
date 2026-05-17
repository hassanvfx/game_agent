# Delta Issue Ledger

## Candidate 1
- **Observed area**: `index.html` layout and initial gameplay input flow
- **Static evidence**: The page relied on Tailwind utility classes such as `h-full`, `absolute`, `hidden`, `flex`, and spacing helpers, while the Tailwind loader referenced a workspace-relative script path that does not resolve when the game is served from this workspace.
- **Browser evidence**: The first Playwright pass showed a `400 x 200` canvas and repeated pointer interception by the container/modal subtree; after adding local fallback layout rules, the re-run showed a `400 x 700` canvas, no blocking modal, and a bounded interaction pass that stayed playable.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: Missing utility styling directly broke mobile layout sizing and blocked touch play.

## Candidate 2
- **Observed area**: `index.html` external Tailwind script request
- **Static evidence**: The script source `../../../../../../../../../../../games_top_gameplays/assets/cdn.tailwindcss.com/3.4.17.js` is outside the served workspace root and returns 404 in the local observation pass.
- **Browser evidence**: Playwright recorded `Failed to load resource: the server responded with a status of 404 (File not found)`.
- **Confidence classification**: likely
- **Proposed action**: leave_as_is
- **Why**: The minimal fallback CSS already restores mechanics and layout, so removing the script was not required for the confirmed gameplay fix.

## Candidate 3
- **Observed area**: looped background music level
- **Static evidence**: `bgmEl.volume = 0.26;` exceeds the 20% cap for continuous looping audio.
- **Browser evidence**: Audio playback was not audibly inspected in the bounded headless pass, but the code path is explicit and always applies when music plays.
- **Confidence classification**: confirmed
- **Proposed action**: fix
- **Why**: The hard audio safety rule requires looping audio to stay at 20% volume or lower.