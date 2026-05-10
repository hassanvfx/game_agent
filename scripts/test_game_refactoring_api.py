#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from typing import Any


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Submit and poll a real game_refactoring API job.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--workflow-id", default="creative_remix_v3")
    parser.add_argument("--raw-game-id", action="append", dest="raw_game_ids", required=True)
    parser.add_argument("--prompt", default="harry potter")
    parser.add_argument("--poll-seconds", type=float, default=3.0)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--dry-run-operators", action="store_true")
    parser.add_argument("--dry-run-spec-adaptor", action="store_true")
    return parser


def http_json(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    submit_payload = {
        "id": args.workflow_id,
        "raw_game_ids": args.raw_game_ids,
        "remix_prompt": args.prompt,
        "dry_run_operators": args.dry_run_operators,
        "dry_run_spec_adaptor": args.dry_run_spec_adaptor,
    }

    submit_url = args.base_url.rstrip("/") + "/jobs/game-refactoring"
    try:
        submit_response = http_json("POST", submit_url, submit_payload)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(body)
        return 1

    print(json.dumps({"submit": submit_response}, indent=2))
    task_id = submit_response["task_id"]
    status_url = args.base_url.rstrip("/") + f"/jobs/celery/{task_id}"

    start = time.time()
    while True:
        status_response = http_json("GET", status_url)
        print(json.dumps({"status": status_response}, indent=2))
        if status_response["status"] in {"completed", "failed"}:
            return 0 if status_response["status"] == "completed" else 1
        if time.time() - start > args.timeout_seconds:
            print(json.dumps({"error": "timeout", "taskId": task_id}, indent=2))
            return 2
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))