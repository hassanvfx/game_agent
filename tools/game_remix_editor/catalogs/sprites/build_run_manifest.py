#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
DEFAULT_CATALOG_PATH = ROOT.parent / "sprites.json"
RUNS_DIR = ROOT / "runs"


@dataclass
class JobRecord:
    job_key: str
    query: str
    group: str
    asset_kind: str
    name: str
    source_url: str
    source_pathname: str
    output_relpath: str
    output_abspath: str
    style: str
    prompt: str
    composed_prompt: str
    state: str
    retry_count: int
    state_path: str
    job_file_path: str


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-") or "run"


def default_run_id() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S")


def load_catalog(catalog_path: Path) -> list[dict[str, Any]]:
    return json.loads(catalog_path.read_text())


def group_to_asset_kind(group: str) -> str:
    return {
        "sprites_transparent": "sprite_transparent",
        "backgrounds_opaque": "background_opaque",
    }[group]


def compose_prompt(group: str, prompt: str, style: str) -> str:
    parts = [
        prompt.strip(),
        (
            "Visual quality target: premium AAA-quality casual mobile game art, "
            "high polish, commercially shippable, crisp silhouette readability, "
            "clean forms, tasteful detail, vibrant but controlled color palette, "
            "professional lighting, premium game-ready finish."
        ),
    ]
    if style.strip():
        parts.append(f"Style guide: {style.strip()}.")
    if group == "sprites_transparent":
        parts.append(
            "Output requirement: isolated 2D game sprite, transparent background, no scene, no shadow catcher, centered composition, no text, no UI, no border."
        )
    elif group == "backgrounds_opaque":
        parts.append(
            "Output requirement: full 2D game background scene, opaque image, no transparency, no isolated objects, no text, no UI."
        )
    return " ".join(parts)


def build_job_key(pathname: str) -> str:
    path = Path(pathname.lstrip("/"))
    without_suffix = path.with_suffix("")
    return without_suffix.as_posix()


def make_job_record(run_dir: Path, query: str, group: str, asset: dict[str, Any]) -> JobRecord:
    parsed = urlparse(asset["url"])
    pathname = parsed.path
    relpath = pathname.lstrip("/")
    output_path = run_dir / relpath
    state_path = run_dir / ".state" / f"{Path(relpath).with_suffix('')}.json"
    job_file_path = run_dir / ".jobs" / f"{Path(relpath).with_suffix('')}.json"

    return JobRecord(
        job_key=build_job_key(pathname),
        query=query,
        group=group,
        asset_kind=group_to_asset_kind(group),
        name=asset["name"],
        source_url=asset["url"],
        source_pathname=pathname,
        output_relpath=relpath,
        output_abspath=str(output_path),
        style=asset.get("style", ""),
        prompt=asset["prompt"],
        composed_prompt=compose_prompt(group, asset["prompt"], asset.get("style", "")),
        state="pending",
        retry_count=0,
        state_path=str(state_path),
        job_file_path=str(job_file_path),
    )


def build_manifest(run_dir: Path, catalog_path: Path) -> list[JobRecord]:
    catalog = load_catalog(catalog_path)
    records: list[JobRecord] = []

    for entry in catalog:
        query = entry["query"]
        for group in ("sprites_transparent", "backgrounds_opaque"):
            for asset in entry.get(group, []):
                records.append(make_job_record(run_dir, query, group, asset))

    records.sort(key=lambda item: item.job_key)
    return records


def create_run_scaffold(run_dir: Path) -> None:
    (run_dir / "assets").mkdir(parents=True, exist_ok=True)
    (run_dir / ".jobs").mkdir(parents=True, exist_ok=True)
    (run_dir / ".state").mkdir(parents=True, exist_ok=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    (run_dir / "fixtures").mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a timestamped/named sprites run scaffold and flat manifest."
    )
    parser.add_argument(
        "--run-name",
        help="Optional run name. If omitted, a timestamped run id is used.",
    )
    parser.add_argument(
        "--sample-job-key",
        default="assets/images/sprites/runner/player_runner",
        help="Job key to extract into manifest.sample.json for one-job testing.",
    )
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_CATALOG_PATH),
        help="Path to the source catalog JSON file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_id = slugify(args.run_name) if args.run_name else default_run_id()
    run_dir = RUNS_DIR / run_id
    catalog_path = Path(args.catalog).resolve()

    create_run_scaffold(run_dir)
    manifest = build_manifest(run_dir, catalog_path)

    write_json(
        run_dir / "run.json",
        {
            "run_id": run_id,
            "created_at": datetime.now().astimezone().isoformat(),
            "source_catalog": str(catalog_path),
            "run_dir": str(run_dir),
            "job_count": len(manifest),
            "sample_job_key": args.sample_job_key,
        },
    )
    write_json(run_dir / "manifest.json", [asdict(item) for item in manifest])

    sample = [asdict(item) for item in manifest if item.job_key == args.sample_job_key]
    write_json(run_dir / "manifest.sample.json", sample)

    print(json.dumps(
        {
            "ok": True,
            "run_id": run_id,
            "run_dir": str(run_dir),
            "job_count": len(manifest),
            "sample_job_key": args.sample_job_key,
            "sample_count": len(sample),
            "manifest": str(run_dir / "manifest.json"),
            "sample_manifest": str(run_dir / "manifest.sample.json"),
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()