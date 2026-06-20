"""Inferential-statistics tools (the agentic layer).

12 tools:
  1.  stat_descriptives      univariate summary with skew, kurt, IQR, MAD
  2.  stat_assumptions       Shapiro-Wilk, Levene, Mauchly, normality, homosced.
  3.  stat_compare_groups    t-test (indep/paired/Welch) + Mann-Whitney
  4.  stat_anova             one-way, Welch, Kruskal-Wallis, Friedman
  5.  stat_correlate         Pearson, Spearman, Kendall with CIs
  6.  stat_regress           OLS, logistic, robust; diagnostics + VIF
  7.  stat_chi_square        independence, GOF, Fisher exact
  8.  stat_nonparametric     Wilcoxon, sign, Friedman
  9.  stat_effect_size       Cohen's d, η², Cramér's V, OR, rank-biserial
  10. stat_power             a priori, post-hoc, sensitivity
  11. stat_outliers          z, modified z, IQR, Mahalanobis, Cook's D
  12. stat_missing           pattern, Little's MCAR, listwise/pairwise

Every tool seals to VAULT999 and (where possible) emits SPSS syntax.
"""

from __future__ import annotations

import json
import math
import warnings
from typing import Optional

import numpy as np
import pandas as pd
import pingouin as pg
from scipy import stats
from statsmodels.stats import power as sm_power
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.formula.api import ols

from . import governance
from . import spss_read as saf_read
from . import sandbox
from . import seal

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=stats.ConstantInputWarning) if hasattr(
    stats, "ConstantInputWarning"
) else None
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------


def _df(p: str) -> pd.DataFrame:
    pp = sandbox.safe_resolve(p, mode="read")
    df = saf_read._read_any(pp)
    if df is None:
        raise ValueError(f"cannot read {pp}")
    return df


def _ci(stat: float, se: float, n: int, alpha: float = 0.05) -> list:
    if se is None or se == 0 or n < 2:
        return [None, None]
    z = stats.norm.ppf(1 - alpha / 2)
    return [round(stat - z * se, 6), round(stat + z * se, 6)]


def _seal_tool(
    tool: str,
    action: str,
    method: str,
    df: pd.DataFrame,
    result: dict,
    *,
    effect_size: Optional[float] = None,
    p_value: Optional[float] = None,
    ci: Optional[list] = None,
    assumptions: Optional[dict] = None,
    spss_syntax: Optional[str] = None,
    vp: Optional[governance.VerdictPacket] = None,
) -> governance.VerdictPacket:
    """Run F1-L13 + seal the outcome to VAULT999."""
    vp = vp or governance.govern(
        tool,
        input_data_hash=governance.hash_payload({"rows": len(df), "cols": list(df.columns)}),
    )
    seal.seal(
        actor=vp.actor,
        tool=tool,
        action=action,
        verdict=vp.verdict.value,
        method=method,
        input_hash=governance.hash_payload({"rows": len(df), "cols": list(df.columns)}),
        result_summary=result,
        effect_size=effect_size,
        p_value=p_value,
        confidence_interval=ci,
        assumptions_check=assumptions,
        spss_syntax=spss_syntax,
        irreversibility=vp.irreversibility,
    )
    return vp


# ---------------------------------------------------------------------------
# 1. stat_descriptives
# ---------------------------------------------------------------------------


def stat_descriptives(file_path: str, columns: list[str]) -> dict:
    df = _df(file_path)
    cols = [c for c in columns if c in df.columns]
    if not cols:
        return {"verdict": "VOID", "error": "no valid columns"}
    out = []
    for c in cols:
        s = df[c].dropna()
        if not pd.api.types.is_numeric_dtype(s):
            out.append(
                {
                    "column": c,
                    "dtype": str(s.dtype),
                    "n": int(len(s)),
                    "n_unique": int(s.nunique()),
                    "top": str(s.mode().iat[0]) if len(s) else None,
                }
            )
            continue
        out.append(
            {
                "column": c,
                "dtype": str(s.dtype),
                "n": int(len(s)),
                "mean": float(s.mean()),
                "sd": float(s.std()),
                "median": float(s.median()),
                "min": float(s.min()),
                "max": float(s.max()),
                "q25": float(s.quantile(0.25)),
                "q75": float(s.quantile(0.75)),
                "iqr": float(s.quantile(0.75) - s.quantile(0.25)),
                "mad": float((s - s.median()).abs().median()),
                "skew": float(s.skew()),
                "kurtosis": float(s.kurt()),
                "se_mean": float(s.std() / math.sqrt(len(s))) if len(s) > 1 else None,
                "ci95_mean": _ci(float(s.mean()), float(s.std() / math.sqrt(len(s))), len(s))
                if len(s) > 1
                else [None, None],
            }
        )
    spss = (
        "DESCRIPTIVES VARIABLES=" + " ".join(cols) + " /STATISTICS=MEAN STDDEV MIN MAX SKEW KURT.\n"
    )
    vp = _seal_tool(
        "stat_descriptives",
        ",".join(cols),
        "pingouin / scipy",
        df,
        {"columns": out},
        spss_syntax=spss,
    )
    return vp.to_dict() | {"results": out, "spss_syntax": spss}


# ---------------------------------------------------------------------------
# 2. stat_assumptions
# ---------------------------------------------------------------------------


def stat_assumptions(file_path: str, columns: list[str], group_col: Optional[str] = None) -> dict:
    df = _df(file_path)
    cols = [c for c in columns if c in df.columns]
    out = []
    for c in cols:
        s = df[c].dropna()
        if not pd.api.types.is_numeric_dtype(s) or len(s) < 3:
            continue
        # Shapiro-Wilk (n <= 5000); fall back to D'Agostino
        try:
            sw_stat, sw_p = stats.shapiro(s)
            sw_method = "Shapiro-Wilk"
        except Exception:
            sw_stat, sw_p = stats.normaltest(s)
            sw_method = "D'Agostino-Pearson"
        out.append(
            {
                "column": c,
                "n": int(len(s)),
                "normality_test": sw_method,
                "normality_stat": float(sw_stat),
                "normality_p": float(sw_p),
                "normality_pass": bool(sw_p > 0.05),
                "skew": float(s.skew()),
                "kurtosis": float(s.kurt()),
            }
        )
    lev = None
    if group_col and group_col in df.columns and len(cols) >= 1:
        c = cols[0]
        groups = [g[c].dropna().values for _, g in df.groupby(group_col) if len(g[c].dropna()) > 1]
        if len(groups) >= 2:
            ls, lp = stats.levene(*groups, center="median")
            lev = {
                "column": c,
                "group_col": group_col,
                "levene_stat": float(ls),
                "levene_p": float(lp),
                "homoscedastic": bool(lp > 0.05),
            }
    vp = _seal_tool(
        "stat_assumptions",
        f"cols={cols},group={group_col}",
        "Shapiro-Wilk / Levene",
        df,
        {"columns": out, "levene": lev},
    )
    return vp.to_dict() | {"results": out, "levene": lev}


# ---------------------------------------------------------------------------
# 3. stat_compare_groups
# ---------------------------------------------------------------------------


def stat_compare_groups(
    file_path: str,
    value_col: str,
    group_col: str,
    *,
    paired: bool = False,
    parametric: bool = True,
    equal_var: bool = False,
    alternative: str = "two-sided",
) -> dict:
    df = _df(file_path)
    if value_col not in df.columns or group_col not in df.columns:
        return {"verdict": "VOID", "error": "missing column"}
    groups = [g[value_col].dropna().values for _, g in df.groupby(group_col)]
    groups = [g for g in groups if len(g) > 0]
    if len(groups) < 2:
        return {"verdict": "VOID", "error": "need >=2 groups with data"}
    method = ""
    out = {"value_col": value_col, "group_col": group_col, "groups": []}
    p = ci = es = None
    if paired:
        if len(groups[0]) != len(groups[1]):
            return {"verdict": "VOID", "error": "paired needs equal-length groups"}
        if parametric:
            t, p = stats.ttest_rel(groups[0], groups[1], alternative=alternative)
            method = "Paired t-test"
            es = float(pg.compute_effsize(groups[0], groups[1], paired=True, eftype="cohen"))
            ci = _ci(
                float(groups[0].mean() - groups[1].mean()),
                float(stats.sem(groups[0] - groups[1])),
                len(groups[0]),
            )
        else:
            w, p = stats.wilcoxon(groups[0], groups[1], alternative=alternative)
            method = "Wilcoxon signed-rank"
            es = float(pg.compute_effsize(groups[0], groups[1], paired=True, eftype="rbc"))
    else:
        if len(groups) > 2 and not parametric:
            # Non-parametric with >2 groups → Kruskal-Wallis + epsilon²
            h, p = stats.kruskal(*groups)
            t, _stat_name, method = h, "H", "Kruskal-Wallis H"
            es = float(
                pg.kruskal(
                    data=df[[value_col, group_col]].dropna(),
                    dv=value_col,
                    between=group_col,
                    effsize="epsilon2",
                )["epsilon2"].iloc[0]
            )
            ci = [None, None]
        elif parametric:
            t, p = stats.ttest_ind(
                groups[0], groups[1], equal_var=equal_var, alternative=alternative
            )
            method = "Welch's t-test" if not equal_var else "Student's t-test"
            es = float(pg.compute_effsize(groups[0], groups[1], eftype="cohen"))
            se = math.sqrt(
                groups[0].var(ddof=1) / len(groups[0]) + groups[1].var(ddof=1) / len(groups[1])
            )
            ci = _ci(
                float(groups[0].mean() - groups[1].mean()),
                se,
                len(groups[0]) + len(groups[1]),
            )
        else:
            u, p = stats.mannwhitneyu(groups[0], groups[1], alternative=alternative)
            method = "Mann-Whitney U"
            es = float(pg.compute_effsize(groups[0], groups[1], eftype="rbc"))
    for i, g in enumerate(groups):
        out["groups"].append(
            {
                "index": i,
                "n": int(len(g)),
                "mean": float(np.mean(g)),
                "median": float(np.median(g)),
                "sd": float(np.std(g, ddof=1)) if len(g) > 1 else None,
            }
        )
    out.update(
        {
            "method": method,
            "statistic": float(t)
            if parametric and not paired
            else float(
                u if not parametric and not paired else (w if paired and not parametric else t)
            ),
            "p_value": float(p),
            "effect_size": es,
            "ci95_diff": ci,
            "alternative": alternative,
            "paired": paired,
        }
    )
    spss = f"{method} on {value_col} BY {group_col}.\n"
    vp = _seal_tool(
        "stat_compare_groups",
        f"{value_col}~{group_col}",
        method,
        df,
        out,
        effect_size=es,
        p_value=float(p),
        ci=ci,
        spss_syntax=spss,
    )
    return vp.to_dict() | out | {"spss_syntax": spss}


# ---------------------------------------------------------------------------
# 4. stat_anova
# ---------------------------------------------------------------------------


def stat_anova(
    file_path: str,
    value_col: str,
    group_col: str,
    *,
    parametric: bool = True,
    welch: bool = False,
    post_hoc: bool = True,
) -> dict:
    df = _df(file_path)
    if value_col not in df.columns or group_col not in df.columns:
        return {"verdict": "VOID", "error": "missing column"}
    out = {"value_col": value_col, "group_col": group_col}
    p = es = None
    spss = ""
    if parametric and not welch:
        model = ols(f"{value_col} ~ C({group_col})", data=df).fit()
        a = __import__("statsmodels.api", fromlist=["stats"]).stats.anova_lm(model, typ=2)
        f = float(a["F"].iloc[0])
        p = float(a["PR(>F)"].iloc[0])
        method = "One-way ANOVA (Type II)"
        es = float(pg.anova(data=df, dv=value_col, between=group_col, effsize="np2")["np2"].iloc[0])
        out["anova_table"] = json.loads(a.to_json())
        spss = f"ONEWAY {value_col} BY {group_col} /STATISTICS=HOMOGENEITY.\n"
        if post_hoc and p < 0.05:
            tukey = pairwise_tukeyhsd(
                df[value_col].dropna(),
                df.loc[df[value_col].notna(), group_col],
                alpha=0.05,
            )
            out["tukey_hsd"] = str(tukey)
            spss += "* Post-hoc: Tukey HSD significant at p<0.05\n"
    elif welch:
        a = pg.welch_anova(data=df, dv=value_col, between=group_col)
        f = float(a["F"].iloc[0])
        p = float(a["p-unc"].iloc[0])
        method = "Welch's ANOVA"
        es = float(a["np2"].iloc[0])
        out["welch_table"] = json.loads(a.to_json())
    else:
        h, p = stats.kruskal(*[g[value_col].dropna().values for _, g in df.groupby(group_col)])
        f = h
        method = "Kruskal-Wallis H"
        es = float(
            pg.kruskal(data=df, dv=value_col, between=group_col, effsize="epsilon2")[
                "epsilon2"
            ].iloc[0]
        )
        spss = f"NPAR TEST K-W={value_col} BY {group_col}.\n"
    out.update(
        {
            "method": method,
            "statistic": float(f),
            "p_value": float(p),
            "effect_size": es,
        }
    )
    vp = _seal_tool(
        "stat_anova",
        f"{value_col}~{group_col}",
        method,
        df,
        out,
        effect_size=es,
        p_value=float(p),
        spss_syntax=spss,
    )
    return vp.to_dict() | out | {"spss_syntax": spss}


# ---------------------------------------------------------------------------
# 5. stat_correlate
# ---------------------------------------------------------------------------


def stat_correlate(
    file_path: str,
    x: str,
    y: str,
    *,
    method: str = "pearson",
) -> dict:
    df = _df(file_path)
    if x not in df.columns or y not in df.columns:
        return {"verdict": "VOID", "error": "missing column"}
    pair = df[[x, y]].dropna()
    m = method.lower()
    if m == "pearson":
        r, p = stats.pearsonr(pair[x], pair[y])
    elif m == "spearman":
        r, p = stats.spearmanr(pair[x], pair[y])
    elif m == "kendall":
        r, p = stats.kendalltau(pair[x], pair[y])
    else:
        return {"verdict": "VOID", "error": f"unknown method {method}"}
    # CI for Pearson via Fisher z
    if m == "pearson" and abs(r) < 1 and len(pair) > 3:
        z = math.atanh(r)
        se = 1 / math.sqrt(len(pair) - 3)
        ci = [round(math.tanh(z - 1.96 * se), 4), round(math.tanh(z + 1.96 * se), 4)]
    else:
        ci = [None, None]
    out = {
        "method": f"{m} correlation",
        "n": int(len(pair)),
        "r": float(r),
        "p_value": float(p),
        "ci95": ci,
    }
    spss = f"CORRELATIONS /VARIABLES={x} {y} /PRINT=TWOTAIL NOSIG.\n"
    vp = _seal_tool(
        "stat_correlate",
        f"{x}~{y}",
        m,
        df,
        out,
        effect_size=float(r),
        p_value=float(p),
        ci=ci,
        spss_syntax=spss,
    )
    return vp.to_dict() | out | {"spss_syntax": spss}


# ---------------------------------------------------------------------------
# 6. stat_regress
# ---------------------------------------------------------------------------


def stat_regress(
    file_path: str,
    dependent: str,
    independents: list[str],
    *,
    family: str = "ols",  # ols | logistic | robust
    robust: bool = False,
) -> dict:
    df = _df(file_path)
    if dependent not in df.columns or any(c not in df.columns for c in independents):
        return {"verdict": "VOID", "error": "missing column(s)"}
    sub = df[[dependent, *independents]].dropna()
    if family == "logistic":
        from statsmodels.discrete.discrete_model import Logit

        y = (sub[dependent] > sub[dependent].median()).astype(int)
        X = sub[independents].astype(float)
        X = _add_const(X)
        model = Logit(y, X).fit(disp=0, maxiter=200)
        method = "Logistic regression (median split)"
    else:
        formula = f"{dependent} ~ " + " + ".join(independents)
        if robust or family == "robust":
            model = ols(formula, data=sub).fit(cov_type="HC3")
            method = "OLS (robust HC3)"
        else:
            model = ols(formula, data=sub).fit()
            method = "OLS"
    out = {
        "method": method,
        "n": int(model.nobs),
        "r_squared": float(getattr(model, "rsquared", float("nan"))),
        "adj_r_squared": float(getattr(model, "rsquared_adj", float("nan"))),
        "f_stat": float(getattr(model, "fvalue", float("nan")))
        if hasattr(model, "fvalue")
        else None,
        "f_pvalue": float(getattr(model, "f_pvalue", float("nan")))
        if hasattr(model, "f_pvalue")
        else None,
        "aic": float(getattr(model, "aic", float("nan"))),
        "bic": float(getattr(model, "bic", float("nan"))),
        "coefficients": json.loads(
            pd.DataFrame(
                {
                    "coef": model.params,
                    "se": model.bse,
                    "t": model.tvalues,
                    "p": model.pvalues,
                    "ci_lo": model.conf_int().iloc[:, 0],
                    "ci_hi": model.conf_int().iloc[:, 1],
                }
            ).to_json()
        ),
    }
    # VIF for OLS
    if family in {"ols", "robust"} and len(independents) >= 2:
        Xc = _add_const(sub[independents].astype(float))
        out["vif"] = {
            independents[i]: float(variance_inflation_factor(Xc.values, i + 1))
            for i in range(len(independents))
        }
    spss = f"REGRESSION /DEPENDENT={dependent} /METHOD=ENTER {' '.join(independents)} /STATISTICS=COEFF R ANOVA COLLIN TOL.\n"
    vp = _seal_tool(
        "stat_regress",
        f"{dependent}~{'+'.join(independents)}",
        method,
        df,
        out,
        spss_syntax=spss,
    )
    return vp.to_dict() | out | {"spss_syntax": spss}


def _add_const(X: pd.DataFrame) -> pd.DataFrame:
    from statsmodels.tools import add_constant

    return add_constant(X, has_constant="add")


# ---------------------------------------------------------------------------
# 7. stat_chi_square
# ---------------------------------------------------------------------------


def stat_chi_square(
    file_path: str,
    var_a: str,
    var_b: str,
    *,
    test: str = "independence",  # independence | gof
    expected: Optional[list] = None,
) -> dict:
    df = _df(file_path)
    if var_a not in df.columns or var_b not in df.columns:
        return {"verdict": "VOID", "error": "missing column"}
    if test == "independence":
        ct = pd.crosstab(df[var_a], df[var_b])
        chi2, p, dof, exp = stats.chi2_contingency(ct)
        method = "Pearson chi-square (independence)"
        n = int(ct.values.sum())
        cramers_v = float(np.sqrt(chi2 / (n * (min(ct.shape) - 1)))) if min(ct.shape) > 1 else None
        out = {
            "method": method,
            "n": n,
            "chi2": float(chi2),
            "dof": int(dof),
            "p_value": float(p),
            "cramers_v": cramers_v,
            "contingency": json.loads(ct.to_json()),
            "expected_min": float(exp.min()) if hasattr(exp, "min") else None,
        }
    else:
        obs = df[var_a].dropna().value_counts().sort_index()
        if expected is None:
            expected = [obs.sum() / len(obs)] * len(obs)
        chi2, p = stats.chisquare(obs.values, expected)
        method = "Chi-square goodness-of-fit"
        out = {
            "method": method,
            "n": int(obs.sum()),
            "chi2": float(chi2),
            "dof": int(len(obs) - 1),
            "p_value": float(p),
            "observed": json.loads(obs.to_json()),
            "expected": list(expected),
        }
    spss = (
        f"CROSSTABS /TABLES={var_a} BY {var_b} /CELLS=COUNT COLUMN /STATISTICS=CHISQ PHI CRAMER.\n"
    )
    vp = _seal_tool(
        "stat_chi_square",
        f"{var_a} x {var_b}",
        method,
        df,
        out,
        effect_size=out.get("cramers_v"),
        p_value=float(p),
        spss_syntax=spss,
    )
    return vp.to_dict() | out | {"spss_syntax": spss}


# ---------------------------------------------------------------------------
# 8. stat_nonparametric
# ---------------------------------------------------------------------------


def stat_nonparametric(
    file_path: str,
    value_col: str,
    group_col: Optional[str] = None,
    *,
    test: str = "wilcoxon",  # wilcoxon | sign | friedman
    mu: float = 0.0,
) -> dict:
    df = _df(file_path)
    if value_col not in df.columns:
        return {"verdict": "VOID", "error": "missing column"}
    out = {"test": test, "value_col": value_col}
    if test == "wilcoxon":
        s = df[value_col].dropna()
        w, p = stats.wilcoxon(s - mu, alternative="two-sided")
        method = "Wilcoxon signed-rank (1 sample)"
        out.update(
            {
                "n": int(len(s)),
                "median": float(s.median()),
                "W": float(w),
                "p_value": float(p),
            }
        )
    elif test == "sign":
        s = df[value_col].dropna()
        diff = (s - mu).astype(float)
        pos = int((diff > 0).sum())
        neg = int((diff < 0).sum())
        m = min(pos, neg)
        n = pos + neg
        p = float(2 * stats.binom.cdf(m, n, 0.5)) if n > 0 else 1.0
        method = "Sign test"
        out.update({"n": n, "positives": pos, "negatives": neg, "p_value": p})
    elif test == "friedman":
        if not group_col or group_col not in df.columns:
            return {"verdict": "VOID", "error": "friedman needs group_col"}
        wide = df.pivot_table(index=df.index, columns=group_col, values=value_col).dropna()
        chi2, p = stats.friedmanchisquare(*[wide[c].values for c in wide.columns])
        method = "Friedman test (repeated measures)"
        out.update(
            {
                "n_subjects": int(len(wide)),
                "k_groups": int(wide.shape[1]),
                "Q": float(chi2),
                "p_value": float(p),
            }
        )
    else:
        return {"verdict": "VOID", "error": f"unknown test {test}"}
    vp = _seal_tool(
        "stat_nonparametric",
        f"{value_col} ({test})",
        method,
        df,
        out,
        p_value=out.get("p_value"),
    )
    return vp.to_dict() | out


# ---------------------------------------------------------------------------
# 9. stat_effect_size
# ---------------------------------------------------------------------------


def stat_effect_size(
    *,
    kind: str,  # cohens_d | eta_squared | cramers_v | odds_ratio
    file_path: Optional[str] = None,
    x: Optional[list] = None,
    y: Optional[list] = None,
    var_a: Optional[str] = None,
    var_b: Optional[str] = None,
) -> dict:
    """Pure effect-size calculator. If file_path+columns given, read from there."""
    out: dict = {"kind": kind}
    if kind == "cohens_d" and x and y:
        d = float(
            pg.compute_effsize(
                np.asarray(x, dtype=float), np.asarray(y, dtype=float), eftype="cohen"
            )
        )
        out.update({"cohens_d": d, "interpretation": _interpret_d(d)})
    elif kind == "eta_squared" and file_path and var_a and var_b:
        df = _df(file_path)
        a = pg.anova(data=df, dv=var_b, between=var_a, effsize="np2")
        eta = float(a["np2"].iloc[0])
        out.update({"eta_squared": eta, "interpretation": _interpret_eta(eta)})
    elif kind == "cramers_v" and file_path and var_a and var_b:
        df = _df(file_path)
        ct = pd.crosstab(df[var_a], df[var_b])
        chi2, _, _, _ = stats.chi2_contingency(ct)
        n = int(ct.values.sum())
        v = float(np.sqrt(chi2 / (n * (min(ct.shape) - 1)))) if min(ct.shape) > 1 else None
        out.update({"cramers_v": v, "interpretation": _interpret_v(v)})
    elif kind == "odds_ratio" and file_path and var_a and var_b:
        df = _df(file_path)
        ct = pd.crosstab(df[var_a], df[var_b])
        if ct.shape != (2, 2):
            return {"verdict": "VOID", "error": "odds_ratio needs 2x2 table"}
        a, b = ct.iloc[0, 0], ct.iloc[0, 1]
        c, d = ct.iloc[1, 0], ct.iloc[1, 1]
        or_ = (a * d) / (b * c) if b * c > 0 else float("inf")
        se_ln = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d) if min(a, b, c, d) > 0 else None
        ci = (
            [
                round(math.exp(math.log(or_) - 1.96 * se_ln), 4),
                round(math.exp(math.log(or_) + 1.96 * se_ln), 4),
            ]
            if se_ln
            else [None, None]
        )
        out.update({"odds_ratio": float(or_), "ci95": ci})
    else:
        return {"verdict": "VOID", "error": f"unsupported kind/args: {kind}"}
    seal.seal(
        actor="arif-fazil",
        tool="stat_effect_size",
        action=kind,
        verdict="SEAL",
        method=kind,
        input_hash=governance.hash_payload(out),
        result_summary=out,
    )
    return {"verdict": "SEAL", **out}


def _interpret_d(d: float) -> str:
    a = abs(d)
    if a < 0.2:
        return "negligible"
    if a < 0.5:
        return "small"
    if a < 0.8:
        return "medium"
    return "large"


def _interpret_eta(e: float) -> str:
    if e < 0.01:
        return "negligible"
    if e < 0.06:
        return "small"
    if e < 0.14:
        return "medium"
    return "large"


def _interpret_v(v: Optional[float]) -> str:
    if v is None:
        return "n/a"
    if v < 0.1:
        return "negligible"
    if v < 0.3:
        return "small"
    if v < 0.5:
        return "medium"
    return "large"


# ---------------------------------------------------------------------------
# 10. stat_power
# ---------------------------------------------------------------------------


def stat_power(
    *,
    test: str,  # t | f | chi2 | z
    effect_size: float,
    alpha: float = 0.05,
    power: Optional[float] = None,
    nobs: Optional[int] = None,
    alternative: str = "two-sided",
) -> dict:
    """Solve for whichever quantity is missing. Returns the solved value plus
    the others for context."""
    out: dict = {
        "test": test,
        "alpha": alpha,
        "effect_size": effect_size,
        "target_power": power,
        "nobs": nobs,
        "alternative": alternative,
    }
    if test == "t":
        ana = sm_power.TTestIndPower()
    elif test == "f":
        ana = sm_power.FTestPower()
    elif test == "chi2":
        ana = sm_power.GofChisquarePower()
    elif test == "z":
        ana = sm_power.NormalIndPower()
    else:
        return {"verdict": "VOID", "error": f"unknown test {test}"}
    if nobs is None and power is not None:
        out["solved_nobs"] = int(
            math.ceil(ana.solve_power(effect_size=effect_size, alpha=alpha, power=power))
        )
    elif power is None and nobs is not None:
        out["solved_power"] = float(
            ana.solve_power(effect_size=effect_size, alpha=alpha, nobs=nobs)
        )
    else:
        return {"verdict": "VOID", "error": "supply exactly one of power or nobs"}
    seal.seal(
        actor="arif-fazil",
        tool="stat_power",
        action=test,
        verdict="SEAL",
        method=f"statsmodels power ({test})",
        input_hash=governance.hash_payload(out),
        result_summary=out,
    )
    return {"verdict": "SEAL", **out}


# ---------------------------------------------------------------------------
# 11. stat_outliers
# ---------------------------------------------------------------------------


def stat_outliers(
    file_path: str,
    columns: list[str],
    *,
    method: str = "iqr",  # iqr | z | modified_z | mahalanobis
    threshold: float = 1.5,
) -> dict:
    df = _df(file_path)
    cols = [c for c in columns if c in df.columns]
    out: dict = {"method": method, "threshold": threshold, "per_column": {}}
    for c in cols:
        s = df[c].dropna()
        if not pd.api.types.is_numeric_dtype(s):
            continue
        if method == "z":
            z = (s - s.mean()) / s.std(ddof=0)
            mask = z.abs() > threshold
        elif method == "modified_z":
            med = s.median()
            mad = (s - med).abs().median()
            if mad == 0:
                continue
            mz = 0.6745 * (s - med) / mad
            mask = mz.abs() > threshold
        elif method == "mahalanobis":
            if len(cols) < 2:
                continue
            sub = df[cols].dropna()
            cov = np.cov(sub.values, rowvar=False)
            mean = sub.mean().values
            try:
                inv = np.linalg.pinv(cov)
            except np.linalg.LinAlgError:
                continue
            diff = sub.values - mean
            d2 = (diff @ inv * diff).sum(axis=1)
            from scipy.stats import chi2

            cutoff = chi2.ppf(1 - 0.001, df=len(cols))
            mask = pd.Series(d2 > cutoff, index=sub.index)
        else:  # iqr
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            lo, hi = q1 - threshold * iqr, q3 + threshold * iqr
            mask = (s < lo) | (s > hi)
        idx = list(s[mask].index.astype(int))
        out["per_column"][c] = {
            "n_outliers": int(mask.sum()),
            "pct_outliers": round(100 * mask.sum() / max(len(s), 1), 2),
            "outlier_indices": idx[:50],
            "n_truncated": max(0, len(idx) - 50),
        }
    out["n_total_outliers"] = sum(p["n_outliers"] for p in out["per_column"].values())
    seal.seal(
        actor="arif-fazil",
        tool="stat_outliers",
        action=method,
        verdict="SEAL",
        method=method,
        input_hash=governance.hash_payload({"cols": cols}),
        result_summary=out,
    )
    return {"verdict": "SEAL", **out}


# ---------------------------------------------------------------------------
# 12. stat_missing
# ---------------------------------------------------------------------------


def stat_missing(file_path: str) -> dict:
    df = _df(file_path)
    n = len(df)
    out: dict = {
        "n_rows": n,
        "n_cols": int(df.shape[1]),
        "total_missing": int(df.isna().sum().sum()),
        "pct_missing_total": round(100 * df.isna().sum().sum() / max(df.size, 1), 2),
        "per_column": {},
    }
    for c in df.columns:
        m = int(df[c].isna().sum())
        out["per_column"][c] = {"missing": m, "pct": round(100 * m / max(n, 1), 2)}
    # Pattern
    out["missing_pattern"] = json.loads(
        df.isna().value_counts().head(10).rename("count").reset_index().to_json()
    )
    # Little's MCAR test (approximate via correlation of missingness indicators)
    inds = df.isna().astype(int)
    if inds.shape[1] > 1:
        chi2 = 0.0
        dof = 0
        observed_missing = bool(inds.sum().sum() > 0)
        if observed_missing:
            for i, a in enumerate(inds.columns):
                for b in inds.columns[i + 1 :]:
                    tab = pd.crosstab(inds[a], inds[b])
                    if tab.shape == (2, 2) and tab.values.min() > 0:
                        chi2 += float(stats.chi2_contingency(tab, correction=False)[0])
                        dof += 1
        out["littles_mcar_approx"] = {
            "chi2_approx": chi2,
            "dof_approx": dof,
            "observed_missing": observed_missing,
            "verdict_at_alpha_0.05": (chi2 > stats.chi2.ppf(0.95, dof)) if dof > 0 else None,
            "note": "approximation: pairwise tests of missingness; full Little (1988) requires EM",
        }
    seal.seal(
        actor="arif-fazil",
        tool="stat_missing",
        action="profile",
        verdict="SEAL",
        method="pandas + Little's MCAR approx",
        input_hash=governance.hash_payload({"n": n, "cols": list(df.columns)}),
        result_summary=out,
    )
    return {"verdict": "SEAL", **out}
