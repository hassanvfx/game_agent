# Runtime Naming Audit

This document records compatibility-sensitive naming references that remain after the documentation-first cleanup pass.

Its purpose is to separate:
- names that were safely cleaned in current-facing documentation
- names that remain in code/tests for compatibility or historical-fixture reasons
- names that may be candidates for a later reviewed rename

## Status after documentation cleanup

The current-facing documentation surface was cleaned so that repo identity now points to `game_refactoring` and the operator pipeline is the documented architectural center.

A focused code search still found a small set of compatibility-sensitive runtime references.

## Remaining code-facing references

### 1. `scripts/create_run.py`
Remaining reference:
- `run_game_remixer_<timestamp>`

Current role:
- default run ID prefix

Risk level:
- high

Why it remains:
- this value likely affects run directory naming, dashboards, existing artifacts, test assumptions, and operator/runtime tooling that may expect the current prefix format

Recommended treatment:
- defer rename until doing a dedicated compatibility-reviewed runtime migration

Recommended future options:
- keep as-is permanently if backward compatibility matters more than naming purity
- add a configurable run ID prefix later
- migrate to a new prefix only with an explicit transition plan for old/new run trees

## 2. `scripts/write_dashboard_launcher.py`
Remaining reference:
- `/tmp/game_remixer_dashboard_${PORT}.log`

Current role:
- temporary dashboard server log file name inside generated launcher content

Risk level:
- medium

Why it remains:
- low architectural importance, but it is still a runtime/helper behavior rather than a documentation string

Recommended treatment:
- safe candidate for later rename, but not necessary for the documentation-first pass

Recommended future options:
- rename to `/tmp/game_refactoring_dashboard_${PORT}.log`
- or use a more generic neutral name such as `/tmp/operator_pipeline_dashboard_${PORT}.log`

## 3. `scripts/test_media_mapper_prompt_fixture.py`
Remaining reference:
- fixture path under `runs/run_game_remixer_...`

Current role:
- historical fixture provenance embedded in a test input path

Risk level:
- low to medium

Why it remains:
- this appears to be a fixture snapshot referencing a real historical run directory, not active branding

Recommended treatment:
- leave unchanged unless the test is redesigned to use neutral synthetic fixture paths

Recommended future options:
- preserve as provenance if the exact run snapshot matters
- replace with a neutral fixture workspace if the test is rewritten to avoid dependence on historical run naming

## 4. `scripts/test_media_policy_fixture.py`
Remaining references:
- fixture path under `runs/run_game_remixer_...`
- `default_run_id()` context associated with historical fixture naming

Current role:
- historical fixture provenance and/or test support naming

Risk level:
- low to medium

Why it remains:
- appears tied to fixture snapshots and historical run-path assumptions rather than current-facing project identity

Recommended treatment:
- leave unchanged until the fixture strategy is redesigned

Recommended future options:
- preserve as-is if the test intentionally validates against historical fixture material
- replace with synthetic neutral test data later if the fixture set is modernized

## Rename classes going forward

### Rename now only with low risk
These can be renamed in a future small cleanup pass if desired:
- helper temp/log file names
- non-semantic generated launcher labels
- comments or variable names that are not part of compatibility-sensitive artifacts

### Rename later with migration review
These require a deliberate compatibility plan:
- run ID prefixes
- run directory naming conventions
- helper paths that assume old run tree names
- code symbols tied to orchestration or artifact discovery

### Usually leave unchanged
These are usually better treated as historical provenance:
- generated run artifacts
- historical fixture paths derived from real runs
- archived journals and reports

## Recommended next technical move

If the next goal is still cleanup rather than repurposing behavior, the safest follow-up is:

1. leave `run_game_remixer_*` unchanged for now
2. optionally rename only the helper temp log name in `write_dashboard_launcher.py`
3. leave fixture tests unchanged unless we are ready to redesign test fixtures
4. move on to designing the repurposed operator-step model

## Conclusion

The repo no longer has legacy naming in current-facing documentation, but a few code/test references remain for understandable reasons.

The key distinction is:

- documentation identity has been modernized
- runtime compatibility naming has not yet been migrated
- fixture provenance naming should not be rewritten casually

That separation keeps the codebase stable while preserving a path for a later, deliberate runtime rename pass.