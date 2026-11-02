# Game Actor Mock

## Overview and pipeline position

This tool exercises asynchronous job submission and durable run-state contracts
with simulated game work. It backs the root API's `POST /jobs` endpoint and can also
be submitted through its own CLI.

```text
mock_actor_cli submit / POST /jobs
                  |
          initialize run files
                  |
          Redis -> Celery worker
                       |
              simulated game phases
                       |
           run state + events + result
                       |
           CLI status / GET /jobs/<run_id>
```

Real transformations use the separate `POST /jobs/game-refactoring` endpoint and
`game_refactoring` tool. The mock is useful for checking queue connectivity and
filesystem persistence without starting an AI transformation.

All commands below run from `tools/game_actor_mock/`, with the root API/worker
Python environment and Redis available. From the repository root, prefix script
paths with `tools/game_actor_mock/`.

See the [API source](../../app/api.py) and [workspace overview](../../README.md).

A standalone mock async actor tool that mirrors `game_refactoring`-style run persistence while using Redis + Celery for queueing and execution.

## Scope

This tool is focused on five capabilities only:

- submit a mock async run
- persist per-run filesystem state in a `game_refactoring`-like layout
- enqueue execution through Celery
- poll run status by run id
- produce result and event artifacts for inspection

It intentionally excludes real `game_refactoring` execution for now.

## Public workflow

Submit a mock run:

```bash
python3 scripts/mock_actor_cli.py submit \
  --prompt "spider man" \
  --game game_a \
  --game game_b
```

Poll status:

```bash
python3 scripts/mock_actor_cli.py status --run-id <run_id>
```

## Persistence model

Each run gets its own directory under `runs/` with a layout intentionally similar to `game_refactoring`:

```text
runs/<run_id>/
  request.json
  run_state.json
  result.json
  events.jsonl
  input/
  output/
  dashboard/
  games/
    <game_id>/
      game_state.json
```

## Local runtime expectation

- Redis provides broker/backend
- Celery worker picks up queued jobs
- filesystem stores durable run state and result metadata

## Notes

- The submission/polling/run-state shape is intended to be kept stable so the mock execution body can later be replaced by real `game_refactoring` invocation with minimal orchestration changes.