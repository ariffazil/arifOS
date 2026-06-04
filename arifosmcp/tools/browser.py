"""
arifosmcp/tools/browser.py — 111_SENSE Browser Layer (Governed Playwright)

Browser automation tool with observe/interact separation.
- browser_observe: pure extraction (navigate, scroll, screenshot, extract_dom)
  → OBSERVE risk class, no human ack required
- browser_interact: form fills, clicks, multi-step flows
  → INTERACT risk class, requires explicit human ack (F1 Amanah)

DITEMPA BUKAN DIBERI — 999 SEAL
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from typing import Any

from arifosmcp.constitutional_map import RiskClass
from arifosmcp.core.floors import evaluate_tool_call
from arifosmcp.integrations.playwright_bridge import playwright_bridge
from arifosmcp.runtime.model import RuntimeEnvelope as _RE

logger = logging.getLogger(__name__)

# ─── Constitutional Guardrail Helpers ───────────────────────────────────────

INJECTION_PATTERNS = [
    "<script",
    "javascript:",
    "onerror=",
    "onload=",
    "onclick=",
    "data:text/html",
    "vbscript:",
]


def _f_web_scan(content: str) -> tuple[bool, str]:
    """Scan content for F-WEB injection patterns. Returns (clean, reason)."""
    if not content:
        return True, ""
    lower = content.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern.lower() in lower:
            return False, f"F-WEB injection pattern detected: {pattern}"
    return True, ""


def _evidence_receipt(
    action: str,
    url: str,
    status: str,
    payload: dict[str, Any],
    notes: str = "",
) -> dict[str, Any]:
    """Create a structured evidence receipt for VAULT999 / audit trail."""
    return {
        "receipt_id": f"brw_{hashlib.sha256(f'{action}{url}{datetime.now(UTC).isoformat()}'.encode()).hexdigest()[:16]}",
        "action": action,
        "url": url,
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "payload_hash": hashlib.sha256(str(payload).encode()).hexdigest()[:16],
        "notes": notes,
    }


# ─── Tool Implementations ────────────────────────────────────────────────────

OBSERVE_ALLOWED_ACTIONS = {
    "navigate",
    "wait_for_selector",
    "scroll",
    "extract_dom",
    "screenshot",
    "get_cookies",
    "go_back",
    "go_forward",
    "reload",
}

INTERACT_ALLOWED_ACTIONS = OBSERVE_ALLOWED_ACTIONS | {
    "click",
    "fill",
    "press",
    "select_option",
    "check",
    "uncheck",
    "submit",
    "set_input_files",
}


async def arif_browser_observe(
    url: str,
    actions: list[str] | None = None,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    actor_id: str = "anonymous",
    session_id: str | None = None,
) -> _RE:
    """
    Browser observe — pure extraction, no state mutation.

    Allowed actions: navigate, wait_for_selector, scroll, extract_dom,
    screenshot, get_cookies, go_back, go_forward, reload.

    Risk: LOW (OBSERVE). No human ack required.
    Constitutional floors: F2 (truth), F9 (anti-hantu), F12 (injection guard).
    """
    actions = actions or ["navigate", "extract_dom"]

    # 1. Constitutional pre-check
    gov = evaluate_tool_call(
        action="browser_observe",
        tool_name="arif_browser_observe",
        parameters={"url": url, "actions": actions},
        actor_id=actor_id,
        session_id=session_id,
    )
    if gov.verdict != "SEAL":
        return _RE(
            ok=False,
            tool="arif.browser_observe",
            canonical_tool_name="arif.browser_observe",
            stage="111_SENSE",
            verdict=gov.verdict,
            detail=gov.message,
            payload={"violations": gov.violations},
            risk_class=RiskClass.LOW,
        )

    # 2. Validate actions are observe-only
    invalid_actions = [a for a in actions if a not in OBSERVE_ALLOWED_ACTIONS]
    if invalid_actions:
        return _RE(
            ok=False,
            tool="arif.browser_observe",
            stage="111_SENSE",
            verdict="HOLD",
            detail=f"Invalid observe actions: {invalid_actions}. Use browser_interact for clicks/fills.",
            risk_class=RiskClass.LOW,
        )

    # 3. F-WEB pre-scan URL
    clean_url, url_reason = _f_web_scan(url)
    if not clean_url:
        return _RE(
            ok=False,
            tool="arif.browser_observe",
            stage="111_SENSE",
            verdict="VOID",
            detail=f"URL failed F-WEB scan: {url_reason}",
            risk_class=RiskClass.MEDIUM,
        )

    # 4. Execute browser observe sequence
    try:
        results = []
        for action in actions:
            result = await playwright_bridge.call_browser_tool(action, {"url": url})
            if "error" in result:
                results.append({"action": action, "status": "ERROR", "error": result["error"]})
            else:
                # F-WEB post-scan on content
                content = str(result.get("content", result.get("result", "")))
                clean, scan_reason = _f_web_scan(content)
                if not clean:
                    results.append(
                        {
                            "action": action,
                            "status": "FLAGGED",
                            "f_web_scan": "FAIL",
                            "reason": scan_reason,
                        }
                    )
                else:
                    results.append({"action": action, "status": "OK", "result": result})

        receipt = _evidence_receipt(
            "browser_observe", url, "SEAL", {"actions": actions, "results": results}
        )

        return _RE(
            ok=True,
            tool="arif.browser_observe",
            stage="111_SENSE",
            verdict="SEAL",
            payload={
                "url": url,
                "actions": actions,
                "results": results,
                "evidence_receipt": receipt,
            },
            risk_class=RiskClass.LOW,
        )

    except Exception as e:
        logger.error(f"Browser observe failed: {e}")
        return _RE(
            ok=False,
            tool="arif.browser_observe",
            stage="111_SENSE",
            verdict="VOID",
            detail=f"Browser automation error: {str(e)[:200]}",
            risk_class=RiskClass.MEDIUM,
        )


async def arif_browser_interact(
    url: str,
    actions: list[str],
    max_steps: int = 10,
    actor_id: str = "anonymous",
    session_id: str | None = None,
    ack_irreversible: bool = False,
) -> _RE:
    """
    Browser interact — state-mutating browser actions (click, fill, submit, etc.)

    Risk: HIGH (INTERACT). Requires explicit human ack via ack_irreversible=True.

    Constitutional floors: F1 (amanah/irreversible), F2 (truth), F6 (dignity),
    F9 (anti-hantu), F12 (injection guard), F13 (sovereign veto).

    This tool MUST NOT be called without explicit human authorization.
    """
    # 1. HARD GATE: F1 Amanah — irreversible actions require explicit ack
    if not ack_irreversible:
        return _RE(
            ok=False,
            tool="arif.browser_interact",
            canonical_tool_name="arif.browser_interact",
            stage="111_SENSE",
            verdict="HOLD",
            detail=(
                "F1 AMANAH: browser_interact is a potentially irreversible operation. "
                "Requires explicit ack_irreversible=True and human authorization. "
                "Use browser_observe for read-only operations."
            ),
            risk_class=RiskClass.HIGH,
        )

    # 2. Constitutional pre-check
    gov = evaluate_tool_call(
        action="browser_interact",
        tool_name="arif_browser_interact",
        parameters={"url": url, "actions": actions, "max_steps": max_steps},
        actor_id=actor_id,
        session_id=session_id,
    )
    if gov.verdict not in ("SEAL", "SABAR"):
        return _RE(
            ok=False,
            tool="arif.browser_interact",
            stage="111_SENSE",
            verdict=gov.verdict,
            detail=gov.message,
            payload={"violations": gov.violations},
            risk_class=RiskClass.HIGH,
        )

    # 3. Validate actions include at least one interact-mode action
    interact_actions = [a for a in actions if a in INTERACT_ALLOWED_ACTIONS]
    if not interact_actions:
        return _RE(
            ok=False,
            tool="arif.browser_interact",
            stage="111_SENSE",
            verdict="HOLD",
            detail="No interact-mode actions specified. Use browser_observe.",
            risk_class=RiskClass.HIGH,
        )

    # 4. F-WEB pre-scan URL
    clean_url, url_reason = _f_web_scan(url)
    if not clean_url:
        return _RE(
            ok=False,
            tool="arif.browser_interact",
            stage="111_SENSE",
            verdict="VOID",
            detail=f"URL failed F-WEB scan: {url_reason}",
            risk_class=RiskClass.HIGH,
        )

    # 5. Step limit guard
    if max_steps > 20:
        return _RE(
            ok=False,
            tool="arif.browser_interact",
            stage="111_SENSE",
            verdict="HOLD",
            detail=f"max_steps={max_steps} exceeds safety limit (20). Reduce steps.",
            risk_class=RiskClass.HIGH,
        )

    # 6. Execute with step-by-step logging
    try:
        results = []
        for i, action in enumerate(actions[:max_steps], 1):
            result = await playwright_bridge.call_browser_tool(action, {"url": url})
            step_status = (
                "OK" if "error" not in result else f"ERROR: {result.get('error', 'unknown')[:100]}"
            )
            results.append({"step": i, "action": action, "status": step_status})

            # F-WEB post-scan on content
            content = str(result.get("content", result.get("result", "")))
            clean, scan_reason = _f_web_scan(content)
            if not clean:
                results[-1]["f_web_scan"] = "FAIL"
                results[-1]["reason"] = scan_reason

        receipt = _evidence_receipt(
            "browser_interact",
            url,
            "SEAL",
            {"actions": actions, "results": results, "actor_id": actor_id},
            notes=f"IRREVERSIBLE_GATED: ack_irreversible={ack_irreversible}",
        )

        return _RE(
            ok=True,
            tool="arif.browser_interact",
            stage="111_SENSE",
            verdict="SEAL",
            payload={
                "url": url,
                "actions": actions,
                "results": results,
                "evidence_receipt": receipt,
                "blast_radius_estimate": "HIGH"
                if any(a in {"click", "fill", "submit"} for a in actions)
                else "MEDIUM",
            },
            risk_class=RiskClass.HIGH,
        )

    except Exception as e:
        logger.error(f"Browser interact failed: {e}")
        return _RE(
            ok=False,
            tool="arif.browser_interact",
            stage="111_SENSE",
            verdict="VOID",
            detail=f"Browser automation error: {str(e)[:200]}",
            risk_class=RiskClass.HIGH,
        )
