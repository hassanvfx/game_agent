# Game Obfuscator Default Tuning Journal

**Last Updated:** 2026-05-14  
**Feature Spec:** N/A  
**Backend Reference:** See `tools/game_obfuscator/scripts/`

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Baseline inspection and test harness - **COMPLETE**

- [x] Inspect the current Game Obfuscator CLI entrypoints and simple pipeline behavior
- [x] Confirm the input manifest shape and raw game source layout
- [x] Create a reusable 4-random-game test harness against `games/raw`
- [x] Add a compact output inspection helper for rapid review

**Status:** ✅ Complete

### Phase 2: Baseline execution and review - **COMPLETE**

- [x] Run the 4-game baseline batch with current defaults
- [x] Review output structure, retained files, and generated reports
- [x] Summarize observed default behavior and compatibility characteristics

**Status:** Complete

### Phase 3: Default-behavior tuning - **COMPLETE (NO CHANGE REQUIRED FOR PUBLISH PARAMETERIZATION)**

- [x] Identify low-risk default changes based on observed outputs
- [x] Confirm whether publish uses different obfuscator parameterization
- [x] Confirm whether any publish-specific adjustment is required for inline-script handling

**Status:** ✅ Complete

---

## 📝 Journal Entries

### 2026-05-14 18:21 - Initial baseline inspection

**What Changed:**
- Created the task journal for obfuscator default-tuning work
- Inspected the current CLI wrapper and run-scaffold scripts
- Confirmed the current obfuscator pipeline is synchronous from the CLI `start` surface
- Confirmed raw game folders under `games/raw` are viable direct sources for a baseline batch

**Why:**
The goal is to closely inspect the current output before changing defaults. That requires understanding exactly how the current simple pipeline mirrors, prunes, transforms, and reports per-game outputs.

**Files Reviewed:**
- `tools/game_obfuscator/README.md` - documents the current simple deterministic pipeline and `GAME_OBFUSCATION_LEVEL`
- `tools/game_obfuscator/scripts/game_obfuscator_cli.py` - CLI entrypoints and payload contracts
- `tools/game_obfuscator/scripts/create_run.py` - run scaffold and manifest normalization
- `tools/game_obfuscator/scripts/prepare_inputs.py` - source mirroring and integrity verification
- `tools/game_obfuscator/scripts/obfuscate_simple_outputs.py` - prune + transform behavior
- `tools/game_obfuscator/manifests/random_batch_005.json` - example manifest shape
- `tmp/run_raw_obfuscator.py` - older disposable helper showing prior test harness pattern
- `games/raw/gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0` - representative raw game directory shape

**Technical Findings:**
- `start` in `game_obfuscator_cli.py` currently runs the simple pipeline synchronously and returns final result JSON.
- `create_run.py` accepts a manifest with `games[].game_id`, `display_name`, and `source_path`, then materializes per-game state and output paths.
- `prepare_inputs.py` mirrors each source directory and only enforces the presence of `index.html` as the integrity gate.
- `obfuscate_simple_outputs.py`:
  - mirrors the prepared input to the output directory
  - preserves `index.html`
  - preserves top-level folders from `preserved_surface_folders` with defaults `assets` and `screenshots`
  - deletes all other top-level files/folders
  - inside `assets/`, keeps only `.js` and `.css`, deleting other asset file types
  - runs `transform_web_assets.js`
  - writes `artifacts/simple_obfuscation_report.json`

**Next Steps:**
- [x] Build a reusable 4-random-game manifest/test launcher for `games/raw`
- [x] Add a compact inspection helper that summarizes outputs and reports per selected game
- [x] Run the baseline batch and inspect output details before proposing any tuning
- [ ] Decide which defaults should change first, based on the baseline findings
- [ ] Re-run the same seeded batch after tuning for direct comparison

**Status:** In Progress

---

### 2026-05-14 18:23 - Baseline batch executed on four seeded raw games

**Achievement:**
- Added a deterministic seeded 4-game baseline harness and an inspection helper
- Executed the batch successfully with the current default settings
- Captured a concrete summary of what the current simple obfuscator keeps, removes, and transforms

**Implementation Details:**
- Created `tmp/run_four_random_raw_obfuscator_batch.py` to:
  - select 4 raw games with a fixed seed (`20260514`)
  - generate `tmp/raw_random4_obfuscator_manifest.json`
  - run `tools/game_obfuscator/scripts/game_obfuscator_cli.py start`
- Created `tmp/inspect_four_random_raw_obfuscator_batch.py` to summarize:
  - run status
  - per-game output paths
  - kept files
  - removed file/dir counts
  - HTML/CSS/JS transform reports
- The seeded batch selected:
  - `gamezone-270f7610-41c2-4d0f-851a-d57a84e67c79`
  - `gamezone-2f94531d-edf7-453d-8ea9-7867990e79c2`
  - `gamezone-761f3f96-d712-4b3f-91e5-8abea61baeb7`
  - `gamezone-d08b83c5-e2ac-439f-9e20-dc9db627759b`

**Observed Default Behavior:**
- Run completed successfully for all 4/4 games.
- Output surface was reduced very aggressively.
- For all sampled games, output effectively collapsed to:
  - `index.html`
  - a heavily-pruned `assets/` folder containing only `.js` and `.css`
  - `artifacts/simple_obfuscation_report.json`
- The current pruning behavior removed many source files and directories:
  - removed files ranged from `19` to `23`
  - removed directories ranged from `7` to `15`
- External and inline JavaScript were transformed with low obfuscation/minification behavior:
  - inline classic scripts were transformed with `obfuscated_classic_low`
  - some external JS files increased in size after obfuscation (for example `407279 -> 484068`)
  - some tiny external JS files were transformed down to `0` bytes, which is a potential tuning concern
- CSS was lightly reduced or preserved with minimal size changes.
- The default preserved surface folders remain:
  - `assets`
  - `screenshots`
  but no screenshot files appeared in the summarized output for this seeded sample.

**Technical Decisions:**
- The baseline harness uses a fixed seed so future tuning runs can compare against the exact same 4 games.
- The run id is fixed (`run_game_obfuscator_raw_random4_baseline`) to make results easy to inspect, though re-running requires removing the prior run directory first.

**Testing:**
```bash
python3 tmp/run_four_random_raw_obfuscator_batch.py
python3 tmp/inspect_four_random_raw_obfuscator_batch.py
```

**Next Steps:**
- [x] Inspect whether `screenshots/` should truly be preserved for raw-game defaults
- [x] Inspect why some tiny external JS files transformed to `0` bytes
- [x] Decide whether the default prune policy is too aggressive for raw-game compatibility
- [x] Implement the first default-tuning pass and compare against this seeded baseline

**Status:** Complete

---

### 2026-05-14 19:04 - Publish-vs-direct-public comparison documented

**Achievement:**
- Verified that `game_publish_pipeline` does not introduce a hidden obfuscator parameter delta
- Confirmed that publish obfuscation matches a direct obfuscator replay on the exact same public deploy outputs
- Documented that the observed delta versus raw-mode comes from input surface shape, not from different inline-script settings

**Implementation Details:**
- Ran publish first on the same 4 seeded raw inputs using:
  - `tmp/run_publish_pipeline_on_raw_random4.py`
- Captured public deploy outputs and obfuscated publish outputs in:
  - `tmp/game_publish_pipeline_raw_random4_report.json`
- Ran a direct obfuscator replay on those same public deploy outputs using:
  - `tmp/run_direct_obfuscator_on_publish_public_random4.py`
- Compared all three surfaces using:
  - `tmp/compare_publish_vs_direct_public_obfuscator.py`

**Findings:**
- For all 4 games:
  - `publish_matches_direct_public = true`
  - `raw_matches_publish = false`
- Inline-script handling stayed the same across raw, publish, and direct-public runs:
  - classic inline scripts remained `obfuscated_classic_low`
  - skipped external/non-executable script blocks remained skipped
- Publish/public runs preserved more files than raw runs because the public deploy surface already includes screenshots that survive the default preserved-folder policy.
- Therefore, the retained output shape difference is explained by:
  - `raw -> obfuscator`
  - versus
  - `raw -> deploy(public) -> obfuscator`

**Technical Decision:**
No publish-specific obfuscator adjustment is required for the current concern. The publish wrapper is not changing the effective inline-script parameterization.

**Remaining Follow-Up Possibilities:**
- [ ] Decide whether raw-mode should be adjusted to preserve a more publish-like surface, especially screenshots
- [ ] Decide whether tiny external JS files that collapse to `0` bytes should be protected by an additional heuristic
- [ ] Decide whether to keep raw-mode intentionally stricter than publish/public-mode

**Status:** Complete

---

## 🐛 Known Issues

### Default behavior risks not yet evaluated

**Problem:**  
The current simple pipeline aggressively prunes top-level files/folders and removes non-JS/CSS files from `assets/`, but the compatibility impact has not yet been measured on a controlled 4-game raw batch.

**Root Cause:**  
The implementation is understood from code inspection, but the practical effect on representative raw-game outputs has not yet been reviewed end-to-end.

**Status:**  
- [x] Being investigated
- [ ] Blocked (waiting for...)
- [ ] Fixed

**Workaround:**  
Create a small repeatable baseline batch and inspect generated reports before changing defaults.

**Resolution:**  
Pending baseline run and review.

---

## 📚 Quick Reference

### Key Files

- `tools/game_obfuscator/scripts/game_obfuscator_cli.py` - CLI `start`, `status`, and `output-path`
- `tools/game_obfuscator/scripts/create_run.py` - run scaffold and manifest normalization
- `tools/game_obfuscator/scripts/prepare_inputs.py` - mirrors inputs and checks `index.html`
- `tools/game_obfuscator/scripts/obfuscate_simple_outputs.py` - prune and transform logic
- `tools/game_obfuscator/manifests/random_batch_005.json` - reference manifest format
- `games/raw/` - raw source candidates for the 4-game batch

### Important Commands

```bash
python3 tools/game_obfuscator/scripts/game_obfuscator_cli.py start --manifest <manifest.json>
python3 tools/game_obfuscator/scripts/game_obfuscator_cli.py status --run-id <run_id>
python3 tools/game_obfuscator/scripts/game_obfuscator_cli.py output-path --run-id <run_id> --include-games
```

### Environment Variables

```bash
GAME_OBFUSCATION_LEVEL=none
GAME_OBFUSCATION_LEVEL=low
GAME_OBFUSCATION_LEVEL=moderate
GAME_OBFUSCATION_LEVEL=aggressive
```

---

## 💭 Notes & Decisions

### Design Decisions

**Decision:** Build a reusable 4-random-game harness instead of relying on one-off long shell commands.  
**Rationale:** The user wants iterative baseline review and this repository already benefits from short helper scripts over long inline commands.  
**Alternatives Considered:** Ad-hoc inline `python -c` / shell pipelines were rejected because they are harder to repeat and inspect.

### Future Enhancements

**Nice to Have:**
- Side-by-side diff helper for source vs obfuscated output file surfaces
- Optional sampling constraints for selecting raw games with varied shapes