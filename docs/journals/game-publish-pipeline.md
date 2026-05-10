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