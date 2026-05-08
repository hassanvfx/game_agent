#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "configs" / "operator_pipeline_v2.json"


class OperatorRegistryError(ValueError):
    """Raised when the operator pipeline registry is invalid."""


@dataclass(frozen=True)
class OperatorDefinition:
    id: str
    stage_number: int
    prompt: Path
    summary_required: bool
    accepted_upstream_statuses: tuple[str, ...]

    @property
    def stage_slug(self) -> str:
        return stage_slug(self.stage_number, self.id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "stage_number": self.stage_number,
            "stage_slug": self.stage_slug,
            "prompt": str(self.prompt),
            "summary_required": self.summary_required,
            "accepted_upstream_statuses": list(self.accepted_upstream_statuses),
        }


@dataclass(frozen=True)
class OperatorRegistry:
    pipeline_id: str
    max_retries_per_stage: int
    default_agent_timeout_seconds: int
    operators: tuple[OperatorDefinition, ...]

    def get(self, operator_id: str) -> OperatorDefinition:
        for operator in self.operators:
            if operator.id == operator_id:
                return operator
        valid = ", ".join(operator.id for operator in self.operators)
        raise OperatorRegistryError(f"Unknown operator '{operator_id}'. Valid operators: {valid}")

    def through(self, operator_id: str) -> tuple[OperatorDefinition, ...]:
        target = self.get(operator_id)
        return tuple(
            operator
            for operator in self.operators
            if operator.stage_number <= target.stage_number
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "max_retries_per_stage": self.max_retries_per_stage,
            "default_agent_timeout_seconds": self.default_agent_timeout_seconds,
            "operators": [operator.to_dict() for operator in self.operators],
        }


def stage_slug(stage_number: int, operator_id: str) -> str:
    return f"stage_{stage_number:02d}_{operator_id}"


def _require_dict(payload: Any, context: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise OperatorRegistryError(f"{context} must be an object")
    return payload


def _require_positive_int(payload: dict[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or value <= 0:
        raise OperatorRegistryError(f"'{key}' must be a positive integer")
    return value


def _require_nonempty_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise OperatorRegistryError(f"'{key}' must be a non-empty string")
    return value


def _resolve_prompt_path(config_path: Path, prompt_value: str) -> Path:
    prompt_path = Path(prompt_value)
    if not prompt_path.is_absolute():
        prompt_path = REPO_ROOT / prompt_path
    return prompt_path.resolve()


def _read_accepted_upstream_statuses(operator_payload: dict[str, Any], operator_id: str) -> tuple[str, ...]:
    value = operator_payload.get("accepted_upstream_statuses", ["ok", "warning", "error"])
    if not isinstance(value, list) or not value:
        raise OperatorRegistryError(
            f"Operator '{operator_id}' field 'accepted_upstream_statuses' must be a non-empty array"
        )

    allowed = {"ok", "warning", "error"}
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or item not in allowed:
            raise OperatorRegistryError(
                f"Operator '{operator_id}' field 'accepted_upstream_statuses' must contain only: {sorted(allowed)}"
            )
        normalized.append(item)

    return tuple(normalized)


def load_registry(config_path: Path = DEFAULT_REGISTRY_PATH) -> OperatorRegistry:
    config_path = config_path.resolve()
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OperatorRegistryError(f"Registry config not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise OperatorRegistryError(f"Registry config is not valid JSON: {config_path}: {exc}") from exc

    payload = _require_dict(payload, "registry config")
    pipeline_id = _require_nonempty_string(payload, "pipeline_id")
    max_retries_per_stage = _require_positive_int(payload, "max_retries_per_stage")
    default_agent_timeout_seconds = _require_positive_int(
        payload,
        "default_agent_timeout_seconds",
    )

    raw_operators = payload.get("operators")
    if not isinstance(raw_operators, list) or not raw_operators:
        raise OperatorRegistryError("'operators' must be a non-empty array")

    operators: list[OperatorDefinition] = []
    seen_ids: set[str] = set()
    seen_stage_numbers: set[int] = set()

    for index, raw_operator in enumerate(raw_operators, start=1):
        operator_payload = _require_dict(raw_operator, f"operators[{index}]")
        operator_id = _require_nonempty_string(operator_payload, "id")
        stage_number = _require_positive_int(operator_payload, "stage_number")
        prompt_value = _require_nonempty_string(operator_payload, "prompt")
        summary_required = operator_payload.get("summary_required")

        if not isinstance(summary_required, bool):
            raise OperatorRegistryError(
                f"Operator '{operator_id}' field 'summary_required' must be boolean"
            )

        accepted_upstream_statuses = _read_accepted_upstream_statuses(operator_payload, operator_id)

        if operator_id in seen_ids:
            raise OperatorRegistryError(f"Duplicate operator id: {operator_id}")
        seen_ids.add(operator_id)

        if stage_number in seen_stage_numbers:
            raise OperatorRegistryError(f"Duplicate stage number: {stage_number}")
        seen_stage_numbers.add(stage_number)

        prompt_path = _resolve_prompt_path(config_path, prompt_value)
        if not prompt_path.exists():
            raise OperatorRegistryError(
                f"Prompt file for operator '{operator_id}' does not exist: {prompt_path}"
            )
        if not prompt_path.is_file():
            raise OperatorRegistryError(
                f"Prompt path for operator '{operator_id}' is not a file: {prompt_path}"
            )

        operators.append(
            OperatorDefinition(
                id=operator_id,
                stage_number=stage_number,
                prompt=prompt_path,
                summary_required=summary_required,
                accepted_upstream_statuses=accepted_upstream_statuses,
            )
        )

    operators.sort(key=lambda operator: operator.stage_number)
    expected_stage_numbers = list(range(1, len(operators) + 1))
    actual_stage_numbers = [operator.stage_number for operator in operators]
    if actual_stage_numbers != expected_stage_numbers:
        raise OperatorRegistryError(
            "Stage numbers must be sequential starting at 1. "
            f"Expected {expected_stage_numbers}, got {actual_stage_numbers}"
        )

    return OperatorRegistry(
        pipeline_id=pipeline_id,
        max_retries_per_stage=max_retries_per_stage,
        default_agent_timeout_seconds=default_agent_timeout_seconds,
        operators=tuple(operators),
    )


def resolve_step(registry: OperatorRegistry, operator_id: str) -> tuple[OperatorDefinition, ...]:
    return (registry.get(operator_id),)


def resolve_through(registry: OperatorRegistry, operator_id: str) -> tuple[OperatorDefinition, ...]:
    return registry.through(operator_id)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and inspect Operator Pipeline v2 registry.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help=f"Registry config path. Default: {DEFAULT_REGISTRY_PATH.relative_to(REPO_ROOT)}",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("inspect", help="Print the validated registry as JSON.")

    step_parser = subparsers.add_parser("step", help="Resolve one operator by id.")
    step_parser.add_argument("operator_id")

    through_parser = subparsers.add_parser("through", help="Resolve operators through an operator id.")
    through_parser.add_argument("operator_id")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        registry = load_registry(args.config)
        if args.command == "step":
            payload = [operator.to_dict() for operator in resolve_step(registry, args.operator_id)]
        elif args.command == "through":
            payload = [operator.to_dict() for operator in resolve_through(registry, args.operator_id)]
        else:
            payload = registry.to_dict()
    except OperatorRegistryError as exc:
        parser.exit(status=2, message=f"operator_registry_v2: error: {exc}\n")

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())