#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

from orchestration_state import detect_stale_game, load_json, recompute_run_state, update_game_state, write_json
from verify_outputs import verify_site


CSS_LINK_RE = re.compile(r'(<link[^>]+rel=["\']stylesheet["\'][^>]+href=["\'])([^"\']+)(["\'][^>]*>)', re.IGNORECASE)
SCRIPT_SRC_RE = re.compile(r'(<script[^>]+src=["\'])([^"\']+)(["\'][^>]*>\s*</script>)', re.IGNORECASE)
INLINE_STYLE_RE = re.compile(r"<style(?P<attrs>[^>]*)>(?P<content>.*?)</style>", re.IGNORECASE | re.DOTALL)
INLINE_SCRIPT_RE = re.compile(r"<script(?P<attrs>[^>]*)>(?P<content>.*?)</script>", re.IGNORECASE | re.DOTALL)
SCRIPT_TYPE_RE = re.compile(r'type\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
SCRIPT_SRC_ATTR_RE = re.compile(r'\ssrc\s*=\s*["\'][^"\']+["\']', re.IGNORECASE)
IMPORTMAP_BLOCK_RE = re.compile(r'<script(?P<attrs>[^>]*)>(?P<content>.*?)</script>', re.IGNORECASE | re.DOTALL)
IMPORTMAP_RELATIVE_PATH_RE = re.compile(r'(?P<prefix>:\s*["\'])(assets/[^"\']+)(?P<suffix>["\'])')
CSS_URL_RE = re.compile(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)', re.IGNORECASE)
IMPORTMAP_SKIP_PREFIXES = ("./", "../", "/", "http://", "https://", "data:")

NORMALIZATION_REPLACEMENTS = [
    ("rezona", "gamezone"),
    ("gizmo", "gamezone"),
]

SKIP_JS_OBFUSCATION_PATH_MARKERS = (
    "assets/cdn.",
    "assets/unpkg.",
    "assets/cdnjs.",
    "assets/jsdelivr.",
    "assets/skypack.",
    "assets/esm.sh",
    "assets/react.dev/",
    "assets/www.w3.org/",
    "assets/aistudiocdn.com/",
)

COPYRIGHT_COMMENT = "<!-- Copyright Gamezone -->"
COPYRIGHT_META = '<meta name="copyright" content="Gamezone">'

TEXT_FILE_EXTENSIONS = {
    ".html",
    ".js",
    ".css",
    ".json",
    ".md",
    ".txt",
    ".svg",
}

MODERATE_JS_CONFIG = {
    "compact": True,
    "controlFlowFlattening": False,
    "deadCodeInjection": False,
    "debugProtection": False,
    "disableConsoleOutput": False,
    "identifierNamesGenerator": "hexadecimal",
    "renameGlobals": False,
    "selfDefending": False,
    "stringArray": True,
    "stringArrayEncoding": ["base64"],
    "stringArrayThreshold": 0.75,
    "stringArrayRotate": True,
    "stringArrayShuffle": True,
    "splitStrings": True,
    "splitStringsChunkLength": 8,
    "transformObjectKeys": False,
    "unicodeEscapeSequence": False,
    "sourceMap": False,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Produce moderate separate-file obfuscation outputs.")
    parser.add_argument("--run-dir", required=True, help="Path to a Game Obfuscator run directory.")
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=8000,
        help="Playwright verification timeout in milliseconds.",
    )
    parser.add_argument(
        "--game-id",
        help="Optional single game_id to process for debugging/validation.",
    )
    parser.add_argument(
        "--stale-after-seconds",
        type=int,
        default=300,
        help="Mark a running game as stalled if heartbeat age exceeds this threshold during launcher startup.",
    )
    parser.add_argument(
        "--max-game-seconds",
        type=int,
        default=300,
        help="Maximum allowed wall-clock time for one separate-obfuscation game before marking it stalled.",
    )
    parser.add_argument(
        "--worker-mode",
        action="store_true",
        help="Run a single-game separate-obfuscation worker process without launcher supervision.",
    )
    return parser.parse_args()


def run_command(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Command failed")


def collect_local_assets(html_text: str) -> tuple[list[str], list[str]]:
    css_refs = [match.group(2) for match in CSS_LINK_RE.finditer(html_text)]
    js_refs = [match.group(2) for match in SCRIPT_SRC_RE.finditer(html_text)]
    css_refs = [ref for ref in css_refs if not ref.startswith(("http://", "https://", "data:"))]
    js_refs = [ref for ref in js_refs if not ref.startswith(("http://", "https://", "data:"))]
    return css_refs, js_refs


def is_js_executable_type(script_type: str | None) -> bool:
    if script_type is None:
        return True

    normalized = script_type.strip().lower()
    return normalized in {
        "text/javascript",
        "application/javascript",
        "application/ecmascript",
        "text/ecmascript",
        "module",
    }


def apply_normalization_replacements(text: str) -> tuple[str, int]:
    updated = text
    replacement_count = 0

    for source, target in NORMALIZATION_REPLACEMENTS:
        occurrences = updated.count(source)
        if occurrences:
            updated = updated.replace(source, target)
            replacement_count += occurrences

    return updated, replacement_count


def rename_branded_paths(site_dir: Path) -> list[dict]:
    renamed_paths: list[dict] = []

    candidates = [path for path in site_dir.rglob("*") if any(source in path.name for source, _ in NORMALIZATION_REPLACEMENTS)]
    candidates.sort(key=lambda path: len(path.parts), reverse=True)

    for path in candidates:
        current_name = path.name
        new_name, replacement_count = apply_normalization_replacements(current_name)
        if replacement_count == 0 or new_name == current_name:
            continue

        target = path.with_name(new_name)
        if target.exists():
            raise FileExistsError(f"Cannot rename path because target already exists: {target}")

        path.rename(target)
        renamed_paths.append(
            {
                "from": str(path.relative_to(site_dir)),
                "to": str(target.relative_to(site_dir)),
            }
        )

    return renamed_paths


def normalize_site_text_content(site_dir: Path) -> tuple[list[dict], int]:
    normalized_files: list[dict] = []
    total_replacements = 0

    for path in sorted(site_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_FILE_EXTENSIONS:
            continue

        original = path.read_text(encoding="utf-8", errors="ignore")
        updated, replacement_count = apply_normalization_replacements(original)
        if replacement_count == 0:
            continue

        path.write_text(updated, encoding="utf-8")
        normalized_files.append(
            {
                "path": str(path.relative_to(site_dir)),
                "replacement_count": replacement_count,
            }
        )
        total_replacements += replacement_count

    return normalized_files, total_replacements


def inject_copyright_notice(index_path: Path) -> bool:
    html_text = index_path.read_text(encoding="utf-8", errors="ignore")
    changed = False

    if COPYRIGHT_COMMENT not in html_text:
        if "<head>" in html_text:
            html_text = html_text.replace("<head>", f"<head>\n    {COPYRIGHT_COMMENT}", 1)
        else:
            html_text = f"{COPYRIGHT_COMMENT}\n{html_text}"
        changed = True

    if COPYRIGHT_META not in html_text:
        if "<head>" in html_text:
            html_text = html_text.replace("<head>", f"<head>\n    {COPYRIGHT_META}", 1)
        else:
            html_text = f"{COPYRIGHT_META}\n{html_text}"
        changed = True

    if changed:
        index_path.write_text(html_text, encoding="utf-8")

    return changed


def minify_html_file_in_place(index_path: Path) -> None:
    temp_output = index_path.parent / f"{index_path.name}.tmp.html"
    run_command(["node", "scripts/minify_html.js", str(index_path), str(temp_output), "minify"])
    temp_output.replace(index_path)


def rewrite_css_urls(css_text: str, original_css_rel: str, generated_css_rel: str) -> tuple[str, int]:
    original_base = Path(original_css_rel).parent
    generated_base = Path(generated_css_rel).parent
    rewrite_count = 0

    def replacer(match: re.Match[str]) -> str:
        nonlocal rewrite_count
        quote = match.group(1)
        raw_url = match.group(2).strip()

        if raw_url.startswith(("data:", "http://", "https://", "/", "#")):
            return match.group(0)

        rewritten_path = Path(
            os.path.relpath((original_base / raw_url).as_posix(), generated_base.as_posix())
        ).as_posix()
        rewrite_count += 1
        return f"url({quote}{rewritten_path}{quote})"

    rewritten = CSS_URL_RE.sub(replacer, css_text)
    return rewritten, rewrite_count


def write_js_config(destination: Path) -> None:
    write_json(destination, MODERATE_JS_CONFIG)


def normalize_importmap_address(specifier_key: str, address: str) -> tuple[str, int]:
    if address.startswith(IMPORTMAP_SKIP_PREFIXES):
        normalized_address = address
    elif address.startswith("assets/"):
        normalized_address = f"./{address}"
    else:
        normalized_address = address

    if specifier_key.endswith("/") and normalized_address and not normalized_address.endswith("/"):
        normalized_address = f"{normalized_address}/"

    rewrite_count = 1 if normalized_address != address else 0
    return normalized_address, rewrite_count


def rewrite_importmap_value(value: object, specifier_key: str | None = None) -> tuple[object, int]:
    if isinstance(value, str):
        if specifier_key is None:
            return value, 0
        return normalize_importmap_address(specifier_key, value)

    if isinstance(value, dict):
        rewritten: dict[object, object] = {}
        rewrite_count = 0
        for key, nested_value in value.items():
            child_specifier_key = key if isinstance(key, str) else None
            updated_value, nested_count = rewrite_importmap_value(nested_value, child_specifier_key)
            rewritten[key] = updated_value
            rewrite_count += nested_count
        return rewritten, rewrite_count

    if isinstance(value, list):
        rewritten_list: list[object] = []
        rewrite_count = 0
        for item in value:
            updated_item, nested_count = rewrite_importmap_value(item, specifier_key)
            rewritten_list.append(updated_item)
            rewrite_count += nested_count
        return rewritten_list, rewrite_count

    return value, 0


def rewrite_importmap_paths(html_text: str) -> tuple[str, int]:
    rewrite_count = 0

    def script_replacer(match: re.Match[str]) -> str:
        nonlocal rewrite_count
        attrs = match.group("attrs") or ""
        content = match.group("content") or ""

        script_type_match = SCRIPT_TYPE_RE.search(attrs)
        script_type = script_type_match.group(1).strip().lower() if script_type_match else None
        if script_type != "importmap":
            return match.group(0)

        original_content = content
        normalized_content = content.strip()
        rewritten_content = content
        block_rewrite_count = 0

        try:
            parsed_content = json.loads(normalized_content)
            rewritten_json, block_rewrite_count = rewrite_importmap_value(parsed_content)
            rewritten_content = json.dumps(rewritten_json, ensure_ascii=False, separators=(",", ":"))
        except json.JSONDecodeError:
            rewritten_content = IMPORTMAP_RELATIVE_PATH_RE.sub(
                lambda path_match: (
                    path_match.group(0)
                    if path_match.group(2).startswith(IMPORTMAP_SKIP_PREFIXES)
                    else f"{path_match.group('prefix')}./{path_match.group(2)}{path_match.group('suffix')}"
                ),
                normalized_content,
            )
            block_rewrite_count = rewritten_content.count("./assets/") - normalized_content.count("./assets/")

        if not rewritten_content.startswith(("{", "[")):
            rewritten_content = rewritten_content.strip()

        rewrite_count += block_rewrite_count
        return f'<script{attrs}>{rewritten_content}</script>'

    rewritten_html = IMPORTMAP_BLOCK_RE.sub(script_replacer, html_text)
    return rewritten_html, rewrite_count


def should_skip_js_obfuscation(js_ref: str) -> str | None:
    normalized_ref = js_ref.replace("\\", "/").lower()
    for marker in SKIP_JS_OBFUSCATION_PATH_MARKERS:
        if marker in normalized_ref:
            return f"path_matches_skip_marker:{marker}"
    return None


def validate_js_file(path: Path) -> tuple[bool, str | None]:
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    if result.returncode == 0:
        return True, None
    return False, (result.stderr.strip() or result.stdout.strip() or "JavaScript syntax validation failed")


def is_probable_module_syntax_error(error_text: str | None) -> bool:
    if not error_text:
        return False
    lowered = error_text.lower()
    return "failed to load the es module" in lowered or "import" in lowered or "export" in lowered


def obfuscate_js_file_in_place(src: Path, config_path: Path) -> tuple[bool, str | None]:
    original_content = src.read_text(encoding="utf-8", errors="ignore")
    temp_output = src.parent / f"{src.name}.tmp.js"
    try:
        run_command(
            [
                "npx",
                "javascript-obfuscator",
                str(src),
                "--output",
                str(temp_output),
                "--config",
                str(config_path),
            ]
        )
        temp_output.replace(src)
    except Exception as exc:
        if temp_output.exists():
            temp_output.unlink()
        src.write_text(original_content, encoding="utf-8")
        return False, str(exc)

    is_valid, validation_error = validate_js_file(src)
    if is_valid or is_probable_module_syntax_error(validation_error):
        return True, None

    src.write_text(original_content, encoding="utf-8")
    return False, validation_error


def minify_css_file_in_place(src: Path) -> None:
    temp_output = src.parent / f"{src.name}.tmp.css"
    run_command(["npx", "postcss", str(src), "-o", str(temp_output)])
    temp_output.replace(src)


def transform_site_in_place(site_dir: Path) -> dict:
    renamed_paths = rename_branded_paths(site_dir)
    normalized_files, normalization_replacement_count = normalize_site_text_content(site_dir)

    index_path = site_dir / "index.html"
    html_text = index_path.read_text(encoding="utf-8", errors="ignore")

    transformed_js: list[str] = []
    transformed_css: list[str] = []
    missing_js: list[str] = []
    missing_css: list[str] = []
    skipped_js_transforms: list[dict] = []
    externalized_inline_script_blocks: list[dict] = []
    externalized_inline_style_blocks: list[dict] = []
    skipped_inline_script_blocks: list[dict] = []
    rewritten_inline_css_url_count = 0

    generated_assets_dir = site_dir / "assets" / "obfuscated"
    generated_assets_dir.mkdir(parents=True, exist_ok=True)

    style_counter = 0

    def style_replacer(match: re.Match[str]) -> str:
        nonlocal style_counter, rewritten_inline_css_url_count
        content = match.group("content")
        if not content.strip():
            return match.group(0)

        style_counter += 1
        generated_rel = f"assets/obfuscated/inline-style-{style_counter:03d}.css"
        generated_path = site_dir / generated_rel
        rewritten_css, rewrite_count = rewrite_css_urls(content, "index.html", generated_rel)
        rewritten_inline_css_url_count += rewrite_count
        generated_path.write_text(rewritten_css, encoding="utf-8")
        externalized_inline_style_blocks.append(
            {
                "index": style_counter,
                "generated_file": generated_rel,
                "rewritten_url_count": rewrite_count,
            }
        )
        return f'<link rel="stylesheet" href="{generated_rel}">'

    html_text = INLINE_STYLE_RE.sub(style_replacer, html_text)

    script_counter = 0

    def script_replacer(match: re.Match[str]) -> str:
        nonlocal script_counter
        attrs = match.group("attrs") or ""
        content = match.group("content")

        if SCRIPT_SRC_ATTR_RE.search(attrs):
            return match.group(0)

        script_type_match = SCRIPT_TYPE_RE.search(attrs)
        script_type = script_type_match.group(1) if script_type_match else None

        if not content.strip():
            return match.group(0)

        if "document.currentScript" in content:
            skipped_inline_script_blocks.append(
                {
                    "index": script_counter + 1,
                    "reason": "uses_document_currentScript",
                    "type": script_type,
                }
            )
            return match.group(0)

        if not is_js_executable_type(script_type):
            skipped_inline_script_blocks.append(
                {
                    "index": script_counter + 1,
                    "reason": "non_executable_script_type",
                    "type": script_type,
                }
            )
            return match.group(0)

        script_counter += 1
        generated_rel = f"assets/obfuscated/inline-script-{script_counter:03d}.js"
        normalized_type = script_type.strip().lower() if script_type else None

        generated_path = site_dir / generated_rel
        original_content = content.strip() + "\n"
        generated_path.write_text(original_content, encoding="utf-8")
        externalized_inline_script_blocks.append(
            {
                "index": script_counter,
                "generated_file": generated_rel,
                "type": script_type or "classic",
            }
        )

        preserved_attrs = SCRIPT_SRC_ATTR_RE.sub("", attrs)
        preserved_attrs = re.sub(r'\s+type\s*=\s*["\']module["\']', "", preserved_attrs, flags=re.IGNORECASE)
        if normalized_type == "module":
            return f'<script type="module"{preserved_attrs} src="{generated_rel}"></script>'
        return f'<script{preserved_attrs} src="{generated_rel}"></script>'

    html_text = INLINE_SCRIPT_RE.sub(script_replacer, html_text)
    html_text, importmap_rewrite_count = rewrite_importmap_paths(html_text)
    index_path.write_text(html_text, encoding="utf-8")

    css_refs, js_refs = collect_local_assets(html_text)

    temp_config_dir = Path(tempfile.mkdtemp(prefix="game_obfuscator_moderate_js_"))
    config_path = temp_config_dir / "moderate.json"
    write_jsConfig = write_js_config
    write_jsConfig(config_path)

    try:
        for js_ref in js_refs:
            src = site_dir / js_ref
            if not src.exists() or not src.is_file():
                missing_js.append(js_ref)
                continue

            skip_reason = should_skip_js_obfuscation(js_ref)
            if skip_reason:
                skipped_js_transforms.append(
                    {
                        "file": js_ref,
                        "reason": skip_reason,
                        "fallback": "kept_original_file",
                    }
                )
                continue

            transformed, validation_error = obfuscate_js_file_in_place(src, config_path)
            if transformed:
                transformed_js.append(js_ref)
            else:
                skipped_js_transforms.append(
                    {
                        "file": js_ref,
                        "reason": "obfuscation_failed_or_syntax_validation_failed",
                        "validation_error": validation_error,
                        "fallback": "kept_original_file",
                    }
                )

        for css_ref in css_refs:
            src = site_dir / css_ref
            if not src.exists() or not src.is_file():
                missing_css.append(css_ref)
                continue
            minify_css_file_in_place(src)
            transformed_css.append(css_ref)
    finally:
        shutil.rmtree(temp_config_dir, ignore_errors=True)

    copyright_injected = inject_copyright_notice(index_path)
    minify_html_file_in_place(index_path)

    remaining_branded_paths = [
        str(path.relative_to(site_dir))
        for path in sorted(site_dir.rglob("*"))
        if any(source in path.name for source, _ in NORMALIZATION_REPLACEMENTS)
    ]

    return {
        "runtime_index": str(index_path),
        "transformed_js": transformed_js,
        "transformed_css": transformed_css,
        "missing_js": missing_js,
        "missing_css": missing_css,
        "skipped_js_transforms": skipped_js_transforms,
        "externalized_inline_script_blocks": externalized_inline_script_blocks,
        "externalized_inline_style_blocks": externalized_inline_style_blocks,
        "skipped_inline_script_blocks": skipped_inline_script_blocks,
        "rewritten_inline_css_url_count": rewritten_inline_css_url_count,
        "importmap_rewrite_count": importmap_rewrite_count,
        "normalized_files": normalized_files,
        "normalization_replacement_count": normalization_replacement_count,
        "renamed_paths": renamed_paths,
        "remaining_branded_paths": remaining_branded_paths,
        "html_minified": True,
        "copyright_injected": copyright_injected,
    }


def process_game(game_state: dict, run_dir: Path, timeout_ms: int) -> dict:
    runtime_output_dir = Path(game_state["output_path"])
    artifacts_dir = Path(game_state["artifacts_path"])
    source_site_dir = Path(game_state.get("artifacts", {}).get("pre_bundle_site", artifacts_dir / "pre_bundle_site"))
    source_index_path = source_site_dir / "index.html"

    if not source_index_path.exists():
        raise FileNotFoundError(f"Missing pre-bundle site index.html: {source_index_path}")

    separate_root = artifacts_dir / "separate_obfuscation"
    if separate_root.exists():
        shutil.rmtree(separate_root)
    separate_root.mkdir(parents=True, exist_ok=True)

    source_snapshot_dir = separate_root / "source_site"
    shutil.copytree(source_site_dir, source_snapshot_dir)

    target_site_dir = runtime_output_dir
    transform_result = transform_site_in_place(target_site_dir)

    if transform_result["remaining_branded_paths"]:
        raise RuntimeError(
            "Branded path names remain after normalization: " + ", ".join(transform_result["remaining_branded_paths"])
        )

    candidate_verification = verify_site(
        Path(transform_result["runtime_index"]),
        target_site_dir / "assets" / "emoji",
        run_dir,
        timeout_ms,
    )
    write_json(
        separate_root / "verification.json",
        {
            "generated_at": utc_now(),
            "game_id": game_state["game_id"],
            "mode": "moderate_separate_file",
            **candidate_verification,
        },
    )

    if candidate_verification["status"] == "passed":
        write_json(
            artifacts_dir / "verification.json",
            {
                "generated_at": utc_now(),
                "game_id": game_state["game_id"],
                "mode": "moderate_separate_file",
                **candidate_verification,
            },
        )

    report = {
        "generated_at": utc_now(),
        "game_id": game_state["game_id"],
        "mode": "moderate_separate_file",
        "source_site": str(source_site_dir),
        "source_snapshot_site": str(source_snapshot_dir),
        "published_output_dir": str(target_site_dir),
        "runtime_index": transform_result["runtime_index"],
        "transformed_js": transform_result["transformed_js"],
        "transformed_css": transform_result["transformed_css"],
        "missing_js": transform_result["missing_js"],
        "missing_css": transform_result["missing_css"],
        "skipped_js_transforms": transform_result["skipped_js_transforms"],
        "externalized_inline_script_blocks": transform_result["externalized_inline_script_blocks"],
        "externalized_inline_style_blocks": transform_result["externalized_inline_style_blocks"],
        "skipped_inline_script_blocks": transform_result["skipped_inline_script_blocks"],
        "rewritten_inline_css_url_count": transform_result["rewritten_inline_css_url_count"],
        "importmap_rewrite_count": transform_result["importmap_rewrite_count"],
        "normalized_files": transform_result["normalized_files"],
        "normalization_replacement_count": transform_result["normalization_replacement_count"],
        "normalization_replacements": [
            {"from": source, "to": target}
            for source, target in NORMALIZATION_REPLACEMENTS
        ],
        "renamed_paths": transform_result["renamed_paths"],
        "remaining_branded_paths": transform_result["remaining_branded_paths"],
        "html_minified": transform_result["html_minified"],
        "copyright_injected": transform_result["copyright_injected"],
        "published_verification_status": candidate_verification["status"],
        "verification_artifact": str(separate_root / "verification.json"),
        "selected": candidate_verification["status"] == "passed",
    }
    write_json(artifacts_dir / "separate_obfuscation_report.json", report)
    return report


def should_process_game(game_state: dict, requested_game_id: str | None) -> bool:
    if requested_game_id:
        return game_state["game_id"] == requested_game_id
    return game_state.get("status") not in {"succeeded", "verification_passed"}


def should_time_out(started_at: str | None, max_game_seconds: int) -> bool:
    if not started_at:
        return False
    started_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    return datetime.now(timezone.utc) - started_dt > timedelta(seconds=max_game_seconds)


def run_worker_process(run_dir: Path, game_id: str, timeout_ms: int, max_game_seconds: int) -> subprocess.CompletedProcess[str]:
    python_executable = os.environ.get("GAME_OBFUSCATOR_PYTHON", sys.executable)
    command = [
        python_executable,
        str(Path(__file__).resolve()),
        "--run-dir",
        str(run_dir),
        "--game-id",
        game_id,
        "--timeout-ms",
        str(timeout_ms),
        "--max-game-seconds",
        str(max_game_seconds),
        "--worker-mode",
    ]
    return subprocess.run(command, capture_output=True, text=True, timeout=max_game_seconds)


def run_game_job(run_dir: Path, game_state: dict, timeout_ms: int, max_game_seconds: int) -> dict:
    game_id = game_state["game_id"]
    artifacts_dir = Path(game_state["artifacts_path"])

    updated_state = update_game_state(
        run_dir,
        game_id,
        status="running",
        phase="separate_obfuscation_started",
        last_error=None,
        mark_started=True,
        increment_attempt=True,
        heartbeat=True,
        progress=True,
    )
    recompute_run_state(
        run_dir,
        current_phase="separate_obfuscation_running",
        note="Sequential separate-output launcher running.",
    )

    if should_time_out(updated_state.get("started_at"), max_game_seconds):
        stalled_state = update_game_state(
            run_dir,
            game_id,
            status="stalled",
            phase="separate_obfuscation_timed_out",
            last_error=f"Exceeded {max_game_seconds} seconds in separate obfuscation.",
            heartbeat=True,
            progress=True,
            mark_completed=True,
        )
        recompute_run_state(run_dir, current_phase="separate_obfuscation_timeout")
        return stalled_state

    try:
        result = run_worker_process(run_dir, game_id, timeout_ms, max_game_seconds)
        if result.returncode != 0:
            updated_state = update_game_state(
                run_dir,
                game_id,
                status="failed",
                phase="separate_obfuscation_failed",
                last_error=(result.stderr.strip() or result.stdout.strip() or "Separate obfuscation worker failed."),
                heartbeat=True,
                progress=True,
                mark_completed=True,
            )
            recompute_run_state(run_dir, current_phase="separate_obfuscation_failed")
            return updated_state

        refreshed_state = load_json(run_dir / "games" / game_id / "game_state.json")
        recompute_run_state(run_dir, current_phase=refreshed_state.get("current_phase", "separate_obfuscation_complete"))
        return refreshed_state
    except subprocess.TimeoutExpired:
        stalled_state = update_game_state(
            run_dir,
            game_id,
            status="stalled",
            phase="separate_obfuscation_timed_out",
            last_error=f"Exceeded {max_game_seconds} seconds in separate obfuscation.",
            heartbeat=True,
            progress=True,
            mark_completed=True,
        )
        recompute_run_state(run_dir, current_phase="separate_obfuscation_timeout")
        return stalled_state


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    manifest = load_json(run_dir / "input_manifest.json")

    if args.worker_mode:
        if not args.game_id:
            raise SystemExit("--worker-mode requires --game-id")
        game_state = load_json(run_dir / "games" / args.game_id / "game_state.json")
        artifacts_dir = Path(game_state["artifacts_path"])
        try:
            report = process_game(game_state, run_dir, args.timeout_ms)
            final_status = "succeeded" if report["selected"] else "verification_failed"
            final_error = None if report["selected"] else "Moderate separate-file obfuscation did not pass verification."
            update_game_state(
                run_dir,
                args.game_id,
                status=final_status,
                phase="separate_obfuscation_complete",
                last_error=final_error,
                heartbeat=True,
                progress=True,
                mark_completed=True,
                artifacts={
                    "separate_obfuscation_report": str(artifacts_dir / "separate_obfuscation_report.json"),
                    "verification": str(artifacts_dir / "verification.json"),
                },
            )
            print(run_dir)
            return
        except Exception as exc:
            update_game_state(
                run_dir,
                args.game_id,
                status="failed",
                phase="separate_obfuscation_failed",
                last_error=str(exc),
                heartbeat=True,
                progress=True,
                mark_completed=True,
            )
            raise

    recompute_run_state(run_dir, current_phase="separate_obfuscation_launcher_start")

    for game in manifest.get("games", []):
        game_id = game["game_id"]
        game_state = load_json(run_dir / "games" / game_id / "game_state.json")
        if not should_process_game(game_state, args.game_id):
            continue

        detect_stale_game(run_dir, game_id, stale_after_seconds=args.stale_after_seconds)
        game_state = load_json(run_dir / "games" / game_id / "game_state.json")
        if game_state.get("status") == "stalled":
            recompute_run_state(run_dir, current_phase="separate_obfuscation_stalled_detected")
            continue

        run_game_job(run_dir, game_state, args.timeout_ms, args.max_game_seconds)

    recompute_run_state(run_dir, current_phase="separate_obfuscation_launcher_complete")
    print(run_dir)


if __name__ == "__main__":
    main()