# Kill-All Operation

## Purpose

This document defines the operator-facing cancellation workflow for terminating active remix-related CLI and worker processes inside `game_remix_editor`.

The goal is to provide a tool-native replacement for ad hoc shell snippets when a run needs to be stopped quickly.

## Command

### Dry-run preview

```bash
python3 scripts/creative_refactor_cli.py kill-all --dry-run
```

Lists matching processes without sending any signal.

### Soft kill

```bash
python3 scripts/creative_refactor_cli.py kill-all
```

Sends `SIGTERM` to known remix-related processes.

### Force kill

```bash
python3 scripts/creative_refactor_cli.py kill-all --force
```

Sends `SIGKILL` to known remix-related processes.

### Include generic cline processes

```bash
python3 scripts/creative_refactor_cli.py kill-all --include-cline
```

This expands the match set to include generic `cline` processes in addition to known remixer script names.

Use this with care.

## JSON mode

Structured output is available with `--json`:

```bash
python3 scripts/creative_refactor_cli.py --json kill-all --dry-run
python3 scripts/creative_refactor_cli.py --json kill-all
python3 scripts/creative_refactor_cli.py --json kill-all --force
```

## Default process match rules

By default, `kill-all` matches these script patterns:

- `creative_refactor_cli.py`
- `run_parallel_batch.py`
- `run_single_game.py`
- `debug_creative_refactor.py`

Optional broader pattern:

- `cline`

The CLI excludes its own current pid from termination so the command can report results safely.

## Output behavior

### Human-readable mode

The command prints:

- whether `--dry-run` is active
- whether `--force` is active
- whether `--include-cline` is active
- matched process count
- matched processes
- signal used
- terminated pids
- survivor count
- survivor processes

### JSON mode

The JSON payload includes fields such as:

- `mode`
- `include_cline`
- `dry_run`
- `force`
- `matched_processes`
- `matched_count`
- `signal`
- `terminated_pids`
- `errors`
- `survivors`
- `survivor_count`
- `success`

## Recommended operator sequence

### 1. Preview first

```bash
python3 scripts/creative_refactor_cli.py kill-all --dry-run
```

### 2. Attempt graceful shutdown

```bash
python3 scripts/creative_refactor_cli.py kill-all
```

### 3. Escalate if needed

```bash
python3 scripts/creative_refactor_cli.py kill-all --force
```

## When to use `--include-cline`

Use `--include-cline` only when you have strong reason to believe remixer-owned work is still alive under generic `cline` process names.

Example:

```bash
python3 scripts/creative_refactor_cli.py kill-all --force --include-cline
```

Because this can target broader `cline` activity, it should not be your first step unless necessary.

## Operational notes

- `kill-all` is process-based, not run-id-based.
- It is intended for emergency or broad operator cancellation.
- If a run registry or dashboard needs reconciliation after cancellation, use the normal run status/result workflows after the processes are stopped.

## Related files

- `scripts/creative_refactor_cli.py`
- `scripts/process_kill_utils.py`
- `docs/journals/kill-all-operation.md`