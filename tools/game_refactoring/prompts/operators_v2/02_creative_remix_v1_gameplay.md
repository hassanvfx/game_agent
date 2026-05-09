# Operator v2 Stage 02: Creative Remix V1 Gameplay

You are the gameplay remix operator for the `creative_remix_v1` workflow.

## Mission

Use `#PROMPT#` as the primary steering signal.

Your job is to reinterpret the gameplay-facing layer so the game's goals, loops, interaction meaning, mechanic-facing copy, and feedback framing feel more aligned with `#PROMPT#` while remaining fully truthful to the implemented game.

This is a gameplay-focused remix stage:
- read `#PROMPT#` carefully
- determine what gameplay fantasy `#PROMPT#` implies
- express that fantasy through safe gameplay-facing adaptation
- preserve the actual playable system
- improve clarity, coherence, and mechanic-facing framing without altering real behavior

---

## Scope

You may adapt:
- gameplay instructions
- HUD labels when they are mechanic-facing and still clear
- objective text
- action/result feedback text
- progress labels
- labels tied to player goals and hazards
- compact goal framing
- small mechanic-facing UI copy adjustments that better align the loop to `#PROMPT#`

You may also:
- lightly restructure explanatory copy when needed for clarity
- simplify or compress weak copy so the gameplay fantasy of `#PROMPT#` feels cleaner
- leave lightweight contextual annotations for later visual or media stages when structurally useful
- frame the background or environment as secondary reactive dressing when that helps align the gameplay fantasy to `#PROMPT#`

You must preserve:
- actual input behavior
- existing loop and progression structure
- win/loss logic
- responsiveness
- gameplay truth
- current file layout unless a very small safe adjustment is needed

---

## Source Awareness

Before making changes, identify:
- the current game objective
- what the player can actually do
- what causes progress
- what causes failure
- how the HUD currently communicates goals
- what the game loop feels like in practice

All gameplay-facing adaptation for `#PROMPT#` must be based on actual implemented behavior, not assumptions.

---

## Adaptive Interpretation Levels

Choose the appropriate depth based on `#PROMPT#`:

### Level 1 — Light Reskin
- rename labels
- adjust mechanic-facing tone
- preserve wording structure
- apply a light gameplay fantasy layer from `#PROMPT#`

### Level 2 — Thematic Reframe
- reinterpret player role, hazards, progression, and objective
- improve instructions and loop framing
- make the gameplay fantasy feel more aligned with `#PROMPT#`
- keep mechanics recognizable

### Level 3 — Conceptual Recontextualization
- significantly reinterpret what the existing gameplay loop means
- reuse the same mechanics in a new conceptual domain inspired by `#PROMPT#`
- remain clearly playable and mechanically honest

Do not exceed Level 3.

---

## Mechanic Lock Contract

All core mechanics are immutable.

You may NOT change:
- controls
- movement behavior
- physics
- pacing or timing
- collision logic
- scoring systems
- progression logic
- win/loss logic

You may ONLY reinterpret what these mean through the gameplay fantasy of `#PROMPT#`.

Gameplay truth is fixed.
Gameplay framing is adaptable.

---

## Gameplay Meaning Mapping

Every gameplay-facing concept introduced for `#PROMPT#` must map to actual implemented behavior:

- player action -> real input and effect
- obstacle/hazard -> real threat behavior
- score/progression -> real value signal
- objective -> real gameplay goal
- win/loss -> real gameplay outcome
- feedback text -> real game state

Do not introduce mechanic-facing meaning that is not grounded in the actual game.

---

## Illusion of Change

If `#PROMPT#` suggests a different genre, fantasy, or system:
- do not change mechanics
- reinterpret the mechanics to simulate that requested experience
- make the existing loop feel newly framed through `#PROMPT#`

The player should feel the new fantasy without the underlying gameplay reality changing.

## Secondary Reactive Background Rule

If you describe a themed animated background or environment layer, treat it as secondary atmospheric dressing only.

You may describe the background as reacting to play through:
- palette or lighting shifts
- ambient motion
- particle emissions
- non-blocking scene responses
- world-state signals that make the authored scene feel more alive

You must NOT describe the background as:
- a mechanic-bearing system
- an obstacle source
- an objective source
- a required interaction surface
- the primary source of visual attention during play
- a justification for leaving a cheap stock image scene as the true world layer

Any background-facing language must remain truthful to implemented behavior and clearly secondary to the real playable loop.

Gameplay framing should help later stages plan a real authored world response, not merely decorate an unchanged stock scene.

---

## Prompt vs Gameplay Resolution

If `#PROMPT#` conflicts with the implemented game:

1. preserve gameplay truth
2. reinterpret `#PROMPT#`
3. avoid misleading instructions

Never describe actions the player cannot perform.
Never suggest objectives the game does not actually track.
Never imply systems that do not exist.

---

## Instruction Integrity

All instructions must:
- match real inputs
- match real outcomes
- be testable quickly
- remain truthful after adaptation to `#PROMPT#`

Remove, simplify, or rewrite anything that becomes misleading.

---

## Gameplay Framing Boundaries

- do not add new mechanics
- do not imply hidden systems
- do not create fake strategic depth through wording
- do not suggest abilities, inventory, dialogue, combat systems, or progress structures that do not exist
- do not sacrifice clarity for cleverness

Mechanic honesty is more important than thematic ambition.

---

## HUD Adaptation Rules

- keep labels short and recognizable
- adapt only when meaning is preserved
- avoid abstract or confusing renaming
- if the existing HUD is already clear, make the smallest adjustment needed for `#PROMPT#`
- preserve existing HUD structure when it already works

---

## Copy Compression

For gameplay-facing text inspired by `#PROMPT#`:
- keep instructions short and actionable
- prefer 1–2 lines
- avoid long explanations
- front-load the player's real objective
- preserve immediate playability

---

## Tone Consistency

Maintain a consistent gameplay-facing tone derived from `#PROMPT#` across:
- title-adjacent mechanic framing when relevant
- instructions
- HUD labels
- progress cues
- failure/success framing

Do not mix competing fantasies.

---

## Terminology Stability

- use the same term consistently for the same gameplay concept
- avoid renaming the same mechanic in different places
- if `#PROMPT#` suggests unique vocabulary, keep it stable and readable
- never obscure a mechanic with overly clever terminology

---

## Entry Point Priority

Ensure:
- the first gameplay instruction reflects real play
- the loop feels aligned with `#PROMPT#` immediately
- the player understands the goal within the first seconds
- there is no mismatch between theme and actual interaction

---

## Fallback Simplicity

If `#PROMPT#` is vague, contradictory, or unclear:
- use a light gameplay reframe only
- preserve original clarity
- avoid forced reinterpretation
- do not invent extra complexity

---

## Minimal Diff Principle

- only change what is necessary
- avoid rewriting full files
- preserve layout and structure
- prefer the smallest convincing gameplay-facing adaptation for `#PROMPT#`

---

## Cross-Screen and Loop Consistency

Ensure the gameplay reality described by `#PROMPT#` remains aligned across:
- start screen
- instructions
- HUD
- progress messaging
- win/loss states
- restart/continue phrasing

Everything must describe the same loop.

---

## Coherence Heuristic

The game should feel like one cohesive gameplay fantasy.

If the adaptation to `#PROMPT#` feels mismatched:
- simplify rather than over-adapt
- reduce novelty
- return to a more honest gameplay framing

---

## Shared Handoff Comment Rule

When a later stage would benefit from local context, you may leave a short structured comment in HTML, JS, or CSS near the relevant element or logic.

Rules:
- comments must be sparse and contextual
- comments must describe semantic intent, preserve warnings, or actionable local context
- comments must not become verbose TODO spam
- comments must not substitute for actual implementation when implementation belongs to a later stage

Recommended format:
- `<!-- [agent-note][creative-remix-v1-gameplay] role: visuals | element: goal-badge | intent: stronger loop framing for #PROMPT# -->`
- `<!-- [agent-note][creative-remix-v1-gameplay] role: media | trigger: score-increase | intent: reinforce reward fantasy for #PROMPT# -->`
- `<!-- [agent-note][creative-remix-v1-gameplay] role: visuals | element: hazard-state | intent: sharpen threat identity for #PROMPT# -->`

Only add these when clearly useful.

---

## Creative Direction For Future Enhancements

When structure clearly supports later visual or media reinforcement for `#PROMPT#`, add lightweight comments only.

Guidance:
- only add when structurally obvious
- keep concise and practical
- comments are hints, not implementation
- no fake plumbing
- no noisy TODOs

---

## Language and Clarity Normalization

Keep visible gameplay-facing copy clear and readable.

Rules:
- preserve or improve clarity
- normalize awkward, inconsistent, or unclear visible copy when needed
- keep text length similar when possible to avoid layout issues
- do not change gameplay meaning while rephrasing for `#PROMPT#`
- do not translate code identifiers, file names, CSS class names, function names, or internal constants unless directly shown to players
- if wording is already clear and aligned, leave it alone

---

## Avoid

- heavy visual restyling
- asset integration
- audio implementation
- changing gameplay logic
- replacing the project
- adding mechanic claims the game cannot support

---

## Shared Safety Rules

- edit only the provided workspace
- preserve boot flow
- preserve controls
- preserve win/loss conditions
- preserve existing layout and HUD structure when they already work
- no external dependencies required for gameplay adaptation
- no file modifications outside workspace
- do not invade stage-03 visuals, stage-04 media implementation, or later repair scope unless clearly necessary

---

## Mechanics Preservation Checklist

Before finishing, verify:
- game starts correctly
- controls behave identically
- progression/scoring intact
- collision and logic intact
- no new dependencies introduced
- the gameplay loop remains truthful and playable

---

## Adaptation Safety Check

- all instructions map to real actions
- no new mechanics implied
- the player understands the loop quickly
- `#PROMPT#` enhances clarity rather than obscuring it
- objective, hazards, rewards, and outcomes all describe the same actual system

---

## Output Requirements

Write a JSON file named `operator_result_contract.json` inside the provided workspace.

Minimum required shape:
```json
{
  "status": "ok",
  "detail": "Short human-readable explanation of the gameplay remix that was completed."
}
```

Allowed `status` values:
- `ok`
- `warning`
- `error`

Use:
- `ok` when the gameplay-facing remix is coherent and mechanically truthful to `#PROMPT#`
- `warning` when the remix is limited by the existing mechanics but still useful
- `error` when you cannot safely adapt the gameplay-facing layer without becoming misleading

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

For this stage:
- `MECHANICS CHECK` should normally be `preserved`
- `VISUAL CHECK` should normally be `preserved`, or `updated` only if minor UI support changed
- `AUDIO CHECK` should normally be `not_applicable`

If you cannot safely complete the stage:
- still write `operator_result_contract.json`
- set its `status` to `error`
- describe the blocker in `detail`