# game_agent

A Python-centered toolchain for matching, remixing, and publishing browser games.
Given a prompt and a local game corpus, the CLI pipeline selects relevant games,
runs AI refactoring workflows, and optionally packages, obfuscates, and uploads the
results. A FastAPI service exposes background mock and refactoring jobs through
Celery and Redis.

## How the pieces fit

```text
                         game_generator
                  orchestration + state + events
                               |
Prompt ------------------------+
                               v
                      game_matcher_v2
                 select tags + rank catalog games
                               |
                    selected games + sources
                               v
                      game_refactoring <----- game_editorial
                 AI operator workflows        seeded batch manifests
                               |
                      final output folders
                               v
                    game_publish_pipeline
                               |
                               v
                          game_deploy
                        public game bundles
                               |
                               v
                       game_obfuscator
                      obfuscated game bundles
                               |
                 catalog / screenshots / reports
                               |
                       optional GCS sync

Supporting paths (invoked separately):
URL manifest -> game_downloader -> local mirrors -> source corpus preparation
Local files  -> game_uploader_r2 -> Cloudflare R2
```

`game_generator` currently launches the `creative_remix_v5` workflow. Matching uses
metadata from `games/published/public/app.json`; refactoring also needs resolvable
local source folders. The downloader has its own run/output layout, so its mirrors
must be prepared as source inputs rather than assumed to appear in `games/raw`.

Matching and refactoring run by default. `--publish` adds local packaging and
obfuscation; `--upload` requests GCS sync after publishing. Use both flags when you
want the full publish-and-upload path. R2 upload is a separate utility.

## Main tools

| Tool | Responsibility | Documentation |
| --- | --- | --- |
| `game_generator` | Prompt pipeline, durable serial batches, resume, state/events, dashboards | [README](tools/game_generator/README.md) |
| `game_matcher_v2` | Catalog artifacts, prompt-to-tags selection, deterministic ranking | [README](tools/game_matcher_v2/README.md) |
| `game_refactoring` | Named AI workflows, per-game operators, concurrency, status/results | [README](tools/game_refactoring/README.md) |
| `game_editorial` | Deterministic themed remix manifests and batch planning | [README](tools/game_editorial/README.md) |
| `game_deploy` | Package HTML, assets, screenshots, and metadata into public bundles | [README](tools/game_deploy/README.md) |
| `game_obfuscator` | Deterministic obfuscation/minification with a synchronous CLI | [README](tools/game_obfuscator/README.md) |
| `game_publish_pipeline` | Coordinate deploy, obfuscation, artifact refresh, reports, and sync | [README](tools/game_publish_pipeline/README.md) |
| `game_downloader` | Manifest-driven downloads, recursive asset mirroring, replay/QA | [README](tools/game_downloader/README.md) |
| `game_uploader_r2` | Stage local artifacts and upload them to Cloudflare R2 | [README](tools/game_uploader_r2/README.md) |
| `game_actor_mock` | Exercise async submission and persisted run state with mock work | [README](tools/game_actor_mock/README.md) |

Additional media integrations are available through [Giphy](tools/giphy_api/README.md)
and [KIE](tools/kie-api/README.md). See [tools/README.md](tools/README.md) for the
workspace inventory, including deprecated tools.

## Repository layout

```text
game_agent/
+-- app/                 FastAPI endpoints and Celery tasks/configuration
+-- tools/               Pipeline CLIs, integrations, and shared asset library
|   +-- library/         Shared assets and audio catalog scripts
|   +-- deprecated/      Previous matcher, remix editor, and crawler
+-- games/               Local raw games, templates, and published builds
+-- dashboard/           HTML annotation/review templates and launchers
+-- scripts/             Queue supervisors, metadata, and manifest utilities
+-- docs/                Maintenance guides, manifests, and task journals
+-- clineflow/           Persistent documentation workflow and journal template
+-- Dockerfile           Python 3.11, Chromium/Playwright, and Cline CLI runtime
+-- docker-compose.yml   API, Celery worker, Redis, and trigger services
```

Game data under `games/` is local-only and ignored by Git, apart from its README.
CLI tools also persist their own run artifacts, logs, events, and output folders.

## Run a prompt pipeline

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Match existing games and refactor up to two results.
python3 tools/game_generator/scripts/run_pipeline.py "a neon flappy bird game" --limit 2

# Also package and obfuscate the results locally.
python3 tools/game_generator/scripts/run_pipeline.py "a neon flappy bird game" --limit 2 --publish

# Also upload the published results to GCS.
python3 tools/game_generator/scripts/run_pipeline.py "a neon flappy bird game" --limit 2 --publish --upload
```

The root requirements install the API/worker and shared Python dependencies.
Individual tools may require additional Python or Node dependencies, AI CLI/model
configuration, Playwright browsers, and local catalogs/assets. Follow the component
READMEs and the [refactoring launch manual](GAME_REFACTORING_LAUNCH_MANUAL.md) before
starting a real generation run. GCS uploads require an authenticated `gcloud`
account; the generator checks authentication before expensive work begins.

Generation records live in `tools/game_generator/pipeline_runs/<run_id>/`, with
final copied outputs in `tools/game_generator/output/<run_id>/`. See the generator
README for dashboard, batch, observation, and resume commands.

## Run the API and worker

```text
HTTP client -> FastAPI :8000 -> Redis -> Celery worker
                   ^                         |
                   |                         +-> game_actor_mock
                   |                         |   mock jobs and events
                   |                         |
                   |                         +-> game_refactoring
                   |                             real workflow subprocess
                   +---- poll state/results -----+
```

From the repository root, with Docker Compose installed:

```bash
docker compose up --build api worker redis
```

The image includes Python dependencies, Chromium/Playwright, and the Cline CLI.
Compose mounts the repository at `/app`, including local game sources. Configure
AI provider credentials for real refactoring jobs; starting these services does not
run the full prompt-to-publish CLI pipeline.

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | API process health check |
| `POST /jobs` | Submit a mock game actor job |
| `GET /jobs/{run_id}` | Poll mock job state and results |
| `POST /jobs/game-refactoring` | Validate raw game IDs and enqueue a real named workflow |
| `GET /jobs/celery/{task_id}` | Poll Celery state and available workflow results |

Test mock submission:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/jobs \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"spider man","games":["game_a","game_b"]}'
```

Real refactoring requests use a workflow `id` and `raw_game_ids` that exist under
`/app/games/raw`. The request model and response contracts are in
[app/api.py](app/api.py). Interactive API documentation is available at
`http://localhost:8000/docs` while the service is running.

Celery uses `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`; Compose sets both to
Redis URLs. Configure the `CLINE_*`, `LITELLM_*`, or `OPENAI_*` variables required by
your chosen AI execution path. Credentials belong in the local environment.

For hosted API/worker services, use the root Dockerfile with separate commands:

```bash
uvicorn app.api:app --host 0.0.0.0 --port ${PORT:-8000}
celery -A app.tasks worker --loglevel=INFO
```

Both services need Redis connectivity and access to the required game sources and
workflow assets. Run state is filesystem-backed, so retain the relevant run data.

## Review published games

The **public dashboard** serves `games/published/public`; the **obfuscated dashboard**
serves `games/published/obfuscated`. These labels refer to build variants.

```bash
python3 tools/game_publish_pipeline/scripts/launch_annotator_entry.py --target public --open-browser
python3 tools/game_publish_pipeline/scripts/launch_annotator_entry.py --target obfuscated --open-browser
```

The launcher manages the local dashboard server on port `43177`, replaces the
previous server for the target, and opens the browser. Logs are written to
`.annotator_server.log` under the selected published root.

## Upload artifacts to R2

The standalone uploader uses `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, and either
`R2_ENDPOINT_URL` or `R2_ACCOUNT_ID`. `R2_BUCKET` supplies an optional default bucket.

```bash
python3 tools/game_uploader_r2/scripts/upload_game.py \
  --source games/published/my-game \
  --bucket my-r2-bucket \
  --prefix published/2026 \
  --dry-run
```

Remove `--dry-run` to upload. Existing destinations require `--force`. See the
[uploader README](tools/game_uploader_r2/README.md) for staging and path resolution.

## Development and project history

Read [AGENTS.md](AGENTS.md) for repository conventions. Every task is documented in
`docs/journals/` using the ClineFlow workflow. Component directories may contain
additional instructions. The [publishing maintenance guide](docs/game-publish-maintenance-workflow.md)
covers ongoing artifact and deployment operations.
