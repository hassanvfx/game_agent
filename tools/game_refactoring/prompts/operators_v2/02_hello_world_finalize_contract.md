# Operator Stage: Hello World Finalize Contract Proof

You are the second-stage proving operator for chaining-policy validation.

## Goal

Work only inside the provided workspace.

Read the current `index.html` and confirm the visible player-facing text is already in Spanish.

If the page currently shows `Hola Mundo`, make a tiny safe follow-up update:
- change the visible heading text to `¡Hola Mundo!`

If the workspace does not already contain the successful Spanish output expected from the previous stage, do not guess and do not repair broadly.

## Required edit

- Only make the small follow-up update when the visible heading already reflects the prior-stage Spanish result.
- Preserve existing HTML structure and styling unless a tiny safe adjustment is absolutely required.
- Do not introduce new dependencies.
- Do not change unrelated content.

## Required contract artifact

Write a JSON file named `operator_result_contract.json` in the workspace with exactly these keys:

```json
{
  "status": "ok",
  "detail": "Validated prior Spanish output and finalized the visible heading."
}
```

## Allowed status values

- `ok`
- `warning`
- `error`

## If blocked

If the expected prior-stage Spanish output is missing:
- do not fake success
- write:

```json
{
  "status": "error",
  "detail": "Expected upstream Spanish heading was not present."
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
