# Node 2: Specimen Inference Outputs

Work only inside the provided workspace.

This node assumes node 1 already completed runtime QA and basic playability fixing.

Your job is to analyze the stabilized game and produce the following inference artifacts.

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

### 2. `Identity.json`
Write a structured JSON descriptor of the game.

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

### 3. category ranking file
Create a file that ranks the top 5 best matches from the following category list, ordered from strongest match to weakest match among the selected 5:

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

Use a clear machine-readable format.

### 4. semantic tags file
Create a tags file with rich semantic gaming tags describing:
- theme
- setting
- characters
- mechanics
- mood
- similar games
- similar franchises if useful

Franchise references are allowed here.

## Requirements

- Do not perform another runtime-fix pass in this node.
- Focus only on inference and output generation.
- Keep outputs grounded in the actual code and observed game behavior.
- Be explicit when confidence is low.

## Required contract artifact

Write a JSON file named `operator_result_contract.json` in the workspace.

If successful, write:

```json
{
  "status": "ok",
  "detail": "Generated Blueprint.md, Identity.json, top-5 category ranking, and semantic tags from the stabilized game."
}
```

## If blocked

If you cannot generate the required inference outputs reliably, write:

```json
{
  "status": "error",
  "detail": "Could not generate the required inference outputs reliably."
}
```

## Stdout contract

End stdout with exactly these lines:

```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues
```
