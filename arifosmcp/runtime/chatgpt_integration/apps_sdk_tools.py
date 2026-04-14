"""
ChatGPT Apps-style tools and widget resources for arifOS.

Implements OpenAI ChatGPT Apps SDK specification:
- text/html;profile=mcp-app MIME type for widget templates
- _meta.ui.domain (required for app submission)
- _meta.ui.csp for sandbox security
- structuredContent + content + _meta response pattern

Ref: https://developers.openai.com/apps-sdk/build/state-management
"""

from __future__ import annotations

import logging
import pathlib
import uuid
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP

from arifosmcp.runtime.rest_routes import _build_governance_status_payload

logger = logging.getLogger(__name__)

ARIFOS_WIDGET_DOMAIN = "https://arifosmcp.arif-fazil.com"
VAULT_WIDGET_URI = f"{ARIFOS_WIDGET_DOMAIN}/widget/vault-seal"
RESOURCE_MIME_TYPE = "text/html;profile=mcp-app"

# Standalone widget HTML file (served via /ui/ static route)
_WIDGET_FILE = pathlib.Path(__file__).parent.parent / "widgets" / "vault_seal_widget.html"


def _clamp_score(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(float(value), 1.0))
    except (TypeError, ValueError):
        return default


def _build_vault_seal_structured_content(
    *,
    verdict: str = "SEAL",
    floors: dict[str, Any] | None = None,
    witness: dict[str, Any] | None = None,
    trace_root: str | None = None,
    policy_digest: str | None = None,
) -> dict[str, Any]:
    status = _build_governance_status_payload()
    default_floors = status.get("floors", {})
    default_witness = status.get("witness", {})

    resolved_floors = dict(default_floors)
    resolved_floors.update(floors or {})
    resolved_witness = dict(default_witness)
    resolved_witness.update(witness or {})

    truth_score = _clamp_score(resolved_floors.get("F2"), 0.99)
    humility_level = _clamp_score(resolved_floors.get("F7"), 0.04)
    care_level = _clamp_score(resolved_floors.get("F6"), 0.97)
    trust_vote = _clamp_score(resolved_floors.get("F3"), 0.95)
    amanah_lock = bool(resolved_floors.get("F1", 1.0))

    timestamp = datetime.now(timezone.utc).isoformat()

    # Phase A: Real BLS12-381 signature aggregation (3-of-5 supermajority)
    bls_data: dict[str, Any] = {"quorum_fraction": 0.0, "juror_count": 0, "aggregate_signature": ""}
    chain_hash = ""
    seal_id = f"seal_{uuid.uuid4().hex[:16]}"  # fallback
    try:
        from core.shared.bls_vault import BLSVaultSigner, JUROR_IDS

        bls_payload = {
            "verdict": verdict,
            "tau_truth": truth_score,
            "kappa_r": care_level,
            "tri_witness": trust_vote,
            "timestamp": timestamp,
        }
        signer = BLSVaultSigner()
        sigs = [signer.sign(bls_payload, j) for j in JUROR_IDS[:3]]
        bls_seal = signer.aggregate_seal(bls_payload, sigs)
        seal_id = bls_seal.seal_id
        chain_hash = bls_seal.chain_hash()
        bls_data = {
            "quorum_fraction": bls_seal.quorum_fraction,
            "juror_count": len(bls_seal.juror_ids),
            "aggregate_signature": bls_seal.aggregate_signature_hex[:20] + "…",
        }
    except Exception as exc:
        logger.debug("BLS vault unavailable — using fallback seal: %s", exc)

    return {
        "seal_id": seal_id,
        "verdict": verdict,
        "timestamp": timestamp,
        "floors": {
            "tau_truth": truth_score,
            "omega_0": humility_level,
            "delta_s": status.get("telemetry", {}).get("dS", -0.35),
            "peace2": status.get("telemetry", {}).get("peace2", 1.04),
            "kappa_r": care_level,
            "tri_witness": trust_vote,
            "amanah_lock": amanah_lock,
        },
        "bls": bls_data,
        "zkpc": {
            "receipt_id": None,
            "proof_status": "Phase B — pending",
            "program_id": "arifos-constitution-v888.1.1",
        },
        "chain_hash": chain_hash,
        "summary": {
            "truth_score": truth_score,
            "humility_level": humility_level,
            "care_level": care_level,
            "trust_vote": trust_vote,
            "safety_lock": "ON" if amanah_lock else "OFF",
        },
        "witness": {
            "human": _clamp_score(resolved_witness.get("human"), 0.95),
            "ai": _clamp_score(resolved_witness.get("ai"), 0.94),
            "earth": _clamp_score(resolved_witness.get("earth"), 0.93),
        },
        "witness_ai": _clamp_score(resolved_witness.get("ai"), 0.94),
        "witness_earth": _clamp_score(resolved_witness.get("earth"), 0.93),
        "trace_root": trace_root or "trace_root_unset",
        "policy_digest": policy_digest or "policy_digest_unset",
    }


def vault_seal_widget_html() -> str:
    """Return vault seal widget HTML — reads from standalone file, falls back to minimal inline."""
    if _WIDGET_FILE.exists():
        return _WIDGET_FILE.read_text(encoding="utf-8")
    # Minimal inline fallback
    return (
        "<!DOCTYPE html><html><body style='font-family:sans-serif;padding:16px'>"
        "<p><strong>arifOS Vault Seal</strong> — widget file not found.</p>"
        "<script>window.addEventListener('message',(e)=>{"
        "if(e.data?.method==='ui/notifications/tool-result'){"
        "document.body.innerHTML='<pre>'+JSON.stringify(e.data.params?.structuredContent,null,2)+'</pre>';}});"
        "</script></body></html>"
    )


def register_chatgpt_app_tools(mcp: FastMCP) -> None:
    """
    Register arifOS ChatGPT App tools with full widget support.

    Implements OpenAI ChatGPT Apps SDK specification:
    - Widget resource with text/html;profile=mcp-app MIME type
    - _meta.ui.domain (required for app submission)
    - _meta.ui.csp for sandbox security
    - _meta.ui.prefersBorder, _meta.ui.prefersExpanded

    Ref: https://developers.openai.com/apps-sdk/build/state-management
    """

    @mcp.resource(
        VAULT_WIDGET_URI,
        name="arifOS Vault Seal Widget",
        mime_type=RESOURCE_MIME_TYPE,
        meta={
            "openai/widgetDescription": "Displays constitutional seal telemetry and witness alignment.",
        },
    )
    def vault_seal_widget_resource() -> str:
        """Return widget HTML with full MCP Apps UI bridge support."""
        html = vault_seal_widget_html()
        return html

    def _build_widget_template() -> dict[str, Any]:
        """Build the widget template response with full ChatGPT Apps SDK metadata."""
        return {
            "contents": [
                {
                    "uri": VAULT_WIDGET_URI,
                    "mimeType": RESOURCE_MIME_TYPE,
                    "text": vault_seal_widget_html(),
                    "_meta": {
                        "ui": {
                            "prefersBorder": True,
                            "domain": ARIFOS_WIDGET_DOMAIN,
                            "csp": {
                                "connectDomains": [
                                    "https://arifosmcp.arif-fazil.com",
                                    "https://arif-fazil.com",
                                ],
                                "resourceDomains": [
                                    "https://*.oaistatic.com",
                                ],
                            },
                        },
                        "openai/widgetDescription": "arifOS constitutional seal — displays F1-F13 floor status, verdict, and tri-witness consensus.",
                    },
                }
            ],
        }

    @mcp.tool(
        name="vault_seal_card",
        title="Vault Seal Card Data",
        description=(
            "Build structured constitutional seal data for ChatGPT widgets. "
            "Uses existing arifOS telemetry and optional floor overrides; no irreversible sealing occurs."
        ),
        annotations={"readOnlyHint": True},
    )
    async def vault_seal_card(
        verdict: str = "SEAL",
        floors: dict[str, Any] | None = None,
        witness: dict[str, Any] | None = None,
        trace_root: str | None = None,
        policy_digest: str | None = None,
    ) -> dict[str, Any]:
        data = _build_vault_seal_structured_content(
            verdict=verdict,
            floors=floors,
            witness=witness,
            trace_root=trace_root,
            policy_digest=policy_digest,
        )
        return {
            "structuredContent": data,
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Prepared constitutional seal card. Verdict: {data['verdict']}, "
                        f"Truth Score: {data['summary']['truth_score']:.1%}, "
                        f"Trust Vote: {data['summary']['trust_vote']:.1%}."
                    ),
                }
            ],
        }

    @mcp.tool(
        name="render_vault_seal",
        title="Render Vault Seal Widget",
        description=(
            "Render the arifOS constitutional health check widget from structured seal data. "
            "Sets _meta.ui.domain for ChatGPT sandbox rendering under domain.web-sandbox.oaiusercontent.com"
        ),
        annotations={"readOnlyHint": True},
        meta={
            "ui": {
                "resourceUri": VAULT_WIDGET_URI,
                "visibility": "user",
                "domain": ARIFOS_WIDGET_DOMAIN,
            },
            "openai/outputTemplate": VAULT_WIDGET_URI,
            "openai/toolInvocation/invoking": "Rendering constitutional health check...",
            "openai/toolInvocation/invoked": "Constitutional health check displayed.",
        },
    )
    async def render_vault_seal(seal_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "structuredContent": seal_data,
            "content": [
                {
                    "type": "text",
                    "text": "Displaying constitutional health check...",
                }
            ],
            "_meta": {
                "ui": {
                    "resourceUri": VAULT_WIDGET_URI,
                    "prefersBorder": True,
                    "prefersExpanded": seal_data.get("verdict") != "SEAL",
                    "domain": ARIFOS_WIDGET_DOMAIN,
                    "csp": {
                        "connectDomains": [
                            "https://arifosmcp.arif-fazil.com",
                        ],
                        "resourceDomains": [
                            "https://*.oaistatic.com",
                        ],
                    },
                },
            },
        }

    @mcp.tool(
        name="get_constitutional_health",
        title="Get Constitutional Health",
        description="Read-only constitutional health snapshot. Returns F1-F13 floor status, telemetry, and widget URI.",
        annotations={"readOnlyHint": True},
    )
    async def _get_constitutional_health(session_id: str = "global") -> dict[str, Any]:
        from arifosmcp.runtime.tools import get_constitutional_health as _gch

        result = await _gch(session_id=session_id)
        if hasattr(result, "model_dump"):
            return result.model_dump(mode="json")
        return result if isinstance(result, dict) else {"result": str(result)}

    @mcp.tool(
        name="list_recent_verdicts",
        title="List Recent Verdicts",
        description="Read-only summary of the most recent constitutional verdicts. Phase 1: no write path exposed.",
        annotations={"readOnlyHint": True},
    )
    async def _list_recent_verdicts(limit: int = 5) -> list:
        from arifosmcp.runtime.tools import list_recent_verdicts as _lrv

        return await _lrv(limit=limit)


async def render_vault_seal(seal_data: dict[str, Any]) -> dict[str, Any]:
    """Render the arifOS constitutional health check widget from structured seal data."""
    return {
        "structuredContent": seal_data,
        "content": [
            {
                "type": "text",
                "text": "Displaying constitutional health check...",
            }
        ],
        "_meta": {
            "ui": {
                "resourceUri": VAULT_WIDGET_URI,
                "prefersBorder": True,
                "prefersExpanded": seal_data.get("verdict") != "SEAL",
            }
        },
    }


__all__ = [
    "ARIFOS_WIDGET_DOMAIN",
    "VAULT_WIDGET_URI",
    "RESOURCE_MIME_TYPE",
    "_build_vault_seal_structured_content",
    "register_chatgpt_app_tools",
    "vault_seal_widget_html",
    "render_vault_seal",
]
