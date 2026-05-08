gu# Repo Identity and Operator Pipeline Reframe Implementation Journal

**Last Updated:** 2026-05-05 12:37 America/Mexico_City  
**Feature Spec:** Documentation-first cleanup and re-framing of the `game_refactoring` repository as the canonical operator-pipeline project  
**Backend Reference:** N/A

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Discovery and Scope Definition - **COMPLETE**

- [x] Inspect top-level documentation and journals
- [x] Inventory `game_remix_editor` / `game_remixer` references
- [x] Identify likely non-core lab, generated, and historical areas
- [x] Define rename categories and documentation authority concerns

**Status:** ✅ Complete

### Phase 2: Documentation Authority Reset - **COMPLETE**

- [x] Rewrite `README.md` as the canonical repo identity
- [x] Add a repository architecture/taxonomy document
- [x] Reframe operator documentation around the intended core pipeline
- [x] Add quarantine guidance for non-core areas

**Status:** ✅ Complete

### Phase 3: Deferred Runtime Naming Review - **COMPLETE**

- [x] Re-audit remaining repo-owned naming references after docs cleanup
- [x] Separate safe documentation renames from compatibility-sensitive runtime identifiers
- [x] Summarize deferred code/runtime renames for a later pass

**Status:** ✅ Complete

### Phase 4: Evidence-First Validation and Dry-Run Planning - **COMPLETE**

- [x] Produce code-grounded runtime/spec-adaptor/media-policy fact docs
- [x] Produce intent-vs-code delta documentation
- [x] Write evidence-first refactor process guidance
- [x] Write dry-run mode plan for orchestrator validation
- [x] Map static vs dynamic pipeline boundaries
- [x] Plan safe invariant-contract merge approach
- [x] Implement and validate smallest `--dry-run-operators` slice

**Status:** ✅ Complete

### Phase 5: Executor Specialization Cleanup - **COMPLETE**

- [x] Repair prompt-builder helper split in `run_operator_pipeline_game.py`
- [x] Extract `media_mapper` post-run completion/warning evaluation into isolated helper logic
- [x] Revalidate `--dry-run-operators`
- [x] Revalidate `--dry-run-operators` + `--dry-run-spec-adaptor`
- [x] Continue reducing stage-specific logic in the generic executor loop

**Status:** ✅ Complete

---

## 📝 Journal Entries

### 2026-05-06 18:13 - Standalone workflow launcher extracted from the main CLI

**Achievement:**
Reverted `scripts/creative_refactor_cli.py` to the latest tagged state and moved workflow orchestration into a new standalone launcher so the workflow abstraction does not regress the main refactor CLI surface.

**Implementation Details:**
- Restored `scripts/creative_refactor_cli.py` to the latest tagged version instead of keeping `game_workflow` embedded in the main CLI.
- Added a new standalone workflow launcher:
  - `scripts/game_workflow.py`
- Implemented a small workflow definition layer using a dedicated immutable data model:
  - `WorkflowDefinition`
- Implemented the first named workflow:
  - `tag_and_fix`
- Kept workflow structure self-contained in the new script:
  - `run_label: tag-and-fix`
  - nodes:
    - `inference_outputs`
    - `playwright_fix`
- Required the caller to supply the input games manifest explicitly via:
  - `--games-manifest-source`
- Generated workflow manifests into:
  - `runs/_workflow_manifests/`
- Delegated actual batch launching back into the existing stable CLI surface through:
  - `python3 scripts/creative_refactor_cli.py --json start-batch ...`
- Re-ran the 10-game input set through the new standalone workflow launcher with:
  - `--max-concurrency 10`
- Confirmed the run launched successfully as:
  - `runs/run_game_remixer_20260506T120943Z`
- Ran the existing kill-all helper afterward and confirmed there were no active surviving workflow-related processes to terminate.

**Technical Decisions:**
- Applied a SOLID-style separation to avoid regressions in the existing CLI:
  - kept `creative_refactor_cli.py` focused on its preexisting responsibilities
  - moved workflow lookup, games-manifest validation, generated-manifest creation, and workflow launch orchestration into `scripts/game_workflow.py`
- Treated the workflow definition as source-controlled code, not as a fixture-backed template, so the input game list remains a required external input and the workflow definition remains stable and explicit.
- Reused the existing `start-batch` launch path rather than duplicating orchestration logic.

**Testing / Validation:**
- Dry-run validation:
  - `python3 scripts/game_workflow.py --json --id tag_and_fix --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json --dry-run-operators --dry-run-spec-adaptor`
  - returned:
    - `workflow_id: tag_and_fix`
    - `workflow_games_count: 10`
    - generated workflow manifest under `runs/_workflow_manifests/`
- Live launch validation:
  - `python3 scripts/game_workflow.py --json --id tag_and_fix --games-manifest-source fixtures/specimen_random10_inference_playwright_manifest.json --max-concurrency 10`
  - returned:
    - `run_id: run_game_remixer_20260506T120943Z`
    - `workflow_id: tag_and_fix`
    - `workflow_games_count: 10`
- Kill-all validation:
  - `python3 scripts/creative_refactor_cli.py --json kill-all`
  - returned:
    - `matched_count: 0`
    - `survivor_count: 0`
    - `success: true`

**Status:** In Progress

---

### 2026-05-06 04:12 - Playwright shared-runtime resolution restored for async operator runs

**Achievement:**
Restored Playwright-backed operator execution in the async named-manifest pipeline path by fixing the worker runtime environment instead of retrying per-run installation.

**Implementation Details:**
- Verified the machine-level Playwright CLI was installed and working:
  - `playwright --version` returned `Version 1.59.1`
- Verified the failing condition directly:
  - `node` and the Playwright CLI were available
  - plain `require.resolve('playwright')` failed with `MODULE_NOT_FOUND`
  - `NODE_PATH` was effectively unset for the worker runtime
- Verified the working condition directly:
  - injecting `NODE_PATH=/Users/hassan/.nvm/versions/node/v24.15.0/lib/node_modules`
  - made `require.resolve('playwright')` succeed
- Updated:
  - `scripts/creative_refactor_runtime.py`
  - to propagate worker environment with a default shared Node module path:
    - `NODE_PATH=/Users/hassan/.nvm/versions/node/v24.15.0/lib/node_modules`
- Relaunched the specimen single-game Playwright manifest through the async CLI path used by prior successful runs:
  - `python3 scripts/creative_refactor_cli.py --json start-batch --manifest fixtures/specimen_single_game_inference_playwright_fix_manifest.json --pipeline v2 --max-concurrency 1`
- Verified the resulting async run completed successfully:
  - `runs/run_game_remixer_20260506T100713Z`
  - `status: transform_completed`
- Verified node 2 (`playwright_fix`) produced a valid live Playwright result contract:
  - `status: ok`
  - browser evidence artifacts were created
  - screenshots were captured
  - the pass completed as a conservative no-code-change outcome rather than a blocked Playwright-missing outcome

**Technical Decisions:**
- Treated this as a runtime environment propagation problem, not a prompt-header or per-run installation problem.
- Kept the simpler rolled-back Playwright prompt shape and fixed the actual worker environment instead.
- Used the async named-manifest CLI entrypoint as the validation path so the confirmed milestone matches real operational usage.

**Testing / Validation:**
- Direct runtime preflight proved:
  - without `NODE_PATH`, `require.resolve('playwright')` fails
  - with injected `NODE_PATH`, `require.resolve('playwright')` succeeds
- Async run validation:
  - `python3 scripts/creative_refactor_cli.py --json status --run-dir runs/run_game_remixer_20260506T100713Z`
  - reported:
    - `status: transform_completed`
    - `games_transform_completed: 1`
    - `games_transform_failed: 0`
- Inspected:
  - `runs/run_game_remixer_20260506T100713Z/games/gamezone-ea127465-3223-4053-af7b-2a61f74c312c/operator_pipeline/node_02_playwright_fix/attempt_01/operator_result.json`
  - `.../workspace/operator_result_contract.json`
  - `.../workspace/playwright_observation_log.md`
  - `.../workspace/delta_issue_ledger.md`

**Status:** In Progress

---

### 2026-05-06 02:00 - Stage-4 clone rebuild experiment removed after failure

**Achievement:**
Removed the temporary Stage 4 clone-rebuild experiment scaffolding after the broad 10-game node-1 -> node-4 attempt proved unsuccessful and should not be retried in the same form.

**Implementation Details:**
- Removed the temporary stage-4 prompt file:
  - `prompts/operators_v2/04_specimen_mobile_clone_rebuild.md`
- Removed the temporary 10-game inference+clone experiment manifest:
  - `fixtures/specimen_random10_inference_clone_manifest.json`
- Preserved the rest of the specimen pipeline assets so the repo can return to the earlier stage-based experiments without losing the conservative fixer, inference outputs, or creative rename scaffolding.
- Recorded the operational failure mode as a warning in this journal rather than leaving the experimental stage-4 artifacts in the active working set.

**Warning / Decision:**
- Do **not** retry the same stage-4 clone-rebuild experiment as previously designed.
- The broad node-1 -> node-4 experiment was treated as a total failure by the user and should be considered rejected in its current form.
- If a future clone-rebuild experiment is attempted, it should be redesigned from first principles instead of reusing the removed prompt/manifest shape.

**Next Steps:**
- [x] Remove temporary stage-4 experiment files from the repo working set
- [x] Preserve earlier stage prompts/manifests for future reuse
- [ ] If clone-rebuild is revisited later, redesign it as a new experiment with a narrower and better-constrained scope

**Status:** In Progress

---

### 2026-05-04 22:39 - Initial setup and planning

**What Changed:**
- Created the task journal for the documentation-first cleanup and repo re-framing effort
- Captured the phased plan for resetting documentation authority before any code-symbol rename work
- Recorded the distinction between safe documentation cleanup and deferred runtime compatibility decisions

**Why:**
The repo was cloned from `game_remix_editor`, but the immediate goal is not to change working code. The immediate goal is to make the repository understandable as a reusable operator-pipeline system, remove stale branding from current-facing docs, and classify non-core material before any destructive cleanup or code rename work.

**Files Created:**
- `docs/journals/repo-identity-and-operator-pipeline-reframe.md` - Task journal and decision log for this cleanup pass

**Next Steps:**
- [x] Rewrite `README.md` so it describes the current repo identity and intended architecture
- [x] Add a repository architecture/taxonomy document covering core, operational, lab, generated, and historical areas
- [x] Update operator-facing docs to align with the intended core pipeline framing
- [x] Re-audit remaining repo-owned naming references and document what is intentionally deferred
- [x] Add evidence-first runtime/spec-adaptor/media-policy architecture docs
- [x] Add process, dry-run, static/dynamic, and invariant-merge planning docs
- [x] Implement and validate the first operator dry-run slice
- [x] Implement and validate spec-adaptor dry-run for full no-`cline` shell execution
- [x] Repair and revalidate the in-progress `run_operator_pipeline_game.py` prompt-builder split
- [x] Extract and revalidate the first `media_mapper` post-run specialization helper
- [ ] Continue reducing Python-side executor specialization in controlled passes

**Status:** In Progress

---

### 2026-05-05 22:37 - Node-chain runtime cleanup, specimen setup, and style removal

**Achievement:**
Completed the main runtime cleanup pass that removes spec-adaptor and style from the active generic node-chain path, slims the Python-side prompt packet down to a true runtime I/O contract, and scaffolds a new specimen-focused two-node evaluation chain.

**Implementation Details:**
- Updated `scripts/run_operator_pipeline_batch.py` to:
  - remove active `spec_adaptor.py` invocation from the batch orchestration path
  - keep `--dry-run-spec-adaptor` only as a deprecated compatibility flag
  - stop threading `style` through worker launch and run-state updates
  - keep the active batch path centered on:
    - run scaffold
    - input preparation
    - detached batch execution
    - node-chain worker scheduling
- Updated `scripts/creative_refactor_cli.py` to:
  - remove `--style` from the active `start-batch` launch surface
  - stop passing style into the batch runner
  - stop emitting style in launcher metadata
- Updated `scripts/run_operator_pipeline_game.py` to:
  - remove active style usage and `selected_style_id` writes
  - collapse the Python-side prompt builder to a lean runtime contract
  - remove inherited media/catalog/font/icon boilerplate from generated prompt payloads
  - make the manifest/user prompt optional
  - if present, render it only as:
    - `During this pipeline, adapt your operation to the following prompt: "<user input>"`
  - keep node prompt files as the primary instruction source
- Added planning docs:
  - `docs/async_operator_pipeline_port_plan.md`
  - `docs/node_chain_cli_adaptation_plan.md`
- Added new node prompts and manifests for proving and specimen work:
  - `prompts/operators_v2/02_invert_palette_after_translation.md`
  - `prompts/operators_v2/03_capture_mobile_screenshot.md`
  - `prompts/operators_v2/01_specimen_runtime_qa.md`
  - `prompts/operators_v2/02_specimen_inference_outputs.md`
  - `fixtures/sample_manifest_generic_spanish.json`
  - `fixtures/specimen_runtime_qa_manifest.json`
- Added `.gitignore` rules for:
  - `runs/`
  - Python caches
  - macOS/editor noise
  - large non-code asset/output directories

**Technical Decisions:**
- Treated the sibling async CLI comparison as evidence that this repo already had the correct detached launcher shape; the real remaining mismatch was the leftover batch-level spec adaptor step.
- Treated the Python-built stage packet as legacy overreach and cut it back to runtime identity + workspace + upstream contract + stdout contract + node prompt body.
- Treated user prompt input as optional context only, not the primary source of node behavior.
- Kept style as legacy compatibility only until this pass, then removed it from the active generic node-chain runtime path.

**Testing:**
- `python3 -m py_compile scripts/run_operator_pipeline_game.py`
- `python3 -m py_compile scripts/creative_refactor_cli.py scripts/run_operator_pipeline_batch.py scripts/run_operator_pipeline_game.py`
- Started and inspected detached async runs showing:
  - no spec-adaptor phase in the active batch path
  - `start-batch -> status` working through the generic node-chain path
- Verified lean generated prompt output in:
  - `runs/run_game_remixer_lean_packet_check/.../operator_prompt.txt`
- Validated no-style launch path with:
  - `python3 scripts/creative_refactor_cli.py start-batch --manifest fixtures/hello_world_manifest.json --run-id run_game_remixer_no_style_validation --model gpt-5.4 --agent-timeout 300 --max-concurrency 1 --dry-run-operators`

**Next Steps:**
- [x] Remove leftover `spec_adaptor.py` invocation from batch orchestration
- [x] Revalidate async `start-batch -> status -> finish` without spec adaptor
- [x] Strip Python-side prompt packet down to true runtime I/O contract only
- [x] Make manifest/user prompt optional and node-first
- [ ] Run the specimen chain and inspect outputs
- [ ] Validate whether screenshot capture inside the worker truly produces the required artifact under live execution

**Status:** In Progress

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Do a documentation-first cleanup before changing code behavior or runtime identifiers.  
**Rationale:** Current repo confusion is caused by stale branding, conflicting documentation, and mixed historical/generated material. Resetting documentation authority first is the safest way to preserve a working codebase while preparing later repurposing work.  
**Alternatives Considered:** Immediate code symbol renames and blanket search/replace were rejected because they risk breaking run IDs, tests, helper scripts, and generated artifact assumptions.

**Decision:** Treat naming references in categories rather than as one global rename set.  
**Rationale:** Product identity text, filesystem path examples, runtime identifiers, and generated historical artifacts have different risk levels and should not be edited with the same strategy.

### Future Enhancements

**Nice to Have:**
- A later compatibility-reviewed pass for runtime identifier renames
- A later physical quarantine/archive move for clearly non-core directories

**Potential Improvements:**
- Add a concise “main entrypoints” operations doc after the first cleanup pass
- Add a formal manifest of generated vs source-controlled artifacts

---

### 2026-05-05 12:37 - Hello World contract proof scaffolding

**Achievement:**
Built the first concrete Stage 1 proving scaffold for the universal stage-result contract using a tiny fixture that still runs through the real operator pipeline shell.

**Implementation Details:**
- Added a tiny real-pipeline input fixture:
  - `fixtures/hello_world_game/index.html`
  - `fixtures/hello_world_manifest.json`
- Added a dedicated proving prompt:
  - `prompts/operators_v2/01_hello_world_spanish_contract.md`
- Added a dedicated single-stage registry:
  - `configs/operator_pipeline_hello_world.json`
- Extended `scripts/run_operator_pipeline_game.py` to:
  - accept `--registry-config`
  - reserve a stable contract artifact path: `operator_result_contract.json`
  - read that contract JSON if present
  - record `operator_result_contract` and `operator_result_contract_path` into `operator_result.json`
- Extended `scripts/run_operator_pipeline_batch.py` to:
  - accept `--registry-config`
  - accept `--through`
  - forward both to per-game workers
- Confirmed the minimal fixture can run through the real batch shell in dry-run mode when invoked with:
  - `--manifest fixtures/hello_world_manifest.json`
  - `--registry-config configs/operator_pipeline_hello_world.json`
  - `--through gameplay_narrative`

**Observed Result:**
- Dry-run proof succeeded in:
  - `runs/run_game_remixer_20260505T183620Z`
- The run completed with:
  - `status: transform_completed`
- The operator result now records:
  - `operator_result_contract`
  - `operator_result_contract_path`
- In dry-run mode the contract payload is still `null`, which is expected because no live operator wrote `operator_result_contract.json`.

**Technical Decisions:**
- Used a dedicated registry config instead of mutating the production registry.
- Used a dedicated prompt instead of rewriting the production Stage 01 prompt.
- Added contract-reading as a bridge feature, not as a replacement of the existing stdout/result path.
- Added `--through` support to batch execution so a single-stage proving registry can run cleanly through the same shell.

**Testing:**
- `python3 -m py_compile scripts/run_operator_pipeline_game.py scripts/run_operator_pipeline_batch.py`
- `python3 scripts/run_operator_pipeline_batch.py --manifest fixtures/hello_world_manifest.json --registry-config configs/operator_pipeline_hello_world.json --through gameplay_narrative --style neutral_prototype --dry-run-operators --max-concurrency 1 --poll-seconds 1`
- Verified:
  - `runs/run_game_remixer_20260505T183620Z/run_state.json`
  - `runs/run_game_remixer_20260505T183620Z/games/hello-world-fixture/operator_pipeline/stage_01_gameplay_narrative/attempt_01/operator_result.json`

**Next Steps:**
- [x] Create a tiny proving fixture that survives the normal pipeline path
- [x] Add a minimal operator-emitted JSON result bridge with backward-compatible fallback
- [ ] Run one live non-dry operator pass on the Hello World fixture so the contract file is actually emitted
- [ ] Decide whether operator contract status should remain informational first or drive stage success in the next pass
- [ ] Add accepted-upstream-status policy support after the live contract emission is verified

**Status:** In Progress

---

### 2026-05-05 12:05 - Universal stage-result contract planning doc

**Achievement:**
Documented the next abstraction target as a grounded planning artifact focused on a universal stage-result contract, explicit accepted-status chaining policy, and a real-pipeline proving fixture.

**Implementation Details:**
- Added `docs/universal_stage_result_contract_plan.md`.
- Captured the currently intended universal contract:
  - operator-emitted JSON result
  - minimum fields: `status`, `detail`
  - allowed statuses: `ok`, `warning`, `error`
- Captured the clarified scope boundary:
  - simplify only the proving input and operator task
  - keep the real pipeline path intact
- Recorded the files most likely to require future implementation work:
  - `scripts/run_operator_pipeline_game.py`
  - `scripts/operator_registry_v2.py`
  - `configs/operator_pipeline_v2.json`
  - `scripts/run_operator_pipeline_batch.py`
  - `scripts/creative_refactor_cli.py`
  - `prompts/operators_v2/...`
  - fixture/sample input area
  - `scripts/prepare_inputs.py`
- Recorded side-effect concerns and migration risks:
  - backward compatibility with current stage result fields
  - dashboard/reporting assumptions
  - retry semantics
  - warning propagation
  - fixture-only logic drift
  - keeping spec-adaptor separate
- Updated `docs/master_index.md` so future sessions can find the new planning doc as the current milestone.

**Technical Decisions:**
- Treat universal stage evaluation as a bridge migration, not a replace-everything rewrite.
- Keep executor transport status separate from future universal stage evaluation status.
- Prove the abstraction with a tiny input fixture running through the real pipeline before changing production stages broadly.

**Testing:**
- Documentation-only pass; no runtime behavior changed in this step.

**Next Steps:**
- [x] Write grounded planning doc for universal stage-result contract work
- [x] Capture observed files to touch, side effects, and risk boundaries
- [ ] Create a tiny proving fixture that survives the normal pipeline path
- [ ] Add a minimal operator-emitted JSON result bridge with backward-compatible fallback
- [ ] Add accepted-upstream-status policy support
- [ ] Validate the real pipeline against the proving fixture

**Status:** In Progress

---

### 2026-05-05 01:35 - Media-mapper post-run extraction and dry-run revalidation

**Achievement:**
Isolated the `media_mapper` final-attempt completion/warning decision into helper logic and revalidated both dry-run shells afterward.

**Implementation Details:**
- Updated `scripts/run_operator_pipeline_game.py` to add:
  - `normalize_media_mapper_post_run_status(...)`
- Kept the generic stage loop responsible for orchestration while moving the final-attempt `media_mapper` completion/warning decision behind a dedicated helper boundary.
- Preserved existing behavior:
  - non-`media_mapper` stages are unaffected
  - `media_mapper` still fails intermediate attempts when actionable URLs/media refs remain
  - `media_mapper` still completes on the final attempt while emitting the same warning when unresolved refs remain
- Revalidated dry-run execution after the extraction:
  - operator-only dry run completed successfully in `runs/run_game_remixer_20260505T070957Z`
  - combined operator + spec-adaptor dry run completed successfully in `runs/run_game_remixer_20260505T072635Z`
- Observed one failed rerun against an already-used run directory (`run_game_remixer_20260505T072116Z`), then confirmed that failure was rerun-state contamination rather than a regression in the extracted helper logic.

**Technical Decisions:**
- Chose a minimal helper extraction instead of a larger media-policy refactor so the semantics stayed easy to compare against the pre-change flow.
- Kept the retry-failure branch in the loop for now and extracted only the final-attempt normalization/warning branch as the smallest safe step.
- Treated reused run-directory failures as validation noise, not product regressions, and revalidated with a fresh run directory.

**Testing:**
- `python3 scripts/run_operator_pipeline_batch.py --manifest fixtures/sample_manifest.json --run-id run_game_remixer_20260505T070957Z --model gpt-5.4 --agent-timeout 3600 --max-concurrency 1 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --style neutral_prototype --dry-run-operators`
- `python3 scripts/prepare_inputs.py --run-dir runs/run_game_remixer_20260505T072635Z`
- `python3 scripts/spec_adaptor.py --run-dir runs/run_game_remixer_20260505T072635Z --style neutral_prototype --remix-prompt "test prompt" --dry-run-spec-adaptor`
- `python3 scripts/run_operator_pipeline_batch.py --manifest fixtures/sample_manifest.json --run-id run_game_remixer_20260505T072635Z --model gpt-5.4 --agent-timeout 3600 --max-concurrency 1 --poll-seconds 5.0 --stale-heartbeat-seconds 900 --style neutral_prototype --remix-prompt "test prompt" --dry-run-operators --dry-run-spec-adaptor`

**Next Steps:**
- [x] Extract the `media_mapper`-specific post-run evaluation out of the generic stage loop
- [x] Revalidate operator-only dry run after the extraction
- [x] Revalidate combined operator/spec-adaptor dry run after the extraction
- [ ] Continue reducing stage-specific media-policy handling in smaller helper passes
- [ ] Decide whether to document rerun-directory contamination as an operational footnote in core docs

**Status:** In Progress

---

### 2026-05-04 23:27 - Evidence pack, master index, and next executable milestone

**Achievement:**
Captured the current architecture understanding in a consolidated evidence pack and established a master index for future sessions.

**Implementation Details:**
- Updated repo-facing documentation and architecture memory through:
  - `docs/master_index.md`
  - `docs/code_facts_runtime_flow.md`
  - `docs/code_facts_spec_adaptor.md`
  - `docs/code_facts_media_policy.md`
  - `docs/intent_vs_code_deltas.md`
  - `docs/static_vs_dynamic_pipeline_map.md`
  - `docs/evidence_first_refactor_process.md`
  - `docs/dry_run_mode_plan.md`
  - `docs/invariant_contract_merge_plan.md`
- Confirmed the run-level spec adaptor boundary is real and should remain separate from the per-game operator chain.
- Confirmed the orchestrator shell is more reusable than the current v2 per-game executor.
- Confirmed the largest specialization hotspot currently lives in Python media-policy generation, prompt-packet assembly, and `media_mapper` post-run enforcement.
- Added `docs/master_index.md` so future sessions can resume from one canonical index instead of reconstructing context from scattered docs.

**Technical Decisions:**
- Deferred behavior-sensitive implementation until after evidence docs were in place.
- Chose `--dry-run-operators` as the next smallest executable milestone because it validates the orchestrator shell without depending on `cline`.
- Treated invariant-contract merge as a staged migration with compatibility bridge rather than direct replacement.

**Testing:**
- Verified repo-owned current-facing naming cleanup earlier in the task.
- Verified evidence docs only reflect inspected code paths and explicitly record remaining blind spots and future-read requirements.

**Next Steps:**
- [x] Implement `--dry-run-operators` in the smallest possible slice
- [x] Validate dry-run run/game/stage artifacts end to end
- [x] Implement `--dry-run-spec-adaptor` for full no-`cline` shell validation
- [x] Repair and revalidate the first prompt-builder helper split in `run_operator_pipeline_game.py`
- [ ] Continue executor specialization cleanup in smaller helper extractions
- [ ] Only then revisit deeper worker-guidance simplification

**Status:** In Progress

---

## ✅ Testing Checklist

- [ ] Manual verification that updated docs reflect current intended architecture
- [ ] Manual verification that no code behavior was changed in this documentation/evidence pass
- [ ] Search verification for remaining repo-owned legacy naming references after doc updates
- [x] Dry-run shell validation once `--dry-run-operators` is implemented
- [x] Full shell validation with `--dry-run-operators` + `--dry-run-spec-adaptor`
- [x] Post-extraction revalidation after isolating `media_mapper` post-run logic

---

## 🎯 Success Criteria

- [x] Canonical repo identity documented in `README.md`
- [x] Core architecture and taxonomy documented clearly
- [x] Operator-facing docs aligned with intended future core pipeline
- [x] Non-core/generated/historical areas clearly classified
- [x] Deferred runtime/code rename decisions summarized without altering working behavior
- [x] Code-grounded evidence docs created for runtime/spec-adaptor/media-policy architecture
- [x] Evidence-first process and dry-run plan documented
- [x] Smallest dry-run operator slice implemented and validated
- [x] Full no-`cline` shell dry-run implemented and validated
- [ ] Python-side executor specialization reduced in follow-up controlled passes
