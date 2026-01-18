"""
APEX_LLAMA MCP Tool - Call local Llama via Ollama.

This tool provides a thin, fail-open wrapper around a local Ollama
instance (e.g. `ollama run llama3`). It is intended for IDE / MCP
usage only and does NOT change core governance semantics.

Design:
- Reads prompt + optional model / max_tokens from request
- Calls Ollama HTTP API on localhost
- Returns raw model output as a structured response
- On error, returns an error field instead of raising
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from ..models import ApexLlamaRequest, ApexLlamaResponse


def _call_ollama(
    prompt: str,
    model: str,
    max_tokens: int,
    host: str = "http://localhost:11434",
    timeout: float = 60.0,
) -> str:
    """
    Call local Ollama HTTP API and return the generated text.

    This uses only Python stdlib to avoid new dependencies.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        # Ollama uses num_predict for max tokens in some versions; fall back gracefully.
        "num_predict": max_tokens,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=f"{host}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")

    # Ollama returns a single JSON object when stream=False
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        # Best-effort: return raw body
        return raw

    return obj.get("response", raw)


def apex_llama(request: ApexLlamaRequest) -> ApexLlamaResponse:
    """
    Call local Llama (via Ollama) and return the response.

    Fail-open behaviour:
    - On network / API errors, returns an ApexLlamaResponse with error populated.
    """
    start = time.time()
    try:
        output = _call_ollama(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
        )
        elapsed_ms = int((time.time() - start) * 1000)
        return ApexLlamaResponse(
            output=output,
            model=request.model,
            elapsed_ms=elapsed_ms,
            error=None,
        )
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        elapsed_ms = int((time.time() - start) * 1000)
        return ApexLlamaResponse(
            output="",
            model=request.model,
            elapsed_ms=elapsed_ms,
            error=f"Ollama error: {exc}",
        )
    except Exception as exc:  # pragma: no cover - safety net
        elapsed_ms = int((time.time() - start) * 1000)
        return ApexLlamaResponse(
            output="",
            model=request.model,
            elapsed_ms=elapsed_ms,
            error=f"APEX_LLAMA unexpected error: {exc}",
        )


__all__ = ["apex_llama"]

