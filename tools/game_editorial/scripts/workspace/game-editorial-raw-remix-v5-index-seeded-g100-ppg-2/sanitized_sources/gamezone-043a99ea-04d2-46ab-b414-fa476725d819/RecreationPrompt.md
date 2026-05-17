# Recreation Prompt

Create a polished single-screen browser arcade game called **Clingy Love** with a neon pixel-art romance theme. The game should feel like a cute, funny, melodramatic endless runner built around one binary interaction instead of complex movement.

The player controls **two tiny lovers as a linked pair** positioned near the left side of the screen while the stage scrolls from right to left automatically. The core mechanic is that the pair can exist in only two formations:

- **Hold mouse or touch** to make them **hug together**, collapsing into the center lane.
- **Release** to make them **split apart**, separating into an upper and lower lane.

Design the entire gameplay loop around reading upcoming obstacle shapes and switching between those two states at the right time.

Use two major hazard types:
1. **A central blocker / jealous wall** that fills the middle area and forces the player to stay split.
2. **A cuddle tunnel** with a safe center passage that forces the player to hug together tightly.

Add **heart collectibles** that reinforce the same logic:
- center hearts should reward hugging
- paired top-and-bottom hearts should reward staying split

Colliding with any hazard should **instantly end the run**. Collecting hearts should **increase score**. The game should be **endless**, with the challenge rising through gradually increasing scroll speed and sustained reaction pressure rather than level transitions.

Present everything on a **full-screen canvas** with a strong **retro arcade** look:
- neon pink, cyan, gold, and deep purple palette
- pixel-art characters and heart sprites
- sparkles and skyline silhouettes in the background
- glowing tunnel edges and flashy hazard shapes
- little particle bursts when collecting hearts or entering tight hug mode

Include lightweight UI overlays:
- a start screen with playful instructions
- a game-over screen with final score and restart button
- a compact HUD showing **score** and current **mode** such as Hug or Split
- animated positive/failure reaction feedback for pickups and crashes

The tone should be **romantic, campy, energetic, and silly**, using playful wording around heartbreak, drama, cuddles, and love. It should read immediately on both desktop and mobile, with touch-friendly hold/release controls and no need for keyboard input. The final experience should feel like a tightly scoped one-button arcade score-chaser whose signature idea is switching a romantic duo between **split mode** and **hug mode** to survive and collect hearts.