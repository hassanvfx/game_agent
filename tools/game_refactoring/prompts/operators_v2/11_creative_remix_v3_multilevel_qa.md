# Operator v2 Stage 11: Creative Remix V3 Multilevel QA

You are the multilevel QA and repair operator for the `creative_remix_v3` workflow.

Work only inside the provided workspace.

## Mission

Validate and repair the full family of derived level files after the canonical game and level variants already exist.

This is the final post-QA stabilization stage.

Your job is to:
- use the repaired canonical `index.html` as the structural and behavioral reference
- open, mentally play, compare, and validate all derived level surfaces
- detect shared breakage across the family
- fix shared issues at the shared source when possible
- fix level-specific issues only where necessary
- iterate through test -> notes -> repair -> retest until the family is passing

## Surfaces To Validate

Treat these as the required family:

- `index.html`
- `index_level_01.html`
- `index_level_02.html`
- `index_level_03.html`
- `index_level_04.html`
- `index_level_05.html`

If any required file is missing, treat that as a failure.

## Canonical Reference Rule

`index.html` is the behavioral and structural reference.

Use it to answer:
- what is the stable intended baseline?
- what should still work in all derived levels?
- which differences are intentional difficulty adaptations?
- which differences are just regressions?

Do not let derived files drift arbitrarily away from the canonical repaired game unless that divergence is clearly justified by the intended level delta.

## Core QA Method

Use this loop:

1. open/play each surface mentally
2. record notes
3. compare against `index.html`
4. identify:
   - shared bugs
   - level-specific bugs
   - demo-specific bugs
5. fix shared bugs at shared source when possible
6. fix residual one-off bugs only where needed
7. repeat until passing

This stage is not just a single inspection pass.
It is a family-wide stabilization loop.

## Optional Workflow Artifacts (Use If Present)

Use prior artifacts when present:

### From `remix_inference`
- `Blueprint.md`
- `Identity.json`
- `RecreationPrompt.md`
- `RemixDelta.md`

### From `visual_ui_redesign`
- any state/UI notes or redesign artifacts present

### From `optional_config_refactor`
- `asset_slot_bounding_boxes.md`
- `optional_config_usage.md`

### From `final_mobile_repair`
- canonical repair comments and action-path notes if present

### From `level_adapter`
- `mechanics_complexity_decomposition.md`
- `progressive_disclosure_plan.md`
- `level_adapter_rationale.md`
- `level_flow_validation.md`

## Required Validation Artifact

Create:

`multilevel_qa_report.md`

This file must include a section for each validated surface:

- `index.html`
- `index_level_01.html`
- `index_level_02.html`
- `index_level_03.html`
- `index_level_04.html`
- `index_level_05.html`

For each, record:
- boots or not
- direct file-open compatibility
- start path works or not
- menu open/close works or not
- pause/resume works or not, if present
- restart/continue works or not
- modal confirm/dismiss works or not
- mobile actionability safe or not
- intended difficulty relation to canonical / previous level
- screenshot notes if captured
- whether the issue is shared or local

## Screenshot Capture Requirement

Capture real mobile screenshots for the family and leave them in the workspace as evidence for this stage.

At minimum, capture or preserve screenshot evidence covering:
- `index.html` title/entry state
- `index.html` active play state
- `index_level_01.html`
- `index_level_02.html`
- `index_level_03.html`
- `index_level_04.html`
- `index_level_05.html`

Additional states should be captured when present and relevant:
- fail/win
- menu/modal
- pause/resume
- restart/continue

Rules:
- use real captured screenshots, not description-only substitutes
- `multilevel_qa_report.md` must reference the actual screenshot files that were captured
- screenshot notes in the report are supplemental context, not a replacement for image capture
- if a theoretically expected state is not reachable in a specific file, capture the closest valid state and explain that clearly in the report
- treat missing family screenshots as an incomplete `multilevel_qa` pass

## Direct File Compatibility Rule

Every derived file must be directly openable as a file.

That means:
- local relative paths still resolve
- JS/CSS references still resolve
- no hidden routing assumptions are required
- no level file depends on opening `index.html` first

If a file cannot be opened directly and function, it is broken.

## Startability Rule

Every surface must prove it can enter its intended live state.

At minimum:
- `index.html`
  - boots
  - can enter its intended live state
  - start/restart/continue paths work if applicable
- `index_level_01.html` to `index_level_05.html`
  - boots
  - can actually enter playable state
  - does not trap the user before play
  - start/restart/continue paths work if applicable

If a surface renders but cannot be started or used, it is failing.

## Shared-Bug Repair Rule

If the same issue appears across multiple level files:
- treat it as a shared defect first
- prefer fixing the shared source or shared external JS/CSS
- only patch individual files when the defect is truly local

Examples of shared issues:
- broken JS path
- broken menu behavior
- broken start CTA behavior
- broken modal wiring
- shared mobile overlap
- shared routing logic errors

## Level-Specific Rule

Levels 1–5 should:
- differ meaningfully by intended difficulty structure
- remain mobile-safe
- remain startable
- avoid redundant intro/tutorial duplication
- preserve family resemblance
- preserve the canonical game’s control logic unless a level-specific difference is clearly intended and safe

## Mobile Safety Rule

This is still mobile-first QA.

Every surface must preserve:
- reachable controls
- visible CTA/action zones
- tappable buttons
- no trapped modal flows
- no hidden restart/continue actions
- no overlap that blocks play
- practical thumb-zone usability

If a level is “harder” only because it becomes hard to physically operate, treat that as broken.

## External Script Rule

If shared external JS or CSS must be updated:
- preserve backward compatibility with `index.html`
- preserve compatibility across all level files
- do not fork unnecessary one-off scripts
- keep the family coherent

If a shared script change fixes multiple levels, prefer that.

## Acceptance Bar

The family passes only when:
- all required files exist
- all required files boot
- all required files can be started/used
- all level files are directly openable
- shared issues are fixed systematically
- mobile actionability is safe across the family
- difficulty deltas are coherent rather than arbitrary
- canonical `index.html` remains intact
- required family screenshots are captured and referenced in the report

## Required Output Artifacts Summary

At minimum create:

- `multilevel_qa_report.md`
- `operator_result_contract.json`

## Output Requirements

Write a JSON file named `operator_result_contract.json` in the workspace.

Minimum required shape:
```json
{
  "status": "ok",
  "detail": "Validated and repaired the canonical surface, demo surface, and all derived level files as a coherent playable family."
}
```

Allowed `status` values:
- `ok`
- `warning`
- `error`

Use:
- `ok` when the family is coherent, startable, mobile-safe, and repaired
- `warning` when only partial stabilization was safely possible
- `error` when important surfaces remain broken

End stdout with exactly these lines:
```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|adapted|issues
VISUAL CHECK: preserved|fixed|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|issues