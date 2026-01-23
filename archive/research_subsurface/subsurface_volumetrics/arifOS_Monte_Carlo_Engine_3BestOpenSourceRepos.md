# arifOS Monte Carlo Engine: Best Open Source Repos Analysis
## The "Boring Math" You Don't Need to Reinvent

**Date:** December 13, 2025  
**Truth:** It's multiplication with uncertainty. Copy the pattern, inject your basin laws.

---

## The Verdict: THREE Repos to Know

| Rank | Repo | Author | Use Case | Pattern |
|------|------|--------|----------|----------|
| **🥇 BEST** | `pyreservoir` | yohanesnuwara | Production-grade volumetric library | Full integration |
| **🥈 SNIPER** | `Volumetrics` | salsa360 | Clean Monte Carlo pattern (scipy.stats) | Copy the loop |
| **🥉 REFERENCE** | `oil_volume_calculator` | rghalayini | Probabilistic calculator walkthrough | Learning |

---

## 🥇 BEST: `pyreservoir` by Yohanes Nuwara

**GitHub:** https://github.com/yohanesnuwara/pyreservoir  
**Status:** ✓ Active (2024)  
**Why:** Production-grade, structured library (not just equations)

### Modules:
- `volumetrics` — OOIP/OGIP deterministic (Trapezoidal/Simpson rules)
- `matbal` — Material balance (cross-check volumetric estimates)
- `dca` — Decline curve + Monte Carlo bootstrap
- `pvt` — Archie, Standing, McCain correlations
- `welltest` — Pressure drawdown analysis

### Quick Integration:

```python
from pyreservoir.volumetrics import volumetrics_trapezoidal

stoiip = volumetrics_trapezoidal(area, thickness, porosity, saturation, bo)
```

✓ **Use This:** For deterministic Layer 4-5 calculations (point estimates)

---

## 🥈 SNIPER: `Volumetrics` by salsa360

**GitHub:** https://github.com/salsa360/Volumetrics  
**File:** `Monte Carlo Oil Volumetrics - Part 1.ipynb`  
**Why:** Clean 30-line Monte Carlo pattern using scipy.stats

### The Exact Pattern to Copy:

```python
from scipy.stats import norm
import numpy as np

n = 10000

# Define distributions
area = norm(loc=200, scale=50).rvs(n)           # Normal distribution
thickness = norm(loc=100, scale=25).rvs(n)
porosity = norm(loc=0.32, scale=0.02).rvs(n)
sw = norm(loc=0.35, scale=0.05).rvs(n)
bo = norm(loc=1.28, scale=0.05).rvs(n)

# Vectorized calculation (no loops)
results = (area * thickness * porosity * (1 - sw) / bo * 5.614583) / 1e6

# Extract percentiles
p90 = np.percentile(results, 90)
p50 = np.percentile(results, 50)
p10 = np.percentile(results, 10)
```

✓ **Use This:** For Monte Carlo Layer 5 calculations (P10/P50/P90)

---

## 🥉 REFERENCE: `oil_volume_calculator` by rghalayini

**GitHub:** https://github.com/rghalayini/oil_volume_calculator  
**What:** Working example (oil + gas) with visualization  
**Why:** Shows complete probabilistic workflow end-to-end

✓ **Use This:** For learning the full pipeline + plotting results

---

## The One Formula You Need (Memorize)

```
STOIIP = (Area × Thickness × Porosity × (1 - Saturation)) / Bo × 5.614583 / 1,000,000

For Monte Carlo:
  - Draw 10,000 random samples from each distribution
  - Calculate STOIIP for each sample
  - Extract P10 (10th percentile), P50 (50th), P90 (90th)

That's it. Everything else is: 
  1. Defining the distributions (your basin model)
  2. Uncertainty propagation (randomness)
  3. Visualization (histograms)
```

---

## arifOS Integration Strategy

### Option 1: USE pyreservoir (Recommended)

```python
from pyreservoir.volumetrics import volumetrics_trapezoidal
from arifOS import predict_basin_parameters

def volumetric_point_estimate(basin, depth, area, thick):
    params = predict_basin_parameters(basin, depth)  # arifOS basin model
    stoiip = volumetrics_trapezoidal(area, thick, 
                                      params['porosity'], 
                                      params['saturation'],
                                      params['bo'])
    return stoiip * params['recovery_factor']
```

**Time:** 1-2 weeks (production-ready)

---

### Option 2: COPY salsa360 Pattern (Fast)

```python
from scipy.stats import norm
import numpy as np
from arifOS import predict_basin_parameters

def volumetric_monte_carlo(basin, depth, area, thick, n=10000):
    # Get point estimate from basin model
    p50 = predict_basin_parameters(basin, depth)
    
    # Define distributions around point estimate
    area_dist = norm(loc=area*247.105, scale=area*0.20)
    thick_dist = norm(loc=thick, scale=thick*0.15)
    phi_dist = norm(loc=p50['porosity'], scale=p50['porosity']*0.10)
    sw_dist = norm(loc=p50['saturation'], scale=p50['saturation']*0.15)
    bo_dist = norm(loc=p50['bo'], scale=p50['bo']*0.05)
    
    # Generate samples
    results = (area_dist.rvs(n) * thick_dist.rvs(n) * phi_dist.rvs(n) * 
               (1 - sw_dist.rvs(n)) / bo_dist.rvs(n) * 5.614583) / 1e6
    
    # Extract percentiles
    return {
        'p10': np.percentile(results, 10),
        'p50': np.percentile(results, 50),
        'p90': np.percentile(results, 90)
    }
```

**Time:** 3-5 days (lean implementation)

---

### Option 3: COMBINE Both (Best)

- **pyreservoir** for deterministic point estimates
- **salsa360 pattern** for Monte Carlo around point
- Inject **arifOS basin laws** into distributions

**Time:** 1 week (production-grade + custom uncertainty)

---

## Your Week 1 Build Plan

```yaml
Day_1:
  Clone: yohanesnuwara/pyreservoir
  Test: volumetrics on Tapis field (known benchmark)
  Goal: Verify STOIIP within 10% of actual

Day_2:
  Clone: salsa360/Volumetrics
  Study: Extract Monte Carlo loop (30 lines)
  Copy: Pattern into your predictor.py

Day_3:
  Integrate: pyreservoir + salsa360 + arifOS
  Code: Full volumetric calculator (deterministic + stochastic)
  Test: Tapis field (recoverable should match ~100 MMstb)

Day_4:
  Polish: Add killer questions (Organ 5) + PRMS check (Organ 4)
  Deploy: predictor.py ready for GPT
```

---

## Commands to Get Started

```bash
git clone https://github.com/yohanesnuwara/pyreservoir.git
git clone https://github.com/salsa360/Volumetrics.git
cd pyreservoir && pip install -e .
jupyter notebook ../Volumetrics/"Monte Carlo Oil Volumetrics - Part 1.ipynb"
```

---

**You do NOT need to reinvent the wheel. Copy, inject your basin laws, deploy. 🔥**