flow# Visual Identity Contract

## Purpose
Define the shared visual identity contract that supports `operators_v2/02_visual_emoji_identity.md` and related operator stages as the primary authority for visual transformation.

## Authority Model
- `operators_v2/02_visual_emoji_identity.md` is the leading operational authority for visual identity work.
- `operators_v2/01_gameplay_narrative.md`, `operators_v2/03_media_mapper.md`, and `operators_v2/04_final_code_ui_mobile_repair.md` may further constrain or refine the result within their own scope.
- This root contract defines shared visual guardrails, mobile-first boundaries, and validation expectations.
- This file must support the operator pipeline and must not reintroduce older visual-only restrictions that conflict with active stages.

## Core Execution Model
- The source input is immutable.
- Work only on the provided working clone.
- Edit existing files in place unless repair or recovery requires a deeper intervention.
- Preserve gameplay logic, structure, interaction flow, DOM structure, asset wiring, and behavioral intent as much as possible while changing presentation.
- Do not replace the project from zero unless recovery or repair truly requires it.

## Visual Transformation Standard
The result should feel intentionally adapted, visually coherent, and meaningfully updated relative to the source while preserving gameplay truth.

Visual work may include:
- title and branding updates
- opening-state polish
- character-first presentation
- clearer UI hierarchy
- stronger palette cohesion
- thematic styling across panels, buttons, overlays, and feedback states
- lightweight expressive elements that remain safe for gameplay and mobile use

Visual work must not:
- change mechanics
- alter rules, pacing, difficulty, or win/loss behavior
- obstruct controls or gameplay space
- introduce decorative systems that make the game harder to read or use on small screens

## Mobile-First Layout Preservation
Mobile-first thinking is mandatory.

Hard rules:
- assume the incoming layout may already be reasonably mobile-friendly
- preserve the existing layout structure as closely as possible when it is already functional and readable
- make the smallest possible spacing, sizing, or positioning change needed to fix overlap, clipping, obstruction, or unreadability
- protect gameplay space, control hit zones, and critical HUD visibility first
- keep HUD, counters, cards, and overlays compact enough for narrow viewports
- avoid oversized labels, excessive padding, thick decorative chrome, and bulky UI blocks
- preserve visible and reachable actions in modals, overlays, and menus
- if a layout choice is readable but visually bulky, prefer the more compact readable option
- if a visual enhancement risks overlap or control obstruction, do not apply it

## Character-First Identity Guidance
When the active stage calls for stronger visual adaptation:
- prioritize the player-facing character or avatar as the clearest expression of identity
- derive enemies, collectibles, hazards, and UI accents from a coherent shared palette and shape language
- preserve strong existing handcrafted visuals where they are already effective
- enhance or frame existing assets rather than overwriting good craft with generic replacements

## Typography Guidance
- Typography should follow the active operator workflow and approved catalog or import model where applicable.
- Titles and branding may be more expressive.
- HUD, buttons, labels, and body text must remain compact and readable on small screens.
- Decorative typography must not dominate the viewport or reduce gameplay clarity.
- If the existing typography is already readable and mobile-safe, prefer minimal change.

## Color and Visual Effects Guidance
- Palette changes should be coherent and intentional.
- Preserve contrast, status clarity, outline legibility, and gameplay readability.
- Use glow, particles, transitions, or similar effects only when they remain lightweight, non-blocking, and visually helpful.
- Avoid visual noise, heavy rendering, or effects that obscure the play area.

## Scope Boundaries
This supporting contract is not a replacement for the staged operator prompts.

In practice:
- Stage 01 owns meaning, copy, narrative framing, and gameplay-aligned wording.
- Stage 02 owns visual identity, character-first presentation, and UI styling.
- Stage 03 owns audio, GIF, and font mapping from approved workflow sources.
- Stage 04 owns minimal repair of broken or unsafe UI, code, and mobile issues.

## Validation Expectations
A compliant visual result should satisfy all of the following:
- gameplay remains preserved
- the result looks intentionally adapted rather than accidentally degraded
- mobile usability remains intact or improves
- controls remain reachable and unobstructed
- the playfield remains visible enough for play
- title, UI, overlays, and key feedback states feel visually coherent
- layout remains close to the original when the original was already mobile-friendly
- visual ambition does not override compactness, readability, or safety

## Judge Failure Examples
Validation or review should fail when it observes:
- visual changes that alter gameplay behavior
- controls blocked by overlays or decorative layers
- oversized UI that occludes meaningful play space
- mobile layout regressions caused by unnecessary styling changes
- random or incoherent palette/application drift
- decorative media or styling that reduces clarity more than it helps
- heavy-handed redesign where minimal layout preservation was the safer choice