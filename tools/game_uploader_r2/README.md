y# Game Uploader R2

A standalone game artifact uploader for copying local game files into a staging area and pushing them to a specific Cloudflare R2 destination.

## Scope

This tool is focused on four capabilities only:

- source path resolution from repository-relative or `games/` paths
- local staging copy before upload
- Cloudflare R2 upload to a bucket/prefix/destination name
- safe operational controls such as dry-run and overwrite gating

It intentionally excludes any game generation, refactoring, crawling, or dashboard/report runtime.

## Current public workflow

```bash
python3 scripts/upload_game.py \
  --source games/published/my-game \
  --bucket my-r2-bucket \
  --prefix published/2026 \
  --destination-name my-game
```

Dry-run without copying or uploading:

```bash
python3 scripts/upload_game.py \
  --source games/published/my-game \
  --bucket my-r2-bucket \
  --prefix published/2026 \
  --dry-run
```

## Required environment variables

- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`

And one of:

- `R2_ENDPOINT_URL`
- `R2_ACCOUNT_ID`

Optional defaults:

- `R2_BUCKET`

## Directory layout

```text
game_uploader_r2/
  README.md
  VERSION
  docs/
    journals/
  game_uploader_r2/
    __init__.py
    uploader.py
  scripts/
    upload_game.py
```

## CLI behavior

The uploader:

1. resolves the source path from either the repository root or `games/`
2. computes the destination object root as `{prefix}/{destination-name}`
3. copies the source into a temporary staging area
4. uploads files to Cloudflare R2 using its S3-compatible API
5. refuses to upload over an existing destination unless `--force` is set

## Key arguments

- `--source` - source directory or file to upload
- `--bucket` - R2 bucket name, defaults to `R2_BUCKET`
- `--prefix` - destination prefix inside the bucket
- `--destination-name` - override for the uploaded root folder/file name
- `--dry-run` - print the upload plan only
- `--force` - allow uploads when the destination already exists

## Dependency

The root repository dependency set now includes `boto3` for S3-compatible uploads:

```bash
pip install -r requirements.txt
```

## Notes

- Relative `--source` values resolve from the repository root and then from `games/`.
- Directories are staged into a temp copy before upload so the source tree remains untouched.
- The uploader currently uses the repository root dependency set instead of a separate package-local `pyproject.toml`.