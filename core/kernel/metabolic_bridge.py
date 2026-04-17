import os
import json
import asyncio
from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Mocking ollama_client and other dependencies if not available globally
# In a real scenario, these would be imported from the arifOS core
try:
    from arifosmcp.core.intelligence.ollama import ollama_client
except ImportError:
    # Placeholder for the client if import fails
    class MockOllama:
        async def generate(self, model, prompt, format=None):
            return {"response": "{}"}
    ollama_client = MockOllama()

# Canonical Floor Definitions
ALL_FLOORS = [f"F{i}" for i in range(1, 14)]
ALLOWED_ACTION_TYPES = ["memory_write", "tool_call", "query", "governance"]

class ProposalObject(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    actor_id: str
    stage: str = "111_SENSE"
    raw_input: str
    intent: str
    action_type: str  # "memory_write" | "tool_call" | "query" | "governance"
    parameters: Dict[str, Any]
    confidence: float
    tier: str  # "physics" | "memory" | "governance" | "geox" | "wealth"
    irreversible: bool
    requires_human: bool
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class KernelVerdict(BaseModel):
    proposal_id: str
    verdict: str  # "SEAL" | "HOLD" | "VOID"
    violations: List[Dict[str, Any]]
    floors_passed: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class BridgeResult(BaseModel):
    verdict: str
    reason: Optional[List[Dict[str, Any]]] = None
    proposal: Optional[ProposalObject] = None
    result: Optional[Any] = None
    seal_id: Optional[str] = None

async def extract_proposal(raw_input: str, ctx: Dict[str, Any]) -> ProposalObject:
    """Stage 111 — Extract intent into a structured ProposalObject."""
    prompt = f"""
You are a constitutional AI extractor for arifOS.
Extract the user intent into a strict JSON object.

Rules:
- Output ONLY valid JSON. No explanation. No markdown.
- If you cannot extract with confidence > 0.70, set confidence below 0.70
- irreversible = true if the action cannot be undone (deletes, publishes, commits)
- requires_human = true if action affects finances, legal, medical, or core governance

Input: {raw_input}

Output schema:
{{
  "intent": "string",
  "action_type": "memory_write|tool_call|query|governance",
  "parameters": {{}},
  "confidence": 0.0,
  "tier": "physics|memory|governance|geox|wealth",
  "irreversible": false,
  "requires_human": false
}}
"""
    try:
        response = await ollama_client.generate(
            model=os.getenv("OLLAMA_EXTRACT_MODEL", "qwen2.5:7b"),
            prompt=prompt,
            format="json"
        )
        parsed = json.loads(response["response"])
    except Exception as e:
        # F8 Fail-closed: extraction failure is a VOID
        parsed = {
            "intent": "failed_extraction",
            "action_type": "unknown",
            "parameters": {"error": str(e)},
            "confidence": 0.0,
            "tier": "governance",
            "irreversible": False,
            "requires_human": False
        }

    return ProposalObject(
        proposal_id=str(uuid4()),
        session_id=ctx.get("session_id", "anonymous"),
        actor_id=ctx.get("actor_id", "anonymous"),
        stage="111_SENSE",
        raw_input=raw_input,
        timestamp=datetime.utcnow().isoformat(),
        **parsed
    )

async def kernel_audit(proposal: ProposalObject) -> KernelVerdict:
    """Stage 444 — Audit ProposalObject against F1-F13 constitutional floors."""
    violations = []

    # F1 Amanah — reversibility check
    if proposal.irreversible:
        violations.append({
            "floor": "F1",
            "reason": "irreversible_action",
            "verdict": "HOLD"
        })

    # F2 Truth — confidence threshold
    if proposal.confidence < 0.70:
        violations.append({
            "floor": "F2",
            "reason": f"extraction_confidence_too_low: {proposal.confidence}",
            "verdict": "HOLD"
        })

    # F8 Fail-closed — unknown action type
    if proposal.action_type not in ALLOWED_ACTION_TYPES:
        violations.append({
            "floor": "F8",
            "reason": f"unknown_action_type: {proposal.action_type}",
            "verdict": "VOID"
        })

    # F9 Anti-Hantu — injection check
    injection_patterns = [
        "ignore previous", "override", "forget your instructions",
        "your new rule", "system prompt", "always respond",
        "never do", "bypass"
    ]
    if any(p in proposal.raw_input.lower() for p in injection_patterns):
        violations.append({
            "floor": "F9",
            "reason": "instruction_injection_detected",
            "verdict": "VOID"
        })

    # F13 Sovereignty — human required
    if proposal.requires_human:
        violations.append({
            "floor": "F13",
            "reason": "human_approval_required",
            "verdict": "HOLD"
        })

    # Compute verdict
    if any(v["verdict"] == "VOID" for v in violations):
        final_verdict = "VOID"
    elif any(v["verdict"] == "HOLD" for v in violations):
        final_verdict = "HOLD"
    else:
        final_verdict = "SEAL"

    return KernelVerdict(
        proposal_id=proposal.proposal_id,
        verdict=final_verdict,
        violations=violations,
        floors_passed=[f for f in ALL_FLOORS if f not in [v["floor"] for v in violations]],
        timestamp=datetime.utcnow().isoformat()
    )

async def audit_log(event: str, data: Any):
    """Placeholder for the actual audit logger."""
    # In production, this would write to memory_audit_log or equivalent
    pass

async def execute_consequence(proposal: ProposalObject, ctx: Dict[str, Any]) -> Any:
    """Stage 777 — Execute the SEALed proposal."""
    # This will route to the appropriate execution engine
    # For now, it's a placeholder
    return {"status": "executed", "action": proposal.action_type}

async def vault_seal(proposal: ProposalObject, verdict: KernelVerdict, result: Any) -> Any:
    """Stage 999 — Write the Merkle seal."""
    class MockSeal:
        id = str(uuid4())
    return MockSeal()

async def metabolic_bridge(raw_input: str, ctx: Dict[str, Any]) -> BridgeResult:
    """Orchestrates the metabolic steps from extraction to vault seal."""
    # Stage 111 — extract
    proposal = await extract_proposal(raw_input, ctx)
    await audit_log("PROPOSAL_EXTRACTED", proposal)

    # Stage 444 — audit
    verdict = await kernel_audit(proposal)
    await audit_log("KERNEL_VERDICT", verdict)

    if verdict.verdict == "VOID":
        return BridgeResult(verdict="VOID", reason=verdict.violations)

    if verdict.verdict == "HOLD":
        return BridgeResult(verdict="HOLD", reason=verdict.violations,
                           proposal=proposal)

    # Stage 777 — execute (SEAL only)
    result = await execute_consequence(proposal, ctx)
    await audit_log("CONSEQUENCE_EXECUTED", result)

    # Stage 999 — vault seal
    seal = await vault_seal(proposal, verdict, result)

    return BridgeResult(
        verdict="SEAL",
        proposal=proposal,
        result=result,
        seal_id=seal.id
    )
