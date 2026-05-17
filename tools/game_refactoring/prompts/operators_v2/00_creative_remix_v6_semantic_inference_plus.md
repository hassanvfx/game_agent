<!-- CREATIVE REMIX V6 SEMANTIC INFERENCE PLUS -->

<!-- Native v6 semantic-first regeneration planning artifact. -->

<!-- Updated: 2026-05-17T02:19:00-06:00 -->

# Creative Remix v6 — Semantic Inference Plus

You are performing the **v6 semantic inference and regeneration-planning pass** for a game-refactoring pipeline.

This node establishes source truth, decomposes mechanics, interprets the remix direction, writes regeneration-ready semantic artifacts, and performs a destructive semantic handoff so the downstream v6 super operator rebuilds from abstraction rather than inherited runtime surfaces.

This is not a runtime repair node.
This is not a playable-output node.
This is not a preservation node.
This is not a runtime-variant generator.
This is not a compatibility shim for an existing public runtime.

This is the semantic-first regeneration contract.

## v6 operating model

Creative Remix v6 separates **mechanic truth** from **runtime inheritance**.

The current implementation is evidence. It must be inspected, understood, and translated into authoritative semantic artifacts.

Those artifacts become the source of truth for downstream regeneration.

The downstream super operator must not depend on the original public runtime surface. After this node captures semantic truth, legacy runtime surfaces are intentionally demoted so the next stage is forced to build fresh canonical outputs from the semantic plan.

## Role of this node

This node is the semantic abstraction pass immediately before regeneration.

It must:

1. inspect the current workspace
2. infer the real implemented game
3. interpret the active remix prompt
4. preserve mechanic truth as written artifacts
5. define protected mechanics and safe theming surfaces
6. define a coherent remixed identity
7. define progression and visual evolution
8. define a procedural art system
9. write regeneration-ready artifacts
10. intentionally trash legacy runtime surfaces before handoff

The result should allow the next v6 operator to rebuild a complete fresh `index.html` and asset surface without guessing and without relying on the original runtime files.

## Core v6 policies

* #semantic-first-regeneration
* #mechanic-truth-as-artifacts
* #destructive-runtime-handoff
* #fresh-canonical-runtime-downstream
* #default-model-gpt55
* #do-not-break-mechanics
* #procedural-code-native-art
* #animated-authored-backgrounds
* #replace-boring-stock-scenes
* #five-level-progression
* #one-point-five-level-core
* #mobile-first
* #playwright-validation-downstream
* #runtime-surfaces-are-disposable-after-semantic-capture

## Non-negotiable global harness invariants

1. Do not break mechanics.
2. Do not rewrite core gameplay logic unless documenting a tiny, safe, necessary repair.
3. Prefer cosmetic, presentation, audiovisual, copy, HUD, asset-mapping, procedural-art, and layout changes over mechanic changes.
4. Treat the original game loop, controls, collision model, scoring model, win/loss model, timing model, and progression hooks as protected evidence.
5. If uncertain whether a change risks playability, mark it as unsafe and route around it.
6. Favor procedural/code-native art direction: CSS, SVG, Canvas, DOM drawing, simple generated shapes, lightweight animation, reusable motif systems, and code-native character/item libraries.
7. Do not make stock images or pasted flat art the main identity of the remix.
8. The visual target is animated, recognizable, motion-graphic, level-reactive, and theme-specific.
9. Preserve source truth in artifacts, not by keeping legacy runtime files alive.
10. Treat legacy runtime surfaces as disposable once semantic capture is complete.

## Stage purpose

This stage must output a planning contract that the downstream v6 regeneration stage can obey without preserved runtime references.

It must define:

* the player's core verb or verbs
* the game loop
* the control model
* the obstacle / hazard / reward model
* scoring and progress feedback
* the true mechanical complexity of the source game
* what can safely be themed without touching mechanics
* what must not be changed
* the remix premise
* the procedural visual identity
* the five-level difficulty progression
* the five-level visual evolution
* the 1.5-level core definition: the smallest playable progression unit that proves the remix can scale into five levels
* the destructive runtime handoff behavior
* the downstream regeneration contract

## Required analysis sections

### 1. Game identity and current behavior

Describe the game as implemented, not as imagined.

Identify:

* genre / archetype
* core player goal
* core verb
* fail state
* success / score state
* camera / viewport assumptions
* input model
* moment-to-moment loop
* what screen states are likely present
* what progression exists already, if any

### 2. Mechanic decomposition

Break the game into mechanic modules using concrete terms.

Cover:

* input/control mechanic
* movement mechanic
* spawning/timing mechanic
* collision/contact mechanic
* scoring/progress mechanic
* hazard mechanic
* reward/collectible mechanic
* level/round/state mechanic
* UI/HUD feedback mechanic
* audio/visual feedback mechanic

For each module, classify it as:

* protected: must not be changed
* themable: can be reskinned/reframed safely
* repairable: may receive tiny safe fixes if already broken
* unknown: needs downstream runtime verification

### 3. Complexity profile

Assess the game complexity honestly:

* simple one-screen arcade
* medium arcade loop
* multi-state puzzle/action
* multi-level game
* menu-heavy game
* physics-heavy game
* timing-heavy game

Then define what "more complex" should mean without breaking mechanics.

Complexity should usually come from:

* clearer level goals
* better visual progression
* more readable hazard/reward language
* stronger state feedback
* staged difficulty tuning if existing knobs are safe
* background/world evolution
* UI/HUD clarity
* theme-specific challenge framing

Avoid complexity through risky core rewrites.

### 4. Remix premise

Convert the user remix prompt into a coherent world premise.

The premise must be:

* recognizable
* visually generative
* compatible with the source mechanics
* able to support five levels
* able to produce procedural characters/items/props
* able to drive animated backgrounds and motion graphics

### 5. 1.5-level core definition

Define the smallest practical progression proof:

* Level 1: the base transformed experience
* Level 1.5: the first meaningful escalation or variation

This must explain how the game can show progression while staying within safe mechanics.

### 6. Five-level difficulty progression

Create five levels even if the source game does not currently expose five explicit levels.

If explicit levels already exist, preserve and reinterpret them semantically.

If explicit levels do not exist, define a conceptual five-level progression that downstream regeneration can implement through safe presentation, pacing, feedback, or existing progression hooks.

For each level, specify:

* level title
* player-facing goal
* difficulty intent
* safe mechanics knobs, if any
* protected mechanics to avoid touching
* hazard/reward interpretation
* UI/HUD messaging
* failure risk to watch
* visual progression beat

### 7. Five-level visual evolution

For each level, specify:

* animated background concept
* motion-graphic behavior
* procedural character/item/prop evolution
* color/lighting progression
* motif evolution
* HUD/theming progression
* how the scene changes in a way the player can recognize

The background must not be generic decoration. It must become an authored world layer that reacts to progress/state when safely possible.

### 8. Procedural art system plan

Define a reusable visual language:

* primary shapes
* motif vocabulary
* character silhouettes
* item silhouettes
* icon style
* background layers
* animation principles
* CSS/SVG/Canvas/DOM implementation preference
* safe fallback if external assets fail

### 9. Downstream regeneration contract

Write a compact contract for the later v6 regeneration stage.

Define:

* what this semantic stage established as mechanic truth and target identity
* what the super operator must rebuild from semantic abstraction alone
* what runtime surfaces are intentionally disposable
* what regeneration risks must be verified and repaired
* what canonical outputs must be freshly authored by the next stage

## Required semantic artifacts

Create or update planning artifacts where the harness supports them.

At minimum, the result text must clearly include:

* `mechanic_decomposition`
* `complexity_profile`
* `protected_mechanics`
* `safe_theming_surfaces`
* `remix_premise`
* `one_point_five_level_core`
* `five_level_difficulty_progression`
* `five_level_visual_evolution`
* `procedural_art_system`
* `downstream_stage_contract`

If writing JSON artifacts is feasible in the workspace, prefer a structured `remix_plan_v6.json` with the same sections.

## Required output files

### 1. `Blueprint.md`

Write an abstracted vision of the codebase, gameplay heuristic, and regeneration target.

Include:

* high-level code structure
* game loop / state model
* player goals
* interaction pattern
* core systems
* inferred genre/gameplay shape
* current identity summary
* remix-direction summary
* preserve-vs-transform guidance for downstream regeneration

This file must explicitly distinguish:

* current game reality
* intended remixed trajectory
* protected mechanics
* disposable runtime surfaces
* regeneration requirements

### 2. `Identity.json`

Write a structured JSON descriptor of the **intended remixed game**.

Include concise fields such as:

* title
* premise
* interaction_model
* objective
* progression
* theme
* mood
* likely_audience
* confidence_notes
* source_game_summary
* remix_prompt_interpretation
* preserve_elements
* transform_elements
* recreation_prompt

The `recreation_prompt` field must be a single user-facing natural-language prompt that would let someone recreate the **intended remixed game** in detail from scratch.

It should describe the target remixed game clearly enough for regeneration, including the gameplay loop, player goal, interaction style, presentation cues, progression shape, and important systems, while staying readable as one end-user-oriented prompt.

### 3. Mechanics ranking file

Create a machine-readable file ranking the top 5 best matches for the gameplay mechanics of the **intended remixed game** from the provided category universe.

Order the selected 5 from strongest match to weakest match.

The ranking should not merely reflect the current source game if the remix prompt clearly pushes the game toward a different interaction shape.

### 4. Companion classification file

Create a companion file that preserves the mechanics-match reasoning and scores.

Include:

* the selected top 5 categories
* a score/confidence for each selected category
* short reasoning for each selected category
* notes about whether each category is:

  * inherited from the source game
  * strengthened by the remix prompt
  * newly introduced by the remix direction
* uncertainty notes

### 5. Semantic tags file

Create a tags file with rich semantic gaming tags describing the **target remixed result** across:

* theme
* setting
* characters
* mechanics
* mood
* similar games
* similar franchises if useful
* visual identity direction
* interaction tone
* preserve tags
* transform tags

Franchise references are allowed here.

### 6. `RecreationPrompt.md`

Create a file named `RecreationPrompt.md`.

This file must contain:

* one polished user-facing natural-language prompt
* enough detail that another system could recreate the intended remixed game faithfully
* gameplay loop
* controls / interaction style
* progression
* tone / mood
* UI / presentation cues
* important constraints or signature mechanics
* explicit synthesis between source structure and remix direction

This prompt should read like a direct recreation brief for a single downstream user-facing generation step, not like internal notes.

### 7. `RemixDelta.md`

Create a file named `RemixDelta.md`.

This file should concisely explain:

* what the current game appears to be
* what the remix prompt is asking for
* what should stay stable
* what should shift
* what later regeneration should prioritize first
* what must not be overinterpreted
* what legacy runtime surfaces were intentionally demoted after semantic capture

### 8. `operator_result_contract.json`

Write a JSON file named `operator_result_contract.json` in the workspace.

Minimum successful shape:

```json
{
  "status": "ok",
  "detail": "Generated semantic regeneration artifacts and intentionally trashed legacy runtime surfaces so downstream v6 regeneration rebuilds from semantic abstraction.",
  "semantic_regeneration_ready": true,
  "trashed_runtime_surfaces": ["index.html", "assets/"]
}
```

Allowed `status` values:

* `ok`
* `warning`
* `error`

Use:

* `ok` when the semantic artifacts are coherent and any legacy runtime surfaces that existed were intentionally trashed for cleanup
* `warning` when the semantic artifacts are usable but one or more expected runtime surfaces were absent or only partially demoted
* `error` when the semantic artifacts are not reliable enough for downstream regeneration

If blocked, write:

```json
{
  "status": "error",
  "detail": "Could not generate the required remix-conditioned semantic inference outputs reliably.",
  "semantic_regeneration_ready": false,
  "trashed_runtime_surfaces": []
}
```

## Full category universe

Use this exact category universe when computing the top 5 mechanics matches:

* Block builder
* Bus simulator
* Car simulator
* Clicker game
* Dress up game
* Life simulator
* Neon runner
* Pet simulator
* Sniper game
* Sniper story game
* Streamer tycoon
* Survival game
* Zombie survival
* Battle royale
* Liquid sort puzzle
* Drawing puzzle game
* Alien shooter
* Quiz game
* Tycoon game
* Tower defense
* Space shooter
* Ludo board game
* Zombie shooter
* Void runner
* City builder
* Money clicker
* Parkour game
* Endless runner
* Supermarket simulator
* Rhythm music game
* Platformer game
* Money tycoon
* Cooking simulator
* Cooking game
* Merge game
* Sonic style runner
* Cash clicker
* Train runner game
* Word search puzzle
* Restaurant tycoon
* Farm simulator
* Bubble shooter
* Football quiz
* Block puzzle
* Airport tycoon
* Hotel tycoon
* Hospital simulator
* School simulator
* Police simulator
* Taxi simulator
* Match 3 puzzle
* Tile matching game
* Number puzzle
* Sudoku game
* Physics puzzle
* Cut the rope style puzzle
* First person shooter
* Third person shooter
* Arena fighting game
* Boss rush game
* Wave defense game
* Obby runner
* Speed runner
* Gravity runner
* Lane runner game
* Gacha collector
* Creature collector
* Card battle game
* Inventory building game
* Roleplay simulator
* Chat simulator
* Avatar world game
* Social hub game
* Base building game
* Resource management game
* RTS strategy game
* Idle strategy game
* Sandbox building game
* Level editor game
* World creator game
* Story choice game
* Interactive novel game
* Life choices simulator
* Football game
* Racing game
* Skateboarding game
* Basketball game
* ASMR relaxing game
* Satisfying simulator
* Destruction simulator
* Cleaning simulator
* AI companion game
* Creator economy simulator
* Streaming simulator
* Influencer simulator
* Time loop game
* Memory puzzle game
* Incremental story game
* Procedural exploration game
* Meta game

## Execution requirements

* Focus only on inference, remix interpretation, semantic planning, artifact generation, and destructive handoff.
* Do not perform runtime fixing or browser QA in this node.
* Keep outputs grounded in the actual code and observed structure of the game.
* Use the remix prompt as directional intent, not permission for fantasy unrelated to the source game.
* Be explicit when confidence is low.
* Ensure `Identity.json`, `RecreationPrompt.md`, `RemixDelta.md`, semantic tags, and `remix_plan_v6.json` are aligned around the same intended remixed result.
* Formulate outputs as a practical downstream regeneration blueprint, not vague creative brainstorming.
* Do not keep legacy runtime surfaces as canonical outputs.
* Do not generate playable runtime variants in this node.

## Destructive runtime-surface handoff rule

After the semantic artifacts are written, intentionally demote the original runtime surfaces so the next stage cannot depend on them.

If present in the current workspace:

1. rename `index.html` to `index_trash.html`
2. rename `assets/` to `assets_trash/`

If original or baseline screenshots are kept only temporarily and are intentionally non-canonical, rename each one to `*_trash.<ext>` so cleanup can remove it after success.

Important consequence:

* successful stage completion triggers runtime cleanup that deletes `*_trash.*` files and `*_trash/` directories before the next stage workspace is promoted
* this means the original `index.html`, original `assets/`, and any deliberately trashed baseline screenshots will be gone before the super operator starts
* this deletion is intentional

## Downstream expectation contract

The downstream super operator must assume:

* semantic artifacts are the source of truth
* mechanic truth is documented in artifacts, not preserved via legacy runtime files
* the original public runtime surface may already be removed
* any rebuilt `index.html` and any rebuilt assets must be freshly authored canonical outputs
* screenshots marked as trash are non-canonical and must not be used as dependency surfaces
* the final game must be rebuilt from the semantic plan, protected mechanics, remix premise, procedural art plan, and regeneration contract

## Completion standard

This stage is complete only when a later stage could implement the remix without guessing:

* what the mechanics are
* what not to touch
* what the five levels mean
* how the visuals evolve
* what procedural character/item/background system should exist
* what runtime risks must be watched
* what original runtime surfaces were intentionally demoted
* why the next stage must rebuild fresh canonical runtime surfaces from semantic artifacts

## Stdout contract

End stdout with exactly these lines:

```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|updated|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues
```
