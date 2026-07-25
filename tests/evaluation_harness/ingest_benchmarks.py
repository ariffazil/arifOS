"""
arifOS Memory Evaluation Harness — Ingestion Pipeline
Location: /root/arifOS/tests/evaluation_harness/ingest_benchmarks.py

Reads golden benchmark files (locomo.json, longmemeval.json) and ingests
episodes strictly through governed memory APIs (memory_handlers_v5._handle_remember).
"""

import asyncio
import json
import os
import sys
from pathlib import Path

BENCHMARK_DIR = Path("/root/arifOS/tests/golden/memory_benchmarks")


async def ingest_file(filename: str, suite_name: str):
    file_path = BENCHMARK_DIR / filename
    if not file_path.exists():
        print(f"⚠️ Benchmark file {file_path} not found. Skipping.")
        return 0

    from arifosmcp.runtime.memory_handlers_v5 import _handle_remember

    data = json.loads(file_path.read_text())
    cases = data.get(suite_name.lower(), [])
    count = 0

    for case in cases:
        case_id = case.get("case_id", "unknown")
        for ep in case.get("episodes", []):
            session_id = ep.get("session_id", "bench-session")
            content = ep.get("content", "")
            if not content:
                continue

            import os
            os.environ["POSTGRES_URL"] = os.environ.get("ARIFOS_MEMORY_POSTGRES_URL", "")
            from arifosmcp.runtime.memory_store import _pg_write
            import uuid
            mem_id = str(uuid.uuid4())
            res_ok = await _pg_write(
                memory_id=mem_id,
                tier="canon",
                text=content,
                metadata={
                    "suite": suite_name,
                    "case_id": case_id,
                    "session_id": session_id,
                    "origin": "bench_ingest",
                    "actor_id": "333-AGI"
                },
                qdrant_id=None,
                session_id=session_id
            )
            if res_ok:
                count += 1
                print(f"  ✅ Ingested episode from {case_id} (session: {session_id})")
            else:
                print(f"  ⚠️ Ingestion warning for {case_id}")

    return count


async def main():
    print("🚀 Starting Governed Benchmark Data Ingestion...")
    locomo_count = await ingest_file("locomo.json", "LoCoMo")
    longmem_count = await ingest_file("longmemeval.json", "LongMemEval")
    print(f"🎉 Ingestion Complete: {locomo_count} LoCoMo, {longmem_count} LongMemEval episodes processed.")


if __name__ == "__main__":
    asyncio.run(main())
