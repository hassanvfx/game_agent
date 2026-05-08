import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error, parse, request

from fetch_rezona_game_details import fetch_game_details_for_run


BASE_URL = "https://api.rezona.ai"
DEFAULT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzcxODY4ODMsImlhdCI6MTc3NTg5MDg4MywidXNlck5hbWUiOiJGZXJuYW5kYSBCZWx0csOhbiIsInVzZXJfaWQiOjk3OTA0NzAsInVzZXJfbmFtZSI6IkZlcm5hbmRhIEJlbHRyw6FuIn0.2Two5KNUcB_kTHuCGzgh2UDZeuPF9H9K1oDx53lKcFw"
DEFAULT_DELAY_SECONDS = 2.0
DEFAULT_SEARCH_PAGE_SIZE = 50
DEFAULT_TOPIC_PAGE_SIZE = 50
DEFAULT_MAX_RESULTS_PER_QUERY = 500
DEFAULT_OUTPUT_ROOT = "outputs/rezona_crawl"

DEFAULT_QUERIES = [
    "brainrot",
    "meme",
    "skibidi",
    "sigma",
    "rizz",
    "npc",
    "tiktok",
    "viral",
    "alpha",
    "genz",
    "drama",
    "love",
    "romance",
    "crush",
    "dating",
    "quiz",
    "trivia",
    "zombie",
    "racing",
    "fighting",
    "horror",
    "obby",
    "runner",
    "tycoon",
    "simulator",
    "minecraft",
    "flappy bird",
    "angry birds",
    "gta",
    "roblox",
    "fortnite",
    "subway surfers",
    "fnaf",
    "among us",
    "mario",
    "sonic",
    "pokemon",
]


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "query"


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(payload), encoding="utf-8")


def dedupe_games(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, Any]] = set()
    deduped: list[dict[str, Any]] = []

    for item in items:
        game_id = item.get("game_id")
        game_version = item.get("game_version")
        key = (game_id, game_version)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped


class RezonaCrawler:
    def __init__(
        self,
        token: str,
        output_root: Path,
        delay_seconds: float,
        search_page_size: int,
        topic_page_size: int,
        max_results_per_query: int,
        queries: list[str],
        fresh_run: bool,
    ) -> None:
        self.token = token
        self.output_root = output_root
        self.delay_seconds = delay_seconds
        self.search_page_size = search_page_size
        self.topic_page_size = topic_page_size
        self.max_results_per_query = max_results_per_query
        self.queries = queries
        self.fresh_run = fresh_run

        self.run_dir = self._resolve_run_dir()
        self.topics_dir = self.run_dir / "topics"
        self.search_dir = self.run_dir / "search"
        self.summaries_dir = self.run_dir / "summaries"
        self.manifest_path = self.run_dir / "manifest.json"

        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.topics_dir.mkdir(parents=True, exist_ok=True)
        self.search_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

        self.manifest = self._load_or_init_manifest()
        self.total_api_calls = int(self.manifest.get("total_api_calls", 0))

    def _resolve_run_dir(self) -> Path:
        if self.fresh_run:
            return self.output_root / f"run_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"

        latest_path = self.output_root / "latest_run.txt"
        if latest_path.exists():
            existing = latest_path.read_text(encoding="utf-8").strip()
            if existing:
                candidate = self.output_root / existing
                if candidate.exists():
                    return candidate

        return self.output_root / f"run_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"

    def _load_or_init_manifest(self) -> dict[str, Any]:
        latest_path = self.output_root / "latest_run.txt"
        latest_path.parent.mkdir(parents=True, exist_ok=True)
        latest_path.write_text(self.run_dir.name, encoding="utf-8")

        manifest = read_json(
            self.manifest_path,
            {
                "run_id": self.run_dir.name,
                "created_at": utc_now(),
                "updated_at": utc_now(),
                "base_url": BASE_URL,
                "delay_seconds": self.delay_seconds,
                "search_page_size": self.search_page_size,
                "topic_page_size": self.topic_page_size,
                "max_results_per_query": self.max_results_per_query,
                "query_count": len(self.queries),
                "queries": self.queries,
                "token_source": "hardcoded_default_or_cli_flag",
                "total_api_calls": 0,
                "topics": {
                    "status": "pending",
                    "topic_count": 0,
                    "completed_topics": 0,
                    "total_games_collected": 0,
                    "last_topic_id": None,
                },
                 "search": {
                     "status": "pending",
                     "query_count": len(self.queries),
                     "completed_queries": 0,
                     "total_games_collected": 0,
                     "last_query": None,
                 },
                "game_details_enrichment": {
                    "status": "pending",
                    "games_file": "summaries/all_games_deduped.json",
                    "output_dir": "game_details",
                    "total_candidates": 0,
                    "processed": 0,
                    "succeeded": 0,
                    "failed": 0,
                    "skipped": 0,
                    "api_calls_made": 0,
                    "last_game_id": None,
                    "started_at": None,
                    "completed_at": None,
                    "updated_at": None,
                },
            },
        )
        return manifest

    def save_manifest(self) -> None:
        self.manifest["updated_at"] = utc_now()
        self.manifest["total_api_calls"] = self.total_api_calls
        write_json(self.manifest_path, self.manifest)

    def request_json(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        query_string = parse.urlencode(
            {key: value for key, value in params.items() if value is not None}
        )
        url = f"{BASE_URL}{endpoint}"
        if query_string:
            url = f"{url}?{query_string}"

        if self.total_api_calls > 0:
            print(f"⏳ sleeping {self.delay_seconds:.1f}s before next call", flush=True)
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
        self.manifest["total_api_calls"] = self.total_api_calls
        self.save_manifest()

        print(f"← status={status_code} bytes={len(body)} calls={self.total_api_calls}", flush=True)

        payload = json.loads(body)
        if payload.get("code") != 0:
            raise RuntimeError(f"API error for {url}: {payload}")

        return payload

    def fetch_topics(self) -> list[dict[str, Any]]:
        self.manifest["topics"]["status"] = "running"
        self.save_manifest()

        payload = self.request_json("/api/v3/topic/all", {})
        topics = payload.get("data", {}).get("items", [])

        topics_payload = {
            "fetched_at": utc_now(),
            "count": len(topics),
            "items": topics,
        }
        write_json(self.topics_dir / "topics.json", topics_payload)

        self.manifest["topics"]["topic_count"] = len(topics)
        self.manifest["topics"]["status"] = "completed"
        self.save_manifest()

        print(f"✓ fetched {len(topics)} topics", flush=True)
        return topics

    def crawl_topic_games(self, topics: list[dict[str, Any]]) -> None:
        self.manifest["topics"]["status"] = "running"
        self.save_manifest()

        total_topics = len(topics)
        completed_topics = 0
        total_games = 0

        for index, topic in enumerate(topics, start=1):
            topic_id = topic.get("id")
            topic_name = topic.get("name", "")
            topic_path = self.topics_dir / f"topic_{topic_id}.json"
            topic_state = read_json(
                topic_path,
                {
                    "topic": topic,
                    "pages_fetched": [],
                    "last_page_fetched": 0,
                    "completed": False,
                    "stop_reason": None,
                    "games": [],
                    "total_collected": 0,
                    "expected_total": None,
                    "updated_at": None,
                },
            )

            if topic_state.get("completed"):
                completed_topics += 1
                total_games += len(topic_state.get("games", []))
                print(
                    f"↷ Topics: {index}/{total_topics} | topic_id={topic_id} | already completed | "
                    f"total {len(topic_state.get('games', []))}",
                    flush=True,
                )
                continue

            current_page = int(topic_state.get("last_page_fetched", 0)) + 1

            while True:
                payload = self.request_json(
                    "/api/v3/game/get_by_topic",
                    {
                        "topic_id": topic_id,
                        "page": current_page,
                        "size": self.topic_page_size,
                    },
                )
                data = payload.get("data", {})
                page = int(data.get("page", current_page))
                pages = int(data.get("pages", page))
                items = data.get("items", [])

                existing_games = topic_state.get("games", [])
                topic_state["games"] = dedupe_games(existing_games + items)
                topic_state["pages_fetched"] = sorted(
                    set(topic_state.get("pages_fetched", []) + [page])
                )
                topic_state["last_page_fetched"] = page
                topic_state["expected_total"] = data.get("total")
                topic_state["total_collected"] = len(topic_state["games"])
                topic_state["updated_at"] = utc_now()

                if page >= pages:
                    topic_state["completed"] = True
                    topic_state["stop_reason"] = "api_exhausted"

                write_json(topic_path, topic_state)

                self.manifest["topics"]["last_topic_id"] = topic_id
                self.manifest["topics"]["completed_topics"] = completed_topics + (
                    1 if topic_state.get("completed") else 0
                )
                self.manifest["topics"]["total_games_collected"] = total_games + len(
                    topic_state["games"]
                )
                self.save_manifest()

                print(
                    f"Topics: {index}/{total_topics} | topic_id={topic_id} | "
                    f"name={topic_name!r} | page {page}/{pages} | +{len(items)} items | "
                    f"total {topic_state['total_collected']}",
                    flush=True,
                )

                if topic_state.get("completed"):
                    break

                current_page = page + 1

            completed_topics += 1
            total_games += len(topic_state["games"])
            self.manifest["topics"]["completed_topics"] = completed_topics
            self.manifest["topics"]["total_games_collected"] = total_games
            self.save_manifest()

        self.manifest["topics"]["status"] = "completed"
        self.save_manifest()

    def crawl_search_queries(self) -> None:
        self.manifest["search"]["status"] = "running"
        self.save_manifest()

        completed_queries = 0
        total_games = 0

        for index, query in enumerate(self.queries, start=1):
            slug = slugify(query)
            query_path = self.search_dir / f"query_{slug}.json"
            query_state = read_json(
                query_path,
                {
                    "query": query,
                    "slug": slug,
                    "pages_fetched": [],
                    "last_page_fetched": 0,
                    "completed": False,
                    "stop_reason": None,
                    "items": [],
                    "games": [],
                    "total_collected": 0,
                    "expected_total": None,
                    "updated_at": None,
                },
            )

            if query_state.get("completed"):
                completed_queries += 1
                total_games += len(query_state.get("games", []))
                print(
                    f"↷ Search: {index}/{len(self.queries)} | query={query!r} | already completed | "
                    f"total {len(query_state.get('games', []))}",
                    flush=True,
                )
                continue

            current_page = int(query_state.get("last_page_fetched", 0)) + 1

            while True:
                payload = self.request_json(
                    "/api/v3/search",
                    {
                        "type": "game",
                        "q": query,
                        "page": current_page,
                        "size": self.search_page_size,
                    },
                )
                data = payload.get("data", {})
                page = int(data.get("page", current_page))
                pages = int(data.get("pages", page))
                items = data.get("items", [])

                flattened_games = []
                for item in items:
                    game = item.get("game")
                    if isinstance(game, dict):
                        flattened_games.append(game)

                existing_games = query_state.get("games", [])
                query_state["items"] = query_state.get("items", []) + items
                query_state["games"] = dedupe_games(existing_games + flattened_games)
                query_state["pages_fetched"] = sorted(
                    set(query_state.get("pages_fetched", []) + [page])
                )
                query_state["last_page_fetched"] = page
                query_state["expected_total"] = data.get("total")
                query_state["total_collected"] = len(query_state["games"])
                query_state["updated_at"] = utc_now()

                if query_state["total_collected"] >= self.max_results_per_query:
                    query_state["games"] = query_state["games"][: self.max_results_per_query]
                    query_state["total_collected"] = len(query_state["games"])
                    query_state["completed"] = True
                    query_state["stop_reason"] = "limit_reached"
                elif page >= pages:
                    query_state["completed"] = True
                    query_state["stop_reason"] = "api_exhausted"

                write_json(query_path, query_state)

                self.manifest["search"]["last_query"] = query
                self.manifest["search"]["completed_queries"] = completed_queries + (
                    1 if query_state.get("completed") else 0
                )
                self.manifest["search"]["total_games_collected"] = total_games + len(
                    query_state["games"]
                )
                self.save_manifest()

                print(
                    f"Search: {index}/{len(self.queries)} | query={query!r} | "
                    f"page {page}/{pages} | +{len(flattened_games)} games | "
                    f"collected {query_state['total_collected']}/{self.max_results_per_query}",
                    flush=True,
                )

                if query_state.get("completed"):
                    break

                current_page = page + 1

            completed_queries += 1
            total_games += len(query_state["games"])
            self.manifest["search"]["completed_queries"] = completed_queries
            self.manifest["search"]["total_games_collected"] = total_games
            self.save_manifest()

        self.manifest["search"]["status"] = "completed"
        self.save_manifest()

    def write_summaries(self) -> None:
        topic_summary = {
            "generated_at": utc_now(),
            "topics": [],
        }
        all_topic_games: list[dict[str, Any]] = []

        for topic_file in sorted(self.topics_dir.glob("topic_*.json")):
            data = read_json(topic_file, {})
            topic = data.get("topic", {})
            games = data.get("games", [])
            topic_summary["topics"].append(
                {
                    "topic_id": topic.get("id"),
                    "topic_name": topic.get("name"),
                    "completed": data.get("completed", False),
                    "stop_reason": data.get("stop_reason"),
                    "pages_fetched": len(data.get("pages_fetched", [])),
                    "total_collected": len(games),
                    "expected_total": data.get("expected_total"),
                    "file": str(topic_file.relative_to(self.run_dir)),
                }
            )
            all_topic_games.extend(games)

        search_summary = {
            "generated_at": utc_now(),
            "queries": [],
        }
        all_search_games: list[dict[str, Any]] = []

        for query_file in sorted(self.search_dir.glob("query_*.json")):
            data = read_json(query_file, {})
            games = data.get("games", [])
            search_summary["queries"].append(
                {
                    "query": data.get("query"),
                    "slug": data.get("slug"),
                    "completed": data.get("completed", False),
                    "stop_reason": data.get("stop_reason"),
                    "pages_fetched": len(data.get("pages_fetched", [])),
                    "total_collected": len(games),
                    "expected_total": data.get("expected_total"),
                    "file": str(query_file.relative_to(self.run_dir)),
                }
            )
            all_search_games.extend(games)

        deduped_union = dedupe_games(all_topic_games + all_search_games)

        write_json(self.summaries_dir / "topics_summary.json", topic_summary)
        write_json(self.summaries_dir / "search_summary.json", search_summary)
        write_json(
            self.summaries_dir / "all_games_deduped.json",
            {
                "generated_at": utc_now(),
                "count": len(deduped_union),
                "items": deduped_union,
            },
        )

        print(
            f"✓ summaries written | topics={len(topic_summary['topics'])} | "
            f"queries={len(search_summary['queries'])} | deduped_games={len(deduped_union)}",
            flush=True,
        )

    def run(
        self,
        post_enrich_game_details: bool = False,
        post_enrich_limit: int = 0,
        post_enrich_force: bool = False,
    ) -> None:
        print(f"Run directory: {self.run_dir}", flush=True)
        print(f"Configured queries: {len(self.queries)}", flush=True)
        print(f"Delay between calls: {self.delay_seconds:.1f}s", flush=True)

        topics_payload = read_json(self.topics_dir / "topics.json", None)
        if topics_payload and isinstance(topics_payload.get("items"), list):
            topics = topics_payload["items"]
            print(f"↷ reusing saved topics list ({len(topics)} topics)", flush=True)
        else:
            topics = self.fetch_topics()

        self.crawl_topic_games(topics)
        self.crawl_search_queries()
        self.write_summaries()

        if post_enrich_game_details:
            print("→ starting game detail enrichment", flush=True)
            fetch_game_details_for_run(
                token=self.token,
                run_dir=self.run_dir,
                games_file=self.summaries_dir / "all_games_deduped.json",
                output_dir=self.run_dir / "game_details",
                delay_seconds=self.delay_seconds,
                limit=post_enrich_limit,
                force=post_enrich_force,
                manifest_path=self.manifest_path,
            )

        print("✓ crawl complete", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Rezona topics, exhaust topic pagination, and run curated search "
            "queries while saving progressive JSON state."
        )
    )
    parser.add_argument(
        "--token",
        default=DEFAULT_TOKEN,
        help="Rezona bearer token. Defaults to the script constant near the top of the file.",
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory where run folders and JSON progress files are written.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help="Delay between API calls.",
    )
    parser.add_argument(
        "--search-page-size",
        type=int,
        default=DEFAULT_SEARCH_PAGE_SIZE,
        help="Requested page size for search pagination.",
    )
    parser.add_argument(
        "--topic-page-size",
        type=int,
        default=DEFAULT_TOPIC_PAGE_SIZE,
        help="Requested page size for topic game pagination.",
    )
    parser.add_argument(
        "--max-results-per-query",
        type=int,
        default=DEFAULT_MAX_RESULTS_PER_QUERY,
        help="Maximum deduped games to keep per search query.",
    )
    parser.add_argument(
        "--queries",
        nargs="*",
        default=DEFAULT_QUERIES,
        help="Optional override query list. If omitted, the built-in curated list is used.",
    )
    parser.add_argument(
        "--fresh-run",
        action="store_true",
        help="Start a new run directory instead of resuming the latest one.",
    )
    parser.add_argument(
        "--post-enrich-game-details",
        action="store_true",
        help="After writing the deduped crawl summary, fetch game detail payloads for each game_id.",
    )
    parser.add_argument(
        "--post-enrich-limit",
        type=int,
        default=0,
        help="Maximum number of uncached game detail fetches to perform after the crawl. 0 means no limit.",
    )
    parser.add_argument(
        "--post-enrich-force",
        action="store_true",
        help="Re-fetch cached game detail outputs during the post-enrichment phase.",
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

    crawler = RezonaCrawler(
        token=args.token,
        output_root=Path(args.output_root),
        delay_seconds=args.delay_seconds,
        search_page_size=args.search_page_size,
        topic_page_size=args.topic_page_size,
        max_results_per_query=args.max_results_per_query,
        queries=args.queries,
        fresh_run=args.fresh_run,
    )
    crawler.run(
        post_enrich_game_details=args.post_enrich_game_details,
        post_enrich_limit=args.post_enrich_limit,
        post_enrich_force=args.post_enrich_force,
    )


if __name__ == "__main__":
    main()