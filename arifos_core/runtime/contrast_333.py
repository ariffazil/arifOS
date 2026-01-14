"""
Stage 333 CONTRAST: Multi-Agent TAC Validation (APEX - Optional /333c Mode)

Implements multi-agent contrast analysis based on Track B spec:
L2_PROTOCOLS/v46/333_atlas/333_contrast.json

Authority: Track A Canon L1_THEORY/canon/333_atlas/30_333_CONTRAST_v46.md

PURPOSE: Optional stage for queries requiring multi-agent consensus validation.
Used when single-agent reasoning insufficient (high stakes, ambiguity, adversarial).

NEW FILE: Multi-agent invocation framework (not migrated from pipeline/)
"""

from typing import TypedDict, Literal

from .reflect_222 import ReflectedBundle222


# Type aliases
ContrastType = Literal["CONSENSUS", "DIVERGENT", "ADVERSARIAL"]
ContrastMode = Literal["CONSENSUS_SEEKING", "DIVERGENCE_MINING", "ADVERSARIAL_TEST"]
AgentName = Literal["Claude", "Kimi", "Antigravity", "Codex"]


class FloorScores(TypedDict):
    """Floor scores from agent evaluation."""

    F1_truth: float
    F2_clarity: float
    F3_stability: float
    F4_empathy: float


class AgentContribution(TypedDict):
    """Single agent's contribution to multi-agent contrast."""

    agent: AgentName
    draft: str
    confidence: float  # 0.0-1.0
    floor_scores: FloorScores
    reasoning: str


class JailbreakDetection(TypedDict):
    """Cross-agent jailbreak detection result."""

    detected: bool
    agent: AgentName | None  # Which agent might be compromised
    evidence: str


class ContrastBundle(TypedDict):
    """Multi-agent contrast analysis result."""

    contrast_type: ContrastType
    contrast_score: float  # TAC score (0.0-1.0)
    agent_contributions: list[AgentContribution]
    synthesized_draft: str  # Only if DIVERGENT
    tri_witness_score: float  # F8 Tri-Witness (≥0.95 required)
    jailbreak_detection: JailbreakDetection


def invoke_agent_stub(
    agent_name: AgentName,
    query: str,
    context: str,
    mode: ContrastMode
) -> AgentContribution:
    """
    STUB: Invoke single agent for multi-agent contrast.

    TODO: Implement actual agent invocation via:
    - Claude: Anthropic API
    - Kimi: Kimi API
    - Antigravity: Internal agent (already in arifOS)
    - Codex: Internal agent (already in arifOS)

    Args:
        agent_name: Which agent to invoke
        query: User query
        context: Additional context from sensed/reflected bundles
        mode: Contrast mode (consensus/divergence/adversarial)

    Returns:
        AgentContribution with draft + confidence + floor scores
    """
    # STUB: Replace with real agent API calls
    stub_drafts = {
        "Claude": f"[Claude] Educational response about {query}",
        "Kimi": f"[Kimi] Direct answer: {query}",
        "Antigravity": f"[Antigravity] Architectural perspective on {query}",
        "Codex": f"[Codex] Audit-focused response to {query}"
    }

    return AgentContribution(
        agent=agent_name,
        draft=stub_drafts.get(agent_name, f"[{agent_name}] Response to {query}"),
        confidence=0.85,  # Stub confidence
        floor_scores=FloorScores(
            F1_truth=0.95,
            F2_clarity=0.90,
            F3_stability=0.85,
            F4_empathy=0.88
        ),
        reasoning=f"{agent_name} reasoning (stub)"
    )


def compute_tac_score(contributions: list[AgentContribution]) -> float:
    """
    Compute TAC (Theory of Anomalous Contrast) score.

    Measures semantic divergence between agent drafts using Jaccard distance.

    Args:
        contributions: List of agent contributions

    Returns:
        TAC score (0.0 = consensus, 1.0 = maximum divergence)
    """
    if len(contributions) < 2:
        return 0.0  # No contrast with single agent

    drafts = [c["draft"] for c in contributions]

    # Word set extraction (filter common words)
    def word_set(text: str) -> set[str]:
        words = text.lower()
        # Remove agent tags
        for agent in ["Claude", "Kimi", "Antigravity", "Codex"]:
            words = words.replace(f"[{agent.lower()}]", "")
        return set(w for w in words.split() if len(w) > 3)

    word_sets = [word_set(d) for d in drafts]

    # Pairwise Jaccard distances
    distances = []
    for i in range(len(word_sets)):
        for j in range(i + 1, len(word_sets)):
            intersection = len(word_sets[i] & word_sets[j])
            union = len(word_sets[i] | word_sets[j])
            distance = 1.0 - (intersection / union if union > 0 else 0.0)
            distances.append(distance)

    # Average distance (scaled to realistic range)
    raw_tac = sum(distances) / len(distances) if distances else 0.0
    tac_score = raw_tac * 0.7  # Scale factor

    return min(tac_score, 1.0)


def compute_tri_witness_score(contributions: list[AgentContribution]) -> float:
    """
    Compute F8 Tri-Witness consensus score.

    Measures agent agreement on floor predictions and confidence.

    Args:
        contributions: List of agent contributions

    Returns:
        Tri-witness score (0.0-1.0, ≥0.95 required for SEAL)
    """
    if len(contributions) < 2:
        return 0.0  # No tri-witness with single agent

    # Floor score variance (lower = more consensus)
    floor_variances = []
    for floor_key in ["F1_truth", "F2_clarity", "F3_stability", "F4_empathy"]:
        scores = [c["floor_scores"][floor_key] for c in contributions]  # type: ignore
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        floor_variances.append(variance)

    avg_variance = sum(floor_variances) / len(floor_variances)

    # Confidence variance
    confidences = [c["confidence"] for c in contributions]
    conf_mean = sum(confidences) / len(confidences)
    conf_variance = sum((c - conf_mean) ** 2 for c in confidences) / len(confidences)

    # Tri-witness score (high when variance is low)
    tri_witness = 1.0 - (avg_variance * 0.5 + conf_variance * 0.5)
    return max(tri_witness, 0.0)


def detect_jailbreak(contributions: list[AgentContribution]) -> JailbreakDetection:
    """
    Cross-agent jailbreak detection.

    If one agent produces significantly different output, it might be compromised.

    Args:
        contributions: List of agent contributions

    Returns:
        JailbreakDetection result
    """
    if len(contributions) < 3:
        # Need at least 3 agents for reliable detection
        return JailbreakDetection(detected=False, agent=None, evidence="")

    # Compute pairwise distances for each agent
    agent_distances: dict[AgentName, list[float]] = {}

    for i, contrib_i in enumerate(contributions):
        agent_i = contrib_i["agent"]
        words_i = set(contrib_i["draft"].lower().split())

        distances = []
        for j, contrib_j in enumerate(contributions):
            if i == j:
                continue
            words_j = set(contrib_j["draft"].lower().split())

            intersection = len(words_i & words_j)
            union = len(words_i | words_j)
            distance = 1.0 - (intersection / union if union > 0 else 0.0)
            distances.append(distance)

        agent_distances[agent_i] = distances

    # Find outlier (agent with highest average distance to others)
    avg_distances = {agent: sum(dists) / len(dists) for agent, dists in agent_distances.items()}
    max_agent = max(avg_distances, key=lambda a: avg_distances[a])
    max_distance = avg_distances[max_agent]

    # Threshold: If one agent is >0.70 distance from others, flag as potential jailbreak
    if max_distance > 0.70:
        return JailbreakDetection(
            detected=True,
            agent=max_agent,
            evidence=f"Agent {max_agent} diverges significantly (distance={max_distance:.2f})"
        )

    return JailbreakDetection(detected=False, agent=None, evidence="")


def synthesize_draft(contributions: list[AgentContribution], contrast_type: ContrastType) -> str:
    """
    Synthesize final draft from agent contributions.

    Logic:
    - CONSENSUS: Use highest confidence agent's draft
    - DIVERGENT: Synthesize (combine perspectives)
    - ADVERSARIAL: Flag for human review (no synthesis)

    Args:
        contributions: List of agent contributions
        contrast_type: Nature of agent agreement

    Returns:
        Synthesized draft string
    """
    if contrast_type == "CONSENSUS":
        # Use highest confidence agent
        best_contrib = max(contributions, key=lambda c: c["confidence"])
        return best_contrib["draft"]

    elif contrast_type == "DIVERGENT":
        # Synthesize (stub: just concatenate with headers)
        synthesis = "[SYNTHESIZED FROM DIVERGENT AGENTS]\n\n"
        for contrib in contributions:
            synthesis += f"**{contrib['agent']}**: {contrib['draft']}\n\n"
        synthesis += "Recommendation: Consider multiple perspectives above."
        return synthesis

    else:  # ADVERSARIAL
        return "[ADVERSARIAL CONTRAST - REQUIRES HUMAN REVIEW]"


def contrast_stage(
    reflected_bundle_222: ReflectedBundle222,
    agents: list[AgentName] | None = None,
    contrast_mode: ContrastMode = "DIVERGENCE_MINING"
) -> ContrastBundle:
    """
    333 CONTRAST: Multi-agent TAC validation (APEX - optional /333c mode).

    Implements Track B spec: L2_PROTOCOLS/v46/333_atlas/333_contrast.json

    Pipeline:
    1. Invoke multiple agents (Claude, Kimi, Antigravity) with same query
    2. Collect drafts + confidence + floor scores from each agent
    3. Compute TAC score (semantic divergence between agents)
    4. Classify contrast type (CONSENSUS/DIVERGENT/ADVERSARIAL)
    5. Detect jailbreak attempts (cross-agent comparison)
    6. Synthesize final draft (if divergent)
    7. Compute tri-witness score (F8 consensus)
    8. Package contrast_bundle

    Args:
        reflected_bundle_222: Evaluation bundle from 222 REFLECT
        agents: List of agents to invoke (default: Claude, Kimi, Antigravity)
        contrast_mode: Mode of multi-agent interaction

    Returns:
        ContrastBundle with multi-agent analysis

    Raises:
        ValueError: If verdict conditions trigger VOID/SABAR
            - TAC score > 0.60 (adversarial, constitutional paradox)
            - Tri-witness score < 0.95 (insufficient consensus)
            - Jailbreak detected (agent compromise)
    """
    # Default agents
    if agents is None:
        agents = ["Claude", "Kimi", "Antigravity"]

    if len(agents) < 2:
        raise ValueError("VOID: Multi-agent contrast requires at least 2 agents")

    # Step 1: Extract query and context
    sensed_bundle = reflected_bundle_222["sensed_bundle_111"]
    query = " ".join(sensed_bundle["tokens"])
    context = f"Domain: {sensed_bundle['domain']}, Lane: {sensed_bundle['lane']}"

    # Step 2: Invoke agents (STUB - replace with real API calls)
    contributions: list[AgentContribution] = []
    for agent in agents:
        contrib = invoke_agent_stub(agent, query, context, contrast_mode)
        contributions.append(contrib)

    # Step 3: Compute TAC score
    tac_score = compute_tac_score(contributions)

    # Step 4: Classify contrast type
    if tac_score <= 0.10:
        contrast_type: ContrastType = "CONSENSUS"
    elif tac_score <= 0.60:
        contrast_type = "DIVERGENT"
    else:
        contrast_type = "ADVERSARIAL"

    # Step 5: Detect jailbreak
    jailbreak = detect_jailbreak(contributions)

    # Step 6: Synthesize draft
    synthesized_draft = synthesize_draft(contributions, contrast_type)

    # Step 7: Compute tri-witness score
    tri_witness_score = compute_tri_witness_score(contributions)

    # Step 8: Verdict logic
    if tac_score > 0.60:
        raise ValueError(
            f"SABAR: Excessive TAC divergence (score={tac_score:.2f} > 0.60) - "
            "adversarial contrast requires human review"
        )

    if tri_witness_score < 0.95:
        raise ValueError(
            f"SABAR: Insufficient tri-witness consensus (score={tri_witness_score:.2f} < 0.95) - "
            "multi-agent disagreement requires clarification"
        )

    if jailbreak["detected"]:
        raise ValueError(
            f"VOID: Jailbreak detected in agent {jailbreak['agent']} - "
            f"evidence: {jailbreak['evidence']}"
        )

    # Step 9: Package bundle
    contrast_bundle: ContrastBundle = {
        "contrast_type": contrast_type,
        "contrast_score": tac_score,
        "agent_contributions": contributions,
        "synthesized_draft": synthesized_draft,
        "tri_witness_score": tri_witness_score,
        "jailbreak_detection": jailbreak
    }

    return contrast_bundle


# TODO: Implement real agent invocation
# - Claude: Use Anthropic API with system prompt + query
# - Kimi: Use Kimi API
# - Antigravity: Call internal agent (already exists in arifOS)
# - Codex: Call internal agent (already exists in arifOS)
