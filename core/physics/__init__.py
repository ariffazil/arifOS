"""core.physics — Constitutional physics invariants for arifOS.

This package enforces the physical, thermodynamic, economic, and institutional
constraints that bind AI-mediated institutional action. Every invariant here is
a hard floor: if one breaks, the action is constitutional.

Modules:
  thermodynamics_hardened  — F1 energy/reversibility/entropy (invariants 1-5)
  economic_invariants      — capital conservation, optionality, hysteresis (6-10)
  institutional_evolution  — mortality/succession/absorption (invariant 15)
  thermo_budget            — session thermodynamic budget tracker

The pre_execution_gate imports from this package. Every module here runs BEFORE
any mutation-class or irreversible action is allowed to proceed.
"""

from __future__ import annotations

from typing import Any

__all__: list[str] = []

# ═══════════════════════════════════════════════════════
# Thermodynamics (hardened)
# ═══════════════════════════════════════════════════════
try:
    from core.physics.thermodynamics_hardened import (
        ThermodynamicError,
        ThermodynamicBudgetLedger,
        MaintenanceScaling,
        compute_exergy_ratio,
        apply_maintenance_decay,
        init_budget_ledger,
        get_budget_ledger,
        record_budget_operation,
    )
except ImportError as _exc:  # pragma: no cover - guarded for optional symbols
    ThermodynamicError = None  # type: ignore[misc,assignment]
    ThermodynamicBudgetLedger = None  # type: ignore[misc,assignment]
    MaintenanceScaling = None  # type: ignore[misc,assignment]
    compute_exergy_ratio = None  # type: ignore[misc,assignment]
    apply_maintenance_decay = None  # type: ignore[misc,assignment]
    init_budget_ledger = None  # type: ignore[misc,assignment]
    get_budget_ledger = None  # type: ignore[misc,assignment]
    record_budget_operation = None  # type: ignore[misc,assignment]

__all__.extend(
    [
        "ThermodynamicError",
        "ThermodynamicBudgetLedger",
        "MaintenanceScaling",
        "compute_exergy_ratio",
        "apply_maintenance_decay",
        "init_budget_ledger",
        "get_budget_ledger",
        "record_budget_operation",
    ]
)

# ═══════════════════════════════════════════════════════
# Economic invariants
# ═══════════════════════════════════════════════════════
try:
    from core.physics.economic_invariants import (
        EconomicInvariantError,
        MaintenanceScalingError,
        check_maintenance_scaling,
        run_all_invariants,
    )
except ImportError as _exc:  # pragma: no cover - guarded for optional symbols
    EconomicInvariantError = None  # type: ignore[misc,assignment]
    MaintenanceScalingError = None  # type: ignore[misc,assignment]
    check_maintenance_scaling = None  # type: ignore[misc,assignment]
    run_all_invariants = None  # type: ignore[misc,assignment]

__all__.extend(
    [
        "EconomicInvariantError",
        "MaintenanceScalingError",
        "check_maintenance_scaling",
        "run_all_invariants",
    ]
)

# ═══════════════════════════════════════════════════════
# Institutional evolution
# ═══════════════════════════════════════════════════════
try:
    from core.physics.institutional_evolution import (
        # Exception types
        SuccessionError,
        InstitutionalEvolutionError,
        AttentionBudgetExceededError,
        PopulationAbsorptionError,
        SuccessionContinuityError,
        AIAdaptationRateExceededError,
        # Function API
        check_human_attention_budget,
        check_institutional_succession,
        check_ai_adaptation_rate,
        check_population_absorption,
        check_institutional_evolution,
        # Guard class
        InstitutionalEvolutionGuard,
    )
except ImportError as _exc:  # pragma: no cover - guarded for optional symbols
    SuccessionError = None  # type: ignore[misc,assignment]
    InstitutionalEvolutionError = None  # type: ignore[misc,assignment]
    AttentionBudgetExceededError = None  # type: ignore[misc,assignment]
    PopulationAbsorptionError = None  # type: ignore[misc,assignment]
    SuccessionContinuityError = None  # type: ignore[misc,assignment]
    AIAdaptationRateExceededError = None  # type: ignore[misc,assignment]
    check_human_attention_budget = None  # type: ignore[misc,assignment]
    check_institutional_succession = None  # type: ignore[misc,assignment]
    check_ai_adaptation_rate = None  # type: ignore[misc,assignment]
    check_population_absorption = None  # type: ignore[misc,assignment]
    check_institutional_evolution = None  # type: ignore[misc,assignment]
    InstitutionalEvolutionGuard = None  # type: ignore[misc,assignment]

__all__.extend(
    [
        "SuccessionError",
        "InstitutionalEvolutionError",
        "AttentionBudgetExceededError",
        "PopulationAbsorptionError",
        "SuccessionContinuityError",
        "AIAdaptationRateExceededError",
        "check_human_attention_budget",
        "check_institutional_succession",
        "check_ai_adaptation_rate",
        "check_population_absorption",
        "check_institutional_evolution",
        "InstitutionalEvolutionGuard",
    ]
)
