from pathlib import Path
import json

root = Path(".")

blueprint = """# Blueprint

## High-level code structure
- Single-file HTML game with inline CSS, HTML UI, configuration JSON, audio asset declarations, and all gameplay logic in one embedded script.
- Rendering is handled with a full-screen HTML5 canvas.
- UI overlays are regular DOM elements layered above the canvas for HUD, feedback banners, reaction GIFs, and the game-over modal.
- The game uses lightweight class-based entities (`Particle`, `Ingredient`) plus global state variables for score, lives, timers, difficulty, and current mode.

## Game loop / state model
- Main states are `INIT`, `PLAYING`, and `GAMEOVER`.
- `resize()` initializes the canvas, starts the game once, and kicks off `requestAnimationFrame(loop)`.
- `loop()` computes delta time, updates simulation only while in `PLAYING`, always redraws the scene, and self-recovers from loop errors.
- `update()` handles timed spawning, falling ingredient motion, missed-item penalties, and particle cleanup.
- `draw()` renders the kitchen-themed background, counter, decorative lights/grid, then ingredients and particles.
- State transitions are centralized through `setState()`, which toggles HUD visibility, game-over screen, and music playback.

## Player goals
- Tap falling fresh ingredients before they leave the bottom of the screen.
- Avoid tapping rotten ingredients.
- Survive as long as possible with 3 lives while increasing the order count/score.
- Maintain streaks for positive feedback and a feeling of kitchen momentum.

## Interaction pattern
- Primary interaction is single-pointer tapping/clicking on falling circular targets.
- A hit checks collision against the top-most ingredient under the pointer.
- Good taps remove fresh food, play chop/score feedback, spawn celebratory particles, and add score.
- Bad taps on rotten items or allowing fresh items to fall off-screen cost a life.
- Tapping empty space does not remove life, but it breaks combo momentum and triggers warning feedback.

## Core systems
- **Spawn system:** Ingredients appear on a timer, with spawn interval clamped and sped up by difficulty.
- **Difficulty ramp:** `difficultyMultiplier = 1 + score / 500`, increasing fall speed pressure and effective spawn pace over time.
- **Entity system:** Falling ingredient objects and short-lived particle effects.
- **Scoring/combo system:** Fresh hits give 10 points; combo streak messaging starts at 3 consecutive successes.
- **Life/failure system:** The player starts with 3 mistakes; life loss comes from missed fresh items or tapping rotten ones.
- **Audio/haptics system:** Background loop plus SFX for chop, score, warning, fail, and UI; vibration hooks exist for supported environments.
- **Presentation feedback:** Banner callouts, shake effect, success/failure GIF overlays, HUD counters, and a restart modal.

## Inferred genre / gameplay shape
- Arcade reflex game centered on rapid target tapping.
- Best described as a casual cooking-themed click/tap action game with survival scoring pressure.
- Structurally similar to “fruit slicing / ingredient chopping” lane-less tap survival games, but without swipe slicing; it is discrete tap-to-hit gameplay.
- Session shape is short, score-chasing, and endless until mistakes are exhausted.

## Gameplay heuristic
- The player visually scans the whole screen for descending ingredients.
- Priority is to quickly identify safe targets (fresh items) and ignore hazards (rotten items).
- Higher scores imply faster reaction speed and stronger discrimination under increasing spawn density.
- The intended feel is a busy prep line: quick correct taps, accumulating streak hype, and sudden collapse after repeated kitchen mistakes.
"""

recreation_prompt = "Recreate a fast-paced single-screen mobile-friendly arcade cooking game called “Chef's Rush: Prep Line.” Present it as a full-screen HTML5 canvas game with a warm neon kitchen look: purple-to-orange gradient background, subtle tile/grid motion, hanging menu lights, a service counter at the bottom, and glossy cartoon ingredients falling from the top. The player interacts only by tapping or clicking ingredients. Most falling targets are fresh food and should be tapped before they reach the bottom; some are rotten hazard ingredients and must be avoided. Fresh ingredients should have cute friendly faces and bright food colors, while rotten ones should look darker and unpleasant with crossed eyes or spoiled details so they can be distinguished instantly. Each successful tap should remove the ingredient, spawn juicy particle bursts, play chop and score feedback, increment an orders/score counter by 10, and build a combo streak that starts showing hype feedback after several clean hits. Missing a fresh ingredient or tapping a rotten one should cost one of 3 lives/mistakes, trigger danger feedback, screen shake, and a fail or warning response. Tapping empty space should not remove a life, but it should break the combo and show a small warning effect. Increase difficulty endlessly by making ingredients fall faster and effectively spawn more often as the score rises. Use simple states for init, playing, and game over. Overlay a HUD showing Orders on the left and Mistakes on the right, transient feedback banners near the bottom center, optional success/fail reaction visuals near the screen edges, and a polished game-over modal with the final score and a restart button. Include looping background music, short arcade kitchen sound effects, mobile-safe pointer controls, responsive layout, and a short-session endless score-chasing tone that feels energetic, playful, and hectic like surviving a busy prep line."

identity = {
    "title": "Chef's Rush: Prep Line",
    "premise": "A frantic kitchen reflex game where the player taps fresh falling ingredients to keep the prep line moving while avoiding rotten items.",
    "interaction_model": "Single-pointer tap/click target selection on falling objects in a full-screen canvas.",
    "objective": "Score as many completed orders as possible by chopping fresh ingredients before they fall, while avoiding hazards and preserving 3 lives.",
    "progression": "Endless survival score chase with increasing fall speed and spawn pressure as score rises; run ends at zero lives and can be instantly restarted.",
    "theme": "Arcade kitchen prep rush with colorful cartoon food and light restaurant-showmanship presentation.",
    "mood": "Energetic, playful, hectic, and lightly stressful in a fun arcade way.",
    "likely_audience": "Casual mobile and web players who enjoy quick reflex games, cooking themes, and short replayable score-attack sessions.",
    "confidence_notes": [
        "High confidence in the tap-to-chop endless arcade loop because all core mechanics are explicit in the source.",
        "Moderate confidence in genre labeling because it mixes cooking theme with target-tapping rather than simulation-heavy cooking systems.",
        "High confidence that the game is intended for mobile-first play due to pointer input, viewport constraints, vibration support, and responsive HUD."
    ],
    "recreation_prompt": recreation_prompt
}

mechanics_ranking = {
    "top_5_mechanics": [
        "Clicker game",
        "Cooking game",
        "Satisfying simulator",
        "ASMR relaxing game",
        "Endless runner"
    ]
}

mechanics_companion = {
    "selected_top_5": [
        {
            "category": "Clicker game",
            "score": 0.89,
            "reasoning": "The core loop is rapid repeated tapping on targets for immediate reward, which most closely matches click/tap-driven arcade interaction.",
            "uncertainty": "It is more action-reflex-oriented than economy-driven clickers, so the fit is mechanical rather than genre-market exactness."
        },
        {
            "category": "Cooking game",
            "score": 0.86,
            "reasoning": "The theme, scoring language, feedback, and ingredients all frame the game as a kitchen prep experience even though systems are arcade-simple.",
            "uncertainty": "It lacks broader recipe assembly or station management, so this is theme-plus-loop rather than a full cooking simulator."
        },
        {
            "category": "Satisfying simulator",
            "score": 0.71,
            "reasoning": "Successful chops produce tactile audiovisual feedback, particles, combo callouts, and a satisfying repetitive action cadence.",
            "uncertainty": "The game has failure pressure and life loss, so it is less purely soothing than many titles in this category."
        },
        {
            "category": "ASMR relaxing game",
            "score": 0.42,
            "reasoning": "The game uses pleasing taps, chop effects, and visually appealing ingredient pops that partially overlap with ASMR-like design goals.",
            "uncertainty": "The escalating urgency and mistake penalties make it more stressful than actually relaxing."
        },
        {
            "category": "Endless runner",
            "score": 0.31,
            "reasoning": "It has endless survival escalation and constant incoming obstacles/targets, which resembles the pressure curve of endless arcade runners.",
            "uncertainty": "There is no movement through space or lane navigation, so this is only a distant structural similarity."
        }
    ],
    "uncertainty_notes": [
        "The provided category universe does not include a direct 'fruit ninja' or 'tap reflex arcade' category, so the ranking uses closest mechanical approximations.",
        "Cooking theming is explicit, but deeper cooking-system categories would overstate the amount of simulation present."
    ]
}

semantic_tags = {
    "theme": [
        "cooking",
        "kitchen rush",
        "restaurant prep",
        "arcade chef fantasy"
    ],
    "setting": [
        "stylized kitchen",
        "prep line",
        "restaurant service counter",
        "neon food arcade backdrop"
    ],
    "characters": [
        "player as unseen line cook",
        "cartoon fresh ingredients",
        "rotten hazard ingredients",
        "chef-branded UI persona"
    ],
    "mechanics": [
        "tap to chop",
        "falling targets",
        "hazard avoidance",
        "endless survival",
        "score attack",
        "combo streaks",
        "lives system",
        "difficulty ramp",
        "particle feedback",
        "arcade restart loop"
    ],
    "mood": [
        "playful",
        "hectic",
        "juicy",
        "colorful",
        "arcade intense",
        "lightly comedic"
    ],
    "similar_games": [
        "Fruit Ninja",
        "Piano Tiles (target-tapping pace only)",
        "Cooking Mama minigame energy"
    ],
    "similar_franchises": [
        "Cooking Mama",
        "Papa's cooking games",
        "Fruit Ninja"
    ]
}

recreation_md = recreation_prompt + "\n"

contract = {
    "status": "ok",
    "detail": "Generated Blueprint.md, Identity.json, mechanics ranking, companion classification data, semantic tags, and a detailed user-facing recreation prompt."
}

files = {
    "Blueprint.md": blueprint,
    "Identity.json": json.dumps(identity, indent=2, ensure_ascii=False) + "\n",
    "mechanics_ranking.json": json.dumps(mechanics_ranking, indent=2, ensure_ascii=False) + "\n",
    "mechanics_classification.json": json.dumps(mechanics_companion, indent=2, ensure_ascii=False) + "\n",
    "semantic_tags.json": json.dumps(semantic_tags, indent=2, ensure_ascii=False) + "\n",
    "RecreationPrompt.md": recreation_md,
    "operator_result_contract.json": json.dumps(contract, indent=2, ensure_ascii=False) + "\n",
}

for name, content in files.items():
    (root / name).write_text(content, encoding="utf-8")