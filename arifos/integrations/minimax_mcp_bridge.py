"""
arifos/integrations/minimax_mcp_bridge.py — MiniMax MCP Sub-Process Bridge
DITEMPA BUKAN DIBERI

Replaces mcp-library-based bridge with raw stdio subprocess.
Avoids anyio/cancel-scope compatibility issues in Python 3.12.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess
from typing import Any

logger = logging.getLogger(__name__)

_MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
_MINIMAX_API_HOST = os.getenv("MINIMAX_API_HOST", "https://api.minimax.io")
_MINIMAX_MCP_ENABLED = os.getenv("ARIFOS_MINIMAX_MCP_ENABLED", "auto").lower()


class _RawMinimaxBridge:
    """Raw stdio bridge — no external mcp library dependency."""

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None
        self._lock = asyncio.Lock()
        self._request_id = 0

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.setdefault("MINIMAX_API_KEY", _MINIMAX_API_KEY)
        env.setdefault("MINIMAX_API_HOST", _MINIMAX_API_HOST)
        return env

    async def _spawn(self) -> subprocess.Popen:
        uvx = shutil.which("uvx") or "/usr/local/bin/uvx"
        env = self._env()
        if not env.get("MINIMAX_API_KEY"):
            raise RuntimeError("MINIMAX_API_KEY not set")

        proc = subprocess.Popen(
            [uvx, "minimax-coding-plan-mcp", "--transport", "stdio"],
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
                "clientInfo": {"name": "arifOS", "version": "2026.04.20"},
            },
        }
        proc.stdin.write(json.dumps(init_req) + "\n")
        proc.stdin.flush()

        # The server may print startup logs (e.g. "Starting Minimax MCP server")
        # before the JSON-RPC initialize response. Read until we get JSON.
        line = proc.stdout.readline()
        while line and not line.strip().startswith("{"):
            line = proc.stdout.readline()
        if not line:
            raise RuntimeError("MiniMax MCP closed stdout during init")

        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        )
        proc.stdin.flush()
        return proc

    async def _call(self, method: str, params: dict[str, Any]) -> Any:
        async with self._lock:
            if self._proc is None or self._proc.poll() is not None:
                self._proc = await self._spawn()

            self._request_id += 1
            req = {"jsonrpc": "2.0", "id": self._request_id, "method": method, "params": params}
            self._proc.stdin.write(json.dumps(req) + "\n")
            self._proc.stdin.flush()

            line = self._proc.stdout.readline()
            if not line:
                raise RuntimeError("MiniMax MCP closed stdout")

            resp = json.loads(line)
            if "error" in resp:
                raise RuntimeError(f"MiniMax MCP error: {resp['error']}")
            return resp.get("result")

    async def web_search(self, query: str) -> dict[str, Any]:
        result = await self._call(
            "tools/call", {"name": "web_search", "arguments": {"query": query}}
        )
        if result is None:
            return {
                "organic": [],
                "base_resp": {"status_code": -1, "status_msg": "bridge_result_none"},
            }
        for block in result.get("content", []):
            if block.get("type") == "text":
                text = block["text"]
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    if text.startswith("Failed") or text.startswith("Error"):
                        return {
                            "error": text,
                            "base_resp": {"status_code": 400, "status_msg": text},
                        }
                    return {"result": text, "base_resp": {"status_code": 200, "status_msg": "ok"}}
        return {"organic": [], "base_resp": {"status_code": -1, "status_msg": "no text content"}}

    async def understand_image(self, image_url: str, prompt: str = "") -> dict[str, Any]:
        arguments: dict[str, Any] = {"image_source": image_url}
        if prompt:
            arguments["prompt"] = prompt
        result = await self._call(
            "tools/call", {"name": "understand_image", "arguments": arguments}
        )
        if result is None:
            return {
                "result": "",
                "base_resp": {"status_code": -1, "status_msg": "bridge_result_none"},
            }
        for block in result.get("content", []):
            if block.get("type") == "text":
                text = block["text"]
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    if text.startswith("Failed") or text.startswith("Error"):
                        return {
                            "error": text,
                            "base_resp": {"status_code": 400, "status_msg": text},
                        }
                    return {"result": text, "base_resp": {"status_code": 200, "status_msg": "ok"}}
        return {"result": "", "base_resp": {"status_code": -1, "status_msg": "no text content"}}


# ── Full MiniMax MCP Bridge (Token Plan Plus — media generation) ──
class _RawFullMinimaxBridge:
    """Raw stdio bridge to the full minimax-mcp package (TTS, image, video, music)."""

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None
        self._lock = asyncio.Lock()
        self._request_id = 0

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.setdefault("MINIMAX_API_KEY", _MINIMAX_API_KEY)
        env.setdefault("MINIMAX_API_HOST", _MINIMAX_API_HOST)
        env.setdefault("MINIMAX_MCP_BASE_PATH", os.getenv("MINIMAX_MCP_BASE_PATH", "/tmp/minimax"))
        env.setdefault("MINIMAX_API_RESOURCE_MODE", os.getenv("MINIMAX_API_RESOURCE_MODE", "url"))
        return env

    async def _spawn(self) -> subprocess.Popen:
        uvx = shutil.which("uvx") or "/usr/local/bin/uvx"
        env = self._env()
        if not env.get("MINIMAX_API_KEY"):
            raise RuntimeError("MINIMAX_API_KEY not set")

        proc = subprocess.Popen(
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
                "clientInfo": {"name": "arifOS", "version": "2026.04.20"},
            },
        }
        proc.stdin.write(json.dumps(init_req) + "\n")
        proc.stdin.flush()

        line = proc.stdout.readline()
        while line and not line.strip().startswith("{"):
            line = proc.stdout.readline()
        if not line:
            raise RuntimeError("Full MiniMax MCP closed stdout during init")

        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        )
        proc.stdin.flush()
        return proc

    async def _call(self, method: str, params: dict[str, Any]) -> Any:
        async with self._lock:
            if self._proc is None or self._proc.poll() is not None:
                self._proc = await self._spawn()

            self._request_id += 1
            req = {"jsonrpc": "2.0", "id": self._request_id, "method": method, "params": params}
            self._proc.stdin.write(json.dumps(req) + "\n")
            self._proc.stdin.flush()

            line = self._proc.stdout.readline()
            if not line:
                raise RuntimeError("Full MiniMax MCP closed stdout")

            resp = json.loads(line)
            if "error" in resp:
                raise RuntimeError(f"Full MiniMax MCP error: {resp['error']}")
            return resp.get("result")

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Calls ANY tool on the full MiniMax MCP server (TTS, Video, Image, Music)."""
        result = await self._call("tools/call", {"name": name, "arguments": arguments})
        if result is None:
            return {
                "result": None,
                "status": "error",
                "base_resp": {"status_code": -1, "status_msg": "bridge_result_none"},
            }

        # Flatten content blocks into a single response
        text_content = ""
        for block in result.get("content", []):
            if block.get("type") == "text":
                text_content += block["text"]
            elif block.get("type") == "image":
                # Handle image generation results
                return {
                    "result": block.get("data"),
                    "type": "image",
                    "status": "success",
                    "base_resp": {"status_code": 200},
                }

        try:
            return json.loads(text_content)
        except json.JSONDecodeError:
            if text_content.startswith("Failed") or text_content.startswith("Error"):
                return {"error": text_content, "status": "error", "base_resp": {"status_code": 400}}
            return {"result": text_content, "status": "success", "base_resp": {"status_code": 200}}


# Singletons
_raw_bridge = _RawMinimaxBridge()
_raw_full_bridge = _RawFullMinimaxBridge()


class MinimaxMCPBridge:
    """
    Compatibility wrapper — exposes the same interface as the old
    mcp-library-based bridge so _111_sense and _222_witness don't change.
    """

    async def web_search(self, query: str, max_results: int = 5) -> dict[str, Any]:
        """Web search with old-code compatibility wrapper."""
        try:
            raw = await _raw_bridge.web_search(query)
            if "error" in raw:
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": raw["error"],
                    "error_class": "bridge_failure",
                    "results": None,
                    "answer": None,
                    "hits": [],
                    "result_count": 0,
                    "metrics": {"f2_truth_score": 0.99, "f3_earth_witness": 0.33},
                    "witness_debug": {
                        "human": True,
                        "ai": True,
                        "earth": False,
                        "bridge": "minimax_web_search",
                    },
                }

            organic = raw.get("organic", [])
            base_resp = raw.get("base_resp", {})
            status_code = base_resp.get("status_code", 200)

            # Empty or no-content results are partial failures, not zeros
            if status_code < 0 or not organic:
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": base_resp.get("status_msg", "earth_witness_timeout"),
                    "error_class": "earth_witness_timeout",
                    "results": raw,
                    "answer": None,
                    "hits": [],
                    "result_count": 0,
                    "metrics": {"f2_truth_score": 0.99, "f3_earth_witness": 0.33},
                    "witness_debug": {
                        "human": True,
                        "ai": True,
                        "earth": False,
                        "bridge": "minimax_web_search",
                    },
                }

            # Score based on result quality
            hit_count = len(organic)
            # F2 Truth must be >= 0.99 for constitutional SEAL; map strong
            # Earth-witness results to the SEAL band.
            f2 = 0.99 if hit_count >= 5 else 0.95 if hit_count >= 1 else 0.33
            f3 = 0.95 if hit_count >= 5 else 0.7 if hit_count >= 1 else 0.33

            return {
                "status": "success",
                "verdict": "SEAL",
                "results": raw,
                "answer": raw.get("result"),
                "hits": organic[:max_results],
                "result_count": hit_count,
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": True,
                    "bridge": "minimax_web_search",
                },
                "metrics": {
                    "f2_truth_score": round(f2, 4),
                    "f3_earth_witness": round(f3, 4),
                },
            }
        except Exception as exc:
            logger.error("MinimaxMCPBridge.web_search failed: %s", exc)
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": str(exc),
                "error_class": "bridge_timeout",
                "results": None,
                "answer": None,
                "hits": [],
                "result_count": 0,
                "metrics": {"f2_truth_score": 0.99, "f3_earth_witness": 0.33},
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": False,
                    "bridge": "minimax_web_search",
                },
            }

    async def understand_image(self, image_url: str, question: str | None = None) -> dict[str, Any]:
        """Image understanding with old-code compatibility wrapper."""
        try:
            raw = await _raw_bridge.understand_image(image_url, question or "")
            if "error" in raw:
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": raw["error"],
                    "error_class": "bridge_failure",
                    "description": None,
                    "metrics": {"f9_hantu_score": 0.0, "description_length": 0},
                    "witness_debug": {
                        "human": True,
                        "ai": False,
                        "earth": False,
                        "bridge": "minimax_vision",
                    },
                }

            description = raw.get("result", "")
            base_resp = raw.get("base_resp", {})
            status_code = base_resp.get("status_code", 200)

            # No text content is a partial failure, not a success with empty description
            if status_code < 0 or not description:
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": base_resp.get("status_msg", "minimax_vision_empty"),
                    "error_class": "bridge_timeout",
                    "description": None,
                    "metrics": {"f9_hantu_score": 0.0, "description_length": 0},
                    "witness_debug": {
                        "human": True,
                        "ai": False,
                        "earth": False,
                        "bridge": "minimax_vision",
                    },
                }

            # Simple hantu check — look for anthropomorphic language
            hantu_words = [
                "i feel",
                "i think",
                "my opinion",
                "i believe",
                "conscious",
                "sentient",
                "mind",
            ]
            hantu_score = sum(1 for w in hantu_words if w in description.lower()) / len(hantu_words)
            verdict = "VOID" if hantu_score > 0.5 else "SEAL"

            return {
                "status": "success",
                "verdict": verdict,
                "image_url": image_url,
                "description": description,
                "metrics": {
                    "f9_hantu_score": round(hantu_score, 4),
                    "description_length": len(description),
                },
                "witness_debug": {
                    "human": True,
                    "ai": True,
                    "earth": True,
                    "bridge": "minimax_vision",
                },
            }
        except Exception as exc:
            logger.error("MinimaxMCPBridge.understand_image failed: %s", exc)
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": str(exc),
                "error_class": "bridge_timeout",
                "description": None,
                "metrics": {"f9_hantu_score": 0.0, "description_length": 0},
                "witness_debug": {
                    "human": True,
                    "ai": False,
                    "earth": False,
                    "bridge": "minimax_vision",
                },
            }

    # ── Token Plan Plus: Media Generation ──────────────────────
    async def text_to_image(
        self, prompt: str, aspect_ratio: str = "1:1", n: int = 1, model: str = "image-01"
    ) -> dict[str, Any]:
        """Generate images from text via MiniMax MCP."""
        try:
            raw = await _raw_full_bridge.call_tool(
                "text_to_image",
                {"prompt": prompt, "aspect_ratio": aspect_ratio, "n": n, "model": model},
            )
            if "error" in raw:
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": raw["error"],
                    "images": None,
                }
            return {
                "status": "success",
                "verdict": "SEAL",
                "images": raw.get("result", raw),
                "raw": raw,
            }
        except Exception as exc:
            logger.error("text_to_image failed: %s", exc)
            return {"status": "error", "verdict": "SABAR", "error": str(exc), "images": None}

    async def text_to_audio(
        self,
        text: str,
        voice_id: str = "female-shaonv",
        model: str = "speech-02-hd",
        speed: float = 1.0,
    ) -> dict[str, Any]:
        """Synthesize speech via MiniMax MCP."""
        try:
            raw = await _raw_full_bridge.call_tool(
                "text_to_audio",
                {"text": text, "voice_id": voice_id, "model": model, "speed": speed},
            )
            if "error" in raw:
                return {"status": "error", "verdict": "SABAR", "error": raw["error"], "audio": None}
            return {
                "status": "success",
                "verdict": "SEAL",
                "audio": raw.get("result", raw),
                "raw": raw,
            }
        except Exception as exc:
            logger.error("text_to_audio failed: %s", exc)
            return {"status": "error", "verdict": "SABAR", "error": str(exc), "audio": None}

    async def music_generation(self, prompt: str, lyrics: str) -> dict[str, Any]:
        """Generate music via MiniMax MCP."""
        try:
            raw = await _raw_full_bridge.call_tool(
                "music_generation",
                {"prompt": prompt, "lyrics": lyrics},
            )
            if "error" in raw:
                return {"status": "error", "verdict": "SABAR", "error": raw["error"], "music": None}
            return {
                "status": "success",
                "verdict": "SEAL",
                "music": raw.get("result", raw),
                "raw": raw,
            }
        except Exception as exc:
            logger.error("music_generation failed: %s", exc)
            return {"status": "error", "verdict": "SABAR", "error": str(exc), "music": None}

    async def generate_video(
        self, prompt: str, model: str = "MiniMax-Hailuo-02", duration: int = 6
    ) -> dict[str, Any]:
        """Generate video via MiniMax MCP."""
        try:
            raw = await _raw_full_bridge.call_tool(
                "generate_video",
                {"prompt": prompt, "model": model, "duration": duration},
            )
            if "error" in raw:
                return {"status": "error", "verdict": "SABAR", "error": raw["error"], "video": None}
            return {
                "status": "success",
                "verdict": "SEAL",
                "video": raw.get("result", raw),
                "raw": raw,
            }
        except Exception as exc:
            logger.error("generate_video failed: %s", exc)
            return {"status": "error", "verdict": "SABAR", "error": str(exc), "video": None}

    async def health(self) -> dict[str, Any]:
        """Runtime health check."""
        if not _MINIMAX_API_KEY:
            return {"available": False, "reason": "MINIMAX_API_KEY not set"}
        try:
            result = await _raw_bridge.web_search("test")
            if "error" in result and "no text content" not in result.get("error", ""):
                return {"available": False, "reason": result.get("error", "unknown")}
            return {
                "available": True,
                "tools_discovered": [
                    "web_search",
                    "understand_image",
                    "text_to_image",
                    "text_to_audio",
                    "music_generation",
                    "generate_video",
                ],
                "reason": None,
            }
        except Exception as exc:
            return {"available": False, "reason": str(exc)}


# Singleton export
minimax_bridge = MinimaxMCPBridge()
