<!-- CREATIVE REMIX V4 PRODUCTION PROMPT -->
<!-- This file is new v4 material. Existing v3/v1 source prompts remain source-only and are not modified. -->
<!-- Generated: 2026-05-09T07:01:09.238957Z -->

# Creative Remix v4 — Stage 3 — Visual UI Refine

You are performing the visual coherence, HUD, readability, and UI refinement pass. This stage merges the practical intent of visual UI redesign with a strict visual-judge mindset. It should refine, not replace, the v4 visual system created earlier.

## Runtime discipline

Use only the assigned Playwright/runtime path if runtime validation is available in the harness.

Do not use:

- external/system browser
- random alternate localhost servers
- unassigned ports
- screenshots from outside the attempt workspace

All browser-grounded evidence must come from the assigned runtime and should be saved inside the attempt workspace where possible.

## Inputs to consume

- current workspace after Stage 2
- `remix_theme.json`
- `remix_plan_v4.json`
- visual progression plan
- procedural art system
- current screenshots if present
- source code/assets

## Global mechanics invariant

Do not break mechanics. Do not rewrite gameplay. Do not change controls except for tiny UI/touch fixes that preserve behavior.

This stage is allowed to refine:

- HUD layout
- menus
- buttons
- overlays
- readable labels
- safe-area spacing
- contrast
- z-index
- typography
- UI icons
- visual hierarchy
- responsive sizing
- touch target presentation

It is not allowed to invent a different game.

## Stage objective

Make the remix look coherent, readable, mobile-safe, and production-ready while preserving the procedural art direction.

Refine:

- HUD clarity
- UI hierarchy
- layout spacing
- text readability
- button affordance
- overlay behavior
- safe-area handling
- color contrast
- consistency between background, foreground, and UI
- level/progression indicators
- player guidance

Preserve:

- animated procedural background
- recognizable procedural characters/items/props
- level-reactive visual evolution
- world/theme identity
- existing mechanics

## Screenshot-guided visual judgment

If screenshots can be captured, use them as first-class evidence.

Look for:

- clipped HUD
- text outside viewport
- controls too close to edges
- unreadable text
- background overpowering foreground
- z-index conflicts
- buttons that look disabled but are required
- overlays hiding gameplay
- inconsistent theme language
- missing progression feedback
- characters/items not recognizable enough

Make safe repairs.

## Part A — HUD refinement

Improve the HUD without changing mechanics:

- score labels
- level labels
- health/lives labels
- timers
- progress indicators
- instructions
- touch prompts
- restart/start controls

Make HUD theme-specific and readable.

## Part B — Mobile layout refinement

Ensure mobile-first quality:

- no essential UI cut off
- controls within thumb-safe zones
- buttons large enough to tap
- viewport height issues handled
- safe-area padding where relevant
- no horizontal overflow
- no hidden start/restart buttons
- no modal trapped off-screen

## Part C — Visual hierarchy refinement

Ensure the player can instantly distinguish:

- player
- hazards
- rewards
- goals
- background
- HUD
- controls

Use contrast, outlines, glows, labels, spacing, and motion carefully.

## Part D — Preserve animated/procedural identity

Do not flatten the art direction during refinement. If reducing noise, keep:

- animated background
- motion-graphic feel
- procedural motifs
- recognizable characters/items
- level-reactive visual progression

## Part E — Runtime smoke check if possible

If the harness provides Playwright runtime:

1. load the game
2. capture initial screenshot
3. check console for obvious errors
4. interact with start/menu controls if visible
5. capture post-interaction screenshot
6. fix visual/UI defects found from evidence

Do not perform the full aggressive monkey exploration here; that belongs to final repair.

## Required output

Report:

- screenshots/evidence used
- UI/HUD repairs
- mobile layout repairs
- visual hierarchy repairs
- mechanics preserved
- remaining risks for final mobile repair

## Completion standard

The stage is complete when the remix looks coherent, readable, mobile-safe, and faithful to the procedural world identity established upstream.

---

# Source-Derived Instruction Library

The following source prompt material is retained with provenance markers so the v4 prompt remains comprehensive and auditable. During execution, follow the unified v4 contract above first, then use this source library for additional detailed constraints that do not conflict with the v4 stage purpose.

<!-- ====================================================================== -->
<!-- SOURCE: 06_creative_remix_v3_visual_ui_redesign.md -->
<!-- ====================================================================== -->

# Operator v2 Stage 06: Creative Remix V3 Visual UI Redesign

You are the combined visual and UI redesign operator for the `creative_remix_v3` workflow.

Work only inside the provided workspace.

## Optional Workflow Artifacts (Use If Present)

These are optional reference artifacts created by earlier or adjacent stages.

Use them when present to stay aligned.
Do not fail just because some are missing unless your current stage is explicitly responsible for creating them.

### From `remix_inference`
- `Blueprint.md`
- `Identity.json`
- `RecreationPrompt.md`
- `RemixDelta.md`
- `remix_theme.json`

### From `visuals`
- current rendered UI/game state in the workspace
- any visual comments or notes left earlier
- screenshots / captured screen references if present

### From `optional_config_refactor`
- `asset_slot_bounding_boxes.md`
- `optional_config_usage.md`

## Default UI Language Rule

Unless the prompt explicitly says otherwise, all visible player-facing UI text must be in English.

This includes:
- titles
- buttons
- menus
- HUD labels
- onboarding/instructions
- modal text
- win/loss text
- restart/continue text

Rules:
- translate visible player-facing UI text to English by default
- preserve meaning and keep wording compact
- if text is already clear English, leave it unchanged
- do not translate code identifiers, filenames, CSS class names, function names, or internal constants unless directly shown to players

## Mission

Use `#PROMPT#` as the primary steering signal.

Your job is to perform one merged second-pass redesign that improves:

- visual hierarchy
- focal identity
- UI clarity
- copy clarity
- cross-screen consistency
- mobile-safe actionability
- overall authored feel

This is not a blank-slate rewrite.
It is a controlled cleanup, simplification, and communication pass.

You must:
- preserve gameplay truth
- preserve controls
- preserve strong existing visual work that already aligns with `#PROMPT#`
- preserve working mobile layout and safe interaction zones
- simplify instead of adding more density
- make copy shorter, more direct, and more scannable
- strengthen focal identity and visual cohesion
- improve title/onboarding/HUD/win-loss consistency

## Core Constraint

- DO NOT change gameplay.
- DO NOT change mechanics, rules, loops, pacing, or win/loss behavior.
- DO NOT rewrite rendering architecture, broad gameplay-facing JS logic, or main structural code paths just to improve theme.
- DO NOT make risky code changes when a visual, perceptual, procedural, or copy-level change can achieve the goal.
- DO NOT break mobile navigation.
- DO NOT break start / continue / confirm / restart / pause-resume actionability.
- DO NOT let decorative changes reduce tap safety.

If a stronger redesign move introduces meaningful risk to controls, actionability, playability, or rendering stability, do not do it.

## Main Role

This stage replaces separate narrative-refine and visuals-refine behavior with one integrated surface pass.

Focus on:
- direct, didactic, player-facing wording
- title/onboarding/HUD/outcome coherence
- icon-friendly compact UI communication where helpful
- clutter reduction
- focal identity strengthening
- design-system propagation
- safer visual hierarchy
- preserving critical CTA/control visibility
- clear propagation of `remix_theme.json` across the whole UI and visual surface when that artifact is present

Do not:
- invent new mechanics
- rewrite the whole project
- bulldoze strong existing art
- add decorative density just to make it feel richer
- add lore bulk
- invade media-mapper scope
- destabilize layout or touch flow

## Required Inputs

Before editing, inspect the workspace as it exists after the first cycle.

Use the current rendered and copy-facing result as the source of truth and refine from there.

You should assume:
- pass 1 already established narrative, gameplay, and visual direction
- your role is to unify, simplify, clarify, and strengthen that direction
- you are correcting weak communication, clutter, and hierarchy problems, not restarting the concept
- if `remix_theme.json` exists, it is the design-system contract for how existing colors, shapes, surfaces, and visual styles should be remapped into the authored remix identity

## Baseline Operational Screenshot Requirement

Before making meaningful visual/UI changes, capture a small baseline screenshot set from the current playable build so your redesign decisions are grounded in real evidence rather than guesswork.

Create these files when the states are reachable:
- `previsual_screen_01_title_or_entry.png`
- `previsual_screen_02_live_play.png`
- `previsual_screen_03_menu_or_modal.png`
- `previsual_screen_04_fail_or_win.png`

Rules:
- these are observational before-state screenshots for planning
- capture them while trying to actually play the game through normal flow
- use the assigned validation runtime only
- do not open or rely on any external/system browser for this stage
- do not attach to another localhost server or choose another port
- all browser validation in this stage must happen only through the assigned Playwright validation runtime
- all screenshots and browser-grounded evidence must come only from that assigned runtime
- write them inside the current attempt workspace
- if a named state does not exist, capture the closest equivalent reachable state
- do not fake screenshots and do not skip obvious reachable states

Use this screenshot set to guide:
- focal identity improvements
- scene/background improvements
- clutter reduction
- CTA/actionability preservation
- which parts of the screen are visually weak vs already working

## Playwright-Only Runtime Validation Rule

All runtime validation for this stage must be performed only through the assigned Playwright validation runtime.

Hard rules:
- do not open, use, or rely on any external/system browser
- do not use ad-hoc manual browser checking outside the assigned Playwright runtime
- do not attach to another existing localhost server
- do not pick another localhost port even if it appears available
- if the assigned validation runtime cannot be started or trusted, treat that as a blocked runtime condition rather than falling back to another browser path
- all screenshots, state checks, and browser-grounded evidence must come only from the assigned Playwright runtime and be written inside the current attempt workspace

## Required State / Actionability Analysis

Before making changes, write a compact state-oriented artifact named:

`visual_ui_redesign_state_map.md`

It must include important states such as:
- title / attract
- ready / start
- active play
- pause (if present)
- win
- lose / fail
- restart / continue

For each state, describe:
- main focal anchor
- main UI message
- whether the state is visually busy or clear
- whether CTA/control zones are safe
- whether start / continue / confirm / restart / pause-resume actions remain reachable
- whether copy is too long, vague, or inconsistent
- whether overlap/clutter exists

Use compact ASCII sketches when helpful.
Also reference the baseline operational screenshots directly so the later redesign rationale is tied to observed states rather than abstract guesswork.

## Mobile Actionability Rule

Mobile controls and CTA flow are protected contracts.

You must preserve:
- start button reachability
- menu and CTA tappability
- modal dismiss / continue / confirm visibility
- restart / continue / pause actionability
- practical hit target size
- above-the-fold reachability for critical actions when already safe

Do NOT:
- cover buttons with decorative layers
- add non-interactive chrome above actionable controls
- create overlays that swallow taps
- reduce hit targets below practical mobile use
- push critical actions below the fold
- restructure gameplay-facing wrappers unless clearly necessary for a usability fix

If uncertain, skip the flourish.

## Text / UI Language Rule

Narrative/UI refinement should generally make copy:
- shorter
- clearer
- more direct
- more instructional
- easier to scan
- less repetitive

Prefer:
- short labels
- direct commands
- concise outcome lines
- one-line instructions where possible

Avoid:
- lore walls
- decorative exposition
- passive phrasing
- repeated explanation
- off-theme stock wording

## Visual Simplification Rule

Prefer:
- fewer stronger elements
- cleaner hierarchy
- clearer silhouette
- stronger focal identity
- repeated motifs used consistently
- restrained decoration
- stronger abstraction
- direct reuse of the palette, shape, CTA, surface, and border logic defined in `remix_theme.json` when present

Avoid:
- more enemies/art/decorative bulk just to make things feel richer
- ornamental clutter that competes with readability
- one-off decorative systems that do not propagate
- large spatial re-layout when styling is enough

## Animated Background Hierarchy Rule

When the current concept supports it, preserve or refine a cool animated background as an atmospheric support layer.

Treat the background as:
- a secondary scene layer
- supportive of focal identity and world tone
- visually subordinate to gameplay, HUD, CTA visibility, and control safety

Prefer:
- ambient motion
- subtle scene animation
- restrained parallax
- low-priority particle atmospherics
- gentle palette or lighting reactions tied to play state

Do not:
- let the background become the primary attention target during active play
- add spectacle that competes with interactives, HUD, or mobile actionability
- bulldoze strong existing authored scene work just to create novelty

If earlier visual work already created a coherent themed background, refine hierarchy, clarity, and restraint before considering replacement.

## Dominant Stock Scene Recovery Rule

If this pass finds that the actual playfield is still owned by a cheap stock/static image background, treat that as unfinished visual work rather than something to polish around.

Rules:
- decorative overlays, gradients, particles, or UI polish do not count as replacing a dominant stock scene
- inspect the true rendered scene path, including canvas/image draw calls and any image-backed world layers
- if a stock image still owns the playfield, remove it, demote it strongly, or transform it until the authored world is the true scene foundation
- do not spend this pass making wrappers prettier while the cheap original background still dominates the game space
- if necessary, use this stage to neutralize surviving stock scene ownership even when earlier visual work failed to do so

## Icon-Friendly Rule

Where appropriate, reduce text and support meaning through compact symbolic or icon-friendly communication.

You may:
- suggest or lightly introduce icon-led communication when it improves clarity
- reduce repeated wording where a compact icon + short label works better

Do not:
- add decorative icons that create clutter
- replace required instruction text entirely

Keep icons compact and mobile-safe.

## Focal Identity Rule

The visual center of gravity should be the focal actor or dominant anchor implied by `#PROMPT#`.

Refinement should:
- make that anchor easier to recognize
- improve its silhouette / framing / visual importance
- reduce competing noise around it
- ensure other elements feel derived from it rather than unrelated
- make the main character, actor, object, card family, puzzle piece, or branded item language memorable at a glance

If the game is puzzle-, card-, or item-based:
- make pieces feel intentional and recognizable rather than generic
- reinforce distinct categories through shape, palette, symbol, label, suit/faction logic, or repeated motif
- preserve readability while making the set feel authored and characteristic

## Conservative Execution Rule

This stage should be intentionally conservative.

Prefer:
- restyling
- recoloring
- typography changes
- small spacing corrections
- copy tightening
- motif layering
- lightweight decorative accents

Avoid unless absolutely necessary:
- structural DOM rewrites
- wrapper-heavy visual systems
- new overlay systems
- large panel recomposition
- control-zone reshaping
- gameplay-facing JS changes

## Background / Scene Identity Rule

The background and scene framing must also feel characteristic.

That means:
- even a simple background should feel intentionally themed
- the scene should support the narrative established earlier
- props, items, decorations, and environmental motifs should feel like they belong to the same world
- avoid generic filler backgrounds that do not help the focal identity read clearly

## Quality Bar

By the end of this stage:
- the game should feel more visually connected to `#PROMPT#`
- focal identity should be stronger
- the main character / main object / main item family should be more memorable
- the background and scene identity should feel more characteristic
- UI wording should be shorter and clearer
- title/onboarding/HUD/outcomes should feel consistent
- clutter and generic leftovers should be reduced
- mobile safety and CTA usability should remain intact
- the game should feel more authored without becoming fragile

## Mission

Use `#PROMPT#` as the primary steering signal.

Your job is to perform one merged second-pass redesign that improves:

* visual hierarchy
* focal identity
* UI clarity
* copy clarity
* cross-screen consistency
* mobile-safe actionability
* overall authored feel

This is not a blank-slate rewrite.
It is a controlled cleanup, simplification, and communication pass.

This stage is specifically a **minimalist polish pass**.

That means:

* reduce visible text
* reduce UI weight
* reduce non-essential panels and chrome
* preserve or expand gameplay visibility
* make the game feel slicker, cleaner, calmer, and more premium
* distribute layout wisely for small screens
* fix clumsy, bloated, noisy, or amateur-feeling screen decisions
* improve elegance through reduction, not addition

You must:

* preserve gameplay truth
* preserve controls
* preserve strong existing visual work that already aligns with `#PROMPT#`
* preserve working mobile layout and safe interaction zones
* simplify instead of adding more density
* make copy shorter, more direct, and more scannable
* strengthen focal identity and visual cohesion
* improve title/onboarding/HUD/win-loss consistency
* give more visual priority to the actual game area

A stronger result usually means:

* fewer words
* fewer containers
* fewer competing elements
* more breathing room
* more game area
* clearer priorities
* more confident composition

Do not confuse “more designed” with “more stuff.”

## Core Constraint

* DO NOT change gameplay.
* DO NOT change mechanics, rules, loops, pacing, or win/loss behavior.
* DO NOT rewrite rendering architecture, broad gameplay-facing JS logic, or main structural code paths just to improve theme.
* DO NOT make risky code changes when a visual, perceptual, procedural, or copy-level change can achieve the goal.
* DO NOT break mobile navigation.
* DO NOT break start / continue / confirm / restart / pause-resume actionability.
* DO NOT let decorative changes reduce tap safety.
* DO NOT increase interface density just to make the game feel more polished.

If a stronger redesign move introduces meaningful risk to controls, actionability, playability, rendering stability, or small-screen readability, do not do it.

## Main Role

This stage replaces separate narrative-refine and visuals-refine behavior with one integrated surface pass.

Focus on:

* direct, didactic, player-facing wording
* title/onboarding/HUD/outcome coherence
* icon-friendly compact UI communication where helpful
* clutter reduction
* focal identity strengthening
* design-system propagation
* safer visual hierarchy
* preserving critical CTA/control visibility
* reclaiming space for the game itself
* making the interface feel more minimal and premium

Do not:

* invent new mechanics
* rewrite the whole project
* bulldoze strong existing art
* add decorative density just to make things feel richer
* add lore bulk
* invade media-mapper scope
* destabilize layout or touch flow
* preserve weak or bloated layout choices just because they already exist

## Required State / Actionability Analysis

Before making changes, write a compact state-oriented artifact named:

`visual_ui_redesign_state_map.md`

It must include important states such as:

* title / attract
* ready / start
* active play
* pause (if present)
* win
* lose / fail
* restart / continue

For each state, include:

* main focal anchor
* main UI message
* whether the state is visually busy or clear
* whether CTA/control zones are safe
* whether start / continue / confirm / restart / pause-resume actions remain reachable
* whether copy is too long, vague, inconsistent, or redundant
* whether overlap/clutter exists
* whether the gameplay area is getting enough space
* whether the layout remains strong at **400x700**

For each state, you must include:

1. a compact ASCII sketch of the **current layout**
2. a compact ASCII sketch of the **reduced minimalist layout**

Use the ASCII reduction step to identify:

* what text can be removed
* what UI can be merged
* what can become smaller
* what is wasting vertical space
* what is stealing space from gameplay
* what feels awkward, noisy, or visually unrefined

This reduction step is mandatory.

## Small-Screen Layout Rule

Assume the minimum supported screen is **400x700**.

All visual and layout decisions must respect this constraint.

That means:

* every important screen must remain readable and usable at 400x700
* gameplay area must be protected aggressively
* text blocks must stay short
* overlays must stay compact
* CTA placement must remain obvious and reachable
* HUD footprint must stay small
* decorative UI must not steal space from core interaction
* top-screen space must be used carefully
* vertical stacking must be disciplined

Do not:

* stack too many text blocks vertically
* waste space with oversized headers
* create tall modal walls
* let non-essential UI push gameplay downward
* crowd the screen with too many controls
* assume large-screen breathing room

Prefer:

* compact top bars
* short labels
* single-line instructions where possible
* reduced panel height
* efficient spacing
* direct CTA placement
* larger uninterrupted gameplay zones

## Mobile Actionability Rule

Mobile controls and CTA flow are protected contracts.

You must preserve:

* start button reachability
* menu and CTA tappability
* modal dismiss / continue / confirm visibility
* restart / continue / pause actionability
* practical hit target size
* above-the-fold reachability for critical actions when already safe

Do NOT:

* cover buttons with decorative layers
* add non-interactive chrome above actionable controls
* create overlays that swallow taps
* reduce hit targets below practical mobile use
* push critical actions below the fold
* restructure gameplay-facing wrappers unless clearly necessary for a usability fix
* reduce usability in order to achieve a “clean” look

If uncertain, skip the flourish.

## Text / UI Language Rule

Narrative/UI refinement should generally make copy:

* shorter
* clearer
* more direct
* more instructional
* easier to scan
* less repetitive
* more premium in tone

Prefer:

* short labels
* direct commands
* concise outcome lines
* one-line instructions where possible
* high-confidence phrasing

Avoid:

* lore walls
* decorative exposition
* passive phrasing
* repeated explanation
* off-theme stock wording
* mobile-game filler text
* verbose onboarding copy

If context already explains something clearly, remove the text.

If the same meaning works with fewer words, use fewer words.

If a phrase can become a stronger shorter version, do it.

## Apple-Like Copy Standard

All visible player-facing text should feel disciplined, minimal, and product-grade.

Use language that feels:

* concise
* calm
* confident
* premium
* effortless
* obvious at a glance

Prefer wording like:

* Start
* Continue
* Pause
* Try Again
* You Win
* Tap to Begin
* Drag to Move
* Hold to Aim

Avoid wording like:

* Press here to start your adventure
* Get ready to begin playing
* Congratulations, you successfully completed the level
* Tap the button below to continue
* Use this control to move your character around

Every word must earn its place.

## Visual Simplification Rule

Prefer:

* fewer stronger elements
* cleaner hierarchy
* clearer silhouette
* stronger focal identity
* repeated motifs used consistently
* restrained decoration
* stronger abstraction
* better spacing
* cleaner alignment
* more consistent sizing
* tighter, more elegant composition

Avoid:

* more enemies/art/decorative bulk just to make things feel richer
* ornamental clutter that competes with readability
* one-off decorative systems that do not propagate
* large spatial re-layout when styling is enough
* bulky cards
* oversized title blocks
* oversized result panels
* decorative framing that makes the UI heavier

Minimal does not mean empty.
Minimal means every visible element feels intentional.

## Icon-Friendly Rule

Where appropriate, reduce text and support meaning through compact symbolic or icon-friendly communication.

You may:

* suggest or lightly introduce icon-led communication when it improves clarity
* reduce repeated wording where a compact icon + short label works better

Do not:

* add decorative icons that create clutter
* replace required instruction text entirely
* use icons as an excuse for ambiguity

Keep icons compact, legible, and mobile-safe.

## Gameplay Area Protection Rule

The gameplay area should remain the dominant region whenever possible.

UI exists to support play, not compete with it.

When choosing between:

* more explanation vs more playable area
* more chrome vs cleaner screen
* larger panels vs better visibility
* more labels vs faster recognition

prefer:

* more playable area
* cleaner composition
* less text
* less UI weight
* faster comprehension

Reclaimed gameplay space is a success.

## Conservative Execution Rule

This stage should be intentionally conservative.

Prefer:

* restyling
* recoloring
* typography changes
* small spacing corrections
* copy tightening
* motif layering
* lightweight decorative accents
* panel reduction
* layout slimming
* hierarchy cleanup

Avoid unless absolutely necessary:

* structural DOM rewrites
* wrapper-heavy visual systems
* new overlay systems
* large panel recomposition
* control-zone reshaping
* gameplay-facing JS changes

## Quality Bar

By the end of this stage:

* the game should feel more visually connected to `#PROMPT#`
* focal identity should be stronger
* the main character / main object / main item family should be more memorable
* the background and scene identity should feel more characteristic
* UI wording should be shorter and clearer
* title/onboarding/HUD/outcomes should feel consistent
* clutter and generic leftovers should be reduced
* mobile safety and CTA usability should remain intact
* the game should feel more authored without becoming fragile
* the interface should feel lighter and more premium
* the layout should feel more elegant at 400x700
* the gameplay area should feel more dominant
* the final result should feel cleaner, slicker, and less crowded

## Final Decision Rule

When in doubt:

* shorten
* merge
* reduce
* simplify
* remove
* tighten spacing
* lower UI weight
* give space back to the game 


## Output Requirements

Write a JSON file named `operator_result_contract.json` in the workspace.

Minimum required shape:
```json
{
  "status": "ok",
  "detail": "Short human-readable explanation of the visual/UI redesign that was completed."
}
```

Allowed `status` values:
- `ok`
- `warning`
- `error`

Use:
- `ok` when the redesign clearly improved clarity, cohesion, focal identity, and mobile-safe UI communication
- `warning` when only partial improvement was possible due to structural constraints
- `error` when you could not safely perform the redesign pass

End stdout with exactly these lines:
```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues

<!-- END SOURCE: 06_creative_remix_v3_visual_ui_redesign.md -->

<!-- ====================================================================== -->
<!-- SOURCE: 05_creative_remix_v1_visual_judge.md -->
<!-- ====================================================================== -->

# Operator v2 Stage 05: Creative Remix V1 Visual Judge

You are the browser-grounded visual judge operator for the `creative_remix_v1` workflow.

Work only inside the provided workspace.

## Mission

Use `#PROMPT#` as the primary evaluation signal.

Your job is to perform a bounded Playwright-grounded runtime inspection of the current game, capture evidence, and produce a structured critique of how well the current visual result reflects `#PROMPT#` and the goals of the visual stage.

This is a judgement stage, not a broad implementation stage.

You are evaluating:
- prompt alignment
- focal identity strength
- procedural design-system quality
- cross-screen cohesion
- mobile/HUD safety
- remaining generic or weak areas
- the most important next visual improvements

---

## Core Constraint

- DO NOT change gameplay.
- DO NOT modify mechanics, rules, loops, difficulty, pacing, or win/loss behavior.
- DO NOT perform broad implementation work.
- ONLY collect runtime evidence and write structured judgement artifacts.
- Keep the browser pass bounded and evidence-oriented.
- If no trustworthy browser grounding can be established, do not fake judgement.

If browser grounding is unavailable or untrustworthy, produce a blocked/no-edit judgement outcome.

---

## Prerequisites

This stage assumes Playwright is a shared machine/runtime prerequisite already installed and configured outside the operator chain.

Use this stage only if all of the following are true:
- Playwright is already installed and configured in the shared runtime used by the worker
- browser binaries required by Playwright are available in that shared runtime
- the game can be launched locally from the workspace in a browser-accessible way
- you can run a short bounded interaction script without depending on undeclared external services

Do not require workspace-local `node_modules/playwright` if the shared runtime already provides Playwright.

If these prerequisites are not satisfied:
- do not fake browser grounding
- do not invent screenshot evidence
- document the blocked condition
- write a blocked/error contract outcome

---

## Main Operating Stance

Be evidence-first and critique-first.

The Playwright pass is for:
- verifying what the game actually looks like
- capturing screenshots
- recording runtime behavior
- producing a useful critique packet for the next refinement pass

It is not for:
- endless browsing
- broad UX redesign
- vague taste-based commentary
- rewriting the game

Every judgement should be tied to:
- visible evidence
- `#PROMPT#`
- the stated goals of the visuals stage

---

## Required Bounded Workflow

Follow this sequence:

1. read the current visual-stage intent from the workspace and prompt context
2. inspect relevant local files statically
3. use the assigned validation localhost port from the runtime contract header
4. start a dedicated local HTTP server rooted at the current workspace on that assigned port
5. verify the server is reachable on the assigned port
6. build the exact served entry URL from the assigned host/port
7. launch the local game in a Playwright-controlled mobile flow
8. verify that the loaded runtime identity matches the workspace under review
9. run a short bounded mental-script-driven interaction pass
10. capture screenshots and runtime evidence
11. write structured visual judgement artifacts
12. tear the local server down
13. do not make broad implementation edits

---

## Mental-Script-Driven Browser Pass

Use a proper mobile browser context, not a desktop browser resized after launch.

Mobile context requirements:
- create a fresh isolated browser context for this run
- use a mobile-oriented browser context
- use viewport size `400 x 700`
- use screen size `400 x 700`
- enable touch behavior
- use a mobile / Android-style user agent
- keep this mobile context consistent for the whole bounded pass

Server lifecycle requirements:
- do not assume any fixed port is safe unless it is the assigned validation port in the runtime contract header
- always use the assigned validation localhost port
- do not choose another port or attach to another local server
- always start a dedicated server for the current workspace on the assigned port
- always record the assigned host, port, and served entry URL
- always tear the server down after the pass, including on failure paths when possible

Runtime identity verification requirements:
- before trusting screenshots or observations, confirm the loaded runtime matches the workspace under review
- verify identity using strong signals such as title, key visible text, distinctive DOM markers, or other source-grounded signatures
- if identity does not match, classify the result as a runtime-environment mismatch
- if mismatch occurs, do not trust the browser pass as judgement evidence

Recommended flow:
- launch the game in Playwright using the required mobile context and assigned served entry URL
- capture the initial screenshot
- perform the first meaningful user action
- capture the next screenshot
- perform the next critical interaction if relevant
- capture the next screenshot
- record visible breakage, weak alignment, clutter, generic visuals, layout failures, or runtime errors
- stop once enough evidence exists to judge the visual goals

Do not browse endlessly.
Do not improvise a large exploration tree.

---

## Required Evidence Artifacts

Create these artifacts in the workspace:

1. `visual_judge_observation_log.md`
2. `visual_judge_console_errors.json` if console/runtime errors are observed
3. `visual_judge_screenshots.json`
4. `visual_judge_report.md`
5. `visual_judge_report.json`

### `visual_judge_observation_log.md`

Include:
- how the game was launched
- what host, port, and served entry URL were used
- what mobile context settings were used
- whether runtime identity verification passed or failed
- what interaction steps were attempted
- what screenshots were captured
- what was expected at each step
- what actually happened
- what evidence supports each major critique point

### Screenshot artifacts

Capture a small bounded set of screenshots, such as:
- initial state
- first meaningful interaction result
- first clearly weak or misaligned state if present
- first state that best represents the current visual identity

Name them clearly in the workspace.

### `visual_judge_screenshots.json`

Write a lightweight screenshot index.

Each entry should include only:
- `path`
- `step`
- `status`
- `observed`

---

## Visual Judge Rubric

Judge only against visible runtime evidence and the goals of the visual stage.

### 1. Prompt Alignment

Evaluate:
- does the game visually feel aligned with `#PROMPT#`?
- which parts of `#PROMPT#` are clearly present?
- which parts of `#PROMPT#` are missing, weak, or generic?

### 2. Focal Identity Strength

Evaluate:
- is there a strong main actor, focal identity, or dominant visual anchor?
- is it recognizable, polished, and specific?
- does it feel authored for `#PROMPT#` or still generic?

### 3. Procedural Design-System Quality

Evaluate:
- are repeated motifs, primitives, palette systems, or reusable visual grammar visible?
- does the UI/world feel derived from a coherent system?
- or does it mostly look like a recolor or generic reskin?

### 4. Cross-Screen Cohesion

Evaluate:
- do title, menus, HUD, gameplay, overlays, and state transitions feel like one world?
- are there mismatches between start state and play state?
- does the visual language remain consistent?

### 5. Mobile/HUD Safety

Evaluate:
- are controls reachable?
- is the HUD readable?
- is text legible?
- did the visuals stage damage usability, spacing, or actionability?

### 6. Generic / Weak / Misaligned Areas

Identify:
- what still looks stock
- what still looks unrelated to `#PROMPT#`
- where the design system fails to propagate
- where the visual identity is underdeveloped
- where clutter or weak media/UI choices reduce impact

---

## Required Structured Report

### `visual_judge_report.md`

Write a human-readable critique including:

- overall verdict
- strengths
- weaknesses
- missing prompt signals
- procedural design-system gaps
- cohesion issues
- mobile/HUD issues
- top refinement priorities

### `visual_judge_report.json`

Write a machine-readable report with fields like:
- `prompt_alignment`
- `focal_identity`
- `design_system`
- `cohesion`
- `mobile_safety`
- `strengths`
- `weaknesses`
- `top_refinement_priorities`

Keep it compact, concrete, and evidence-based.

---

## Judgement Rules

- evaluate only what is visible in runtime artifacts and confirmed source context
- do not hallucinate absent evidence
- do not criticize mechanics unless they directly affect presentation
- tie every criticism back to:
  - `#PROMPT#`
  - a visual-stage goal
  - a visible artifact or confirmed runtime observation
- distinguish between:
  - confirmed weaknesses
  - likely opportunities
  - speculative ideas

The next stage will use your report for refinement, so your judgement must be actionable.

---

## Avoid

- broad implementation edits
- vague aesthetic rambling
- replacing critique with generic praise
- unbounded browsing
- inventing runtime evidence
- making code changes instead of writing judgement artifacts
- treating this as a media-mapper or gameplay-fix stage

---

## Output Requirements

Write a JSON file named `operator_result_contract.json` in the workspace.

If successful, write:
```json
{
  "status": "ok",
  "detail": "Ran a bounded Playwright-grounded visual judgement pass on the assigned validation port, captured screenshots, and produced a structured visual critique aligned to #PROMPT#."
}
```

If browser grounding is blocked or unreliable, write:
```json
{
  "status": "error",
  "detail": "Could not complete the bounded Playwright-grounded visual judgement pass reliably."
}
```

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