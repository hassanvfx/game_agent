# Code Facts: Media Policy and Specialization

This document records concrete observations about `scripts/media_policy.py` and its relationship to current operator specialization.

It is an evidence document, not a redesign proposal.

## Confidence legend

- **Confirmed**: directly supported by inspected code
- **Unconfirmed**: plausible but still needs more files
- **Unknown**: not yet inspected

## Sources read

- `scripts/media_policy.py`
- `scripts/run_operator_pipeline_game.py`
- `prompts/operators_v2/03_media_mapper.md`
- `scripts/prepare_inputs.py`
- `scripts/run_parallel_batch.py`
- `scripts/run_single_game.py`

## Observation 1 — media policy is a deterministic static analysis pass over workspace files

**Status:** Confirmed

**Evidence:**
- `scripts/media_policy.py`
  - scans files by suffix sets
  - uses regex-based extraction for:
    - external URLs
    - CSS URLs
    - HTML src/href/poster/data-* attributes
    - quoted local asset paths
    - font-family declarations
    - font imports
    - material-symbol token usage

**Interpretation:**
This subsystem is not agent-based. It is a deterministic Python inspection layer over a workspace.

## Observation 2 — media policy produces structured dynamic hints consumed by the operator pipeline

**Status:** Confirmed

**Evidence:**
- `scripts/media_policy.py`
  - `build_media_policy_report(workspace)` returns:
    - `potential_urls_to_remove`
    - `actionable_media_replacement_candidates`
    - `actionable_font_replacement_candidates`
    - `normalized_media_replacement_plan`
    - `media_cleanup_plan`
    - `approved_icon_vocabulary`
- `scripts/run_operator_pipeline_game.py`
  - writes pre-run media policy report
  - injects these values into `build_operator_prompt_text(...)`
  - re-runs media policy after operator execution
  - uses remaining findings to affect result evaluation

**Interpretation:**
The media policy layer is a major dynamic-input generator for stage execution.

## Observation 3 — current stage prompt assembly mixes static prompt text with dynamic Python-generated policy hints

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_game.py`
  - `build_operator_prompt_text(...)` combines:
    - operator prompt file text
    - workspace contract
    - run context
    - adapted spec dir
    - Python media policy hint JSON
    - media replacement candidates
    - font candidates
    - normalized replacement refs
    - media cleanup plan
    - icon vocabulary
- `prompts/operators_v2/03_media_mapper.md`
  - also independently instructs the stage to treat Python-flagged candidates as required work

**Interpretation:**
This is a strong static/dynamic hybrid:
- static prompt file
- dynamic runtime hints
- dynamic post-run enforcement

## Observation 4 — media policy enforces an allowlist/blocklist model for external URLs

**Status:** Confirmed

**Evidence:**
- `scripts/media_policy.py`
  - `ALLOWED_EXACT_HOSTS`
  - `ALLOWED_HOST_SUBSTRINGS`
  - `HARDBLOCK_HOST_SUBSTRINGS`
  - `collect_potential_urls_to_remove(...)`

**Interpretation:**
Some current operator specialization is not just creative guidance; it is policy enforcement derived from hard-coded Python rule sets.

## Observation 5 — media policy is heavily tuned to media, fonts, icons, and assets under `assets/`

**Status:** Confirmed

**Evidence:**
- regexes and extension maps explicitly cover:
  - audio
  - image
  - gif
  - video
  - font files
  - font stylesheets
- local asset filtering strongly targets `assets/...`
- normalized placeholder generation creates `assets/inferred/...`

**Interpretation:**
This subsystem is domain-specific, not a generic operator-policy engine.

## Observation 6 — media policy distinguishes between static raw findings and actionable findings

**Status:** Confirmed

**Evidence:**
- `collect_media_replacement_candidates(...)`
- `_filter_actionable_candidates(...)`
- `actionable_*` fields in final report
- `_is_actionable_source_file(...)` excludes catalogs and non-source suffixes

**Interpretation:**
The policy layer already has a notion of:
- observed candidates
- actionable candidates
This is useful, but also means stage behavior depends on Python-side classification.

## Observation 7 — media mapper completion is partly enforced by post-run policy re-scan, not just by worker self-report

**Status:** Confirmed

**Evidence:**
- `scripts/run_operator_pipeline_game.py`
  - post-run `write_media_policy_report(...)`
  - collects remaining candidate lists
  - for `operator.id == "media_mapper"`:
    - if remaining URLs or media candidates exist and retries remain → force failed
    - if final attempt and unresolved remain → mark completed but attach warning

**Interpretation:**
This is a concrete example of runtime specialization embedded in Python rather than purely in prompt/config.

## Observation 8 — the legacy path also uses spec-adaptor gating, but not the operator-pipeline media-policy machinery

**Status:** Confirmed

**Evidence:**
- `scripts/run_parallel_batch.py`
  - same high-level orchestration shape as v2:
    - prepare inputs
    - optional spec adaptor
    - bounded concurrency
  - launches `run_single_game.py`, not `run_operator_pipeline_game.py`
- `scripts/run_single_game.py`
  - no media policy import
  - builds a single creative-refactor prompt from packet + contracts

**Interpretation:**
The media-policy specialization is a v2 operator-pipeline feature, not a universal runtime feature.

## Observation 9 — `prepare_inputs.py` is simple and mostly static

**Status:** Confirmed

**Evidence:**
- mirrors source directory into input mirror
- only integrity check is existence of `index.html`
- updates per-game and run-level state
- no prompt/media dynamic behavior

**Interpretation:**
`prepare_inputs.py` is a static scaffolding step, not a major specialization source.

## Observation 10 — legacy vs v2 share the same broad orchestration skeleton, but differ in game-worker specialization

**Status:** Confirmed

**Evidence:**
- `run_parallel_batch.py` and `run_operator_pipeline_batch.py` are structurally very similar:
  - create/reuse run
  - prepare inputs
  - optional spec adaptor
  - bounded concurrency scheduling
  - stale-heartbeat handling
  - dashboard rebuilding
  - final run-state updates
- divergence occurs at worker launch:
  - legacy → `run_single_game.py`
  - v2 → `run_operator_pipeline_game.py`

**Interpretation:**
The orchestrator shell is more reusable than the per-game execution layer.

## Observation 11 — `run_single_game.py` is itself a static/dynamic hybrid, but with a simpler model than v2

**Status:** Confirmed

**Evidence:**
- static:
  - prompt template path from task packet
  - policy paths from packet
  - reusable spec-adaptor files
- dynamic:
  - runtime remix prompt
  - optional spec-adaptor ready-state reuse
  - packet generation
  - worker execution
- absent:
  - no per-stage operator registry
  - no media-policy re-scan loop
  - no stage promotion model

**Interpretation:**
Legacy flow is simpler, but less modular.

## Blind spot warning

**Potential blind spot noticed during this pass:**
We may over-attribute complexity to prompts when an important part of the specialization actually lives in:
- Python media-policy scanning
- Python post-run enforcement
- Python prompt-packet assembly

So if we later simplify prompts alone, we may still leave the real specialization intact in runtime code.

## Static vs dynamic classification from this pass

### Static
- regex patterns and suffix sets
- allowlists / blocklists
- icon vocabulary
- operator prompt file text
- registry stage order
- input mirroring rules
- legacy packet prompt shape

### Dynamic
- workspace scan findings
- actionable candidate lists
- normalized replacement plans
- media cleanup plans
- runtime remix prompt
- adapted spec dir
- retry context
- post-run unresolved candidate checks

### Mixed/problematic zone
- `build_operator_prompt_text(...)`
  - combines static operator prompt with many dynamic policy structures
- `media_mapper` completion logic
  - static operator id check + dynamic unresolved findings

## Preliminary implications

### Good
- the orchestration shell is cleaner than the specialization layer
- legacy and v2 share enough top-level shape that dry-run can likely target common orchestration behavior

### Problematic
- the v2 operator executor is strongly specialized through Python policy injection
- the current abstraction boundary is weaker than the registry/config alone suggests
- stage 03 is not just “a prompt”; it is prompt + Python analysis + Python enforcement

## Likely next docs

After this pass, the most useful additional docs would be:
- `docs/code_facts_legacy_vs_v2.md`
- `docs/static_vs_dynamic_pipeline_map.md`
- `docs/invariant_contract_merge_plan.md`

## Working summary

The current system has a very important split:

- the **orchestrator shell** is relatively reusable
- the **v2 per-game executor** is where most specialization lives

And within the v2 executor, the biggest specialization source currently visible is:

- dynamic media-policy generation
- dynamic prompt packet assembly
- post-run enforcement tied specifically to `media_mapper`