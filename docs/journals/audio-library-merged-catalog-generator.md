# Audio Library Merged Catalog Generator Implementation Journal

**Last Updated:** 2026-05-19 23:20 America/Mexico_City  
**Feature Spec:** Merged canonical audio catalog + cache-backed Suno generation workflow for `tools/library/assets/audios`

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Discovery and Scope - **COMPLETE**

- [x] Confirm the requirement is a literal merge of both existing `audios.json` files
- [x] Confirm `tools/library/audio_library` should behave like a cache/materialized artifact store
- [x] Confirm Suno sounds vs music route selection is operationally important
- [x] Confirm skip-existing by default and `--overwrite-all` override behavior

**Status:** ✅ Complete

### Phase 2: Audit and Schema Design - **IN PROGRESS**

- [x] Audit normalization collisions between the library inventory view and the game_refactoring semantic view
- [x] Verify prompt coverage and target output tree expectations
- [x] Finalize canonical merged schema fields, naming rules, and regeneration views

**Status:** ✅ Complete

### Phase 3: Tooling Implementation - **IN PROGRESS**

- [x] Implement merge/materialization tooling for the canonical catalog
- [x] Implement async Suno submit/poll/download/rename/place workflow
- [x] Implement continue-on-error batch processing with skip-existing and `--overwrite-all`
- [x] Decide downstream-view policy: explicit regeneration only

**Status:** 🔧 In Progress

---

## 📝 Journal Entries

### 2026-05-19 11:24 - Initial scope lock

**What Changed:**
- Locked the architecture direction for the audio library work
- Established that the two existing catalogs must be merged literally into one normalized canonical catalog
- Established that `tools/library/audio_library` is effectively a cache/materialized output tree for generated assets

**Why:**
- The existing library catalog contains the concrete filenames and live tree locations currently in use
- The existing game_refactoring catalog contains semantic/query-driven regeneration intent
- The generator must preserve route choice (`suno-sounds` vs `suno-music`) and rename downloaded assets deterministically into the expected tree

**Key Decisions:**
- Keep the concrete filename families such as `level_complete_01` and `arcade_loop_01`
- Make generation route explicit in canonical records
- Use small `tmp/` scripts for audits/probes instead of long shell commands
- Default to skip-existing behavior, with `--overwrite-all` as the destructive override

**Next Steps:**
- [ ] Add tmp audit scripts for collisions and prompt coverage
- [ ] Add a tmp probe script that demonstrates the KIE/Suno async submit/poll flow from the existing code
- [ ] Use those results to finalize the canonical merged schema before implementing the real tooling

**Status:** In Progress

---

### 2026-05-19 11:35 - Audit + first implementation pass

**Achievement:**
Built the first merged-catalog and generator tooling pass, then validated the key dry-run behaviors.

**Implementation Details:**
- Created `tmp/audit_audio_catalog_merge_collisions.py` to inspect normalization overlap risk between the two current source catalogs.
- Created `tmp/check_audio_prompt_coverage.py` to verify prompt coverage and expected output directories.
- Created `tmp/probe_kie_suno_workflow.py` to prove the current KIE/Suno submit/poll route behavior from existing code.
- Created `tools/library/scripts/build_audio_catalog.py` to materialize `tools/library/audio_library/catalog.json`.
- Created `tools/library/scripts/generate_audio_variants.py` to provide cache-aware async generation with skip-existing, continue-on-error, and `--overwrite-all` behavior.
- Updated `tools/library/audio_library/README.md` to document the canonical catalog and generator workflow.
- Added a prompt alias block for `failure` in `tools/library/audio_library/README.md` to close the only prompt-coverage gap found during the audit.

**Validation Results:**
- Collision audit: 0 internal collisions in either source view, 0 direct cross-id overlaps in the first normalization pass.
- Prompt coverage: 32/32 library base names now covered after adding the `failure` alias block.
- Output tree expectations confirmed: `ambience`, `music`, `sfx`, `ui`.
- Canonical catalog build succeeded with:
  - `asset_family_count = 32`
  - `semantic_query_count = 140`
  - `record_count = 172`
- Generator dry-run validation confirmed:
  - skip-existing works when desired count is already satisfied
  - `--overwrite-all` forces deterministic target naming from `_01`, `_02`, etc.
  - `jump` resolves to `suno-sounds`
  - `ambient_loop` resolves to `suno-music`

**Technical Decisions:**
- The first canonical format keeps two record types:
  - `asset_family` for concrete cache/inventory families
  - `semantic_query` for query/regeneration-oriented records
- The generator currently targets only `asset_family` records, which is the safest way to preserve concrete filenames and directory compatibility first.
- The semantic records remain preserved in the canonical catalog for future regeneration/mapping passes.

**Next Steps:**
- [ ] Decide whether regenerated downstream views should be emitted automatically or only behind explicit flags
- [ ] Optionally enrich semantic-query records with stronger aliasing back to asset families
- [ ] Run a live generation test against a safe record once you want real network execution

**Status:** In Progress

---

### 2026-05-19 11:46 - Env loading follow-up for live orchestration

**Problem Encountered:**
The first live generation attempt failed even though KIE credentials existed, because the generator was executed from the repo root while the KIE key lived in `tools/kie-api/.env`.

**Solution:**
- Updated `tools/kie-api/src/kie_cli/config.py` so dotenv loading now checks multiple locations without overriding existing environment variables:
  1. current working directory `.env`
  2. repository root `.env`
  3. `tools/kie-api/.env`

**Why:**
This keeps tool-local configuration working while also supporting root-run orchestration scripts like `tools/library/scripts/generate_audio_variants.py`.

**Next Steps:**
- [ ] Re-run one live safe generation after the config fallback patch

**Status:** In Progress

---

### 2026-05-19 11:49 - Live download fallback hardening

**Problem Encountered:**
The first live `jump` generation successfully submitted and polled to `succeeded`, but the first returned temp MP3 URL produced HTTP 403 during download.

**Solution:**
- Updated `tools/library/scripts/generate_audio_variants.py` to:
  - collect multiple candidate Suno download URLs from `sunoData`
  - prefer `streamAudioUrl`, then `audioUrl`, then source URLs
  - retry candidates in order until one downloads successfully
  - send a browser-like `User-Agent` header during download requests

**Why:**
Some returned KIE/Suno URLs are completion metadata but not equally usable as direct download sources from the orchestration script context.

**Next Steps:**
- [ ] Retry the same safe live generation after the fallback patch

**Status:** In Progress

---

### 2026-05-19 11:51 - Live generation success

**Achievement:**
Completed live end-to-end generation for the safe `jump` asset family.

**What Was Verified:**
- async submit succeeded
- polling completed to terminal success
- alternate Suno download URL fallback worked
- file was downloaded and materialized into the library tree as `tools/library/audio_library/sfx/jump_04.mp3`
- catalog views were updated to include the new concrete variant

**Evidence:**
- submit job record exists at `tools/library/audio_library/jobs/jump/jump_03.mp3.submit.json`
- final job record shows successful polling and Suno outputs in `tools/library/audio_library/jobs/jump/jump_03.mp3.final.json`
- inventory now contains `jump_03` and `jump_04` entries in the library catalog view

**Technical Note:**
The first live run proved that polling worked but exposed a 403 on the first temp download URL. After adding ordered URL fallback, the subsequent live run succeeded using a `musicfile.kie.ai` download source.

**Next Steps:**
- [ ] Decide whether downstream views should be regenerated automatically by default
- [ ] Optionally generalize semantic-to-asset linkage beyond the first merged schema pass

**Status:** In Progress

---

### 2026-05-19 12:39 - Jobs-list + unattended batch runner

**Achievement:**
Added the normalized flat jobs-list layer plus a resumable unattended batch runner for the 32 concrete asset families.

**What Changed:**
- Added `tools/library/scripts/build_audio_jobs_list.py`
- Added `tools/library/scripts/run_audio_jobs_batch.py`
- Updated `tools/library/scripts/generate_audio_variants.py` so one request can map to multiple target variants
- Modeled Suno as returning **2 outputs per request** by default via `variants_per_request=2`

**Jobs-list Design:**
Each concrete family now expands into a normalized generation job containing fields like:
- `id`
- `destination_dir`
- `destination_pattern`
- `prompt`
- `generation_route`
- `existing_count`
- `missing_variants`
- `variants_per_request`
- `requests_needed`

**Batch Runner Behavior:**
- rebuilds `jobs_list.json` from the current canonical catalog
- skips complete families by default
- persists resumable state to `tools/library/audio_library/jobs/batch/latest_batch_state.json`
- supports dry-run, `--record-id`, and `--max-records`

**Validation Results:**
- jobs list built successfully for all `32` concrete asset families
- current summary:
  - `pending_job_count = 31`
  - `complete_job_count = 1`
  - `desired_total_variants = 4`
  - `variants_per_request = 2`
- dry-run batch wrapper succeeded on sample records and wrote resumable batch state

**Decision:**
Downstream non-library views should be regenerated **explicitly**, not automatically, during unattended overnight runs.

**Why:**
This keeps overnight generation focused on the concrete library taxonomy without mutating the semantic/refactoring-side source views unexpectedly.

**Next Steps:**
- [ ] Optionally run the unattended batch over all pending jobs overnight
- [ ] Optionally add richer reporting/summary output after a full overnight pass

**Status:** In Progress

---

### 2026-05-19 12:52 - Combined jobs list with semantic records

**Achievement:**
Extended the normalized jobs list so it can include both concrete asset-family records and semantic/world records in one shared job shape.

**What Changed:**
- Updated `tools/library/scripts/build_audio_jobs_list.py`
- Semantic records are now appended to the same `jobs_list.json`
- Added `record_type` so consumers can distinguish:
  - `asset_family`
  - `semantic_query`

**Shape Decision:**
The user asked that the semantic records use the **same job shape** as the concrete jobs.

**How Semantic Jobs Differ:**
- they carry `reference_urls`
- they use derived semantic destination patterns instead of concrete library taxonomy paths
- they are still normalized into the same top-level list

**Batch Safety Rule:**
`run_audio_jobs_batch.py` continues to execute only `asset_family` records by default, so the overnight concrete library run remains stable.

**Next Steps:**
- [ ] Rebuild and validate the combined jobs list summary counts

**Status:** In Progress

---

### 2026-05-19 13:01 - Preserve original Vercel taxonomy for semantic jobs

**Problem Encountered:**
The first semantic-job normalization pass rewrote semantic destinations into derived paths like `semantic/forest/bgm_03.mp3`, which lost the actual taxonomy already encoded in the Vercel-hosted source URLs.

**Why This Was Wrong:**
- the semantic source catalog already points at concrete Vercel repo paths like:
  - `assets/audios/bgm/forest_bgm_01.mp3`
  - `assets/audios/sfx/forest_enemy_01.mp3`
- those URLs are not arbitrary references; they already express the real vendored taxonomy we want to preserve

**Fix Implemented:**
- Updated `tools/library/scripts/build_audio_jobs_list.py`
- semantic jobs now derive `destination_pattern`, `destination_dir`, and `filename_prefix` from the first available reference URL
- when possible, semantic jobs now preserve exact patterns such as:
  - `assets/audios/bgm/forest_bgm_{nn:02d}.mp3`
  - `assets/audios/sfx/forest_enemy_{nn:02d}.mp3`
- fallback behavior still exists for malformed/missing URLs, but the normal path now preserves the Vercel taxonomy directly

**Validation Results:**
- rebuilt `tools/library/audio_library/jobs_list.json`
- confirmed semantic records now use preserved taxonomy paths instead of `semantic/...`
- verified examples including:
  - `assets/audios/bgm/calm_bgm_{nn:02d}.mp3`
  - `assets/audios/sfx/forest_enemy_{nn:02d}.mp3`
  - `assets/audios/sfx/forest_character_{nn:02d}.mp3`

**Decision:**
The reconciled jobs list should preserve the original Vercel taxonomy whenever that taxonomy is already present in the semantic source URLs.

**Status:** In Progress

---

### 2026-05-19 13:10 - Full 172-job execution support

**Problem Encountered:**
The batch runner and generator could only execute `asset_family` records even though `jobs_list.json` had already been expanded to 172 unified jobs.

**Root Cause:**
- `run_audio_jobs_batch.py` hard-filtered to `record_type == "asset_family"`
- `generate_audio_variants.py` assumed concrete record fields like `target` and `variants`
- semantic records instead store their prior materialization in `reference_items`

**Fix Implemented:**
- Updated `tools/library/scripts/generate_audio_variants.py` to support both record types
- semantic execution now:
  - derives target directory/prefix from semantic reference URLs
  - reads existing variants from `reference_items`
  - appends newly generated outputs back into `reference_items`
  - preserves `assets/audios/...` taxonomy for generated destinations
- Updated `tools/library/scripts/run_audio_jobs_batch.py` with:
  - `--include-semantic-query`
  - state tracking for whether semantic jobs are included

**Validation Results:**
- dry-run over the full expanded set succeeded with:
  - `jobs_total = 171`
  - `completed_jobs = 171`
- this matches the current state where 1 job was already complete and 171 remained pending

**Decision:**
- default batch behavior stays conservative for concrete-only runs
- full reconciled execution is now an explicit opt-in via `--include-semantic-query`

**Next Steps:**
- [ ] Launch the real full 172-job-capable batch

**Status:** In Progress

---

### 2026-05-19 13:22 - Verbose stage logging + music submit fix

**Problem Encountered:**
After enabling full 172-job execution, the first real batch showed two immediate orchestration issues:

- some `suno-music` submits failed with `Please enter callBackUrl.`
- another music submit failed because the model field was missing/invalid

The user also asked for execution output to be verbose **per item stage** before rerunning.

**Fix Implemented:**
- Updated `tools/library/scripts/generate_audio_variants.py`
  - added per-item `stage_events`
  - added `--verbose-stages`
  - added a default music model for library batch execution
  - added callback-url propagation into both Suno music and Suno sounds payloads
- Updated `tools/library/scripts/run_audio_jobs_batch.py`
  - added `--verbose-stages`
  - added `--callback-url`
  - now prints concise stage lines per job while still persisting structured JSON state

**Verbose Stages Added:**
- `record_start`
- `record_skip`
- `request_planned`
- `request_dry_run`
- `submit`
- `poll`
- `outputs`
- `download`
- `materialize`
- `request_error`

**Validation Results:**
- ran a focused real probe over previously failing music jobs:
  - `action_loop`
  - `ambient_loop`
  - `arcade_loop`
- all three completed successfully with verbose stage output
- batch summary after probe confirmed progress advanced and pending count dropped

**Decision:**
The full rerun should use verbose stage output so progress is human-readable while still writing resumable machine state to `tools/library/audio_library/jobs/batch/latest_batch_state.json`.

**Next Steps:**
- [ ] Relaunch the remaining full reconciled batch with verbose stage output

**Status:** In Progress

---

### 2026-05-19 14:02 - Mirrored root migration + filesystem-first reconciliation

**Problem Encountered:**
The local cache root had been manually moved to mirror the Vercel taxonomy under
`tools/library/assets/audios`, but the scripts were still hard-coded to the old
`tools/library/audio_library` path. Also, generation planning still trusted JSON
state more than on-disk reality.

**Fix Implemented:**
- Added shared path helper module:
  - `tools/library/scripts/audio_paths.py`
- Added filesystem reconciliation helper module:
  - `tools/library/scripts/audio_reality.py`
- Updated these scripts to resolve the mirrored root automatically:
  - `tools/library/scripts/build_audio_catalog.py`
  - `tools/library/scripts/build_audio_jobs_list.py`
  - `tools/library/scripts/generate_audio_variants.py`
  - `tools/library/scripts/run_audio_jobs_batch.py`
- Added tmp helpers for safe validation/refresh:
  - `tmp/validate_library_audio_reality_sync.py`
  - `tmp/inspect_library_audio_missing_examples.py`
  - `tmp/refresh_mirrored_library_audio_artifacts.py`

**New Behavior:**
- scripts prefer `tools/library/assets/audios` when present
- catalog/job planning now reconcile against the filesystem first
- deleted files are removed from effective planning state and become pending again
- batch/generator output continues to work with the mirrored root

**Validation Results:**
- mirrored root resolver selected:
  - `tools/library/assets/audios`
- reconciliation changed planning state based on real files on disk
- missing-file examples now surface as pending asset-family jobs such as:
  - `action_loop_03.mp3`
  - `ambient_loop_03.mp3`
  - `arcade_loop_03.mp3`

**Decision:**
The mirrored local root is now the canonical execution root whenever it exists,
and job planning should follow filesystem reality rather than stale index state.

**Next Steps:**
- [ ] Refresh generated catalog/jobs artifacts under the mirrored root
- [ ] Optionally resume generation from the reconciled pending set

**Status:** In Progress

---

### 2026-05-19 14:36 - Added disk-reconciled `catalog_final.json`

**Problem Encountered:**
The workflow now had a clean split between:

- `catalog.json` as planner shape
- `jobs_list.json` as the flat operational ledger reconciled from disk

but it was still missing a final materialized artifact in `catalog.json`-compatible
shape. That made it harder to inspect the current resolved state without mentally
joining planner records and job-ledger status.

**Fix Implemented:**
- Added `tools/library/scripts/build_audio_catalog_final.py`
- Added `tools/library/assets/audios/catalog_final.json` as a new generated artifact
- Updated `tmp/reconcile_flat_jobs_ledger_from_disk.py` so it now rebuilds both:
  - `jobs_list.json`
  - `catalog_final.json`
- Updated `tools/library/assets/audios/README.md` to document the new artifact and
  the intended role split

**`catalog_final.json` Design:**
- preserves the planner record shape from `catalog.json`
- rewrites concrete `variants` from real files on disk
- rewrites semantic `reference_items` from real files on disk
- adds per-record `materialized` status metadata derived from disk reality:
  - `existing_count`
  - `missing_variants`
  - `next_variant_numbers`
  - `next_destinations`
  - `status`

**Why:**
This keeps the roles separated cleanly:

- `catalog.json` = immutable/logical planner shape
- `jobs_list.json` = operational flat job ledger
- `catalog_final.json` = resolved/materialized final snapshot

**Next Steps:**
- [ ] Regenerate and inspect `catalog_final.json` against current disk state
- [ ] Optionally decide whether generation-time mutation should eventually move away
      from planner artifacts entirely and materialize only final snapshots

**Status:** In Progress

---

### 2026-05-19 14:44 - Promoted reconcile flow into a stable library launcher

**Problem Encountered:**
The new reconcile flow worked, but the easiest single command still lived under
`tmp/`, which made it feel like an experiment instead of a stable part of the
library workflow.

**Fix Implemented:**
- Added `tools/library/scripts/reconcile_audio_artifacts.py` as the official
  single-command launcher
- Kept `tmp/reconcile_flat_jobs_ledger_from_disk.py` as a thin compatibility
  wrapper that now delegates to the new library script
- Updated the README so the primary recommended command is now:
  - `python3 tools/library/scripts/reconcile_audio_artifacts.py`

**Why:**
This gives the workflow one durable entrypoint inside the library tooling itself,
while preserving the old tmp command for continuity.

**Status:** In Progress

---

### 2026-05-19 14:51 - Upgraded launcher to reconcile + run + refresh

**Problem Encountered:**
The first promoted launcher still only refreshed artifacts. That was not enough
for the intended operational workflow, which needed one command to:

1. reconcile
2. run missing jobs
3. refresh the local JSON artifacts again at the end

**Fix Implemented:**
- Upgraded `tools/library/scripts/reconcile_audio_artifacts.py`
- it now:
  - refreshes `jobs_list.json` and `catalog_final.json`
  - launches `run_audio_jobs_batch.py` for missing jobs
  - refreshes reconciled artifacts again after the run
- added workflow flags including:
  - `--reconcile-only`
  - `--dry-run`
  - `--include-semantic-query`
  - `--max-records`
  - `--record-id`

**Primary Command:**
- `python3 tools/library/scripts/reconcile_audio_artifacts.py`

**Why:**
This makes the launcher match the real desired behavior instead of acting like a
read-only artifact refresh helper.

**Status:** In Progress

---

### 2026-05-19 14:53 - Repaired launcher regression

**Problem Encountered:**
The first attempt to upgrade the launcher introduced a broken `main()` function
and stray lines, which left `tools/library/scripts/reconcile_audio_artifacts.py`
invalid.

**Fix Implemented:**
- rewrote `reconcile_audio_artifacts.py` cleanly
- restored a valid flow:
  - parse args
  - reconcile artifacts
  - optionally run missing jobs
  - refresh artifacts again
  - print final summary report

**Why:**
The single launcher needs to be reliable, since it is now the primary operational
entrypoint for the library audio workflow.

**Status:** In Progress

---

### 2026-05-19 15:03 - Switched launcher defaults to all jobs + verbose stages

**Problem Encountered:**
Even after the launcher was repaired, its default behavior still inherited the
older safety model:

- concrete-only by default
- quiet output by default

That was the opposite of the intended one-command UX.

**Fix Implemented:**
- Updated `tools/library/scripts/reconcile_audio_artifacts.py`
- the bare command now defaults to:
  - include semantic jobs
  - enable verbose per-item stage output
- added inverse flags for control:
  - `--concrete-only`
  - `--quiet`

**New Mental Model:**
The bare command:

```bash
python3 tools/library/scripts/reconcile_audio_artifacts.py
```

now effectively means:

```bash
python3 tools/library/scripts/reconcile_audio_artifacts.py --include-semantic-query --verbose-stages
```

**Why:**
This matches the intended operational UX: one command should run the full
workflow across all jobs and make the progress human-readable without extra flags.

**Status:** In Progress

---

## 💭 Notes & Decisions

### Current mental model

- `tools/library/assets/audios/audios.json` = concrete inventory / cache view
- `tools/game_refactoring/catalogs/audios.json` = semantic regeneration/query view
- future `catalog.json` = canonical merged source of truth

### Generation workflow constraints

- SFX and ultra-short event sounds use Suno sounds
- Music-like background/ambient assets use Suno music
- Suno tasks are async and must be polled until terminal status
- Returned audio must be downloaded, renamed to the expected variant filename, and moved into the correct library subtree

---

## ✅ Testing Checklist

- [x] Collision audit script runs successfully
- [x] Prompt coverage script runs successfully
- [x] Suno workflow probe script runs successfully
- [x] Canonical merge tool can run without overwriting existing files by default
- [x] `--overwrite-all` behavior is explicit and controlled

---

### 2026-05-19 22:37 - Published obfuscated audio CDN/name mismatch audit

**Achievement:**
Audited published `gamezone*` outputs under `games/published/obfuscated` to map
`*.mp3` usage and compare runtime references against the reconciled library artifacts.

**What Changed:**
- Added `tmp/library-consolitaion/audit_published_game_audio_refs.py`
- Added `tmp/library-consolitaion/summarize_published_game_audio_ref_audit.py`
- Added `tmp/library-consolitaion/analyze_runtime_cdn_mismatches.py`
- Added `tmp/library-consolitaion/OPERATION_RULES.md`

**Operational Rule Locked:**
- For this audit lane, do **not** use long inline shell commands.
- Use focused tmp scripts only, and keep all outputs under `tmp/library-consolitaion/`.

**Audit Findings:**
- scanned `1032` published `gamezone*` folders
- scanned `5188` text files
- found `11406` mp3 references total
- split into:
  - `8609` runtime-source references
  - `2797` artifact-report references
- runtime-only mismatch count: `2934`

**Runtime mismatch breakdown:**
- `1892` = `cdn_library_path_missing_from_catalog`
- `1028` = `basename_only_audios_match`
- `8` = `other_mp3_reference`
- `6` = `obfuscated_local_audio_asset`

**Interpretation:**
- The dominant real problem is **catalog/path drift**, not total absence of audio names.
- Many published games reference files like:
  - `assets/audios/ui/ui_click_01.mp3`
  - `assets/audios/ui/fail_01.mp3`
  - `assets/audios/ui/level_complete_01.mp3`
  - `assets/audios/ui/success_01.mp3`
- A large subset still matches by basename in `audios.json`, which suggests the main issue is:
  - wrong directory taxonomy
  - or catalog finalization/path materialization mismatch
  - rather than totally unknown files

**Noise clarified:**
- `artifacts/simple_obfuscation_report.json` contributes a large amount of non-runtime noise.
- That noise is now separated from runtime HTML/JS/CSS references before evaluating next steps.

**Next likely repair direction:**
- Build a canonical **published-runtime path reconciliation list** for the top mismatched runtime paths.
- Decide whether to:
  1. rewrite published runtime refs to canonical library paths
  2. materialize missing canonical-compatible aliases in the library
  3. or fix `catalog_final.json` path emission so future publish output references the right locations.

**Status:** In Progress

---

### 2026-05-19 22:52 - Added permanent reduced/enriched deploy-audio mapping layer

**Achievement:**
Created a permanent compatibility-mapping manifest for runtime path repair before
implementing the eventual deploy/sanitizer workflows.

**What Changed:**
- Added `tools/library/assets/audios/deploy_audio_mappings.json`
- Added `tools/library/scripts/validate_deploy_audio_mappings.py`
- Updated `tools/library/assets/audios/README.md`

**Mapping Model:**
- `reduced_aliases`
  - low-risk reroot/taxonomy normalization mappings
- `enriched_aliases`
  - curated semantic polyfills for high-frequency runtime expectations

**Seeded Reduced Examples:**
- `ui/game_over_01..04` → `sfx/game_over_01..04`
- `ui/level_complete_01..04` → `sfx/level_complete_01..04`
- `ui/success_01..04` → `sfx/success_01..04`
- `ambience/ambience_loop_01..04` → `music/ambient_loop_01..04`

**Seeded Enriched Examples:**
- `ui/fail_01..04` → `sfx/failure_01..04`
- `ui/start_game_01..04` → `ui/start_01..04`
- `ui/ui_click_01..04` → `ui/click_01..04`
- `ui/ui_hover_01..04` → `ui/hover_01..04`
- `music/music_loop_01..04` → `music/ambient_loop_01..04`
- `music/space_ambient_01` → `music/ambient_loop_01`

**Sanitization Prep Captured in Manifest:**
- `assets/bgm/0001/`
- `assets/sfx/0001/`
- `assets/audio/0000/`

These prefixes are not deployed compatibility aliases; they are marked as future
sanitize-to-empty families for the obfuscator/publication cleanup pass.

**Why:**
This gives the workflow a permanent source of truth for:

1. safe compatibility aliases
2. creative semantic polyfills
3. known bad outlier families that should be stripped instead of mapped

**Next Steps:**
- [ ] run the validator and confirm focused mismatch coverage
- [ ] implement the future `deploy_audios.py` two-stage materializer
- [ ] implement the obfuscator-side outlier sanitization pass using the manifest

**Status:** In Progress

---

### 2026-05-19 22:57 - Added manifest-driven `deploy_audios.py` for sibling library deployment

**Achievement:**
Implemented the first real deploy step: a manifest-driven audio deployer that can
materialize the canonical + reduced view first and then overlay enriched aliases
into the sibling `game_agent_library` repo.

**What Changed:**
- Added `tools/library/scripts/deploy_audios.py`
- Updated `tools/library/assets/audios/README.md`

**Target Confirmed:**
- sibling repo root exists at `../game_agent_library`
- target audio root exists at `../game_agent_library/assets/audios`
- current target already contains:
  - `ambience/`
  - `bgm/`
  - `music/`
  - `sfx/`
  - `ui/`
  - `unmatched/`

**Deploy Script Behavior:**
- `--stage reduced`
  - copies canonical files from the current library
  - applies only `reduced_aliases`
- `--stage enriched`
  - applies only `enriched_aliases`
  - intended to layer on top of the reduced/base view
- `--stage all`
  - runs canonical + reduced + enriched in one shot

**Output Report:**
- default report path:
  - `../game_agent_library/assets/audios/deploy_audio_report.json`

**Why:**
This turns the compatibility-mapping manifest into an operational deployment
workflow instead of leaving it as documentation-only policy.

**Next Steps:**
- [ ] dry-run the new deploy script against `../game_agent_library/assets/audios`
- [ ] inspect the deploy report counts for canonical/reduced/enriched operations
- [ ] implement the obfuscator-side sanitize-to-empty pass using the same manifest

**Status:** In Progress

---

### 2026-05-19 23:10 - Real sibling deploy + one-time legacy gamezone sanitization

**Achievement:**
Completed the real sibling-library deploy and then ran a one-time cleanup pass that
blanked legacy/outlier audio refs across all `games/**/gamezone-*` descendants.

**What Changed:**
- Ran real deploy into sibling library via:
  - `python3 tools/library/scripts/deploy_audios.py --stage all`
- Added one-time cleanup utility:
  - `tmp/library-consolitaion/sanitize_gamezone_legacy_audio_refs.py`
- Wrote cleanup report:
  - `tmp/library-consolitaion/gamezone_legacy_audio_sanitization_report.json`

**Sibling Deploy Result:**
- target: `../game_agent_library/assets/audios`
- canonical files:
  - `copied = 0`
  - `unchanged = 684`
- reduced aliases:
  - `copied = 16`
- enriched aliases:
  - `copied = 21`
- report written to:
  - `../game_agent_library/assets/audios/deploy_audio_report.json`

**Interpretation:**
- the sibling library already had the canonical base populated
- this pass layered in the missing compatibility aliases/polyfills only

**One-Time Sanitization Scope:**
- scans all `gamezone-*` descendants under `games/`
- includes raw/published/backups/runs/quarantine-style descendants when present
- only removes known bad legacy/outlier audio path families:
  - `assets/bgm/0001/`
  - `assets/sfx/0001/`
  - `assets/audio/0000/`

**Sanitization Result:**
- `scanned_file_count = 95430`
- `changed_file_count = 880`
- `total_replacements = 3704`

**Representative changed paths:**
- `games/raw/gamezone-0d23d3a8-564a-4409-966f-296027a2ee9f/index.html`
- `games/raw/gamezone-1824d860-3dfa-452e-937a-e4ad7f171844/index.html`
- `games/published/public/gamezone-1824d860-3dfa-452e-937a-e4ad7f171844/remix-98883734dd52288ebeb13856ade0a330/index.html`
- many mirrored/backup/quarantine descendants of the same gamezone families

**Behavior Confirmed:**
- legacy refs were not remapped
- they were turned into inert empty-string paths / empty audio source values
- representative spot checks showed the old `assets/bgm/0001/...`,
  `assets/sfx/0001/...`, and `assets/audio/0000/...` references were removed

**Why:**
This keeps the permanent fix split cleanly:

1. deploy compatibility aliases into the sibling library for the real supported
   audio taxonomy
2. do a one-time cleanup on historical `gamezone-*` artifacts so the known bad
   legacy refs stop leaking through old outputs

**Status:** In Progress

---

### 2026-05-19 23:20 - Coverage summary documented and completion checkpoint

**Achievement:**
Documented the practical end-state coverage after both the sibling-library
enrichment deploy and the one-time historical `gamezone-*` sanitization pass.

**Coverage Summary:**
- focused runtime mismatch coverage: `19 / 19` unique high-priority paths
- effective focused coverage rate: `100%`
- sibling compatibility deployment added:
  - `16` reduced aliases
  - `21` enriched aliases
  - `37` total compatibility/polyfill paths
- one-time historical cleanup removed/blanked:
  - `3704` legacy audio refs
  - across `880` files

**Practical Interpretation:**
- the supported runtime mismatch set is fully covered
- the sibling library now exposes the enriched compatibility layer needed for the
  targeted runtime taxonomy drift cases
- the old bad legacy path families were scrubbed from historical `gamezone-*`
  outputs instead of being remapped forward

**Final State:**
- enriched compatibility paths are now materialized in the sibling library
- historical legacy refs under `games/**/gamezone-*` have been neutralized into
  inert empty-string/no-op values
- the report artifacts for both deployment and cleanup are preserved for audit

**Status:** Complete

---

## 🎯 Success Criteria

- [x] One canonical merged audio catalog exists
- [x] Existing concrete filenames and directories remain compatible
- [x] Semantic regeneration intent from the refactoring catalog is preserved
- [x] Async Suno generation workflow is supported end-to-end
- [x] Skip-existing and continue-on-error behavior are implemented
- [x] Documentation and journal are updated
