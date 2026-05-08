"""Live network tests for the KIE generation/LLM acceptance matrix.

These tests use the synthetic prompt/image fixtures but make real KIE network
requests. They are skipped by default and run only when explicitly enabled:

    RUN_KIE_LIVE_TESTS=1 .venv/bin/python -m pytest tests/integration -q

Optional filtering:

    KIE_LIVE_SCOPE=llm
    KIE_LIVE_SCOPE=gemini
    KIE_LIVE_SCOPE=image
    KIE_LIVE_SCOPE=video
    KIE_LIVE_SCOPE=suno
    KIE_LIVE_SCOPE=generation
    KIE_LIVE_SCOPE=all

Image/video tests are full end-to-end checks: they submit jobs, save job
records, wait for final results, assert generated output URLs exist, and store
complete input/output fixtures under outputs/live_tests/<timestamp>/<case>/.
"""

from __future__ import annotations

import io
import json
import os
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from kie_cli.cli import main


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_KIE_LIVE_TESTS") != "1",
    reason="Set RUN_KIE_LIVE_TESTS=1 to run live KIE API tests.",
)


FIXTURE_ROOT = Path("tests/fixtures")
PROMPTS = FIXTURE_ROOT / "prompts"
IMAGES = FIXTURE_ROOT / "images"
LIVE_ROOT = Path("outputs/live_tests")


def live_scope() -> str:
    return os.getenv("KIE_LIVE_SCOPE", "all").strip().lower()


def live_poll_interval() -> str:
    return os.getenv("KIE_LIVE_POLL_INTERVAL", "10")


def live_timeout() -> str:
    return os.getenv("KIE_LIVE_TIMEOUT", "900")


def live_suno_callback_url() -> str:
    value = os.getenv("KIE_SUNO_CALLBACK_URL", "").strip()
    if not value:
        pytest.skip("Set KIE_SUNO_CALLBACK_URL to run live Suno tests.")
    return value


def require_scope(*scopes: str) -> None:
    requested = live_scope()
    allowed = {"all", *scopes}
    if requested not in allowed:
        pytest.skip(f"Set KIE_LIVE_SCOPE to one of: {', '.join(sorted(allowed))}")


@pytest.fixture(scope="session")
def run_root() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = LIVE_ROOT / timestamp
    path.mkdir(parents=True, exist_ok=True)
    write_json(
        path / "manifest.json",
        {
            "startedAt": timestamp,
            "scope": live_scope(),
            "pollIntervalSeconds": live_poll_interval(),
            "timeoutSeconds": live_timeout(),
            "cases": [],
        },
    )
    return path


def run_cli_json(argv: list[str], io_dir: Path) -> tuple[int, dict[str, Any]]:
    io_dir.mkdir(parents=True, exist_ok=True)

    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = main(argv)

    stdout_text = stdout.getvalue()
    stderr_text = stderr.getvalue()
    write_json(io_dir / "argv.json", argv)
    (io_dir / "stdout.json").write_text(stdout_text, encoding="utf-8")
    (io_dir / "stderr.txt").write_text(stderr_text, encoding="utf-8")

    try:
        payload = json.loads(stdout_text)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"CLI did not emit JSON. stderr={stderr_text!r}") from exc

    return exit_code, payload


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_manifest_case(run_root: Path, case_summary: dict[str, Any]) -> None:
    manifest_path = run_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["cases"].append(case_summary)
    write_json(manifest_path, manifest)


def write_case_fixture(
    case_dir: Path,
    *,
    case_name: str,
    kind: str,
    model_alias: str,
    expected_model: str,
    prompt_file: Path,
    submit_argv: list[str],
    wait_argv: list[str] | None = None,
    input_images: list[Path] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "case": case_name,
        "kind": kind,
        "modelAlias": model_alias,
        "expectedModel": expected_model,
        "promptFile": str(prompt_file),
        "inputImages": [str(path) for path in input_images or []],
        "requiresUpload": bool(input_images),
        "submitCommand": submit_argv,
    }
    if wait_argv is not None:
        payload["waitCommand"] = wait_argv
    write_json(case_dir / "case.json", payload)


def assert_live_submit_result(payload: dict[str, Any], *, expected_model: str, job_file: Path) -> None:
    assert payload["ok"] is True
    assert payload["model"] == expected_model
    assert payload["jobId"]
    assert payload["jobFile"] == str(job_file)
    assert job_file.is_file()


def assert_uploaded_media(payload: dict[str, Any], case_dir: Path) -> None:
    resolved_media = payload.get("resolvedMedia") or []
    assert resolved_media, "Expected resolved media entries for reference-image case"
    assert resolved_media[0]["uploaded"] is True
    assert resolved_media[0]["resolved_url"].startswith("http")
    write_json(case_dir / "input_media.json", resolved_media)


def wait_for_final_result(job_file: Path, case_dir: Path) -> dict[str, Any]:
    wait_argv = [
        "wait",
        "--job-file",
        str(job_file),
        "--poll-interval",
        live_poll_interval(),
        "--timeout",
        live_timeout(),
        "--json",
    ]
    wait_exit_code, final_payload = run_cli_json(wait_argv, case_dir / "wait")
    write_json(case_dir / "final.json", final_payload)

    assert wait_exit_code == 0
    assert final_payload["ok"] is True
    assert final_payload["status"] == "succeeded"
    assert final_payload.get("outputUrls"), "Expected final generated output URLs"
    assert all(str(url).startswith("http") for url in final_payload["outputUrls"])

    write_json(
        case_dir / "output_urls.json",
        {
            "jobId": final_payload["jobId"],
            "model": final_payload.get("model"),
            "status": final_payload["status"],
            "outputUrls": final_payload["outputUrls"],
        },
    )
    return final_payload


def assert_final_matches_submit(final_payload: dict[str, Any], submit_payload: dict[str, Any]) -> None:
    assert final_payload["jobId"] == submit_payload["jobId"]
    assert final_payload["model"] == submit_payload["model"]


def wait_for_suno_lyrics_result(job_id: str, case_dir: Path) -> dict[str, Any]:
    wait_argv = [
        "wait",
        job_id,
        "--model",
        "suno-lyrics",
        "--poll-interval",
        live_poll_interval(),
        "--timeout",
        live_timeout(),
        "--json",
    ]
    wait_exit_code, final_payload = run_cli_json(wait_argv, case_dir / "wait")
    write_json(case_dir / "final.json", final_payload)

    assert wait_exit_code == 0
    assert final_payload["ok"] is True
    assert final_payload["status"] == "succeeded"
    lyrics = final_payload.get("lyrics") or ((final_payload.get("response") or {}).get("data"))
    assert isinstance(lyrics, list) and lyrics, "Expected generated lyrics data"
    write_json(case_dir / "lyrics.json", lyrics)
    return final_payload


def run_suno_generation_case(
    run_root: Path,
    *,
    case_name: str,
    subcommand: str,
    prompt: str,
    expected_model: str,
    extra_args: list[str] | None = None,
    callback_required: bool = True,
) -> dict[str, Any]:
    require_scope("suno")
    case_dir = run_root / case_name
    job_file = case_dir / "job.json"

    submit_argv = ["suno", subcommand, "--prompt", prompt]
    submit_argv.extend(extra_args or [])
    callback_url = live_suno_callback_url() if callback_required else None
    if callback_url:
        submit_argv.extend(["--callback-url", callback_url])
    submit_argv.extend(["--save-job", str(job_file), "--json"])

    wait_argv = [
        "wait",
        "--job-file",
        str(job_file),
        "--poll-interval",
        live_poll_interval(),
        "--timeout",
        live_timeout(),
        "--json",
    ]
    write_case_fixture(
        case_dir,
        case_name=case_name,
        kind="suno",
        model_alias=subcommand,
        expected_model=expected_model,
        prompt_file=Path("<inline>"),
        submit_argv=submit_argv,
        wait_argv=wait_argv,
    )

    submit_exit_code, submit_payload = run_cli_json(submit_argv, case_dir / "submit")
    write_json(case_dir / "submit_payload.json", submit_payload)
    skip_transient_provider_maintenance(submit_payload)

    assert submit_exit_code == 0
    assert_live_submit_result(submit_payload, expected_model=expected_model, job_file=job_file)

    final_payload = wait_for_final_result(job_file, case_dir)
    assert_final_matches_submit(final_payload, submit_payload)

    append_manifest_case(
        run_root,
        {
            "case": case_name,
            "kind": "suno",
            "status": final_payload["status"],
            "jobId": final_payload["jobId"],
            "model": final_payload["model"],
            "outputUrls": final_payload["outputUrls"],
            "polls": final_payload.get("polls"),
            "elapsedSeconds": final_payload.get("elapsedSeconds"),
        },
    )
    return final_payload


def run_suno_lyrics_case(run_root: Path, *, case_name: str, prompt: str) -> dict[str, Any]:
    require_scope("suno")
    case_dir = run_root / case_name

    submit_argv = ["suno", "lyrics", "--prompt", prompt]
    callback_url = live_suno_callback_url()
    submit_argv.extend(["--callback-url", callback_url])
    submit_argv.append("--json")

    write_case_fixture(
        case_dir,
        case_name=case_name,
        kind="suno",
        model_alias="lyrics",
        expected_model="suno-lyrics",
        prompt_file=Path("<inline>"),
        submit_argv=submit_argv,
        wait_argv=[
            "wait",
            "<taskId>",
            "--model",
            "suno-lyrics",
            "--poll-interval",
            live_poll_interval(),
            "--timeout",
            live_timeout(),
            "--json",
        ],
    )

    submit_exit_code, submit_payload = run_cli_json(submit_argv, case_dir / "submit")
    write_json(case_dir / "submit_payload.json", submit_payload)
    skip_transient_provider_maintenance(submit_payload)

    assert submit_exit_code == 0
    assert submit_payload["ok"] is True
    assert submit_payload["model"] == "suno-lyrics"
    assert submit_payload["jobId"]

    final_payload = wait_for_suno_lyrics_result(submit_payload["jobId"], case_dir)
    assert_final_matches_submit(final_payload, submit_payload)

    append_manifest_case(
        run_root,
        {
            "case": case_name,
            "kind": "suno",
            "status": final_payload["status"],
            "jobId": final_payload["jobId"],
            "model": final_payload["model"],
            "lyricsCount": len(final_payload.get("lyrics") or []),
            "polls": final_payload.get("polls"),
            "elapsedSeconds": final_payload.get("elapsedSeconds"),
        },
    )
    return final_payload


def run_generation_case(
    run_root: Path,
    *,
    case_name: str,
    kind: str,
    model_alias: str,
    expected_model: str,
    prompt_file: Path,
    input_images: list[Path] | None = None,
) -> dict[str, Any]:
    require_scope(kind, "generation")
    case_dir = run_root / case_name
    job_file = case_dir / "job.json"

    command = "image" if kind == "image" else "video"
    submit_argv = [
        command,
        model_alias,
        "--prompt-file",
        str(prompt_file),
    ]
    for image in input_images or []:
        submit_argv.extend(["--image", str(image)])
    submit_argv.extend(["--save-job", str(job_file), "--json"])

    wait_argv = [
        "wait",
        "--job-file",
        str(job_file),
        "--poll-interval",
        live_poll_interval(),
        "--timeout",
        live_timeout(),
        "--json",
    ]
    write_case_fixture(
        case_dir,
        case_name=case_name,
        kind=kind,
        model_alias=model_alias,
        expected_model=expected_model,
        prompt_file=prompt_file,
        input_images=input_images,
        submit_argv=submit_argv,
        wait_argv=wait_argv,
    )

    submit_exit_code, submit_payload = run_cli_json(submit_argv, case_dir / "submit")
    assert submit_exit_code == 0
    assert_live_submit_result(submit_payload, expected_model=expected_model, job_file=job_file)

    if input_images:
        assert_uploaded_media(submit_payload, case_dir)

    final_payload = wait_for_final_result(job_file, case_dir)
    assert_final_matches_submit(final_payload, submit_payload)

    append_manifest_case(
        run_root,
        {
            "case": case_name,
            "kind": kind,
            "status": final_payload["status"],
            "jobId": final_payload["jobId"],
            "model": final_payload["model"],
            "outputUrls": final_payload["outputUrls"],
            "polls": final_payload.get("polls"),
            "elapsedSeconds": final_payload.get("elapsedSeconds"),
        },
    )
    return final_payload


def test_live_llm_prompt(run_root):
    require_scope("llm")
    case_name = "llm-prompt"
    case_dir = run_root / case_name
    prompt_file = PROMPTS / "llm_prompt.txt"
    argv = [
        "llm",
        "gpt-5-2",
        "--prompt-file",
        str(prompt_file),
        "--reasoning-effort",
        "low",
        "--json",
    ]
    write_case_fixture(
        case_dir,
        case_name=case_name,
        kind="llm",
        model_alias="gpt-5-2",
        expected_model="gpt-5-2",
        prompt_file=prompt_file,
        submit_argv=argv,
    )

    exit_code, payload = run_cli_json(argv, case_dir)
    write_json(case_dir / "final.json", payload)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["status"] == "succeeded"
    assert payload["model"] in {"gpt-5-2", "gpt-5.2"}
    assert payload.get("text")

    append_manifest_case(
        run_root,
        {
            "case": case_name,
            "kind": "llm",
            "status": payload["status"],
            "model": payload["model"],
            "hasText": bool(payload.get("text")),
        },
    )


def test_live_llm_vision_prompt(run_root):
    require_scope("llm")
    case_name = "llm-vision-prompt"
    case_dir = run_root / case_name
    prompt = "What do you see in this image?"
    input_image = IMAGES / "synthetic_reference_a.png"
    argv = [
        "llm",
        "gpt-5-2",
        "--prompt",
        prompt,
        "--image",
        str(input_image),
        "--reasoning-effort",
        "low",
        "--json",
    ]
    write_case_fixture(
        case_dir,
        case_name=case_name,
        kind="llm",
        model_alias="gpt-5-2",
        expected_model="gpt-5-2",
        prompt_file=Path("<inline>"),
        submit_argv=argv,
        input_images=[input_image],
    )

    exit_code, payload = run_cli_json(argv, case_dir)
    write_json(case_dir / "final.json", payload)
    assert_uploaded_media(payload, case_dir)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["status"] == "succeeded"
    assert payload["model"] in {"gpt-5-2", "gpt-5.2"}
    assert payload.get("text")

    append_manifest_case(
        run_root,
        {
            "case": case_name,
            "kind": "llm",
            "status": payload["status"],
            "model": payload["model"],
            "hasText": bool(payload.get("text")),
            "uploadedMedia": bool(payload.get("resolvedMedia")),
        },
    )


def test_live_gemini_vision_prompt(run_root):
    require_scope("gemini")
    case_name = "gemini-vision-prompt"
    case_dir = run_root / case_name
    prompt = "What do you see here? Describe in canonical pop culture detail as you see fit."
    input_image = IMAGES / "synthetic_reference_a.png"
    argv = [
        "gemini",
        "gemini-3-pro",
        "--prompt",
        prompt,
        "--image",
        str(input_image),
        "--reasoning-effort",
        "low",
        "--json",
    ]
    write_case_fixture(
        case_dir,
        case_name=case_name,
        kind="gemini",
        model_alias="gemini-3-pro",
        expected_model="gemini-3-pro",
        prompt_file=Path("<inline>"),
        submit_argv=argv,
        input_images=[input_image],
    )

    exit_code, payload = run_cli_json(argv, case_dir)
    write_json(case_dir / "final.json", payload)
    assert_uploaded_media(payload, case_dir)
    skip_transient_provider_maintenance(payload)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["status"] == "succeeded"
    assert payload["model"] in {"gemini-3-pro", "gemini-3-pro-preview"}
    assert payload.get("text")

    append_manifest_case(
        run_root,
        {
            "case": case_name,
            "kind": "gemini",
            "status": payload["status"],
            "model": payload["model"],
            "hasText": bool(payload.get("text")),
            "uploadedMedia": bool(payload.get("resolvedMedia")),
        },
    )


def skip_transient_provider_maintenance(payload: dict[str, Any]) -> None:
    raw = payload.get("raw") or {}
    error = payload.get("error") or {}
    message = " ".join(
        str(value)
        for value in [
            raw.get("msg") if isinstance(raw, dict) else None,
            error.get("message") if isinstance(error, dict) else None,
        ]
        if value
    ).lower()
    if "maintain" in message or "maintenance" in message:
        pytest.skip(f"KIE provider is temporarily unavailable: {message}")


def test_live_image_prompt_only(run_root):
    run_generation_case(
        run_root,
        case_name="image-prompt-only",
        kind="image",
        model_alias="gpt-image-2",
        expected_model="gpt-image-2-text-to-image",
        prompt_file=PROMPTS / "image_text_prompt.txt",
    )


def test_live_image_with_prompt(run_root):
    run_generation_case(
        run_root,
        case_name="image-with-prompt",
        kind="image",
        model_alias="gpt-image-2",
        expected_model="gpt-image-2-image-to-image",
        prompt_file=PROMPTS / "image_reference_prompt.txt",
        input_images=[IMAGES / "synthetic_reference_a.png"],
    )


def test_live_video_prompt_only(run_root):
    run_generation_case(
        run_root,
        case_name="video-prompt-only",
        kind="video",
        model_alias="grok",
        expected_model="grok-imagine/text-to-video",
        prompt_file=PROMPTS / "video_text_prompt.txt",
    )


def test_live_video_with_prompt(run_root):
    run_generation_case(
        run_root,
        case_name="video-with-prompt",
        kind="video",
        model_alias="grok",
        expected_model="grok-imagine/image-to-video",
        prompt_file=PROMPTS / "video_reference_prompt.txt",
        input_images=[IMAGES / "synthetic_reference_a.png"],
    )


def test_live_suno_music(run_root):
    run_suno_generation_case(
        run_root,
        case_name="suno-music",
        subcommand="music",
        prompt="A dreamy synth-pop song about neon rain.",
        expected_model="suno-music",
        extra_args=["--model", "V5_5"],
    )


def test_live_suno_lyrics(run_root):
    run_suno_lyrics_case(
        run_root,
        case_name="suno-lyrics",
        prompt="A nostalgic song about childhood memories in a small town.",
    )


def test_live_suno_sounds(run_root):
    run_suno_generation_case(
        run_root,
        case_name="suno-sounds",
        subcommand="sounds",
        prompt="A looping cyberpunk city ambience with distant sirens.",
        expected_model="suno-sounds",
        extra_args=["--model", "V5_5", "--sound-loop", "--sound-tempo", "110", "--sound-key", "Am"],
    )
