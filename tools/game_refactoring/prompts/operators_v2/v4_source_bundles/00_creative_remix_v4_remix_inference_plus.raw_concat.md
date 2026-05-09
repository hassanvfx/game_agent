<!-- SOURCE: 00_creative_remix_v3_remix_inference.md -->
# Operator v2 Stage 00: Creative Remix V3 Remix Inference

Work only inside the provided workspace.

Your job is to analyze the current game and produce remix-conditioned inference artifacts before any downstream transformation pass.

You are not just documenting the current game.
You must interpret the existing codebase through the active remix prompt and formulate the intended remixed identity, tags, and future blueprint that later stages should converge toward.

## Core Role

This stage is the **remix-aware blueprint and tagging pass**.

It should:
- inspect the current code and current game structure
- infer the current gameplay and presentation shape
- read the remix prompt as the intended direction of change
- translate that remix prompt into grounded future-facing blueprint outputs
- formulate final tags and downstream guidance that describe the intended remixed result, not just the current source game

The outputs from this stage should help later stages understand:
- what the source game currently is
- what the remix prompt is asking it to become
- which mechanics/identity elements should be preserved
- which blueprint directions should shift

## Required output files

### 1. `Blueprint.md`
Write an abstracted vision of the codebase and the gameplay heuristic.

Include:
- high-level code structure
- game loop / state model
- player goals
- interaction pattern
- core systems
- inferred genre/gameplay shape
- current identity summary
- remix-direction summary
- preserve-vs-change guidance for downstream stages

This file should explicitly distinguish:
- current game reality
- intended remixed trajectory

### 2. `Identity.json`
Write a structured JSON descriptor of the **intended remixed game**.

Include concise fields such as:
- title
- premise
- interaction_model
- objective
- progression
- theme
- mood
- likely_audience
- confidence_notes
- source_game_summary
- remix_prompt_interpretation
- preserve_elements
- transform_elements
- recreation_prompt

The `recreation_prompt` field must be a single user-facing natural-language prompt that would let someone recreate the **intended remixed game** in detail from scratch.

It should describe the target remixed game clearly enough for regeneration, including the gameplay loop, player goal, interaction style, presentation cues, progression shape, and important systems, while staying readable as one end-user-oriented prompt.

### 3. mechanics ranking file
Create a machine-readable file ranking the top 5 best matches for the gameplay mechanics of the **intended remixed game** from the provided category universe.

Order the selected 5 from strongest match to weakest match.

The ranking should not merely reflect the current source game if the remix prompt clearly pushes the game toward a different interaction shape.

### 4. companion classification file
Create a companion file that preserves the mechanics-match reasoning and scores.

Include:
- the selected top 5 categories
- a score/confidence for each selected category
- short reasoning for each selected category
- notes about whether each category is:
  - inherited from the source game
  - strengthened by the remix prompt
  - newly introduced by the remix direction
- uncertainty notes

### 5. semantic tags file
Create a tags file with rich semantic gaming tags describing the **target remixed result** across:
- theme
- setting
- characters
- mechanics
- mood
- similar games
- similar franchises if useful
- visual identity direction
- interaction tone
- preserve tags
- transform tags

Franchise references are allowed here.

### 6. recreation prompt file
Create a file named `RecreationPrompt.md`.

This file must contain:
- one polished user-facing natural-language prompt
- enough detail that another system could recreate the intended remixed game faithfully
- gameplay loop
- controls / interaction style
- progression
- tone / mood
- UI / presentation cues
- important constraints or signature mechanics
- explicit synthesis between source structure and remix direction

This prompt should read like a direct recreation brief for a single downstream user-facing generation step, not like internal notes.

### 7. remix delta brief
Create a file named `RemixDelta.md`.

This file should concisely explain:
- what the current game appears to be
- what the remix prompt is asking for
- what should stay stable
- what should shift
- what later stages should prioritize first
- what must not be overinterpreted

## Full category universe

Use this exact category universe when computing the top 5 mechanics matches:

- Block builder
- Bus simulator
- Car simulator
- Clicker game
- Dress up game
- Life simulator
- Neon runner
- Pet simulator
- Sniper game
- Sniper story game
- Streamer tycoon
- Survival game
- Zombie survival
- Battle royale
- Liquid sort puzzle
- Drawing puzzle game
- Alien shooter
- Quiz game
- Tycoon game
- Tower defense
- Space shooter
- Ludo board game
- Zombie shooter
- Void runner
- City builder
- Money clicker
- Parkour game
- Endless runner
- Supermarket simulator
- Rhythm music game
- Platformer game
- Money tycoon
- Cooking simulator
- Cooking game
- Merge game
- Sonic style runner
- Cash clicker
- Train runner game
- Word search puzzle
- Restaurant tycoon
- Farm simulator
- Bubble shooter
- Football quiz
- Block puzzle
- Airport tycoon
- Hotel tycoon
- Hospital simulator
- School simulator
- Police simulator
- Taxi simulator
- Match 3 puzzle
- Tile matching game
- Number puzzle
- Sudoku game
- Physics puzzle
- Cut the rope style puzzle
- First person shooter
- Third person shooter
- Arena fighting game
- Boss rush game
- Wave defense game
- Obby runner
- Speed runner
- Gravity runner
- Lane runner game
- Gacha collector
- Creature collector
- Card battle game
- Inventory building game
- Roleplay simulator
- Chat simulator
- Avatar world game
- Social hub game
- Base building game
- Resource management game
- RTS strategy game
- Idle strategy game
- Sandbox building game
- Level editor game
- World creator game
- Story choice game
- Interactive novel game
- Life choices simulator
- Football game
- Racing game
- Skateboarding game
- Basketball game
- ASMR relaxing game
- Satisfying simulator
- Destruction simulator
- Cleaning simulator
- AI companion game
- Creator economy simulator
- Streaming simulator
- Influencer simulator
- Time loop game
- Memory puzzle game
- Incremental story game
- Procedural exploration game
- Meta game

## Requirements

- Focus only on inference, remix interpretation, and output generation.
- Do not perform runtime fixing or browser QA in this node.
- Keep outputs grounded in the actual code and observed structure of the game.
- Use the remix prompt as directional intent, not permission for fantasy unrelated to the source game.
- Be explicit when confidence is low.
- Ensure `Identity.json`, `RecreationPrompt.md`, `RemixDelta.md`, and semantic tags are aligned around the same intended remixed result.
- Formulate outputs as a practical downstream blueprint, not vague creative brainstorming.

## Required contract artifact

Write a JSON file named `operator_result_contract.json` in the workspace.

If successful, write:

```json
{
  "status": "ok",
  "detail": "Generated remix-aware blueprint, identity, mechanics ranking, semantic tags, recreation prompt, and remix delta guidance."
}
```

## If blocked

If you cannot generate the required remix-conditioned inference outputs reliably, write:

```json
{
  "status": "error",
  "detail": "Could not generate the required remix-conditioned inference outputs reliably."
}
```

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
<!-- END SOURCE: 00_creative_remix_v3_remix_inference.md -->

<!-- SOURCE: 10_creative_remix_v3_level_adapter.md -->
# Operator v2 Stage 10: Creative Remix V3 Level Adapter

You are the level adaptation operator for the `creative_remix_v3` workflow.

Work only inside the provided workspace.

## Mission

Create a controlled five-level variant set **after** the final repaired canonical game already exists.

This is a post-stabilization stage.

Your job is **not** to redesign the game again.
Your job is to:
- study the stabilized final game deeply
- decompose what actually creates challenge
- use progressive disclosure to build a clean additive difficulty ladder
- generate five derived level variants from simplest to most demanding
- preserve the repaired canonical `index.html` as the main stable surface

## Core Rule

`index.html` remains the canonical final repaired version.

You must derive:

- `index_level_01.html`
- `index_level_02.html`
- `index_level_03.html`
- `index_level_04.html`
- `index_level_05.html`

Do not replace `index.html` with a level variant.

## Optional Workflow Artifacts (Use If Present)

These are optional reference artifacts created by earlier or adjacent stages.

Use them when present to stay aligned.
Do not fail just because some are missing unless your current stage is explicitly responsible for creating them.

### From `remix_inference`
- `Blueprint.md`
- `Identity.json`
- `RecreationPrompt.md`
- `RemixDelta.md`

### From `narrative_refine`
- any copy/layout wording refinements present in the repaired game

### From `visuals_refine`
- `visuals_refine_state_machine.md`
- `screens_01`, `screens_02`, etc. if present
- screenshots / captured screen references if present

### From `optional_config_refactor`
- `asset_slot_bounding_boxes.md`
- `optional_config_usage.md`

### From `final_mobile_repair`
- the stabilized repaired `index.html`
- any local repair comments or flow-preservation notes if present

## High-Level Goal

You must not jump directly into “harder = more stuff.”

First determine:
- what the player is trying to do
- what the irreducible core loop is
- what actually creates difficulty
- which complexity dimensions are real versus superficial
- how to introduce those dimensions progressively and clearly

Then build the level ladder.

## Level Start Rule

There is no separate demo / attract screen in this version of the multilevel design.

The family should stay simple:
- `index.html` remains the canonical repaired surface
- `index_level_01.html` through `index_level_05.html` are the only derived playable variants

Do not introduce:
- attract-mode routing layers
- autoplay-only intermediary shells
- separate title-card wrappers around the actual level files

Each level should open directly into its own intended playable form.
If a lightweight intro or CTA is still necessary inside a specific level, keep it minimal and local to that file rather than introducing a separate demo surface.

## Build Order Diagram (Required Mental Model)

Use this exact construction mindset:

```text
STEP 0 — CANONICAL
+----------------------------------+
| index.html                       |
| stable repaired canonical game   |
| may still contain intro surface  |
+----------------------------------+
                |
                v
STEP 1 — FIRST PLAYABLE LEVEL
+----------------------------------+
| copy index.html                  |
| -> index_level_01.html           |
+----------------------------------+
                |
                v
+----------------------------------+
| strip intro/tutorial duplication |
| keep direct playable form        |
| simplify to easiest real level   |
+----------------------------------+
                |
                v
STEP 2 — DELTA ANALYSIS
+----------------------------------+
| compare:                         |
| index.html                       |
| vs                               |
| index_level_01.html              |
+----------------------------------+
                |
                v
+----------------------------------+
| identify what intro/welcome      |
| layer was removed                |
| identify what stays as gameplay  |
+----------------------------------+
                |
                v
STEP 3 — LEVEL LADDER
+----------------------------------+
| index_level_01.html              |
| easiest direct-play form         |
+----------------------------------+
                |
                v
+----------------------------------+
| clone level 01 -> level 02       |
| add one new demand               |
+----------------------------------+
                |
                v
+----------------------------------+
| clone level 02 -> level 03       |
| full intended stack              |
+----------------------------------+
                |
                v
+----------------------------------+
| clone level 03 -> level 04       |
| same stack under more pressure   |
+----------------------------------+
                |
                v
+----------------------------------+
| clone level 04 -> level 05       |
| near max readable pressure       |
+----------------------------------+
```

The active family shape is simply:

```text
index.html                canonical repaired baseline
index_level_01.html       easiest playable variant
index_level_02.html       additive step 2
index_level_03.html       full intended stack
index_level_04.html       higher pressure
index_level_05.html       upper readable pressure
```

Do not improvise a different pipeline shape unless the current game absolutely forces it.

## Progressive Disclosure Rule (Nintendo-Style)

Use progressive disclosure and additive teaching.

The intended shape is:

- **Level 1**: simplest playable expression of the game
- **Level 2**: add one new demand on top of level 1
- **Level 3**: combine the essential stack into the “full intended form”
- **Level 4**: same essential stack, but under more pressure
- **Level 5**: same essential stack near the upper readable limit

This is **not**:
- easy / medium / hard by random numeric scaling
- clutter escalation for its own sake
- adding unrelated mechanics to simulate depth

This **is**:
- one
- one plus two
- one plus two plus three
- same stack under greater pressure
- full stack near readable overload

## World Identity Across Levels

The five levels should not feel like the same screen with only numeric tuning changes.

Treat the ladder more like a Mario-style world progression:
- five distinct worlds
- one shared metaverse
- one shared gameplay identity
- one shared narrative thread

Each level must be immediately identifiable at a glance as its own world while still clearly belonging to the same game family.

Preserve continuity through:
- the same focal character or core play identity
- the same UI language
- the same motif family
- the same underlying shape logic
- the same metaverse narrative arc

Differentiate worlds through controlled changes such as:
- background scene composition
- skyline / terrain / architecture cues
- palette family
- atmospheric animation
- particles / weather / energy style
- environmental storytelling details
- the visible stage of the metaverse journey

Do not make levels feel disconnected, randomly re-skinned, or like unrelated games.

## Visual Evolution Across Levels

In addition to mechanical progression, define a visual progression across levels.

The animated background and scene framing should help convey:
- evolving time
- evolving stakes
- evolving world state
- evolving storyline across the metaverse narrative

Examples of safe visual evolution include:
- time-of-day drift
- palette pressure or tonal shift
- stronger ambient motion
- increased particle density
- environmental transformation
- growing corruption, energy, weather, ruin, bloom, or calm
- clearer signs that the player is traveling through distinct but related worlds

Visual evolution must:
- remain secondary to gameplay readability
- remain subordinate to interactives, hazards, targets, HUD, and controls
- never imply new mechanics by itself
- never become clutter for its own sake
- preserve the authored world established by the repaired canonical game
- continue the same authored world family rather than falling back to cheap stock scene ownership in later levels

If a cheap stock/static image background still owns the playfield, that does not count as level evolution.
Levels should evolve the authored world, not preserve a generic placeholder scene while adding atmospheric garnish around it.

The goal is not just “harder levels.”
The goal is a five-world journey where gameplay complexity and world identity evolve together.

## Required Artifact 1: Mechanics Complexity Decomposition

Create:

`mechanics_complexity_decomposition.md`

This file must answer:

- what is the player’s objective?
- what is the irreducible core action?
- what is the minimum playable loop?
- what information must the player track?
- what causes failure?
- what creates pressure?
- what creates fake difficulty versus real difficulty?
- what adds noise rather than meaningful depth?

Then explicitly separate the game’s challenge into dimensions such as:

- input complexity
- timing complexity
- spatial complexity
- target-selection complexity
- resource-management complexity
- multitasking complexity
- visual parsing complexity
- punishment severity
- recovery generosity

If some dimensions do not apply, say so clearly.

## Required Artifact 2: Progressive Disclosure Plan

Create:

`progressive_disclosure_plan.md`

This file must explain, level by level:

- what is being taught
- what is being withheld
- what is being added
- what remains constant
- what visual world identity defines that level
- how the background or scene framing evolves the metaverse storyline
- what visual elements stay continuous across all five levels
- why the next level is a sensible additive step mechanically and visually

This should read like an intentional learning/pressure curve and world journey, not arbitrary tuning notes.

## Required Artifact 3: Level Adapter Rationale

Create:

`level_adapter_rationale.md`

This file must explain:

- why the chosen five-level structure fits this specific game
- which complexity dimensions are used for escalation
- which dimensions are intentionally *not* used
- how the ladder avoids random clutter
- how the five levels become visually unique worlds within one metaverse family
- how background/scene evolution supports storyline and world progression without implying new mechanics
- how mobile readability and control safety are preserved
- why level 5 is still readable enough to be meaningful rather than just broken

## External Script Compatibility Rule

You may update external JS files used by the repaired canonical surface if needed to support:
- `index_level_01.html`
- `index_level_02.html`
- `index_level_03.html`
- `index_level_04.html`
- `index_level_05.html`

But if you do:
- keep the canonical `index.html` working
- preserve backward compatibility across all derived level files
- avoid one-off script forks unless absolutely necessary
- prefer shared logic with clearly branched safe behavior
- do not break controls, routing, or mobile actionability in any variant

## Required Artifact 4: Five Derived Level Files

Create:

- `index_level_01.html`
- `index_level_02.html`
- `index_level_03.html`
- `index_level_04.html`
- `index_level_05.html`

These should be derived from the repaired canonical `index.html`.

If additional local JS/CSS files are used by the canonical surface, adapt them only as needed and keep the level files understandable.

Remove redundant intro/tutorial layers from levels 1–5 when safe.
Level variants should open more directly into their playable form rather than repeating the same welcome/instruction surface.

## Difficulty Construction Rules

You may escalate using only the dimensions that are actually real in the current game.

Valid escalation axes may include:
- amount
- speed
- timing pressure
- spacing
- composition
- target ambiguity
- recovery windows
- resource scarcity
- screen-state congestion
- simultaneous task count

Do not assume all of these exist.
Use only what the current game genuinely supports.

## What Not To Do

Do NOT:
- invent mechanics just because a later level feels empty
- add unrelated systems for novelty
- confuse visual clutter with mechanical depth
- make level 4/5 unreadable by brute-force density
- break controls
- break mobile actionability
- let derived levels become less stable than the repaired canonical surface without explicitly documenting the tradeoff
- introduce an unnecessary demo / attract wrapper instead of keeping the level family direct and playable

## Mobile Safety Rule

All derived levels must remain mobile-first.

That means:
- controls remain reachable
- essential CTA/action zones remain visible
- no control trapping
- no impossible thumb-zone demands unless the base game already relies on them
- increased difficulty must come from smarter pressure, not broken usability

If a harder level would only be “harder” because it becomes hard to physically operate on mobile, reject that design.

## Variant Construction Strategy

Prefer:
- cloning the repaired canonical surface first
- making the smallest changes necessary per level
- keeping each level variant explainable
- keeping diffs conceptually meaningful

Each level should feel like an intentional member of the same family.

## Example Additive Pattern

If the game is an avoidance/collection game, the ladder might look like:

- level 1: one objective + one obvious threat lane
- level 2: same objective + one added hazard interaction
- level 3: full intended objective/hazard relationship
- level 4: same loop with denser timing and spacing pressure
- level 5: same loop with maximum readable pressure

If the game is not that type, adapt the logic accordingly.

## Required Screenshot Capture

Capture real mobile screenshots for the derived family and leave them in the workspace as evidence for this stage.

If browser/runtime validation is required for this stage:
- use only the assigned validation localhost URL/port from the runtime contract header
- do not choose another localhost port
- do not attach to another local server
- write screenshots only inside the current attempt workspace

At minimum capture:
- `screens_index_canonical.png`
- `screens_level_01.png`
- `screens_level_02.png`
- `screens_level_03.png`
- `screens_level_04.png`
- `screens_level_05.png`

Rules:
- use real captured screenshots, not text-only substitutions
- screenshots should reflect the actual derived files produced by this stage
- if a level has a notable modal/menu/terminal state that clarifies behavior, capture additional screenshots as needed
- treat missing family screenshots as an incomplete `level_adapter` pass, not an optional nice-to-have

## Required Interaction Flow Simulation

Create:

`level_flow_validation.md`

This file must mentally simulate clicking every active button and validating every important interaction path in:

- `index.html`
- `index_level_01.html`
- `index_level_02.html`
- `index_level_03.html`
- `index_level_04.html`
- `index_level_05.html`

At minimum validate:
- start game
- open menu
- close menu
- pause
- resume
- restart
- continue
- modal confirm
- modal dismiss

If a path is hidden, clipped, trapped, broken, or inconsistent, fix it before finishing.

## Conservative End-of-Stage Recheck

This stage must end conservatively.

Before finishing, run a second mental pass across:
- `index.html`
- `index_level_01.html`
- `index_level_02.html`
- `index_level_03.html`
- `index_level_04.html`
- `index_level_05.html`

During this final recheck:
- prefer reverting risky changes over preserving clever ones
- verify each level still boots and enters play
- verify no new bug was introduced while differentiating later levels
- verify the canonical surface was not degraded indirectly by shared JS/CSS changes
- verify the easiest level is still the cleanest and most stable one
- verify harder levels are harder because of real pressure, not because of broken usability
- if unsure about a late-stage flourish, remove it

This is a conservative variant-construction pass, not a feature-expansion pass.

## Final Preservation Rule

The repaired canonical `index.html` is the most important surface.

If you are unsure:
- leave `index.html` alone
- create the variants conservatively
- document what you chose and why

## Required Output Artifacts Summary

At minimum create:

- `mechanics_complexity_decomposition.md`
- `progressive_disclosure_plan.md`
- `level_adapter_rationale.md`
- `index_level_01.html`
- `index_level_02.html`
- `index_level_03.html`
- `index_level_04.html`
- `index_level_05.html`
- `operator_result_contract.json`

## Output Requirements

Write a JSON file named `operator_result_contract.json` in the workspace.

Minimum required shape:
```json
{
  "status": "ok",
  "detail": "Created a five-level post-repair variant ladder using mechanics decomposition and progressive disclosure, with validation scoped to the assigned runtime contract."
}
```

Allowed `status` values:
- `ok`
- `warning`
- `error`

Use:
- `ok` when the five-level ladder is coherent, additive, mobile-safe, and grounded in real mechanics
- `warning` when only partial level differentiation was safely possible
- `error` when you could not safely derive the five level variants

End stdout with exactly these lines:
```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|adapted|issues
VISUAL CHECK: preserved|adapted|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|issues
<!-- END SOURCE: 10_creative_remix_v3_level_adapter.md -->
