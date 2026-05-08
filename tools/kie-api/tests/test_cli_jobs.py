import json

from kie_cli import cli
from kie_cli.cli import main
from kie_cli.jobs import read_job_record


class FakeKieClient:
    market_submit_response = {"code": 200, "msg": "success", "data": {"taskId": "task_123"}}
    veo_submit_response = {"code": 200, "msg": "success", "data": {"taskId": "veo_task_123"}}
    suno_music_submit_response = {"code": 200, "msg": "success", "data": {"taskId": "suno_music_123"}}
    suno_lyrics_submit_response = {"code": 200, "msg": "success", "data": {"taskId": "suno_lyrics_123"}}
    suno_sounds_submit_response = {"code": 200, "msg": "success", "data": {"taskId": "suno_sounds_123"}}
    market_status_responses = []
    veo_status_responses = []
    suno_music_status_responses = []
    suno_lyrics_status_responses = []

    def __init__(self, config):
        self.config = config

    def create_market_task(self, payload):
        self.last_market_payload = payload
        return self.market_submit_response

    def create_veo_task(self, payload):
        self.last_veo_payload = payload
        return self.veo_submit_response

    def create_suno_music_task(self, payload):
        self.last_suno_music_payload = payload
        return self.suno_music_submit_response

    def create_suno_lyrics_task(self, payload):
        self.last_suno_lyrics_payload = payload
        return self.suno_lyrics_submit_response

    def create_suno_sounds_task(self, payload):
        self.last_suno_sounds_payload = payload
        return self.suno_sounds_submit_response

    def get_market_task(self, task_id):
        if not self.market_status_responses:
            raise AssertionError("Unexpected Market status call")
        return self.market_status_responses.pop(0)

    def get_veo_task(self, task_id):
        if not self.veo_status_responses:
            raise AssertionError("Unexpected Veo status call")
        return self.veo_status_responses.pop(0)

    def get_suno_music_task(self, task_id):
        if not self.suno_music_status_responses:
            raise AssertionError("Unexpected Suno music status call")
        return self.suno_music_status_responses.pop(0)

    def get_suno_lyrics_task(self, task_id):
        if not self.suno_lyrics_status_responses:
            raise AssertionError("Unexpected Suno lyrics status call")
        return self.suno_lyrics_status_responses.pop(0)


def fake_config():
    return object()


def market_status(task_id="task_123", state="success", model="nano-banana-pro"):
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "taskId": task_id,
            "model": model,
            "state": state,
            "resultJson": '{"resultUrls":["https://example.com/out.png"]}',
            "failCode": "",
            "failMsg": "",
        },
    }


def veo_status(task_id="veo_task_123", success_flag=1):
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "taskId": task_id,
            "successFlag": success_flag,
            "response": {"resultUrls": ["https://example.com/out.mp4"]},
        },
    }


def install_fake_client(monkeypatch):
    FakeKieClient.market_status_responses = []
    FakeKieClient.veo_status_responses = []
    FakeKieClient.suno_music_status_responses = []
    FakeKieClient.suno_lyrics_status_responses = []
    monkeypatch.setattr(cli, "load_config", fake_config)
    monkeypatch.setattr(cli, "KieClient", FakeKieClient)


def test_cli_wait_requires_model_without_job_file(monkeypatch, capsys):
    install_fake_client(monkeypatch)

    exit_code = main(["wait", "task_123", "--json"])

    assert exit_code == 1
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is False
    assert "JOB_ID with --model" in output["error"]["message"]


def test_cli_wait_job_file_reads_job_id_and_model(monkeypatch, tmp_path, capsys):
    install_fake_client(monkeypatch)
    FakeKieClient.veo_status_responses = [veo_status(task_id="plain_task_id")]
    job_file = tmp_path / "job.json"
    job_file.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "jobId": "plain_task_id",
                "model": "veo3_fast",
                "status": "queued",
                "submittedAt": "2026-04-29T00:00:00Z",
                "submitEndpoint": "/api/v1/veo/generate",
                "statusEndpoint": "/api/v1/veo/record-info",
                "submittedPayload": {},
                "resolvedMedia": [],
                "rawSubmitResponse": {},
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "wait",
            "--job-file",
            str(job_file),
            "--poll-interval",
            "0",
            "--timeout",
            "1",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["jobId"] == "plain_task_id"
    assert output["model"] == "veo3_fast"
    assert output["status"] == "succeeded"


def test_cli_image_save_job_writes_record(monkeypatch, tmp_path, capsys):
    install_fake_client(monkeypatch)
    job_file = tmp_path / "jobs" / "image-job.json"

    exit_code = main(
        [
            "image",
            "nano-banana-pro",
            "--prompt",
            "KIE_TEST_IMAGE_TEXT_PROMPT_V1",
            "--save-job",
            str(job_file),
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["jobId"] == "task_123"
    assert output["jobFile"] == str(job_file)

    record = read_job_record(job_file)
    assert record.jobId == "task_123"
    assert record.model == "nano-banana-pro"
    assert record.submitEndpoint == "/api/v1/jobs/createTask"
    assert record.statusEndpoint == "/api/v1/jobs/recordInfo"
    assert record.submittedPayload["model"] == "nano-banana-pro"
    assert record.rawSubmitResponse == FakeKieClient.market_submit_response


def test_cli_video_veo_save_job_writes_record(monkeypatch, tmp_path, capsys):
    install_fake_client(monkeypatch)
    job_file = tmp_path / "jobs" / "veo-job.json"

    exit_code = main(
        [
            "video",
            "veo3",
            "--prompt",
            "KIE_TEST_VIDEO_TEXT_PROMPT_V1",
            "--veo-model",
            "veo3_fast",
            "--save-job",
            str(job_file),
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["jobId"] == "veo_task_123"
    assert output["jobFile"] == str(job_file)

    record = read_job_record(job_file)
    assert record.jobId == "veo_task_123"
    assert record.model == "veo3_fast"
    assert record.submitEndpoint == "/api/v1/veo/generate"
    assert record.statusEndpoint == "/api/v1/veo/record-info"
    assert record.submittedPayload["model"] == "veo3_fast"
    assert record.rawSubmitResponse == FakeKieClient.veo_submit_response


def test_cli_suno_music_dry_run_json(monkeypatch, capsys):
    install_fake_client(monkeypatch)

    exit_code = main(
        [
            "suno",
            "music",
            "--prompt",
            "A dreamy synth-pop song about neon rain",
            "--custom-mode",
            "--instrumental",
            "--style",
            "synth-pop",
            "--title",
            "Neon Rain",
            "--negative-tags",
            "harsh, noisy",
            "--json",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "dry_run"
    assert output["model"] == "suno-music"
    assert output["route"] == "suno_music"
    assert output["payload"]["prompt"] == "A dreamy synth-pop song about neon rain"
    assert output["payload"]["customMode"] is True
    assert output["payload"]["instrumental"] is True
    assert output["payload"]["style"] == "synth-pop"


def test_cli_suno_lyrics_dry_run_json(monkeypatch, tmp_path, capsys):
    install_fake_client(monkeypatch)
    prompt_file = tmp_path / "lyrics-prompt.txt"
    prompt_file.write_text("A nostalgic song about childhood memories", encoding="utf-8")

    exit_code = main(
        [
            "suno",
            "lyrics",
            "--prompt-file",
            str(prompt_file),
            "--json",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "dry_run"
    assert output["model"] == "suno-lyrics"
    assert output["route"] == "suno_lyrics"
    assert output["payload"] == {"prompt": "A nostalgic song about childhood memories"}


def test_cli_suno_sounds_save_job_writes_record(monkeypatch, tmp_path, capsys):
    install_fake_client(monkeypatch)
    job_file = tmp_path / "jobs" / "suno-sounds-job.json"

    exit_code = main(
        [
            "suno",
            "sounds",
            "--prompt",
            "A looping cyberpunk city ambience with distant sirens",
            "--model",
            "V5_5",
            "--sound-loop",
            "--sound-tempo",
            "110",
            "--sound-key",
            "Am",
            "--grab-lyrics",
            "--save-job",
            str(job_file),
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["jobId"] == "suno_sounds_123"
    assert output["jobFile"] == str(job_file)

    record = read_job_record(job_file)
    assert record.jobId == "suno_sounds_123"
    assert record.model == "suno-sounds"
    assert record.submitEndpoint == "/api/v1/generate/sounds"
    assert record.statusEndpoint == "/api/v1/generate/record-info"
    assert record.submittedPayload["model"] == "V5_5"
    assert record.submittedPayload["soundLoop"] is True
    assert record.rawSubmitResponse == FakeKieClient.suno_sounds_submit_response


def test_cli_job_status_suno_music_by_model(monkeypatch, capsys):
    install_fake_client(monkeypatch)
    FakeKieClient.suno_music_status_responses = [
        {
            "code": 200,
            "msg": "success",
            "data": {
                "taskId": "suno_music_123",
                "status": "SUCCESS",
                "response": {"sunoData": [{"audioUrl": "https://example.com/song.mp3"}]},
                "type": "MUSIC",
                "errorCode": None,
                "errorMessage": None,
            },
        }
    ]

    exit_code = main(["job-status", "suno_music_123", "--model", "suno-music", "--json"])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["jobId"] == "suno_music_123"
    assert output["status"] == "succeeded"
    assert output["outputUrl"] == "https://example.com/song.mp3"
    assert output["model"] == "suno-music"
