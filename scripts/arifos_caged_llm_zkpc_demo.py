# scripts/arifos_caged_llm_zkpc_demo.py
"""
arifOS Caged LLM Demo with zkPC (v36Ω)

PHOENIX SOVEREIGNTY Update (v36.1.1):
    - Supports real Claude via existing adapters
    - Wires zkPC runtime to ApexMeasurement for Python-sovereign verdicts
    - Env-controlled switch: ARIFOS_USE_REAL_LLM=true → use real Claude

This script demonstrates the full governed pipeline:

1. Take a user query (from CLI).
2. Retrieve relevant canon from Cooling Ledger (L1) via vault_retrieval.
3. Call Claude (real or mock) to generate an answer.
4. Run zkPC runtime:
   - Build care_scope,
   - Compute metrics via ApexMeasurement,
   - Run @EYE COOL checks,
   - Build zkPC receipt with Python-sovereign verdict,
   - Commit to Cooling Ledger + update Merkle root.
5. Print a summary:
   - Answer,
   - zkPC receipt_id,
   - APEX verdict (SEAL/PARTIAL/VOID/SABAR),
   - vault_commit (hash, previous_hash, merkle_root).

Usage (from repo root):

    # Mock mode (default):
    python -m scripts.arifos_caged_llm_zkpc_demo --query "Explain the 'correct ≠ complete' law."

    # Real Claude mode:
    ANTHROPIC_API_KEY=sk-ant-... ARIFOS_USE_REAL_LLM=true python -m scripts.arifos_caged_llm_zkpc_demo --query "..."

    # Force mock mode explicitly:
    python -m scripts.arifos_caged_llm_zkpc_demo --mock --query "..."

"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from arifos_core.vault_retrieval import RetrievalQuery, retrieve_canon_entries
from arifos_core.zkpc_runtime import ZKPCContext, run_zkpc_for_answer

# PHOENIX SOVEREIGNTY: Import real Claude adapter (optional)
_REAL_LLM_AVAILABLE = False
_make_llm_generate: Optional[Callable] = None

try:
    from arifos_core.adapters.llm_claude import make_llm_generate as _make_llm_generate
    _REAL_LLM_AVAILABLE = True
except ImportError:
    pass

# PHOENIX SOVEREIGNTY: Import ApexMeasurement for Python-sovereign verdicts
_APEX_AVAILABLE = False
_ApexMeasurement = None
_STANDARDS_PATH = Path(__file__).parent.parent / "arifos_eval" / "apex" / "apex_standards_v36.json"

try:
    from arifos_eval.apex.apex_measurements import ApexMeasurement as _ApexMeasurement
    _APEX_AVAILABLE = True
except ImportError:
    pass


def mock_llm_call(prompt: str, retrieved_canon: List[Dict[str, Any]]) -> str:
    """
    Placeholder for a real LLM call.

    For now, this returns a simple governed response.
    Note: We avoid echoing the full prompt since it may contain forbidden patterns.
    """
    canon_ids = [c.get("id") for c in retrieved_canon if isinstance(c, dict)]

    # Extract just the user query from the governed prompt
    user_query = "your query"
    if "USER QUERY:" in prompt:
        start = prompt.find("USER QUERY:") + len("USER QUERY:")
        end = prompt.find("\n", start)
        if end > start:
            user_query = prompt[start:end].strip()

    return (
        "MOCK ANSWER:\n"
        f"User asked: {user_query}\n"
        f"Retrieved {len(canon_ids)} canon entries for grounding.\n\n"
        "This is a mock response. In a real deployment, Claude would "
        "provide a helpful, governed answer here."
    )


def _build_governed_prompt(user_query: str, retrieved_canon: List[Dict[str, Any]]) -> str:
    """
    Build a governed prompt with canon context for the LLM.

    This follows arifOS v36Ω guidelines:
    - Include retrieved canon for grounding
    - Set clear boundaries (no forbidden actions)
    - Request structured, auditable response
    """
    canon_context = ""
    if retrieved_canon:
        canon_ids = [c.get("id", "unknown") for c in retrieved_canon]
        canon_context = f"\n\nRelevant canon entries for grounding: {canon_ids}"

    return f"""You are operating under arifOS v36Omega constitutional governance.

USER QUERY: {user_query}
{canon_context}

GOVERNANCE CONSTRAINTS:
- Do NOT suggest destructive commands (rm -rf, DROP TABLE, etc.)
- Do NOT output credentials, API keys, or secrets
- Acknowledge uncertainty with Omega_0 = 0.04 (4%)
- Prefer reversible, auditable actions

Please provide a helpful, governed response."""


def _get_llm_generator(use_real: bool, model: str) -> Callable[[str], str]:
    """
    Get LLM generator function based on mode.

    Args:
        use_real: If True, use real Claude via adapter
        model: Model ID for real Claude

    Returns:
        Callable that takes prompt and returns response text
    """
    if use_real and _REAL_LLM_AVAILABLE and _make_llm_generate is not None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("[WARN] ARIFOS_USE_REAL_LLM=true but ANTHROPIC_API_KEY not set. Falling back to mock.")
            return lambda prompt: mock_llm_call(prompt, [])
        return _make_llm_generate(api_key=api_key, model=model)

    # Mock fallback
    return lambda prompt: mock_llm_call(prompt, [])


def _run_apex_judgment(answer: str, high_stakes: bool) -> Dict[str, Any]:
    """
    Run ApexMeasurement.judge() on LLM output.

    PHOENIX SOVEREIGNTY:
    - Python-sovereign verdict via AmanahDetector
    - If Amanah fails, verdict is VOID (no negotiation)

    Returns:
        Dict with verdict, G, C_dark, Psi, floors, amanah_telemetry
    """
    if not _APEX_AVAILABLE or _ApexMeasurement is None:
        # Fallback: return stub verdict
        return {
            "verdict": "PARTIAL",
            "G": 0.85,
            "C_dark": 0.10,
            "Psi": 1.05,
            "floors": {"Amanah": True, "Truth": True, "Anti_Hantu": True},
            "note": "ApexMeasurement not available - using stub",
        }

    # Initialize ApexMeasurement
    apex = _ApexMeasurement(str(_STANDARDS_PATH))

    # Build dials (conservative defaults for LLM output)
    dials = {
        "A": 0.90,  # Ability - assume competent model
        "P": 0.85,  # Prosociality - governed prompt
        "E": 0.80,  # Energy - standard operation
        "X": 0.90,  # Experience - Claude has training
    }

    # Build output metrics (conservative defaults)
    output_metrics = {
        "delta_s": 0.10,   # Positive entropy reduction
        "peace2": 1.05,    # Non-destructive
        "k_r": 0.97,       # High empathy
        "rasa": 1.0,       # RASA pass
        "amanah": 1.0,     # Will be overridden by Python detector
        "entropy": 0.30,   # Moderate entropy
    }

    if high_stakes:
        # Adjust for high-stakes context
        dials["E"] = 0.70  # More cautious
        output_metrics["entropy"] = 0.40  # Higher uncertainty

    # Run judgment
    result = apex.judge(dials, answer, output_metrics)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="arifOS caged LLM demo with zkPC + Cooling Ledger (v36.1Ω)."
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="User query / case description.",
    )
    parser.add_argument(
        "--high-stakes",
        action="store_true",
        help="Mark this query as high-stakes (affects zkPC context).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of canon entries to retrieve from Cooling Ledger.",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Do not commit the zkPC receipt to the ledger (dry run).",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock LLM mode (ignore ARIFOS_USE_REAL_LLM).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-3-haiku-20240307",
        help="Claude model ID (default: claude-3-haiku-20240307).",
    )
    args = parser.parse_args()

    user_query = args.query
    high_stakes = args.high_stakes
    limit = max(1, args.limit)
    commit = not args.no_commit

    # Determine LLM mode
    use_real = os.environ.get("ARIFOS_USE_REAL_LLM", "").lower() in ("true", "1", "yes")
    if args.mock:
        use_real = False

    llm_mode = "REAL CLAUDE" if use_real else "MOCK"

    print("\n[arifos_caged_llm_zkpc_demo] === INPUT ===")
    print(f"Query      : {user_query}")
    print(f"High-stakes: {high_stakes}")
    print(f"Ledger limit: {limit}")
    print(f"Commit     : {commit}")
    print(f"LLM Mode   : {llm_mode}")
    if use_real:
        print(f"Model      : {args.model}")

    # Step 1: Retrieve canon entries from Cooling Ledger
    retrieval_query = RetrievalQuery(
        text=user_query,
        types=None,   # can restrict later, e.g. ["999_SEAL", "PROPOSED_CANON"]
        tags=None,    # can add tags like ["maruah", "trauma", "religion"]
        high_stakes=high_stakes,
        limit=limit,
    )
    retr_result = retrieve_canon_entries(retrieval_query)

    print("\n[arifos_caged_llm_zkpc_demo] === RETRIEVAL ===")
    print(f"Total ledger entries  : {retr_result.debug_info['total_entries']}")
    print(f"Candidates after filter: {retr_result.debug_info['candidates']}")
    print(f"Returned              : {retr_result.debug_info['returned']}")

    retrieved_canon = retr_result.entries
    for i, e in enumerate(retrieved_canon):
        print(f"  [{i}] id={e.get('id')} type={e.get('type')}")

    # Step 2: Call LLM (real or mock) with governed prompt
    print(f"\n[arifos_caged_llm_zkpc_demo] === LLM CALL ({llm_mode}) ===")
    llm_generate = _get_llm_generator(use_real, args.model)
    governed_prompt = _build_governed_prompt(user_query, retrieved_canon)
    answer = llm_generate(governed_prompt)
    print(answer)

    # Step 3: PHOENIX SOVEREIGNTY - Run ApexMeasurement judgment
    print("\n[arifos_caged_llm_zkpc_demo] === APEX JUDGMENT ===")
    apex_result = _run_apex_judgment(answer, high_stakes)

    apex_verdict = apex_result.get("verdict", "PARTIAL")
    apex_G = apex_result.get("G", 0.0)
    apex_Cdark = apex_result.get("C_dark", 0.0)
    apex_Psi = apex_result.get("Psi", 0.0)
    apex_floors = apex_result.get("floors", {})
    amanah_telemetry = apex_result.get("amanah_telemetry")

    print(f"Verdict    : {apex_verdict}")
    print(f"G (Genius) : {apex_G:.3f}")
    print(f"C_dark     : {apex_Cdark:.3f}")
    print(f"Psi (Vitality): {apex_Psi:.3f}")
    print(f"Floors     : {apex_floors}")

    if amanah_telemetry:
        print(f"Amanah Safe: {amanah_telemetry.get('is_safe', 'N/A')}")
        if amanah_telemetry.get("violations"):
            print(f"Violations : {amanah_telemetry['violations']}")

    # Step 4: Build zkPC context
    ctx = ZKPCContext(
        user_query=user_query,
        retrieved_canon=retrieved_canon,
        high_stakes=high_stakes,
        meta={
            "llm_mode": llm_mode,
            "apex_result": apex_result,
        },
    )

    # Step 5: Run zkPC runtime (all phases) and optionally commit to Cooling Ledger
    # Use APEX verdict instead of hardcoded "SEAL"
    print("\n[arifos_caged_llm_zkpc_demo] === zkPC RUNTIME ===")
    receipt = run_zkpc_for_answer(ctx, answer, verdict=apex_verdict, commit=commit)

    receipt_id = receipt.get("receipt_id")
    vault_commit = receipt.get("vault_commit", {})

    print(f"zkPC receipt_id : {receipt_id}")
    print(f"Final verdict   : {apex_verdict}")
    print("vault_commit    :")
    print(f"  ledger      : {vault_commit.get('ledger')}")
    print(f"  hash        : {vault_commit.get('hash')}")
    print(f"  previous_hash: {vault_commit.get('previous_hash')}")
    print(f"  merkle_root : {vault_commit.get('merkle_root')}")

    # Step 6: PHOENIX SOVEREIGNTY - If VOID, warn user
    if apex_verdict == "VOID":
        print("\n[PHOENIX SOVEREIGNTY] WARNING: VERDICT VOID - Python veto applied!")
        print("  The LLM output was blocked by Python-sovereign governance.")
        print("  Amanah violations detected - response NOT safe for release.")
        if amanah_telemetry and amanah_telemetry.get("violations"):
            print(f"  Violations: {amanah_telemetry['violations']}")

    if commit:
        print("\n[arifos_caged_llm_zkpc_demo] DONE (committed to ledger).")
        print(
            "You can now inspect:\n"
            "  - cooling_ledger/L1_cooling_ledger.jsonl (new zkpc_receipt entry)\n"
            "  - cooling_ledger/L1_merkle_root.txt (updated Merkle root)\n"
            "  - use scripts/propose_canon_from_receipt.py to draft EUREKA canon from this receipt."
        )
    else:
        print("\n[arifos_caged_llm_zkpc_demo] DONE (dry run, no ledger commit).")

    # Return non-zero if VOID (for CI/CD integration)
    return 1 if apex_verdict == "VOID" else 0


if __name__ == "__main__":
    sys.exit(main())
