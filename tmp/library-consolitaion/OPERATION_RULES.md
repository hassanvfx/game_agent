# Library Consolidation Operation Rules

## Audit workflow rules

1. **Do not use long inline shell commands** for this audit workflow.
2. **Create a dedicated tmp script** for each non-trivial inspection or comparison.
3. **Run scripts with short commands only**, for example:
   - `python3 tmp/library-consolitaion/audit_published_game_audio_refs.py`
   - `python3 tmp/library-consolitaion/summarize_published_game_audio_ref_audit.py`
4. **Write artifacts back into `tmp/library-consolitaion/`** so the work is resumable.
5. **Separate runtime references from artifact-report noise** before drawing conclusions.
6. **Prefer JSON outputs** for machine-readable audit artifacts, then add small summary scripts for human-readable reports.

## Current audit scope

- Published source: `games/published/obfuscated/gamezone*`
- Library source of comparison: `tools/library/assets/audios/`
- Main output artifact: `tmp/library-consolitaion/published_game_audio_ref_audit.json`
