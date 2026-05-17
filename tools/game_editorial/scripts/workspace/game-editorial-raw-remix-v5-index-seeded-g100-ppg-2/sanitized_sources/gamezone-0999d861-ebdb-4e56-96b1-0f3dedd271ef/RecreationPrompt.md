Create a polished, mobile-friendly browser mini-game called **"Witch's Wardrobe: Elements"** where the player must quickly dress a cute cartoon witch to match a displayed target outfit before the timer runs out. The game should take place on a single screen with a highly readable HUD, a central character showcase, and large touch-friendly controls. Present the game as a whimsical moonlit fantasy wardrobe challenge with rich purple-and-gold colors, magical glow effects, starry ambience, and an arcade-like sense of urgency.

At the top of the screen, show a **target outfit panel** with three required item icons: one for **Head**, one for **Body**, and one for **Hand**. Beside that, show a **score counter** and a **countdown timer**. In the center, render a stylized full-body witch character standing on a magical stage with animated stars, glow halos, and subtle celebratory particle effects during successful matches. The witch should be visibly updated in real time as the player changes outfit parts.

At the bottom, provide three clearly labeled control rows for **Head**, **Body**, and **Hand**. Each row should have a left arrow and right arrow so the player can cycle through exactly **five options** in that category with wraparound behavior. Use distinct themed options such as:
- **Head:** pointy hat, flower crown, hood, devilish horns, moon tiara
- **Body:** purple robe, nature-inspired dress, royal gown, bone-themed outfit, starry cosmic dress
- **Hand:** broom, wand, lantern, potion bottle, spellbook

The main gameplay loop should be:
1. Start with a 60-second timer.
2. Generate a random target combination for head, body, and hand.
3. Let the player cycle the three slots until the displayed witch matches the target.
4. Require the player to press a large **"Cast Spell"** button to submit the current outfit.
5. If the outfit matches exactly, award a big score bonus, add extra time, play a cheerful magical sound, show a positive reaction animation, briefly celebrate the success, and then generate a new random target.
6. If the outfit is incorrect, subtract time, play a fail sound, show a negative reaction, and keep the same target active so the player can correct it and try again.
7. End the run when time reaches zero and show a game-over screen with the final score and a restart button.

Make the interface feel responsive and satisfying on both desktop and phone screens. Use dramatic title and result overlays, bright fantasy-styled buttons, clear feedback for matched target slots, and a cozy-but-energetic magical tone. The experience should feel like a compact arcade dress-up matching game rather than an open-ended sandbox, with fast replayability, readable visual cues, and strong audiovisual feedback for every action.