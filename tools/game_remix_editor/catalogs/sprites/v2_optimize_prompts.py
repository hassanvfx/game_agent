#!/usr/bin/env python3
"""
Resumable V2 prompt optimizer.

This worker optimizes sprites_expanded_v2.json with the neighboring ../../kie-api
LLM CLI. The current V2 catalog is a flat 600-asset list, so the worker groups
assets by their URL taxonomy folder, processes 10 groups per job, validates that
names/URLs/order are preserved, atomically merges successful chunks, saves state
after every chunk, retries failures, and refreshes the V2 dashboard after each
successful merge.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent

DEFAULT_CATALOG = REPO_ROOT / "sprites_expanded_v2.json"
DEFAULT_WORK_DIR = ROOT / "v2_prompt_optimize"
DEFAULT_STATE = DEFAULT_WORK_DIR / "state.json"
DEFAULT_FAILURES = DEFAULT_WORK_DIR / "failures.json"
DEFAULT_KIE_ROOT = REPO_ROOT / ".." / ".." / "kie-api"
DEFAULT_KIE_CLI = DEFAULT_KIE_ROOT / ".venv" / "bin" / "kie-cli"
DEFAULT_DASHBOARD_SCRIPT = ROOT / "render_dashboard.py"
DEFAULT_DASHBOARD_OUTPUT = ROOT / "dashboard_v2.html"
DEFAULT_LIVE_DIR = ROOT / "live_v2"
DEFAULT_DASHBOARD_TITLE = "Sprites Taxonomy Dashboard V2"

VALID_STATUSES = {"pending", "running", "completed", "failed", "retrying", "skipped"}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return copy.deepcopy(default)
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


def atomic_write_catalog(path: Path, catalog: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(catalog, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with tmp.open("r", encoding="utf-8") as fh:
            parsed = json.load(fh)
        if not isinstance(parsed, list) or len(parsed) != len(catalog):
            raise ValueError("catalog temp file failed full parse/length validation")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def asset_kind_from_url(url: str) -> str:
    path = urlparse(url).path
    if "/backgrounds/" in path:
        return "backgrounds_opaque"
    return "sprites_transparent"


def group_slug_from_url(url: str) -> str:
    parts = [part for part in urlparse(url).path.split("/") if part]
    if len(parts) < 2:
        return "unknown"
    return parts[-2]


def title_from_slug(slug: str) -> str:
    return slug.replace("_", " ")


def catalog_groups(catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
    for index, asset in enumerate(catalog):
        slug = group_slug_from_url(str(asset.get("url", "")))
        group = grouped.setdefault(
            slug,
            {
                "query": title_from_slug(slug),
                "slug": slug,
                "indices": [],
                "assets": [],
            },
        )
        group["indices"].append(index)
        group["assets"].append(
            {
                "index": index,
                "kind": asset_kind_from_url(str(asset.get("url", ""))),
                "name": asset.get("name", ""),
                "url": asset.get("url", ""),
                "style": asset.get("style", ""),
                "usage": asset.get("usage", ""),
                "prompt": asset.get("prompt", ""),
            }
        )
    return list(grouped.values())


def chunk_ranges(total_groups: int, chunk_size_groups: int) -> List[Tuple[int, int, int]]:
    ranges = []
    chunk_id = 1
    for start in range(0, total_groups, chunk_size_groups):
        end = min(start + chunk_size_groups, total_groups)
        ranges.append((chunk_id, start, end))
        chunk_id += 1
    return ranges


def chunk_key(chunk_id: int) -> str:
    return f"chunk_{chunk_id:03d}"


def default_state(catalog_path: Path, chunk_size: int, groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    state = {
        "version": 2,
        "mode": "flat_url_groups",
        "catalog_path": str(catalog_path),
        "chunk_size_query_groups": chunk_size,
        "total_query_groups": len(groups),
        "total_assets": sum(len(group["assets"]) for group in groups),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "chunks": {},
    }
    for cid, start, end in chunk_ranges(len(groups), chunk_size):
        key = chunk_key(cid)
        selected = groups[start:end]
        indices = [idx for group in selected for idx in group["indices"]]
        state["chunks"][key] = {
            "chunk_id": cid,
            "start_group_index": start,
            "end_group_index_exclusive": end,
            "query_slugs": [group["slug"] for group in selected],
            "asset_indices": indices,
            "status": "pending",
            "attempts": 0,
            "max_retries": None,
            "last_started_at": None,
            "last_finished_at": None,
            "last_error": None,
            "prompt_file": None,
            "input_file": None,
            "raw_response_file": None,
            "output_file": None,
            "merged_at": None,
        }
    return state


def reconcile_state(
    state: Optional[Dict[str, Any]],
    catalog: List[Dict[str, Any]],
    catalog_path: Path,
    chunk_size: int,
    max_retries: int,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    groups = catalog_groups(catalog)

    # Rebuild any old state created against the wrong flat-asset chunk model.
    if not state or state.get("version") != 2 or state.get("mode") != "flat_url_groups":
        state = default_state(catalog_path, chunk_size, groups)

    old_chunks = state.get("chunks", {})
    expected: Dict[str, Dict[str, Any]] = {}
    for cid, start, end in chunk_ranges(len(groups), chunk_size):
        key = chunk_key(cid)
        selected = groups[start:end]
        indices = [idx for group in selected for idx in group["indices"]]
        existing = old_chunks.get(key, {})
        status = existing.get("status", "pending")
        if status not in VALID_STATUSES:
            status = "pending"
        expected[key] = {
            "chunk_id": cid,
            "start_group_index": start,
            "end_group_index_exclusive": end,
            "query_slugs": [group["slug"] for group in selected],
            "asset_indices": indices,
            "status": status,
            "attempts": int(existing.get("attempts", 0) or 0),
            "max_retries": max_retries,
            "last_started_at": existing.get("last_started_at"),
            "last_finished_at": existing.get("last_finished_at"),
            "last_error": existing.get("last_error"),
            "prompt_file": existing.get("prompt_file"),
            "input_file": existing.get("input_file"),
            "raw_response_file": existing.get("raw_response_file"),
            "output_file": existing.get("output_file"),
            "merged_at": existing.get("merged_at"),
        }

    state.update(
        {
            "version": 2,
            "mode": "flat_url_groups",
            "catalog_path": str(catalog_path),
            "chunk_size_query_groups": chunk_size,
            "total_query_groups": len(groups),
            "total_assets": len(catalog),
            "updated_at": now_iso(),
            "chunks": expected,
        }
    )
    state.setdefault("created_at", now_iso())
    return state, groups


def build_llm_prompt(chunk_groups: List[Dict[str, Any]], chunk_id: int) -> str:
    payload = []
    for group in chunk_groups:
        payload_group = {
            "query": group["query"],
            "slug": group["slug"],
            "assets": [],
        }
        for asset in group["assets"]:
            payload_group["assets"].append(
                {
                    "index": asset["index"],
                    "kind": asset["kind"],
                    "name": asset["name"],
                }
            )
        payload.append(payload_group)

    return f"""You are optimizing a mobile game asset prompt catalog for GPT Image 2 production.

TASK
Rewrite the `usage` and `prompt` for every asset in this compact JSON chunk.
The input contains up to 10 query groups and only includes query, slug, kind, index, and name to keep the KIE request small.
Return a flat patch list, not the input schema.

OUTPUT FORMAT
Return VALID JSON ONLY: a flat array of patch objects.
No markdown fences. No commentary. No trailing prose.

EACH PATCH OBJECT MUST HAVE EXACTLY:
- "index": same integer asset index from input
- "name": same asset name from input
- "usage": improved usage sentence
- "prompt": improved image-generation prompt

RETURN EXAMPLE
[
  {{"index": 123, "name": "player_avatar", "usage": "...", "prompt": "..."}}
]

HARD RULES
- Return exactly one patch per input asset.
- Preserve every `index` exactly.
- Preserve every `name` exactly.
- Do not return URLs.
- Do not return style.
- Infer creative visual direction from query, slug, kind, and asset name.
- Do not add extra fields.
- Do not reorder requirements by inventing assets.
- Rewrite/improve every `usage`.
- Rewrite/improve every `prompt`.

USAGE RULES
- One concise sentence.
- Explain the asset's functional role in the game loop.
- Mention how it is used by the player, progression, level, combat, collection, building, simulation, or reward loop.
- Do not describe art style in `usage`.

PROMPT RULES FOR kind == "sprites_transparent"
- Request one isolated transparent-background sprite.
- Include concrete silhouette, materials, palette, shape language, pose/view angle where relevant, and genre-specific details.
- Avoid text, logos, watermarks, UI labels, full scenes, cropped edges, and background environments.
- Make it production-ready for casual mobile game art.
- Include transparent-background constraints.

PROMPT RULES FOR kind == "backgrounds_opaque"
- Request a complete opaque gameplay background/environment.
- Include readable gameplay layout, depth layers, focal staging, lighting, mood, genre-specific props, and safe space for gameplay.
- Avoid text, logos, watermarks, and transparent-background instructions.
- Make it production-ready for casual mobile game art.

CREATIVITY BAR
Make each prompt feel custom to the query and asset name. Replace generic phrasing
with vivid, concrete visual direction. Keep prompts practical and image-model ready.

BANNED GENERIC PHRASES
Do not use these phrases: "core task object", "interactive environment",
"simulator character", "high quality asset", "game asset".

Return the optimized flat patch JSON array for chunk {chunk_id:03d}.

INPUT JSON:
{json.dumps(payload, indent=2, ensure_ascii=False)}
"""


def split_groups_by_asset_count(groups: List[Dict[str, Any]], asset_batch_size: int) -> List[List[Dict[str, Any]]]:
    batches: List[List[Dict[str, Any]]] = []
    current_groups: List[Dict[str, Any]] = []
    current_count = 0

    for group in groups:
        group_assets = list(group.get("assets", []))
        for offset in range(0, len(group_assets), asset_batch_size):
            piece = copy.deepcopy(group)
            piece["assets"] = group_assets[offset : offset + asset_batch_size]
            if not piece["assets"]:
                continue

            if current_groups and current_count + len(piece["assets"]) > asset_batch_size:
                batches.append(current_groups)
                current_groups = []
                current_count = 0

            current_groups.append(piece)
            current_count += len(piece["assets"])

            if current_count >= asset_batch_size:
                batches.append(current_groups)
                current_groups = []
                current_count = 0

    if current_groups:
        batches.append(current_groups)

    return batches


def run_kie_llm(
    kie_cli: Path,
    kie_root: Path,
    prompt_file: Path,
    timeout: int,
    reasoning_effort: str,
    request_timeout: float,
    max_completion_tokens: int,
) -> Tuple[int, str, str]:
    cmd = [
        str(kie_cli),
        "llm",
        "gpt-5-2",
        "--prompt-file",
        str(prompt_file),
        "--reasoning-effort",
        reasoning_effort,
        "--request-timeout",
        str(request_timeout),
        "--max-completion-tokens",
        str(max_completion_tokens),
        "--json",
    ]
    proc = subprocess.run(cmd, cwd=str(kie_root), text=True, capture_output=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def extract_json_from_text(text: str) -> Any:
    text = text.strip()
    if not text:
        raise ValueError("empty LLM response")

    try:
        return unwrap_llm_json(json.loads(text))
    except json.JSONDecodeError:
        pass

    fence = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        return extract_json_from_text(fence.group(1))

    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])

    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        return unwrap_llm_json(json.loads(text[brace_start : brace_end + 1]))

    raise ValueError("could not extract JSON list from LLM response")


def unwrap_llm_json(parsed: Any) -> Any:
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        for key in ("text", "content", "message", "response", "result", "output", "answer"):
            value = parsed.get(key)
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                return extract_json_from_text(value)
        choices = parsed.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                if isinstance(first.get("text"), str):
                    return extract_json_from_text(first["text"])
                message = first.get("message")
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    return extract_json_from_text(message["content"])
        data = parsed.get("data")
        if isinstance(data, (dict, list)):
            return unwrap_llm_json(data)
    raise ValueError("LLM response JSON envelope did not contain a JSON list")


def expected_assets_by_index(original: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    expected_assets: Dict[int, Dict[str, Any]] = {}
    for group in original:
        for asset in group.get("assets", []):
            expected_assets[int(asset["index"])] = asset
    return expected_assets


def normalize_patches(original: List[Dict[str, Any]], optimized: Any) -> Any:
    if not isinstance(optimized, list):
        return optimized

    expected_assets = expected_assets_by_index(original)
    normalized = copy.deepcopy(optimized)

    for patch in normalized:
        if not isinstance(patch, dict):
            continue
        try:
            index = int(patch.get("index"))
        except Exception:
            continue

        before_asset = expected_assets.get(index)
        if not before_asset:
            continue

        prompt = str(patch.get("prompt", "")).strip()
        lowered = prompt.lower()

        if before_asset.get("kind") == "sprites_transparent" and prompt and "transparent" not in lowered:
            patch["prompt"] = prompt.rstrip(".") + ", isolated on a transparent background."

        if before_asset.get("kind") == "backgrounds_opaque" and "transparent background" in lowered:
            patch["prompt"] = re.sub(
                r",?\s*(?:isolated\s+)?(?:on\s+a\s+)?transparent background\.?",
                "",
                prompt,
                flags=re.IGNORECASE,
            ).strip()
            prompt = str(patch.get("prompt", "")).strip()

        banned_replacements = {
            "core task object": "primary objective prop",
            "interactive environment": "readable gameplay scene",
            "simulator character": "simulation avatar",
            "high quality asset": "polished production sprite",
            "game asset": "game-ready visual element",
        }
        for banned, replacement in banned_replacements.items():
            prompt = re.sub(re.escape(banned), replacement, prompt, flags=re.IGNORECASE)

        patch["prompt"] = prompt.strip()

    return normalized


def validate_groups(original: List[Dict[str, Any]], optimized: Any) -> List[str]:
    errors: List[str] = []
    expected_assets = expected_assets_by_index(original)

    if not isinstance(optimized, list):
        return ["optimized response is not a JSON list"]
    if len(optimized) != len(expected_assets):
        return [f"patch count changed: expected {len(expected_assets)}, got {len(optimized)}"]

    seen: set[int] = set()
    allowed_keys = {"index", "name", "usage", "prompt"}

    for pi, patch in enumerate(optimized):
        prefix = f"patch[{pi}]"
        if not isinstance(patch, dict):
            errors.append(f"{prefix} is not an object")
            continue

        extra = set(patch.keys()) - allowed_keys
        missing = allowed_keys - set(patch.keys())
        if extra:
            errors.append(f"{prefix} has extra keys: {sorted(extra)}")
        if missing:
            errors.append(f"{prefix} missing keys: {sorted(missing)}")

        try:
            index = int(patch.get("index"))
        except Exception:
            errors.append(f"{prefix}.index is not an integer")
            continue

        if index in seen:
            errors.append(f"{prefix}.index duplicated: {index}")
            continue
        seen.add(index)

        before_asset = expected_assets.get(index)
        if before_asset is None:
            errors.append(f"{prefix}.index not in input chunk: {index}")
            continue

        if patch.get("name") != before_asset.get("name"):
            errors.append(f"{prefix}.name changed for index {index}")

        usage = str(patch.get("usage", "")).strip()
        prompt = str(patch.get("prompt", "")).strip()
        before_prompt = str(before_asset.get("prompt", "")).strip()
        lowered = prompt.lower()

        if not usage:
            errors.append(f"{prefix}.usage is empty")
        if not prompt:
            errors.append(f"{prefix}.prompt is empty")
        if len(prompt) < 90:
            errors.append(f"{prefix}.prompt is too short ({len(prompt)} chars)")
        if prompt == before_prompt:
            errors.append(f"{prefix}.prompt was not changed")
        if "http://" in prompt or "https://" in prompt:
            errors.append(f"{prefix}.prompt contains URL text")

        for banned in (
            "core task object",
            "interactive environment",
            "simulator character",
            "high quality asset",
            "game asset",
        ):
            if banned in lowered:
                errors.append(f"{prefix}.prompt contains banned phrase: {banned}")

        if before_asset.get("kind") == "sprites_transparent" and "transparent" not in lowered:
            errors.append(f"{prefix}.sprite prompt must mention transparent background")
        if before_asset.get("kind") == "backgrounds_opaque" and "transparent background" in lowered:
            errors.append(f"{prefix}.background prompt incorrectly mentions transparent background")

    missing_indices = sorted(set(expected_assets) - seen)
    if missing_indices:
        errors.append(f"missing patch indices: {missing_indices[:20]}")

    return errors


def merge_optimized_groups(catalog: List[Dict[str, Any]], optimized_groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = copy.deepcopy(catalog)
    for patch in optimized_groups:
        index = int(patch["index"])
        merged[index]["usage"] = str(patch.get("usage", "")).strip()
        merged[index]["prompt"] = str(patch.get("prompt", "")).strip()
    return merged


def validate_full_catalog(catalog: List[Dict[str, Any]]) -> None:
    for index, asset in enumerate(catalog):
        for key in ("name", "url", "style", "usage", "prompt"):
            if key not in asset:
                raise ValueError(f"asset[{index}] missing {key}")
        if not str(asset.get("usage", "")).strip():
            raise ValueError(f"asset[{index}] has empty usage")
        if not str(asset.get("prompt", "")).strip():
            raise ValueError(f"asset[{index}] has empty prompt")


def refresh_dashboard(catalog_path: Path, live_dir: Path, output_path: Path, dashboard_script: Path, title: str) -> None:
    cmd = [
        sys.executable,
        str(dashboard_script),
        "--catalog",
        str(catalog_path),
        "--live-dir",
        str(live_dir),
        "--output",
        str(output_path),
        "--title",
        title,
    ]
    subprocess.run(cmd, cwd=str(REPO_ROOT), check=True)


def summarize_state(state: Dict[str, Any]) -> Dict[str, int]:
    counts = {status: 0 for status in sorted(VALID_STATUSES)}
    for chunk in state.get("chunks", {}).values():
        status = chunk.get("status", "pending")
        counts[status] = counts.get(status, 0) + 1
    return counts


def append_failure(failures_path: Path, entry: Dict[str, Any]) -> None:
    failures = load_json(failures_path, default=[])
    if not isinstance(failures, list):
        failures = []
    failures.append(entry)
    write_json(failures_path, failures)


def select_chunks(
    state: Dict[str, Any],
    explicit_chunk: Optional[int],
    all_chunks: bool,
    resume: bool,
    failed_only: bool,
    max_retries: int,
) -> List[str]:
    chunks = state["chunks"]
    if explicit_chunk is not None:
        key = chunk_key(explicit_chunk)
        if key not in chunks:
            raise ValueError(f"chunk {explicit_chunk} does not exist")
        return [key]

    keys = sorted(chunks.keys())
    if failed_only:
        return [
            key
            for key in keys
            if chunks[key]["status"] in {"failed", "retrying"} and int(chunks[key].get("attempts", 0) or 0) < max_retries
        ]

    if all_chunks or resume:
        return [
            key
            for key in keys
            if chunks[key]["status"] != "completed"
            and not (
                chunks[key]["status"] in {"failed", "retrying"}
                and int(chunks[key].get("attempts", 0) or 0) >= max_retries
            )
        ]

    for key in keys:
        attempts = int(chunks[key].get("attempts", 0) or 0)
        if chunks[key]["status"] == "pending":
            return [key]
        if chunks[key]["status"] in {"failed", "retrying"} and attempts < max_retries:
            return [key]
    return []


def process_chunk(args: argparse.Namespace, state: Dict[str, Any], groups: List[Dict[str, Any]], key: str) -> bool:
    catalog_path = Path(args.catalog)
    jobs_dir = Path(args.work_dir) / "jobs"
    state_path = Path(args.state)
    failures_path = Path(args.failures)

    catalog = load_json(catalog_path)
    chunk_state = state["chunks"][key]
    cid = int(chunk_state["chunk_id"])
    start = int(chunk_state["start_group_index"])
    end = int(chunk_state["end_group_index_exclusive"])
    original_groups = copy.deepcopy(groups[start:end])

    previous_attempts = int(chunk_state.get("attempts", 0) or 0)
    if previous_attempts >= args.max_retries and not args.force:
        chunk_state["status"] = "skipped"
        chunk_state["last_error"] = f"retry budget exhausted ({previous_attempts}/{args.max_retries})"
        state["updated_at"] = now_iso()
        write_json(state_path, state)
        return False

    attempt_number = previous_attempts + 1
    jobs_dir.mkdir(parents=True, exist_ok=True)
    base = jobs_dir / f"{key}_attempt_{attempt_number:02d}"
    input_file = base.with_name(base.name + "_input.json")
    prompt_file = base.with_name(base.name + "_prompt.txt")
    raw_file = base.with_name(base.name + "_raw_response.txt")
    output_file = base.with_name(base.name + "_optimized.json")
    error_file = base.with_name(base.name + "_error.txt")

    asset_batches = split_groups_by_asset_count(original_groups, args.asset_batch_size)
    write_json(input_file, original_groups)

    if args.dry_run:
        for batch_index, batch_groups in enumerate(asset_batches, start=1):
            batch_prompt_file = base.with_name(base.name + f"_batch_{batch_index:02d}_prompt.txt")
            batch_input_file = base.with_name(base.name + f"_batch_{batch_index:02d}_input.json")
            write_json(batch_input_file, batch_groups)
            batch_prompt_file.write_text(build_llm_prompt(batch_groups, cid), encoding="utf-8")

        chunk_state.update(
            {
                "status": chunk_state.get("status", "pending") if chunk_state.get("status") != "running" else "pending",
                "attempts": previous_attempts,
                "max_retries": args.max_retries,
                "last_error": "dry-run scaffolded job files; KIE LLM call skipped",
                "prompt_file": str(base.with_name(base.name + "_batch_01_prompt.txt")),
                "input_file": str(input_file),
                "raw_response_file": str(raw_file),
                "output_file": str(output_file),
            }
        )
        state["updated_at"] = now_iso()
        write_json(state_path, state)
        print(f"[DRY-RUN] wrote {input_file} and {len(asset_batches)} batch prompt files")
        return True

    chunk_state.update(
        {
            "status": "running" if previous_attempts == 0 else "retrying",
            "attempts": attempt_number,
            "max_retries": args.max_retries,
            "last_started_at": now_iso(),
            "last_finished_at": None,
            "last_error": None,
            "prompt_file": str(base.with_name(base.name + "_batch_01_prompt.txt")),
            "input_file": str(input_file),
            "raw_response_file": str(raw_file),
            "output_file": str(output_file),
        }
    )
    state["updated_at"] = now_iso()
    write_json(state_path, state)

    try:
        optimized: List[Dict[str, Any]] = []
        for batch_index, batch_groups in enumerate(asset_batches, start=1):
            batch_prompt_file = base.with_name(base.name + f"_batch_{batch_index:02d}_prompt.txt")
            batch_input_file = base.with_name(base.name + f"_batch_{batch_index:02d}_input.json")
            batch_raw_file = base.with_name(base.name + f"_batch_{batch_index:02d}_raw_response.txt")
            batch_output_file = base.with_name(base.name + f"_batch_{batch_index:02d}_optimized.json")

            write_json(batch_input_file, batch_groups)
            batch_prompt_file.write_text(build_llm_prompt(batch_groups, cid), encoding="utf-8")

            returncode, stdout, stderr = run_kie_llm(
                kie_cli=Path(args.kie_cli),
                kie_root=Path(args.kie_root),
                prompt_file=batch_prompt_file,
                timeout=args.timeout,
                reasoning_effort=args.reasoning_effort,
                request_timeout=args.request_timeout,
                max_completion_tokens=args.max_completion_tokens,
            )
            batch_raw_file.write_text(stdout + ("\n\nSTDERR:\n" + stderr if stderr else ""), encoding="utf-8")

            if returncode != 0:
                raise RuntimeError(
                    f"KIE LLM exited {returncode} on batch {batch_index}/{len(asset_batches)}: "
                    f"{stderr.strip() or stdout.strip()}"
                )

            batch_optimized = normalize_patches(batch_groups, extract_json_from_text(stdout))
            errors = validate_groups(batch_groups, batch_optimized)
            if errors:
                raise ValueError(
                    f"validation failed on batch {batch_index}/{len(asset_batches)}:\n- "
                    + "\n- ".join(errors[:100])
                )

            write_json(batch_output_file, batch_optimized)
            optimized.extend(batch_optimized)

        optimized = normalize_patches(original_groups, optimized)
        errors = validate_groups(original_groups, optimized)
        if errors:
            raise ValueError("aggregate validation failed:\n- " + "\n- ".join(errors[:100]))

        write_json(output_file, optimized)

        latest_catalog = load_json(catalog_path)
        merged = merge_optimized_groups(latest_catalog, optimized)
        validate_full_catalog(merged)
        atomic_write_catalog(catalog_path, merged)

        if args.refresh_dashboard:
            refresh_dashboard(
                catalog_path=catalog_path,
                live_dir=Path(args.live_dir),
                output_path=Path(args.dashboard_output),
                dashboard_script=Path(args.dashboard_script),
                title=args.dashboard_title,
            )

        chunk_state.update(
            {
                "status": "completed",
                "last_finished_at": now_iso(),
                "last_error": None,
                "merged_at": now_iso(),
            }
        )
        state["updated_at"] = now_iso()
        write_json(state_path, state)
        return True

    except Exception as exc:
        error_text = f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()}"
        error_file.write_text(error_text, encoding="utf-8")
        terminal = attempt_number >= args.max_retries
        chunk_state.update(
            {
                "status": "failed" if terminal else "retrying",
                "last_finished_at": now_iso(),
                "last_error": str(exc),
            }
        )
        state["updated_at"] = now_iso()
        write_json(state_path, state)
        append_failure(
            failures_path,
            {
                "at": now_iso(),
                "chunk": key,
                "chunk_id": cid,
                "attempt": attempt_number,
                "terminal": terminal,
                "error": str(exc),
                "error_file": str(error_file),
                "input_file": str(input_file),
                "prompt_file": str(prompt_file),
                "raw_response_file": str(raw_file),
            },
        )
        print(f"[FAIL] {key} attempt {attempt_number}: {exc}", file=sys.stderr)
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resumable KIE LLM optimizer for sprites_expanded_v2.json")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Flat V2 catalog JSON to optimize in-place")
    parser.add_argument("--work-dir", default=str(DEFAULT_WORK_DIR), help="Prompt optimization work directory")
    parser.add_argument("--state", default=str(DEFAULT_STATE), help="State JSON path")
    parser.add_argument("--failures", default=str(DEFAULT_FAILURES), help="Failures JSON path")
    parser.add_argument("--chunk-size", type=int, default=10, help="Query groups per LLM job")
    parser.add_argument("--chunk", type=int, help="Run one 1-based chunk id")
    parser.add_argument("--all", action="store_true", help="Run every pending/retryable chunk")
    parser.add_argument("--resume", action="store_true", help="Skip completed chunks and continue pending/retryable chunks")
    parser.add_argument("--failed-only", action="store_true", help="Run only failed/retrying chunks with retry budget left")
    parser.add_argument("--max-retries", type=int, default=3, help="Max attempts per chunk")
    parser.add_argument("--force", action="store_true", help="Allow explicit chunk run even if retry budget is exhausted")
    parser.add_argument("--timeout", type=int, default=1200, help="Local subprocess timeout seconds")
    parser.add_argument("--request-timeout", type=float, default=300, help="KIE HTTP request timeout seconds")
    parser.add_argument("--max-completion-tokens", type=int, default=12000, help="KIE LLM output token budget")
    parser.add_argument("--asset-batch-size", type=int, default=12, help="Assets per KIE LLM request inside each chunk")
    parser.add_argument("--sleep", type=float, default=1.0, help="Sleep seconds between chunks")
    parser.add_argument("--kie-root", default=str(DEFAULT_KIE_ROOT.resolve()), help="Neighbor kie-api root")
    parser.add_argument("--kie-cli", default=str(DEFAULT_KIE_CLI.resolve()), help="kie-cli executable path")
    parser.add_argument("--reasoning-effort", choices=["low", "high"], default="high")
    parser.add_argument("--dashboard-script", default=str(DEFAULT_DASHBOARD_SCRIPT))
    parser.add_argument("--dashboard-output", default=str(DEFAULT_DASHBOARD_OUTPUT))
    parser.add_argument("--live-dir", default=str(DEFAULT_LIVE_DIR))
    parser.add_argument("--dashboard-title", default=DEFAULT_DASHBOARD_TITLE)
    parser.add_argument("--no-refresh-dashboard", dest="refresh_dashboard", action="store_false")
    parser.add_argument("--dry-run", action="store_true", help="Write job/state scaffolding but do not call KIE")
    parser.set_defaults(refresh_dashboard=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    catalog_path = Path(args.catalog)
    state_path = Path(args.state)
    failures_path = Path(args.failures)
    work_dir = Path(args.work_dir)
    jobs_dir = work_dir / "jobs"

    if args.chunk_size <= 0:
        print("--chunk-size must be positive", file=sys.stderr)
        return 2
    if args.max_retries <= 0:
        print("--max-retries must be positive", file=sys.stderr)
        return 2
    if not catalog_path.exists():
        print(f"catalog not found: {catalog_path}", file=sys.stderr)
        return 2
    if not Path(args.kie_root).exists():
        print(f"kie root not found: {args.kie_root}", file=sys.stderr)
        return 2
    if not Path(args.kie_cli).exists() or not os.access(args.kie_cli, os.X_OK):
        print(f"kie cli not found/executable: {args.kie_cli}", file=sys.stderr)
        return 2

    work_dir.mkdir(parents=True, exist_ok=True)
    jobs_dir.mkdir(parents=True, exist_ok=True)

    catalog = load_json(catalog_path)
    if not isinstance(catalog, list):
        print(f"catalog is not a JSON list: {catalog_path}", file=sys.stderr)
        return 2

    validate_full_catalog(catalog)

    state = load_json(state_path, default=None)
    state, groups = reconcile_state(state, catalog, catalog_path, args.chunk_size, args.max_retries)
    write_json(state_path, state)
    if not failures_path.exists():
        write_json(failures_path, [])

    selected = select_chunks(
        state=state,
        explicit_chunk=args.chunk,
        all_chunks=args.all,
        resume=args.resume,
        failed_only=args.failed_only,
        max_retries=args.max_retries,
    )

    if not selected:
        counts = summarize_state(state)
        print(f"No chunks selected. State: {counts}")
        return 0

    print(f"Catalog assets: {len(catalog)}")
    print(f"Query groups: {len(groups)}")
    print(f"Chunk size: {args.chunk_size} groups")
    print(f"Selected chunks: {', '.join(selected)}")

    successes = 0
    failures = 0

    for index, key in enumerate(selected, start=1):
        state = load_json(state_path, default=state)
        state, groups = reconcile_state(state, load_json(catalog_path), catalog_path, args.chunk_size, args.max_retries)
        print(f"[{index}/{len(selected)}] Processing {key}")
        ok = process_chunk(args, state, groups, key)
        if ok:
            successes += 1
            print(f"[OK] {key}")
        else:
            failures += 1
        if index < len(selected) and args.sleep > 0:
            time.sleep(args.sleep)

    final_state = load_json(state_path, default=state)
    counts = summarize_state(final_state)
    print(json.dumps({"successes": successes, "failures": failures, "state": counts}, indent=2))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())