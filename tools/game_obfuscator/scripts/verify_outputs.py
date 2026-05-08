#!/usr/bin/env python3
from __future__ import annotations

import argparse
import threading
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from orchestration_state import load_json, recompute_run_state, update_game_state, write_json

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record verification findings for Game Obfuscator outputs.")
    parser.add_argument("--run-dir", required=True, help="Path to a Game Obfuscator run directory.")
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=8000,
        help="Browser navigation/runtime observation timeout in milliseconds.",
    )
    return parser.parse_args()


class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def build_runtime_url(index_path: Path, server_root: Path, port: int) -> str:
    relative_path = index_path.resolve().relative_to(server_root.resolve())
    return f"http://127.0.0.1:{port}/{relative_path.as_posix()}"


def run_browser_verification(runtime_url: str, timeout_ms: int) -> dict:
    console_messages: list[dict] = []
    page_errors: list[str] = []
    request_failures: list[dict] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.on(
            "console",
            lambda msg: console_messages.append(
                {
                    "type": msg.type,
                    "text": msg.text,
                }
            ),
        )
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        page.on(
            "requestfailed",
            lambda request: request_failures.append(
                {
                    "url": request.url,
                    "failure": request.failure,
                }
            ),
        )

        page.goto(runtime_url, wait_until="load", timeout=timeout_ms)
        page.wait_for_timeout(min(timeout_ms, 3000))

        browser.close()

    return {
        "console_messages": console_messages,
        "page_errors": page_errors,
        "request_failures": request_failures,
    }


def verify_site(index_path: Path, emoji_dir: Path, run_dir: Path, timeout_ms: int) -> dict:
    findings: list[dict] = []
    passed_checks: list[str] = []
    failed_checks: list[str] = []

    if index_path.exists():
        passed_checks.append("runtime_entrypoint_exists")
    else:
        failed_checks.append("runtime_entrypoint_exists")

    if emoji_dir.exists():
        passed_checks.append("emoji_assets_directory_exists")
    else:
        failed_checks.append("emoji_assets_directory_exists")

    browser_artifact = {
        "runtime_url": None,
        "console_messages": [],
        "page_errors": [],
        "request_failures": [],
        "status": "skipped",
    }

    if index_path.exists():
        server_root = run_dir
        handler = partial(QuietHTTPRequestHandler, directory=str(server_root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        try:
            runtime_url = build_runtime_url(index_path, server_root, server.server_port)
            browser_artifact["runtime_url"] = runtime_url

            try:
                browser_result = run_browser_verification(runtime_url, timeout_ms)
                browser_artifact.update(browser_result)
                browser_artifact["status"] = "executed"

                fatal_console_errors = [
                    entry
                    for entry in browser_result["console_messages"]
                    if entry["type"] == "error" and entry["text"]
                ]

                if browser_result["page_errors"] or fatal_console_errors:
                    failed_checks.append("no_fatal_js_boot_errors")

                    for message in browser_result["page_errors"]:
                        findings.append(
                            {
                                "type": "browser_runtime_error",
                                "severity": "error",
                                "message": message,
                                "source": "playwright_pageerror",
                            }
                        )

                    for entry in fatal_console_errors:
                        findings.append(
                            {
                                "type": "browser_console_error",
                                "severity": "error",
                                "message": entry["text"],
                                "source": "playwright_console",
                            }
                        )
                else:
                    passed_checks.append("no_fatal_js_boot_errors")

                if browser_result["request_failures"]:
                    findings.extend(
                        {
                            "type": "browser_request_failure",
                            "severity": "warning",
                            "message": f"{item['url']} :: {item['failure']}",
                            "source": "playwright_requestfailed",
                        }
                        for item in browser_result["request_failures"]
                    )
            except (PlaywrightError, TimeoutError) as exc:
                failed_checks.append("browser_verification_execution")
                findings.append(
                    {
                        "type": "browser_verification_error",
                        "severity": "error",
                        "message": str(exc),
                        "source": "playwright_runner",
                    }
                )
                browser_artifact["status"] = "failed"
        finally:
            server.shutdown()
            server.server_close()
            server_thread.join(timeout=2)

    if not findings and "no_fatal_js_boot_errors" not in passed_checks:
        findings.append(
            {
                "type": "verification_incomplete",
                "severity": "warning",
                "message": "Browser verification did not run to completion.",
                "source": "verification_pipeline",
            }
        )

    return {
        "runtime_entrypoint": str(index_path),
        "passed_checks": sorted(set(passed_checks)),
        "failed_checks": sorted(set(failed_checks)),
        "findings": findings,
        "browser_artifact": browser_artifact,
        "status": "failed" if failed_checks else "passed",
    }


def verify_game(game_state: dict, run_dir: Path, timeout_ms: int) -> dict:
    output_dir = Path(game_state["output_path"])
    artifacts_dir = Path(game_state["artifacts_path"])
    index_path = output_dir / "index.html"
    emoji_dir = output_dir / "assets" / "emoji"

    verification = {
        "generated_at": utc_now(),
        "game_id": game_state["game_id"],
        **verify_site(index_path, emoji_dir, run_dir, timeout_ms),
    }
    write_json(artifacts_dir / "verification.json", verification)
    return verification


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    manifest = load_json(run_dir / "input_manifest.json")
    run_state = load_json(run_dir / "run_state.json")
    recompute_run_state(run_dir, current_phase="verification_started", note="Verification stage started.")

    verified_games = 0
    verification_failed = 0

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        game_state_path = run_dir / "games" / game_id / "game_state.json"
        game_state = load_json(game_state_path)

        update_game_state(
            run_dir,
            game_id,
            status="running",
            phase="verification_started",
            last_error=None,
            mark_started=True,
            heartbeat=True,
            progress=True,
        )

        verification = verify_game(game_state, run_dir, args.timeout_ms)
        verified_games += 1

        if verification["failed_checks"]:
            verification_failed += 1
            status = "failed"
        else:
            status = "succeeded"

        artifacts_dir = Path(game_state["artifacts_path"])
        update_game_state(
            run_dir,
            game_id,
            status=status,
            phase="verification_complete",
            last_error=verification["findings"][0]["message"] if verification["failed_checks"] else None,
            heartbeat=True,
            progress=True,
            mark_completed=True,
            artifacts={
                "verification": str(artifacts_dir / "verification.json"),
            },
        )

    run_state["games_verified"] = verified_games
    run_state["games_verification_failed"] = verification_failed
    run_state["current_phase"] = "verification_complete"
    run_state["status"] = "verification_failed" if verification_failed else "verification_passed"
    run_state["updated_at"] = utc_now()
    run_state.setdefault("notes", []).append("Playwright verification completed.")
    write_json(run_dir / "run_state.json", run_state)
    recompute_run_state(run_dir, current_phase="verification_complete")

    print(run_dir)


if __name__ == "__main__":
    main()