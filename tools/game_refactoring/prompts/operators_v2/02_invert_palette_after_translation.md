# Operator Stage: Invert Palette After Translation

You are the second-stage proving operator for real-game chained contract validation.

## Goal

Work only inside the provided workspace.

Read the current game files and confirm the visible player-facing text is already in Spanish from the previous node.

Only if that prior Spanish translation is clearly present, perform a second-stage visual transformation:
- invert the main color palette across the player-facing UI and game styling
- keep gameplay, controls, layout, and overall structure intact

This stage is not allowed to do the primary translation itself. It must validate that translation already happened before making the palette change.

## Upstream validation requirement

Before changing anything, verify that the current workspace already contains clear Spanish-visible UI text, such as Spanish menu labels, buttons, HUD labels, headings, or game-over text.

If the workspace does not already show convincing Spanish-visible output from the prior node:
- do not guess
- do not broadly rewrite copy
- do not silently continue
- fail contractually

## Required edit

If upstream Spanish output is present:

- invert or strongly reverse the main palette used by the page
- update CSS variables, inline colors, gradients, shadows, overlays, canvas styling, and other palette-driving values as needed
- preserve readability on mobile
- preserve gameplay behavior and controls
- do not remove required assets or break audio wiring
- keep changes focused on palette inversion / visual reversal rather than a whole redesign

The result should be visibly different from node 1, with a substantially inverted or reversed dark/light and accent balance.

## Required contract artifact

Write a JSON file named `operator_result_contract.json` in the workspace.

If successful, write exactly this shape:

```json
{
  "status": "ok",
  "detail": "Validated upstream Spanish translation and inverted the game palette while preserving gameplay."
}
```

## Allowed status values

- `ok`
- `warning`
- `error`

## If blocked

If the expected upstream Spanish output is missing, write:

```json
{
  "status": "error",
  "detail": "Expected upstream Spanish translation was not present, so palette inversion was not applied."
}
```

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
