# Node 1: Specimen Runtime QA, Playability, And Fix Pass

Work only inside the provided workspace.

Your job is to make this game runnable and interactively testable in a browser, then fix issues you find.

## Main responsibilities

1. Figure out how to serve the game from the repository root using Python.
2. Obtain a random free port.
3. Retry until the local server starts successfully.
4. Open the served game in a browser.
5. Try to play it.
6. Tap or click the main button to enter gameplay.
7. Capture screenshots as you interact.
8. Fix whatever breaks.
9. Repeat until the game is playable enough for a basic smoke test.

## Requirements

- Keep changes focused on runtime/playability fixes.
- Do not do broad redesign work.
- Do not do abstract classification/inference work in this node.
- If browser/runtime issues appear, fix the actual source files inside the workspace.
- Save any screenshots you capture inside the workspace with clear names.
- Preserve the game’s intended behavior as much as possible while making it runnable.

## Serve requirement

You should reason explicitly about how to:
- run a Python HTTP server from the correct root
- choose a random free port
- retry if the port or server start fails
- use the served URL for browser testing instead of relying on raw `file://` loading

## Expected deliverables

By the end of this node, the workspace should contain:
- the fixed runnable game
- one or more screenshots captured during the interaction/testing pass

## Required contract artifact

Write a JSON file named `operator_result_contract.json` in the workspace.

If successful, write:

```json
{
  "status": "ok",
  "detail": "Served the game locally, interacted with it, captured screenshots, and fixed runtime/playability issues."
}
```

## If blocked

If you cannot get the game into a basically playable tested state, write:

```json
{
  "status": "error",
  "detail": "Could not complete the runtime QA and fix pass safely."
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
