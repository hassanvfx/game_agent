Create a polished single-screen HTML5 canvas arcade game called **Cloud Courier** where the player controls a cute airborne courier character in a bright futuristic sky. The game should feel like an endless runner mixed with a platformer: the world auto-scrolls steadily from left to right, the player character stays near the left side of the screen, and survival depends on hopping across procedurally generated floating platforms that vary in width, spacing, and height.

Use a very simple control scheme suited for both desktop and mobile: tap/click on the canvas or press **Space** to jump. Allow a **double jump**, so the player can jump once from the ground and once again in midair before needing to land to refresh jumps. Build the movement around gravity, vertical velocity, landing detection, and responsive jump timing. The challenge should come from judging gaps, recovering with the second jump, and deciding whether to chase riskier pickups without falling.

The main gameplay loop should be:
1. Start on a title screen with a prominent **Start Run** button.
2. Begin an endless run with automatic forward scrolling.
3. Jump from platform to platform while the route continuously generates ahead.
4. Collect floating **package tags / delivery pickups** placed above or near many platforms for large score bonuses.
5. Gain additional score gradually from distance traveled.
6. Lose immediately if the player falls below the bottom of the screen.
7. Show a game-over panel with the run score, a persistent best score, and a clear **Try Again** restart button.

Present the game with a vivid sky gradient background, soft drifting cloud forms, rounded floating platforms, and a bright glassy sci-fi HUD. Show the current route score in a compact overlay badge during play. Make the UI feel cheerful, high-contrast, and mobile safe, with full-screen canvas presentation and overlay panels for start and game-over states.

Add satisfying arcade juice: the character should rotate slightly while airborne, squash/stretch on jumps and landings, and trigger particles on jump, pickup, and failure. Package pickups should create a celebratory burst and brief feedback card such as “Delivery bonus!” or “Package saved!” Failure should trigger a short shake effect and a playful “route missed” style response rather than a harsh tone.

Include upbeat looping background music and distinct sound effects for start, restart, jump, landing, pickup, and game over. Overall, the game should feel breezy, replayable, and score-driven: a lightweight sky-delivery endless platform runner designed for short sessions, fast restarts, and chasing a better route every run.