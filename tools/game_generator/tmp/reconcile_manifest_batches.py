#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
BATCH_RUNS_DIR = ROOT / "batch_runs"
OUT_PATH = ROOT / "tmp" / "manifest_may_18_searches_1.json"

BATCH_IDS = [
    "batch_pipeline_20260517T205036Z",
    "batch_pipeline_20260517T205038Z",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def infer_manifest_label(source_manifest_path: str) -> str:
    name = Path(source_manifest_path).name
    if name == "curated_limit2_prompt_only_manifest.json":
        return "curated_top_80"
    if name == "vatsal_top_mechanics.json":
        return "vatsal_top_mechanics_200"
    return name


def success_record(batch_id: str, manifest_label: str, item: dict[str, Any]) -> dict[str, Any]:
    summary = item.get("result_summary") or {}
    return {
        "batch_id": batch_id,
        "manifest_label": manifest_label,
        "item_id": item.get("item_id"),
        "prompt": item.get("prompt"),
        "pipeline_run_id": item.get("pipeline_run_id"),
        "pipeline_run_dir": item.get("pipeline_run_dir"),
        "final_output_dir": summary.get("final_output_dir"),
        "final_output_dirs": summary.get("final_output_dirs", []),
        "projected_cdn_urls": summary.get("projected_cdn_urls", []),
        "dashboard_path": summary.get("dashboard_path"),
        "completed_at": item.get("completed_at"),
        "status": item.get("status"),
    }


def failure_record(batch_id: str, manifest_label: str, item: dict[str, Any]) -> dict[str, Any]:
    summary = item.get("result_summary") or {}
    error = item.get("last_error") or summary.get("error") or {}
    details = error.get("details") if isinstance(error, dict) else None
    upstream_run_id = None
    upstream_dashboard_path = None
    upstream_status = None
    if isinstance(details, dict):
        upstream_run_id = details.get("run_id")
        upstream_dashboard_path = details.get("dashboard_path")
        upstream_status = details.get("status")
    return {
        "batch_id": batch_id,
        "manifest_label": manifest_label,
        "item_id": item.get("item_id"),
        "prompt": item.get("prompt"),
        "pipeline_run_id": item.get("pipeline_run_id"),
        "pipeline_run_dir": item.get("pipeline_run_dir"),
        "failed_step": error.get("step") if isinstance(error, dict) else None,
        "error_message": error.get("message") if isinstance(error, dict) else None,
        "error_details": details,
        "dashboard_path": summary.get("dashboard_path"),
        "stderr_path": details.get("stderr_path") if isinstance(details, dict) else None,
        "upstream_run_id": upstream_run_id,
        "upstream_dashboard_path": upstream_dashboard_path,
        "upstream_status": upstream_status,
        "completed_at": item.get("completed_at"),
        "status": item.get("status"),
    }


def reconcile_batch(batch_id: str) -> dict[str, Any]:
    batch_dir = BATCH_RUNS_DIR / batch_id
    state = load_json(batch_dir / "batch_state.json")
    manifest_label = infer_manifest_label(str(state.get("source_manifest_path") or ""))
    items_dir = batch_dir / "items"

    successes: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    failures_by_step: Counter[str] = Counter()

    for item_path in sorted(items_dir.glob("*.json")):
        item = load_json(item_path)
        status = item.get("status")
        if status == "completed":
            successes.append(success_record(batch_id, manifest_label, item))
        elif status == "failed":
            record = failure_record(batch_id, manifest_label, item)
            failures.append(record)
            failures_by_step[str(record.get("failed_step") or "unknown")] += 1

    return {
        "batch_id": batch_id,
        "manifest_label": manifest_label,
        "source_manifest_path": state.get("source_manifest_path"),
        "batch_status": state.get("status"),
        "counts": state.get("counts"),
        "defaults": state.get("defaults"),
        "successful_items": successes,
        "failed_items": failures,
        "failure_counts_by_step": dict(sorted(failures_by_step.items())),
    }


def main() -> int:
    batch_reports = [reconcile_batch(batch_id) for batch_id in BATCH_IDS]

    all_successes = [item for report in batch_reports for item in report["successful_items"]]
    all_failures = [item for report in batch_reports for item in report["failed_items"]]

    success_by_manifest: dict[str, int] = defaultdict(int)
    failure_by_manifest: dict[str, int] = defaultdict(int)
    failure_by_step: Counter[str] = Counter()

    for item in all_successes:
        success_by_manifest[str(item["manifest_label"])] += 1
    for item in all_failures:
        failure_by_manifest[str(item["manifest_label"])] += 1
        failure_by_step[str(item.get("failed_step") or "unknown")] += 1

    payload = {
        "artifact_name": "manifest_may_18_searches_1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_batch_ids": BATCH_IDS,
        "summary": {
            "total_batches": len(batch_reports),
            "total_successes": len(all_successes),
            "total_failures": len(all_failures),
            "success_count_by_manifest": dict(sorted(success_by_manifest.items())),
            "failure_count_by_manifest": dict(sorted(failure_by_manifest.items())),
            "failure_count_by_step": dict(sorted(failure_by_step.items())),
        },
        "batches": batch_reports,
        "successful_items": all_successes,
        "failed_items": all_failures,
    }

    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "artifact_path": str(OUT_PATH),
                "total_successes": len(all_successes),
                "total_failures": len(all_failures),
                "failure_count_by_step": dict(sorted(failure_by_step.items())),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())