# Game Deploy Tool Journal

**Last Updated:** 2026-05-10  
**Feature Spec:** game_deploy  
**Backend Reference:** game_refactoring output → published public remix bundle

---

## 📊 Implementation Status Overview

### ✅ Phase 1: Tool scaffolding - **COMPLETE**
- [x] Mirror the standalone tool layout used by adjacent tools
- [x] Create package module and CLI entrypoint
- [x] Add top-level README

### ✅ Phase 2: Deploy bundle contract - **COMPLETE**
- [x] Lock published path shape to `games/published/public/<game_id>/remix-<uuid>/`
- [x] Lock public artifact count to:
  - `index.html`
  - `assets/`
  - `screenshots/`
  - `game-obfuscated-<uuid>.json`
- [x] Base the unified JSON contract on the provided public reference file

### ✅ Phase 3: Initial deploy implementation - **COMPLETE**
- [x] Resolve one or more source refactoring output directories
- [x] Infer `game_id`
- [x] Generate remix UUID
- [x] Copy runtime entrypoint
- [x] Copy filtered runtime assets
- [x] Copy screenshots
- [x] Build unified obfuscated metadata JSON
- [x] Support dry-run

### ✅ Phase 4: Basic validation - **COMPLETE**
- [x] Dry-run validate against the provided public reference source directory
- [x] Confirm expected deploy destination and obfuscated metadata path are produced

---

## 📝 Journal Entries

### 2026-05-10 07:06 - Initial `game_deploy` tool scaffold and contract implementation

**What Changed:**
Created a new standalone tool at `tools/game_deploy/` for converting `game_refactoring` outputs into deployable public remix bundles.

**Files Created:**
- `tools/game_deploy/README.md`
- `tools/game_deploy/game_deploy/__init__.py`
- `tools/game_deploy/game_deploy/deployer.py`
- `tools/game_deploy/scripts/deploy_games.py`

**Published Path Contract:**
Each deployed remix is written under:

```text
games/published/public/<game_id>/remix-<uuid>/
```

with exactly these public artifacts:

```text
index.html
assets/
screenshots/
game-obfuscated-<uuid>.json
```

**Unified Metadata Contract:**
The obfuscated metadata JSON is based on the user-provided public reference file and currently aggregates:

- `game_id`
- `aggregated_at`
- `recreation_prompt_markdown`
- `blueprint_markdown`
- `semantic_tags`
- `semantic_tags_source_mode`
- `identity`
- `identity_source_mode`
- `mechanics_classification`
- `mechanics_classification_source_mode`
- `screenshots_png`
- `screenshots_jpg`
- deploy provenance block

**Implementation Notes:**
- The deployer accepts either:
  - `--inputs <dir>...`
  - `--manifest <json-array>`
- It prefers an existing source JSON with `game_id` as the source-of-truth metadata shape.
- It falls back to markdown discovery for recreation prompt / blueprint fields.
- Assets are filtered into the public bundle instead of blindly copying all internal artifacts.
- Screenshot references in the obfuscated JSON are rewritten to relative public paths under `screenshots/`.

**Validation:**
Dry-run validation succeeded against the provided public reference source directory:

```json
{
  "results": [
    {
      "source": "/Users/hassan/repos/game_agent/games/published/public/gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06",
      "game_id": "gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06",
      "remix_uuid": "10b00e2e-9c49-448e-827e-629db4f0c3d5",
      "deploy_dir": "/Users/hassan/repos/game_agent/games/published/public/gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06/remix-10b00e2e-9c49-448e-827e-629db4f0c3d5",
      "metadata_path": "/Users/hassan/repos/game_agent/games/published/public/gamezone-0a01fa77-8b8b-4c02-93db-07cf4e05ee06/remix-10b00e2e-9c49-448e-827e-629db4f0c3d5/game-obfuscated-10b00e2e-9c49-448e-827e-629db4f0c3d5.json"
    }
  ]
}
```

**Technical Decisions:**
- Kept the first version intentionally narrow:
  - one deployer module
  - one CLI
  - no uploader coupling
- Treated deploy as a normalization step between refactoring and upload.
- Used a public-reference-first strategy for the unified metadata contract instead of inventing a new schema from scratch.

**Known Follow-Up:**
- Harden source discovery for real `game_refactoring` output trees, not only public-reference-like directories.
- Add more deterministic extraction rules for semantic/mechanics/prompt fields from refactor artifacts.
- Potentially add deploy manifest output for batch downstream upload automation.

**Status:** Complete

---

## 📚 Quick Reference

### CLI
```bash
python3 tools/game_deploy/scripts/deploy_games.py --inputs /path/to/refactor/output/gamezone-abc...
```

### Dry-run
```bash
python3 tools/game_deploy/scripts/deploy_games.py --inputs /path/to/refactor/output/gamezone-abc... --dry-run
```

### Manifest mode
```bash
python3 tools/game_deploy/scripts/deploy_games.py --manifest deploy_inputs.json
```

### Key Files
- `tools/game_deploy/game_deploy/deployer.py`
- `tools/game_deploy/scripts/deploy_games.py`
- `tools/game_deploy/README.md`

---

## 🎯 Success Criteria

- [x] New standalone deploy tool exists
- [x] Published remix path contract is implemented
- [x] Public artifact count is constrained to the 4 agreed artifacts
- [x] Unified obfuscated metadata JSON follows the provided reference shape
- [x] Dry-run validates against the provided reference source directory

---

*This journal documents the first implementation pass of the missing `game_deploy` tool that converts `game_refactoring` outputs into normalized public remix bundles suitable for later upload/publishing workflows.*