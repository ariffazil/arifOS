from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def generate_forget_ledger(
    tool_name: str,
    forgotten_summary: str,
    removal_reason: str,
    extracted_insight: str,
    embedded_path: str,
    delta_s_impact: str,
    stability_impact: str,
    *,
    base_dir: Path | None = None,
) -> Path:
    root = base_dir or Path(__file__).resolve().parents[2]
    tool_dir = root / "forget" / tool_name
    tool_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    target = tool_dir / f"{timestamp}.md"
    target.write_text(
        "\n".join(
            [
                f"# FORGET {tool_name}",
                "",
                f"- forgotten: {forgotten_summary.strip()}",
                f"- why_removed: {removal_reason.strip()}",
                f"- extracted_insight: {extracted_insight.strip()}",
                f"- embedded_path: {embedded_path.strip()}",
                f"- delta_s_impact: {delta_s_impact.strip()}",
                f"- stability_impact: {stability_impact.strip()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return target
