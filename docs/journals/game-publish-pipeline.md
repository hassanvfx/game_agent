# Game Publish Pipeline Journal

**Last Updated:** 2026-05-10  
**Feature Spec:** game_publish_pipeline  
**Backend Reference:** game_obfuscator → game_deploy orchestration

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Contract discovery - **COMPLETE**
- [x] Inspect `game_obfuscator` machine-facing CLI surfaces
- [x] Confirm `game_deploy` can act as the packaging step after obfuscation
- [x] Define the higher-order orchestration role

### ✅ Phase 2: Tool scaffolding - **COMPLETE**
- [x] Create package module
- [x] Create CLI entrypoint
- [x] Add README

### ✅ Phase 3: Orchestration implementation - **COMPLETE**
- [x] Resolve source refactor outputs
- [x] Build obfuscator manifest
- [x] Launch obfuscator via `start`
- [x] Poll canonical obfuscator `status`
- [x] Resolve obfuscated game outputs via `output-path --include-games`
- [x] Build deploy manifest
- [x] Launch `game_deploy`
- [x] Emit final pipeline report JSON

### ✅ Phase 4: External-contract alignment - **COMPLETE**
- [x] Inspect the cleaned-up `game_obfuscator` external-agent contract
- [x] Confirm the supported machine-facing surface is `start` / `status` / `output-path`
- [x] Remove unsupported publish-pipeline launch flags that are no longer part of the contract
- [x] Re-verify the publish pipeline CLI surface after the integration change

---

## 📝 Journal Entries

### 2026-05-10 07:34 - Initial higher-order publish pipeline scaffold

**What Changed:**
Created a higher-order orchestration tool at `tools/game_publish_pipeline/` that chains `game_obfuscator` and `game_deploy`.

**Files Created:**
- `tools/game_publish_pipeline/game_publish_pipeline/__init__.py`
- `tools/game_publish_pipeline/game_publish_pipeline/pipeline.py`
- `tools/game_publish_pipeline/scripts/publish_games.py`
- `tools/game_publish_pipeline/README.md`

**Orchestration Flow:**
1. accept one or more `game_refactoring` output directories
2. build a temporary obfuscator manifest
3. call:
   - `game_obfuscator_cli.py start`
4. poll:
   - `game_obfuscator_cli.py status`
5. resolve outputs:
   - `game_obfuscator_cli.py output-path --include-games`
6. build a temporary deploy manifest
7. call:
   - `tools/game_deploy/scripts/deploy_games.py`
8. write a final pipeline report

**Machine-Facing Report Shape:**
- `source_inputs`
- `obfuscation.manifest_path`
- `obfuscation.start`
- `obfuscation.final_status`
- `obfuscation.output`
- `deployment.manifest_path`
- `deployment.results`

**Design Decision:**
Kept `game_publish_pipeline` as pure orchestration glue:
- no new obfuscation logic
- no new deploy transformation logic
- only manifest shaping, subprocess orchestration, polling, and final report aggregation

**Status:** Complete

### 2026-05-10 11:18 - Align publish pipeline with cleaned-up obfuscator contract

**What Changed:**
Updated `tools/game_publish_pipeline/game_publish_pipeline/pipeline.py` after reviewing the new `tools/game_obfuscator/docs/game-obfuscator-external-agent-contract.md` and the linked README section, then simplified the pipeline again based on the newer blocking execution behavior.

**Contract Findings:**
- the supported external CLI surface is now:
  - `start`
  - `status`
  - `output-path`
- input is configured through `--manifest`
- output location is derived from `runs/<run_id>/output/`
- caller-configurable launch flags like `--timeout-ms` and `--max-game-seconds` are not part of the documented machine-facing contract anymore
- the obfuscation launch stage is now treated as synchronous/blocking for pipeline integration, so an additional poll loop is no longer needed in `game_publish_pipeline`

**Implementation Change:**
Removed the extra obfuscator launch flags from `game_publish_pipeline` and dropped the obfuscator polling stage so the orchestrator now:
1. calls the blocking launch surface
2. captures the returned payload
3. resolves outputs immediately via `output-path`

```bash
python3 scripts/game_obfuscator_cli.py start --manifest <manifest-path>
python3 scripts/game_obfuscator_cli.py output-path --run-id <run_id> --include-games
```

**Why:**
This keeps `game_publish_pipeline` aligned with the simplified external contract and avoids unnecessary orchestration complexity when the obfuscator stage is already blocking.

**Verification:**
- ran:
  - `python3 tools/game_publish_pipeline/scripts/publish_games.py --help`
- confirmed the pipeline CLI still parses and no longer exposes the removed obfuscator passthrough flags or poll interval configuration

**Documentation Follow-up:**
- updated `tools/game_publish_pipeline/README.md` so it now describes:
  - deterministic raw staging
  - deploy-then-obfuscate flow
  - the current report fields and supported arguments

**Smoke Test Finding:**
- an earlier rerun of `tmp/run_publish_pipeline_fixed.py` showed the first sync assumption was still ahead of the actual implementation at that time
- the immediate no-poll attempt returned:
  - `obfuscation.final_status.status = "created"`
  - `obfuscation.output.status = "running"`

**Updated Tool Contract Follow-up:**
- re-checked the actual `game_obfuscator` implementation after the sync/output-root changes landed
- confirmed `tools/game_obfuscator/scripts/game_obfuscator_cli.py` now:
  - runs `start` synchronously via `subprocess.run(...)`
  - accepts `--output-root`
  - returns terminal result JSON including per-game `game_outputs`

**Pipeline Refactor:**
- updated `tools/game_publish_pipeline/game_publish_pipeline/pipeline.py` to:
  - call synchronous `start`
  - pass `--output-root` using `games/published/obfuscated`
  - remove the main polling loop
  - stop depending on `output-path` for the primary flow
  - use the terminal `start` payload as `obfuscation.final_status`

**Verified Outcome After Refactor:**
- reran `tmp/run_publish_pipeline_fixed.py`
- confirmed the report now contains direct obfuscator output placement and terminal completion in one pass, including:
  - `obfuscation.start.status = "completed"`
  - `obfuscation.output.output_path = "/Users/hassan/repos/game_agent/games/published/obfuscated"`
  - per-game outputs under `games/published/obfuscated/<game_id>`

**Documentation Follow-up:**
- updated `tools/game_publish_pipeline/README.md` to reflect:
  - synchronous `start`
  - direct `--output-root`
  - no polling in the main flow

**Maintenance Script Addition:**
- added `tools/game_publish_pipeline/scripts/rebuild_all_raw_games.py`
- purpose:
  - walk all top-level raw game directories under `games/raw`
  - build a manifest automatically
  - rerun `game_publish_pipeline` over the full raw set
  - rebuild both public and obfuscated outputs in one reusable operation
- operator-facing behavior:
  - prints discovered raw games with indexed progress lines
  - shows the exact publish command before execution
  - supports `--dry-run`
  - supports `--limit` for smaller smoke passes
  - writes a consolidated report under `tmp/rebuild_all_raw_games_reports/`

**Maintenance Script Verification:**
- ran:
  - `python3 tools/game_publish_pipeline/scripts/rebuild_all_raw_games.py --help`
- fixed an initial repo-root path bug in the script defaults
- reran:
  - `python3 tools/game_publish_pipeline/scripts/rebuild_all_raw_games.py --dry-run --limit 3`
- confirmed the script now:
  - discovers raw games under `/Users/hassan/repos/game_agent/games/raw`
  - prints indexed progress lines
  - emits the exact downstream publish command
  - writes the expected manifest/report paths

**Historical Remix Manifest Prep:**
- added `tmp/build_deploy_manifest_from_historical_runs.py`
- purpose:
  - inspect a fixed list of historical v4 runs on `/Volumes/HDD2026/output`
  - find usable remix outputs under each run’s `output/<game_id>/`
  - select the most recent available remix per original `game_id`
  - write a deploy-ready manifest without running publish/deploy
- output manifest:
  - `tmp/retry_manifests/latest_selected_remix_deploy_manifest.json`

**Historical Manifest Verification:**
- ran:
  - `python3 tmp/build_deploy_manifest_from_historical_runs.py --dry-run`
  - `python3 tmp/build_deploy_manifest_from_historical_runs.py`
- confirmed:
  - 17 historical runs were inspected
  - 50 unique game ids were selected from the most recent available remix outputs
  - the written manifest shape matches `game_deploy` expectations:
    - array of objects with `source` paths only

**Status:** Complete

### 2026-05-10 20:48 - Single-game publisher screenshot preservation probe

**What Changed:**
Created a one-item publish probe manifest and ran `game_publish_pipeline` against a single retry output that already contained screenshot files, while targeting isolated temporary public/obfuscated roots under `tmp/publisher_probe/`.

**Probe Input:**
- source:
  - `/Volumes/HDD2026/output/run_v4_brainrot_momsday_retry_20260509T160832Z/output/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- probe manifest:
  - `tmp/retry_manifests/single_gamezone_0f3dc736_brainrot_retry_publish_manifest.json`

**Pre-Publish Verification:**
Confirmed the source input already contained screenshot-like runtime captures:
- `screens_01_title_or_entry.png`
- `screens_02_live_play.png`
- `screens_03_menu_or_modal.png`
- `screens_04_fail_or_win.png`
- plus postvisual images:
  - `postvisual_screen_01_entry.png`
  - `postvisual_screen_02_play.png`

**Probe Command:**
```bash
python3 tools/game_publish_pipeline/scripts/publish_games.py \
  --manifest tmp/retry_manifests/single_gamezone_0f3dc736_brainrot_retry_publish_manifest.json \
  --published-public-root tmp/publisher_probe/public \
  --published-obfuscated-root tmp/publisher_probe/obfuscated \
  --report-path tmp/publisher_probe/report.json \
  --overwrite
```

**Observed Publish Result:**
- raw staging created:
  - `games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0/remix-c2e0f95e77955251616baff7b6f0c66e`
- public deploy created:
  - `tmp/publisher_probe/public/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0/remix-c2e0f95e77955251616baff7b6f0c66e`
- obfuscated output created:
  - `tmp/publisher_probe/obfuscated/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0/remix-c2e0f95e77955251616baff7b6f0c66e`

**Critical Verification:**
Confirmed that both output roots contain screenshot directories and files:
- public:
  - `tmp/publisher_probe/public/.../screenshots/01.jpg` through `06.jpg`
- obfuscated:
  - `tmp/publisher_probe/obfuscated/.../screenshots/01.jpg` through `06.jpg`

**Conclusion:**
This probe shows the current publish pipeline + obfuscator path can preserve screenshots into the obfuscated output when the input game contains them. The remaining failures are therefore more likely tied to historical/stale published outputs or the downstream app-artifact refresh/catalog mapping path, rather than the core single-game publisher path itself.

**Status:** Complete

### 2026-05-10 20:55 - Ten-item mixed-source pilot validation

**What Changed:**
Prepared a 10-item pilot manifest from the 231 source pool, mixing:
- 5 local raw inputs from `games/raw`
- 5 HDD-backed run outputs from `/Volumes/HDD2026/output/...`

Then ran the publisher into isolated temp roots and validated screenshot carry-through from public deploy outputs to obfuscated outputs with a dedicated helper script.

**Pilot Manifest:**
- `tmp/retry_manifests/vatsal_app_alpha_10_pilot_manifest.json`

**Pilot Validation Helper:**
- `tmp/validate_publisher_probe_10.py`

**Pilot Publish Roots:**
- public:
  - `tmp/publisher_probe_10/public`
- obfuscated:
  - `tmp/publisher_probe_10/obfuscated`
- report:
  - `tmp/publisher_probe_10/report.json`

**Validation Outcome:**
- total pilot rows:
  - `10`
- public outputs with screenshots:
  - `10 / 10`
- obfuscated outputs with screenshots:
  - `9 / 10`
- exact screenshot count match from public → obfuscated:
  - `9 / 10`

**Single Failing Entry:**
- `game_id`:
  - `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- `remix_uuid`:
  - `75e46ca7e006279a9ec2d8352e54a018`
- public screenshot count:
  - `4`
- obfuscated screenshot count:
  - `0`

**Failure Shape:**
The failing obfuscated path for the raw-backed entry was completely absent when inspected:
- `tmp/publisher_probe_10/obfuscated/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0/remix-75e46ca7e006279a9ec2d8352e54a018`

This means the 10-item pilot does **not** show a pure screenshot-copy bug across the board. Instead:
- 9 entries successfully carried screenshots all the way through
- 1 raw-backed entry failed because its obfuscated output directory was not produced/populated at all

**Interpretation:**
The publisher/obfuscator path is mostly working for both source families, but there is still at least one edge case where an obfuscated remix output is missing entirely. That failure should be debugged as an output-generation / per-entry obfuscation issue, not merely as screenshot remapping.

**Status:** Complete

### 2026-05-10 20:59 - Ten-item pilot retry confirms persistent raw-backed failure

**What Changed:**
Re-ran the same 10-item pilot into a fresh temp output root using a short helper script so the result could be compared without reusing the first probe directories.

**Retry Helper Scripts:**
- publish retry:
  - `tmp/retry_publisher_probe_10.py`
- retry validator:
  - `tmp/validate_publisher_probe_10_retry.py`

**Retry Publish Roots:**
- public:
  - `tmp/publisher_probe_10_retry/public`
- obfuscated:
  - `tmp/publisher_probe_10_retry/obfuscated`
- report:
  - `tmp/publisher_probe_10_retry/report.json`

**Retry Outcome:**
The retry reproduced the same aggregate result:
- public outputs with screenshots:
  - `10 / 10`
- obfuscated outputs with screenshots:
  - `9 / 10`
- exact screenshot count match from public → obfuscated:
  - `9 / 10`

**Persistent Failing Entry:**
- `game_id`:
  - `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- retry remix uuid:
  - `4037302139cfa7befef5d711f08f4b82`
- public screenshot count:
  - `4`
- obfuscated screenshot count:
  - `0`

**Persistence Finding:**
The failure is persistent for the raw-backed `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0` source:
- first pilot failure:
  - remix `75e46ca7e006279a9ec2d8352e54a018`
- retry failure:
  - remix `4037302139cfa7befef5d711f08f4b82`

Meanwhile, the HDD-backed source for the same `game_id` continued to succeed:
- remix `c2e0f95e77955251616baff7b6f0c66e`
- public screenshots:
  - `6`
- obfuscated screenshots:
  - `6`

**Interpretation:**
The deeper investigation changed the working hypothesis.

**Root Cause Discovery:**
This is not primarily a source-shape bug. The real outlier trigger is a **run-level identity collision** inside `game_obfuscator` when the pilot includes two different remix sources that share the same `game_id`.

Evidence:
- the pilot includes both:
  - raw-backed `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
  - HDD-backed `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- in the retry obfuscator run state, both entries report the same per-game paths:
  - `input_mirror_path`: `.../input/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
  - `working_path`: `.../games/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0/working`
- the persisted `game_state.json` for that `game_id` only reflects the HDD-backed successful remix:
  - `source_path`: `.../remix-c2e0f95e77955251616baff7b6f0c66e`
  - `status`: `succeeded`
  - `attempt_count`: `2`

That means the raw-backed and HDD-backed entries are not isolated from each other inside the same obfuscator run:
- they collapse onto the same per-game state directory keyed only by `game_id`
- later processing can overwrite earlier per-game state/artifact paths
- this explains why the raw-backed remix output can disappear while the HDD-backed remix for the same `game_id` survives

**Additional Source Comparison Finding:**
The raw-backed source does differ from the HDD-backed source:
- raw-backed source has older-style files like:
  - `playwright_after_shot.png`
  - `playwright_after_start.png`
  - `playwright_initial.png`
- HDD-backed source has:
  - `screens_01_title_or_entry.png`
  - `screens_02_live_play.png`
  - `screens_03_menu_or_modal.png`
  - `screens_04_fail_or_win.png`
  - `postvisual_screen_01_entry.png`
  - `postvisual_screen_02_play.png`
  - plus `amp/`

But the collision evidence is stronger than the source-shape theory because the obfuscator run itself stores both variants under the same `game_id`-scoped run paths.

**Conclusion:**
The persistent outlier is caused by a per-run collision on duplicate `game_id` entries, not simply by screenshot naming differences. The obfuscator needs a per-entry identity that includes remix-level uniqueness, not just `game_id`, when mirroring input / working state / game state inside a run.

**Status:** Complete

### 2026-05-10 21:21 - Obfuscator entry-key fix validated against the 10-item pilot

**What Changed:**
Adapted the obfuscator so its internal run-scoped identity is derived from the externally unique output path mirror instead of collapsing to bare `game_id`.

**Core Fix:**
- added `entry_key` derivation from `output_path`
- propagated `entry_key` into the copied input manifest
- changed internal run bookkeeping to key by `entry_key` for:
  - `run_dir / games / <entry_key> / game_state.json`
  - `run_dir / input / <entry_key>`
  - `working_path`
- preserved the externally provided unique `output_path` as-is

**Files Updated:**
- `tools/game_obfuscator/scripts/orchestration_state.py`
- `tools/game_obfuscator/scripts/create_run.py`
- `tools/game_obfuscator/scripts/prepare_inputs.py`
- `tools/game_obfuscator/scripts/obfuscate_simple_outputs.py`
- `tools/game_obfuscator/scripts/game_obfuscator_cli.py`

**Validation Scripts Added:**
- `tmp/retry_publisher_probe_10_v2.py`
- `tmp/validate_publisher_probe_10_v2.py`

**Validation Run:**
Executed the 10-item pilot again into fresh roots:
- public:
  - `tmp/publisher_probe_10_v2/public`
- obfuscated:
  - `tmp/publisher_probe_10_v2/obfuscated`
- report:
  - `tmp/publisher_probe_10_v2/report.json`

**Validated Result:**
- public outputs with screenshots:
  - `10 / 10`
- obfuscated outputs with screenshots:
  - `10 / 10`
- exact public → obfuscated screenshot count match:
  - `10 / 10`

**Important Specimen Recovery:**
The previously failing raw-backed specimen for:
- `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
now succeeds alongside the HDD-backed variant because the two entries are separated by distinct entry keys:
- `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0__remix-9fe6189a855a034640b92a006ba70e20`
- `gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0__remix-c2e0f95e77955251616baff7b6f0c66e`

**Outcome:**
The collision is fixed for the validated pilot. The obfuscator now honors the unique mirrored public/obfuscated identity all the way through its internal run bookkeeping.

**Status:** Complete

---

## 📚 Quick Reference

### CLI
```bash
python3 tools/game_publish_pipeline/scripts/publish_games.py --inputs /path/to/refactor/output/game-a
```

### Dry-run
```bash
python3 tools/game_publish_pipeline/scripts/publish_games.py --inputs /path/to/refactor/output/game-a --dry-run
```

### Key Files
- `tools/game_publish_pipeline/game_publish_pipeline/pipeline.py`
- `tools/game_publish_pipeline/scripts/publish_games.py`
- `tools/game_publish_pipeline/README.md`

---

## 🎯 Success Criteria

- [x] Higher-order orchestration tool exists
- [x] Uses the existing `game_obfuscator` machine-facing contract
- [x] Feeds obfuscator outputs into `game_deploy`
- [x] Emits one final machine-readable pipeline report
- [x] Stays aligned with the simplified external-agent contract documented for `game_obfuscator`

---

*This journal documents the first pass of the higher-order `game_publish_pipeline` tool that orchestrates obfuscation followed by deploy packaging.*