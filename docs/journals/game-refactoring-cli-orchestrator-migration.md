
**Last Updated:** 2026-05-10  
**Scope:** Migrate from API/Celery queue orchestration to direct CLI sequential orchestration for `game_refactoring`

---

## Goal

Replace the current API/Celery-based queue launcher with a simpler direct CLI orchestrator that:

- executes `tools/game_refactoring/scripts/game_workflow.py` directly
- processes one manifest/prompt combination at a time
- persists a durable ledger
- resumes safely after interruption
- retries each batch a limited number of times
- optionally runs under a thin external supervisor
- logs verbosely to both terminal and logfile

---

## Why migrate

### Current pain points with API/Celery path
- too many moving parts:
  - FastAPI
  - Celery
  - Redis
  - Docker runtime coordination
- status interpretation is more complex than necessary
- queue completion depends on polling wrapper semantics
- API task success/failure is one more abstraction layer over the real CLI execution
- troubleshooting becomes harder because launcher state is separated from the actual transform subprocess behavior

### Benefits of direct CLI orchestration
- simpler mental model
- fewer components to keep alive
- direct process exit code is the source of truth
- easier retry semantics
- easier resumability
- easier shared terminal/file logging
- easier to run externally from one shell command

---

## Migration target architecture

### Old model
1. submit API request
2. Celery task enqueues workflow
3. API poller checks `/jobs/celery/{task_id}`
4. queue wrapper interprets `current_phase == parallel_batch_finished`

### New model
1. direct queue runner reads a JSON config
2. launches `game_workflow.py` directly for one job
3. captures stdout/stderr and exit code
4. records status in a ledger
5. retries if needed
6. advances to next job only after success
7. optional thin supervisor restarts the queue runner process itself if it dies

---

## Proposed new files

### New primary runner
- `scripts/run_game_refactoring_cli_queue.py`

### Optional thin supervisor
- `scripts/run_game_refactoring_cli_queue_supervisor.py`

### Example config
- `tmp/game_refactoring_cli_queue_test_config.json`

### Durable ledger
- `tmp/game_refactoring_cli_queue_ledger.json`

### Optional log file
- `tmp/game_refactoring_cli_queue.log`

---

## Execution contract

Each queue job should represent one direct CLI batch launch.

### Per-job config shape
```json
{
  "jobs": [
    {
      "name": "harry-potter-single",
      "workflow_id": "creative_remix_v3",
      "games_manifest_source": "tmp/some_manifest.json",
      "remix_prompt": "harry potter",
      "model": "gpt-5.5",
      "max_concurrency": 2,
      "agent_timeout": 3600,
      "poll_seconds": 5,
      "stale_heartbeat_seconds": 900,
      "source_mode": "copy",
      "pipeline": "v2"
    }
  ]
}
```

### Required fields
- `workflow_id` or `id`
- `games_manifest_source`
- `remix_prompt`

### Optional fields
- `model`
- `max_concurrency`
- `agent_timeout`
- `poll_seconds`
- `stale_heartbeat_seconds`
- `source_mode`
- `pipeline`
- `playwright_port_base`
- `playwright_port_pool_size`
- `playwright_port_lease_ttl_seconds`
- `dry_run_operators`
- `dry_run_spec_adaptor`

---

## Success / failure semantics

### Success
A job is successful if the direct CLI process exits with code `0`.

### Failure
A job is failed if the direct CLI process exits non-zero.

### Retry policy
Default:
- total attempts per batch job: `3`
- meaning:
  - 1 initial attempt
  - 2 retries

### Resume behavior
If the queue process is interrupted:
- read ledger
- detect current job state
- if current job is already completed, skip
- if current job is in-progress, either:
  - re-run from scratch for direct CLI mode
  - or treat previous attempt as interrupted and retry cleanly
- continue from the first non-completed job

For the direct CLI mode, restart-from-scratch per interrupted batch is acceptable and simpler than reconstructing live subprocess state.

---

## Logging requirements

The direct CLI queue runner should be extremely verbose.

### Terminal logging
Print:
- queue start
- config path
- ledger path
- current job index
- full launch command
- attempt number
- process start time
- process end time
- exit code
- retry decisions
- ledger persistence
- queue completion summary

### File logging
Support shared terminal + logfile with external `tee`:
```bash
python3 scripts/run_game_refactoring_cli_queue_supervisor.py tmp/game_refactoring_cli_queue_test_config.json 2>&1 | tee tmp/game_refactoring_cli_queue.log
```

---

## Migration steps

### Phase 1 — create direct CLI runner
Implement:
- `scripts/run_game_refactoring_cli_queue.py`

Behavior:
- read config
- maintain ledger
- launch one direct CLI batch at a time
- persist attempt state
- retry on non-zero exit
- proceed sequentially

### Phase 2 — create thin supervisor
Implement:
- `scripts/run_game_refactoring_cli_queue_supervisor.py`

Behavior:
- repeatedly invoke CLI queue runner
- if queue runner process dies, restart it
- stop only when:
  - ledger says all jobs completed
  - or one job exhausted retries

### Phase 3 — create real single-test config
Create:
- `tmp/game_refactoring_cli_queue_test_config.json`

Use:
- one real manifest/prompt combination
- minimal surface area for validation

### Phase 4 — validate single test
Validate:
- direct command launches successfully
- ledger persists
- retries behave correctly
- resume works after manual interruption
- logs are readable in terminal and file

### Phase 5 — expand to 4-prompt production queue
Create config containing the real consolidated retry manifests:
- rick_morty
- brainrot_momsday
- flappy_bird
- harry_potter

---

## Decommission plan for old API queue layer

These files can remain temporarily but should stop being the recommended path:
- `scripts/run_game_refactoring_queue.py`
- `scripts/run_game_refactoring_queue_supervisor.py`
- `scripts/test_game_refactoring_api.py`

### Recommendation
- keep them for reference during transition
- document them as legacy
- move all operational usage to direct CLI queue runner once validated

---

## Risks / caveats

1. **Interrupted direct subprocesses**
   - we cannot truly resume an existing OS process
   - mitigation: retry that batch from scratch using ledger state

2. **Long-running batches**
   - use large timeout defaults
   - current expectation:
     - poll/log heartbeat every 60s
     - timeout per batch default can remain 24h or larger if needed

3. **Large output logs**
   - expected and acceptable
   - use `tee` and log rotation externally if needed

4. **Partial outputs from failed attempts**
   - acceptable as historical artifacts
   - queue success should still be based on final successful exit code for that job

---

## Recommended final operator command

Single test:
```bash
python3 scripts/run_game_refactoring_cli_queue_supervisor.py tmp/game_refactoring_cli_queue_test_config.json 2>&1 | tee tmp/game_refactoring_cli_queue.log
```

---

## Summary

The migration should move orchestration from:
- API/Celery task wrappers
to:
- direct CLI sequential execution with durable ledger and thin supervisor

This will reduce complexity, improve debuggability, and better match the real operational model of `game_refactoring`.