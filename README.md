# Docker + Celery + Playwright + Cline proof

This project is a minimal end-to-end proof that a Docker image can run:

- Python Celery worker
- Playwright with Chromium
- Cline CLI

The worker executes two mocked tools sequentially with a delay:

1. `tools/tool_cline.py` proves the Cline CLI command runs inside the container.
2. `tools/tool_playwright.py` proves Playwright can launch a browser inside the container.

## Project structure

- `app/celery_app.py` - Celery configuration
- `app/tasks.py` - mock workflow task
- `app/trigger.py` - enqueues the task
- `tools/tool_cline.py` - Cline runtime proof
- `tools/tool_playwright.py` - Playwright runtime proof
- `Dockerfile` - container image
- `docker-compose.yml` - local Redis + worker + trigger

## Required environment variables

### Celery
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`

### Optional app settings
- `CELERY_TASK_DELAY_SECONDS=2`
- `LOG_LEVEL=INFO`
- `PYTHONUNBUFFERED=1`

### Playwright
- `PLAYWRIGHT_HEADLESS=true`
- `PLAYWRIGHT_BROWSER=chromium`

### Cline / LiteLLM
Use the exact values required by your Cline CLI setup.

Recommended variables to set in Railway:
- `CLINE_MODEL`
- `CLINE_BASE_URL`
- `CLINE_API_KEY`

If your LiteLLM/OpenAI flow needs them directly, also set:
- `LITELLM_BASE_URL`
- `LITELLM_API_KEY`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

For the basic runtime proof in this repository, the default command is:
- `CLINE_CHECK_COMMAND="clite --help"`

You can change that to a model-backed command once your CLI configuration is ready.

## Local run

Build and start the worker and Redis:

```bash
docker compose up --build worker redis
```

In another terminal, enqueue the test task:

```bash
docker compose run --rm trigger
```

View worker logs:

```bash
docker compose logs -f worker
```

Expected outcome:
- Celery worker starts
- Cline tool returns success output
- Playwright launches Chromium and returns title/body text
- task completes successfully

## Railway deployment

Recommended setup:
- create a GitHub repo for this project
- create a Railway project
- add a Redis service
- add a worker service from this repo
- use the `Dockerfile` for builds
- start command:

```bash
celery -A app.tasks worker --loglevel=INFO
```

Set Railway environment variables:
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `CELERY_TASK_DELAY_SECONDS`
- `LOG_LEVEL`
- `PLAYWRIGHT_HEADLESS`
- `PLAYWRIGHT_BROWSER`
- `CLINE_CHECK_COMMAND`

And for LiteLLM/Cline as needed:
- `CLINE_MODEL`
- `CLINE_BASE_URL`
- `CLINE_API_KEY`
- `LITELLM_BASE_URL`
- `LITELLM_API_KEY`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

## R2 game upload utility

This repository now includes a root-level uploader utility for copying a local game directory or file into a staging area and pushing it to a specific Cloudflare R2 destination.

### Required environment variables

- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`

And one of:
- `R2_ENDPOINT_URL`
- `R2_ACCOUNT_ID`

Optional defaults:
- `R2_BUCKET`

### Install dependency

```bash
pip install -r requirements.txt
```

### Example usage

Dry-run a game upload without copying or uploading files:

```bash
python scripts/upload_game_to_r2.py \
  --source games/published/my-game \
  --bucket my-r2-bucket \
  --prefix published/2026 \
  --dry-run
```

Upload a game directory to a specific destination folder in R2:

```bash
python scripts/upload_game_to_r2.py \
  --source games/published/my-game \
  --bucket my-r2-bucket \
  --prefix published/2026 \
  --destination-name harry-potter-flappy
```

If the destination already exists, require explicit overwrite permission:

```bash
python scripts/upload_game_to_r2.py \
  --source games/published/my-game \
  --bucket my-r2-bucket \
  --prefix published/2026 \
  --destination-name harry-potter-flappy \
  --force
```

Notes:
- Relative `--source` paths resolve from the repository root and then from `games/`.
- Directories are copied into a temporary staging area before upload.
- The destination object root is formed as `{prefix}/{destination-name}`.
- Content types are inferred automatically when possible.

## Notes

- This repository is designed to prove runtime readiness, not full product behavior.
- `tool_cline.py` currently validates that the Cline CLI executable (`clite`) works inside the container.
- `tool_playwright.py` validates that Playwright can launch a browser inside the container.
- Once your exact Cline model invocation is finalized, `CLINE_CHECK_COMMAND` can be changed to a deeper proof command.
