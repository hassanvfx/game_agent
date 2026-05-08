import json

from kie_cli.cli import main
from kie_cli.llm import build_gemini_vision_payload, build_gpt_5_2_chat_payload, normalize_chat_completion


def test_build_gpt_5_2_chat_payload():
    payload = build_gpt_5_2_chat_payload(
        prompt="Write a tagline.",
        reasoning_effort="low",
    )

    assert payload == {
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": "Write a tagline."}],
            }
        ],
        "reasoning_effort": "low",
    }


def test_build_gpt_5_2_chat_payload_with_image():
    payload = build_gpt_5_2_chat_payload(
        prompt="What is in this image?",
        image_urls=["https://example.com/reference.png"],
        reasoning_effort="low",
    )

    assert payload == {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/reference.png"},
                    },
                ],
            }
        ],
        "reasoning_effort": "low",
    }


def test_build_gpt_5_2_chat_payload_with_web_search():
    payload = build_gpt_5_2_chat_payload(
        prompt="What changed today?",
        reasoning_effort="high",
        web_search=True,
    )

    assert payload["tools"] == [{"type": "function", "function": {"name": "web_search"}}]


def test_build_gpt_5_2_chat_payload_with_web_search_and_image():
    payload = build_gpt_5_2_chat_payload(
        prompt="What changed today?",
        image_urls=["https://example.com/reference.png"],
        reasoning_effort="high",
        web_search=True,
    )

    assert payload["tools"] == [{"type": "function", "function": {"name": "web_search"}}]
    assert payload["messages"][0]["content"][1] == {
        "type": "image_url",
        "image_url": {"url": "https://example.com/reference.png"},
    }


def test_build_gemini_vision_payload():
    payload = build_gemini_vision_payload(
        prompt="What do you see?",
        image_urls=["https://example.com/reference.png"],
        reasoning_effort="low",
    )

    assert payload == {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/reference.png"},
                    },
                ],
            }
        ],
        "stream": False,
        "include_thoughts": False,
        "reasoning_effort": "low",
    }


def test_build_gemini_vision_payload_with_web_search():
    payload = build_gemini_vision_payload(
        prompt="What current context matters?",
        image_urls=["https://example.com/reference.png"],
        web_search=True,
    )

    assert payload["tools"] == [{"type": "function", "function": {"name": "googleSearch"}}]


def test_normalize_chat_completion_success():
    result = normalize_chat_completion(
        {
            "id": "chatcmpl_123",
            "model": "gpt-5-2",
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Hello from KIE."},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 4, "total_tokens": 9},
        }
    )

    assert result["ok"] is True
    assert result["status"] == "succeeded"
    assert result["text"] == "Hello from KIE."
    assert result["usage"]["total_tokens"] == 9


def test_normalize_chat_completion_missing_text():
    result = normalize_chat_completion({"model": "gpt-5-2", "choices": []})

    assert result["ok"] is False
    assert result["status"] == "failed"
    assert result["error"]["code"] == "NO_COMPLETION_TEXT"


def test_cli_llm_dry_run_local_image(capsys):
    exit_code = main(
        [
            "llm",
            "gpt-5-2",
            "--prompt",
            "What do you see?",
            "--image",
            "tests/fixtures/images/synthetic_reference_a.png",
            "--reasoning-effort",
            "low",
            "--dry-run",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["status"] == "dry_run"
    assert output["model"] == "gpt-5-2"
    assert output["kind"] == "chat_completions"
    assert output["route"] == "chat_completions"
    assert output["resolvedMedia"][0]["uploaded"] is True
    assert output["resolvedMedia"][0]["resolved_url"] == "dry-run://uploaded/synthetic_reference_a.png"
    content = output["payload"]["messages"][0]["content"]
    assert content[0] == {"type": "text", "text": "What do you see?"}
    assert content[1] == {
        "type": "image_url",
        "image_url": {"url": "dry-run://uploaded/synthetic_reference_a.png"},
    }
    assert output["payload"]["reasoning_effort"] == "low"


def test_cli_gemini_dry_run_local_image(capsys):
    exit_code = main(
        [
            "gemini",
            "gemini-3-pro",
            "--prompt",
            "What do you see?",
            "--image",
            "tests/fixtures/images/synthetic_reference_a.png",
            "--reasoning-effort",
            "low",
            "--dry-run",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["status"] == "dry_run"
    assert output["model"] == "gemini-3-pro"
    assert output["route"] == "chat_completions"
    assert output["resolvedMedia"][0]["uploaded"] is True
    assert output["resolvedMedia"][0]["resolved_url"] == "dry-run://uploaded/synthetic_reference_a.png"
    content = output["payload"]["messages"][0]["content"]
    assert content[0] == {"type": "text", "text": "What do you see?"}
    assert content[1] == {
        "type": "image_url",
        "image_url": {"url": "dry-run://uploaded/synthetic_reference_a.png"},
    }
    assert output["payload"]["stream"] is False
    assert output["payload"]["include_thoughts"] is False
    assert output["payload"]["reasoning_effort"] == "low"


def test_cli_llm_dry_run(capsys):
    exit_code = main(
        [
            "llm",
            "gpt-5-2",
            "--prompt",
            "Write a tagline.",
            "--reasoning-effort",
            "low",
            "--dry-run",
            "--json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is True
    assert output["model"] == "gpt-5-2"
    assert output["kind"] == "chat_completions"
    assert output["payload"]["messages"][0]["content"][0]["text"] == "Write a tagline."
    assert output["payload"]["reasoning_effort"] == "low"