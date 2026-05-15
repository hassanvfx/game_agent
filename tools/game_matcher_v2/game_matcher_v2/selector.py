from __future__ import annotations

import json
import os
import signal
import subprocess
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT_DIR.parent.parent
DEFAULT_RUNS_DIR = ROOT_DIR / "tmp" / "selector_runs"
DEFAULT_MODEL = "gpt-5.5"
DEFAULT_TIMEOUT_SECONDS = 1800
MAX_RANK = 5

PROJECTED_PRICING_USD_PER_MILLION = {
    "inputTokens": 5.00,
    "cacheReadTokens": 0.50,
    "outputTokens": 30.00,
    "cacheWriteTokens": 0.00,
}

TAG_FAMILIES = (
    "mechanic_tags",
    "semantic_tags",
    "mood_tags",
    "setting_tags",
    "character_tags",
    "games_tags",
    "franchise_tags",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def iso_to_timestamp(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def prompt_slug(prompt: str) -> str:
    return "-".join(prompt.lower().split())[:48] or "query"


def stream_reader(stream, destination: Path, sink: list[str]) -> None:
    with destination.open("w", encoding="utf-8") as handle:
        for line in iter(stream.readline, ""):
            handle.write(line)
            handle.flush()
            sink.append(line)
    stream.close()


@dataclass
class SelectorExecutionResult:
    command: list[str]
    pid: int
    returncode: int
    stdout_text: str
    stderr_text: str
    timed_out: bool
    started_at: str
    finished_at: str
    duration_seconds: float
    run_result_event: dict[str, Any] | None

    @property
    def status(self) -> str:
        if self.timed_out:
            return "timeout"
        return "completed" if self.returncode == 0 else "failed"


@dataclass(frozen=True)
class SelectorPaths:
    run_root: Path
    workspace: Path
    selector_prompt: Path
    selector_result_contract: Path
    selector_selected_tags: Path
    selector_stdout: Path
    selector_stderr: Path
    selector_invocation: Path
    selector_result: Path
    selector_usage: Path
    selector_workspace_manifest: Path


@dataclass
class SelectorRunResult:
    run_root: Path
    workspace: Path
    selected_tags: dict[str, list[dict[str, Any]]]
    validated_selected_tags: dict[str, list[dict[str, Any]]]
    execution: SelectorExecutionResult


class SelectorError(RuntimeError):
    pass


def parse_cline_run_result_event(stdout_text: str) -> dict[str, Any] | None:
    last_run_result: dict[str, Any] | None = None
    for raw_line in stdout_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and payload.get("type") == "run_result":
            last_run_result = payload
    return last_run_result


def normalize_cline_usage_summary(run_result_event: dict[str, Any] | None) -> dict[str, Any] | None:
    if not run_result_event:
        return None
    aggregate_usage = run_result_event.get("aggregateUsage")
    usage = run_result_event.get("usage")
    usage_payload = aggregate_usage if isinstance(aggregate_usage, dict) else usage if isinstance(usage, dict) else {}
    model_payload = run_result_event.get("model") if isinstance(run_result_event.get("model"), dict) else {}
    normalized_usage = {
        "inputTokens": usage_payload.get("inputTokens", 0),
        "outputTokens": usage_payload.get("outputTokens", 0),
        "cacheReadTokens": usage_payload.get("cacheReadTokens", 0),
        "cacheWriteTokens": usage_payload.get("cacheWriteTokens", 0),
        "totalCost": usage_payload.get("totalCost", 0),
    }
    projected_cost_breakdown = {
        key: round((normalized_usage.get(key, 0) / 1_000_000) * rate, 6)
        for key, rate in PROJECTED_PRICING_USD_PER_MILLION.items()
    }
    projected_cost_total = round(sum(projected_cost_breakdown.values()), 6)
    total_tokens = normalized_usage["inputTokens"] + normalized_usage["outputTokens"]
    total_tokens_including_cache = total_tokens + normalized_usage["cacheReadTokens"] + normalized_usage["cacheWriteTokens"]
    return {
        "source_event_type": "run_result",
        "finishReason": run_result_event.get("finishReason"),
        "iterations": run_result_event.get("iterations"),
        "durationMs": run_result_event.get("durationMs"),
        "provider": model_payload.get("provider"),
        "model": model_payload.get("id"),
        "usage": normalized_usage,
        "tokenTotals": {
            "totalTokens": total_tokens,
            "totalTokensIncludingCache": total_tokens_including_cache,
        },
        "projectedCost": {
            "currency": "USD",
            "pricingBasis": "GPT-5.5 standard API pricing",
            "ratesPerMillionTokens": PROJECTED_PRICING_USD_PER_MILLION,
            "breakdown": projected_cost_breakdown,
            "total": projected_cost_total,
        },
    }


def execute_cline_command(
    command: list[str],
    cwd: Path,
    stdout_path: Path,
    stderr_path: Path,
    timeout_seconds: int | None,
) -> SelectorExecutionResult:
    env = os.environ.copy()
    env.setdefault("NODE_PATH", "/Users/hassan/.nvm/versions/node/v24.15.0/lib/node_modules")

    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        start_new_session=True,
        env=env,
    )

    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []

    stdout_thread = threading.Thread(
        target=stream_reader,
        args=(process.stdout, stdout_path, stdout_chunks),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=stream_reader,
        args=(process.stderr, stderr_path, stderr_chunks),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()

    started_at = utc_now()
    timed_out = False
    try:
        returncode = process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        returncode = process.wait()

    stdout_thread.join(timeout=5.0)
    stderr_thread.join(timeout=5.0)

    finished_at = utc_now()
    stdout_text = "".join(stdout_chunks)
    stderr_text = "".join(stderr_chunks)
    return SelectorExecutionResult(
        command=command,
        pid=process.pid,
        returncode=returncode,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
        timed_out=timed_out,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=round(iso_to_timestamp(finished_at) - iso_to_timestamp(started_at), 3),
        run_result_event=parse_cline_run_result_event(stdout_text),
    )


def selector_paths(prompt: str, runs_dir: Path | None = None) -> SelectorPaths:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = prompt_slug(prompt)
    run_root = (runs_dir or DEFAULT_RUNS_DIR).resolve() / f"selector_{timestamp}_{slug}"
    workspace = run_root / "workspace"
    return SelectorPaths(
        run_root=run_root,
        workspace=workspace,
        selector_prompt=run_root / "selector_prompt.txt",
        selector_result_contract=workspace / "selector_result_contract.json",
        selector_selected_tags=workspace / "selected_tags.json",
        selector_stdout=run_root / "selector_stdout.txt",
        selector_stderr=run_root / "selector_stderr.txt",
        selector_invocation=run_root / "selector_invocation.json",
        selector_result=run_root / "selector_result.json",
        selector_usage=run_root / "selector_usage.json",
        selector_workspace_manifest=run_root / "selector_workspace_manifest.json",
    )


def build_selector_prompt_text(prompt: str) -> str:
    family_descriptions = {
        "mechanic_tags": "core gameplay verbs, systems, loop, and interaction structure",
        "semantic_tags": "high-level concepts, themes, and abstract gameplay identity",
        "mood_tags": "tone, feeling, atmosphere, and player emotional framing",
        "setting_tags": "world, environment, location, and backdrop context",
        "character_tags": "named or archetypal characters, creatures, or role identities",
        "games_tags": "specific game titles or direct game references",
        "franchise_tags": "franchise, IP, or series references",
    }
    family_section_lines: list[str] = []
    for family in TAG_FAMILIES:
        family_section_lines.extend(
            [
                f"### {family}",
                f"- Purpose: {family_descriptions[family]}",
                f"- Allowed source: Read only `catalog/{family}.json` and copy exact `tag` values from that file.",
                "- Output up to 5 entries with descending normalized scores.",
                "- Omit the family entirely if nothing is plausibly relevant.",
                "",
            ]
        )

    return "\n".join(
        [
            "# Game Matcher V2 Selector",
            "",
            "You are selecting ranked tags for a deterministic game matcher.",
            "",
            "## User Prompt",
            "",
            "```text",
            prompt.strip(),
            "```",
            "",
            "## Goal",
            "",
            "Infer the most relevant tags for the user prompt, but only by choosing exact tags from the provided family vocabularies.",
            "",
            "Your main job is to approximate the user's intended game into this limited controlled vocabulary while staying truthful.",
            "When the exact mechanic is missing from the vocabulary, choose the nearest mechanically-faithful available tag instead of inventing a new one.",
            "",
            "## Hard Rules",
            "",
            "- Do not invent tags.",
            "- Do not paraphrase tags.",
            "- Copy tag values exactly as they appear in the provided catalog JSON files.",
            "- Output valid JSON only.",
            "- Write the final JSON object to `selected_tags.json` in the workspace.",
            "- The top-level JSON value must be an object keyed by family name.",
            "- Each family value must be an array of objects in this exact shape: `{\"tag\": \"...\", \"score\": 0.0}`.",
            "- `score` must be a normalized confidence value from 0.0 to 1.0.",
            "- Prefer stronger tags to have higher scores, and weaker tags to have lower scores.",
            "- Keep only families that have at least one strong, defensible match.",
            "- Prefer precision over recall.",
            "- If the exact franchise fantasy is missing, preserve mechanic truth before theme/style resemblance.",
            "- Prefer specific mechanic primitives over broad genre labels whenever the catalog supports that specificity.",
            "",
            "## Selection Priority",
            "",
            "Use this priority order when distributing scores:",
            "1. mechanic_tags first and most heavily",
            "2. games_tags / franchise_tags only when there is strong direct evidence",
            "3. semantic_tags for nearest truthful abstraction",
            "4. mood_tags only as supporting evidence",
            "5. setting_tags and character_tags last",
            "",
            "## Mechanic Inference Rules",
            "",
            "For mechanic_tags, think in this order:",
            "- what repeated player input is performed",
            "- what movement model or aiming model defines the play",
            "- what obstacle / collision / destruction model defines success and failure",
            "- what scoring / retry / progression loop defines the game",
            "",
            "Prefer tags that capture concrete loop structure such as:",
            "- launch / aim / drag / release patterns",
            "- flap / tap / dodge / avoid patterns",
            "- stomp / jump / platform / timing patterns",
            "- physics puzzle / projectile / destruction patterns",
            "",
            "Avoid overusing broad fallback labels like `platformer game` or generic mood/theme tags when a more specific mechanic tag is available in the catalog.",
            "",
            "## Truthfulness Rules",
            "",
            "- Do not force franchise tags if the prompt is mainly defined by mechanics.",
            "- Do not force mechanics that are iconic to a franchise unless they are truly implied by the prompt.",
            "- If the prompt names a game/franchise, first infer the core mechanics that people actually associate with playing it, then map those mechanics into the nearest available controlled tags.",
            "- If only part of the latent concept exists in the catalog, choose the nearest truthful subset rather than exaggerating confidence.",
            "",
            "## Family Guidance",
            "",
            *family_section_lines,
            "## Required Output File",
            "",
            "Write `selected_tags.json` with content shaped like:",
            "",
            "```json",
            "{",
            '  "mechanic_tags": [{"tag": "endless runner", "score": 0.95}],',
            '  "games_tags": [{"tag": "Flappy Bird", "score": 0.99}]',
            "}",
            "```",
            "",
            "Do not include any explanation outside the JSON file.",
        ]
    )


def prepare_selector_workspace(
    *,
    prompt: str,
    artifacts_dir: Path,
    runs_dir: Path | None = None,
) -> SelectorPaths:
    paths = selector_paths(prompt, runs_dir=runs_dir)
    paths.workspace.mkdir(parents=True, exist_ok=True)
    catalog_dir = paths.workspace / "catalog"
    catalog_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "created_at": utc_now(),
        "prompt": prompt,
        "artifacts_dir": str(artifacts_dir.resolve()),
        "families": {},
    }
    for family in TAG_FAMILIES:
        source_path = artifacts_dir / f"{family}.json"
        if not source_path.exists():
            raise SelectorError(f"Missing family artifact: {source_path}")
        payload = load_json(source_path)
        slim_payload = {
            "family": family,
            "tag_count": payload.get("tag_count", 0),
            "tags": [{"tag": item.get("tag"), "count": item.get("count", 0)} for item in payload.get("tags", [])],
        }
        destination_path = catalog_dir / f"{family}.json"
        write_json(destination_path, slim_payload)
        manifest["families"][family] = {
            "source_path": str(source_path.resolve()),
            "workspace_path": str(destination_path.resolve()),
            "tag_count": slim_payload["tag_count"],
        }

    prompt_text = build_selector_prompt_text(prompt)
    paths.selector_prompt.write_text(prompt_text + "\n", encoding="utf-8")
    write_json(
        paths.selector_result_contract,
        {
            "type": "game_matcher_v2_selected_tags",
            "required_shape": {"<family>": [{"tag": "exact controlled tag", "score": 0.0}]},
            "allowed_families": list(TAG_FAMILIES),
            "score_range": [0.0, 1.0],
            "output_path": "selected_tags.json",
        },
    )
    write_json(paths.selector_workspace_manifest, manifest)
    return paths


def _normalize_tag(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def validate_selected_tags(
    selected_tags: dict[str, Any],
    *,
    artifacts_dir: Path,
) -> dict[str, list[dict[str, Any]]]:
    if not isinstance(selected_tags, dict):
        raise SelectorError("selected tag payload must be a JSON object")

    allowed_by_family: dict[str, dict[str, str]] = {}
    for family in TAG_FAMILIES:
        family_payload = load_json(artifacts_dir / f"{family}.json")
        allowed_by_family[family] = {
            _normalize_tag(item.get("tag")).casefold(): _normalize_tag(item.get("tag"))
            for item in family_payload.get("tags", [])
            if _normalize_tag(item.get("tag"))
        }

    normalized_payload: dict[str, list[dict[str, Any]]] = {}
    unknown_families = sorted(set(selected_tags.keys()) - set(TAG_FAMILIES))
    if unknown_families:
        raise SelectorError(f"unknown families in selector output: {', '.join(unknown_families)}")

    for family in TAG_FAMILIES:
        raw_items = selected_tags.get(family)
        if raw_items is None:
            continue
        if not isinstance(raw_items, list):
            raise SelectorError(f"{family} must be an array")

        seen_tags: set[str] = set()
        normalized_items: list[dict[str, Any]] = []
        for item in raw_items:
            if not isinstance(item, dict):
                continue

            tag = _normalize_tag(item.get("tag"))
            if not tag:
                continue

            allowed_tag = allowed_by_family[family].get(tag.casefold())
            if not allowed_tag:
                continue

            try:
                score = float(item.get("score"))
            except (TypeError, ValueError):
                continue

            if score < 0.0 or score > 1.0:
                continue
            if allowed_tag.casefold() in seen_tags:
                continue

            seen_tags.add(allowed_tag.casefold())
            normalized_items.append({"tag": allowed_tag, "score": round(score, 6)})

        normalized_items.sort(key=lambda item: (-item["score"], item["tag"].casefold()))
        if normalized_items:
            normalized_payload[family] = normalized_items

    if not normalized_payload:
        raise SelectorError("selector output did not contain any valid controlled-vocabulary tags")

    return normalized_payload


def run_selector(
    *,
    prompt: str,
    artifacts_dir: Path,
    model: str = DEFAULT_MODEL,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    runs_dir: Path | None = None,
) -> SelectorRunResult:
    paths = prepare_selector_workspace(prompt=prompt, artifacts_dir=artifacts_dir, runs_dir=runs_dir)

    command = [
        "cline",
        "-a",
        "-y",
        "--json",
        "-v",
        "-t",
        str(timeout_seconds),
        "--reasoning-effort",
        "high",
        "-c",
        str(paths.workspace),
        "--model",
        model,
        paths.selector_prompt.read_text(encoding="utf-8"),
    ]
    write_json(
        paths.selector_invocation,
        {
            "created_at": utc_now(),
            "cwd": str(REPO_ROOT.resolve()),
            "workspace": str(paths.workspace.resolve()),
            "command": command,
            "model": model,
            "timeout_seconds": timeout_seconds,
            "prompt_path": str(paths.selector_prompt.resolve()),
            "result_contract_path": str(paths.selector_result_contract.resolve()),
            "expected_selected_tags_path": str(paths.selector_selected_tags.resolve()),
        },
    )

    execution = execute_cline_command(
        command=command,
        cwd=REPO_ROOT,
        stdout_path=paths.selector_stdout,
        stderr_path=paths.selector_stderr,
        timeout_seconds=timeout_seconds,
    )

    if not paths.selector_selected_tags.exists():
        fallback_payload = find_fallback_selected_tags(prompt=prompt, failed_run_root=paths.run_root, runs_dir=runs_dir)
        if fallback_payload is None:
            raise SelectorError(f"Cline selector did not produce selected_tags.json: {paths.selector_selected_tags}")
        write_json(paths.selector_selected_tags, fallback_payload)

    raw_selected_tags = load_json(paths.selector_selected_tags)
    validated_selected_tags = validate_selected_tags(raw_selected_tags, artifacts_dir=artifacts_dir)
    usage_summary = normalize_cline_usage_summary(execution.run_result_event)
    if usage_summary is not None:
        write_json(paths.selector_usage, usage_summary)

    write_json(
        paths.selector_result,
        {
            "status": execution.status,
            "run_root": str(paths.run_root.resolve()),
            "workspace": str(paths.workspace.resolve()),
            "selected_tags_path": str(paths.selector_selected_tags.resolve()),
            "validated_selected_tags": validated_selected_tags,
            "stdout_path": str(paths.selector_stdout.resolve()),
            "stderr_path": str(paths.selector_stderr.resolve()),
            "invocation_path": str(paths.selector_invocation.resolve()),
            "usage_path": str(paths.selector_usage.resolve()) if usage_summary is not None else None,
            "usage_summary": usage_summary,
            "started_at": execution.started_at,
            "finished_at": execution.finished_at,
            "duration_seconds": execution.duration_seconds,
            "returncode": execution.returncode,
            "timed_out": execution.timed_out,
        },
    )

    return SelectorRunResult(
        run_root=paths.run_root,
        workspace=paths.workspace,
        selected_tags=raw_selected_tags,
        validated_selected_tags=validated_selected_tags,
        execution=execution,
    )


def find_fallback_selected_tags(
    *,
    prompt: str,
    failed_run_root: Path,
    runs_dir: Path | None = None,
) -> dict[str, Any] | None:
    root = (runs_dir or DEFAULT_RUNS_DIR).resolve()
    slug = prompt_slug(prompt)
    candidates = sorted(root.glob(f"selector_*_{slug}"), reverse=True)
    for candidate in candidates:
        if candidate.resolve() == failed_run_root.resolve():
            continue
        result_path = candidate / "selector_result.json"
        selected_tags_path = candidate / "workspace" / "selected_tags.json"
        if not result_path.exists() or not selected_tags_path.exists():
            continue
        try:
            result_payload = load_json(result_path)
            selected_tags_payload = load_json(selected_tags_path)
        except Exception:
            continue
        if not isinstance(result_payload, dict) or result_payload.get("status") != "completed":
            continue
        if not isinstance(selected_tags_payload, dict):
            continue
        return selected_tags_payload
    return None