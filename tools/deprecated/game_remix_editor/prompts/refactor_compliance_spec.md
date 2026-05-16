# Refactor Compliance Spec

## Purpose
Define the baseline compliance targets for the operator-driven refactor system, with `operators_v2/` as the primary workflow authority and root-level contracts acting as supporting validation rules.

## Authority Model
- Compliance is evaluated against the staged operator pipeline first.
- Root-level contracts refine validation, safety, and publish readiness.
- When older root-level assumptions conflict with the stage prompts, validation should follow the operator pipeline unless a universal platform invariant is at risk.

## Required Compliance Themes
- output remains reconstructable from saved evidence
- transformed result is produced from a working clone
- required artifacts exist for each attempt
- stage outputs remain reviewable by judge and validators
- publish is blocked until validators pass
- gameplay, controls, boot flow, and win/loss behavior remain preserved unless a stage explicitly authorizes otherwise
- mobile-first usability is preserved across all stages
- layout remains as close as practical to the incoming structure when the original layout is already functional and mobile-safe

## Stage-Aware Compliance Expectations

### Stage 01 — Gameplay + Narrative Adaptation
- narrative changes must map to implemented gameplay
- instructions must match real actions and outcomes
- no new mechanics may be implied through text
- title, onboarding, HUD copy, and result language must remain internally consistent
- visible text should be normalized to English where applicable

### Stage 02 — Visual / Emoji Identity
- visual identity changes must preserve gameplay behavior
- character-first presentation and UI clarity should be visibly improved where appropriate
- visual work must remain mobile-first
- UI changes must avoid overlap, blocked controls, off-screen actions, and playfield occlusion
- if the existing layout is already mobile-friendly, the spatial structure should remain close to the original

### Stage 03 — Media Mapper
- approved workspace-local catalogs are the authority for media mapping when applicable
- required media integration must be actually wired, not merely suggested
- audio, GIF, and font changes must not alter mechanics
- media usage must be non-blocking, failure-tolerant, and mobile-safe
- unresolved disallowed or invalid media references should fail compliance

### Stage 04 — Final Code / UI / Mobile Repair
- only broken, unsafe, or non-functional issues should be repaired
- fixes must be minimal and non-gameplay
- repair should preserve the prior stage intent while restoring stability, readability, and mobile safety

## Mobile-First Compliance Requirements
- controls remain reachable on narrow viewports
- gameplay-critical areas remain visible
- HUD, overlays, cards, and panels remain compact enough for small screens
- modal actions remain visible and accessible
- text remains readable without dominating the viewport
- layout changes should be minimal when the incoming layout is already mobile-safe
- decorative changes must never take priority over compactness, control safety, or playfield visibility

## Evidence Requirements
Each attempt should preserve enough evidence for structured review, including:
- changed files
- stage completion state
- concise summaries of meaningful changes
- documented exceptions or blockers
- progress or validation artifacts required by the active workflow

## Retry Loop
- Attempt 1: initial staged operator pass
- Attempt 2: remediation using judge or validator feedback
- Attempt 3: final remediation pass
- Preserve all attempt artifacts even when superseded

## Failure Conditions
A refactor attempt should fail compliance when it shows any of the following:
- output cannot be reconstructed from saved evidence
- required stage artifacts are missing
- gameplay truth is contradicted by narrative or UI text
- mechanics, controls, pacing, or win/loss behavior are altered by a non-authorized stage
- UI overlap, blocked controls, off-screen actions, or severe mobile occlusion remain
- media requirements or media safety rules required by the active stage remain unresolved
- repair work introduces unnecessary redesign instead of minimal stabilization
- validator or judge cannot clearly verify what changed and why

## Non-Goals For This Milestone
- bounded concurrency
- multi-worker scheduling
- final schema enforcement logic