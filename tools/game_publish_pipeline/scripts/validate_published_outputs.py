#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
TOOL_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]

DEFAULT_PUBLIC_ROOT = REPO_ROOT / "games" / "published" / "public"
DEFAULT_OBFUSCATED_ROOT = REPO_ROOT / "games" / "published" / "obfuscated"

INDEX_NAME = "index.json"
APP_TAGS_NAME = "app_tags.json"
APP_NAME = "app.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate published public/obfuscated outputs, screenshots, and persistent app artifacts "
            "against a collection manifest."
        )
    )
    parser.add_argument("--manifest", required=True, help="Collection manifest with entries.")
    parser.add_argument("--public-root", default=str(DEFAULT_PUBLIC_ROOT), help="Published public root.")
    parser.add_argument("--obfuscated-root", default=str(DEFAULT_OBFUSCATED_ROOT), help="Published obfuscated root.")
    parser.add_argument("--collection-slug", default="vatsal_app_alpha", help="Collection slug for app artifacts.")
    parser.add_argument("--report-path", help="Optional path to write the JSON validation report.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any required validation failure is detected.",
    )
    return parser


def make_failure(category: str, message: str, *, expected: Any | None = None, actual: Any | None = None) -> dict[str, Any]:
    payload = {"category": category, "message": message}
    if expected is not None:
        payload["expected"] = expected
    if actual is not None:
        payload["actual"] = actual
    return payload


def sorted_screenshot_names(directory: Path) -> list[str]:
    if not directory.is_dir():
        return []
    names = [
        path.name
        for path in sorted(directory.iterdir())
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    ]
    return names


def expected_screenshot_names_from_record(record: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for key in ("screenshots", "screenshots_png", "screenshots_jpg"):
        value = record.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.strip():
                    names.append(Path(item).name)
    deduped: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name not in seen:
            deduped.append(name)
            seen.add(name)
    return deduped


def infer_manifest_entries(
    manifest_payload: Any,
    *,
    public_root: Path,
) -> list[dict[str, Any]]:
    if isinstance(manifest_payload, dict):
        entries = manifest_payload.get("entries")
        if not isinstance(entries, list):
            raise SystemExit("Manifest must be a JSON object with an 'entries' array.")
        normalized_entries: list[dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise SystemExit("Manifest entries must be JSON objects.")
            composite_key = str(entry.get("composite_key") or "")
            if not composite_key:
                raise SystemExit("Each manifest entry must include composite_key.")
            normalized_entries.append(entry)
        return normalized_entries

    if isinstance(manifest_payload, list):
        source_map: dict[str, list[str]] = {}
        for item in manifest_payload:
            if not isinstance(item, str):
                raise SystemExit("List manifests must contain source path strings.")
            game_id = Path(item).name
            source_map.setdefault(game_id, []).append(item)

        normalized_entries = []
        game_counters: Counter[str] = Counter()
        for index_path in sorted(public_root.rglob("index.html")):
            rel = index_path.relative_to(public_root)
            parts = rel.parts
            if len(parts) < 3:
                continue
            game_id = parts[0]
            remix_id = parts[1]
            published_path = str(Path(*parts[:-1]))
            ordinal = game_counters[game_id]
            game_counters[game_id] += 1
            sources = source_map.get(game_id, [])
            source = sources[ordinal] if ordinal < len(sources) else (sources[0] if sources else None)
            normalized_entries.append(
                {
                    "game_id": game_id,
                    "remix_id": remix_id,
                    "composite_key": f"{game_id}__{remix_id}",
                    "published_path": published_path,
                    "source": source,
                }
            )
        if not normalized_entries:
            raise SystemExit("Could not infer entries from list manifest and public root.")
        return normalized_entries

    raise SystemExit("Manifest must be either a JSON object with entries or a JSON list of source paths.")


def resolve_obfuscated_paths(entry: dict[str, Any], obfuscated_root: Path) -> tuple[Path, Path, Path]:
    game_id = str(entry.get("game_id") or "")
    remix_id = str(entry.get("remix_id") or "")
    nested_dir = obfuscated_root / game_id / remix_id
    if (nested_dir / "index.html").is_file() or nested_dir.is_dir():
        obfuscated_dir = nested_dir
    else:
        obfuscated_dir = obfuscated_root / game_id
    return obfuscated_dir, obfuscated_dir / "index.html", obfuscated_dir / "screenshots"


def validate_entry(entry: dict[str, Any], public_root: Path, obfuscated_root: Path) -> dict[str, Any]:
    composite_key = str(entry.get("composite_key") or "")
    game_id = str(entry.get("game_id") or "")
    remix_id = str(entry.get("remix_id") or "")
    published_path = str(entry.get("published_path") or "")

    public_dir = public_root / published_path
    public_index = public_dir / "index.html"
    public_screenshots_dir = public_dir / "screenshots"

    obfuscated_dir, obfuscated_index, obfuscated_screenshots_dir = resolve_obfuscated_paths(entry, obfuscated_root)

    failures: list[dict[str, Any]] = []

    if not public_dir.is_dir():
        failures.append(
            make_failure(
                "missing_public_output",
                "Public output directory is missing.",
                expected=str(public_dir),
            )
        )
    if not public_index.is_file():
        failures.append(
            make_failure(
                "missing_public_index",
                "Public index.html is missing.",
                expected=str(public_index),
            )
        )
    if not obfuscated_dir.is_dir():
        failures.append(
            make_failure(
                "missing_obfuscated_output",
                "Obfuscated output directory is missing.",
                expected=str(obfuscated_dir),
            )
        )
    if not obfuscated_index.is_file():
        failures.append(
            make_failure(
                "missing_obfuscated_index",
                "Obfuscated index.html is missing.",
                expected=str(obfuscated_index),
            )
        )

    public_screenshot_names = sorted_screenshot_names(public_screenshots_dir)
    obfuscated_screenshot_names = sorted_screenshot_names(obfuscated_screenshots_dir)
    expected_screenshot_names = expected_screenshot_names_from_record(entry)
    screenshots_expected = len(expected_screenshot_names) > 0

    if screenshots_expected and not public_screenshots_dir.is_dir():
        failures.append(
            make_failure(
                "missing_public_screenshots_dir",
                "Public screenshots directory is missing even though screenshots are expected.",
                expected=str(public_screenshots_dir),
            )
        )
    if screenshots_expected and not obfuscated_screenshots_dir.is_dir():
        failures.append(
            make_failure(
                "missing_obfuscated_screenshots_dir",
                "Obfuscated screenshots directory is missing even though screenshots are expected.",
                expected=str(obfuscated_screenshots_dir),
            )
        )

    if screenshots_expected and len(public_screenshot_names) != len(expected_screenshot_names):
        failures.append(
            make_failure(
                "public_screenshot_count_mismatch",
                "Public screenshot count does not match the manifest-backed expectation.",
                expected=len(expected_screenshot_names),
                actual=len(public_screenshot_names),
            )
        )

    if screenshots_expected and public_screenshot_names != expected_screenshot_names:
        failures.append(
            make_failure(
                "public_screenshot_name_mismatch",
                "Public screenshot filenames do not match the manifest-backed expectation.",
                expected=expected_screenshot_names,
                actual=public_screenshot_names,
            )
        )

    if len(public_screenshot_names) != len(obfuscated_screenshot_names):
        failures.append(
            make_failure(
                "screenshot_count_mismatch",
                "Public and obfuscated screenshot counts do not match.",
                expected=len(public_screenshot_names),
                actual=len(obfuscated_screenshot_names),
            )
        )

    if public_screenshot_names != obfuscated_screenshot_names:
        failures.append(
            make_failure(
                "screenshot_name_mismatch",
                "Public and obfuscated screenshot filenames are not preserved.",
                expected=public_screenshot_names,
                actual=obfuscated_screenshot_names,
            )
        )

    expected_public_index = f"{published_path}/index.html"
    expected_obfuscated_indexes = [
        f"{game_id}/{remix_id}/index.html",
        f"{game_id}/index.html",
    ]
    actual_public_index = str(entry.get("public_index_html") or entry.get("index_html") or "")
    actual_obfuscated_index = str(entry.get("obfuscated_index_html") or "")

    if actual_public_index and actual_public_index != expected_public_index:
        failures.append(
            make_failure(
                "metadata_public_index_mismatch",
                "Entry public index metadata does not match the expected published path.",
                expected=expected_public_index,
                actual=actual_public_index,
            )
        )

    if actual_obfuscated_index and actual_obfuscated_index not in expected_obfuscated_indexes:
        failures.append(
            make_failure(
                "metadata_obfuscated_index_mismatch",
                "Entry obfuscated index metadata does not match an expected obfuscated path shape.",
                expected=expected_obfuscated_indexes,
                actual=actual_obfuscated_index,
            )
        )

    return {
        "composite_key": composite_key,
        "game_id": game_id,
        "remix_id": remix_id,
        "published_path": published_path,
        "source": entry.get("source"),
        "public_dir": str(public_dir),
        "obfuscated_dir": str(obfuscated_dir),
        "public_index_exists": public_index.is_file(),
        "obfuscated_index_exists": obfuscated_index.is_file(),
        "expected_screenshot_names": expected_screenshot_names,
        "public_screenshot_names": public_screenshot_names,
        "obfuscated_screenshot_names": obfuscated_screenshot_names,
        "screenshots_expected": screenshots_expected,
        "status": "failed" if failures else "passed",
        "failures": failures,
    }


def validate_catalog_record_paths(
    *,
    label: str,
    record: dict[str, Any],
    composite_key: str,
    expected_game_id: str,
    expected_remix_id: str,
    expected_published_path: str,
    public_root: Path,
    obfuscated_root: Path,
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []

    actual_game_id = str(record.get("game_id") or "")
    actual_remix_id = str(record.get("remix_id") or "")
    actual_published_path = str(record.get("published_path") or "")

    if actual_game_id != expected_game_id:
        failures.append(
            make_failure(
                "catalog_game_id_mismatch",
                f"{label} record game_id does not match manifest entry.",
                expected=expected_game_id,
                actual=actual_game_id,
            )
        )
    if actual_remix_id != expected_remix_id:
        failures.append(
            make_failure(
                "catalog_remix_id_mismatch",
                f"{label} record remix_id does not match manifest entry.",
                expected=expected_remix_id,
                actual=actual_remix_id,
            )
        )
    if actual_published_path != expected_published_path:
        failures.append(
            make_failure(
                "catalog_published_path_mismatch",
                f"{label} record published_path does not match manifest entry.",
                expected=expected_published_path,
                actual=actual_published_path,
            )
        )

    public_index_html = record.get("public_index_html") or record.get("index_html")
    if isinstance(public_index_html, str) and public_index_html.strip():
        public_index_path = public_root / public_index_html
        if not public_index_path.is_file():
            failures.append(
                make_failure(
                    "broken_app_public_reference",
                    f"{label} record points at a public index that does not exist.",
                    expected=str(public_index_path),
                    actual=public_index_html,
                )
            )

    obfuscated_index_html = record.get("obfuscated_index_html") or record.get("index_html")
    if isinstance(obfuscated_index_html, str) and obfuscated_index_html.strip():
        obfuscated_index_path = obfuscated_root / obfuscated_index_html
        if not obfuscated_index_path.is_file():
            failures.append(
                make_failure(
                    "broken_app_obfuscated_reference",
                    f"{label} record points at an obfuscated index that does not exist.",
                    expected=str(obfuscated_index_path),
                    actual=obfuscated_index_html,
                )
            )

    screenshots = record.get("screenshots")
    if isinstance(screenshots, list):
        for item in screenshots:
            if isinstance(item, str) and item.strip():
                screenshot_path = public_root / item
                if not screenshot_path.is_file():
                    failures.append(
                        make_failure(
                            "broken_app_screenshot_reference",
                            f"{label} record points at a screenshot that does not exist.",
                            expected=str(screenshot_path),
                            actual=item,
                        )
                    )
                    break

    return failures


def validate_catalog_artifact(
    *,
    label: str,
    path: Path,
    manifest_entries: dict[str, dict[str, Any]],
    public_root: Path,
    obfuscated_root: Path,
) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    record_results: list[dict[str, Any]] = []

    if not path.is_file():
        return {
            "label": label,
            "path": str(path),
            "status": "failed",
            "record_count": 0,
            "failures": [
                make_failure(
                    "missing_app_artifact",
                    f"{label} artifact is missing.",
                    expected=str(path),
                )
            ],
            "records": [],
        }

    payload = load_json(path)
    if not isinstance(payload, dict):
        return {
            "label": label,
            "path": str(path),
            "status": "failed",
            "record_count": 0,
            "failures": [
                make_failure(
                    "invalid_app_artifact_format",
                    f"{label} artifact must be a JSON object keyed by composite key.",
                    actual=type(payload).__name__,
                )
            ],
            "records": [],
        }

    payload_keys = set(payload.keys())
    manifest_keys = set(manifest_entries.keys())

    missing_keys = sorted(manifest_keys - payload_keys)
    extra_keys = sorted(payload_keys - manifest_keys)

    if missing_keys:
        failures.append(
            make_failure(
                "missing_app_entries",
                f"{label} artifact is missing manifest entries.",
                expected=missing_keys,
            )
        )
    if extra_keys:
        failures.append(
            make_failure(
                "unexpected_app_entries",
                f"{label} artifact contains unexpected entries not present in the manifest.",
                actual=extra_keys,
            )
        )

    for composite_key in sorted(payload_keys & manifest_keys):
        manifest_entry = manifest_entries[composite_key]
        record = payload.get(composite_key)
        if not isinstance(record, dict):
            record_failures = [
                make_failure(
                    "invalid_app_record",
                    f"{label} record must be a JSON object.",
                    actual=type(record).__name__,
                )
            ]
        else:
            record_failures = validate_catalog_record_paths(
                label=label,
                record=record,
                composite_key=composite_key,
                expected_game_id=str(manifest_entry.get("game_id") or ""),
                expected_remix_id=str(manifest_entry.get("remix_id") or ""),
                expected_published_path=str(manifest_entry.get("published_path") or ""),
                public_root=public_root,
                obfuscated_root=obfuscated_root,
            )
        if record_failures:
            failures.extend(record_failures)
        record_results.append(
            {
                "composite_key": composite_key,
                "status": "failed" if record_failures else "passed",
                "failures": record_failures,
            }
        )

    return {
        "label": label,
        "path": str(path),
        "status": "failed" if failures else "passed",
        "record_count": len(payload),
        "failures": failures,
        "records": record_results,
    }


def build_summary(
    entry_results: list[dict[str, Any]],
    app_artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    counter: Counter[str] = Counter()

    for entry in entry_results:
        for failure in entry["failures"]:
            counter[failure["category"]] += 1

    for artifact in app_artifacts:
        for failure in artifact["failures"]:
            counter[failure["category"]] += 1
        for record in artifact.get("records", []):
            for failure in record.get("failures", []):
                counter[failure["category"]] += 1

    total_failures = sum(counter.values())
    return {
        "entries_total": len(entry_results),
        "entries_passed": sum(1 for item in entry_results if item["status"] == "passed"),
        "entries_failed": sum(1 for item in entry_results if item["status"] == "failed"),
        "app_artifacts_total": len(app_artifacts),
        "app_artifacts_failed": sum(1 for item in app_artifacts if item["status"] == "failed"),
        "failure_count": total_failures,
        "failure_categories": dict(sorted(counter.items())),
        "status": "failed" if total_failures else "passed",
    }


def main() -> None:
    args = build_parser().parse_args()

    manifest_path = Path(args.manifest).resolve()
    public_root = Path(args.public_root).resolve()
    obfuscated_root = Path(args.obfuscated_root).resolve()
    collection_slug = str(args.collection_slug)

    manifest_payload = load_json(manifest_path)
    entries = infer_manifest_entries(manifest_payload, public_root=public_root)

    manifest_entries: dict[str, dict[str, Any]] = {}
    for entry in entries:
        composite_key = str(entry.get("composite_key") or "")
        manifest_entries[composite_key] = entry

    entry_results = [validate_entry(entry, public_root, obfuscated_root) for entry in entries]

    app_artifacts = [
        validate_catalog_artifact(
            label="public_index",
            path=public_root / INDEX_NAME,
            manifest_entries=manifest_entries,
            public_root=public_root,
            obfuscated_root=obfuscated_root,
        ),
        validate_catalog_artifact(
            label="public_app_tags",
            path=public_root / APP_TAGS_NAME,
            manifest_entries=manifest_entries,
            public_root=public_root,
            obfuscated_root=obfuscated_root,
        ),
        validate_catalog_artifact(
            label="public_app",
            path=public_root / APP_NAME,
            manifest_entries=manifest_entries,
            public_root=public_root,
            obfuscated_root=obfuscated_root,
        ),
        validate_catalog_artifact(
            label="obfuscated_index",
            path=obfuscated_root / INDEX_NAME,
            manifest_entries=manifest_entries,
            public_root=public_root,
            obfuscated_root=obfuscated_root,
        ),
        validate_catalog_artifact(
            label="obfuscated_app_tags",
            path=obfuscated_root / APP_TAGS_NAME,
            manifest_entries=manifest_entries,
            public_root=public_root,
            obfuscated_root=obfuscated_root,
        ),
        validate_catalog_artifact(
            label="obfuscated_app",
            path=obfuscated_root / APP_NAME,
            manifest_entries=manifest_entries,
            public_root=public_root,
            obfuscated_root=obfuscated_root,
        ),
    ]

    dashboard_artifacts: list[dict[str, Any]] = []

    summary = build_summary(entry_results, app_artifacts)

    report = {
        "manifest": str(manifest_path),
        "collection_slug": collection_slug,
        "public_root": str(public_root),
        "obfuscated_root": str(obfuscated_root),
        "entry_results": entry_results,
        "app_artifacts": app_artifacts,
        "dashboard_artifacts": dashboard_artifacts,
        "summary": summary,
    }

    if args.report_path:
        write_json(Path(args.report_path).resolve(), report)

    print(json.dumps(report, indent=2))
    if args.strict and summary["failure_count"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()