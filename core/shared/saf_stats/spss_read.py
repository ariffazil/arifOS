"""Read-side tools (inherited from upstream SAF semantics).

7 tools:
  1.  list_data_files
  2.  inspect_spss_metadata
  3.  preview_spss_data
  4.  profile_spss_data
  5.  convert_spss_to_csv
  6.  convert_csv_to_sav
  7.  generate_basic_spss_syntax

All read tools respect F6 PRIVACY (sandbox) and F1 AMANAH (sealed
verdict). Destructive tools (convert_* overwriting, generate overwriting)
return SABAR unless ack_irreversible=True.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import pyreadstat

from . import governance
from . import sandbox
from . import seal


# ---------------------------------------------------------------------------
# 1. list_data_files
# ---------------------------------------------------------------------------


def list_data_files(subdir: str = "") -> dict:
    root = sandbox.get_data_root()
    target = (root / subdir).resolve() if subdir else root
    try:
        target.relative_to(root)
    except ValueError:
        return {
            "verdict": "VOID",
            "files": [],
            "error": f"subdir escapes sandbox: {subdir}",
        }

    if not target.exists():
        return {"verdict": "SEAL", "root": str(root), "files": [], "note": "empty"}

    files = []
    for p in sorted(target.rglob("*")):
        if p.is_file() and p.suffix.lower() in sandbox.ALLOWED_READ_EXTS:
            files.append(
                {
                    "path": sandbox.relative_to_root(p),
                    "size_bytes": p.stat().st_size,
                    "ext": p.suffix.lower(),
                }
            )
    return {
        "verdict": "SEAL",
        "root": str(root),
        "count": len(files),
        "files": files,
    }


# ---------------------------------------------------------------------------
# 2. inspect_spss_metadata
# ---------------------------------------------------------------------------


def inspect_spss_metadata(file_path: str) -> dict:
    p = sandbox.safe_resolve(file_path, mode="read")
    try:
        df, meta = (
            pyreadstat.read_sav(str(p), metadataonly=True)
            if p.suffix.lower() in {".sav", ".zsav"}
            else pyreadstat.read_por(str(p), metadataonly=True)
        )
    except Exception as e:
        # CSV/TSV fallback — pyreadstat can't introspect these.
        if p.suffix.lower() in {".csv", ".tsv"}:
            try:
                df = pd.read_csv(p) if p.suffix.lower() == ".csv" else pd.read_csv(p, sep="\t")
            except Exception as ee:
                return {"verdict": "VOID", "error": f"CSV/TSV read failed: {ee}"}
            meta = _csv_meta(df)
        else:
            return {"verdict": "VOID", "error": f"metadata read failed: {e}"}

    variables = []
    if hasattr(meta, "column_names_to_labels") and meta.column_names_to_labels:
        for col, label in meta.column_names_to_labels.items():
            vtype = "unknown"
            try:
                vtype = str(df[col].dtype) if col in df.columns else "unknown"
            except Exception:
                pass
            variables.append(
                {
                    "name": col,
                    "label": label,
                    "type": vtype,
                    "format": getattr(meta, "original_variable_types", {}).get(col, ""),
                }
            )
    else:
        for col in df.columns:
            variables.append(
                {
                    "name": col,
                    "label": "",
                    "type": str(df[col].dtype),
                    "format": "",
                }
            )

    return {
        "verdict": "SEAL",
        "file": sandbox.relative_to_root(p),
        "n_rows": int(getattr(meta, "number_rows", len(df)) or len(df)),
        "n_cols": int(getattr(meta, "number_columns", len(df.columns)) or len(df.columns)),
        "variables": variables,
        "variable_value_labels": _safe_json(getattr(meta, "variable_value_labels", {})),
    }


def _csv_meta(df: pd.DataFrame) -> "object":
    class M:
        pass

    m = M()
    m.number_rows = len(df)
    m.number_columns = len(df.columns)
    m.column_names_to_labels = {c: "" for c in df.columns}
    m.original_variable_types = {c: str(df[c].dtype) for c in df.columns}
    m.variable_value_labels = {}
    return m


def _safe_json(obj, limit: int = 200) -> object:
    """JSON-roundtrip an object, dropping anything non-trivial, capping size."""
    try:
        s = json.dumps(obj, default=str, ensure_ascii=False)
    except Exception:
        return None
    if len(s) > limit * 50:
        return {"_truncated": True, "preview": s[: limit * 50]}
    return obj


# ---------------------------------------------------------------------------
# 3. preview_spss_data
# ---------------------------------------------------------------------------


def preview_spss_data(file_path: str, n_rows: int = 20) -> dict:
    p = sandbox.safe_resolve(file_path, mode="read")
    df = _read_any(p)
    if df is None:
        return {"verdict": "VOID", "error": f"cannot read {p}"}
    n_rows = max(1, min(int(n_rows), len(df), 1000))
    head = df.head(n_rows).copy()
    return {
        "verdict": "SEAL",
        "file": sandbox.relative_to_root(p),
        "n_rows_total": int(len(df)),
        "n_cols": int(df.shape[1]),
        "n_previewed": int(n_rows),
        "columns": list(df.columns),
        "rows": _rows_to_jsonable(head),
    }


def _rows_to_jsonable(df: pd.DataFrame) -> list:
    out = []
    for _, r in df.iterrows():
        row = {}
        for c in df.columns:
            v = r[c]
            if pd.isna(v):
                row[c] = None
            elif isinstance(v, (np.integer,)):
                row[c] = int(v)
            elif isinstance(v, (np.floating,)):
                row[c] = float(v)
            else:
                row[c] = str(v)
        out.append(row)
    return out


# ---------------------------------------------------------------------------
# 4. profile_spss_data
# ---------------------------------------------------------------------------


def profile_spss_data(file_path: str) -> dict:
    p = sandbox.safe_resolve(file_path, mode="read")
    df = _read_any(p)
    if df is None:
        return {"verdict": "VOID", "error": f"cannot read {p}"}

    profile = []
    for col in df.columns:
        s = df[col]
        info = {
            "name": col,
            "dtype": str(s.dtype),
            "n_total": int(len(s)),
            "n_missing": int(s.isna().sum()),
            "pct_missing": round(100 * s.isna().sum() / max(len(s), 1), 2),
        }
        if pd.api.types.is_numeric_dtype(s) and s.dropna().size > 0:
            info.update(
                {
                    "min": float(s.min()),
                    "max": float(s.max()),
                    "mean": float(s.mean()),
                    "median": float(s.median()),
                    "std": float(s.std()),
                    "skew": float(s.skew()),
                    "kurtosis": float(s.kurt()),
                    "n_unique": int(s.nunique()),
                }
            )
        else:
            info["n_unique"] = int(s.nunique())
            if s.dropna().size > 0:
                top = s.value_counts().head(3)
                info["top_values"] = [{"value": str(k), "count": int(v)} for k, v in top.items()]
        profile.append(info)

    return {
        "verdict": "SEAL",
        "file": sandbox.relative_to_root(p),
        "n_rows": int(len(df)),
        "n_cols": int(df.shape[1]),
        "total_missing_cells": int(df.isna().sum().sum()),
        "pct_missing_cells": round(100 * df.isna().sum().sum() / max(df.size, 1), 2),
        "columns": profile,
    }


# ---------------------------------------------------------------------------
# 5. convert_spss_to_csv
# ---------------------------------------------------------------------------


def convert_spss_to_csv(
    file_path: str,
    output_path: str,
    *,
    ack_irreversible: bool = False,
) -> dict:
    src = sandbox.safe_resolve(file_path, mode="read")
    dst = sandbox.safe_resolve(output_path, mode="write", must_exist=False)
    vp = governance.govern(
        "convert_spss_to_csv",
        is_destructive=True,
        writes_to_disk=True,
        ack_irreversible=ack_irreversible,
    )
    if vp.verdict == governance.Verdict.SABAR:
        return vp.to_dict() | {
            "note": "set ack_irreversible=True to actually write the file",
            "would_write": sandbox.relative_to_root(dst),
        }
    df = _read_any(src)
    if df is None:
        return {"verdict": "VOID", "error": f"cannot read {src}"}
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dst, index=False)
    rec = seal.seal(
        actor="arif-fazil",
        tool="convert_spss_to_csv",
        action=f"{src.name} -> {dst.name}",
        verdict=vp.verdict.value,
        method="pandas.to_csv",
        input_hash=governance.hash_payload({"src": str(src), "n_rows": len(df)}),
        result_summary={
            "rows": len(df),
            "cols": df.shape[1],
            "out": sandbox.relative_to_root(dst),
        },
        irreversibility=vp.irreversibility,
    )
    return vp.to_dict() | {
        "ok": True,
        "src": sandbox.relative_to_root(src),
        "dst": sandbox.relative_to_root(dst),
        "rows": int(len(df)),
        "cols": int(df.shape[1]),
        "merkle_leaf": rec.merkle_leaf,
    }


# ---------------------------------------------------------------------------
# 6. convert_csv_to_sav
# ---------------------------------------------------------------------------


def convert_csv_to_sav(
    file_path: str,
    output_path: str,
    *,
    column_labels: Optional[dict] = None,
    ack_irreversible: bool = False,
) -> dict:
    src = sandbox.safe_resolve(file_path, mode="read")
    dst = sandbox.safe_resolve(output_path, mode="write", must_exist=False)
    vp = governance.govern(
        "convert_csv_to_sav",
        is_destructive=True,
        writes_to_disk=True,
        ack_irreversible=ack_irreversible,
    )
    if vp.verdict == governance.Verdict.SABAR:
        return vp.to_dict() | {
            "note": "set ack_irreversible=True to actually write the file",
            "would_write": sandbox.relative_to_root(dst),
        }
    df = _read_any(src)
    if df is None:
        return {"verdict": "VOID", "error": f"cannot read {src}"}
    dst.parent.mkdir(parents=True, exist_ok=True)
    labels = column_labels or {}
    pyreadstat.write_sav(df, str(dst), column_labels=labels)
    rec = seal.seal(
        actor="arif-fazil",
        tool="convert_csv_to_sav",
        action=f"{src.name} -> {dst.name}",
        verdict=vp.verdict.value,
        method="pyreadstat.write_sav",
        input_hash=governance.hash_payload({"src": str(src), "n_rows": len(df)}),
        result_summary={
            "rows": len(df),
            "cols": df.shape[1],
            "out": sandbox.relative_to_root(dst),
        },
        irreversibility=vp.irreversibility,
    )
    return vp.to_dict() | {
        "ok": True,
        "src": sandbox.relative_to_root(src),
        "dst": sandbox.relative_to_root(dst),
        "rows": int(len(df)),
        "cols": int(df.shape[1]),
        "merkle_leaf": rec.merkle_leaf,
    }


# ---------------------------------------------------------------------------
# 7. generate_basic_spss_syntax
# ---------------------------------------------------------------------------


def generate_basic_spss_syntax(
    file_path: str,
    *,
    descriptives: list[str] | None = None,
    cross_tab: list[list[str]] | None = None,
    correlations: list[list[str]] | None = None,
    regressions: list[dict] | None = None,
) -> dict:
    """Emit SPSS syntax as TEXT only. We never execute arbitrary SPSS."""
    p = sandbox.safe_resolve(file_path, mode="read")
    fname = p.name
    blocks: list[str] = [
        f"* Generated by SAF-arifOS at {pd.Timestamp.now('UTC').isoformat()}Z.",
        f"* Source: {fname}  (read-only, sandboxed).",
        "GET FILE='" + fname + "'.",
        "",
    ]

    if descriptives:
        blocks.append("* Descriptives.")
        for v in descriptives:
            blocks.append(f"DESCRIPTIVES VARIABLES={v} /STATISTICS=MEAN STDDEV MIN MAX SKEW KURT.")
        blocks.append("")

    if cross_tab:
        blocks.append("* Cross-tabulations with chi-square.")
        for pair in cross_tab:
            if len(pair) != 2:
                continue
            blocks.append(
                f"CROSSTABS /TABLES={pair[0]} BY {pair[1]} "
                f"/CELLS=COUNT COLUMN /STATISTICS=CHISQ PHI CRAMER."
            )
        blocks.append("")

    if correlations:
        blocks.append("* Correlations.")
        for triple in correlations:
            if len(triple) >= 2:
                vars_ = " ".join(triple[:3])
                blocks.append(
                    f"CORRELATIONS /VARIABLES={vars_} /PRINT=TWOTAIL NOSIG /MISSING=PAIRWISE."
                )
        blocks.append("")

    if regressions:
        blocks.append("* Regressions.")
        for spec in regressions:
            dep = spec.get("dependent", "")
            indep = spec.get("independent", [])
            method = spec.get("method", "ENTER").upper()
            if dep and indep:
                blocks.append(
                    f"REGRESSION /DEPENDENT={dep} /METHOD={method} "
                    f"{' '.join(indep)} /STATISTICS=COEFF R ANOVA COLLIN TOL."
                )
        blocks.append("")

    syntax = "\n".join(blocks).rstrip() + "\n"
    return {
        "verdict": "SEAL",
        "file": sandbox.relative_to_root(p),
        "syntax": syntax,
        "byte_count": len(syntax),
        "line_count": syntax.count("\n"),
        "warning": "SPSS syntax is emitted as text only. SAF does not execute SPSS code.",
    }


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _read_any(p: Path) -> Optional[pd.DataFrame]:
    """Read any allowed SPSS-compatible format into a DataFrame."""
    ext = p.suffix.lower()
    try:
        if ext in {".sav", ".zsav"}:
            df, _ = pyreadstat.read_sav(str(p))
            return df
        if ext == ".por":
            df, _ = pyreadstat.read_por(str(p))
            return df
        if ext == ".csv":
            return pd.read_csv(p)
        if ext == ".tsv":
            return pd.read_csv(p, sep="\t")
    except Exception:
        return None
    return None
