# Node 2: Specimen Runtime QA, Browser Automation, And Fix Pass

Work only inside the provided workspace.

Your job is to make this game runnable and interactively testable only in cline cli browser tool, then fix issues you find.

## Main responsibilities

1. Figure out how to serve the game from the repository root using Python.
2. Obtain a random free port.
3. Retry until the local server starts successfully.
4. Use Cline browser automation to open the served game.
5. Try to play it.
6. Tap or click the main button to enter gameplay.
8. Fix whatever breaks.
6. Tap or click the secondary button to enter gameplay.
8. Fix whatever breaks.
6. Tap or click the therriary button to enter gameplay.
8. Fix whatever breaks.
9. Repeat until the game is playable enough for a basic smoke test.

## Browser requirement

You must explicitly use Cline browser automation for:
- opening the served URL
- interacting with the game
- tapping/clicking the primary entry button
- capturing screenshots during the flow
- rechecking behavior after fixes

Do not open the external/default/system browser.
Do not use OS-level browser launch commands as a fallback.
Do not rely only on static inspection if browser interaction is needed to validate the game.

If you do not know how to correctly use Cline browser automation for this node, you must fail instead of guessing.

## Requirements

- Keep changes focused on runtime/playability fixes.
- Do not do broad redesign work.
- Do not redo the inference/classification work from node 1.
- If browser/runtime issues appear, fix the actual source files inside the workspace.
- Save screenshots you capture inside the workspace with clear names.
- Preserve the game’s intended behavior as much as possible while making it runnable.
- If you start a local Python server, you must shut it down before completion.

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
  "detail": "Served the game locally, used Cline browser automation to interact with it, captured screenshots, fixed runtime/playability issues, and shut the server down cleanly."
}
```

## If blocked

If you cannot get the game into a basically playable tested state, or if you cannot correctly use Cline browser automation, or if you fail to shut the server down, write:

```json
{
  "status": "error",
  "detail": "Could not complete the runtime QA and browser-automation fix pass safely."
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
