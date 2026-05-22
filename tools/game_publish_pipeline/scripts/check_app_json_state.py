#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"
DEFAULT_APP_JSON = DEFAULT_OBFUSCATED_ROOT / "app.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate app.json against real published public/obfuscated folder state, "
            "compute HTML MD5s, and flag identical public/obfuscated index files."
        )
    )
    parser.add_argument("--app-json", default=str(DEFAULT_APP_JSON), help="Path to the app.json catalog to validate.")
    parser.add_argument("--public-root", default=str(DEFAULT_PUBLIC_ROOT), help="Published public root.")
    parser.add_argument("--obfuscated-root", default=str(DEFAULT_OBFUSCATED_ROOT), help="Published obfuscated root.")
    parser.add_argument(
        "--mode",
        choices=("public", "obfuscated", "both"),
        default="both",
        help="Which published roots to validate against the app.json entries.",
    )
    parser.add_argument("--report-path", help="Optional path to write the JSON report.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any folder/index is missing or any same-content pair is detected.",
    )
    return parser


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def md5_file(path: Path) -> str:
    return md5_bytes(path.read_bytes())


def md5_json_payload(payload: Any) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return md5_bytes(normalized)


def normalize_entries(payload: Any) -> list[tuple[str, dict[str, Any]]]:
    if isinstance(payload, dict):
        if all(isinstance(value, dict) for value in payload.values()):
            return [(str(key), value) for key, value in payload.items()]
        entries = payload.get("entries")
        if isinstance(entries, list):
            normalized: list[tuple[str, dict[str, Any]]] = []
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    raise SystemExit("All entries in app.json must be JSON objects.")
                key = str(entry.get("composite_key") or f"entry_{index}")
                normalized.append((key, entry))
            return normalized
    raise SystemExit("app.json must be either a composite-key object map or an object with an 'entries' array.")


def relative_file_from_entry(entry: dict[str, Any], field_name: str, fallback_published_path: str) -> str:
    value = entry.get(field_name)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return str(Path(fallback_published_path) / "index.html")


def build_side_result(*, root: Path, directory_rel: str, index_rel: str) -> dict[str, Any]:
    directory_path = root / directory_rel
    index_path = root / index_rel
    folder_exists = directory_path.is_dir()
    index_exists = index_path.is_file()
    index_md5 = md5_file(index_path) if index_exists else None
    return {
        "root": str(root),
        "directory_rel": directory_rel,
        "directory_path": str(directory_path),
        "folder_exists": folder_exists,
        "index_rel": index_rel,
        "index_path": str(index_path),
        "index_exists": index_exists,
        "index_md5": index_md5,
    }


def append_failure(failures: list[dict[str, Any]], *, entry_key: str, side: str, category: str, path: str) -> None:
    failures.append(
        {
            "entry_key": entry_key,
            "side": side,
            "category": category,
            "path": path,
        }
    )


def generate_report(
    *,
    app_json_path: Path,
    public_root: Path,
    obfuscated_root: Path,
    mode: str = "both",
) -> dict[str, Any]:
    app_json_path = app_json_path.resolve()
    public_root = public_root.resolve()
    obfuscated_root = obfuscated_root.resolve()

    app_json_raw = app_json_path.read_bytes()
    app_json_payload = json.loads(app_json_raw.decode("utf-8"))
    app_json_md5 = md5_bytes(app_json_raw)
    entries = normalize_entries(app_json_payload)

    validate_public = mode in {"public", "both"}
    validate_obfuscated = mode in {"obfuscated", "both"}

    failures: list[dict[str, Any]] = []
    identical_html_entries: list[dict[str, Any]] = []
    entry_reports: list[dict[str, Any]] = []
    public_state_records: list[dict[str, Any]] = []
    obfuscated_state_records: list[dict[str, Any]] = []

    counts = {
        "missing_public_folder_count": 0,
        "missing_public_index_count": 0,
        "missing_obfuscated_folder_count": 0,
        "missing_obfuscated_index_count": 0,
        "same_html_count": 0,
        "valid_public_count": 0,
        "valid_obfuscated_count": 0,
    }

    for entry_key, entry in entries:
        published_path = str(entry.get("published_path") or "").strip()
        if not published_path:
            raise SystemExit(f"Entry '{entry_key}' is missing published_path.")

        entry_report: dict[str, Any] = {
            "entry_key": entry_key,
            "game_id": entry.get("game_id"),
            "remix_id": entry.get("remix_id"),
            "published_path": published_path,
        }

        public_result: dict[str, Any] | None = None
        obfuscated_result: dict[str, Any] | None = None

        if validate_public:
            public_index_rel = relative_file_from_entry(entry, "public_index_html", published_path)
            public_result = build_side_result(
                root=public_root,
                directory_rel=published_path,
                index_rel=public_index_rel,
            )
            entry_report["public"] = public_result
            public_state_records.append(
                {
                    "entry_key": entry_key,
                    "published_path": published_path,
                    "folder_exists": public_result["folder_exists"],
                    "index_exists": public_result["index_exists"],
                    "index_md5": public_result["index_md5"],
                }
            )
            if not public_result["folder_exists"]:
                counts["missing_public_folder_count"] += 1
                append_failure(
                    failures,
                    entry_key=entry_key,
                    side="public",
                    category="missing_folder",
                    path=public_result["directory_path"],
                )
            if not public_result["index_exists"]:
                counts["missing_public_index_count"] += 1
                append_failure(
                    failures,
                    entry_key=entry_key,
                    side="public",
                    category="missing_index",
                    path=public_result["index_path"],
                )
            if public_result["folder_exists"] and public_result["index_exists"]:
                counts["valid_public_count"] += 1

        if validate_obfuscated:
            obfuscated_index_rel = relative_file_from_entry(entry, "obfuscated_index_html", published_path)
            obfuscated_result = build_side_result(
                root=obfuscated_root,
                directory_rel=published_path,
                index_rel=obfuscated_index_rel,
            )
            entry_report["obfuscated"] = obfuscated_result
            obfuscated_state_records.append(
                {
                    "entry_key": entry_key,
                    "published_path": published_path,
                    "folder_exists": obfuscated_result["folder_exists"],
                    "index_exists": obfuscated_result["index_exists"],
                    "index_md5": obfuscated_result["index_md5"],
                }
            )
            if not obfuscated_result["folder_exists"]:
                counts["missing_obfuscated_folder_count"] += 1
                append_failure(
                    failures,
                    entry_key=entry_key,
                    side="obfuscated",
                    category="missing_folder",
                    path=obfuscated_result["directory_path"],
                )
            if not obfuscated_result["index_exists"]:
                counts["missing_obfuscated_index_count"] += 1
                append_failure(
                    failures,
                    entry_key=entry_key,
                    side="obfuscated",
                    category="missing_index",
                    path=obfuscated_result["index_path"],
                )
            if obfuscated_result["folder_exists"] and obfuscated_result["index_exists"]:
                counts["valid_obfuscated_count"] += 1

        if public_result and obfuscated_result and public_result["index_md5"] and obfuscated_result["index_md5"]:
            same_html = public_result["index_md5"] == obfuscated_result["index_md5"]
            entry_report["public_vs_obfuscated_same_html"] = same_html
            if same_html:
                counts["same_html_count"] += 1
                identical_html_entries.append(
                    {
                        "entry_key": entry_key,
                        "published_path": published_path,
                        "public_index_path": public_result["index_path"],
                        "obfuscated_index_path": obfuscated_result["index_path"],
                        "html_md5": public_result["index_md5"],
                    }
                )
        entry_reports.append(entry_report)

    public_state_md5 = md5_json_payload(public_state_records)
    obfuscated_state_md5 = md5_json_payload(obfuscated_state_records)
    combined_state_md5 = md5_json_payload(
        {
            "mode": mode,
            "public": public_state_records,
            "obfuscated": obfuscated_state_records,
        }
    )

    return {
        "app_json_path": str(app_json_path),
        "public_root": str(public_root),
        "obfuscated_root": str(obfuscated_root),
        "mode": mode,
        "app_json_md5": app_json_md5,
        "public_state_md5": public_state_md5,
        "obfuscated_state_md5": obfuscated_state_md5,
        "combined_state_md5": combined_state_md5,
        "cache_key": f"{app_json_md5}:{combined_state_md5}",
        "entry_count": len(entries),
        **counts,
        "failure_count": len(failures),
        "failures": failures,
        "identical_html_entries": identical_html_entries,
        "entries": entry_reports,
    }


def report_has_failures(report: dict[str, Any]) -> bool:
    return bool(report.get("failure_count") or report.get("same_html_count"))


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    report = generate_report(
        app_json_path=Path(args.app_json),
        public_root=Path(args.public_root),
        obfuscated_root=Path(args.obfuscated_root),
        mode=args.mode,
    )

    if args.report_path:
        write_json(Path(args.report_path).resolve(), report)

    print(json.dumps(report, indent=2))

    if args.strict and report_has_failures(report):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())