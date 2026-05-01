from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from arifos.runtime.distilled_kernel import load_distilled_kernel
from arifos.runtime.forget import generate_forget_ledger
from arifos.core.governance import ThermodynamicMetrics, apex_constitutional_review, seal_to_vault999
from arifos.runtime.verify_arifos_tools import run_tool_vitality


@dataclass
class AntigravityInsight:
    tool_name: str
    eureka: str
    pattern: str


@dataclass
class OpenCodeVariant:
    tool_name: str
    change_summary: str
    predicted_delta_s: float


def antigravity_extract(tool_name: str) -> AntigravityInsight:
    kernel = load_distilled_kernel()
    return AntigravityInsight(
        tool_name=tool_name,
        eureka=f"Distill invariant for {tool_name}",
        pattern=kernel.patterns[0],
    )


def opencode_variant(insight: AntigravityInsight) -> OpenCodeVariant:
    return OpenCodeVariant(
        tool_name=insight.tool_name,
        change_summary=f"Micro-variant based on {insight.pattern}",
        predicted_delta_s=-0.01,
    )


def apex_gemini_judge(primary_metric_value: float, predicted_delta_s: float) -> str:
    metrics = ThermodynamicMetrics(0.995, predicted_delta_s, 0.04, 1.05, True, 0.97, 0.99)
    return apex_constitutional_review(metrics)


async def run_orchestration_loop(tool_name: str, *, base_dir: Path | None = None) -> dict:
    insight = antigravity_extract(tool_name)
    variant = opencode_variant(insight)
    vitality_record = await run_tool_vitality(tool_name)
    verdict = apex_gemini_judge(vitality_record.primary_metric.value, variant.predicted_delta_s)

    forget_path = None
    if verdict in {"SEAL", "SABAR"}:
        forget_path = generate_forget_ledger(
            tool_name=tool_name,
            forgotten_summary="Obsolete heuristic replaced by distilled invariant.",
            removal_reason="Variant superseded earlier implementation shape.",
            extracted_insight=insight.eureka,
            embedded_path="arifos/runtime/distilled_kernel.py",
            delta_s_impact=str(variant.predicted_delta_s),
            stability_impact="stable",
            base_dir=base_dir,
        )

    vault_receipt = seal_to_vault999(
        tool_name=tool_name,
        payload={
            "insight": insight.eureka,
            "variant": variant.change_summary,
            "vitality_score": vitality_record.vitality_score,
            "verdict": verdict,
        },
        verdict=verdict,
    )

    return {
        "tool_name": tool_name,
        "agent_loop": ["ANTIGRAVITY", "OPENCODE", "APEX-GEMINI", "FORGET", "VAULT-999"],
        "verdict": verdict,
        "forget_path": str(forget_path) if forget_path else None,
        "vault_receipt": vault_receipt,
        "vitality_score": vitality_record.vitality_score,
    }
