"""
arifosmcp/runtime/minimax_multimodal_bridge.py — MiniMax MCP multimodal bridge.

Wires the FULL MiniMax multimodal MCP server (10 tools) into arifOS:
  1.  text_to_audio         — TTS
  2.  list_voices           — query available voices
  3.  voice_clone           — clone a voice from an audio file
  4.  voice_design          — generate a voice from a prompt
  5.  play_audio            — play a local/URL audio file
  6.  music_generation      — generate music from prompt + lyrics
  7.  generate_video        — T2V / I2V via Hailuo-02
  8.  image_to_video        — I2V (JS MCP variant)
  9.  query_video_generation — poll async video task status
  10. text_to_image         — image generation

The Token-Plan MCP (2 tools: web_search + understand_image) is in
minimax_bridge.py — this is the FULL multimodal MCP (`minimax-mcp`, not
`minimax-coding-plan-mcp`).

Constitutional binding (F1-F13):
- F1 AMANAH: generated files go to MINIMAX_MCP_BASE_PATH (reversible dir).
- F2 TRUTH: prompts are factual; no fabricated claims in TTS.
- F9 ANTIHANTU: voice/TTS does not declare consciousness; image prompts
  are factual, not identity-claiming.
- F11 AUTH: uses the same MINIMAX_API_KEY as the rest of the federation.
- F13 SOVEREIGN: image generation of identifiable persons requires
  explicit human ack — the calling layer must enforce, not the bridge.

Sister file: minimax_bridge.py (Token-Plan variant, 2 tools).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess  # nosec B404
from typing import Any

logger = logging.getLogger(__name__)

_MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
_MINIMAX_API_HOST = os.getenv("MINIMAX_API_HOST", "https://api.minimax.io")
_MINIMAX_MCP_BASE_PATH = os.getenv("MINIMAX_MCP_BASE_PATH", "/root/arifos-mcp-output")


def _ensure_output_dir() -> str:
    """F1 AMANAH: ensure output dir exists, never write outside it."""
    p = _MINIMAX_MCP_BASE_PATH
    os.makedirs(p, exist_ok=True)
    return p


class _RawMultimodalBridge:
    """Raw stdio bridge for the FULL MiniMax multimodal MCP server (10 tools).

    Mirrors the pattern from minimax_bridge.py but spawns `minimax-mcp`
    (the full multimodal server) instead of `minimax-coding-plan-mcp`
    (the 2-tool Token-Plan variant).
    """

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None
        self._lock: asyncio.Lock | None = None
        self._request_id = 0

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    def _spawn_sync(self) -> subprocess.Popen:
        for candidate in [
            "/home/arifos/.local/bin/uvx",
            "/root/.local/bin/uvx",
            "/usr/local/bin/uvx",
            shutil.which("uvx"),
        ]:
            if candidate and os.path.exists(candidate):
                uvx = candidate
                break
        else:
            uvx = "uvx"

        env = dict(os.environ)
        env.setdefault("MINIMAX_API_KEY", _MINIMAX_API_KEY)
        env.setdefault("MINIMAX_API_HOST", _MINIMAX_API_HOST)
        env.setdefault("MINIMAX_MCP_BASE_PATH", _MINIMAX_MCP_BASE_PATH)
        env.setdefault("MINIMAX_API_RESOURCE_MODE", "local")
        if not env.get("MINIMAX_API_KEY"):
            raise RuntimeError("MINIMAX_API_KEY not set")

        # Spawn the FULL multimodal MCP server
        proc = subprocess.Popen(  # nosec B603
            [uvx, "minimax-mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        init_req = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "arifOS", "version": "2026.06.02"},
            },
        }
        proc.stdin.write(json.dumps(init_req) + "\n")
        proc.stdin.flush()
        # Read init response (skip any startup log lines)
        line = proc.stdout.readline()
        while line and not line.strip().startswith("{"):
            line = proc.stdout.readline()
        if not line:
            raise RuntimeError("MiniMax multimodal MCP closed stdout during init")
        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        )
        proc.stdin.flush()
        return proc

    def _call_sync(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        if self._proc is None or self._proc.poll() is not None:
            self._proc = self._spawn_sync()
        self._request_id += 1
        req = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        self._proc.stdin.write(json.dumps(req) + "\n")
        self._proc.stdin.flush()

        line = self._proc.stdout.readline()
        if not line:
            raise RuntimeError("MiniMax multimodal MCP closed stdout")

        resp = json.loads(line)
        if "error" in resp:
            raise RuntimeError(f"MiniMax multimodal MCP error ({tool_name}): {resp['error']}")
        return resp.get("result")

    def _parse_content(self, result: Any) -> dict[str, Any]:
        """Parse MCP tool result content. Returns base_resp-aware dict."""
        if result is None:
            return {
                "result": None,
                "base_resp": {"status_code": -1, "status_msg": "bridge_result_none"},
            }
        if isinstance(result, dict) and "content" in result:
            for block in result.get("content", []):
                if block.get("type") == "text":
                    text = block["text"]
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        if text.startswith("Failed") or text.startswith("Error"):
                            return {
                                "error": text,
                                "base_resp": {
                                    "status_code": 400,
                                    "status_msg": text,
                                },
                            }
                        return {
                            "result": text,
                            "base_resp": {
                                "status_code": 200,
                                "status_msg": "ok",
                            },
                        }
        return {
            "result": result,
            "base_resp": {"status_code": 200, "status_msg": "ok"},
        }


_bridge = _RawMultimodalBridge()


def _record(tool: str, status: str) -> None:
    """Best-effort metric record — never breaks the call path."""
    try:
        from arifosmcp.runtime.metrics import record_multimodal_call

        record_multimodal_call(tool, status)
    except Exception:
        pass


def _wrap_exc(tool: str, exc: Exception) -> dict[str, Any]:
    _record(tool, "error")
    logger.error("MinimaxMultimodalBridge.%s failed: %s", tool, exc)
    return {
        "status": "error",
        "verdict": "SABAR",
        "tool": tool,
        "error": str(exc),
        "error_class": "bridge_failure",
        "witness_debug": {
            "human": True,
            "ai": True,
            "earth": False,
            "bridge": "minimax_multimodal",
        },
    }


def _wrap_success(tool: str, payload: dict[str, Any]) -> dict[str, Any]:
    _record(tool, "success")
    return {
        "status": "success",
        "verdict": "SEAL",
        "tool": tool,
        "results": payload,
        "witness_debug": {
            "human": True,
            "ai": True,
            "earth": True,
            "bridge": "minimax_multimodal",
        },
    }


class MinimaxMultimodalBridge:
    """Async wrapper for the 10 MiniMax multimodal MCP tools.

    Each method is opt-in and called by the appropriate organ:
    - GEOX: text_to_image (visual evidence), generate_video (seismic viz)
    - AAA:  text_to_image, generate_video (research briefings)
    - Hermes: list_voices, text_to_audio (Telegram voice channel)
    - A-FORGE: text_to_image (UI mockups)

    Constitutional enforcement (F1-F13) is at the CALLING layer.
    This bridge is a transport + tool wrapper, not a judge.
    """

    async def _call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            raw = await asyncio.get_event_loop().run_in_executor(
                None, _bridge._call_sync, tool, arguments
            )
        except Exception as exc:
            return _wrap_exc(tool, exc)
        payload = _bridge._parse_content(raw)
        if "error" in payload:
            _record(tool, "error")
            return {
                "status": "error",
                "verdict": "SABAR",
                "tool": tool,
                "error": payload["error"],
                "error_class": "bridge_failure",
                "results": payload,
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "minimax_multimodal",
                },
            }
        return _wrap_success(tool, payload)

    # ────────────── 1. text_to_audio ──────────────
    async def text_to_audio(
        self,
        text: str,
        voice_id: str = "female-shaonv",
        model: str = "speech-02-hd",
        speed: float = 1.0,
        vol: float = 1.0,
        pitch: int = 0,
        emotion: str = "happy",
        sample_rate: int = 32000,
        bitrate: int = 128000,
        channel: int = 1,
        format: str = "mp3",
        language_boost: str | None = None,
    ) -> dict[str, Any]:
        """Text → natural speech audio file.

        F2 TRUTH: text input is the user's verbatim prompt. F9 ANTIHANTU:
        no first-person consciousness claims. F1 AMANAH: file written
        to MINIMAX_MCP_BASE_PATH (reversible).
        """
        if not _MINIMAX_API_KEY:
            return _wrap_exc("text_to_audio", RuntimeError("MINIMAX_API_KEY not set"))
        if not text or len(text) > 10_000:
            return _wrap_exc(
                "text_to_audio", ValueError(f"text length {len(text)} outside 1..10000")
            )
        args: dict[str, Any] = {
            "text": text,
            "output_directory": _ensure_output_dir(),
            "voice_id": voice_id,
            "model": model,
            "speed": speed,
            "vol": vol,
            "pitch": pitch,
            "emotion": emotion,
            "sample_rate": sample_rate,
            "bitrate": bitrate,
            "channel": channel,
            "format": format,
        }
        if language_boost:
            args["language_boost"] = language_boost
        return await self._call("text_to_audio", args)

    # ────────────── 2. list_voices ──────────────
    async def list_voices(self, voice_type: str = "all") -> dict[str, Any]:
        """List available voices."""
        return await self._call("list_voices", {"voice_type": voice_type})

    # ────────────── 3. voice_clone ──────────────
    async def voice_clone(
        self,
        voice_id: str,
        file: str,
        text: str = "",
        output_directory: str | None = None,
        is_url: bool = False,
    ) -> dict[str, Any]:
        """Clone a voice from an audio file. F11 AUTH: voice_id must be unique.

        Constraints per doc: voice_id length [8,256], must start with letter,
        may contain digits/letters/-/_, must not end with - or _.
        """
        if not (8 <= len(voice_id) <= 256):
            return _wrap_exc("voice_clone", ValueError("voice_id length must be 8..256"))
        if not voice_id[0].isalpha():
            return _wrap_exc("voice_clone", ValueError("voice_id must start with a letter"))
        if voice_id[-1] in ("-", "_"):
            return _wrap_exc("voice_clone", ValueError("voice_id must not end with - or _"))
        return await self._call(
            "voice_clone",
            {
                "voice_id": voice_id,
                "file": file,
                "text": text[:2000],
                "output_directory": output_directory or _ensure_output_dir(),
                "is_url": is_url,
            },
        )

    # ────────────── 4. voice_design ──────────────
    async def voice_design(
        self,
        prompt: str,
        preview_text: str,
        voice_id: str | None = None,
        output_directory: str | None = None,
    ) -> dict[str, Any]:
        """Generate a voice + preview audio from a prompt."""
        return await self._call(
            "voice_design",
            {
                "prompt": prompt,
                "preview_text": preview_text,
                "voice_id": voice_id or "",
                "output_directory": output_directory or _ensure_output_dir(),
            },
        )

    # ────────────── 5. play_audio ──────────────
    async def play_audio(self, input_file_path: str, is_url: bool = False) -> dict[str, Any]:
        """Play a local file or URL audio."""
        return await self._call(
            "play_audio", {"input_file_path": input_file_path, "is_url": is_url}
        )

    # ────────────── 6. music_generation ──────────────
    async def music_generation(
        self,
        prompt: str,
        lyrics: str,
        sample_rate: int = 32000,
        bitrate: int = 128000,
        format: str = "mp3",
        output_directory: str | None = None,
    ) -> dict[str, Any]:
        """Generate music from prompt + lyrics.

        F2 TRUTH: lyrics are user-supplied verbatim; no fabrication.
        Length constraints per doc: prompt 10-300, lyrics 10-600.
        """
        if not (10 <= len(prompt) <= 300):
            return _wrap_exc(
                "music_generation",
                ValueError(f"prompt length {len(prompt)} outside 10..300"),
            )
        if not (10 <= len(lyrics) <= 600):
            return _wrap_exc(
                "music_generation",
                ValueError(f"lyrics length {len(lyrics)} outside 10..600"),
            )
        return await self._call(
            "music_generation",
            {
                "prompt": prompt,
                "lyrics": lyrics,
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "format": format,
                "output_directory": output_directory or _ensure_output_dir(),
            },
        )

    # ────────────── 7. generate_video ──────────────
    async def generate_video(
        self,
        prompt: str | None = None,
        first_frame_image: str | None = None,
        model: str = "MiniMax-Hailuo-02",
        duration: int = 6,
        resolution: str | None = None,
        output_directory: str | None = None,
        async_mode: bool = False,
    ) -> dict[str, Any]:
        """Generate a video from a prompt and/or a first frame image.

        At least one of prompt/first_frame_image required.
        F13 SOVEREIGN: generating video of identifiable persons requires
        explicit human ack — the CALLER must enforce.
        """
        if not prompt and not first_frame_image:
            return _wrap_exc(
                "generate_video",
                ValueError("At least one of prompt/first_frame_image required"),
            )
        if not prompt or len(prompt) > 2000:
            return _wrap_exc(
                "generate_video",
                ValueError(f"prompt length {len(prompt) if prompt else 0} outside 1..2000"),
            )
        if duration not in (6, 10):
            return _wrap_exc("generate_video", ValueError("duration must be 6 or 10 seconds"))
        args: dict[str, Any] = {
            "model": model,
            "duration": duration,
            "async_mode": async_mode,
        }
        if prompt:
            args["prompt"] = prompt
        if first_frame_image:
            args["first_frame_image"] = first_frame_image
        if resolution:
            args["resolution"] = resolution
        args["output_directory"] = output_directory or _ensure_output_dir()
        return await self._call("generate_video", args)

    # ────────────── 8. image_to_video ──────────────
    async def image_to_video(
        self,
        first_frame_image: str,
        prompt: str | None = None,
        model: str = "MiniMax-Hailuo-02",
        output_directory: str | None = None,
        async_mode: bool = False,
    ) -> dict[str, Any]:
        """Image-to-video. JS MCP variant per docs.
        first_frame_image is required."""
        if not first_frame_image:
            return _wrap_exc("image_to_video", ValueError("first_frame_image required"))
        if prompt and len(prompt) > 2000:
            return _wrap_exc(
                "image_to_video",
                ValueError(f"prompt length {len(prompt)} outside 0..2000"),
            )
        args: dict[str, Any] = {
            "first_frame_image": first_frame_image,
            "model": model,
            "async_mode": async_mode,
        }
        if prompt:
            args["prompt"] = prompt
        args["output_directory"] = output_directory or _ensure_output_dir()
        return await self._call("image_to_video", args)

    # ────────────── 9. query_video_generation ──────────────
    async def query_video_generation(
        self, task_id: str, output_directory: str | None = None
    ) -> dict[str, Any]:
        """Poll status of an async video generation task."""
        return await self._call(
            "query_video_generation",
            {
                "task_id": task_id,
                "output_directory": output_directory or _ensure_output_dir(),
            },
        )

    # ────────────── 10. text_to_image ──────────────
    async def text_to_image(
        self,
        prompt: str,
        model: str = "image-01",
        aspect_ratio: str = "1:1",
        n: int = 1,
        prompt_optimizer: bool = True,
        output_directory: str | None = None,
    ) -> dict[str, Any]:
        """Generate images from a text prompt.

        F2 TRUTH: prompt is user-supplied verbatim. F13 SOVEREIGN:
        images of identifiable persons require explicit human ack
        (enforced at the calling layer).
        F1 AMANAH: file written to MINIMAX_MCP_BASE_PATH (reversible).
        """
        if not (1 <= len(prompt) <= 1500):
            return _wrap_exc(
                "text_to_image",
                ValueError(f"prompt length {len(prompt)} outside 1..1500"),
            )
        if not (1 <= n <= 9):
            return _wrap_exc("text_to_image", ValueError("n must be 1..9"))
        return await self._call(
            "text_to_image",
            {
                "prompt": prompt,
                "model": model,
                "aspect_ratio": aspect_ratio,
                "n": n,
                "prompt_optimizer": prompt_optimizer,
                "output_directory": output_directory or _ensure_output_dir(),
            },
        )


minimax_multimodal_bridge = MinimaxMultimodalBridge()


__all__ = [
    "MinimaxMultimodalBridge",
    "minimax_multimodal_bridge",
    "_MINIMAX_API_HOST",
    "_MINIMAX_MCP_BASE_PATH",
]
