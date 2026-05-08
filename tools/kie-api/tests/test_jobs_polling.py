import pytest

from kie_cli.jobs import build_job_record, read_job_record, write_job_record
from kie_cli.polling import get_status_once, poll_until_complete
from kie_cli.routes import (
    MARKET_STATUS_ENDPOINT,
    MARKET_SUBMIT_ENDPOINT,
    SUNO_LYRICS_STATUS_ENDPOINT,
    SUNO_LYRICS_SUBMIT_ENDPOINT,
    SUNO_MUSIC_STATUS_ENDPOINT,
    SUNO_MUSIC_SUBMIT_ENDPOINT,
    SUNO_SOUNDS_SUBMIT_ENDPOINT,
    VEO_STATUS_ENDPOINT,
    VEO_SUBMIT_ENDPOINT,
    route_for_model,
)


class FakeStatusClient:
    def __init__(self, *, market=None, veo=None, suno_music=None, suno_lyrics=None):
        self.market = list(market or [])
        self.veo = list(veo or [])
        self.suno_music = list(suno_music or [])
        self.suno_lyrics = list(suno_lyrics or [])
        self.market_calls = []
        self.veo_calls = []
        self.suno_music_calls = []
        self.suno_lyrics_calls = []

    def get_market_task(self, task_id):
        self.market_calls.append(task_id)
        if not self.market:
            raise AssertionError("Unexpected Market status call")
        return self.market.pop(0)

    def get_veo_task(self, task_id):
        self.veo_calls.append(task_id)
        if not self.veo:
            raise AssertionError("Unexpected Veo status call")
        return self.veo.pop(0)

    def get_suno_music_task(self, task_id):
        self.suno_music_calls.append(task_id)
        if not self.suno_music:
            raise AssertionError("Unexpected Suno music status call")
        return self.suno_music.pop(0)

    def get_suno_lyrics_task(self, task_id):
        self.suno_lyrics_calls.append(task_id)
        if not self.suno_lyrics:
            raise AssertionError("Unexpected Suno lyrics status call")
        return self.suno_lyrics.pop(0)


def market_response(task_id, state, *, model="nano-banana-pro"):
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "taskId": task_id,
            "model": model,
            "state": state,
            "resultJson": '{"resultUrls":["https://example.com/out.png"]}' if state == "success" else None,
            "failCode": "FAILED" if state == "fail" else "",
            "failMsg": "failed for test" if state == "fail" else "",
        },
    }


def veo_response(task_id, success_flag):
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "taskId": task_id,
            "successFlag": success_flag,
            "response": {"resultUrls": ["https://example.com/out.mp4"]} if success_flag == 1 else {},
        },
    }


def test_route_for_market_model():
    route = route_for_model("nano-banana-pro")

    assert route.model == "nano-banana-pro"
    assert route.route == "market"
    assert route.submit_endpoint == MARKET_SUBMIT_ENDPOINT
    assert route.status_endpoint == MARKET_STATUS_ENDPOINT


def test_route_for_veo_model():
    route = route_for_model("veo3_fast")

    assert route.model == "veo3_fast"
    assert route.route == "veo"
    assert route.submit_endpoint == VEO_SUBMIT_ENDPOINT
    assert route.status_endpoint == VEO_STATUS_ENDPOINT


def test_route_for_suno_music_model():
    route = route_for_model("suno-music")

    assert route.model == "suno-music"
    assert route.route == "suno_music"
    assert route.submit_endpoint == SUNO_MUSIC_SUBMIT_ENDPOINT
    assert route.status_endpoint == SUNO_MUSIC_STATUS_ENDPOINT


def test_route_for_suno_sounds_model():
    route = route_for_model("suno-sounds")

    assert route.model == "suno-sounds"
    assert route.route == "suno_music"
    assert route.submit_endpoint == SUNO_SOUNDS_SUBMIT_ENDPOINT
    assert route.status_endpoint == SUNO_MUSIC_STATUS_ENDPOINT


def test_route_for_suno_lyrics_model():
    route = route_for_model("suno-lyrics")

    assert route.model == "suno-lyrics"
    assert route.route == "suno_lyrics"
    assert route.submit_endpoint == SUNO_LYRICS_SUBMIT_ENDPOINT
    assert route.status_endpoint == SUNO_LYRICS_STATUS_ENDPOINT


def test_route_for_unknown_model_raises():
    with pytest.raises(ValueError, match="Supported async models"):
        route_for_model("unknown-model")


def test_build_job_record_includes_schema_and_route_metadata():
    record = build_job_record(
        job_id="task_123",
        model="nano-banana-pro",
        submitted_payload={"model": "nano-banana-pro"},
        resolved_media=[{"source": "https://example.com/ref.png"}],
        raw_submit_response={"code": 200},
    )

    assert record.schemaVersion == 1
    assert record.jobId == "task_123"
    assert record.model == "nano-banana-pro"
    assert record.submitEndpoint == MARKET_SUBMIT_ENDPOINT
    assert record.statusEndpoint == MARKET_STATUS_ENDPOINT
    assert record.submittedPayload == {"model": "nano-banana-pro"}
    assert record.resolvedMedia == [{"source": "https://example.com/ref.png"}]
    assert record.rawSubmitResponse == {"code": 200}


def test_job_record_round_trip(tmp_path):
    record = build_job_record(job_id="veo_task_123", model="veo3_fast")
    path = write_job_record(record, tmp_path / "jobs" / "job.json")

    loaded = read_job_record(path)

    assert loaded == record


def test_get_status_once_routes_market_by_model():
    client = FakeStatusClient(market=[market_response("task_123", "success")])

    result = get_status_once(
        client=client,
        job_id="task_123",
        model="nano-banana-pro",
        market_normalizer=lambda response: {"status": response["data"]["state"], "jobId": response["data"]["taskId"]},
        veo_normalizer=lambda response: {"status": "should-not-run"},
    )

    assert result["jobId"] == "task_123"
    assert result["model"] == "nano-banana-pro"
    assert client.market_calls == ["task_123"]
    assert client.veo_calls == []


def test_get_status_once_routes_veo_by_model_even_with_non_veo_id():
    client = FakeStatusClient(veo=[veo_response("task_without_prefix", 1)])

    result = get_status_once(
        client=client,
        job_id="task_without_prefix",
        model="veo3_fast",
        market_normalizer=lambda response: {"status": "should-not-run"},
        veo_normalizer=lambda response: {"status": "succeeded", "jobId": response["data"]["taskId"]},
    )

    assert result["jobId"] == "task_without_prefix"
    assert result["model"] == "veo3_fast"
    assert client.market_calls == []
    assert client.veo_calls == ["task_without_prefix"]


def test_get_status_once_routes_suno_music_by_model():
    client = FakeStatusClient(
        suno_music=[
            {
                "code": 200,
                "msg": "success",
                "data": {
                    "taskId": "suno_music_123",
                    "status": "SUCCESS",
                    "response": {"sunoData": [{"audioUrl": "https://example.com/song.mp3"}]},
                },
            }
        ]
    )

    result = get_status_once(
        client=client,
        job_id="suno_music_123",
        model="suno-music",
        market_normalizer=lambda response: {"status": "should-not-run"},
        veo_normalizer=lambda response: {"status": "should-not-run"},
        suno_music_normalizer=lambda response, model=None: {
            "status": "succeeded",
            "jobId": response["data"]["taskId"],
            "model": model,
        },
    )

    assert result["jobId"] == "suno_music_123"
    assert result["model"] == "suno-music"
    assert client.suno_music_calls == ["suno_music_123"]
    assert client.market_calls == []
    assert client.veo_calls == []


def test_get_status_once_routes_suno_lyrics_by_model():
    client = FakeStatusClient(
        suno_lyrics=[
            {
                "code": 200,
                "msg": "success",
                "data": {
                    "taskId": "suno_lyrics_123",
                    "status": "SUCCESS",
                    "response": {"data": [{"text": "lyric", "title": "song", "status": "complete"}]},
                },
            }
        ]
    )

    result = get_status_once(
        client=client,
        job_id="suno_lyrics_123",
        model="suno-lyrics",
        market_normalizer=lambda response: {"status": "should-not-run"},
        veo_normalizer=lambda response: {"status": "should-not-run"},
        suno_music_normalizer=lambda response, model=None: {"status": "should-not-run"},
        suno_lyrics_normalizer=lambda response, model=None: {
            "status": "succeeded",
            "jobId": response["data"]["taskId"],
            "model": model,
        },
    )

    assert result["jobId"] == "suno_lyrics_123"
    assert result["model"] == "suno-lyrics"
    assert client.suno_lyrics_calls == ["suno_lyrics_123"]
    assert client.market_calls == []
    assert client.veo_calls == []


def test_poll_until_complete_queued_running_succeeded():
    client = FakeStatusClient(
        market=[
            market_response("task_123", "waiting"),
            market_response("task_123", "generating"),
            market_response("task_123", "success"),
        ]
    )
    now = {"value": 0.0}

    def clock():
        return now["value"]

    def sleep(seconds):
        now["value"] += seconds

    result = poll_until_complete(
        client=client,
        job_id="task_123",
        model="nano-banana-pro",
        market_normalizer=lambda response: {
            "ok": response["data"]["state"] != "fail",
            "jobId": response["data"]["taskId"],
            "status": {
                "waiting": "queued",
                "generating": "running",
                "success": "succeeded",
                "fail": "failed",
            }[response["data"]["state"]],
            "model": response["data"]["model"],
        },
        veo_normalizer=lambda response: {"status": "should-not-run"},
        poll_interval=2.0,
        timeout=10.0,
        sleep=sleep,
        clock=clock,
    )

    assert result["ok"] is True
    assert result["status"] == "succeeded"
    assert result["polls"] == 3
    assert result["elapsedSeconds"] == 4.0
    assert client.market_calls == ["task_123", "task_123", "task_123"]


def test_poll_until_complete_failed():
    client = FakeStatusClient(veo=[veo_response("veo_task_123", 2)])

    result = poll_until_complete(
        client=client,
        job_id="veo_task_123",
        model="veo3",
        market_normalizer=lambda response: {"status": "should-not-run"},
        veo_normalizer=lambda response: {
            "ok": False,
            "jobId": response["data"]["taskId"],
            "status": "failed",
            "error": {"code": "FAILED", "message": "failed for test"},
        },
        poll_interval=1.0,
        timeout=10.0,
        sleep=lambda seconds: None,
        clock=lambda: 0.0,
    )

    assert result["ok"] is False
    assert result["status"] == "failed"
    assert result["polls"] == 1
    assert result["error"]["message"] == "failed for test"


def test_poll_until_complete_timeout():
    client = FakeStatusClient(
        market=[
            market_response("task_123", "waiting"),
            market_response("task_123", "generating"),
        ]
    )
    times = iter([0.0, 0.0, 6.0])

    result = poll_until_complete(
        client=client,
        job_id="task_123",
        model="nano-banana-pro",
        market_normalizer=lambda response: {
            "ok": True,
            "jobId": response["data"]["taskId"],
            "status": "running",
            "model": response["data"]["model"],
        },
        veo_normalizer=lambda response: {"status": "should-not-run"},
        poll_interval=1.0,
        timeout=5.0,
        sleep=lambda seconds: None,
        clock=lambda: next(times),
    )

    assert result["ok"] is False
    assert result["status"] == "timeout"
    assert result["polls"] == 2
    assert result["lastStatus"]["status"] == "running"
    assert result["error"]["code"] == "POLL_TIMEOUT"


def test_poll_until_complete_suno_music_running_to_succeeded():
    client = FakeStatusClient(
        suno_music=[
            {"data": {"taskId": "suno_music_123", "status": "PENDING"}},
            {"data": {"taskId": "suno_music_123", "status": "FIRST_SUCCESS"}},
            {"data": {"taskId": "suno_music_123", "status": "SUCCESS"}},
        ]
    )
    now = {"value": 0.0}

    def clock():
        return now["value"]

    def sleep(seconds):
        now["value"] += seconds

    result = poll_until_complete(
        client=client,
        job_id="suno_music_123",
        model="suno-music",
        market_normalizer=lambda response: {"status": "should-not-run"},
        veo_normalizer=lambda response: {"status": "should-not-run"},
        suno_music_normalizer=lambda response, model=None: {
            "ok": True,
            "jobId": response["data"]["taskId"],
            "status": {
                "PENDING": "queued",
                "FIRST_SUCCESS": "running",
                "SUCCESS": "succeeded",
            }[response["data"]["status"]],
            "model": model,
        },
        poll_interval=2.0,
        timeout=10.0,
        sleep=sleep,
        clock=clock,
    )

    assert result["ok"] is True
    assert result["status"] == "succeeded"
    assert result["polls"] == 3
    assert result["elapsedSeconds"] == 4.0
    assert client.suno_music_calls == ["suno_music_123", "suno_music_123", "suno_music_123"]
