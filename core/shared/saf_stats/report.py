"""Markdown report composer. Aggregates one or more tool outputs into a
single APA-flavored Markdown report. Read-only, no execution.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional


from . import sandbox


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _table(rows: list[dict], columns: Optional[list[str]] = None) -> str:
    if not rows:
        return "_(no rows)_\n"
    cols = columns or list(rows[0].keys())
    head = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    body = []
    for r in rows:
        body.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join([head, sep, *body]) + "\n"


def compose_report(
    *,
    title: str,
    file_path: str,
    blocks: list[dict],
    output_path: Optional[str] = None,
) -> dict:
    """Compose a Markdown report.

    Each *block* is a dict like:
        {"heading": "Descriptives", "tool": "stat_descriptives", "data": {...}}
    The function renders the relevant tables based on the tool name.
    """
    p = sandbox.safe_resolve(file_path, mode="read")
    md = [
        f"# {title}",
        "",
        f"- **Source file:** `{sandbox.relative_to_root(p)}`",
        f"- **Generated:** {_now()}",
        "- **Organ:** SAF-arifOS (F1-L13 governed)",
        "",
    ]

    for b in blocks:
        h = b.get("heading") or b.get("tool", "")
        md.append(f"## {h}")
        md.append("")
        md.append(_render_block(b))
        md.append("")

    text = "\n".join(md).rstrip() + "\n"
    out_path = None
    if output_path:
        out = sandbox.safe_resolve(output_path, mode="write", must_exist=False)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        out_path = sandbox.relative_to_root(out)
    return {
        "verdict": "SEAL",
        "report_chars": len(text),
        "written_to": out_path,
        "report": text,
    }


def _render_block(b: dict) -> str:
    tool = b.get("tool", "")
    data = b.get("data", {})
    if tool == "stat_descriptives":
        rows = []
        for r in data.get("results", []):
            row = {
                "column": r["column"],
                "n": r.get("n"),
                "mean": r.get("mean"),
                "sd": r.get("sd"),
                "median": r.get("median"),
                "min": r.get("min"),
                "max": r.get("max"),
                "skew": r.get("skew"),
                "kurt": r.get("kurtosis"),
            }
            rows.append(
                {
                    k: (round(v, 4) if isinstance(v, float) else v)
                    for k, v in row.items()
                    if v is not None
                }
            )
        body = _table(rows, ["column", "n", "mean", "sd", "median", "min", "max", "skew", "kurt"])
    elif tool == "stat_compare_groups":
        body = (
            f"**Method:** {data.get('method')}  \n"
            f"**Statistic:** {data.get('statistic'):.4f}  \n"
            f"**p-value:** {data.get('p_value'):.4g}  \n"
            f"**Effect size:** {data.get('effect_size')}  \n"
            f"**95% CI of difference:** {data.get('ci95_diff')}  \n\n"
            f"### Group summary\n" + _table(data.get("groups", []))
        )
    elif tool == "stat_anova":
        body = (
            f"**Method:** {data.get('method')}  \n"
            f"**Statistic:** {data.get('statistic'):.4f}  \n"
            f"**p-value:** {data.get('p_value'):.4g}  \n"
            f"**Effect size (η²):** {data.get('effect_size')}  \n"
        )
    elif tool == "stat_correlate":
        body = (
            f"**Method:** {data.get('method')}  \n"
            f"**n:** {data.get('n')}  \n"
            f"**r:** {data.get('r'):.4f}  \n"
            f"**p-value:** {data.get('p_value'):.4g}  \n"
            f"**95% CI:** {data.get('ci95')}  \n"
        )
    elif tool == "stat_regress":
        coef = data.get("coefficients", {})
        rows = [{"var": k, **v} for k, v in coef.items()]
        body = (
            f"**Method:** {data.get('method')}  \n"
            f"**n:** {data.get('n')}  \n"
            f"**R²:** {data.get('r_squared')}  \n"
            f"**Adj R²:** {data.get('adj_r_squared')}  \n"
            f"**F:** {data.get('f_stat')} (p={data.get('f_pvalue')})  \n"
            f"**AIC:** {data.get('aic')}  **BIC:** {data.get('bic')}  \n\n"
            f"### Coefficients\n" + _table(rows, ["var", "coef", "se", "t", "p", "ci_lo", "ci_hi"])
        )
        if data.get("vif"):
            body += "\n### VIF\n" + _table(
                [{"var": k, "vif": round(v, 3)} for k, v in data["vif"].items()],
                ["var", "vif"],
            )
    elif tool == "stat_chi_square":
        body = (
            f"**Method:** {data.get('method')}  \n"
            f"**χ²:** {data.get('chi2'):.4f}  \n"
            f"**df:** {data.get('dof')}  \n"
            f"**p-value:** {data.get('p_value'):.4g}  \n"
            f"**Cramér's V:** {data.get('cramers_v')}  \n"
        )
    elif tool == "stat_outliers":
        body = _table(
            [{"column": c, **v} for c, v in data.get("per_column", {}).items()],
            ["column", "n_outliers", "pct_outliers", "n_truncated"],
        )
    elif tool == "stat_missing":
        body = (
            f"**Total missing:** {data.get('total_missing')} "
            f"({data.get('pct_missing_total')}% of cells)\n\n"
            f"### Per column\n"
            + _table(
                [{"column": c, **v} for c, v in data.get("per_column", {}).items()],
                ["column", "missing", "pct"],
            )
        )
    else:
        body = "```json\n" + json.dumps(data, indent=2, default=str)[:4000] + "\n```\n"
    return body
