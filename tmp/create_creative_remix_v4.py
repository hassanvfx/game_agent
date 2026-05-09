#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "tools/game_refactoring/prompts/operators_v2"
BUNDLES = PROMPTS / "v4_source_bundles"
JOURNAL = ROOT / "docs/journals/creative-remix-v4-merged-prompts.md"
WORKFLOW = ROOT / "tools/game_refactoring/scripts/game_workflow.py"

V4_PROMPTS = {
    "00_creative_remix_v4_remix_inference_plus.md": {
        "title": "Creative Remix v4 — Stage 0 — Remix Inference Plus",
        "sources": [
            "00_creative_remix_v3_remix_inference.md",
            "10_creative_remix_v3_level_adapter.md",
        ],
        "body": r"""
# Creative Remix v4 — Stage 0 — Remix Inference Plus

You are performing the first v4 planning pass. This stage replaces the old split between early remix inference and late level adaptation. It must infer the game, decompose its mechanics, choose a safe remix direction, and produce a complete five-level progression plan before downstream stages touch the presentation.

This is not a short summary stage. It is a comprehensive planning harness. Preserve the full power of the source prompts while removing the old problem where level reasoning arrived too late in the workflow.

## Non-negotiable global harness invariants

1. Do not break mechanics.
2. Do not rewrite core gameplay logic unless you are documenting a tiny, safe, necessary repair.
3. Prefer cosmetic, presentation, audiovisual, copy, HUD, asset-mapping, procedural-art, and layout changes over mechanic changes.
4. Treat the original game loop, controls, collision model, scoring model, win/loss model, timing model, and progression hooks as protected evidence.
5. If uncertain whether a change risks playability, mark it as unsafe and route around it.
6. Favor procedural/code-native art direction: CSS, SVG, Canvas, DOM drawing, simple generated shapes, lightweight animation, reusable motif systems, and code-native character/item libraries.
7. Do not make stock images or pasted flat art the main identity of the remix.
8. The visual target is animated, recognizable, motion-graphic, level-reactive, and theme-specific.

## Stage purpose

This stage must output a planning contract that downstream v4 stages can obey without needing a separate level adapter.

It must define:

- the player's core verb(s)
- the game loop
- the control model
- the obstacle/hazard/reward model
- scoring and progress feedback
- the true mechanical complexity of the source game
- what can safely be themed without touching mechanics
- what must not be changed
- the remix premise
- the procedural visual identity
- the five-level difficulty progression
- the five-level visual evolution
- the 1.5-level core definition: the smallest playable progression unit that proves the remix can scale into five levels

## Required analysis sections

### 1. Game identity and current behavior

Describe the game as implemented, not as imagined. Identify:

- genre / archetype
- core player goal
- core verb
- fail state
- success / score state
- camera / viewport assumptions
- input model
- moment-to-moment loop
- what screen states are likely present
- what progression exists already, if any

### 2. Mechanic decomposition

Break the game into mechanic modules. Use concrete terms:

- input/control mechanic
- movement mechanic
- spawning/timing mechanic
- collision/contact mechanic
- scoring/progress mechanic
- hazard mechanic
- reward/collectible mechanic
- level/round/state mechanic
- UI/HUD feedback mechanic
- audio/visual feedback mechanic

For each module, classify it as:

- protected: must not be changed
- themable: can be reskinned/reframed safely
- repairable: may receive tiny safe fixes if already broken
- unknown: needs downstream runtime verification

### 3. Complexity profile

Assess the game complexity honestly:

- simple one-screen arcade
- medium arcade loop
- multi-state puzzle/action
- multi-level game
- menu-heavy game
- physics-heavy game
- timing-heavy game

Then define what "more complex" should mean without breaking mechanics. Complexity should usually come from:

- clearer level goals
- better visual progression
- more readable hazard/reward language
- stronger state feedback
- staged difficulty tuning if existing knobs are safe
- background/world evolution
- UI/HUD clarity
- theme-specific challenge framing

Avoid complexity through risky core rewrites.

### 4. Remix premise

Convert the user remix prompt into a coherent world premise. The premise must be:

- recognizable
- visually generative
- compatible with the source mechanics
- able to support five levels
- able to produce procedural characters/items/props
- able to drive animated backgrounds and motion graphics

### 5. 1.5-level core definition

Define the smallest practical progression proof:

- Level 1: the base transformed experience
- Level 1.5: the first meaningful escalation or variation

This must explain how the game can show progression while staying within safe mechanics.

### 6. Five-level difficulty progression

Create five levels even if the source game does not currently expose five explicit levels. If explicit levels already exist, preserve and reinterpret them. If they do not exist, define a conceptual five-level progression that downstream prompts can implement through safe presentation/progression hooks.

For each level, specify:

- level title
- player-facing goal
- difficulty intent
- safe mechanics knobs, if any
- protected mechanics to avoid touching
- hazard/reward interpretation
- UI/HUD messaging
- failure risk to watch
- visual progression beat

### 7. Five-level visual evolution

For each level, specify:

- animated background concept
- motion-graphic behavior
- procedural character/item/prop evolution
- color/lighting progression
- motif evolution
- HUD/theming progression
- how the scene changes in a way the player can recognize

The background must not be generic decoration. It must become an authored world layer that reacts to progress/state when safely possible.

### 8. Procedural art system plan

Define a reusable visual language:

- primary shapes
- motif vocabulary
- character silhouettes
- item silhouettes
- icon style
- background layers
- animation principles
- CSS/SVG/Canvas/DOM implementation preference
- safe fallback if external assets fail

### 9. Downstream contract

Write a compact contract for later v4 stages:

- what Stage 1 must preserve and execute
- what Stage 2 must draw/build
- what Stage 3 must refine
- what Stage 4 must verify and repair

## Required artifacts

Create or update planning artifacts where the harness supports them. At minimum the result text must clearly include:

- `mechanic_decomposition`
- `complexity_profile`
- `protected_mechanics`
- `safe_theming_surfaces`
- `remix_premise`
- `one_point_five_level_core`
- `five_level_difficulty_progression`
- `five_level_visual_evolution`
- `procedural_art_system`
- `downstream_stage_contract`

If writing JSON artifacts is feasible in the workspace, prefer a structured `remix_plan_v4.json` with the same sections.

## Completion standard

This stage is complete only when a later stage could implement the remix without guessing:

- what the mechanics are
- what not to touch
- what the five levels mean
- how the visuals evolve
- what procedural character/item/background system should exist
- what runtime risks must be watched
""",
    },
    "01_creative_remix_v4_world_design_superprompt.md": {
        "title": "Creative Remix v4 — Stage 1 — World Design Superprompt",
        "sources": [
            "01_creative_remix_v1_narrative.md",
            "02_creative_remix_v1_gameplay.md",
            "03_media_mapper.md",
            "04_creative_remix_v1_media_mapper.md",
        ],
        "body": r"""
# Creative Remix v4 — Stage 1 — World Design Superprompt

You are performing the main authored-world construction pass for Creative Remix v4. This stage merges the narrative, gameplay-preservation, and media-mapping responsibilities into one comprehensive production prompt.

Do not treat this as a summary. This prompt carries the full behavioral contract of the original narrative, gameplay, and media mapper stages, but unified around a single goal: transform the game into a coherent themed world while preserving mechanics and preparing a robust procedural asset/motif system.

## Inputs to consume

Use all available upstream context, especially the Stage 0 v4 planning contract:

- mechanic decomposition
- complexity profile
- protected mechanics
- safe theming surfaces
- remix premise
- 1.5-level core definition
- five-level difficulty progression
- five-level visual evolution
- procedural art system plan
- user remix prompt

If Stage 0 created `remix_plan_v4.json`, treat it as binding guidance unless it directly conflicts with visible source code reality.

## Global mechanics invariant

The static harness remains: do not break game mechanics.

Preserve:

- control scheme
- player movement semantics
- collision semantics
- timing semantics
- scoring semantics
- fail/win conditions
- playable screen structure
- mobile actionability
- runtime stability

Favor:

- theme/world/copy changes
- asset mappings
- procedural drawings
- CSS/SVG/Canvas/DOM visuals
- HUD labels and instructions
- background/world identity
- safe progression framing
- non-invasive state labels

Avoid:

- rewriting game architecture
- changing physics constants without evidence
- deleting gameplay code
- replacing core loops
- changing input events in risky ways
- blocking progression behind untested menus
- introducing external dependencies

## Stage mission

Build the integrated design layer that later visual stages can execute:

1. translate the remix prompt into an authored world
2. align that world with the mechanic decomposition
3. define gameplay-facing theme semantics without changing mechanics
4. map existing media/assets/references into the new world
5. define the procedural character/item/prop language
6. preserve or impose a five-level progression model
7. produce durable artifacts for later visual/UI repair stages

## Part A — Mechanic-aware world interpretation

Read the inferred mechanics and explain how the theme maps onto them:

- player avatar becomes what?
- obstacles/hazards become what?
- collectibles/rewards become what?
- goals become what?
- score/progress becomes what?
- lives/health/failures become what?
- timers/pressure become what?
- level changes become what?

Each mapping must include a safety note:

- safe because it is cosmetic
- safe because it is copy/HUD only
- safe because it remaps existing media
- unsafe if it changes mechanic logic
- requires runtime verification

## Part B — Authored world and narrative frame

Define a world that is instantly recognizable and specific to the remix prompt.

Include:

- setting
- tone
- player role
- antagonist/pressure source
- reward fantasy
- failure fantasy
- level-to-level story escalation
- key nouns and visual motifs
- text/copy language style
- HUD vocabulary

The world must support animation and procedural art, not just static labels.

## Part C — Five-level progression execution

Use the Stage 0 five-level progression as binding. Expand it into gameplay-facing implementation guidance.

For each level:

- level name
- player-facing objective
- difficulty interpretation
- safe progression knob
- visual/world evolution
- background evolution
- character/item/prop additions
- HUD messaging
- what not to change mechanically
- likely implementation surface in existing code/assets

If the source game has no explicit levels, define progression in safe terms:

- round labels
- escalating background states
- score milestones
- cosmetic phase changes
- difficulty copy
- state-dependent visual changes
- optional safe hooks only if the source code already exposes them

## Part D — Media and asset mapping

Perform media mapping as part of world design.

Inventory and classify:

- current image assets
- audio assets
- CSS background images
- sprite references
- inline SVG/canvas drawing opportunities
- emoji/icon/text assets
- external URLs or brittle media references

For each media item, decide:

- keep
- replace with procedural drawing
- recolor/restyle
- rename/reframe
- remove if unused
- preserve as fallback
- repair if broken

Do not blindly delete assets. Do not leave broken references. Do not depend on network assets for core identity.

## Part E — Procedural character/item/prop system

Define a recognizable procedural library.

This must include:

- player character construction
- enemy/hazard construction
- collectible/reward construction
- environmental props
- UI icons
- particle/effect motifs
- background motifs
- silhouette rules
- animation rules

Prefer code-native implementations:

- CSS gradients
- CSS pseudo-elements
- SVG symbols
- inline SVG
- Canvas drawing helpers
- DOM shape components
- CSS keyframes
- lightweight procedural particles

The goal is that the player can recognize the remix even if every stock image is removed.

## Part F — Animated background and motion-graphic world

The background is not a wallpaper. It is an authored visual layer.

Define:

- base background layers
- level-reactive changes
- animated motion-graphic elements
- parallax/depth ideas
- progress-state changes
- safe performance limits
- mobile readability constraints
- how to keep gameplay foreground readable

Background animation must never hide controls, reduce contrast, or break touch targets.

## Part G — Design-system artifact

Create or update `remix_theme.json` if feasible. It should include:

- palette
- typography/copy tone
- shape language
- character motifs
- item motifs
- hazard motifs
- background motifs
- animation motifs
- HUD style
- level progression colors/motifs
- safe implementation notes

If a JSON file cannot be safely written, include the complete JSON payload in the result text.

## Part H — Local code-editing guidance

When editing files in this stage:

- make only changes aligned with world/design/media mapping
- do not perform final UI repair here
- do not perform aggressive console triage here
- do not make risky mechanic changes
- leave clear artifacts for the visual stages

## Required output

The final response/result must include:

- summary of implemented world mapping
- protected mechanics list
- media mapping decisions
- procedural art system decisions
- five-level progression support
- generated/updated artifacts
- changed files
- known risks for visual/UI/final repair stages

## Completion standard

This stage is complete when the game has a clear themed identity and the later visual stages can execute it without guessing character, item, background, level, or media rules.
""",
    },
    "02_creative_remix_v4_visuals_base.md": {
        "title": "Creative Remix v4 — Stage 2 — Visuals Base",
        "sources": [
            "03_creative_remix_v1_visuals.md",
            "05_creative_remix_v1_visual_judge.md",
        ],
        "body": r"""
# Creative Remix v4 — Stage 2 — Visuals Base

You are performing the main visual transformation pass. This stage should execute the authored world, procedural art system, animated background, recognizable characters/items/props, and level-reactive visual progression defined upstream.

This is not final mobile repair. This is not aggressive console triage. This is the primary art implementation pass while preserving mechanics.

## Inputs to consume

Use upstream artifacts and context:

- `remix_plan_v4.json` if present
- `remix_theme.json` if present
- Stage 0 mechanic decomposition and five-level visual plan
- Stage 1 world design, media mapping, and procedural art system
- current source code/assets
- existing visual state after prior stage

## Global mechanics invariant

Do not break mechanics. Do not rewrite core game logic. Visual transformation must ride on top of existing gameplay.

Protected:

- game loop
- controls
- collisions
- physics/timing
- score/progression semantics
- win/fail logic
- mobile input reliability

Safe surfaces:

- CSS
- DOM structure that does not affect controls
- SVG/canvas drawing helpers
- class names if updated consistently
- text/copy
- HUD styling
- generated procedural elements
- background layers
- asset replacement if references remain valid

## Visual objective

Create a game that looks intentionally remixed, not lightly reskinned.

The visual result must favor:

- procedural drawing
- code-native art
- animated backgrounds
- motion-graphic energy
- recognizable procedural characters
- recognizable icons/items/props
- level-reactive visual changes
- strong theme-specific identity
- readable HUD and foreground action

Avoid:

- generic gradients with no authored identity
- dominant stock-image wallpaper
- pasted images as the whole style
- noisy backgrounds that hide gameplay
- heavy external dependencies
- visual changes that alter hitboxes or controls

## Part A — Implement procedural art library

Where feasible, create reusable visual helpers:

- character drawing
- hazard drawing
- item/reward drawing
- background motifs
- particles/effects
- UI icon motifs

Possible implementation styles:

- CSS custom properties
- CSS classes and pseudo-elements
- inline SVG symbols
- generated DOM shapes
- Canvas helpers
- simple procedural drawing functions
- CSS keyframes and transitions

Keep the system lightweight and compatible with existing files.

## Part B — Implement animated background

The background must be a cool authored motion-graphic layer.

It should include:

- multiple layers
- gentle motion
- level/progress/state reactivity where safe
- theme-specific symbols
- depth/parallax if safe
- color/motif evolution
- readable contrast behind gameplay

Do not place important game information only in the background. Do not let background animation interfere with taps or pointer events.

## Part C — Implement recognizable characters/items/props

Make the main gameplay entities identifiable:

- player avatar
- enemies/hazards
- collectibles/rewards
- goals/portals/finish markers
- powerups or props if present
- ambient world objects

If the source uses sprites/images, either remap them safely or supplement them with procedural overlays. If the source uses pure DOM/canvas, add procedural drawing in the same style.

## Part D — Implement five-level visual progression

Use safe hooks to reflect the five-level plan:

- CSS variables per level
- score/phase based classes if existing state is available
- cosmetic labels
- background state changes
- HUD level badges
- progressive motif changes
- escalating particles/effects

If no explicit level system exists, implement a safe conceptual progression only when there is an existing score/phase/state surface to attach to. Otherwise leave a clear artifact for later stages.

## Part E — Preserve readability

Maintain:

- clear player visibility
- clear hazards
- clear rewards
- high contrast foreground
- readable HUD
- mobile-safe touch targets
- no clipped essential UI
- no overlays blocking gameplay

## Part F — Visual self-judge

Before finishing, inspect the result as if judging screenshots:

- Is the remix immediately recognizable?
- Is the background authored and animated?
- Are characters/items procedural and specific?
- Does the visual system support five-level progression?
- Is the HUD readable?
- Is the game still playable?

Fix obvious visual misses inside this stage if they are safe.

## Required output

Report:

- procedural art systems added
- animated background systems added
- recognizable entity treatments
- level-reactive visual hooks
- files changed
- mechanics preserved
- known issues for visual UI refine or final repair

## Completion standard

This stage is complete when the game has a strong procedural visual identity and animated world layer, while mechanics remain protected.
""",
    },
    "03_creative_remix_v4_visual_ui_refine.md": {
        "title": "Creative Remix v4 — Stage 3 — Visual UI Refine",
        "sources": [
            "06_creative_remix_v3_visual_ui_redesign.md",
            "05_creative_remix_v1_visual_judge.md",
        ],
        "body": r"""
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
""",
    },
    "04_creative_remix_v4_final_mobile_repair_aggressive.md": {
        "title": "Creative Remix v4 — Stage 4 — Final Mobile Repair Aggressive",
        "sources": [
            "09_creative_remix_v3_final_mobile_repair.md",
            "03_capture_mobile_screenshot.md",
            "11_creative_remix_v3_multilevel_qa.md",
        ],
        "body": r"""
# Creative Remix v4 — Stage 4 — Final Mobile Repair Aggressive

You are performing the final aggressive runtime, console, mobile, screenshot, and UI repair pass. This is the last production gate. It must be much more demanding than the old final mobile repair.

This stage fixes all reproducible console/runtime errors it can, explores the UI aggressively, captures screenshots as evidence, repairs visible layout defects, and verifies multiple screen states if possible.

## Absolute runtime discipline

Use only the assigned Playwright/runtime channel provided by the harness.

Do not use:

- external/system browsers
- random ports
- alternate local servers
- screenshots from unrelated sessions
- manual assumptions instead of runtime evidence

All screenshots and browser-grounded evidence must be written inside the attempt workspace if possible.

## Global mechanics invariant

Do not redesign the mechanics. Final repair may fix bugs, but it must not convert the game into another game.

Allowed repairs:

- console/runtime errors
- missing functions or broken references
- asset path bugs
- syntax errors
- viewport/mobile layout bugs
- pointer/touch actionability bugs
- z-index/overlay traps
- clipped controls
- start/restart/menu dead ends
- UI state bugs
- safe minor guards for null/undefined DOM elements
- safe event binding repairs

Not allowed:

- replacing the whole game loop
- changing the win/fail model for style reasons
- deleting major gameplay systems
- hiding broken mechanics under static screens
- weakening the game to pass visually

## Primary goals

1. Fix all reproducible console errors.
2. Run the game on the assigned mobile-sized viewport.
3. Capture screenshots continuously during exploration.
4. Perform guided monkey tapping / input probing.
5. Detect at least 3–4 distinct screen states if the game has them.
6. If 3–4 states cannot be reached, spend about 2 minutes actively trying.
7. Repair UI/layout defects visible in screenshots.
8. Re-check console after each meaningful repair.
9. Preserve procedural art direction and mechanics.

## Required exploration behavior

You must not stop after the initial screen unless the game truly has only one state.

Explore aggressively but intelligently:

- tap primary CTA
- tap play/start/restart buttons
- tap menus/icons/settings/help buttons
- tap HUD elements that appear interactive
- tap corners and obvious affordance zones
- swipe/drag if game genre suggests it
- use keyboard/mouse/touch equivalents if relevant
- wait briefly after interactions
- capture screenshots after state changes
- record what changed

Try to observe at least:

- initial/load state
- start/menu state
- active gameplay state
- failure/game-over state or next-level/progress state

If the game has more:

- pause/settings state
- level selection
- win screen
- reward/upgrade panel
- tutorial/help panel

## Console repair contract

Console errors are defects.

For each console error:

1. reproduce or identify source
2. inspect stack/message
3. fix the underlying cause if safe
4. reload
5. re-check console
6. repeat until clean or documented as non-blocking/external

Do not ignore:

- ReferenceError
- TypeError
- syntax errors
- asset loading failures that break visuals/gameplay
- missing DOM nodes
- failed event bindings
- blocked start buttons
- canvas/context errors
- unhandled promise rejections

Warnings may be documented if harmless, but runtime errors should be fixed.

## Screenshot-guided UI/layout repair

Screenshots are first-class evidence. Use them to fix:

- clipped layout
- controls outside viewport
- text overflow
- unreadable labels
- HUD overlap
- background hiding gameplay
- low contrast
- tiny touch targets
- modals cut off
- z-index traps
- safe-area issues
- horizontal scroll
- start/restart buttons hidden below fold
- level labels missing or unreadable
- procedural characters/items not recognizable enough

After fixing, capture fresh screenshots.

## Multi-screen/state requirement

Attempt to detect and document at least 3–4 distinct screen states.

A distinct state may be:

- loading/title
- menu
- active gameplay
- paused
- level changed
- score milestone
- failure/game over
- win/complete
- settings/help
- restart state

If fewer than 3 states exist, document evidence that the game is intentionally simple and record the exploration attempts.

## Visual integrity requirements

Do not flatten the v4 art direction while repairing.

Preserve:

- animated motion-graphic background
- level-reactive visual progression
- recognizable procedural characters/items/props
- procedural/code-native art system
- themed HUD language
- authored world identity

If a repair requires simplifying visuals for mobile readability, keep the identity and reduce only the defect.

## Final verification loop

Before completion:

1. reload game
2. check console
3. capture initial screenshot
4. interact through reachable states
5. capture screenshots for each state
6. confirm no blocking console errors
7. confirm mobile layout is not clipped
8. confirm touch controls/action buttons are accessible
9. confirm gameplay still starts and responds
10. document any remaining limitation

## Required output

Report:

- console errors found and fixed
- console errors remaining, if any, with reason
- screenshots captured
- screen states observed
- monkey exploration actions attempted
- layout/UI defects fixed
- mobile actionability status
- mechanics preservation statement
- files changed
- final risk notes

## Completion standard

This stage is complete only when the game has survived aggressive runtime exploration, console triage, screenshot-guided visual QA, and mobile layout verification without known blocking defects.
""",
    },
}


def read_source(name: str) -> str:
    path = PROMPTS / name
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def build_prompt(filename: str, spec: dict[str, object]) -> str:
    body = dedent(str(spec["body"])).strip()
    sources = list(spec["sources"])
    parts = [
        "<!-- CREATIVE REMIX V4 PRODUCTION PROMPT -->",
        "<!-- This file is new v4 material. Existing v3/v1 source prompts remain source-only and are not modified. -->",
        f"<!-- Generated: {datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')} -->",
        "",
        body,
        "",
        "---",
        "",
        "# Source-Derived Instruction Library",
        "",
        "The following source prompt material is retained with provenance markers so the v4 prompt remains comprehensive and auditable. During execution, follow the unified v4 contract above first, then use this source library for additional detailed constraints that do not conflict with the v4 stage purpose.",
        "",
    ]
    for source in sources:
        parts.extend(
            [
                "<!-- ====================================================================== -->",
                f"<!-- SOURCE: {source} -->",
                "<!-- ====================================================================== -->",
                "",
                read_source(source),
                "",
                f"<!-- END SOURCE: {source} -->",
                "",
            ]
        )
    return "\n".join(parts).rstrip() + "\n"


def write_v4_prompts() -> None:
    BUNDLES.mkdir(parents=True, exist_ok=True)
    for filename, spec in V4_PROMPTS.items():
        content = build_prompt(filename, spec)
        (PROMPTS / filename).write_text(content, encoding="utf-8")
        raw_parts = []
        for source in spec["sources"]:
            raw_parts.extend(
                [
                    f"<!-- SOURCE: {source} -->",
                    read_source(source),
                    f"<!-- END SOURCE: {source} -->",
                    "",
                ]
            )
        (BUNDLES / filename.replace(".md", ".raw_concat.md")).write_text(
            "\n".join(raw_parts), encoding="utf-8"
        )


def update_workflow() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    if '"creative_remix_v4": WorkflowDefinition(' in text:
        return

    needle = """    "creative_remix_v3": WorkflowDefinition(
        workflow_id="creative_remix_v3",
        run_label="creative-remix-v3",
        nodes=[
            {
                "id": "remix_inference",
                "prompt_file": "prompts/operators_v2/00_creative_remix_v3_remix_inference.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "narrative",
                "prompt_file": "prompts/operators_v2/01_creative_remix_v1_narrative.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "gameplay",
                "prompt_file": "prompts/operators_v2/02_creative_remix_v1_gameplay.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "visuals",
                "prompt_file": "prompts/operators_v2/03_creative_remix_v1_visuals.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "media_mapper",
                "prompt_file": "prompts/operators_v2/04_creative_remix_v1_media_mapper.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "visual_ui_redesign",
                "prompt_file": "prompts/operators_v2/06_creative_remix_v3_visual_ui_redesign.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "final_mobile_repair",
                "prompt_file": "prompts/operators_v2/09_creative_remix_v3_final_mobile_repair.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "level_adapter",
                "prompt_file": "prompts/operators_v2/10_creative_remix_v3_level_adapter.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
        ],
    ),
"""
    addition = needle + """    "creative_remix_v4": WorkflowDefinition(
        workflow_id="creative_remix_v4",
        run_label="creative-remix-v4",
        nodes=[
            {
                "id": "remix_inference_plus",
                "prompt_file": "prompts/operators_v2/00_creative_remix_v4_remix_inference_plus.md",
                "accepted_upstream_statuses": ["ok", "warning", "error"],
                "requires_contract": True,
            },
            {
                "id": "world_design_superprompt",
                "prompt_file": "prompts/operators_v2/01_creative_remix_v4_world_design_superprompt.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "visuals_base",
                "prompt_file": "prompts/operators_v2/02_creative_remix_v4_visuals_base.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "visual_ui_refine",
                "prompt_file": "prompts/operators_v2/03_creative_remix_v4_visual_ui_refine.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
            {
                "id": "final_mobile_repair_aggressive",
                "prompt_file": "prompts/operators_v2/04_creative_remix_v4_final_mobile_repair_aggressive.md",
                "accepted_upstream_statuses": ["ok", "warning"],
                "requires_contract": True,
            },
        ],
    ),
"""
    if needle not in text:
        raise RuntimeError("Could not find creative_remix_v3 workflow block to append v4 after.")
    WORKFLOW.write_text(text.replace(needle, addition), encoding="utf-8")


def update_journal() -> None:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    text = f"""# Creative Remix v4 Merged Prompt Workflow

## Task History
- Task 1 ({now}): Create a no-touch Remix v4 workflow by source-concatenating existing prompt files into new v4 production harnesses and registering a new `creative_remix_v4` workflow.

## Task 1 — Remix v4 merged prompts and workflow registration

### Status
Implemented.

### User Requirements Captured
- Do not modify existing Remix v3/v1 source prompt files.
- Create new Remix v4 prompt files/configuration only.
- Start by concatenating existing large prompt files into v4 draft files with provenance markers.
- Reduce/unify in chunks without losing context.
- Keep final v4 prompts long, comprehensive, and production-grade rather than compressed summaries.
- Preserve global harness invariants:
  - do not break mechanics
  - avoid risky gameplay logic rewrites
  - prefer procedural/code-native art
  - keep animated, level-reactive motion-graphic backgrounds
  - keep recognizable procedural characters/items/props
  - final mobile repair must aggressively fix console/runtime/mobile UI defects
- v4 target stages:
  1. remix inference plus mechanic decomposition / 5-level planning
  2. merged world design / narrative / gameplay / media mapping
  3. visual base transformation
  4. visual UI refinement
  5. aggressive final mobile repair

### Implementation Notes
- New v4 prompt files were generated from existing source prompts.
- Each new v4 prompt starts with a unified v4 production harness, then retains source prompt material as a provenance-marked instruction library.
- Raw source-concat archival bundles were created in `tools/game_refactoring/prompts/operators_v2/v4_source_bundles/`.
- `tools/game_refactoring/scripts/game_workflow.py` now has a new `creative_remix_v4` workflow entry.
- Existing Remix v3/v1 prompt files remain source-only and were not edited.

### New v4 Prompt Files
- `tools/game_refactoring/prompts/operators_v2/00_creative_remix_v4_remix_inference_plus.md`
- `tools/game_refactoring/prompts/operators_v2/01_creative_remix_v4_world_design_superprompt.md`
- `tools/game_refactoring/prompts/operators_v2/02_creative_remix_v4_visuals_base.md`
- `tools/game_refactoring/prompts/operators_v2/03_creative_remix_v4_visual_ui_refine.md`
- `tools/game_refactoring/prompts/operators_v2/04_creative_remix_v4_final_mobile_repair_aggressive.md`

### New Workflow
`creative_remix_v4` active stages:
1. `remix_inference_plus`
2. `world_design_superprompt`
3. `visuals_base`
4. `visual_ui_refine`
5. `final_mobile_repair_aggressive`

### Validation Plan
- Confirm v4 files exist.
- Confirm workflow resolves `creative_remix_v4`.
- Confirm source v3 prompt files were not modified by reviewing git diff scope.
"""
    JOURNAL.write_text(text, encoding="utf-8")


def main() -> None:
    write_v4_prompts()
    update_workflow()
    update_journal()
    print("creative_remix_v4_created")


if __name__ == "__main__":
    main()