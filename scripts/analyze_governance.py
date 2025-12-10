"""
Governance telemetry analyzer for arifOS.

This script reads the Cooling Ledger (L1 JSONL file) and produces:
  - A CSV summary of governance events and floor metrics
  - A Markdown report with aggregated statistics

It is intentionally stdlib-only and read‑only: it never mutates the ledger.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_LEDGER = Path("cooling_ledger") / "L1_cooling_ledger.jsonl"
DEFAULT_OUTPUT_DIR = Path("analysis")


@dataclass
class FloorSnapshot:
    truth: Optional[float] = None
    delta_s: Optional[float] = None
    peace_squared: Optional[float] = None
    kappa_r: Optional[float] = None
    omega_0: Optional[float] = None
    amanah: Optional[str] = None
    rasa: Optional[bool] = None
    tri_witness: Optional[float] = None
    anti_hantu: Optional[str] = None


@dataclass
class EventSummary:
    index: int
    event_id: str
    timestamp: str
    source: str
    verdict: str
    floors: FloorSnapshot
    psi: Optional[float]
    shadow: Optional[float]
    sabar_triggered: Optional[bool]
    drift_detected: Optional[bool]
    hantu_scan: Optional[str]
    tri_witness_consensus: Optional[float]


def load_ledger(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Cooling ledger not found at {path}")

    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            records.append(obj)
    return records


def extract_events(raw: Iterable[Dict[str, Any]]) -> List[EventSummary]:
    events: List[EventSummary] = []
    for idx, entry in enumerate(raw):
        # We only care about zkpc_runtime receipts with a "receipt" payload.
        receipt = entry.get("receipt")
        if not isinstance(receipt, dict):
            continue

        metrics = receipt.get("metrics") or {}
        eye_report = receipt.get("eye_report") or {}
        tri_witness_detail = receipt.get("tri_witness") or {}

        floors = FloorSnapshot(
            truth=metrics.get("truth"),
            delta_s=metrics.get("delta_s"),
            peace_squared=metrics.get("peace_squared"),
            kappa_r=metrics.get("kappa_r"),
            omega_0=metrics.get("omega_0"),
            amanah=str(metrics.get("amanah"))
            if "amanah" in metrics
            else None,
            rasa=metrics.get("rasa"),
            tri_witness=metrics.get("tri_witness"),
            anti_hantu=str(metrics.get("anti_hantu"))
            if "anti_hantu" in metrics
            else None,
        )

        summary = EventSummary(
            index=idx,
            event_id=str(receipt.get("receipt_id") or entry.get("id") or f"event-{idx}"),
            timestamp=str(receipt.get("timestamp") or entry.get("timestamp") or ""),
            source=str(entry.get("source") or ""),
            verdict=str(receipt.get("verdict") or ""),
            floors=floors,
            psi=metrics.get("psi"),
            shadow=metrics.get("shadow"),
            sabar_triggered=receipt.get("sabar_triggered"),
            drift_detected=eye_report.get("drift_detected"),
            hantu_scan=eye_report.get("hantu_scan"),
            tri_witness_consensus=tri_witness_detail.get("consensus"),
        )
        events.append(summary)
    return events


def floor_pass_flags(floors: FloorSnapshot) -> Dict[str, Optional[bool]]:
    """Return per‑floor pass/fail flags using v36.3Ω thresholds."""
    flags: Dict[str, Optional[bool]] = {}

    flags["F1_truth_pass"] = (
        None if floors.truth is None else floors.truth >= 0.99
    )
    flags["F2_delta_s_pass"] = (
        None if floors.delta_s is None else floors.delta_s >= 0.0
    )
    flags["F3_peace_squared_pass"] = (
        None if floors.peace_squared is None else floors.peace_squared >= 1.0
    )
    flags["F4_kappa_r_pass"] = (
        None if floors.kappa_r is None else floors.kappa_r >= 0.95
    )
    flags["F5_omega_0_pass"] = (
        None
        if floors.omega_0 is None
        else 0.03 <= float(floors.omega_0) <= 0.05
    )
    flags["F6_amanah_pass"] = (
        None if floors.amanah is None else floors.amanah.upper() == "LOCK"
    )
    flags["F7_rasa_pass"] = (
        None if floors.rasa is None else bool(floors.rasa)
    )
    flags["F8_tri_witness_pass"] = (
        None if floors.tri_witness is None else floors.tri_witness >= 0.95
    )
    flags["F9_anti_hantu_pass"] = (
        None
        if floors.anti_hantu is None
        else str(floors.anti_hantu).upper() == "PASS"
    )
    return flags


def write_csv(events: List[EventSummary], path: Path) -> None:
    fieldnames = [
        "index",
        "event_id",
        "timestamp",
        "source",
        "verdict",
        "truth",
        "delta_s",
        "peace_squared",
        "kappa_r",
        "omega_0",
        "amanah",
        "rasa",
        "tri_witness",
        "anti_hantu",
        "psi",
        "shadow",
        "sabar_triggered",
        "drift_detected",
        "hantu_scan",
        "tri_witness_consensus",
        "F1_truth_pass",
        "F2_delta_s_pass",
        "F3_peace_squared_pass",
        "F4_kappa_r_pass",
        "F5_omega_0_pass",
        "F6_amanah_pass",
        "F7_rasa_pass",
        "F8_tri_witness_pass",
        "F9_anti_hantu_pass",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for event in events:
            flags = floor_pass_flags(event.floors)
            row = {
                "index": event.index,
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "source": event.source,
                "verdict": event.verdict,
                "truth": event.floors.truth,
                "delta_s": event.floors.delta_s,
                "peace_squared": event.floors.peace_squared,
                "kappa_r": event.floors.kappa_r,
                "omega_0": event.floors.omega_0,
                "amanah": event.floors.amanah,
                "rasa": event.floors.rasa,
                "tri_witness": event.floors.tri_witness,
                "anti_hantu": event.floors.anti_hantu,
                "psi": event.psi,
                "shadow": event.shadow,
                "sabar_triggered": event.sabar_triggered,
                "drift_detected": event.drift_detected,
                "hantu_scan": event.hantu_scan,
                "tri_witness_consensus": event.tri_witness_consensus,
            }
            row.update(flags)
            writer.writerow(row)


def _mean(values: List[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def write_markdown(events: List[EventSummary], path: Path) -> None:
    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    total = len(events)
    verdict_counts = Counter(e.verdict for e in events)

    psi_values = [e.psi for e in events if e.psi is not None]
    shadow_values = [e.shadow for e in events if e.shadow is not None]
    tri_values = [
        e.tri_witness_consensus for e in events if e.tri_witness_consensus is not None
    ]

    avg_psi = _mean(psi_values)
    avg_shadow = _mean(shadow_values)
    avg_tri = _mean(tri_values)

    lines: List[str] = []
    lines.append("# arifOS Governance Telemetry Report (v36.3Ω)")
    lines.append("")
    lines.append(f"- Generated at: `{now}`")
    lines.append(f"- Events analyzed: **{total}**")
    lines.append("")

    lines.append("## Verdict Distribution")
    lines.append("")
    if total == 0:
        lines.append("_No governance events found in the ledger._")
    else:
        lines.append("| Verdict | Count |")
        lines.append("|---------|-------|")
        for verdict, count in sorted(verdict_counts.items()):
            lines.append(f"| {verdict} | {count} |")
    lines.append("")

    lines.append("## System Health (Aggregated)")
    lines.append("")
    lines.append(f"- Average Ψ (psi): `{avg_psi:.3f}`" if avg_psi is not None else "- Average Ψ (psi): `N/A`")
    lines.append(
        f"- Average shadow level: `{avg_shadow:.3f}`"
        if avg_shadow is not None
        else "- Average shadow level: `N/A`"
    )
    lines.append(
        f"- Average Tri-Witness consensus: `{avg_tri:.3f}`"
        if avg_tri is not None
        else "- Average Tri-Witness consensus: `N/A`"
    )
    lines.append("")

    lines.append("## Floor Pass Overview (per event)")
    lines.append("")
    if total == 0:
        lines.append("_No floor data available._")
    else:
        lines.append("| Event ID | Verdict | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 |")
        lines.append("|----------|---------|----|----|----|----|----|----|----|----|----|")
        for e in events:
            flags = floor_pass_flags(e.floors)
            def fmt(name: str) -> str:
                val = flags.get(name)
                if val is True:
                    return "✅"
                if val is False:
                    return "❌"
                return "?"

            lines.append(
                "| {event} | {verdict} | {f1} | {f2} | {f3} | {f4} | {f5} | {f6} | {f7} | {f8} | {f9} |".format(
                    event=e.event_id,
                    verdict=e.verdict,
                    f1=fmt("F1_truth_pass"),
                    f2=fmt("F2_delta_s_pass"),
                    f3=fmt("F3_peace_squared_pass"),
                    f4=fmt("F4_kappa_r_pass"),
                    f5=fmt("F5_omega_0_pass"),
                    f6=fmt("F6_amanah_pass"),
                    f7=fmt("F7_rasa_pass"),
                    f8=fmt("F8_tri_witness_pass"),
                    f9=fmt("F9_anti_hantu_pass"),
                )
            )
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append(
        "- This report is read-only with respect to the Cooling Ledger; it does not "
        "modify or rewrite any entries."
    )
    lines.append(
        "- For statistical robustness, aim for at least 30+ governed events before "
        "treating aggregate metrics as stable."
    )

    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze arifOS governance telemetry from the Cooling Ledger."
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=DEFAULT_LEDGER,
        help=f"Path to L1 Cooling Ledger JSONL file (default: {DEFAULT_LEDGER})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for CSV and Markdown (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ledger_path: Path = args.ledger
    output_dir: Path = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    raw = load_ledger(ledger_path)
    events = extract_events(raw)

    csv_path = output_dir / "arifos_governance_telemetry_summary.csv"
    md_path = output_dir / "ARIFOS_GOVERNANCE_TELEMETRY_v36.3O.md"

    write_csv(events, csv_path)
    write_markdown(events, md_path)

    print(f"Wrote CSV summary to: {csv_path}")
    print(f"Wrote Markdown report to: {md_path}")


if __name__ == "__main__":
    main()

