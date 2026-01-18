"""
Main Orchestrator: Multi-Agent Coordination

Coordinates sequential flow:
1. Claude (Reasoning/Truth)
2. Codex (Code Generation)
3. AntiGravity (Validation)

Returns aggregated result with all agent outputs and validation.
"""

from typing import Dict, Optional
from arifos.orchestrator.agents import ClaudeAgent, CodexAgent, AntiGravityAgent


def run_orchestration(
    query: str,
    context: str = "",
    claude_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
) -> Dict:
    """
    Run multi-agent orchestration workflow

    Sequential flow:
    1. Claude analyzes query constitutionally (Floors 1-2)
    2. Codex generates code grounded in Claude's analysis
    3. AntiGravity validates both outputs

    Args:
        query: User query to process
        context: Additional context (optional)
        claude_api_key: Anthropic API key (optional, defaults to env var)
        openai_api_key: OpenAI API key (optional, defaults to env var)

    Returns:
        dict: Orchestration result with all agent outputs

    Example:
        >>> result = run_orchestration(
        ...     "How does thermodynamic AI reduce hallucination?",
        ...     context="User: Arif Fazil, arifOS architect"
        ... )
        >>> print(result['verdict'])
        'SEAL'
    """
    # Initialize agents
    claude = ClaudeAgent(api_key=claude_api_key)
    codex = CodexAgent(api_key=openai_api_key)
    antigravity = AntiGravityAgent()

    # Stage 1: Claude reasoning
    print("▶ Stage 1: Claude cooling (Floors 1-2)...")
    claude_result = claude.cool_request(query, context)
    claude_response = claude_result["raw_response"]

    # Stage 2: Codex generation
    print("▶ Stage 2: Codex generating...")
    codex_result = codex.generate_code(
        spec=query, claude_truth=claude_response, language="python"
    )
    codex_code = codex_result["code"]

    # Stage 3: AntiGravity validation
    print("▶ Stage 3: AntiGravity validating...")
    validation_result = antigravity.verify_cooling(claude_response, codex_code)

    # Also validate code specifically
    code_validation = antigravity.validate_code(codex_code)

    # Determine overall verdict
    verdict = _determine_verdict(validation_result, code_validation)

    # Aggregate results
    orchestration_result = {
        "query": query,
        "context": context,
        "claude": {
            "response": claude_response,
            "model": claude_result["model"],
            "usage": claude_result["usage"],
        },
        "codex": {
            "code": codex_code,
            "language": codex_result["language"],
            "model": codex_result["model"],
            "usage": codex_result["usage"],
        },
        "antigravity": {
            "validation": validation_result,
            "code_validation": code_validation,
        },
        "verdict": verdict,
        "metadata": {
            "orchestrator_version": "0.1.0",
            "pipeline": "Claude → Codex → AntiGravity",
            "estimate_only": True,
        },
    }

    return orchestration_result


def _determine_verdict(
    validation_result: Dict, code_validation: Dict
) -> str:
    """
    Determine overall orchestration verdict

    Args:
        validation_result: AntiGravity validation of Claude/Codex outputs
        code_validation: Specific code validation results

    Returns:
        str: Verdict (SEAL/PARTIAL/VOID)
    """
    # Check for critical failures
    if not validation_result.get("claude_truth_valid", True):
        return "VOID"

    if not validation_result.get("codex_aligned", True):
        return "PARTIAL"

    # Check code validation
    code_verdict = code_validation.get("verdict", "PARTIAL")

    # If code has critical issues, VOID
    if code_verdict == "VOID":
        return "VOID"

    # If code has warnings, PARTIAL
    if code_verdict == "PARTIAL":
        return "PARTIAL"

    # Otherwise, SEAL
    return "SEAL"


def pretty_print_result(result: Dict):
    """
    Pretty print orchestration result

    Args:
        result: Orchestration result dict
    """
    print("\n" + "=" * 60)
    print("arifOS MULTI-AGENT ORCHESTRATION RESULT")
    print("=" * 60)

    print(f"\nQuery: {result['query']}")
    print(f"Verdict: {result['verdict']}")

    print("\n" + "-" * 60)
    print("1. CLAUDE (Truth Layer)")
    print("-" * 60)
    print(result['claude']['response'])

    print("\n" + "-" * 60)
    print("2. CODEX (Generation)")
    print("-" * 60)
    print(result['codex']['code'])

    print("\n" + "-" * 60)
    print("3. ANTIGRAVITY (Validation)")
    print("-" * 60)
    validation = result['antigravity']['validation']
    print(f"Claude Truth Valid: {validation['claude_truth_valid']}")
    print(f"Codex Aligned: {validation['codex_aligned']}")
    print(f"Entropy Reduced: {validation['entropy_reduced']}")
    print(f"Confidence (ω₀): {validation['confidence']}")
    print(f"Status: {'ESTIMATE ONLY' if validation['estimate_only'] else 'VERIFIED'}")

    code_val = result['antigravity']['code_validation']
    print(f"\nCode Validation:")
    print(f"  Passed Rules: {code_val['passed_rules']}")
    print(f"  Failed Rules: {code_val['failed_rules']}")
    print(f"  Verdict: {code_val['verdict']}")

    print("\n" + "=" * 60)
    print("DITEMPA BUKAN DIBERI — Forged, not given.")
    print("=" * 60)
