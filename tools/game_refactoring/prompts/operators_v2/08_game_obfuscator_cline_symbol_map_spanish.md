# Operator v2 Stage 08: Game Obfuscator Cline Symbol-Map Spanish Rename

You are performing a narrow, deterministic, cross-file code-surface rewrite pass.

Your job is to make the retained code surface look moderately different without changing behavior.

This is a study workflow, not a full creative remix, not a mobile repair pass, and not a runtime/media recovery pass.

## Core Goal

Apply a modest, safe, consistent rename pass across the retained code surface by:

1. building a single symbol map first
2. choosing a safe subset of non-visible symbols
3. renaming them consistently from English-style names to Spanish-style names
4. updating all retained callsites consistently across HTML, JS, and CSS
5. stopping early rather than chasing exhaustive coverage

A modest result is acceptable.

You do **not** need to rewrite everything.
Roughly 20% meaningful code-surface change is enough if it is consistent and safe.

## Retained Surface Rule

Treat the retained workspace as one linked code surface.

The retained surface consists only of:
- `index.html`
- retained `.js` files
- retained `.css` files

You must treat those files as a linked system.

Do not treat files independently if a symbol or selector crosses file boundaries.

## Hard Constraints

- DO NOT intentionally change gameplay, rules, win/loss conditions, scoring, progression, pacing, controls, or logic flow
- DO NOT add build tooling
- DO NOT add frameworks or module systems
- DO NOT move files
- DO NOT split files
- DO NOT inline or flatten files as part of this pass
- DO NOT rename visible/player-facing strings
- DO NOT rename browser APIs, DOM built-ins, library globals, event names, or other uncertain/public contracts
- DO NOT touch media handling, runtime repair, mobile repair, or cosmetic UI redesign
- DO NOT perform broad refactors
- DO NOT force exhaustive symbol coverage
- DO NOT make speculative changes when linkage is uncertain

## Required Sequence

### Phase 1: Retained Surface Inventory

Inspect the retained surface and create a concise artifact:

- `retained_surface_manifest.json`

Include:
- retained files
- file roles (`html`, `js`, `css`)
- obvious cross-file linkage points when visible
  - script references
  - stylesheet references
  - DOM ids/classes referenced from JS
  - selectors referenced across HTML/CSS

### Phase 2: Global Symbol Map

Build one global symbol map across the full retained surface.

Create:

- `obfuscation_symbol_map.json`

Include only symbols you can trace safely across all retained files.

Good candidate categories:
- local/helper function names
- local variables
- internal constants
- simple DOM reference variable names
- internal helper object names
- safe CSS class/id names only if every retained reference can be updated consistently

Rename style:
- Spanish-oriented, readable, consistent names
- examples:
  - `updateScore` -> `actualizarPuntaje`
  - `playerVelocity` -> `velocidadJugador`
  - `gameLoop` -> `bucleJuego`
  - `startButton` -> `botonInicio`

Do not use random gibberish.
Do not use unstable naming.
Keep naming deterministic and interpretable.

### Phase 3: Safe Subset Selection

You are not required to rename everything.

Choose a modest safe subset.

A symbol is eligible only if:
- it is non-visible
- it is fully traceable across the retained surface
- all retained references can be updated consistently
- it does not appear to be a browser/public/library contract
- changing it will not break HTML↔JS↔CSS linkage

If uncertain, skip it.

### Phase 4: Consistent Cross-File Rewrite

Apply the selected rename map consistently across:
- `index.html`
- retained `.js`
- retained `.css`

Preserve:
- HTML ↔ JS linkage
- HTML ↔ CSS linkage
- JS ↔ JS callsites
- CSS selector linkage when touched
- script/style file references

Do not perform unrelated restructuring.

Small, low-risk shape changes are allowed only when bundled naturally with the rename pass:
- touching one line in a function signature
- renaming a local helper and its calls
- regrouping one tiny declaration cluster if needed for consistency

Do not turn this into a large refactor.

### Phase 5: Contract Report

Create:

- `obfuscation_contract_report.json`

Include:
- retained files
- rename candidates considered
- accepted renames
- skipped renames
- skipped reasons
- linkage-sensitive items preserved intentionally
- short summary of the approximate scope of change

## Decision Rule

When choosing between:
- more change with more uncertainty
- less change with high confidence

Prefer the lower-risk option.

A smaller but consistent rename pass is better than a larger risky pass.

## Output Requirements

Write these artifacts if possible:
- `retained_surface_manifest.json`
- `obfuscation_symbol_map.json`
- `obfuscation_contract_report.json`
- `operator_result_contract.json`

Write `operator_result_contract.json` in the workspace.

If the study completes successfully, write:

```json
{
  "status": "ok",
  "detail": "Built a retained-surface manifest, created a global symbol map, and applied a modest cross-file Spanish-style rename pass while preserving mechanics and linkage."
}
```

If no safe changes are justified but the study still completed safely, write:

```json
{
  "status": "ok",
  "detail": "No safe cross-file rename changes were justified, but the retained surface was inspected and study artifacts were produced."
}
```

If the study fails, write:

```json
{
  "status": "error",
  "detail": "Unable to complete the retained-surface rename study safely."
}
```

End stdout with exactly:

```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved
LINKAGE CHECK: preserved|issues
OBFUSCATION CHECK: applied|partial|failed
```

If no safe changes are justified, that is acceptable. In that case end with:

```text
OPERATOR STATUS: completed
CHANGED FILES: NONE
SUMMARY: no safe cross-file rename changes applied
MECHANICS CHECK: preserved
LINKAGE CHECK: preserved
OBFUSCATION CHECK: failed
```
