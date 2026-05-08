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