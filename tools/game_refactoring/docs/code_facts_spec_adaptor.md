# Code Facts: Spec Adaptor

This document records concrete observations about the current spec-adaptor subsystem based on inspected code.

It is an evidence document, not a redesign proposal.

## Confidence legend

- **Confirmed**: directly supported by the cited code
- **Unconfirmed**: plausible but not yet validated in additional files
- **Unknown**: not yet inspected

## Sources read

- `scripts/spec_adaptor.py`
- `scripts/run_operator_pipeline_batch.py`
- `scripts/run_operator_pipeline_game.py`
- `scripts/creative_refactor_cli.py`

## Observation 1 — the spec adaptor is invoked from the batch runner, not from the per-game operator loop

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_batch.py`
  - after `prepare_inputs.py`
  - `if remix_prompt:`
    - `run_spec_adaptor(run_dir, args.style, remix_prompt, ...)`
  - only after that does it initialize run status and launch per-game workers
- `scripts/run_operator_pipeline_game.py`
  - reads `adapted_spec_dir` from run state
  - does not invoke `spec_adaptor.py`

**Interpretation:**
The spec adaptor is currently a run-level pre-worker step, not one of the per-game operator stages.

## Observation 2 — the spec adaptor only runs when a remix prompt is present

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_batch.py`
  - `remix_prompt = resolve_remix_prompt(args)`
  - `if remix_prompt: run_spec_adaptor(...)`

**Interpretation:**
If no remix prompt is provided, the current v2 batch runner skips spec adaptation entirely.

## Observation 3 — the spec adaptor requires a remix prompt at the script interface level

**Status:** Confirmed

**Evidence:**
- `scripts/spec_adaptor.py`
  - `parse_args()` defines:
    - `--run-dir` required
    - `--style`
    - `--remix-prompt` required
    - `--prompt-targets` optional
    - `--model`
    - `--agent-timeout`

**Interpretation:**
The script itself does not implement a no-op or pass-through mode. The current pass-through behavior is effectively “do not invoke spec_adaptor.py”.

## Observation 4 — the spec adaptor builds a run-local workspace under `run_dir/spec_adaptor/`

**Status:** Confirmed

**Evidence:**
- `scripts/spec_adaptor.py`
  - `adaptor_dir = run_dir / "spec_adaptor"`
  - uses:
    - `adapted/`
    - `invariants/`
    - `user_remix_prompt.txt`
    - `selected_style.json`
    - `recomposition_context.json`
    - `spec_recomposition_harness_attempt_XX.md`
    - `recomposition_summary.json`
    - stdout/stderr files
    - `adaptation_report.json`
    - `spec_adaptor_job_state.json`
    - debug trace log

**Interpretation:**
Spec adaptation artifacts are run-scoped and stored in a dedicated subtree.

## Observation 5 — the spec adaptor copies editable style-local creative files and separate invariant prompt files

**Status:** Confirmed

**Evidence:**
- `scripts/spec_adaptor.py`
  - `EDITABLE_CREATIVE_FILE_ORDER` includes:
    - `creative_remix_contract.md`
    - `visual_identity_contract.md`
    - `theme_policy.md`
    - `creative_refactor_agent_template.md`
  - `INVARIANT_REFERENCE_FILES` includes:
    - `audio_policy.md`
    - `network_policy.md`
    - `system_contract.md`
    - `refactor_compliance_spec.md`
  - `copy_editable_creative_bundle(...)`
  - `copy_invariant_reference_files(...)`

**Interpretation:**
The adaptor explicitly separates:
- editable creative bundle
- invariant reference constraints

## Observation 6 — the adaptor uses a CLI agent to rewrite the editable bundle in place

**Status:** Confirmed

**Evidence:**
- `scripts/spec_adaptor.py`
  - `build_recomposition_harness(...)` constructs a full text harness
  - `run_recomposition_agent(...)` launches:
    - `cline`
    - with the adaptor directory as cwd
    - using the harness text as prompt
  - output files are expected to be rewritten in the adaptor workspace

**Interpretation:**
This subsystem is not just file copying; it performs an agent-authored recomposition pass over editable spec files.

## Observation 7 — spec-adaptor retries are built into the subsystem

**Status:** Confirmed

**Evidence:**
- `scripts/spec_adaptor.py`
  - `SPEC_ADAPTOR_MAX_ATTEMPTS = 3`
  - `for attempt_number in range(1, SPEC_ADAPTOR_MAX_ATTEMPTS + 1):`
  - previous failure information is fed into later harnesses via retry guidance

**Interpretation:**
The spec adaptor owns its own retry model, independent of per-game operator retries.

## Observation 8 — success requires both zero exit code and contract validation of `recomposition_summary.json`

**Status:** Confirmed

**Evidence:**
- `scripts/spec_adaptor.py`
  - `validate_recomposition_summary(...)`
  - `evaluate_recomposition_contract(...)`
  - success requires:
    - summary exists
    - valid JSON
    - required keys present
    - placeholders replaced
    - no stdout/file mismatch
  - final success condition:
    - `execution.returncode == 0 and contract_evaluation["success"]`

**Interpretation:**
The adaptor is contract-validated, not just subprocess-exit-based.

## Observation 9 — the adaptor writes both job-local state and top-level `run_state.json`

**Status:** Confirmed

**Evidence:**
- `scripts/spec_adaptor.py`
  - writes `spec_adaptor_job_state.json`
  - updates `run_state["spec_adaptor"]`
  - sets:
    - status
    - adapted_dir
    - invariant_dir
    - adaptation_report_path
    - remix_prompt_path
    - recomposition_context_path
    - explicit_prompt_targets
    - validation payload
    - failure_reason
    - max_attempts

**Interpretation:**
The adaptor produces both local detail and run-level summary visibility.

## Observation 10 — per-game workers consume the adapted spec directory only as read-only context input

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_game.py`
  - `resolve_adapted_spec_dir(run_state)`
  - `adapted_spec_dir` is passed into `build_operator_prompt_text(...)`
  - no writing back into that directory occurs in this file

**Interpretation:**
The current game worker appears to treat adapted specs as shared read-only run context.

## Observation 11 — current behavior is not “pass original specs through into a mirrored adapted bundle” when no prompt is present

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_batch.py`
  - skips the adaptor entirely if no remix prompt exists
- `scripts/spec_adaptor.py`
  - has no no-prompt mode
  - requires `--remix-prompt`

**Interpretation:**
The current runtime behavior is:
- with remix prompt: produce adapted bundle
- without remix prompt: no spec-adaptor subtree is created by this path

This is narrower than a true “adapt or pass-through bundle” model.

## Observation 12 — prompt-target narrowing exists in the adaptor API

**Status:** Confirmed

**Evidence:**
- `scripts/spec_adaptor.py`
  - optional `--prompt-targets`
  - `parse_prompt_targets(...)`
  - supported target labels map to editable creative files
  - harness includes “explicit target scope”

**Interpretation:**
The adaptor already supports focused recomposition on selected creative files, although current batch-runner usage did not yet validate whether it passes this option.

## Open questions

### 1. Does any non-v2 path invoke the spec adaptor differently?
**Status:** Unknown  
**Next files to inspect:** `scripts/run_parallel_batch.py`, possibly legacy helpers

### 2. Are downstream workers actually reading the adapted files in a meaningful way, or only seeing the path in the prompt packet?
**Status:** Unconfirmed  
**Next files to inspect:** prompt files and task-packet generation path

### 3. Should “no remix prompt” conceptually produce a pass-through adapted bundle even if current code does not?
**Status:** Design question, not code fact

## Delta hints vs intended architecture

These are preliminary deltas, not final recommendations.

### Likely aligned
- spec adaptor is separate from the operator chain
- spec adaptor is run-scoped, not game-scoped
- operator workers consume adapted spec context after adaptor completion
- spec adaptor owns its own retries and validation

### Likely misaligned or incomplete relative to intended model
- current code skips spec adaptor entirely when no prompt exists, rather than explicitly producing a pass-through bundle
- current adaptor language and file naming remain remix-specific
- prompt-target capability exists, but actual usage path still needs validation in orchestration

## Working summary

Based on inspected code only:

- the current architecture already treats spec adaptation as a separate run-level subsystem
- it happens before per-game operator execution
- it is optional at the batch level
- it writes a shared adapted bundle under the run directory
- the current “optional” behavior is implemented as skip-or-run, not pass-through bundle generation