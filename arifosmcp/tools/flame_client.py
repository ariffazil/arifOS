"""
flame_client — DEPRECATED 2026-09-11 (FLAME decommissioned 2026-09-04)
═══════════════════════════════════════════════════════════════════════

DEPRECATION NOTICE
------------------
FLAME (Free-Loop AI Model Engine, :18901) was retired by sovereign decision
on 2026-09-04. The replacement substrate is `litellm-federation` at :7074
(FED FLAME FRAME v2). See:
  - A-FORGE commit 6df34922: `chore(submodules): remove retired flame submodule`
  - /root/backups/_CANONICAL/FLAME-retired-20260904/ (F1 AMANAH archive)
  - arifOS upgrade backlog 2026-09-11 (audit: SOT drift cleanup, P0)

This module is kept for import-compat. All calls now return None
(graceful degradation per architectural rule #2 below). Production callers
MUST migrate to the FED gateway or a domain-specific arifOS tool.

Architectural rules (Arif-ratified 2026-07-25):
  1. Strict timeout (8s) — never hang the kernel waiting for FLAME
  2. Graceful degradation — return raw context on failure, never crash
  3. Stateless request — self-contained payload per call
  4. ADVISORY authority — output tagged for F2 truth verification
  5. Prompt constraint — system prompt enforces fact-only extraction

Usage (LEGACY ONLY):
    from arifosmcp.tools.flame_client import flame_synthesize_search

    result = flame_synthesize_search(query, raw_results)
    # Returns None — module is deprecated. Migrate to FED gateway.

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

# DEPRECATED 2026-09-11: FLAME_API_BASE set to empty so all calls fail
# loudly with URLError and trigger the graceful-degradation path. This is
# the existing failure mode (FLAME :18901 has been down since 2026-09-04);
# we are making it explicit instead of misleading. Replace this module
# with a FED-gateway caller when migration is scheduled.
FLAME_API_BASE = ""
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

    DEPRECATED 2026-09-11: When FLAME_API_BASE is empty (deprecation active),
    bail out before urlopen() to avoid ValueError on unparseable URL and to
    avoid the buggy URLError handler below that touches HTTPError-only attrs.

    Args:
        endpoint: API path like '/completions'
        payload: JSON-serialisable dict — self-contained
        timeout_s: HTTP timeout in seconds (default 8)

    Returns:
        Parsed JSON dict, or None on any failure.
    """
    # DEPRECATED 2026-09-11 — FLAME retired. Bail out before any urlparse /
    # urlopen so callers get the documented graceful-None contract.
    if not FLAME_API_BASE:
        logger.debug(
            "flame_client: FLAME_API_BASE empty (deprecated 2026-09-11) — returning None for %s",
            endpoint,
        )
        return None
    url = f"{FLAME_API_BASE}{endpoint}"
    body = json.dumps(payload).encode("utf-8")

    if len(body) > MAX_BODY_CHARS * 4:
        logger.warning("flame_client: payload too large (%d bytes), truncating", len(body))
        body = body[: MAX_BODY_CHARS * 4]

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
                content = content[end + 8 :].strip()

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
