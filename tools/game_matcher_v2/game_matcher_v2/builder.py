import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT_DIR.parent.parent
DEFAULT_APP_JSON_PATH = REPO_ROOT / "games" / "published" / "public" / "app.json"
DEFAULT_ARTIFACTS_DIR = ROOT_DIR / "fixtures" / "derived"
DEFAULT_METADATA_PATH = DEFAULT_ARTIFACTS_DIR / "metadata.json"
SCHEMA_VERSION = 1
TAG_FAMILIES = (
    "mechanic_tags",
    "semantic_tags",
    "mood_tags",
    "setting_tags",
    "character_tags",
    "games_tags",
    "franchise_tags",
)


@dataclass
class BuildArtifactsResult:
    source_path: Path
    artifacts_dir: Path
    metadata_path: Path
    game_count: int
    source_md5: str
    rebuilt: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_app_json_path(app_json: str | Path | None = None) -> Path:
    if app_json is None:
        return DEFAULT_APP_JSON_PATH
    return Path(app_json).expanduser().resolve()


def compute_md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_tag(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def normalize_tag_list(values: Any) -> list[str]:
    if not values:
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in values:
        tag = normalize_tag(item)
        key = tag.casefold()
        if not tag or key in seen:
            continue
        seen.add(key)
        normalized.append(tag)
    return normalized


def is_artifacts_current(app_json_path: Path, artifacts_dir: Path, metadata_path: Path) -> bool:
    if not app_json_path.exists():
        raise FileNotFoundError(app_json_path)
    if not artifacts_dir.exists() or not metadata_path.exists():
        return False

    metadata = load_json(metadata_path)
    current_md5 = compute_md5(app_json_path)
    current_size = app_json_path.stat().st_size
    current_source = str(app_json_path.resolve())

    return (
        metadata.get("schema_version") == SCHEMA_VERSION
        and metadata.get("source_path") == current_source
        and metadata.get("source_md5") == current_md5
        and metadata.get("source_size") == current_size
    )


def build_artifacts(
    app_json: str | Path | None = None,
    *,
    artifacts_dir: str | Path | None = None,
    force: bool = False,
) -> BuildArtifactsResult:
    app_json_path = resolve_app_json_path(app_json)
    resolved_artifacts_dir = Path(artifacts_dir).resolve() if artifacts_dir else DEFAULT_ARTIFACTS_DIR
    metadata_path = resolved_artifacts_dir / "metadata.json"

    if not app_json_path.exists():
        raise FileNotFoundError(f"app.json source not found: {app_json_path}")

    if not force and is_artifacts_current(app_json_path, resolved_artifacts_dir, metadata_path):
        metadata = load_json(metadata_path)
        return BuildArtifactsResult(
            source_path=app_json_path,
            artifacts_dir=resolved_artifacts_dir,
            metadata_path=metadata_path,
            game_count=int(metadata.get("game_count", 0)),
            source_md5=str(metadata.get("source_md5")),
            rebuilt=False,
        )

    payload = load_json(app_json_path)
    normalized_games: list[dict[str, Any]] = []
    aggregated: dict[str, dict[str, Any]] = {family: {} for family in TAG_FAMILIES}

    for entry_id, entry_payload in payload.items():
        game_doc = {
            "doc_id": entry_id,
            "game_id": entry_payload.get("game_id"),
            "remix_id": entry_payload.get("remix_id"),
            "name": entry_payload.get("title"),
            "url": entry_payload.get("public_index_html") or entry_payload.get("index_html"),
            "cover_url": (entry_payload.get("screenshots") or [None])[0],
            "played_count": 0,
            "published_path": entry_payload.get("published_path"),
            "tags": {},
        }

        for family in TAG_FAMILIES:
            tags = normalize_tag_list(entry_payload.get(family, []))
            game_doc["tags"][family] = tags
            for tag in tags:
                key = tag.casefold()
                record = aggregated[family].setdefault(
                    key,
                    {
                        "tag": tag,
                        "count": 0,
                        "games": [],
                    },
                )
                record["count"] += 1
                record["games"].append(entry_payload.get("game_id"))

        normalized_games.append(game_doc)

    resolved_artifacts_dir.mkdir(parents=True, exist_ok=True)

    per_family_payload = {}
    for family, family_records in aggregated.items():
        entries = sorted(
            family_records.values(),
            key=lambda item: (-item["count"], item["tag"].casefold()),
        )
        family_payload = {
            "family": family,
            "tag_count": len(entries),
            "tags": entries,
        }
        write_json(resolved_artifacts_dir / f"{family}.json", family_payload)
        per_family_payload[family] = {
            "tag_count": len(entries),
            "path": str((resolved_artifacts_dir / f"{family}.json").resolve()),
        }

    normalized_payload = {
        "game_count": len(normalized_games),
        "games": normalized_games,
    }
    write_json(resolved_artifacts_dir / "normalized_games.json", normalized_payload)

    source_md5 = compute_md5(app_json_path)
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "source_path": str(app_json_path.resolve()),
        "source_md5": source_md5,
        "source_size": app_json_path.stat().st_size,
        "built_at": utc_now(),
        "game_count": len(normalized_games),
        "families": per_family_payload,
        "normalized_games_path": str((resolved_artifacts_dir / "normalized_games.json").resolve()),
    }
    write_json(metadata_path, metadata)

    return BuildArtifactsResult(
        source_path=app_json_path,
        artifacts_dir=resolved_artifacts_dir,
        metadata_path=metadata_path,
        game_count=len(normalized_games),
        source_md5=source_md5,
        rebuilt=True,
    )


def ensure_artifacts(
    app_json: str | Path | None = None,
    *,
    artifacts_dir: str | Path | None = None,
) -> BuildArtifactsResult:
    return build_artifacts(app_json=app_json, artifacts_dir=artifacts_dir, force=False)