"""OpenAI-compatible LLM helpers for KIE chat completions."""

from __future__ import annotations

from typing import Any


GPT_5_2 = "gpt-5-2"
GEMINI_3_PRO = "gemini-3-pro"


def build_gpt_5_2_chat_payload(
    *,
    prompt: str,
    image_urls: list[str] | None = None,
    reasoning_effort: str = "high",
    web_search: bool = False,
    max_completion_tokens: int | None = None,
) -> dict[str, Any]:
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": prompt,
        }
    ]
    for image_url in image_urls or []:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
            }
        )

    payload: dict[str, Any] = {
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ],
        "reasoning_effort": reasoning_effort,
    }

    if max_completion_tokens is not None:
        payload["max_completion_tokens"] = max_completion_tokens

    if web_search:
        payload["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                },
            }
        ]

    return payload


def build_gemini_vision_payload(
    *,
    prompt: str,
    image_urls: list[str],
    reasoning_effort: str = "high",
    include_thoughts: bool = False,
    web_search: bool = False,
    stream: bool = False,
) -> dict[str, Any]:
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": prompt,
        }
    ]
    for image_url in image_urls:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
            }
        )

    payload: dict[str, Any] = {
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ],
        "stream": stream,
        "include_thoughts": include_thoughts,
        "reasoning_effort": reasoning_effort,
    }

    if web_search:
        payload["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": "googleSearch",
                },
            }
        ]

    return payload


def normalize_chat_completion(response: dict[str, Any], *, model: str = GPT_5_2) -> dict[str, Any]:
    choices = response.get("choices") or []
    text = ""
    finish_reason = None

    if choices:
        first_choice = choices[0] or {}
        message = first_choice.get("message") or {}
        content = message.get("content")
        finish_reason = first_choice.get("finish_reason")

        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            text = _extract_text_from_content_parts(content)

    if not text:
        return {
            "ok": False,
            "model": response.get("model") or model,
            "status": "failed",
            "error": {
                "code": "NO_COMPLETION_TEXT",
                "message": "Chat completion response did not include choices[0].message.content",
            },
            "raw": response,
        }

    return {
        "ok": True,
        "model": response.get("model") or model,
        "status": "succeeded",
        "text": text,
        "finishReason": finish_reason,
        "usage": response.get("usage"),
        "raw": response,
    }


def _extract_text_from_content_parts(parts: list[Any]) -> str:
    chunks: list[str] = []
    for part in parts:
        if isinstance(part, dict):
            value = part.get("text") or part.get("content")
            if isinstance(value, str):
                chunks.append(value)
        elif isinstance(part, str):
            chunks.append(part)
    return "".join(chunks)