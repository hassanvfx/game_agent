# Node 4: Specimen Mobile-First Guided Remake

Work only inside the provided workspace.

Your job is to create the best mobile-first remake you can **without replacing the original workspace files in place**.

You must build the remake as a sibling clone entrypoint next to the existing `index.html`.

## Main goal

Use the accumulated artifacts from earlier nodes to build a stronger, cleaner, mobile-first version of the game while preserving the core gameplay identity.

This node is not a blind rewrite.
It is an artifact-guided remake step.

You must use the prior evidence as the source of truth for:
- what the game is trying to be
- what the user sees
- what gameplay loop should exist
- what mobile/runtime issues were observed
- what should be preserved vs improved

## Required context to consume first

Before building anything, read and use the available upstream artifacts when present, including:

- blueprint / inference / identity artifacts from earlier nodes
- gameplay/mechanics summaries
- `playwright_observation_log.md`
- `playwright_screenshots.json`
- `delta_issue_ledger.md`
- bounded browser screenshots captured in prior nodes
- the current implementation files in the workspace
- catalog files copied into the workspace

Treat those artifacts as constraints, not optional inspiration.

## Output location

Write the remake as a sibling clone entrypoint in the same directory as the original game entrypoint:

```text
index_clone.html
```

Do not overwrite the original `index.html` as part of this node unless a later explicit instruction says to promote the clone.

## Hard output rules

The remake must follow all of these rules:

1. **Single-file app**
   - the remake must be delivered as a single `index.html`
   - inline all CSS and JavaScript into that file

2. **Mobile-first**
   - optimize for mobile devices first
   - prioritize touch interaction, layout clarity, and readable screen composition
   - assume the target browser context is similar to the pipeline’s mobile Playwright context

3. **Preserve core identity**
   - keep the core gameplay loop recognizable
   - preserve the strongest recognizable visual/gameplay identity signals from the upstream artifacts
   - do not change the game into a different genre unless the artifacts strongly justify it

4. **Spanish-first simplified naming**
   - use Spanish as the primary code-language naming style where practical
   - use simplified alphanumeric identifiers only
   - avoid accents, tildes, and non-ascii identifier characters
   - examples of acceptable naming:
     - `estadoJuego`
     - `pantallaInicio`
     - `musicaFondo`
     - `puntajeActual`

5. **Approved media only**
   - do not use media from local `assets/` as gameplay media sources
   - use only approved media from the workspace catalog files for:
     - images
     - sprites
     - gifs
     - audio
     - fonts
   - if you need remote libraries, use only mainstream public CDNs for widely used libraries

6. **Single clone target**
   - produce one strongest remake, not multiple variants
   - write it to `index_clone.html`
   - do not create extra branches of the remake such as `v2`, `final2`, `alt`, etc.

## Library policy

You may use external CDN libraries only when they materially help the remake.

Prefer the lightest viable solution.

### Recommended library categories

#### Animation / interaction polish
You may use:
- GSAP
- Anime.js

Use these for:
- transitions
- small motion effects
- UI emphasis
- feedback animation

Do not use them as a substitute for the core gameplay architecture.

#### 2D rendering / game framework
You may use:
- Phaser
- PixiJS

Recommendations:
- prefer **Phaser** if the remake benefits from a stronger scene/game-loop/input structure
- prefer **PixiJS** if rendering polish matters more than a full gameplay framework
- prefer **vanilla DOM / Canvas** if the remake can be built clearly without a heavier engine

#### Physics
You may use:
- Matter.js

Only if the gameplay genuinely benefits from physics-driven interactions.

### Library restraint rule

Do not pile on libraries just because they are available.

Choose the smallest stack that clearly supports:
- mobile usability
- responsive interaction
- clear feedback
- maintainable single-file delivery

## Content and architecture recommendations

Use the evidence from earlier nodes to decide whether the remake should be built primarily with:

- semantic HTML + CSS + JS
- Canvas 2D
- a lightweight framework-backed scene
- a hybrid UI + canvas structure

When choosing, prefer:
1. mobile readability
2. stable interaction model
3. touch-friendly control surfaces
4. simple deployment
5. clear mapping back to the upstream game identity

## Remake guidance

The remake should improve things such as:
- layout clarity on small screens
- touch affordances
- feedback timing
- visual hierarchy
- state readability
- smoother mobile pacing
- cleaner event flow
- resilience against brittle legacy structure

But do **not**:
- invent unrelated features just to make it flashy
- add broad complexity that is unsupported by the artifacts
- introduce huge framework overhead unless justified
- create a disconnected “inspired by” game that loses the source identity

You do not need to be shy about reusing or translating substantial pieces of implementation structure when that helps produce the strongest mobile-first result.
You may rewrite, reorganize, and translate large sections of code or library-facing glue into Spanish-first simplified naming when useful, as long as the result remains coherent and follows the output rules.

## Required documentation artifact

Write a short summary file:

```text
remake_summary_clone.md
```

Include:
- what upstream artifacts you used
- what gameplay identity you preserved
- what major mobile-first improvements you introduced
- what libraries/CDNs you used and why
- what approved media catalogs you pulled from
- what you intentionally chose not to preserve

## Required contract artifact

Write:

```text
operator_result_contract_clone.json
```

If successful, write:

```json
{
  "status": "ok",
  "detail": "Created a mobile-first guided remake in index_clone.html using upstream gameplay/evidence artifacts, approved media sources, and Spanish-first simplified naming."
}
```

If blocked, write:

```json
{
  "status": "error",
  "detail": "Could not complete the guided mobile-first remake reliably."
}
```

## Expected deliverables

By the end of this node, the workspace should contain:

- `index_clone.html`
- `remake_summary_clone.md`
- `operator_result_contract_clone.json`

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
