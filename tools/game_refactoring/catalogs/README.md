# Catalogs

This directory is the canonical root for catalog files used by the operator pipeline redesign.

## Purpose

These catalogs are intended to become the stable source that gets copied into each operator workspace as:

```text
workspace/catalogs/
```

The goal is to give operator stages a deterministic, workspace-local contract for approved media selection and reusable operator skill references.

## Current Files

- `audios.json` - Bootstrapped from the existing audio catalog and preserved as the first real catalog
- `gifs.json` - Placeholder scaffold for approved GIF/media mappings
- `sprites.json` - Placeholder scaffold for approved sprite/media mappings
- `fonts.json` - Approved font catalog
- `skills/` - Optional read-only operator skill catalog subtree copied into attempt workspaces when present

## Intended Usage

The redesigned pipeline will use these files for the media-mapper pass to:
- replace disallowed external media URLs
- choose approved audio/GIF/sprite assets
- reason from semantic `usage` descriptions instead of guessing filenames
- keep media references aligned with allowed domains and local asset policy

## Notes

- `gifs.json` and `sprites.json` are scaffolds and should be filled in later with approved assets
- `audios.json` is the first migrated catalog and may be normalized further in later milestones
- these files are meant to be copied into operator workspaces before agent execution
- `skills/` is copied as a directory catalog; operators should treat all files under `workspace/catalogs/` as read-only reference input