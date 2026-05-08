# Node 2.5: Specimen Playwright Setup And Verification

Work only inside the provided workspace.

Your job is to prepare and verify a usable Playwright environment for the later browser-grounded fixer stage.

This is an environment-preparation stage, not a gameplay-fix stage.

## Mission

Determine the actual execution environment the worker is using, install Playwright into that same environment if needed, install the required browser binaries if needed, and verify that a minimal browser launch works.

For this experiment, you must **force reinstall Playwright and its browser binaries on every run** even if they appear to already exist.

Treat this forced reinstall mode as mandatory for the current run unless a future prompt explicitly disables it.

If this setup cannot be completed reliably, stop and report failure.
Do not make gameplay code changes in this stage.

## Required execution-context policy

You must detect and use the same environment context the current worker is actually running under.

Prefer, in this order when applicable:
1. project-local runtime environment
2. active virtual environment / isolated environment
3. project-local npm / node_modules context
4. only fall back to global tooling if no local isolated context exists

Do **not** install Playwright into an arbitrary unrelated environment and assume the worker can see it.

## Setup workflow

Follow this sequence:

1. inspect the current workspace for runtime context clues
   - package manifests
   - local node_modules presence
   - virtual environment clues
   - lockfiles
   - existing browser tooling hints

2. determine the most likely actual execution context

3. immediately write placeholder/progress artifacts before any long install step
   - create `playwright_setup_status.json`
   - create `playwright_setup_report.md`
   - mark them with a clear in-progress state such as:
     - `phase: installation_in_progress`
     - `ready_for_browser_stage: false`
     - `install_attempted: false`
   - explicitly note that the stage must come back and overwrite/finalize these artifacts after verification

4. run Playwright preflight checks
   - can the module be resolved from the actual runtime context?
   - are required browser binaries present?
   - can a minimal browser launch succeed?

5. if Playwright or browser binaries are missing, attempt installation into the same context

6. because forced reinstall mode is active for this experiment, reinstall Playwright and its browser binaries even when an existing installation is detected, while staying inside the correct runtime context

7. rerun the same preflight checks

8. overwrite the placeholder/progress artifacts with final results

9. write `operator_result_contract.json`

10. immediately finalize by ending stdout with the exact required stdout contract block and then stop
   - do not leave the stage hanging after install/verification
   - do not keep long-running child processes alive
   - do not continue with exploratory work after the setup report, status artifact, and contract are written

## Allowed install behavior

If installation is needed, you may perform a bounded install step appropriate to the detected environment.

Because this experiment requires **force install/reinstall on every run**, you must do that while ensuring:
- the reinstall happens in the same detected runtime context
- the report clearly states that force reinstall mode was used
- the final verification still passes afterward

Examples of the kind of actions that may be appropriate:
- install Playwright package into the project-local node environment
- install Playwright package into the active Python environment
- install required browser binaries through the matching Playwright toolchain

You must keep the install logic aligned to the detected runtime context.
Do not mix contexts casually.

## Required artifacts

Create:

1. `playwright_setup_report.md`
2. `playwright_setup_status.json`
3. `operator_result_contract.json`

### `playwright_setup_report.md`
Include:
- detected runtime context
- what was checked
- what was missing
- what install actions were attempted
- whether module resolution succeeded afterward
- whether browser binaries were confirmed
- whether a minimal browser launch test passed
- any remaining blockers

### `playwright_setup_status.json`
Write a machine-readable setup summary including fields such as:
- `runtime_context`
- `phase`
- `ready_for_browser_stage`
- `module_resolved`
- `browsers_available`
- `launch_test_passed`
- `install_attempted`
- `install_succeeded`
- `force_reinstall_mode`
- `notes`

## Success condition

This stage succeeds only if all of the following are true after setup:
- Playwright resolves from the correct runtime context
- required browser binaries are available
- a minimal browser launch sanity check succeeds

If any of these fail, this stage must fail.

## Hard rule

Do not modify gameplay/application files in this stage.
This stage is only for Playwright environment preparation and verification.

## Required contract artifact

Write a JSON file named `operator_result_contract.json` in the workspace.

If successful, write:

```json
{
  "status": "ok",
  "detail": "Verified a working Playwright environment in the active runtime context, including module resolution, browser availability, and a minimal launch sanity check."
}
```

## If blocked

If you cannot establish a working Playwright environment reliably, write:

```json
{
  "status": "error",
  "detail": "Could not verify a working Playwright environment in the active runtime context."
}
```

## Stdout contract

This setup stage must still satisfy the generic executor completion format.

After writing the final setup artifacts, you must immediately end stdout with exactly these lines and then terminate cleanly:

```text
OPERATOR STATUS: completed|failed
CHANGED FILES: file1, file2 or NONE
SUMMARY: one short sentence
MECHANICS CHECK: preserved|issues
VISUAL CHECK: preserved|updated|issues
AUDIO CHECK: integrated|not_applicable|issues
MOBILE CHECK: safe|not_checked|issues
```
