"""
flame_client — FLAME Free-Loop HTTP Client for arifOS Kernel
═══════════════════════════════════════════════════════════════

Lightweight client for FLAME API (:18901). Duplicated from GEOX pattern
per F1 AMANAH — tight coupling between organs is forbidden.

Architectural rules (Arif-ratified 2026-07-25):
  1. Strict timeout (8s) — never hang the kernel waiting for FLAME
  2. Graceful degradation — return raw context on failure, never crash
  3. Stateless request — self-contained payload per call
  4. ADVISORY authority — output tagged for F2 truth verification
  5. Prompt constraint — system prompt enforces fact-only extraction

Usage:
    from arifosmcp.tools.flame_client import flame_synthesize_search

    result = flame_synthesize_search(query, raw_results)
    # Returns dict with ok, synthesis, provenance

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger("arifos.flame_client")

# ── Config ───────────────────────────────────────────────────────────────

FLAME_API_BASE = "http://127.0.0.1:18901"
DEFAULT_TIMEOUT_S = 8  # Strict: never hang kernel
MAX_BODY_CHARS = 8000

# F2 TRUTH: Fact-only extraction prompt constraint
_SYNTHESIS_SYSTEM_PROMPT = (
    "Extract and summarize facts only from the provided search results. "
    "Do not add external knowledge. Do not inject opinions. "
    "Do not speculate beyond what the search results contain. "
    "If the search results are empty or contradictory, state that clearly. "
    "Structure the output as: key findings, sources, and uncertainties."
)


# ── Internal ─────────────────────────────────────────────────────────────


def _flame_post(
    endpoint: str,
    payload: dict[str, Any],
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> dict[str, Any] | None:
    """POST to FLAME API with graceful degradation.

    Args:
        endpoint: API path like '/completions'
        payload: JSON-serialisable dict — self-contained
        timeout_s: HTTP timeout in seconds (default 8)

    Returns:
        Parsed JSON dict, or None on any failure.
    """
    url = f"{FLAME_API_BASE}{endpoint}"
    body = json.dumps(payload).encode("utf-8")

    if len(body) > MAX_BODY_CHARS * 4:
        logger.warning("flame_client: payload too large (%d bytes), truncating", len(body))
        body = body[:MAX_BODY_CHARS * 4]

    req = Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Caller-Id": "arifos",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=timeout_s) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            logger.debug(
                "flame_client: %s → ok=%s, latency_ms=%s",
                endpoint,
                result.get("ok", False),
                result.get("latency_ms", "?"),
            )
            return result
    except URLError as e:
        # FLAME returns 400 even when ok=True if "error" key exists
        try:
            body = e.read().decode("utf-8")
            result = json.loads(body)
            if result.get("ok"):
                logger.debug("flame_client: %s → HTTP %d but ok=True — accepting", endpoint, e.code)
                return result
        except Exception:
            pass
        reason = str(e.reason)[:200] if hasattr(e, "reason") else str(e)[:200]
        logger.warning("flame_client: HTTP %d on %s — %s", e.code, endpoint, reason)
        return None
    except TimeoutError:
        logger.warning("flame_client: timeout (%ds) on %s", timeout_s, endpoint)
        return None
    except json.JSONDecodeError:
        logger.warning("flame_client: non-JSON response from %s", endpoint)
        return None
    except Exception as e:
        logger.warning("flame_client: unexpected error on %s — %s", endpoint, str(e)[:200])
        return None


# ── Public API ───────────────────────────────────────────────────────────


def flame_synthesize_search(
    query: str,
    raw_results: list[dict[str, Any]],
    caller_id: str = "arifos_observe",
) -> dict[str, Any]:
    """Synthesize search results via FLAME.

    F2 TRUTH — fact-only extraction enforced via system prompt constraint.
    F1 AMANAH — returns raw context on FLAME failure, never crashes.

    Args:
        query: Original search query for context
        raw_results: List of raw search result dicts (from Brave/DDGS)
        caller_id: Identifier for FLAME audit trail

    Returns:
        Provenance envelope dict:
        {
            "ok": bool,
            "synthesis": str | None,  # FLAME synthesis if ok
            "raw_context": str,        # Always present — raw fallback
            "provenance": {
                "source": "FLAME" | "raw",
                "authority": "ADVISORY",
                "model": str,
                "provider": str,
                "latency_ms": float,
            }
        }
    """
    # Always build raw context fallback (graceful degradation)
    raw_lines: list[str] = []
    for i, r in enumerate(raw_results[:10], 1):
        title = r.get("title", r.get("name", ""))
        snippet = r.get("snippet", r.get("description", ""))
        url_str = r.get("url", r.get("link", ""))
        raw_lines.append(f"[{i}] {title}\n   {snippet}\n   Source: {url_str}")

    raw_context = "\n\n".join(raw_lines) if raw_lines else f"No results found for: {query}"

    if not raw_results:
        return {
            "ok": False,
            "synthesis": None,
            "raw_context": raw_context,
            "provenance": {
                "source": "raw",
                "authority": "ADVISORY",
                "note": "No results to synthesize",
            },
        }

    # Build synthesis prompt with F2 constraint
    prompt_lines = [
        f"Search query: {query[:500]}",
        "",
        "Raw search results:",
        raw_context,
        "",
        "Instruction: Extract and summarize facts only from these search results.",
        "Do not add external knowledge. Do not inject opinions.",
    ]
    prompt = "\n".join(prompt_lines)

    payload = {
        "prompt": prompt[:MAX_BODY_CHARS],
        "system": _SYNTHESIS_SYSTEM_PROMPT,
        "max_tokens": 1024,
        "temperature": 0.2,  # Low temperature for fact extraction
        "caller_id": caller_id,
        "sensitivity": "PUBLIC",
        "task_class": "extract",
    }

    result = _flame_post("/completions", payload)

    if result and result.get("ok"):
        content = result.get("content", "")

        # Strip think tags if present (Groq models add <think>...</think>)
        if content.startswith("<think>"):
            end = content.find("</think>")
            if end != -1:
                content = content[end + 8:].strip()

        return {
            "ok": True,
            "synthesis": content,
            "raw_context": raw_context,
            "provenance": {
                "source": "FLAME",
                "authority": "ADVISORY",  # F2: tagged as advisory
                "model": result.get("model", "unknown"),
                "provider": result.get("provider", "unknown"),
                "latency_ms": result.get("latency_ms", 0),
                "chain_id": result.get("chain_id", "RM0-TOOLS-FREELOOP"),
                "note": "FLAME output is advisory — not constitutional judgment",
            },
        }

    # Graceful degradation: return raw context
    return {
        "ok": False,
        "synthesis": None,
        "raw_context": raw_context,
        "provenance": {
            "source": "raw",
            "authority": "ADVISORY",
            "note": "FLAME unavailable — raw context returned",
        },
    }
