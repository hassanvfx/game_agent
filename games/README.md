# Games Directory

This directory is intentionally kept mostly empty in the repository.

## Purpose

`games/` is used as local storage for game-related working data such as:
- raw imported games
- published/exported game builds
- local template sets
- generated or mirrored game artifacts

## Repository policy

The contents of this directory are ignored by git so large or machine-local game assets do not get committed.

Only this `README.md` is tracked to document the intended use of the folder.

## Expected local subdirectories

Common local-only folders include:
- `raw/`
- `published/`
- `top100_vatsal/`

These may be recreated locally as needed, but their contents should remain untracked.