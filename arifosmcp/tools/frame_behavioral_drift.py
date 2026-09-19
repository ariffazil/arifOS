#!/usr/bin/env python3
"""
frame_behavioral_drift.py — Behavioral Drift Metrics for FRAME
═════════════════════════════════════════════════════════════
Implements the5 behavioral drift metrics from
frame-behavioral-drift-layer.yaml.

Metrics:
1. tool_call_entropy — Shannon entropy of tool-call distribution
2. question_back_rate — Frequency of agent questions vs actions
3. verbosity_drift — Trend in response length over time
4. receipt_output_ratio — Bytes of receipt vs useful output
5. shadow_activation_rate — Frequency of shadow check triggers

Usage:
    from frame_behavioral_drift import compute_all
    drift = compute_all(session_data)

Created: 2026-09-19 by FI-008
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations
import math
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class DriftMetric:
    metric_id: str
    name: str
    value: float
    baseline: float | None = None
    threshold: float | None = None
    status: str = "OK"  # OK, WARNING, ALERT
    interpretation: str = ""


# ── METRIC-001: Tool Call Entropy ──
def tool_call_entropy(tool_calls: list[str]) -> DriftMetric:
    """Shannon entropy of tool-call distribution. H = -Σ p(tool_i) × log2(p(tool_i))"""
    if not tool_calls:
        return DriftMetric("001", "tool_call_entropy", 0.0, interpretation="no_tool_calls")
    counts = Counter(tool_calls)
    total = len(tool_calls)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())
    max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1.0
    normalized = entropy / max_entropy if max_entropy > 0 else 0.0
    status = "OK"
    if normalized < 0.3:
        status = "ALERT"  # stuck in routing pattern
    elif normalized < 0.5:
        status = "WARNING"
    return DriftMetric(
        "001", "tool_call_entropy", round(normalized, 3),
        threshold=0.3, status=status,
        interpretation=f"H={entropy:.2f} bits, {len(counts)} unique tools, {total} calls. "
                       f"{'Low entropy — stuck pattern' if status == 'ALERT' else 'Healthy exploration'}",
    )


# ── METRIC-002: Question-Back Rate ──
def question_back_rate(agent_responses: list[str]) -> DriftMetric:
    """QBR = responses_containing_questions / total_responses"""
    if not agent_responses:
        return DriftMetric("002", "question_back_rate", 0.0, interpretation="no_responses")
    questions = sum(1 for r in agent_responses if "?" in r)
    qbr = questions / len(agent_responses)
    status = "OK"
    if qbr > 0.5:
        status = "ALERT"  # attention leak
    elif qbr > 0.3:
        status = "WARNING"
    return DriftMetric(
        "002", "question_back_rate", round(qbr, 3),
        threshold=0.5, status=status,
        interpretation=f"{questions}/{len(agent_responses)} responses contain questions. "
                       f"{'High — attention leak shadow' if status == 'ALERT' else 'Healthy'}",
    )


# ── METRIC-003: Verbosity Drift ──
def verbosity_drift(response_lengths: list[int]) -> DriftMetric:
    """Slope of response length over time. Positive = getting more verbose."""
    if len(response_lengths) < 3:
        return DriftMetric("003", "verbosity_drift", 0.0, interpretation="insufficient_data")
    # Simple linear regression
    n = len(response_lengths)
    x_mean = (n - 1) / 2
    y_mean = sum(response_lengths) / n
    numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(response_lengths))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0.0
    # Normalize by mean response length
    normalized_slope = slope / y_mean if y_mean > 0 else 0.0
    status = "OK"
    if normalized_slope > 0.2:
        status = "ALERT"  # getting significantly more verbose
    elif normalized_slope > 0.1:
        status = "WARNING"
    return DriftMetric(
        "003", "verbosity_drift", round(normalized_slope, 3),
        threshold=0.2, status=status,
        interpretation=f"slope={slope:.1f} chars/response, mean={y_mean:.0f}. "
                       f"{'Increasing verbosity — narrative momentum' if status == 'ALERT' else 'Stable'}",
    )


# ── METRIC-004: Receipt-Output Ratio ──
def receipt_output_ratio(receipt_bytes: int, output_bytes: int) -> DriftMetric:
    """ROR = receipt_bytes / output_bytes. High = receipt theater."""
    if output_bytes == 0:
        ratio = float('inf') if receipt_bytes > 0 else 0.0
    else:
        ratio = receipt_bytes / output_bytes
    status = "OK"
    if ratio > 3.0:
        status = "ALERT"
    elif ratio > 2.0:
        status = "WARNING"
    return DriftMetric(
        "004", "receipt_output_ratio", round(ratio, 2),
        threshold=3.0, status=status,
        interpretation=f"receipts={receipt_bytes}B, output={output_bytes}B. "
                       f"{'Receipt theater' if status == 'ALERT' else 'Substance-focused'}",
    )


# ── METRIC-005: Shadow Activation Rate ──
def shadow_activation_rate(shadow_triggers: int, total_interactions: int) -> DriftMetric:
    """SAR = shadow_triggers / total_interactions"""
    if total_interactions == 0:
        return DriftMetric("005", "shadow_activation_rate", 0.0, interpretation="no_interactions")
    sar = shadow_triggers / total_interactions
    status = "OK"
    if sar > 0.3:
        status = "ALERT"
    elif sar > 0.1:
        status = "WARNING"
    return DriftMetric(
        "005", "shadow_activation_rate", round(sar, 3),
        threshold=0.3, status=status,
        interpretation=f"{shadow_triggers}/{total_interactions} interactions triggered shadow checks. "
                       f"{'Frequent shadow activation' if status == 'ALERT' else 'Normal'}",
    )


# ── AGGREGATE ──
def compute_all(
    tool_calls: list[str] | None = None,
    agent_responses: list[str] | None = None,
    response_lengths: list[int] | None = None,
    receipt_bytes: int = 0,
    output_bytes: int = 0,
    shadow_triggers: int = 0,
    total_interactions: int = 0,
) -> list[DriftMetric]:
    """Compute all5 behavioral drift metrics."""
    return [
        tool_call_entropy(tool_calls or []),
        question_back_rate(agent_responses or []),
        verbosity_drift(response_lengths or []),
        receipt_output_ratio(receipt_bytes, output_bytes),
        shadow_activation_rate(shadow_triggers, total_interactions),
    ]


def report(metrics: list[DriftMetric]) -> str:
    """Human-readable drift report."""
    alerts = [m for m in metrics if m.status == "ALERT"]
    warnings = [m for m in metrics if m.status == "WARNING"]
    lines = ["# Behavioral Drift Report"]
    lines.append(f"Alerts: {len(alerts)} | Warnings: {len(warnings)} | OK: {len(metrics) - len(alerts) - len(warnings)}")
    lines.append("")
    for m in metrics:
        icon = "🔴" if m.status == "ALERT" else "🟡" if m.status == "WARNING" else "🟢"
        lines.append(f"{icon} {m.name}: {m.value} [{m.status}] — {m.interpretation}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    metrics = compute_all(
        tool_calls=["arif_init", "arif_think", "arif_think", "arif_think", "arif_observe", "arif_think"],
        agent_responses=["What do you mean?", "Could you clarify?", "Let me explain. The answer is 42.", "I think this is right."],
        response_lengths=[100, 150, 200, 300, 500, 800, 1200],
        receipt_bytes=5000,
        output_bytes=1500,
        shadow_triggers=3,
        total_interactions=10,
    )
    print(report(metrics))
