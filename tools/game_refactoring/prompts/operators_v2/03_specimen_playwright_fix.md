# Node 3: Specimen Playwright-Grounded Conservative Fix

Work only inside the provided workspace.

This is the browser-grounded conservative fix stage.

Your job is to use a bounded Playwright-assisted observation pass to gather stronger runtime evidence, then apply only minimal fixes for clearly confirmed problems.

## Prerequisites

This stage assumes Playwright is a shared machine/runtime prerequisite that has already been installed and configured outside the operator chain.

Use this stage only if all of the following are true:

- Playwright is already installed and configured in the shared runtime context used by the worker
- browser binaries required by Playwright are available in that shared runtime context
- the game can be launched locally from the workspace in a browser-accessible way
- you can run a short bounded interaction script without depending on undeclared external services

Do not require workspace-local `node_modules/playwright` as the source of truth if the shared runtime already provides Playwright.

If these prerequisites are not satisfied, do not fake browser grounding.
Document that the browser-grounded pass could not be executed, do not apply gameplay code edits, and fail in a blocked/no-edit state.

## Main operating stance

Be conservative.

The browser pass is for evidence gathering, not for justification of proactive rewrites.

Your default assumption must still be:
- the implementation is acceptable unless evidence strongly shows a real defect

That means:
- do not fix things just because they look stylistically weak
- do not redesign flows because you prefer a different UX
- do not perform broad cleanup
- do not patch uncertain issues

## Required bounded workflow

Follow this sequence:

1. read the analytical artifacts already present in the workspace
2. inspect the relevant local files statically
3. use the assigned validation localhost port from the runtime contract header
4. start a dedicated local HTTP server rooted at the current workspace on that assigned port
5. verify the server is reachable on the assigned port
6. build the exact served entry URL from the assigned host/port
7. launch the local game in a browser-controlled Playwright mobile flow
8. verify that the loaded runtime identity matches the workspace under review
9. run a short bounded mental-script-driven interaction pass
10. capture screenshots and runtime evidence
11. write an issue ledger
12. tear the local server down
13. only then decide whether a fix is justified

## Mental-script-driven browser pass

Use the earlier analytical outputs as rails for what should happen.

Your Playwright pass must stay short and targeted.

Use a proper mobile browser context, not a desktop browser resized down after launch.

Mobile context requirements:
- create a fresh isolated browser context for this run
- use a mobile-oriented browser context rather than a plain desktop page
- use viewport size `400 x 700`
- use screen size `400 x 700`
- enable touch behavior
- use a mobile / Android-style user agent
- keep this mobile context consistent for the whole bounded pass

Server lifecycle requirements:
- do not assume `http://127.0.0.1:8000/` or any other fixed port is safe unless it is the assigned validation port in the runtime contract header
- always use the assigned validation localhost port for the current run
- do not choose another port or attach to another local server
- always start a dedicated server for the current workspace on the assigned port
- always record the assigned host, port, and served entry URL
- always tear the server down after the pass, including on failure paths when possible

Runtime identity verification requirements:
- before trusting screenshots or browser observations, confirm that the loaded runtime matches the workspace under review
- verify identity using strong signals such as page title, key visible text, distinctive DOM markers, or other source-grounded signatures
- if the loaded runtime identity does not match the workspace, classify the result as a runtime-environment mismatch
- if a runtime-environment mismatch is detected, do not treat the screenshots as trustworthy gameplay evidence
- if a runtime-environment mismatch is detected, do not use that browser pass to justify gameplay/application code edits

Recommended flow:
- launch the local game in Playwright using the required mobile context and the assigned served entry URL
- open the initial game state
- capture the initial screenshot
- perform the first key user action
- capture the resulting screenshot
- perform the next critical interaction if relevant
- capture the resulting screenshot
- record visible breakage, dead interactions, layout failures, or runtime errors
- stop once enough evidence exists to classify the issue

Do not browse endlessly.
Do not improvise a huge exploration tree.
Do not treat browser access as permission for uncontrolled testing.

## Required evidence artifacts

Create these artifacts in the workspace:

1. `playwright_observation_log.md`
2. `playwright_console_errors.json` if any console/runtime errors are observed
3. `delta_issue_ledger.md`
4. `playwright_screenshots.json`

### `playwright_observation_log.md`
Include:
- how the game was launched
- what host, port, and served entry URL were used
- what mobile context settings were used
- whether runtime identity verification passed or failed
- what interaction steps were attempted
- what screenshots were captured
- what was expected at each step
- what actually happened
- whether the result confirms, weakly suggests, or fails to support a bug hypothesis

### Screenshot artifacts
Capture a small bounded set of screenshots, such as:
- initial state
- first meaningful action result
- first confirmed broken state if present
- post-fix verification state if a fix is actually applied

Name them clearly in the workspace.

### `playwright_screenshots.json`
Write a lightweight screenshot index.

Each entry should include only:
- `path`
- `step`
- `status`
- `observed`

Example shape:

```json
[
  {
    "path": "playwright_initial.png",
    "step": "initial_state",
    "status": "neutral",
    "observed": "start screen visible"
  }
]
```

## Issue ledger requirement

Before making edits, create a written issue ledger in the workspace named:

`delta_issue_ledger.md`

For each candidate issue include:

1. **Observed area**
   - file / feature / flow

2. **Static evidence**
   - code-level observation

3. **Browser evidence**
   - screenshot / interaction / runtime evidence

4. **Confidence classification**
   - `confirmed`
   - `likely`
   - `uncertain`

5. **Proposed action**
   - `fix`
   - `leave_as_is`
   - `monitor_only`

6. **Why**
   - one short reason

## Edit policy

- You may patch `confirmed` issues.
- You may patch `likely` issues only if the evidence is strong and the patch is minimal.
- You must not patch `uncertain` issues.
- If the browser pass is unavailable or inconclusive, leave the code unchanged.
- If Playwright cannot run or browsers cannot launch, you must not make gameplay/application code edits.
- If the server lifecycle cannot be established reliably, you must not make gameplay/application code edits.
- If runtime identity verification fails, you must not make gameplay/application code edits.

## Minimal patch rule

When you do fix something:
- prefer the smallest possible patch
- patch the specific break, not the surrounding style
- avoid touching unrelated code
- do not bundle cleanup with the fix
- stop editing once the confirmed problem is addressed

## Audio safety guardrail

Treat looping or long-running audio as a hard safety constraint.

Rules:
- any looping background music, ambience bed, or other long-playing continuous audio must not exceed **20% volume**
- if you find looped or continuous music/audio above 20% volume, reduce it to 20% or lower
- do not increase looping or long-running music above 20% volume during any fix
- short one-shot sound effects are not automatically subject to this cap unless they are used as sustained loops or effectively function as background audio

## Requirements

- Do not perform a broad redesign.
- Do not use uncontrolled browser exploration.
- Do not rely on MCP if Playwright/browser grounding is available.
- Keep the browser pass bounded and evidence-oriented.
- Use a proper mobile browser context with viewport and screen size `400 x 700`, touch enabled, and a mobile / Android-style user agent.
- Always use the assigned validation localhost port and tear the dedicated server down after the pass.
- Never choose another port or reuse another local server when the runtime contract assigns a validation URL/port.
- Always verify runtime identity before trusting browser evidence.
- Preserve the evidence-first confirmed/likely/uncertain policy.
- If unsure, leave the code alone and document the uncertainty.
- Missing Playwright or failed browser launch must produce a no-edit blocked outcome rather than a best-effort fix pass.

## Expected deliverables

By the end of this node, the workspace should contain:
- `playwright_observation_log.md`
- screenshots captured during the bounded browser pass
- `playwright_screenshots.json`
- `playwright_console_errors.json` if applicable
- `delta_issue_ledger.md`
- corrected implementation files only if clearly justified
- `operator_result_contract.json`

## Required contract artifact

Write a JSON file named `operator_result_contract.json` in the workspace.

If successful, write:

```json
{
  "status": "ok",
  "detail": "Ran a bounded Playwright-grounded conservative fix pass on the assigned validation port, captured browser evidence, documented an issue ledger, and applied only minimal fixes for clearly confirmed problems."
}
```

If no clearly justified code changes were needed, that is still a valid successful outcome as long as the evidence artifacts and issue ledger are present.

## If blocked

If you cannot complete the browser-grounded pass reliably, write:

```json
{
  "status": "error",
  "detail": "Could not complete the bounded Playwright-grounded conservative fix pass reliably."
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
