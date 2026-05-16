

ENTRY = '''

### 2026-05-16 03:21 - Add optional post-artifact GCG sync stage to publish pipeline

**What Changed:**
Updated `tools/game_publish_pipeline/game_publish_pipeline/pipeline.py` to support an optional post-artifact GCS sync step controlled by new CLI flags.

**New CLI Flags:**
- `--gcg-sync`
- `--gcg-sync-project` (default: `jabali-prod`)
- `--gcg-sync-dry-run`

**Pipeline Integration:**
- Added `SYNC_TO_GCS_SCRIPT` constant pointing to:
  - `tools/game_publish_pipeline/scripts/sync_to_gcs.py`
- Added a conditional sync stage that runs after refresh/validation stages when `--gcg-sync` is passed.
- Wired command shape to:
  - `--target both`
  - `--mode per-item`
  - `--project <gcg-sync-project>`
  - `--public-root <published_public_root>`
  - `--obfuscated-root <published_obfuscated_root>`
  - optional `--dry-run` when `--gcg-sync-dry-run` is set.

**Verification:**
- Ran `python3 tools/game_publish_pipeline/scripts/publish_games.py --help` and confirmed new flags are exposed.
- Ran dry-run with explicit published roots and sync flags:
  - `--published-public-root games/published/public`
  - `--published-obfuscated-root games/published/obfuscated`
  - `--gcg-sync --gcg-sync-dry-run --dry-run`
- Confirmed dry-run payload includes:
  - `gcg_sync.enabled = true`
  - `gcg_sync.project = "jabali-prod"`
  - `gcg_sync.dry_run = true`

**Notes:**
- This keeps sync opt-in and preserves existing behavior when `--gcg-sync` is omitted.
- The selected roots are now explicitly controlled by publish pipeline arguments, matching your requested command shape when targeting `public/obfuscated`.

**Status:** Complete
'''


def main() -> None:
    path = Path("docs/journals/game-publish-pipeline.md")
    content = path.read_text(encoding="utf-8")
    heading = "### 2026-05-16 03:21 - Add optional post-artifact GCG sync stage to publish pipeline"
    if heading in content:
        print("journal entry already present")
        return
    path.write_text(content + ENTRY, encoding="utf-8")
    print("journal updated")


if __name__ == "__main__":
    main()