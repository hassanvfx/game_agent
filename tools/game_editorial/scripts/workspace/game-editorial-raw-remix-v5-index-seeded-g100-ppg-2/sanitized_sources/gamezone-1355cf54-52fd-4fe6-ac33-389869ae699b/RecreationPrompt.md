Create a polished single-screen HTML5 arcade game called **Zero Contact**. The entire experience should center on surviving for as long as possible in a dark futuristic neon arena. The player controls a luminous cyan energy core that starts near the center of the screen, and hostile red breach shapes spawn from random edges of the screen and travel inward. The rule is immediate and simple: **do not let anything touch the core**.

Use a full-screen canvas for gameplay and overlay minimal DOM-based UI panels for the menu, HUD, mute toggle, and game-over state. On desktop, the player should move the core by moving or dragging the mouse; on mobile, touch and drag should do the same. Do not make movement instantaneous—have the core **smoothly drift toward the current pointer/touch position** so the controls feel slightly inertial and evasive. This movement feel is important because much of the tension should come from steering under pressure rather than snapping precisely.

The main gameplay loop should be:
1. Start from a stylish title screen with a short instruction like “Drag to drift. Keep the radiant core clear of every red breach.”
2. Begin a run in a calm but threatening arena.
3. Continuously spawn hostile enemies from the top, bottom, left, and right edges.
4. Increase difficulty over time by making enemies spawn more frequently and move faster.
5. Award score purely based on survival time.
6. End the run instantly on collision.
7. Show a game-over screen with the final survival score and a replay button for immediate restart.

Presentation should feel clean, premium, and cyber-arcade. Use deep navy and near-black gradients for the background, along with subtle glowing grid lines, scanline texture, and small star-like specks to give the arena a digital void feel. The player core should be rendered as a bright cyan-white orb with purple accents, layered glow, and a fading motion trail. Enemies should look dangerous and readable—abstract red pulsing geometric organisms or breach shards with inner glow. Add a small explosion or particle burst when the player dies.

Include a compact HUD that displays survival time near the top of the screen. Add a mute button in a corner. Support short feedback events: when an enemy gets dangerously close, briefly trigger a warning sound and show a small animated alert overlay; on death, play a stronger impact/defeat cue and swap to a breach/failure overlay. Use looping background music during active play and separate sounds for start, UI clicks, warning, impact, and game over.

Keep progression entirely endurance-based. There should be **no shooting, no upgrades, no inventory, no levels, and no meta systems**. The identity of the game is minimalist pressure: smooth drift movement, escalating enemy encirclement, neon audiovisual feedback, instant failure on contact, and fast replayability.