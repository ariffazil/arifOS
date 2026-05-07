"""
GEOX 1D Joint Inversion — CANON_9 from seismic + logs.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, Field
from typing import Literal
from dataclasses import dataclass

from .canon9_profile import Canon9Profile
from .rock_physics import GassmannModel
from .synthetic import SyntheticSeismic, SyntheticCMP


@dataclass
class MisfitResult:
    """Misfit calculation result."""

    total: float
    seismic: float
    logs: float
    regularization: float


class InversionResult(BaseModel):
    """Result of joint inversion."""

    profile: Canon9Profile
    misfit_history: list[float] = Field(default_factory=list)
    converged: bool = False
    iterations: int = 0

    # Uncertainty
    posterior_std: dict[str, np.ndarray] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class JointInversion1D:
    """
    1D joint inversion: seismic + logs → CANON_9.

    Inverts for:
    - Porosity (φ)
    - Water saturation (Sw)
    - Mineral fractions (implicit in rock physics)

    Given:
    - Observed seismic CMP
    - Observed logs (Vp, Vs, density, resistivity)
    - Prior model (initial guess)

    Uses gradient descent or MCMC to minimize:
    J = ||seis_obs - seis_pred||² + ||logs_obs - logs_pred||² + α||x - x_prior||²
    """

    def __init__(
        self,
        rock_physics: GassmannModel | None = None,
        synthetic: SyntheticSeismic | None = None,
        method: Literal["gradient", "monte-carlo"] = "gradient",
    ):
        self.rock_physics = rock_physics or GassmannModel()
        self.synthetic = synthetic or SyntheticSeismic()
        self.method = method

        # Weights for misfit components
        self.w_seismic = 1.0
        self.w_logs = 1.0
        self.w_prior = 0.1

    def forward(
        self, profile: Canon9Profile, mineral_fractions: list[dict[str, float]] | None = None
    ) -> tuple[SyntheticCMP, dict]:
        """
        Forward model: CANON_9 → synthetic seismic + predicted logs.

        Args:
            profile: Current estimate of CANON_9 profile
            mineral_fractions: Mineral composition per layer (or single dict for all)

        Returns:
            (synthetic CMP, predicted logs dict)
        """
        # Apply rock physics to get elastic properties
        processed_samples = []

        for i, sample in enumerate(profile.samples):
            # Get mineral fractions for this layer
            if mineral_fractions is None:
                # Default: clean sand
                minerals = {"quartz": 0.9, "clay": 0.1}
            elif isinstance(mineral_fractions, list):
                minerals = (
                    mineral_fractions[i] if i < len(mineral_fractions) else mineral_fractions[-1]
                )
            else:
                minerals = mineral_fractions

            # Forward rock physics
            processed = self.rock_physics.forward(sample, minerals)
            processed_samples.append(processed)

        processed_profile = Canon9Profile(
            well_id=profile.well_id,
            samples=processed_samples,
            tdr_depths=profile.tdr_depths,
            tdr_times=profile.tdr_times,
        )

        # Generate synthetic seismic
        synthetic = self.synthetic.generate(processed_profile)

        # Predicted logs
        logs_pred = {
            "vp": processed_profile.get_property("vp"),
            "vs": processed_profile.get_property("vs"),
            "density": processed_profile.get_property("density"),
            "resistivity": processed_profile.get_property("resistivity"),
        }

        return synthetic, logs_pred

    def misfit(
        self,
        profile: Canon9Profile,
        obs_seismic: SyntheticCMP | None,
        obs_logs: dict[str, np.ndarray],
        prior_profile: Canon9Profile | None = None,
    ) -> MisfitResult:
        """
        Compute misfit between observed and predicted data.
        """
        # Forward model
        synthetic, logs_pred = self.forward(profile)

        # Seismic misfit
        seis_misfit = 0.0
        if obs_seismic is not None:
            # Match time axes
            t_obs = obs_seismic.time
            t_pred = synthetic.time

            for i in range(len(obs_seismic.angles)):
                # Interpolate predicted to observed time
                trace_pred = np.interp(t_obs, t_pred, synthetic.traces[:, i], left=0, right=0)
                diff = obs_seismic.traces[:, i] - trace_pred
                seis_misfit += np.sum(diff**2)

        # Log misfit
        logs_misfit = 0.0
        for key in ["vp", "vs", "density", "resistivity"]:
            if key in obs_logs:
                diff = obs_logs[key] - logs_pred[key][: len(obs_logs[key])]
                logs_misfit += np.sum(diff**2)

        # Prior misfit (regularization)
        prior_misfit = 0.0
        if prior_profile is not None:
            for i, (s, s_prior) in enumerate(zip(profile.samples, prior_profile.samples)):
                prior_misfit += (s.porosity - s_prior.porosity) ** 2
                prior_misfit += (s.sw - s_prior.sw) ** 2

        total = (
            self.w_seismic * seis_misfit + self.w_logs * logs_misfit + self.w_prior * prior_misfit
        )

        return MisfitResult(
            total=total, seismic=seis_misfit, logs=logs_misfit, regularization=prior_misfit
        )

    def invert_gradient(
        self,
        prior_profile: Canon9Profile,
        obs_seismic: SyntheticCMP | None,
        obs_logs: dict[str, np.ndarray],
        max_iter: int = 100,
        step_size: float = 0.01,
        tolerance: float = 1e-6,
    ) -> InversionResult:
        """
        Gradient descent inversion.

        Optimizes: φ(z), Sw(z) to match observations.
        """
        # Current estimate
        current = Canon9Profile(
            well_id=prior_profile.well_id,
            samples=[s.model_copy() for s in prior_profile.samples],
            tdr_depths=prior_profile.tdr_depths[:],
            tdr_times=prior_profile.tdr_times[:],
        )

        misfit_history = []

        for iteration in range(max_iter):
            # Compute misfit
            misfit = self.misfit(current, obs_seismic, obs_logs, prior_profile)
            misfit_history.append(misfit.total)

            # Check convergence
            if len(misfit_history) > 1:
                if abs(misfit_history[-1] - misfit_history[-2]) < tolerance:
                    return InversionResult(
                        profile=current,
                        misfit_history=misfit_history,
                        converged=True,
                        iterations=iteration,
                    )

            # Simple gradient approximation (finite differences)
            for i, sample in enumerate(current.samples):
                # Gradient w.r.t. porosity
                delta = 0.001

                # Perturb phi
                sample.porosity += delta
                misfit_plus = self.misfit(current, obs_seismic, obs_logs, prior_profile).total
                sample.porosity -= 2 * delta
                misfit_minus = self.misfit(current, obs_seismic, obs_logs, prior_profile).total
                sample.porosity += delta  # Reset

                grad_phi = (misfit_plus - misfit_minus) / (2 * delta)

                # Update
                sample.porosity -= step_size * grad_phi
                sample.porosity = np.clip(sample.porosity, 0.0, 0.5)

                # Gradient w.r.t. Sw
                sample.sw += delta
                misfit_plus = self.misfit(current, obs_seismic, obs_logs, prior_profile).total
                sample.sw -= 2 * delta
                misfit_minus = self.misfit(current, obs_seismic, obs_logs, prior_profile).total
                sample.sw += delta  # Reset

                grad_sw = (misfit_plus - misfit_minus) / (2 * delta)

                # Update
                sample.sw -= step_size * grad_sw
                sample.sw = np.clip(sample.sw, 0.0, 1.0)

        return InversionResult(
            profile=current, misfit_history=misfit_history, converged=False, iterations=max_iter
        )

    def invert(
        self,
        prior_profile: Canon9Profile,
        obs_seismic: SyntheticCMP | None = None,
        obs_logs: dict[str, np.ndarray] | None = None,
        **kwargs,
    ) -> InversionResult:
        """
        Main inversion entry point.
        """
        if obs_logs is None:
            raise ValueError("At least log observations required")

        if self.method == "gradient":
            return self.invert_gradient(prior_profile, obs_seismic, obs_logs, **kwargs)
        else:
            raise NotImplementedError("Monte Carlo not yet implemented")
