# GEOX 1D — Unit Cell of the Large Earth Model

**DITEMPA BUKAN DIBERI**

The 1D GEOX column is the **unit cell** where forward physics and inverse learning meet. Once solid, tile and couple it to build a Large Earth Model without changing the math.

---

## Concept

```
1D CANON_9 Column = Unit Cell
├── State: x(z) = {ρ, Vp, Vs, ρₑ, χ, k, P, T, φ} at each depth
├── Forward: x → synthetic seismic + logs
├── Inverse: (seismic, logs) → updated x
└── 000-999 Governance: anchored, auditable, sealed

Large Earth Model = Many 1D cells + lateral coupling
```

---

## Architecture

### Files

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `canon9_profile.py` | 1D state representation | `Canon9Profile`, `DepthSample` |
| `rock_physics.py` | Gassmann fluid substitution | `GassmannModel.forward()` |
| `reflectivity.py` | Seismic reflection | `ZoeppritzModel.compute_reflectivity()` |
| `synthetic.py` | Wavelet convolution | `SyntheticSeismic.generate()` |
| `inversion.py` | Joint inversion | `JointInversion1D.invert()` |
| `contrast_essential.py` | **ToAC governance (ESSENTIAL)** | `check_tuning_risk()`, `dual_frequency_stability_test()` |
| `demo.py` | Toy example | `main()` - gas sand detection |
| `schema_000_999.json` | arifOS pipeline mapping | Complete 000-999 stage definitions |

---

## Forward Chain: x(z) → Data

```
CANON_9 State x(z)
       │
       ▼
┌─────────────────┐
│  Rock Physics   │  Gassmann: {φ, P, T, Sw} → {ρ, Vp, Vs}
│  F_rock(x)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Reflectivity   │  Zoeppritz: elastic contrasts → R(θ)
│  F_reflect(x)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Synthetic      │  Convolution: R ⊗ W → traces
│  F_synth(x)     │
└────────┬────────┘
         │
    Synthetic CMP
    + Synthetic Logs
```

---

## Inverse Loop: Data → x(z)

```
Observed:                Prior:
├── Seismic CMP          └── x₀(z) (initial guess)
├── Logs (LAS)
└── Core/MDT (optional)
         │
         ▼
┌─────────────────┐
│  Joint Inversion│  min ||d_obs - F(x)||² + α||x - x_prior||²
│  argmin_x J(x)  │
└────────┬────────┘
         │
         ▼
Posterior: x*(z)
├── Updated φ(z), Sw(z)
├── Uncertainty envelope
└── 000-999 audit trail
```

---

## 000-999 Pipeline Mapping

| Stage | arifOS Name | GEOX 1D Function | Floor Check |
|-------|-------------|------------------|-------------|
| 000 | INIT | Load data, verify authority | F1, F13 |
| 111 | THINK | Select operators (Gassmann/Zoeppritz) | F4 |
| 222 | REASON | Propose geological priors | F7 |
| 333 | EXPLORE | Forward F(x) → synthetic | F2, F9 |
| 444 | RESPOND | Plan inversion update | F3 |
| 555 | VALIDATE | Check geological plausibility | F5, F6 |
| 666 | ALIGN | Ethics/regulatory check | F6, F11 |
| 777 | FORGE | Execute inversion numerically | F7 |
| 888 | AUDIT | Tri-witness verification | F3, F8 |
| 999 | SEAL | Commit to VAULT999 | F1, F11, F13 |

---

## Essential ToAC Governance (Minimal)

ToAC in 1D is **simpler** than 2D:

| Risk | 2D/3D | 1D |
|------|-------|-----|
| Display artifacts | Colormap, gain, AGC, migration | **Wavelet frequency, tuning** |
| Critical threshold | Bed thickness < λ/4 | Same |
| Uncertainty source | Velocity pull-up | **Time-depth conversion** |

### Essential Functions (`contrast_essential.py`)

```python
# 1. Tuning detection (F2 Truth)
alert = check_tuning_risk(bed_thickness=5.0, wavelet=Wavelet.ricker(30))
# Returns Alert if bed < λ/4 - amplitude unreliable

# 2. TDR uncertainty (F4 Clarity)
profile = propagate_td_uncertainty(profile, td_time_std=0.005)
# Adds depth_uncertainty to each sample

# 3. Frequency stability (F7 Humility)
score = dual_frequency_stability_test(profile, f1=25, f2=35)
# If unstable → 888_HOLD recommendation
```

**That's it.** No over-engineering. Essential contrast only.

## Demo Usage

```bash
cd /root/GEOX
python -m arifos.geox.oned.demo
```

**Output:**
```
============================================================
GEOX 1D Joint Inversion Demo
DITEMPA BUKAN DIBERI
============================================================

[1] Creating synthetic true model...
    Telemetry: [CANON9_PROFILE | DEMO-001 | n=100 | SEALED]

[2] Generating synthetic seismic...
    Wavelet: Ricker 30.0 Hz
    Angles: [0  5 10 15 20 25 30]

[3] Extracting observed logs...
    Vp range: 2800 to 3200 m/s

[4] Creating prior model...
    Prior φ: 0.200, Prior Sw: 0.800 (WRONG guess)

[5] Running joint inversion...
    Converged: True, Iterations: 2

[6] Results comparison...
    Porosity MAE: 0.3290
    Saturation MAE: 0.1680

[7] Gas sand identification...
    Gas detected: True/False
```

---

## Why This Scales

### 1D is the Unit Cell
- Forward/inverse physics validated at 1D
- Clean gradients and uncertainty diagnostics
- Same math in 1D, 2D, 3D

### Tiling to LEM
```
Large Earth Model = Grid of 1D columns + lateral coupling

Coupling adds:
├── Structural model (faults, horizons)
├── Flow connectivity (permeability between cells)
├── Wavefield propagation (2D/3D seismic)
└── Stress/strain (geomechanics)
```

### AGI Building Block
- LEM/LLM learns priors over grids of 1D states
- Forward/inverse are two directions of same loop
- Every change auditable back to data and physics

---

## Next Steps

1. **Improve inversion**: MCMC or neural surrogate vs gradient descent
2. **Add well-tie**: Real check-shot depth-time calibration
3. **Extend to 2D**: Line-based migration + tomography
4. **Couple columns**: Lateral flow, stress, wave propagation

---

## Schema Reference

Full 000-999 pipeline schema: `schema_000_999.json`

```json
{
  "pipeline": {
    "000_INIT_ANCHOR": {...},
    "111_THINK_SENSE": {...},
    ...
    "999_SEAL": {...}
  }
}
```

---

*DITEMPA BUKAN DIBERI — The 9D manifold is the unit cell.*
