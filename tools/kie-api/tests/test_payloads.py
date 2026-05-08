from kie_cli.payloads import (
    build_gpt_image_2_payload,
    build_grok_video_payload,
    build_nano_banana_pro_payload,
    build_suno_lyrics_payload,
    build_suno_music_payload,
    build_suno_sounds_payload,
    build_veo_payload,
)


def test_nano_banana_pro_payload_with_references():
    payload = build_nano_banana_pro_payload(
        prompt="make a poster",
        image_urls=["https://example.com/ref.png"],
        aspect_ratio="1:1",
        resolution="1K",
        output_format="png",
    )

    assert payload["model"] == "nano-banana-pro"
    assert payload["input"]["prompt"] == "make a poster"
    assert payload["input"]["image_input"] == ["https://example.com/ref.png"]
    assert payload["input"]["aspect_ratio"] == "1:1"


def test_gpt_image_2_text_payload_without_images():
    payload = build_gpt_image_2_payload(prompt="make an image")

    assert payload["model"] == "gpt-image-2-text-to-image"
    assert "input_urls" not in payload["input"]


def test_gpt_image_2_image_payload_with_images():
    payload = build_gpt_image_2_payload(
        prompt="edit this image",
        image_urls=["https://example.com/input.png"],
        aspect_ratio="16:9",
        resolution="2K",
    )

    assert payload["model"] == "gpt-image-2-image-to-image"
    assert payload["input"]["input_urls"] == ["https://example.com/input.png"]
    assert payload["input"]["resolution"] == "2K"


def test_grok_text_to_video_payload_without_images():
    payload = build_grok_video_payload(prompt="camera moves forward", aspect_ratio="2:3")

    assert payload["model"] == "grok-imagine/text-to-video"
    assert payload["input"]["duration"] == 6
    assert "image_urls" not in payload["input"]


def test_grok_image_to_video_payload_with_images():
    payload = build_grok_video_payload(
        prompt="@image1 animate this",
        image_urls=["https://example.com/ref.png"],
        duration=8,
        resolution="720p",
    )

    assert payload["model"] == "grok-imagine/image-to-video"
    assert payload["input"]["image_urls"] == ["https://example.com/ref.png"]
    assert payload["input"]["duration"] == "8"


def test_veo_payload_defaults_generation_type_from_images():
    payload = build_veo_payload(
        prompt="transition between frames",
        image_urls=["https://example.com/a.png", "https://example.com/b.png"],
        model="veo3_fast",
    )

    assert payload["model"] == "veo3_fast"
    assert payload["generationType"] == "FIRST_AND_LAST_FRAMES_2_VIDEO"
    assert payload["imageUrls"] == ["https://example.com/a.png", "https://example.com/b.png"]


def test_veo_payload_text_to_video_without_images():
    payload = build_veo_payload(prompt="a dog runs", model="veo3")

    assert payload["model"] == "veo3"
    assert payload["generationType"] == "TEXT_2_VIDEO"
    assert "imageUrls" not in payload


def test_suno_music_payload_includes_optional_fields():
    payload = build_suno_music_payload(
        prompt="dreamy synth-pop under neon rain",
        custom_mode=True,
        instrumental=True,
        model="V3_5",
        style="synth-pop",
        title="Neon Rain",
        negative_tags="harsh, noisy",
        callback_url="https://example.com/callback",
    )

    assert payload == {
        "prompt": "dreamy synth-pop under neon rain",
        "customMode": True,
        "instrumental": True,
        "model": "V3_5",
        "style": "synth-pop",
        "title": "Neon Rain",
        "negativeTags": "harsh, noisy",
        "callBackUrl": "https://example.com/callback",
    }


def test_suno_lyrics_payload_omits_callback_when_absent():
    payload = build_suno_lyrics_payload(prompt="a nostalgic song about small town summers")

    assert payload == {"prompt": "a nostalgic song about small town summers"}


def test_suno_sounds_payload_with_options():
    payload = build_suno_sounds_payload(
        prompt="looping cyberpunk ambience",
        model="V5_5",
        sound_loop=True,
        sound_tempo=110,
        sound_key="Am",
        grab_lyrics=True,
        callback_url="https://example.com/callback",
    )

    assert payload == {
        "prompt": "looping cyberpunk ambience",
        "soundLoop": True,
        "grabLyrics": True,
        "model": "V5_5",
        "soundTempo": 110,
        "soundKey": "Am",
        "callBackUrl": "https://example.com/callback",
    }
