# Invariant Contract Merge Plan

This document outlines a safe plan for merging the current invariant policy/reference material into a single invariant contract markdown file.

It is a migration plan, not an implementation claim.

## Purpose

The current architecture treats invariant material as fixed context that should remain:

- always on
- not style-local
- not operator-specific
- not rewritten by the spec adaptor
- not dependent on remix prompt input

That makes a single invariant contract a good target architecture.

## Current evidence baseline

### Confirmed current invariant file set
From inspected `scripts/spec_adaptor.py`, the invariant reference files currently copied into the spec-adaptor workspace are:

- `audio_policy.md`
- `network_policy.md`
- `system_contract.md`
- `refactor_compliance_spec.md`

### Confirmed current usage pattern
- `scripts/spec_adaptor.py`
  - defines `INVARIANT_REFERENCE_FILES`
  - copies those files individually into `run_dir/spec_adaptor/invariants/`
  - includes them as fixed context in the recomposition harness
- no explicit direct string references to these exact filenames were found in the searched docs/prompt/config/style/script text scope outside the inspected spec-adaptor handling and related code paths

## Current interpretation

The current system appears to use invariant files mainly through:
- Python-side file enumeration/copying in `spec_adaptor.py`
- packet/prompt assembly paths that likely rely on the file content or copied artifacts rather than hard-coded filename references throughout the rest of the repo

This is encouraging, but not enough yet to perform the merge safely without a migration bridge.

## Why merging is attractive

A merged invariant contract would improve clarity by placing all non-negotiable constraints in one canonical source.

That should make it easier to reason about:

- system/runtime boundaries
- compliance constraints
- network restrictions
- audio restrictions
- artifact/evidence requirements
- gameplay-preservation invariants
- workspace/edit-scope constraints

It would also make the static layer of the architecture more explicit.

## Risks

### Risk 1 — `spec_adaptor.py` currently expects separate invariant files
This is a confirmed compatibility risk.

### Risk 2 — legacy prompt-generation paths may depend on existing policy-path semantics
This is likely, but still needs more code reading for exact confirmation.

### Risk 3 — prompts may conceptually rely on smaller policy separation
Even if filenames are not referenced directly, operator or legacy prompt logic may assume separate conceptual documents.

### Risk 4 — merging content too early could mix architectural cleanup with behavior change
A single merged file may alter emphasis, ordering, or interpretation even if the rules themselves do not change.

## Recommended migration strategy

Use a staged migration, not a direct replacement.

## Stage 1 — Planning and structure design
Do now in docs only.

Define the target merged file, for example:

- `prompts/invariant_contract.md`

Suggested section layout:

1. Purpose and scope
2. Workspace/edit-scope rules
3. Gameplay-preservation invariants
4. System/runtime safety constraints
5. Network restrictions
6. Audio restrictions
7. Compliance/refactor constraints
8. Artifact/evidence expectations
9. Priority and conflict-resolution rules

This stage should not change code behavior.

## Stage 2 — Create merged contract without removing old files
When implementing later:

- create the merged invariant contract
- keep old invariant files in place temporarily
- mark the merged contract as canonical in docs
- treat old files as compatibility-era split references

This minimizes disruption.

## Stage 3 — Add compatibility bridge in code
Update code carefully so both models can coexist during migration.

Possible bridge options:

### Option A — dual-copy bridge
- keep `INVARIANT_REFERENCE_FILES` temporarily
- also copy the merged `invariant_contract.md`
- prompts/harnesses can begin referring to the merged file while old files still exist

### Option B — single-source bridge via generated split files
- maintain one merged source file
- generate or mirror legacy split files from it for backward compatibility

This is cleaner long-term but more implementation work.

### Recommended choice
Start with **Option A** because it is lower risk.

## Stage 4 — Update consuming paths
After the bridge exists, update:
- `spec_adaptor.py` harness wording
- any legacy prompt generation paths
- any packet-generation logic
- docs describing invariants

Goal:
- move consumers conceptually toward one canonical invariant contract

## Stage 5 — Retire the split files
Only after all consumers are verified should the repo consider:
- deleting old split files
- or retaining them as generated compatibility shims

## Safe implementation order

1. keep this plan doc
2. continue evidence reading for remaining prompt/packet consumers if needed
3. create merged invariant contract file
4. do compatibility-bridge update in code
5. validate spec-adaptor and legacy paths
6. only then consider deprecating split files

## What should not change during merge

The invariant merge should not change the actual meaning of the invariant rules.

Specifically, it should preserve:

- no-network rules
- audio restrictions
- system/runtime boundaries
- compliance/refactor constraints
- playability-preservation expectations
- artifact/evidence requirements

The merge is primarily a **packaging and boundary cleanup**, not a policy rewrite.

## Relation to static vs dynamic model

The merged invariant contract belongs clearly in the **static layer**.

That is good because:
- it reduces fragmentation in the static layer
- it strengthens the boundary between invariant context and dynamic runtime adaptation
- it makes spec adaptor responsibilities easier to explain

## Blind spot warning

A likely blind spot would be assuming that “no direct filename string matches in docs/prompt files” means the merge is immediately safe.

That may be false because:
- packet-generation paths may still load policies indirectly
- legacy flow may rely on split conceptual structure
- prompts may rely on separate emphasis even when filenames are not hard-coded

So this plan should remain migration-oriented, not replacement-oriented.

## Recommended next supporting evidence
If we want even tighter safety before implementation, inspect:
- `scripts/generate_task_packet.py`
- any prompt/template files used by legacy flow
- additional operator prompt files if they mention invariant concepts structurally

## Working summary

The merge idea is good.

The safe way to do it is:

- define one canonical merged invariant contract
- keep old split files temporarily
- add a compatibility bridge
- migrate consumers gradually
- only retire split files after validation

That preserves architecture clarity without making a blind compatibility-breaking move.