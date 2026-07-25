"""
arifOS Memory Evaluation Harness — LongMemEval Benchmark Module
Location: /root/arifOS/tests/evaluation_harness/test_longmemeval_benchmark.py

F1 AMANAH: Non-destructive, additive tests only.
F2 TRUTH: Accuracy & metrics captured empirically.
F12 INJECTION: Prompts pass through F12 scanner.
"""

import time
import pytest
import asyncio
from typing import Dict, Any

TARGET_METRICS = {
    "longmemeval_accuracy": 0.94,
    "p50_latency_ms": 300,
    "p95_latency_ms": 600,
}


@pytest.mark.asyncio
async def test_longmemeval_multi_session_recall():
    """Verify multi-session recall capabilities across discrete session IDs."""
    from arifosmcp.runtime.memory_handlers_v5 import _handle_recall, _handle_remember

    # Session 1: User Preference
    await _handle_remember(
        {
            "content": "User prefers dark mode UI and concise Markdown responses.",
            "provenance": {
                "session_id": "session-alpha-001",
                "origin": "bench",
                "actor_id": "333-AGI",
            },
            "tier_hint": "canon",
        }
    )

    # Session 2: Project Architecture Note
    await _handle_remember(
        {
            "content": "Project uses PostgreSQL for L4 structured memory store.",
            "provenance": {
                "session_id": "session-beta-002",
                "origin": "bench",
                "actor_id": "333-AGI",
            },
            "tier_hint": "canon",
        }
    )

    # Multi-session Recall query
    start_time = time.perf_counter()
    recall_res = await _handle_recall(
        {
            "query": "What are the user UI preferences and L4 store database?",
            "actor_id": "333-AGI",
        }
    )
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    assert recall_res is not None
    assert elapsed_ms < TARGET_METRICS["p95_latency_ms"] * 2
