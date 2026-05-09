# Operator Stage: Capture Mobile Screenshot Artifact

You are the third-stage proving operator for artifact-capture validation.

## Goal

Work only inside the provided workspace.

This stage must only run after the previous stages have already:
1. translated the game to Spanish
2. inverted the palette

Validate that the player-facing game already reflects those prior-stage outcomes, then produce a screenshot artifact named `screen1.jpg`.

## Required upstream validation

Before doing anything else, confirm that:
- visible UI text is already in Spanish
- the palette has already been visibly altered from the earlier dark-red horror styling into the new post-inversion look

If either condition is missing:
- do not guess
- do not try to redo prior stages
- fail contractually

## Required artifact

Produce a screenshot file named exactly:

```text
screen1.jpg
```

The screenshot should represent the finished game in a mobile viewport target of:

```text
375 x 667
```

Save `screen1.jpg` inside the provided workspace.

## Allowed ways to complete the task

You may use the tools available to you in the Cline worker environment to open the finished game, render it, and capture the image artifact.

If browser/runtime validation is required for this stage:
- use only the assigned validation localhost URL/port from the runtime contract header
- do not choose another localhost port
- do not attach to another local server
- write screenshots only inside the current attempt workspace

The important requirement is the resulting artifact:
- `screen1.jpg` must exist
- it must be a real screenshot of the finished transformed game
- do not substitute placeholder text files or fake image outputs

## Required contract artifact

Write a JSON file named `operator_result_contract.json` in the workspace.

If successful, write exactly this shape:

```json
{
  "status": "ok",
  "detail": "Validated the upstream Spanish translation and palette inversion using the assigned validation runtime and then captured screen1.jpg."
}
```

## Allowed status values

- `ok`
- `warning`
- `error`

## If blocked

If the expected upstream transformed game state is missing, or if `screen1.jpg` could not be produced, write:

```json
{
  "status": "error",
  "detail": "Expected upstream transformed game state or screenshot artifact was not produced."
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
