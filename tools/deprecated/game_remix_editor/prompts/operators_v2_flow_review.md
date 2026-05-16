# Operator v2 Logical Flow Review

## Purpose
Review the logical flow of `operators_v2`, trace the instruction vectors between stages, and define how to merge and tighten the pipeline without breaking the external rails interface.

## External Rails Constraint
The merge strategy should preserve the existing external interface.

Do not change:
- file names
- stage count
- stage order
- runner assumptions
- output footer formats
- workspace-first editing model

All improvements should come from:
- tighter internal scope boundaries
- clearer precedence rules
- comment-based handoffs inside editable HTML / JS / CSS
- stronger mobile-first preservation rules

## High-Level Interpretation
`operators_v2` is a staged transformation pipeline with four distinct operator roles:

1. Stage 01 — reinterpret meaning without changing mechanics
2. Stage 02 — redesign presentation without changing mechanics and without disturbing already-mobile-safe HUD composition
3. Stage 03 — map and wire approved media without changing mechanics
4. Stage 04 — passively repair only what is broken, unsafe, hidden, blocked, or non-functional

The system follows a descending intervention model:

- Stage 01 changes meaning
- Stage 02 changes appearance
- Stage 03 changes media plumbing
- Stage 04 changes only clear defects

That means creative freedom is strongest early and narrows as the pipeline progresses.

---

## ASCII Diagram — Pipeline Flow

```text
USER PROMPT
   |
   v
+---------------------------+
| INPUT GAME / WORKSPACE    |
| existing mechanics truth  |
| existing UI/layout truth  |
+---------------------------+
   |
   v
+--------------------------------------------------------------+
| STAGE 01: GAMEPLAY + NARRATIVE ADAPTATION                    |
|--------------------------------------------------------------|
| Owns:                                                        |
| - title, framing, story, labels, instructions                |
| - prompt reinterpretation into gameplay reality              |
| - mechanic -> narrative mapping                              |
| - lightweight future-media annotations                       |
| Must preserve: mechanics, controls, pacing, layout truth     |
| Output: semantic layer + media hint comments                 |
+--------------------------------------------------------------+
   |
   | semantic vector:
   | title / copy / framing / mechanic meaning
   |
   | hint vector:
   | future audio / gif / emoji / illustration comments
   v
+--------------------------------------------------------------+
| STAGE 02: VISUAL / CHARACTER-FIRST IDENTITY                  |
|--------------------------------------------------------------|
| Owns:                                                        |
| - character-first visual redesign                            |
| - UI clarity, style cohesion, presentation polish            |
| - mobile-first visual adaptation                             |
| Must preserve: gameplay, stage-01 meaning, HUD composition   |
| Output: stronger visual system, layout kept close if stable  |
+--------------------------------------------------------------+
   |
   | presentation vector:
   | palette / character emphasis / visual system
   | compact readable styling / preserved HUD composition
   v
+--------------------------------------------------------------+
| STAGE 03: MEDIA MAPPER                                       |
|--------------------------------------------------------------|
| Owns:                                                        |
| - audio mapping                                              |
| - GIF mapping                                                |
| - font mapping                                               |
| - import plumbing / asset wiring                             |
| Must preserve: mechanics + prior stage intent                |
| Output: actual media-backed runtime enrichment               |
+--------------------------------------------------------------+
   |
   | media vector:
   | stage-01 hints + stage-02 style -> wired media choices
   | SFX / BGM / GIF / font behavior
   v
+--------------------------------------------------------------+
| STAGE 04: FINAL CODE / UI / MOBILE REPAIR                    |
|--------------------------------------------------------------|
| Owns:                                                        |
| - runtime fixes                                              |
| - broken import/asset/font fixes                             |
| - overlap/readability/mobile safety repairs                  |
| - actionability verification via mental simulation           |
| Must preserve: all prior intended behavior                   |
| Output: stabilized, actionable, mobile-safe final build      |
+--------------------------------------------------------------+
   |
   v
+---------------------------+
| FINAL OPERATOR OUTPUT     |
| mechanics preserved       |
| UI actionable             |
| mobile-safe if possible   |
| coherent, wired, repaired |
+---------------------------+
```

---

## Instruction Vectors

### 1. Meaning Vector
Owned by Stage 01.

```text
prompt
-> inspect real mechanics
-> reinterpret only through implemented behavior
-> adapt title / instructions / HUD / outcomes
-> keep text short, testable, and truthful
```

This is the semantic truth layer for the rest of the pipeline.

### 2. Creative Hint Vector
Also seeded by Stage 01.

```text
implemented gameplay moment
-> identify meaningful future media opportunities
-> leave lightweight comments only
-> do not wire media yet
```

Examples:
- future-audio for collection, hit, fail, win
- future-gif for celebration, fail reaction, pause state
- future-emoji or illustration direction for identity accents

### 3. Identity Vector
Owned by Stage 02.

```text
stage-01 meaning
-> character/world/UI styling
-> palette / typography / visual language
-> readability and mobile-safe polish
```

This stage should produce strong originality through presentation while preserving stable HUD composition when it is already mobile-optimized.

### 4. Media Vector
Owned by Stage 03.

```text
stage-01 hint comments
+ stage-02 visual system
+ approved catalogs
-> actual audio / gif / font choices
-> actual runtime wiring
```

This is the implementation-heavy enrichment stage.

### 5. Actionability Repair Vector
Owned by Stage 04.

```text
prior staged result
-> mentally simulate user flow
-> check visibility / reachability / trigger actionability
-> minimally repair only clear failures
```

This is not a redesign pass. It is a passive safety and usability repair pass.

---

## Recommended Merge Model Without Breaking External Rails

### Keep the external rails stable
Do not alter:
- prompt file names
- number of stages
- output schemas
- runner-stage contract shape

### Merge internally by narrowing authority
- Stage 01 = meaning + future-media annotations only
- Stage 02 = visual identity + readability polish, but preserve HUD composition and layout if already mobile-safe
- Stage 03 = actual media/font wiring and approved catalog use
- Stage 04 = passive actionability/mobile/runtime repair only

### Universal override
Across all stages:
- no gameplay changes
- mobile first
- preserve working layout if already safe
- compact readable UI over decorative bulk
- do not invade another stage’s scope without a clear reason

---

## Stage-Specific Tightening Recommendations

### Stage 01
Keep:
- narrative adaptation
- English UI normalization
- future-media comments

Tighten:
- comments should be lightweight and structurally useful
- no actual asset/media plumbing
- no heavy visual direction that belongs to stage 02

Recommended role:
```text
semantic adaptation + hint seeding
```

### Stage 02
Keep:
- strong visual identity
- character-first design
- UI readability upgrades
- mobile-first thinking

Tighten:
- do not recompose HUD if it is already mobile-optimized
- preserve existing HUD hierarchy and geometry where practical
- restyle rather than rearrange unless there is a clear issue
- avoid visual expansion that reduces gameplay area

Recommended role:
```text
visual originality with layout restraint
```

### Stage 03
Keep:
- real media integration
- catalog authority
- audio/GIF/font wiring
- semantic mapping from gameplay states

Tighten:
- respect stage-01 hints when useful
- do not add noisy media just to satisfy quotas if the integration becomes obstructive
- keep all media mobile-safe and non-blocking

Recommended role:
```text
actual enrichment plumbing
```

### Stage 04
Keep:
- strict repair-only behavior
- minimal, surgical fixes
- no redesign

Tighten:
- mentally model user actions and trigger paths
- verify not only visibility, but actionability
- ask:
  - if user taps here, what happens?
  - is the control visible when needed?
  - is the modal action reachable?
  - is the next step blocked by overlap or hidden UI?
  - is the trigger wired and actionable?
- act only when a clear issue exists

Recommended role:
```text
passive actionability and safety repair
```

---

## Comment-Based Handoff Convention
Because the pipeline can only safely edit `index.html`, JS, and CSS, handoffs should happen through sparse embedded comments.

### Standard format
```html
<!-- [agent-note][stageX] key: value | key: value -->
```

### Recommended comment families

#### Stage 01 — future media / semantic hints
```html
<!-- [agent-note][stage1] role: future-audio | trigger: collect coin | intent: reward feedback -->
<!-- [agent-note][stage1] role: future-gif | trigger: win state | intent: celebration -->
<!-- [agent-note][stage1] role: future-emoji | element: score badge | intent: playful accent -->
<!-- [agent-note][stage1] role: future-illustration | element: hero intro | intent: stronger opening identity -->
```

#### Stage 02 — preserve layout / visual intent
```html
<!-- [agent-note][stage2] preserve: hud-layout | reason: already mobile-safe -->
<!-- [agent-note][stage2] preserve: control-zone | reason: avoid thumb obstruction -->
<!-- [agent-note][stage2] visual-intent: neon-arcade panels | scope: menus,hud -->
```

#### Stage 03 — media resolution notes
```html
<!-- [agent-note][stage3] resolved-audio: collect -> catalogs/audios.json -->
<!-- [agent-note][stage3] resolved-gif: win-overlay -> catalogs/gifs.json -->
<!-- [agent-note][stage3] resolved-font: title/ui -> catalogs/fonts.json -->
```

#### Stage 04 — actionability / repair notes
```html
<!-- [agent-note][stage4] action-path: start-btn -> gameplay -> pause-btn -> resume -->
<!-- [agent-note][stage4] issue: modal-action-risk | element: .restart-btn | reason: may sit below fold -->
<!-- [agent-note][stage4] repaired: overlap | element: .hud-topbar | action: compacted spacing -->
```

### Comment discipline
- comments should help the next agent decide what not to break
- comments should be sparse and high-value
- no noisy TODO spam
- no aspirational fake plumbing

---

## Mobile-First Preservation Rule
This should be treated as the universal pipeline DNA:

- assume the incoming game may already be mobile-friendly
- preserve the existing layout as closely as possible when it already works
- prioritize:
  1. gameplay clarity
  2. controls accessibility
  3. visible actionable UI
  4. readable compact HUD
  5. decoration
- if a choice is between stronger decoration and smaller safer UI, choose the smaller safer UI
- never let visual/media additions obscure control zones or next-step actions

---

## Main Handoff Risks

### 1. Stage 01 over-specifies later media
Risk:
- stage 01 comments become too prescriptive and constrain stage 03 unnecessarily

Mitigation:
- keep stage-01 media notes lightweight and suggestive only

### 2. Stage 02 recomposes stable HUD
Risk:
- visual ambition breaks a layout that was already mobile-safe

Mitigation:
- explicitly preserve HUD composition unless clearly broken

### 3. Stage 03 satisfies quotas too aggressively
Risk:
- media additions create clutter, overlap, or fragility

Mitigation:
- treat mobile safety and non-blocking runtime as higher priority than ornamental density

### 4. Stage 04 repairs only visible layout, not actionability
Risk:
- a button is visible but unreachable, hidden after state change, or logically trapped behind UI flow

Mitigation:
- use mental modeling of tap flow, trigger flow, modal flow, restart flow, pause flow, and win/loss flow

---

## Best Merge Rule
If the process must stay rigid, the cleanest merge strategy is:

```text
same rails outside
+
stricter scope boundaries inside
+
comment-based handoffs in editable files
+
mobile-first preservation as universal override
```

That preserves the external rails interface while making the internal pipeline more disciplined, more original, and less likely to break working mobile gameplay.