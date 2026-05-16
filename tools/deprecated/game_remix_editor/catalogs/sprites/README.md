# Sprites Run Workspace

This directory stores generated sprite/background runs derived from `../sprites.json`.

## Layout

- `runs/<run_id>/manifest.json` — flat list of all jobs for a run
- `runs/<run_id>/manifest.sample.json` — optional one-job sample subset
- `runs/<run_id>/run.json` — run metadata
- `runs/<run_id>/assets/...` — generated files, preserving the remote URL pathname
- `runs/<run_id>/.jobs/...` — raw saved KIE CLI job files
- `runs/<run_id>/.state/...` — durable orchestration state
- `runs/<run_id>/logs/` — run logs
- `runs/<run_id>/fixtures/` — local fixture files for development/testing

## Path mapping

A remote URL like:

`https://gamezone-virid.vercel.app/assets/images/sprites/runner/player_runner.png`

maps to:

`runs/<run_id>/assets/images/sprites/runner/player_runner.png`

## Intended workflow

1. Build a flat manifest from `../sprites.json`.
2. Start with one selected sample job.
3. Submit jobs through the KIE CLI with `--save-job`.
4. Resume/poll using saved job files.
5. Persist output, state, and logs inside the run folder.