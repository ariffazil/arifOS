from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


def print_vitality_dashboard(
    jsonl_path: Path | None = None,
    tsv_path: Path | None = None,
) -> None:
    runtime_dir = Path(__file__).resolve().parent
    jsonl_path = jsonl_path or runtime_dir / "tool_vitality.jsonl"
    tsv_path = tsv_path or runtime_dir / "tool_vitality.tsv"

    if not jsonl_path.exists():
        print("No vitality ledger found.")
        return

    rows = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    verdicts: dict[str, Counter[str]] = defaultdict(Counter)
    delta_s_values: dict[str, list[float]] = defaultdict(list)
    tri_values: dict[str, list[float]] = defaultdict(list)
    primary_values: dict[str, list[float]] = defaultdict(list)
    latency_values: dict[str, list[float]] = defaultdict(list)
    failing_fixtures: dict[str, int] = defaultdict(int)

    for row in rows:
        tool = row["tool_name"]
        verdicts[tool][row["verdict"]] += 1
        governance = row["governance"]
        performance = row["performance"]
        correctness = row["correctness"]
        delta_s_values[tool].append(governance["delta_s"])
        tri_values[tool].append(governance["tri_witness_score"])
        primary_values[tool].append(row["primary_metric"]["value"])
        latency_values[tool].append(performance["latency_ms_p95"])
        failing_fixtures[tool] += int(correctness["failed"])

    for tool in sorted(verdicts):
        print(tool)
        print(f"  verdicts: {dict(verdicts[tool])}")
        print(f"  delta_s_trend: {delta_s_values[tool][0]} -> {delta_s_values[tool][-1]}")
        print(f"  tri_witness_trend: {tri_values[tool][0]} -> {tri_values[tool][-1]}")
        print(f"  primary_metric_trend: {primary_values[tool][0]} -> {primary_values[tool][-1]}")
        print(f"  latency_drift_ms: {latency_values[tool][0]} -> {latency_values[tool][-1]}")
        print(f"  failing_fixtures: {failing_fixtures[tool]}")

    print(f"\njsonl: {jsonl_path}")
    print(f"tsv: {tsv_path}")
