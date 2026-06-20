"""arifosmcp.core.physics — Constitutional physics module."""

from __future__ import annotations

from typing import Any

__all__: list[str] = []

# ═══════════════════════════════════════════════════════
# Thermodynamics (hardened)
# ═══════════════════════════════════════════════════════
try:
    from arifosmcp.core.physics.thermodynamics_hardened import (
        MaintenanceScaling,
        ThermodynamicBudgetLedger,
        ThermodynamicError,
        apply_maintenance_decay,
        compute_exergy_ratio,
        get_budget_ledger,
        init_budget_ledger,
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

__all__.extend([
    "ThermodynamicError",
    "ThermodynamicBudgetLedger",
    "MaintenanceScaling",
    "compute_exergy_ratio",
    "apply_maintenance_decay",
    "init_budget_ledger",
    "get_budget_ledger",
    "record_budget_operation",
])

# ═══════════════════════════════════════════════════════
# Economic invariants
# ═══════════════════════════════════════════════════════
try:
    from arifosmcp.core.physics.economic_invariants import (
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

__all__.extend([
    "EconomicInvariantError",
    "MaintenanceScalingError",
    "check_maintenance_scaling",
    "run_all_invariants",
])

# ═══════════════════════════════════════════════════════
# Institutional evolution
# ═══════════════════════════════════════════════════════
try:
    from arifosmcp.core.physics.institutional_evolution import (
        AIAdaptationRateExceededError,
        AttentionBudgetExceededError,
        InstitutionalEvolutionError,
        # Guard class
        InstitutionalEvolutionGuard,
        PopulationAbsorptionError,
        SuccessionContinuityError,
        # Exception types
        SuccessionError,
        check_ai_adaptation_rate,
        # Function API
        check_human_attention_budget,
        check_institutional_evolution,
        check_institutional_succession,
        check_population_absorption,
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

__all__.extend([
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
])
