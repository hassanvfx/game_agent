# System Contract

## Purpose
Define the shared operating contract for the standalone whitelabel agent orchestration platform, with `operators_v2/` as the primary transformation workflow authority.

## Authority Model
- The `operators_v2/` stage prompts are the leading transformation principles for gameplay adaptation, visual identity, media mapping, and final repair.
- Root-level contracts define platform invariants, shared safety rules, validation expectations, and cross-stage constraints.
- Root-level contracts must support the operator pipeline and must not contradict stage behavior unless they define universal platform safety or publish-blocking requirements.
- If a supporting root policy is ambiguous, interpret it in the way most compatible with the active `operators_v2/` stages.

## Core Guarantees
- Source game folders are immutable inputs.
- Every transformation operates on a working clone.
- Transformations are executed through the staged operator pipeline.
- Publish occurs only after validation and judge pass.
- Important state transitions must be persisted to disk.
- Shared contracts and policies are read before editing begins.

## Cross-Stage Invariants
- Preserve gameplay logic, controls, win/loss behavior, boot flow, and core interaction semantics unless an explicitly authorized stage says otherwise.
- Mobile-first thinking is mandatory across all stages.
- Assume the incoming game may already be reasonably mobile-friendly.
- Preserve the existing layout structure as closely as possible when it is already functional, readable, and mobile-safe.
- Make the smallest layout or UI change necessary to fix overlap, unreadability, obstruction, off-screen actions, broken controls, or unsafe spacing.
- Protect gameplay space, control hit zones, and critical visibility before decorative ambition.
- Avoid bulky HUD, oversized overlays, and inflated typography on narrow screens.
- If a choice is between more decorative UI and more compact readable UI, choose the compact readable option.
- Do not rebuild the project from zero unless recovery or repair truly requires it.

## Execution Model
1. ingest manifest
2. validate inputs
3. create run workspace
4. clone source to working area
5. execute operator pipeline attempts
6. execute judge / validation pass
7. retry up to three attempts if needed
8. validate outputs
9. publish compliant output
10. refresh dashboard state

## Operator Pipeline Model
The primary transformation workflow is the following staged sequence:

1. `operators_v2/01_gameplay_narrative.md`
   - adapt gameplay framing, copy, labels, instructions, title, and narrative interpretation
   - preserve mechanics and gameplay truth

2. `operators_v2/02_visual_emoji_identity.md`
   - apply visual identity, character-first presentation, UI clarity, and mobile-safe redesign
   - preserve gameplay and avoid unsafe visual overreach

3. `operators_v2/03_media_mapper.md`
   - map approved media, audio, GIF, and font usage from workspace-local catalogs
   - integrate media without changing mechanics

4. `operators_v2/04_final_code_ui_mobile_repair.md`
   - perform strict non-gameplay repair
   - fix breakage, unsafe UI, mobile issues, and dependency problems with minimal intervention

## Validation Model
- Validation should assess outputs against the active operator stage requirements plus the shared root-level contracts.
- Supporting policies should refine operator behavior rather than compete with it.
- Mobile safety, layout preservation, control accessibility, and gameplay continuity are publish-level concerns.
- A visually ambitious result that harms gameplay clarity, mobile usability, or operator compliance should fail validation.

## Observability Contract
- Canonical state lives in JSON / JSONL on disk.
- HTML views are read-only polling surfaces over those canonical files.
- Progress and validation artifacts should reflect staged execution clearly enough for later audit and retry handling.