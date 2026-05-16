import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error, parse, request


BASE_URL = "https://api.rezona.ai"
DEFAULT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzcxODY4ODMsImlhdCI6MTc3NTg5MDg4MywidXNlck5hbWUiOiJGZXJuYW5kYSBCZWx0csOhbiIsInVzZXJfaWQiOjk3OTA0NzAsInVzZXJfbmFtZSI6IkZlcm5hbmRhIEJlbHRyw6FuIn0.2Two5KNUcB_kTHuCGzgh2UDZeuPF9H9K1oDx53lKcFw"
DEFAULT_DELAY_SECONDS = 2.0
DEFAULT_OUTPUT_SUBDIR = "game_details"
DEFAULT_OUTPUT_ROOT = "outputs/rezona_crawl"


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(payload), encoding="utf-8")


def resolve_run_dir(
    run_dir: str | None, games_file: str | None, output_dir: str | None
) -> tuple[Path | None, Path, Path]:
    if run_dir:
        resolved_run_dir = Path(run_dir)
        resolved_games_file = resolved_run_dir / "summaries" / "all_games_deduped.json"
        resolved_output_dir = (
            Path(output_dir) if output_dir else resolved_run_dir / DEFAULT_OUTPUT_SUBDIR
        )
        return resolved_run_dir, resolved_games_file, resolved_output_dir

    if games_file:
        resolved_games_file = Path(games_file)
        resolved_run_dir = resolved_games_file.parent.parent
        resolved_output_dir = (
            Path(output_dir) if output_dir else resolved_run_dir / DEFAULT_OUTPUT_SUBDIR
        )
        return resolved_run_dir, resolved_games_file, resolved_output_dir

    latest_run_path = Path(DEFAULT_OUTPUT_ROOT) / "latest_run.txt"
    if latest_run_path.exists():
        latest_run_name = latest_run_path.read_text(encoding="utf-8").strip()
        if latest_run_name:
            resolved_run_dir = Path(DEFAULT_OUTPUT_ROOT) / latest_run_name
            resolved_games_file = resolved_run_dir / "summaries" / "all_games_deduped.json"
            resolved_output_dir = (
                Path(output_dir) if output_dir else resolved_run_dir / DEFAULT_OUTPUT_SUBDIR
            )
            return resolved_run_dir, resolved_games_file, resolved_output_dir

    raise ValueError(
        "Unable to resolve input source. Pass --run-dir or --games-file, or ensure "
        "outputs/rezona_crawl/latest_run.txt points to a valid run."
    )


def normalize_detail_payload(
    source_game: dict[str, Any], detail_payload: dict[str, Any], run_dir: Path | None
) -> dict[str, Any]:
    detail = detail_payload.get("data", {})
    creator = detail.get("creator") or {}
    stats = detail.get("stats") or {}

    return {
        "run_id": run_dir.name if run_dir else None,
        "game_id": detail.get("game_id", source_game.get("game_id")),
        "game_version": detail.get("game_version", source_game.get("game_version")),
        "name": detail.get("name", source_game.get("name")),
        "description": detail.get("description", source_game.get("description")),
        "url": detail.get("url", source_game.get("url")),
        "cover_url": detail.get("cover_url", source_game.get("cover_url")),
        "dynamic_cover_url": detail.get(
            "dynamic_cover_url", source_game.get("dynamic_cover_url")
        ),
        "screen_orientation": detail.get(
            "screen_orientation", source_game.get("screen_orientation")
        ),
        "is_public": detail.get("is_public", source_game.get("is_public")),
        "is_liked": detail.get("is_liked", source_game.get("is_liked")),
        "remixable": detail.get("remixable", source_game.get("remixable")),
        "remixed_games": detail.get("remixed_games", source_game.get("remixed_games")),
        "created_at": detail.get("created_at", source_game.get("created_at")),
        "updated_at": detail.get("updated_at", source_game.get("updated_at")),
        "creator": {
            "id": creator.get("id"),
            "name": creator.get("name"),
            "avatar": creator.get("avatar"),
            "follow_status": creator.get("follow_status"),
        },
        "stats": {
            "played_count": stats.get("played_count"),
            "liked_count": stats.get("liked_count"),
            "shared_count": stats.get("shared_count"),
            "comment_count": stats.get("comment_count"),
        },
        "source_topic": source_game.get("topic"),
    }


class RezonaGameDetailFetcher:
    def __init__(
        self,
        token: str,
        games_file: Path,
        output_dir: Path,
        delay_seconds: float,
        limit: int,
        force: bool,
        run_dir: Path | None,
        manifest_path: Path | None,
    ) -> None:
        self.token = token
        self.games_file = games_file
        self.output_dir = output_dir
        self.delay_seconds = delay_seconds
        self.limit = limit
        self.force = force
        self.run_dir = run_dir
        self.manifest_path = manifest_path
        self.summary_path = self.output_dir / "enrichment_summary.json"
        self.total_api_calls = 0

    def request_json(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        query_string = parse.urlencode(
            {key: value for key, value in params.items() if value is not None}
        )
        url = f"{BASE_URL}{endpoint}"
        if query_string:
            url = f"{url}?{query_string}"

        if self.total_api_calls > 0:
            print(f"⏳ sleeping {self.delay_seconds:.1f}s before next detail call", flush=True)
            time.sleep(self.delay_seconds)

        print(f"→ GET {url}", flush=True)

        req = request.Request(
            url,
            headers={
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.token}",
                "x-os": "ios",
            },
        )

        try:
            with request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                status_code = response.getcode()
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Network error for {url}: {exc}") from exc

        self.total_api_calls += 1
        print(
            f"← status={status_code} bytes={len(body)} detail_calls={self.total_api_calls}",
            flush=True,
        )

        payload = json.loads(body)
        if payload.get("code") != 0:
            raise RuntimeError(f"API error for {url}: {payload}")

        return payload

    def load_games(self) -> list[dict[str, Any]]:
        payload = read_json(self.games_file, {})
        items = payload.get("items")
        if not isinstance(items, list):
            raise ValueError(
                f"Expected {self.games_file} to contain an object with an 'items' list."
            )
        return items

    def update_manifest(self, summary: dict[str, Any], status: str) -> None:
        if not self.manifest_path:
            return

        manifest = read_json(self.manifest_path, {})
        manifest["game_details_enrichment"] = {
            "status": status,
            "games_file": str(
                self.games_file.relative_to(self.run_dir)
                if self.run_dir and self.games_file.is_relative_to(self.run_dir)
                else self.games_file
            ),
            "output_dir": str(
                self.output_dir.relative_to(self.run_dir)
                if self.run_dir and self.output_dir.is_relative_to(self.run_dir)
                else self.output_dir
            ),
            "total_candidates": summary["total_candidates"],
            "processed": summary["processed"],
            "succeeded": summary["succeeded"],
            "failed": summary["failed"],
            "skipped": summary["skipped"],
            "api_calls_made": summary["api_calls_made"],
            "last_game_id": summary["last_game_id"],
            "started_at": summary["started_at"],
            "completed_at": summary.get("completed_at"),
            "updated_at": utc_now(),
        }
        write_json(self.manifest_path, manifest)

    def run(self) -> dict[str, Any]:
        games = self.load_games()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        seen_game_ids: set[Any] = set()
        summary = {
            "started_at": utc_now(),
            "completed_at": None,
            "run_dir": str(self.run_dir) if self.run_dir else None,
            "games_file": str(self.games_file),
            "output_dir": str(self.output_dir),
            "total_candidates": len(games),
            "limit": self.limit,
            "force": self.force,
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "skipped": 0,
            "api_calls_made": 0,
            "last_game_id": None,
            "results": [],
        }

        self.update_manifest(summary, "running")

        for item in games:
            game_id = item.get("game_id")
            if game_id in seen_game_ids:
                continue
            seen_game_ids.add(game_id)

            if game_id is None:
                summary["failed"] += 1
                summary["results"].append(
                    {"game_id": None, "status": "failed", "error": "missing game_id"}
                )
                continue

            game_dir = self.output_dir / f"game_{game_id}"
            source_path = game_dir / "source_game.json"
            detail_path = game_dir / "detail.json"
            normalized_path = game_dir / "normalized.json"

            if detail_path.exists() and not self.force:
                summary["skipped"] += 1
                summary["last_game_id"] = game_id
                summary["results"].append({"game_id": game_id, "status": "skipped"})
                continue

            if self.limit > 0 and summary["processed"] >= self.limit:
                break

            game_dir.mkdir(parents=True, exist_ok=True)
            write_json(source_path, item)

            try:
                payload = self.request_json("/api/v3/game/detail", {"game_id": game_id})
                write_json(detail_path, payload)
                write_json(
                    normalized_path,
                    normalize_detail_payload(item, payload, self.run_dir),
                )
                summary["processed"] += 1
                summary["succeeded"] += 1
                summary["last_game_id"] = game_id
                summary["api_calls_made"] = self.total_api_calls
                summary["results"].append({"game_id": game_id, "status": "success"})
            except Exception as exc:
                summary["processed"] += 1
                summary["failed"] += 1
                summary["last_game_id"] = game_id
                summary["api_calls_made"] = self.total_api_calls
                write_json(
                    game_dir / "error.json",
                    {
                        "game_id": game_id,
                        "error": str(exc),
                        "failed_at": utc_now(),
                    },
                )
                summary["results"].append(
                    {"game_id": game_id, "status": "failed", "error": str(exc)}
                )

            write_json(self.summary_path, summary)
            self.update_manifest(summary, "running")
            print(
                f"[processed={summary['processed']} skipped={summary['skipped']}] "
                f"game_id={game_id} succeeded={summary['succeeded']} failed={summary['failed']}",
                flush=True,
            )

        summary["completed_at"] = utc_now()
        summary["api_calls_made"] = self.total_api_calls
        write_json(self.summary_path, summary)
        self.update_manifest(summary, "completed")
        print(
            f"✓ game detail enrichment complete | processed={summary['processed']} "
            f"skipped={summary['skipped']} succeeded={summary['succeeded']} "
            f"failed={summary['failed']} api_calls={summary['api_calls_made']}",
            flush=True,
        )
        return summary


def fetch_game_details_for_run(
    token: str,
    run_dir: Path | None,
    games_file: Path,
    output_dir: Path,
    delay_seconds: float = DEFAULT_DELAY_SECONDS,
    limit: int = 0,
    force: bool = False,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    fetcher = RezonaGameDetailFetcher(
        token=token,
        games_file=games_file,
        output_dir=output_dir,
        delay_seconds=delay_seconds,
        limit=limit,
        force=force,
        run_dir=run_dir,
        manifest_path=manifest_path,
    )
    return fetcher.run()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Rezona game detail payloads for the deduped games in a crawler run "
            "and save per-game JSON outputs."
        )
    )
    parser.add_argument(
        "--run-dir",
        help="Crawler run directory containing summaries/all_games_deduped.json.",
    )
    parser.add_argument(
        "--games-file",
        help="Explicit path to a deduped all_games_deduped.json file.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory where per-game detail outputs are written. Defaults to <run>/game_details.",
    )
    parser.add_argument(
        "--token",
        default=DEFAULT_TOKEN,
        help="Rezona bearer token. Defaults to the script constant near the top of the file.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help="Delay between game detail API calls.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Maximum number of uncached games to fetch during this execution. 0 means no limit.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-fetch games even when detail.json already exists.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.token or args.token == DEFAULT_TOKEN:
        print(
            "warning: using placeholder token value; replace DEFAULT_TOKEN or pass --token",
            file=sys.stderr,
            flush=True,
        )

    run_dir, games_file, output_dir = resolve_run_dir(
        run_dir=args.run_dir,
        games_file=args.games_file,
        output_dir=args.output_dir,
    )

    manifest_path = run_dir / "manifest.json" if run_dir else None
    fetch_game_details_for_run(
        token=args.token,
        run_dir=run_dir,
        games_file=games_file,
        output_dir=output_dir,
        delay_seconds=args.delay_seconds,
        limit=args.limit,
        force=args.force,
        manifest_path=manifest_path,
    )


if __name__ == "__main__":
    main()