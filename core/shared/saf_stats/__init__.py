"""SAF — Statistical Analysis Forge (merged into arifOS kernel as shared lib).

Migrated: 2026-06-02 per L13 SOVEREIGN directive
Origin:   /root/SAF/ sovereign organ (port 18084, decommissioned)
Auth:     AGI OPENCLAW (agi@arif-fazil.com), Copilot co-author

DITEMPA BUKAN DIBERI — Forged, Not Given.

────────────────────────────────────────────────────────────────────────────
SHARED LIB — used by WEALTH, GEOX, WELL
────────────────────────────────────────────────────────────────────────────
Each organ imports the 12 stat_* tools and re-exposes them under its own
namespace (wealth_*, geox_*, well_*) with domain-specific defaults and
documentation. One implementation, three consumers.

The 12 stat_* tools (scipy / statsmodels / pingouin):
  1.  stat_descriptives      univariate summary with skew, kurt, IQR, MAD
  2.  stat_assumptions       Shapiro-Wilk, Levene, normality, homosced.
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

The 7 SPSS read tools (pyreadstat):
  1.  list_data_files
  2.  inspect_spss_metadata
  3.  preview_spss_data
  4.  profile_spss_data
  5.  convert_spss_to_csv
  6.  convert_csv_to_sav
  7.  generate_basic_spss_syntax

F1 AMANAH: every outcome seals to VAULT999/outcomes.jsonl
F6 PRIVACY: all file I/O resolves under SAF_DATA_ROOT (sandbox)
L13 SOVEREIGN: destructive ops (impute, overwrite) require ack_irreversible
"""

from . import governance, report, sandbox, seal, spss_read

# Public API — governance primitives
from .governance import (
    ALL_FLOORS,
    ConstitutionalCheck,
    Verdict,
    VerdictPacket,
    govern,
    hash_payload,
)

# Public API — 12 stat_* tools (file-based interface)
from .inferential import (
    stat_anova,
    stat_assumptions,
    stat_chi_square,
    stat_compare_groups,
    stat_correlate,
    stat_descriptives,
    stat_effect_size,
    stat_missing,
    stat_nonparametric,
    stat_outliers,
    stat_power,
    stat_regress,
)

# Public API — 1 report composer
from .report import compose_report as stat_report

# Public API — sandbox primitives
from .sandbox import (
    ALLOWED_READ_EXTS,
    ALLOWED_WRITE_EXTS,
    get_data_root,
    relative_to_root,
    safe_resolve,
)
from .seal import (
    SealRecord,
    verify_chain,
)

# Public API — seal primitives
from .seal import (
    seal as vault_seal,
)

# Public API — 7 SPSS read tools
from .spss_read import (
    convert_csv_to_sav,
    convert_spss_to_csv,
    generate_basic_spss_syntax,
    inspect_spss_metadata,
    list_data_files,
    preview_spss_data,
    profile_spss_data,
)

__all__ = [
    # 12 stat_* tools
    "stat_descriptives",
    "stat_assumptions",
    "stat_compare_groups",
    "stat_anova",
    "stat_correlate",
    "stat_regress",
    "stat_chi_square",
    "stat_nonparametric",
    "stat_effect_size",
    "stat_power",
    "stat_outliers",
    "stat_missing",
    # 7 SPSS read tools
    "list_data_files",
    "inspect_spss_metadata",
    "preview_spss_data",
    "profile_spss_data",
    "convert_spss_to_csv",
    "convert_csv_to_sav",
    "generate_basic_spss_syntax",
    # 1 report composer
    "stat_report",
    # governance
    "Verdict",
    "VerdictPacket",
    "ConstitutionalCheck",
    "ALL_FLOORS",
    "govern",
    "hash_payload",
    # sandbox
    "safe_resolve",
    "get_data_root",
    "relative_to_root",
    "ALLOWED_READ_EXTS",
    "ALLOWED_WRITE_EXTS",
    # seal
    "vault_seal",
    "verify_chain",
    "SealRecord",
]
