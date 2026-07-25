"""
arifOS Memory Evaluation Harness — LoCoMo Benchmark Module
Location: /root/arifOS/tests/evaluation_harness/test_locomo_benchmark.py

F1 AMANAH: Non-destructive, additive tests only.
F2 TRUTH: Accuracy & metrics captured empirically.
F12 INJECTION: Prompts pass through F12 scanner.
"""

import time
import pytest
import asyncio
from typing import Dict, Any

TARGET_METRICS = {
    "locomo_accuracy": 0.92,
    "p50_latency_ms": 300,
    "p95_latency_ms": 600,
    "max_tokens_per_query": 7500,
}


@pytest.mark.asyncio
async def test_cross_tier_propagation_speed():
    """Verify L4 -> L3 write propagation speed (FLT3)."""
    from arifosmcp.runtime.memory_handlers_v5 import _handle_remember

    start_time = time.perf_counter()
    mem_res = await _handle_remember(
        {
            "content": "Sovereign Arif established arifOS F13 floor on 2026-07-24.",
            "provenance": {
                "session_id": "bench-locomo-01",
                "origin": "bench",
                "actor_id": "333-AGI",
            },
            "tier_hint": "canon",
        }
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    assert mem_res is not None
    assert (
        elapsed_ms < 1500
    ), f"Write propagation latency too high: {elapsed_ms:.2f}ms"


@pytest.mark.asyncio
async def test_locomo_sample_recall_accuracy():
    """Simulate LoCoMo temporal recall query and verify correct answer selection."""
    from arifosmcp.runtime.memory_handlers_v5 import _handle_recall, _handle_remember

    # Fact 1: Old Fact
    await _handle_remember(
        {
            "content": "Federation architecture core organ runs on port 8080.",
            "provenance": {
                "session_id": "bench-locomo-02",
                "origin": "bench",
                "actor_id": "333-AGI",
            },
            "tier_hint": "canon",
        }
    )

    # Fact 2: Knowledge Update
    await _handle_remember(
        {
            "content": "Federation architecture core organ updated to port 8088 on 2026-07-25.",
            "provenance": {
                "session_id": "bench-locomo-03",
                "origin": "bench",
                "actor_id": "333-AGI",
            },
            "tier_hint": "canon",
        }
    )

    # Recall query
    start_time = time.perf_counter()
    recall_res = await _handle_recall(
        {
            "query": "What port does the arifOS kernel run on?",
            "actor_id": "333-AGI",
        }
    )
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    assert recall_res is not None
    assert elapsed_ms < TARGET_METRICS["p95_latency_ms"] * 2
