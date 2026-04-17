import uuid
from typing import Literal

from pydantic import BaseModel, Field

# --- 1. Internal Cognitive State Models ---

class Hypothesis(BaseModel):
    id: str = Field(default_factory=lambda: f"H-{uuid.uuid4().hex[:4]}")
    claim: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_for: list[str] = []
    evidence_against: list[str] = []
    falsifier: str
    disconfirming_test: str | None = None

class Provenance(BaseModel):
    intelligence_type: Literal["statistical", "embodied", "hybrid"] = "statistical"
    grounding_status: Literal["data-based", "sensor-based", "human-mediated", "ungrounded"] = "human-mediated"
    stakes_model: Literal["none", "simulated", "externalized-to-human", "shared"] = "externalized-to-human"
    confidence_domain: Literal["narrow-task", "broad-context", "ambiguous", "human-judgment-required"] = "ambiguous"
    meaning_source: Literal["human-attributed", "statistical-inference", "ungrounded"] = "statistical-inference"
    human_equivalence_claimed: bool = False

class MindState(BaseModel):
    objective: str
    facts: list[str] = []
    assumptions: list[str] = []
    unknowns: list[str] = []
    hypotheses: list[Hypothesis] = []
    risks: list[str] = []
    contradictions: list[str] = []
    decision_required: bool = False
    provenance: Provenance

# --- 2. External Compression Envelope ---

class OutputEnvelope(BaseModel):
    status: Literal["OK", "PARTIAL", "HOLD", "ERROR"]
    summary: str
    key_facts: list[str] = Field(max_length=3)
    key_uncertainties: list[str] = Field(max_length=3)
    options: list[str] = Field(max_length=3)
    next_step: str
    human_decision_required: bool
    provenance: Provenance

# --- 3. Metabolic Loop Functions ---

def sense(raw_input: str) -> dict:
    """Input chaos -> Grounded facts."""
    # Simulation for implementation demonstration
    return {
        "objective": raw_input,
        "facts": ["Input received by system", "User requesting AGI optimization"],
        "assumptions": ["User has authority", "System is in VPS environment"],
        "unknowns": ["Context depth", "Specific resource limits"]
    }

def mind(sense_packet: dict) -> list[Hypothesis]:
    """Grounded facts -> Hypotheses (min 2, with falsifiers)."""
    return [
        Hypothesis(
            claim="Optimize via aggressive disk cleanup and log rotation.",
            confidence=0.85,
            evidence_for=["Disk is at 87%", "Docker has 71GB reclaimable"],
            evidence_against=["Might delete useful caches"],
            falsifier="What if the cache is actually needed for current operations?"
        ),
        Hypothesis(
            claim="Optimize via system parameter tuning (sysctl, etc.)",
            confidence=0.15,
            evidence_for=["Low load average"],
            evidence_against=["Disk is the primary bottleneck"],
            falsifier="What if system tuning causes instability?"
        )
    ]

def heart(hypotheses: list[Hypothesis]) -> list[str]:
    """Simulate consequences (no value assignment)."""
    risks = []
    for h in hypotheses:
        risks.append(f"Risk for {h.claim}: {h.falsifier}")
    return risks

def judge(state: MindState) -> tuple[str, list[str]]:
    """Constitutional gate (F1-F13)."""
    violations = []
    
    # F9/F13: Anti-Hantu / Sovereign
    if state.provenance.human_equivalence_claimed:
        violations.append("F9/F13 violation: Human-equivalent claim prohibited.")
    
    # F2: Truth (Multi-hypothesis mandate)
    if not state.hypotheses or len(state.hypotheses) < 2:
        violations.append("F2 violation: Fewer than 2 hypotheses generated.")
    
    # Falsification mandate
    for h in state.hypotheses:
        if not h.falsifier.strip():
            violations.append(f"Hypothesis {h.id} missing mandatory falsifier.")
            
    if violations:
        return "HOLD", violations
    
    return "OK", []

def chaos_score(state: MindState) -> float:
    """Entropy gate."""
    score = 0.0
    score += len(state.assumptions) * 0.2
    score += len(state.unknowns) * 0.3
    score += len(state.contradictions) * 0.5
    score += max(0, len(state.hypotheses) - 2) * 0.1
    return round(score, 2)

def compress_for_operator(state: MindState) -> OutputEnvelope:
    """Wide mind -> Narrow voice."""
    top_hypotheses = sorted(state.hypotheses, key=lambda h: h.confidence, reverse=True)[:2]
    options = [h.claim for h in top_hypotheses]
    summary = top_hypotheses[0].claim if top_hypotheses else "No stable hypothesis available."
    
    status: Literal["OK", "PARTIAL", "HOLD", "ERROR"] = "OK"
    if state.decision_required:
        status = "HOLD"
    elif state.unknowns:
        status = "PARTIAL"
        
    return OutputEnvelope(
        status=status,
        summary=summary,
        key_facts=state.facts[:3],
        key_uncertainties=state.unknowns[:3],
        options=options[:3],
        next_step="Requesting confirmation for the primary hypothesis." if status == "HOLD" else "Proceed with falsification test.",
        human_decision_required=state.decision_required,
        provenance=state.provenance
    )

# --- 4. Main AGI Runner ---

def run_agi_mind(raw_input: str) -> OutputEnvelope:
    sensed = sense(raw_input)
    hypotheses = mind(sensed)

    state = MindState(
        objective=sensed["objective"],
        facts=sensed.get("facts", []),
        assumptions=sensed.get("assumptions", []),
        unknowns=sensed.get("unknowns", []),
        hypotheses=hypotheses,
        provenance=Provenance()
    )

    state.risks = heart(state.hypotheses)
    verdict, violations = judge(state)

    if violations:
        state.decision_required = True
        state.contradictions.extend(violations)

    score = chaos_score(state)
    envelope = compress_for_operator(state)

    if verdict == "HOLD" or score >= 2.0:
        envelope.status = "HOLD"
        envelope.next_step = "Narrow scope or obtain human judgment (Entropy too high)."

    return envelope
