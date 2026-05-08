import json

from kie_cli.cli import main
from kie_cli.media import resolve_media_inputs
from kie_cli.status import normalize_market_status, normalize_veo_status


def test_resolve_remote_url_without_upload():
    resolved = resolve_media_inputs(
        ["https://example.com/ref.png"],
        kind="image",
        dry_run=False,
    )

    assert resolved[0].source_type == "remote_url"
    assert resolved[0].resolved_url == "https://example.com/ref.png"
    assert resolved[0].uploaded is False


def test_resolve_local_path_dry_run_upload_placeholder():
    resolved = resolve_media_inputs(
        ["local.png"],
        kind="image",
        dry_run=True,
        upload_path="test/uploads",
    )

    assert resolved[0].source_type == "local_path"
    assert resolved[0].resolved_url == "dry-run://uploaded/local.png"
    assert resolved[0].uploaded is True
    assert resolved[0].upload == {"dryRun": True, "uploadPath": "test/uploads"}


def test_normalize_market_success_result_urls():
    result = normalize_market_status(
        {
            "code": 200,
            "msg": "success",
            "data": {
                "taskId": "task_123",
                "model": "nano-banana-pro",
                "state": "success",
                "resultJson": '{"resultUrls":["https://example.com/out.png"]}',
                "failCode": "",
                "failMsg": "",
            },
        }
    )

    assert result["ok"] is True
    assert result["status"] == "succeeded"
    assert result["outputUrl"] == "https://example.com/out.png"


def test_normalize_market_failure():
    result = normalize_market_status(
        {
            "code": 200,
            "msg": "success",
            "data": {
                "taskId": "task_123",
                "model": "grok-imagine/text-to-video",
                "state": "fail",
                "failCode": "GENERATION_FAILED",
                "failMsg": "bad prompt",
            },
        }
    )

    assert result["ok"] is False
    assert result["status"] == "failed"
    assert result["error"]["message"] == "bad prompt"


def test_normalize_veo_success():
    result = normalize_veo_status(
        {
            "code": 200,
            "msg": "success",
            "data": {
                "taskId": "veo_task_123",
                "successFlag": 1,
                "response": {"resultUrls": ["https://example.com/video.mp4"]},
            },
        }
    )

    assert result["ok"] is True
    assert result["status"] == "succeeded"
    assert result["outputUrl"] == "https://example.com/video.mp4"


def test_cli_dry_run_gpt_image_2_remote_url(capsys):
    exit_code = main(
        [
            "image",
            "gpt-image-2",
            "--prompt",
            "edit this",
            "--image",
            "https://example.com/input.png",
            "--dry-run",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["model"] == "gpt-image-2-image-to-image"
    assert output["payload"]["input"]["input_urls"] == ["https://example.com/input.png"]
    assert output["resolvedMedia"][0]["uploaded"] is False


def test_cli_dry_run_veo_local_images(capsys):
    exit_code = main(
        [
            "video",
            "veo3",
            "--prompt",
            "animate transition",
            "--image",
            "first.png",
            "--image",
            "last.png",
            "--dry-run",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["route"] == "veo"
    assert output["payload"]["generationType"] == "FIRST_AND_LAST_FRAMES_2_VIDEO"
    assert output["payload"]["imageUrls"] == [
        "dry-run://uploaded/first.png",
        "dry-run://uploaded/last.png",
    ]