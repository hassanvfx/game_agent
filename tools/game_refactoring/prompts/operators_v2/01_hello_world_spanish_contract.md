# Operator Stage: Hello World Spanish Contract Proof

You are the proving-stage operator for a minimal contract test.

## Goal

Work only inside the provided workspace.

Find the visible `Hello World` text in `index.html` and translate it to Spanish as `Hola Mundo`.

## Required edit

- Update the visible player-facing text from `Hello World` to `Hola Mundo`.
- Preserve the existing HTML structure and styling unless a tiny safe change is absolutely required.
- Do not introduce new dependencies.
- Do not change unrelated content.

## Required contract artifact

After making the edit, write a JSON file named `operator_result_contract.json` in the stage attempt root provided by the runner.

The file must contain exactly these keys:

```json
{
  "status": "ok",
  "detail": "Translated visible Hello World text to Spanish."
}
```

## Allowed status values

- `ok`
- `warning`
- `error`

## Status meaning

- `ok`: the visible text was successfully translated and the page structure remains usable
- `warning`: the main task was completed but there is a minor issue worth reporting
- `error`: the task could not be completed safely

## Detail field

- Must be a short human-readable sentence
- Must describe what happened
- Must not be empty

## If blocked

If you cannot safely complete the task:
1. do not fake success
2. write `operator_result_contract.json` with:
   - `status: "error"`
   - a short `detail` explaining the blocker

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

For this proving stage:
- `MECHANICS CHECK` should normally be `preserved`
- `AUDIO CHECK` should normally be `not_applicable`
- `MOBILE CHECK` should normally be `safe`