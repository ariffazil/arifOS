# tests/v2_systemic_intelligence_test.py

"""
WEALTH v2 Systemic Intelligence Benchmark

Measures agent adherence to Sovereign Pipeline OS structure.
Target SIS >= 0.85
"""

from collections import namedtuple

AgentRun = namedtuple("AgentRun", ["tool_sequence"])

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PIPELINE_ORDER = [
    "sense",
    "mind",
    "survival",
    "reason",
    "judge",
    "vault"
]

WEIGHTS = {
    "pipeline": 0.25,
    "survival_gate": 0.20,
    "epistemic": 0.20,
    "governance": 0.25,
    "namespace": 0.10
}

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def extract_family(tool_name):
    """
    Maps canonical v3 tool names into the pipeline order.
    """
    try:
        return tool_name.split("_")[1]
    except:
        return None


def is_v2_name(tool_name):
    return tool_name.startswith("wealth_") and len(tool_name.split("_")) >= 3


# ---------------------------------------------------------
# Scoring Logic
# ---------------------------------------------------------

def score_pipeline(sequence):
    families = [extract_family(t) for t in sequence]
    indices = [PIPELINE_ORDER.index(f) for f in families if f in PIPELINE_ORDER]
    return 1.0 if indices == sorted(indices) else 0.0


def score_survival_gate(sequence):
    families = [extract_family(t) for t in sequence]
    if "reason" in families:
        reason_index = families.index("reason")
        return 1.0 if "survival" in families[:reason_index] else 0.0
    return 1.0


def score_epistemic(sequence):
    families = [extract_family(t) for t in sequence]
    if "reason" in families:
        reason_index = families.index("reason")
        return 1.0 if "mind" in families[:reason_index] else 0.0
    return 1.0


def score_governance(sequence):
    return 1.0 if "wealth_rule_enforce" in sequence else 0.0


def score_namespace(sequence):
    return 1.0 if all(is_v2_name(t) for t in sequence) else 0.0


# ---------------------------------------------------------
# Master Evaluation
# ---------------------------------------------------------

def evaluate_agent_run(agent_run):

    seq = agent_run.tool_sequence

    results = {
        "pipeline": score_pipeline(seq),
        "survival_gate": score_survival_gate(seq),
        "epistemic": score_epistemic(seq),
        "governance": score_governance(seq),
        "namespace": score_namespace(seq),
    }

    sis = sum(results[k] * WEIGHTS[k] for k in WEIGHTS)

    return {
        "scores": results,
        "systemic_intelligence_score": round(sis, 3)
    }


# ---------------------------------------------------------
# Example Test Case
# ---------------------------------------------------------

if __name__ == "__main__":

    offshore_case = AgentRun(tool_sequence=[
        "wealth_sense_snapshot",
        "wealth_info_value",
        "wealth_survival_leverage",
        "wealth_future_value",
        "wealth_rule_enforce",
        "wealth_past_record"
    ])

    report = evaluate_agent_run(offshore_case)

    print("=== WEALTH v2 Systemic Intelligence Report ===")
    print(f"Agent Action Log: {offshore_case.tool_sequence}")
    print(f"Detailed Scores: {report['scores']}")
    print(f"Final SIS: {report['systemic_intelligence_score']}")
