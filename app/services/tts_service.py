"""ElevenLabs text-to-speech service with browser-voice fallback."""
from __future__ import annotations

import urllib.request
import urllib.error
import json
from typing import Any, Generator

from app.core.config import settings

_ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"

# Curated default voices (stable IDs that exist on all ElevenLabs accounts)
DEFAULT_VOICES: list[dict[str, str]] = [
    {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah",       "description": "Soft, warm female"},
    {"voice_id": "TX3LPaxmHKxFdv7VOQHJ", "name": "Liam",        "description": "Calm, clear male"},
    {"voice_id": "pFZP5JQG7iQjIQuC4Bku", "name": "Lily",        "description": "Warm British female"},
    {"voice_id": "onwK4e9ZLuTAKqWW03F9", "name": "Daniel",      "description": "Deep, authoritative male"},
    {"voice_id": "XB0fDUnXU5powFXDhCwa", "name": "Charlotte",   "description": "Seductive British female"},
    {"voice_id": "nPczCjzI2devNBz1zQrb", "name": "Brian",       "description": "Deep American male"},
    {"voice_id": "cgSgspJ2msm6clMCkdW9", "name": "Jessica",     "description": "Expressive American female"},
    {"voice_id": "iP95p4xoKVk53GoZ742B", "name": "Chris",       "description": "Casual American male"},
]

# Speed → ElevenLabs speaking_rate mapping
# ElevenLabs accepts 0.7–1.2 for eleven_turbo_v2_5
def _clamp_speed(speed: float) -> float:
    return max(0.7, min(1.2, speed))


def _headers() -> dict[str, str]:
    return {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def is_configured() -> bool:
    """Returns True when an API key is present."""
    return bool(settings.elevenlabs_api_key)


def list_voices() -> list[dict[str, Any]]:
    """
    Fetch available voices from ElevenLabs.
    Falls back to DEFAULT_VOICES if the API call fails.
    """
    if not is_configured():
        return DEFAULT_VOICES

    try:
        req = urllib.request.Request(
            f"{_ELEVENLABS_BASE}/voices",
            headers=_headers(),
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        voices = data.get("voices", [])
        return [
            {
                "voice_id": v["voice_id"],
                "name": v["name"],
                "description": v.get("labels", {}).get("description", ""),
            }
            for v in voices
        ]
    except Exception:
        return DEFAULT_VOICES


def synthesize_stream(
    text: str,
    voice_id: str,
    stability: float = 0.5,
    similarity: float = 0.75,
    speed: float = 1.0,
) -> Generator[bytes, None, None]:
    """
    Stream MP3 audio chunks from ElevenLabs as they arrive.
    Yields raw bytes chunks so the browser can start playing immediately.
    Raises ValueError if not configured, RuntimeError on API failure.
    """
    if not is_configured():
        raise ValueError("ElevenLabs API key is not configured.")

    if len(text) > 5000:
        text = text[:5000]

    payload = json.dumps({
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity,
            "speed": _clamp_speed(speed),
        },
    }).encode("utf-8")

    stream_headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    req = urllib.request.Request(
        f"{_ELEVENLABS_BASE}/text-to-speech/{voice_id}/stream",
        data=payload,
        headers=stream_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                yield chunk
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"ElevenLabs error {exc.code}: {body}") from exc


def synthesize(
    text: str,
    voice_id: str,
    stability: float = 0.5,
    similarity: float = 0.75,
    speed: float = 1.0,
) -> bytes:
    """Convenience wrapper — collects the full stream into bytes."""
    return b"".join(synthesize_stream(text, voice_id, stability, similarity, speed))
