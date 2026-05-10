# Game Refactoring API Handoff

**Last Updated:** 2026-05-10  
**Feature Spec:** N/A  
**Scope:** Local Docker + FastAPI + Celery orchestration for `game_refactoring`

---

## Current status

The local async API orchestration layer has been partially implemented and validated.

### Working today
- FastAPI service exists at `app/api.py`
- Celery worker exists and loads from `app/tasks.py`
- Docker Compose local stack includes:
  - `redis`
  - `worker`
  - `api`
  - `trigger`
- Mock submit/poll flow works end-to-end
- Real `game_refactoring` API path accepts a workflow id and resolves `raw_game_ids` against `games/raw/`
- Internal workflow manifest generation is server-side
- Public-facing polling returns:
  - `taskId`
  - `status`
  - `comment`
  - `result`
  - `run_state`
  - per-game `results`

### Important validated behavior
A real local API submission using:
- `workflow_id = creative_remix_v3`
- `raw_game_id = gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0`
- prompt `"harry potter"`

was submitted and polled successfully.

The poller now distinguishes:
- Celery task finished
- workflow still in progress
- workflow actually terminal via:
  - `current_phase == "parallel_batch_finished"`

This was the key refinement.

---

## Main blocker

### LiteLLM / company VPN dependency
The main blocker is now **not** the orchestration layer.

The current blocker is:

- the LiteLLM / model runtime only works when connected to the company VPN
- local Docker containers currently do not have a proven working path to that VPN-backed model endpoint
- in previous local tests, model-related env vars were missing or blank in Compose
- even when the orchestration path works, a true production-style full transform run still depends on working downstream model access

### Practical implication
The API/Celery/filesystem architecture is good enough to continue, but **full real successful production runs depend on network and secrets availability**, specifically the VPN-gated LiteLLM environment.

---

## Files changed in this phase

### Core app
- `app/api.py`
- `app/tasks.py`
- `app/celery_app.py` (pre-existing runtime used as-is)

### Local orchestration
- `docker-compose.yml`
- `requirements.txt`

### Test artifact
- `scripts/test_game_refactoring_api.py`

### Supporting tool
- `tools/game_actor_mock/...`

### Journals
- `docs/journals/game-actor-mock.md`
- `docs/journals/game-refactoring-api-handoff.md`

---

## Public API design settled so far

### Mock endpoint
- `POST /jobs`
- `GET /jobs/{run_id}`

### Real game_refactoring endpoint
- `POST /jobs/game-refactoring`

Public request should use:
- `id` = workflow id
- `raw_game_ids` = folder ids from `games/raw/`
- optional prompt override
- optional advanced runtime knobs

### Public status endpoint
- `GET /jobs/celery/{task_id}`

Public response shape should continue to favor:
- `taskId`
- `status` = `idle | wip | failed | completed`
- `comment`
- `results: [{game_id, status}]`

The design intent is to keep internal paths/manifest generation private.

---

## Source of truth

### Game input source
`games/raw/` is the source of truth for public API game selection.

The caller should not pass raw filesystem paths.

Instead:
- client passes raw folder ids
- server validates those ids
- server constructs internal manifest entries with:
  - `game_id`
  - `display_name`
  - `source_path`

### Task identity
Public `taskId` should be the Celery task id.

This is unique enough and simplifies the public contract.

---

## Completion semantics

### Important distinction
Do **not** treat Celery `SUCCESS` alone as full workflow completion.

The stronger workflow-completion signal is:
- `run_state.current_phase == "parallel_batch_finished"`

### Current mapping approach
- `idle`
  - waiting for pickup / pending
- `wip`
  - worker started or workflow phase still progressing
- `failed`
  - terminal workflow failure, e.g. `transform_failed`
- `completed`
  - terminal workflow success, e.g. `parallel_batch_finished` + success state

### Per-game result summary
Preferred public output:
```json
{
  "results": [
    {"game_id": "gamezone-...", "status": "completed"},
    {"game_id": "gamezone-...", "status": "failed"}
  ]
}
```

This is preferred over exposing raw notes as the main public result surface.

---

## Local Docker status

### Verified
The stack was brought up successfully and the mock API plumbing was verified.

### Compose services
- `redis`
- `worker`
- `api`
- `trigger`

### Important compose adjustment
The repo is mounted into:
- `worker`
- `api`
- `trigger`

This was necessary so the API-created artifacts were visible to the worker.

---

## Secrets / env var policy

### Safe to bake as defaults
- `LOG_LEVEL`
- `PYTHONUNBUFFERED`
- `PLAYWRIGHT_HEADLESS`
- `PLAYWRIGHT_BROWSER`
- `CLINE_CHECK_COMMAND`

### Must remain runtime-provided
- `OPENAI_API_KEY`
- `LITELLM_API_KEY`
- `LITELLM_BASE_URL`
- `CLINE_API_KEY`
- `CLINE_BASE_URL`
- `CLINE_MODEL`

### Best practice
Use:
- local `.env` or exported shell vars for Docker Compose
- Railway environment tab for deployed services
- do not hardcode secrets into Dockerfile

---

## Known issues / caveats

1. **Redis startup timing during restarts**
   - API can hit transient Redis resolution/connectivity issues right after restart
   - mitigations:
     - healthchecks
     - startup wait
     - retry on enqueue

2. **Current advanced API implementation is still rough**
   - task id generation / manifest wiring was made to work, but could be cleaned up further
   - richer run-state polling can be improved further

3. **True full success still blocked by VPN-gated model backend**
   - orchestration is mostly there
   - runtime network access is the gating issue

---

## Recommended next steps

### Highest priority
1. solve VPN/LiteLLM access for the Docker runtime
2. confirm env vars are actually injected into the containers
3. run a true non-dry-run workflow through the API
4. verify real output artifacts, not just orchestration completion

### Next engineering improvements
1. add Redis healthchecks and service_healthy dependency conditions in compose
2. refine `app/api.py` status response contract
3. tighten task id / run id creation semantics
4. make workflow polling run-state-first rather than Celery-first when terminal
5. possibly add a dedicated `/jobs/game-refactoring/{taskId}` endpoint

---

## Useful commands

### Start local stack
```bash
docker compose up --build -d redis worker api
```

### Health check
```bash
curl http://localhost:8000/health
```

### Mock submit
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"prompt":"spider man","games":["game_a","game_b"]}'
```

### Real submit via reusable script
```bash
python3 scripts/test_game_refactoring_api.py \
  --raw-game-id gamezone-0f3dc736-8159-48cf-93d0-bd78a54b8cd0 \
  --prompt "harry potter"
```

### Poll task
```bash
curl http://localhost:8000/jobs/celery/<task_id>
```

---

## Summary

The orchestration problem is mostly solved.

The main blocker is now **external runtime reachability and credentials for LiteLLM inside the effective execution environment**, especially if the company VPN is required.

The next session should focus on getting the model backend reachable from the runtime, then re-running a true workflow and validating actual output completion.