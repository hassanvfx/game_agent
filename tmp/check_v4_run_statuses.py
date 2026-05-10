#!/usr/bin/env python3
import json
from pathlib import Path

RUNS = [
    "run_v4_brainrot_momsday_vatsal107_model55_c1_20260509T084144Z",
    "run_v4_flappy_bird_vatsal107_model55_c1_20260509T085122Z",
    "run_v4_harry_potter_vatsal107_model55_c1_20260509T083751Z",
    "run_v4_rick_morty_vatsal107_model55_c1_20260509T083929Z",
    "run_v4_trump_xmusk_vatsal107_model55_c1_20260509T082454Z",
]

BASE = Path("/Volumes/HDD2026/output")


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"_parse_error": str(exc)}


def summarize_items(items):
    summary = {
        "total": len(items),
        "done_like": 0,
        "failed_like": 0,
        "other_status_like": 0,
    }
    for item in items:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or item.get("state") or "").lower()
        if any(token in status for token in ("fail", "error")):
            summary["failed_like"] += 1
        elif any(token in status for token in ("done", "success", "complete")):
            summary["done_like"] += 1
        elif status:
            summary["other_status_like"] += 1
    return summary


def print_tail(label: str, path: Path, lines: int = 20):
    if not path.exists():
        return
    try:
        text = path.read_text(errors="replace").splitlines()
    except Exception as exc:
        print(f"{label}_read_error: {exc}")
        return
    print(f"{label}_tail_start")
    for line in text[-lines:]:
        print(line)
    print(f"{label}_tail_end")


def summarize_failed_games(run_dir: Path, limit: int = 5):
    output_dir = run_dir / "output"
    if not output_dir.exists():
        return
    failed_examples = []
    for game_dir in sorted(output_dir.iterdir()):
        if not game_dir.is_dir():
            continue
        error_files = []
        for pattern in ["**/*error*.txt", "**/*error*.log", "**/*stderr*.txt", "**/*traceback*.txt"]:
            error_files.extend(game_dir.glob(pattern))
        if error_files:
            failed_examples.append((game_dir.name, sorted({str(p.relative_to(game_dir)) for p in error_files})[:5]))
        if len(failed_examples) >= limit:
            break
    if failed_examples:
        print("failed_game_examples_start")
        for game_name, files in failed_examples:
            print(f"{game_name}: {', '.join(files)}")
        print("failed_game_examples_end")


def main():
    for run in RUNS:
        run_dir = BASE / run
        print(f"=== {run} ===")
        if not run_dir.exists():
            print("missing: yes\n")
            continue

        candidates = [
            run_dir / "summary.json",
            run_dir / "status.json",
            run_dir / "run.json",
            run_dir / "run_state.json",
            run_dir / "dashboard" / "dashboard_data.json",
            run_dir / "integrity_report.json",
        ]
        for candidate in candidates:
            print(f"{candidate.name}: {'yes' if candidate.exists() else 'no'}")

        inspected_any = False
        for candidate in candidates:
            if not candidate.exists():
                continue
            data = load_json(candidate)
            if "_parse_error" in data:
                print(f"parse_error: {candidate.name}: {data['_parse_error']}")
                continue

            inspected_any = True
            print(f"inspected: {candidate.name}")
            for key in [
                "status",
                "state",
                "completed",
                "failed",
                "succeeded",
                "total",
                "games_total",
                "games_completed",
                "games_failed",
                "start_time",
                "end_time",
                "output_dir",
                "run_id",
            ]:
                if key in data:
                    print(f"{key}: {data[key]}")

            for key in ["games", "results", "items", "entries", "tasks"]:
                value = data.get(key)
                if isinstance(value, list):
                    summarized = summarize_items(value)
                    print(f"{key}_len: {summarized['total']}")
                    print(f"{key}_done_like: {summarized['done_like']}")
                    print(f"{key}_failed_like: {summarized['failed_like']}")
                    print(f"{key}_other_status_like: {summarized['other_status_like']}")

            if candidate.name == "run_state.json":
                if "pending_game_ids" in data:
                    print(f"pending_game_ids: {len(data['pending_game_ids'])}")
                if "active_game_ids" in data:
                    print(f"active_game_ids: {len(data['active_game_ids'])}")
                if "completed_game_ids" in data:
                    print(f"completed_game_ids: {len(data['completed_game_ids'])}")
                if "failed_game_ids" in data:
                    print(f"failed_game_ids: {len(data['failed_game_ids'])}")

            if candidate.name == "dashboard_data.json":
                for key in [
                    "totalGames",
                    "completedGames",
                    "failedGames",
                    "runningGames",
                    "queuedGames",
                    "completionPercent",
                ]:
                    if key in data:
                        print(f"{key}: {data[key]}")
                failed_examples = []
                for game in data.get("games", []):
                    if not isinstance(game, dict):
                        continue
                    status = str(game.get("status") or game.get("state") or "").lower()
                    if "fail" in status or "error" in status:
                        failed_examples.append(
                            {
                                "game_id": game.get("game_id") or game.get("id") or game.get("name"),
                                "status": game.get("status") or game.get("state"),
                                "error": game.get("error") or game.get("failure_reason") or game.get("message"),
                            }
                        )
                    if len(failed_examples) >= 5:
                        break
                if failed_examples:
                    print("dashboard_failed_examples_start")
                    for example in failed_examples:
                        print(
                            f"{example['game_id']}: status={example['status']} error={example['error']}"
                        )
                    print("dashboard_failed_examples_end")

            if candidate.name == "integrity_report.json":
                for key in [
                    "missing_outputs",
                    "unexpected_outputs",
                    "missing_inputs",
                    "orphan_outputs",
                ]:
                    value = data.get(key)
                    if isinstance(value, list):
                        print(f"{key}: {len(value)}")

        if not inspected_any:
            child_dirs = [p for p in run_dir.iterdir() if p.is_dir()]
            print(f"child_dirs: {len(child_dirs)}")

        print_tail("batch_launcher_stderr", run_dir / "batch_launcher_stderr.txt", lines=25)
        print_tail("batch_launcher_stdout", run_dir / "batch_launcher_stdout.txt", lines=25)
        print_tail("run_parallel_batch_debug_trace", run_dir / "run_parallel_batch_debug_trace.log", lines=25)
        summarize_failed_games(run_dir)

        print()


if __name__ == "__main__":
    main()