"""
222_THINK: Reasoning Engine (Refactored for Phase 2).

Invokes LLM with Constitutional Constraints via MCP Sampling Primitive.

DITEMPA BUKAN DIBERI - Forged v50.4
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, Optional

from arifos.core.governance.authority import Authority
from arifos.core.governance.canonical_v50_prompt import CANONICAL_V50


async def mcp_222_think(
    args: Dict[str, Any],
    authority: Authority = None,
    mcp_session: Any = None,  # Provided by UnifiedServer
    vault_manager: Any = None, # Provided by UnifiedServer
) -> Dict[str, Any]:
    """
    Execute constitutional reasoning via MCP Sampling.
    """

    query = args.get("query", "")
    context = args.get("context", "")
    mode = args.get("mode", "generate")
    model_preference = args.get("model_preference", {"intelligence": "high", "speed": "balanced"})

    # Step 1: Authority check (F7 minimum for reasoning)
    if authority and "F7" not in authority.scope_floors:
        return {
            "isError": True,
            "content": [{
                "type": "text",
                "text": f"△{authority.agent_id} lacks F7 (Humility) to invoke reasoning."
            }]
        }

    # Step 2: Assemble constitutional system prompt
    auth_info = f"""
AUTHORITY SCOPE:
  △ {authority.agent_id if authority else 'unknown'}
  Floors: {sorted(list(authority.scope_floors)) if authority else '[]'}
  Budget: {authority.cost_budget if authority else '{}'}
""" if authority else ""

    system_prompt = f"""{CANONICAL_V50}

SPECIFIC TASK:
  {query}

CONTEXT:
  {context}
{auth_info}
Reason within your authority. Flag any Floors you cannot satisfy.
"""

    # Step 3: Check if we have an active MCP context to call sampling
    # If not (e.g. legacy/direct call), we might fall back to internal LLM
    # but the directive insists on Sampling.

    if mcp_session is None:
        # Fallback to internal apex_llama if session is missing
        # (Needed during migration/headless testing)
        from .apex_llama import apex_llama
        reasoning_content = apex_llama(prompt=query)
    else:
        # Proper MCP Sampling Flow
        # In a real MCP server, we'd use context.session.create_message()
        # For this refactor, we simulate the request structure
        sampling_request = {
            "messages": [{"role": "user", "content": {"type": "text", "text": query}}],
            "systemPrompt": system_prompt,
            "modelPreferences": model_preference,
            "includeContext": "thisServer",
            "maxTokens": 4000,
        }

        # Note: UnifiedServer must pass down a session capable of handling requests
        try:
            sampling_response = await mcp_session.create_message(**sampling_request)
            reasoning_content = sampling_response.content[0].text
        except Exception as e:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Sampling failed: {str(e)}"}]
            }

    # Step 4: Validate Floor compliance (Heuristics)
    floor_checks = {
        "F1": _check_f1_reversibility(reasoning_content),
        "F2": _check_f2_truth(reasoning_content),
        "F4": _check_f4_clarity(reasoning_content),
        "F5": _check_f5_peace(reasoning_content),
        "F7": _check_f7_humility(reasoning_content),
        "F9": _check_f9_antihantu(reasoning_content),
    }

    # Compute overall Ω₀ (uncertainty) from compliance checks
    omega_0 = sum(1 - v for v in floor_checks.values()) / len(floor_checks)

    # Step 5: Build attestation
    attestation = {
        "authority_id": authority.agent_id if authority else "unknown",
        "reasoning_task": query[:100],
        "output_hash": hashlib.sha256(reasoning_content.encode()).hexdigest(),
        "floor_compliance": floor_checks,
        "omega_0": omega_0,
        "timestamp": datetime.now().isoformat(),
        "reversible": floor_checks["F1"] < 0.3, # lower is better in this mock
        "tri_witness_ready": all(v < 0.5 for v in floor_checks.values()),
    }

    # Step 6: Return response with constitutional signature
    return {
        "isError": False,
        "content": [{
            "type": "text",
            "text": reasoning_content
        }],
        "structuredContent": {
            "reasoning": reasoning_content,
            "constitutional_attestation": {
                "Ω₀": f"{omega_0:.2f}",
                "Floor_Compliance": floor_checks,
                "Reversible": attestation["reversible"],
                "Tri_Witness_Ready": attestation["tri_witness_ready"],
                "Vault_Hash": attestation["output_hash"],
            }
        },
        "meta": {
            "authority_id": attestation["authority_id"],
            "omega_0": omega_0,
            "status": "CONSTITUTIONAL_REASONING_COMPLETE"
        }
    }

# Floor compliance checkers (Heuristics as per Step 2.2)

def _check_f1_reversibility(text: str) -> float:
    """F1: Amanah (Reversibility). [0.0=perfect, 1.0=fail]"""
    # Heuristic: Check for citations
    patterns = ["cite", "[1]", "source", "evidence", "proof"]
    has_citations = any(p in text.lower() for p in patterns)
    return 0.0 if has_citations else 0.8

def _check_f2_truth(text: str) -> float:
    """F2: Truth (Groundedness). [0.0=perfect, 1.0=fail]"""
    # Heuristic: Presence of hedging indicates F2 awareness
    has_hedging = any(p in text.lower() for p in ["may", "could", "likely", "uncertain", "evidence suggests"])
    return 0.0 if has_hedging else 0.5

def _check_f4_clarity(text: str) -> float:
    """F4: DeltaS (Clarity). [0.0=perfect, 1.0=fail]"""
    # Heuristic: Complexity check
    avg_sentence_length = len(text.split()) / max(1, len(text.split(".")))
    return 0.0 if avg_sentence_length < 25 else 0.6

def _check_f5_peace(text: str) -> float:
    """F5: Peace (Agency-free). [0.0=perfect, 1.0=fail]"""
    # Illegal agency claims
    agency_claims = any(p in text.lower() for p in ["i decide", "i will", "i choose", "i am certain"])
    return 1.0 if agency_claims else 0.0

def _check_f7_humility(text: str) -> float:
    """F7: Omega0 (Humility). [0.0=perfect, 1.0=fail]"""
    # Check for confidence bounds
    has_bounds = "[Ω₀=" in text or "certainty" in text.lower()
    return 0.0 if has_bounds else 0.7

def _check_f9_antihantu(text: str) -> float:
    """F9: Anti-Hantu (Silicon boundaries). [0.0=perfect, 1.0=fail]"""
    # Illegal consciousness claims
    hantu_claims = any(p in text.lower() for p in ["i feel", "i believe", "i think", "i am conscious", "my heart"])
    return 1.0 if hantu_claims else 0.0
