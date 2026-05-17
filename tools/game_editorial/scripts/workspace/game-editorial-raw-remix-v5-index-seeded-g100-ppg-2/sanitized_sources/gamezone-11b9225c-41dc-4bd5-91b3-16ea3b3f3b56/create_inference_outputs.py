from pathlib import Path
import json

root = Path(".")

files = {}

files["Blueprint.md"] = """# Blueprint

## High-level code structure
- Single-file HTML game with embedded CSS, DOM HUD, audio tags, JSON config, and a canvas-based JavaScript game loop.
- Presentation is split between:
  - a full-screen `canvas` for gameplay rendering,
  - DOM overlays for HUD, game-over modal, flavor caption, audio status pill, and reaction GIFs,
  - inline audio elements orchestrated by a small `AudioManager`.
- Runtime tuning values are exposed through `window.gameConfig`, populated from the inline `#game-config` JSON block.

## Game loop / state model
- Main states:
  - `BOOT`: startup before the first resize and initialization pass.
  - `PLAYING`: active endless run.
  - `GAMEOVER`: terminal state entered when the player collides with a bomb.
- Main loop uses `requestAnimationFrame(loop)` and performs:
  1. delta-time calculation,
  2. `update(dt)` for spawn timing, hero movement, collision checks, score changes, particles, and transient feedback timers,
  3. `draw()` for background, hero hoop, falling entities, and particles.
- `resize()` sizes the canvas and starts the first run by calling `initGame()` then `setState('PLAYING')`.
- `initGame()` resets round data, positions the hoop, clears entities and particles, and refreshes HUD values.

## Player goals
- Catch falling basketballs to increase score.
- Avoid bombs, since a single bomb collision ends the run instantly.
- Beat the persistent best score saved in local storage.
- Survive longer as the pace increases with score.

## Interaction pattern
- Pointer/touch controls set a horizontal target position for the hoop.
- The hoop smoothly eases toward the target x-coordinate instead of teleporting.
- `pointerdown` and `pointermove` both function as gameplay input.
- On game over, the next input restarts the session immediately.
- The game is designed for phones as well as desktop: safe-area-aware UI, disabled default touch gestures on the canvas, and optional vibration bridge calls.

## Core systems
- **Hero system:** a hoop-shaped catcher near the bottom of the screen, rendered as a cute neon rim.
- **Spawn system:** falling entities appear on a timer; each spawn is either a ball or a bomb based on `bombChance`.
- **Difficulty scaling:** entity fall speed is based on gravity and scaled upward by score.
- **Collision system:** simple circular distance checks between each falling entity and the hoop catch zone.
- **Score system:** each caught ball adds one point; best score persists via `localStorage`.
- **Failure system:** touching a bomb triggers game over, audio/visual fail feedback, screen shake, and the restart overlay.
- **Feedback system:** particles, reaction GIFs, HUD text changes, audio cues, and haptics reinforce events.
- **Rendering system:** the game draws its own background, hoop, balls, and bombs directly on canvas for a self-contained arcade presentation.

## Inferred genre / gameplay shape
- Arcade reflex score-chaser with catch-and-dodge gameplay.
- Closest overall shape is an endless survival runner/lane-dodger abstraction, even though the field is single-screen and objects fall vertically instead of the world scrolling.
- The presentation theme is a futuristic basketball micro-arcade.

## Gameplay heuristic
- Hover near likely ball trajectories and make compact side-to-side corrections.
- Prioritize survival over perfect collection because bombs cause instant loss while missed balls are not directly punished.
- Expect pressure to rise over time as falling speed accelerates.
- The intended feel is fast restart, short sessions, and repeated best-score attempts.
"""

identity = {
    "title": "Hoop Rush: Neon Dunk",
    "premise": "A neon arcade basketball survival game where a glowing hoop catches falling balls while dodging explosive bombs on a futuristic court.",
    "interaction_model": "Single-screen real-time pointer or touch control; move the hoop horizontally to intercept safe objects and avoid hazards.",
    "objective": "Catch as many basketballs as possible, avoid bombs, and set a new best score before a bomb collision ends the run.",
    "progression": "Endless score attack with gradually increasing fall speed, instant restarts after failure, and persistent best-score tracking.",
    "theme": "Futuristic neon street-basketball arcade.",
    "mood": "Energetic, flashy, reactive, and lightly playful.",
    "likely_audience": "Casual mobile and browser players who enjoy short reflex-based arcade sessions with simple controls and bright feedback.",
    "confidence_notes": "High confidence on the core loop, control scheme, and game-over condition because they are explicit in code. Moderate confidence on category mapping because the provided category universe lacks an exact falling-object catcher label.",
    "recreation_prompt": "Create a mobile-friendly browser arcade game called 'Hoop Rush: Neon Dunk' set on a futuristic neon basketball court. The player controls a glowing hoop positioned near the bottom of the screen and moves it horizontally with touch, drag, or mouse input. Basketballs and bombs fall from random positions at the top of the screen at regular intervals. Catching a basketball increases the score by one, triggers bright particles, quick positive audio, light haptics, and a celebratory reaction image. Touching a bomb immediately ends the run, plays a failure sound, shakes the screen, shows a game-over overlay with the final score, and allows instant restart. The game should be endless rather than level-based, with fall speed increasing as the score rises so the pressure ramps up naturally. Include a HUD for current score and best score, save the best score locally, and present everything with glossy sci-fi UI panels, animated neon court lines, a stylized smiling hoop character, vivid basketball and bomb sprites drawn on canvas, pulsing feedback text, looping background music that starts on first interaction, and a fast, readable one-screen arcade presentation optimized for phones."
}
files["Identity.json"] = json.dumps(identity, indent=2) + "\n"

mechanics_ranking = {
    "top_5_mechanics": [
        "Lane runner game",
        "Endless runner",
        "Obby runner",
        "Satisfying simulator",
        "Arcade fighting game"
    ],
    "notes": "Ranking is constrained to the provided category universe. The actual game is best described as a falling-object catch-and-dodge arcade game, so some category matches are approximate."
}
files["mechanics_ranking.json"] = json.dumps(mechanics_ranking, indent=2) + "\n"

classification = {
    "selected_top_5": [
        {
            "category": "Lane runner game",
            "score": 0.79,
            "reasoning": "Strongest match because play revolves around rapid horizontal lane-like positioning to collect safe targets and avoid hazards during an endless run."
        },
        {
            "category": "Endless runner",
            "score": 0.72,
            "reasoning": "The overall structure is an endless survival score chase with accelerating pace, instant retries, and reflex-heavy avoidance/collection."
        },
        {
            "category": "Obby runner",
            "score": 0.41,
            "reasoning": "There is a loose overlap with obstacle-timing play because the player continuously threads through dangerous object lanes."
        },
        {
            "category": "Satisfying simulator",
            "score": 0.31,
            "reasoning": "Particles, glow effects, tactile collection feedback, and polished audiovisual responses make the catch loop feel satisfying."
        },
        {
            "category": "Arcade fighting game",
            "score": 0.08,
            "reasoning": "Extremely weak fallback match only because it is fast and reactive; there is no real combat system."
        }
    ],
    "uncertainty_notes": [
        "The category universe does not include a direct falling-object catcher, dodge-and-collect arcade, or basketball arcade descriptor.",
        "Runner-adjacent labels are used because the closest abstraction is continuous survival through horizontal positioning.",
        "The bottom two ranked matches are weak approximations rather than strong genre fits."
    ]
}
files["mechanics_classification.json"] = json.dumps(classification, indent=2) + "\n"

tags = {
    "theme": [
        "neon sports",
        "futuristic arcade",
        "cyber basketball",
        "score attack"
    ],
    "setting": [
        "glowing digital court",
        "sci-fi arena backdrop",
        "single-screen playfield",
        "mobile-friendly web canvas"
    ],
    "characters": [
        "smiling hoop avatar",
        "falling basketballs",
        "bomb hazards"
    ],
    "mechanics": [
        "horizontal movement",
        "catch collectibles",
        "avoid hazards",
        "endless survival",
        "difficulty scaling",
        "best-score chasing",
        "instant restart",
        "particle feedback",
        "touch controls"
    ],
    "mood": [
        "energetic",
        "flashy",
        "playful",
        "arcade tense",
        "responsive"
    ],
    "similar_games": [
        "catch-the-falling-object arcade games",
        "endless dodge-and-collect browser games",
        "single-screen reflex score chasers"
    ],
    "similar_franchises": [
        "Geometry Dash",
        "Subway Surfers",
        "basketball arcade cabinet games"
    ]
}
files["semantic_tags.json"] = json.dumps(tags, indent=2) + "\n"

files["RecreationPrompt.md"] = """# Recreation Prompt

Create a one-screen browser game called **Hoop Rush: Neon Dunk** that feels like a futuristic neon basketball arcade survival challenge. The game should run in a full-screen mobile-friendly canvas with glossy HUD panels layered above it. The player controls a glowing hoop near the bottom of the screen by moving left and right with mouse, touch, or drag input. The hoop should ease toward the pointer target instead of snapping instantly so the movement feels smooth and magnetic.

The gameplay loop is fast and simple: basketballs and bombs fall from random positions at the top of the screen at a regular spawn cadence. Catching a basketball gives the player one point and should trigger bright particle bursts, a punchy collect sound, a light vibration cue when available, and a brief celebratory reaction visual. Catching a bomb should immediately end the run, play a harsh fail sound, shake the screen, pause the background music, flash a danger reaction, and open a centered game-over card showing the final score with a clear play-again button. The player should be able to restart instantly.

Make the game endless instead of level-based. Difficulty should ramp naturally by increasing the falling speed as the score rises. Missing a basketball should not directly cause failure; the main challenge is choosing safe interceptions while avoiding bombs. Save and display a persistent best score locally.

For presentation, use a dark sci-fi court backdrop with moving neon lane lines, glow accents, subtle stars or ambient lights, and a polished cyber-sports UI. Show the current score and best score in glassy futuristic HUD cards. Render the hoop as a stylized, slightly cute neon rim character, and draw the basketballs and bombs directly on canvas with bright readable colors and arcade exaggeration. Add looping background music that starts on first interaction, plus distinct sounds for collect, start, button press, and game over. The overall tone should be energetic, flashy, accessible, and optimized for short replayable mobile sessions.
"""

contract = {
    "status": "ok",
    "detail": "Generated Blueprint.md, Identity.json, mechanics ranking, companion classification data, semantic tags, and a detailed user-facing recreation prompt."
}
files["operator_result_contract.json"] = json.dumps(contract, indent=2) + "\n"

for name, content in files.items():
    (root / name).write_text(content, encoding="utf-8")

print("\n".join(files.keys()))