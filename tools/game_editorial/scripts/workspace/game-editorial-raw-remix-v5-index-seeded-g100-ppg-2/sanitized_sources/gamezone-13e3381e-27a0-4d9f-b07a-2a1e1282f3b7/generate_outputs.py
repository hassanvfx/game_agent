from pathlib import Path
import json

workspace = Path(".")

blueprint = """# Blueprint

## High-level code structure
- The game is a self-contained single-page browser project in `index.html`.
- HTML defines the full-screen canvas, HUD, start/game-over overlays, audio elements, config script, and animated GIF feedback nodes.
- CSS establishes the neon streamer/chat aesthetic, responsive layout rules, glass panels, HUD styling, and overlay animation behavior.
- JavaScript contains all runtime systems: audio management, config loading, input handling, state management, spawning, update/draw loop, particles, and UI transitions.

## Game loop / state model
- Core states:
  - `START`
  - `PLAYING`
  - `GAMEOVER`
- `DOMContentLoaded` initializes config, audio, resizing, input, and launches `requestAnimationFrame(gameLoop)`.
- `gameLoop(timestamp)` computes delta time, runs `update(dt)`, then `draw()`.
- `startGame()` resets score, hype, combo, entities, and speed, swaps UI visibility, starts BGM, and spawns the first message.
- `gameOver()` stops BGM, shows the fail overlay, stores the final score, and moves the game into the game-over state.

## Player goals
- Clear as many incoming chat posts as possible.
- Match each falling post to the correct action before it reaches the bottom action line.
- Maintain the hype meter, which acts as the survival resource.
- Build score and combo while surviving increasing speed and feed density.

## Interaction pattern
- Real-time single-screen input via pointer/touch/click.
- Three large bottom buttons represent actions mapped to message categories:
  - `BLOCK` for troll/spam posts
  - `BOOST` for positive fan posts
  - `RIDE` for meme/joke posts
- Pressing a button acts on the lowest active message nearest the bottom, so play is about timing and rapid classification rather than selecting arbitrary targets.
- Correct matches grant score, combo, hype recovery, particles, SFX, and success GIF feedback.
- Wrong matches or ignored posts reduce hype, break combo, shake the screen, and trigger fail feedback.

## Core systems
- **Spawn system:** falling chat bubbles are generated on a timer with randomized text pulled from type-specific pools.
- **Classification mechanic:** every message belongs to one of three fixed categories with a matching button/action.
- **Priority targeting rule:** input always resolves against the lowest active message, making the experience feel like a streamer-themed reaction lane game.
- **Score/combo system:** score increases on success, with combo adding extra reward.
- **Pressure meter:** hype continuously decays and is further damaged by mistakes and misses.
- **Difficulty scaling:** `gameSpeed` rises with score, increasing movement speed and spawn pressure.
- **Feedback system:** BGM, SFX, warning tone, particles, floating score text, canvas shake, bar color changes, and reaction GIFs.
- **Responsive/mobile layout:** canvas fills the viewport and action buttons resize to screen width, indicating mobile-safe intent.

## Inferred genre / gameplay shape
- Casual arcade survival game centered on reflex classification.
- Strong rhythm/timing-adjacent feel because inputs are tied to the lowest approaching item and three persistent bottom actions.
- Theme is modern streamer/chat moderation rather than literal music rhythm or realistic simulation.
- Session loop is score attack: start a run, survive as long as possible, lose when hype empties, and retry immediately.
"""

recreation_prompt = """Recreate a polished mobile-friendly browser arcade game called “Chat Rush: Mod Queue.” The game should present the player as a late-night moderator managing a chaotic livestream or community chat feed inside a neon, futuristic, streamer-inspired interface. Use a full-screen canvas for gameplay and overlay it with stylish HUD panels and menu screens. The core loop is simple and fast: short chat messages fall from the top of the screen toward three large action buttons at the bottom, and the player must quickly press the matching button before each message reaches the action line. There are exactly three message categories and three matching actions: toxic or troll posts should be handled with a red “BLOCK” action, supportive fan messages should be handled with a green “BOOST” action, and meme/joke posts should be handled with a yellow “RIDE” action. The player never taps individual messages directly; instead, each button press should automatically resolve against the lowest currently active incoming message, making the game feel like a rapid classification lane challenge. Correct calls should award score, build combo, slightly restore a survival meter, and trigger satisfying audiovisual feedback such as particles, floating score text, a bright success sound, and a celebratory animated reaction image. Wrong calls or missed messages should reset combo, reduce the survival meter, shake the screen, and trigger a failure sound and fail reaction animation. The survival meter should represent chat stability or hype pressure and should also decay slowly over time, forcing constant action even if the player is not making mistakes. As score increases, the game should get harder by making messages arrive or move faster, creating a score-chasing survival structure. Include a strong start screen with the title, a short one-line rules summary, and clear icon hints for the three actions, plus a game-over screen that shows the total cleared posts and offers an instant restart. The visual style should feel like a hybrid of livestream dashboard, Discord-like chat energy, and arcade neon sci-fi, with dark purple-blue gradients, glowing borders, bold futuristic fonts, emoji-like icons, and animated UI polish. Keep the experience readable, punchy, replayable, and easy to play with mouse or touch on both desktop and mobile."""

identity = {
    "title": "Chat Rush: Mod Queue",
    "premise": "A neon streamer-chat arcade game where the player moderates a flood of incoming posts by matching each one to the right action before the feed overheats.",
    "interaction_model": "Single-screen real-time tap/click control with three persistent bottom action buttons that classify the lowest incoming message.",
    "objective": "Clear as many posts as possible, maintain the hype meter, and survive the accelerating moderation queue.",
    "progression": "A run starts at a manageable pace, then message pressure increases with score while combo boosts scoring and mistakes or misses drain hype toward game over.",
    "theme": "Livestream moderation, internet chat culture, memes, trolls, and fan engagement in a neon futuristic UI.",
    "mood": "Chaotic, playful, fast, reactive, and slightly stressful with punchy streamer-style feedback.",
    "likely_audience": "Players who enjoy casual arcade score-chasing games, mobile-friendly reflex challenges, and internet/streaming aesthetics.",
    "confidence_notes": [
        "High confidence that the game is a real-time reflex classification arcade game built around three fixed moderation actions.",
        "High confidence that the survival resource is the hype bar, which behaves like a health or pressure meter with passive decay.",
        "Moderate confidence that the fantasy is specifically moderator duty rather than being the streamer, though the presentation uses streamer-channel framing.",
        "Moderate confidence that the experience is intended to feel rhythm-adjacent, even though it is not a literal music game."
    ],
    "recreation_prompt": recreation_prompt
}

mechanics_ranking = {
    "top_5_mechanics": [
        "Clicker game",
        "Rhythm music game",
        "Lane runner game",
        "Speed runner",
        "Chat simulator"
    ]
}

mechanics_companion = {
    "selected_top_5": [
        {
            "category": "Clicker game",
            "score": 0.82,
            "reasoning": "The primary interaction is rapid repeated tapping/clicking of on-screen buttons to process a fast stream of incoming targets under pressure.",
            "uncertainty": "It is more skill-based and timing-heavy than a traditional idle or accumulation clicker."
        },
        {
            "category": "Rhythm music game",
            "score": 0.78,
            "reasoning": "The game resembles a three-lane timing challenge where falling items approach a bottom action line and the player must match the right input in sequence.",
            "uncertainty": "There is no beat matching or music-driven chart structure, so this is a thematic mechanical resemblance rather than a strict rhythm title."
        },
        {
            "category": "Lane runner game",
            "score": 0.68,
            "reasoning": "Incoming messages behave like lane-style hazards/targets moving toward the bottom interaction zone, creating a lane-based reaction pattern.",
            "uncertainty": "The player does not move an avatar between lanes; the lane feel comes from the three static action buttons."
        },
        {
            "category": "Speed runner",
            "score": 0.54,
            "reasoning": "Success depends on rapidly making correct inputs as overall speed and pressure increase over time.",
            "uncertainty": "There is no traversal or level racing, so this only matches the escalating reflex/speed emphasis."
        },
        {
            "category": "Chat simulator",
            "score": 0.49,
            "reasoning": "The theme, interface, and objects are all modeled around a live chat feed with moderation actions and channel presentation.",
            "uncertainty": "The structure is arcade abstraction rather than a conversational or social simulation."
        }
    ],
    "uncertainty_notes": [
        "No category in the provided universe exactly captures 'arcade moderation reflex game,' so the ranking emphasizes closest interaction feel rather than perfect genre identity.",
        "Categories like Endless runner or Neon runner are weaker because the player is not controlling forward movement, only reacting to incoming objects.",
        "The game has light simulation theming but does not behave like a deep management or tycoon system."
    ]
}

semantic_tags = {
    "theme": [
        "livestream moderation",
        "internet culture",
        "chat chaos",
        "community management",
        "memes",
        "troll filtering"
    ],
    "setting": [
        "digital chat room",
        "stream dashboard",
        "futuristic neon interface",
        "virtual moderation booth"
    ],
    "characters": [
        "player moderator",
        "fans",
        "trolls",
        "meme posters",
        "stream audience"
    ],
    "mechanics": [
        "real-time classification",
        "three-button input",
        "falling messages",
        "score attack",
        "combo scoring",
        "survival meter",
        "increasing speed",
        "mistake punishment",
        "tap controls",
        "reaction gameplay"
    ],
    "mood": [
        "chaotic",
        "playful",
        "arcade",
        "tense",
        "flashy",
        "energetic"
    ],
    "similar_games": [
        "Papers, Please",
        "Rhythm Heaven",
        "Guitar Hero",
        "Not Tonight"
    ],
    "similar_franchises": [
        "Just Dance",
        "Taiko no Tatsujin",
        "WarioWare"
    ]
}

contract = {
    "status": "ok",
    "detail": "Generated Blueprint.md, Identity.json, mechanics ranking, companion classification data, semantic tags, and a detailed user-facing recreation prompt."
}

files = {
    "Blueprint.md": blueprint,
    "Identity.json": json.dumps(identity, indent=2, ensure_ascii=False) + "\n",
    "mechanics_ranking.json": json.dumps(mechanics_ranking, indent=2, ensure_ascii=False) + "\n",
    "mechanics_classification_companion.json": json.dumps(mechanics_companion, indent=2, ensure_ascii=False) + "\n",
    "semantic_tags.json": json.dumps(semantic_tags, indent=2, ensure_ascii=False) + "\n",
    "RecreationPrompt.md": recreation_prompt + "\n",
    "operator_result_contract.json": json.dumps(contract, indent=2, ensure_ascii=False) + "\n"
}

for name, content in files.items():
    (workspace / name).write_text(content, encoding="utf-8")

required = list(files)
missing = [name for name in required if not (workspace / name).exists()]
if missing:
    raise SystemExit(f"Missing files after write: {missing}")

print("Created:", ", ".join(required))