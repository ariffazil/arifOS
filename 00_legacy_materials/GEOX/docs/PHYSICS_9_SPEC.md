# PHYSICS.9: THE GEOX STATE VECTOR

## MISSION: THE MINIMAL SEMANTIC BASIS

To build a **Large Earth Model (LEM)** capable of predictive forecasting and inverse synthesis, we must define the minimal set of physics variables that fully specify the material state of the crust.

GEOX rejects the "Rock-Physics Teaching Set" in favor of the **Metabolic State Vector**. We prioritize the *drivers* of dynamics over the *responses*.

---

## THE PHYSICS 9

| # | VARIABLE | SYMBOL | UNIT | WHY IT IS PHYSICS CORE |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Density** | **ρ** | kg/m³ | Primary mass measure; drives gravity and acoustic impedance. |
| **2** | **Compressional Velocity** | **Vp** | m/s | Primary mechanical signal; specifies longitudinal stiffness. |
| **3** | **Shear Velocity** | **Vs** | m/s | Secondary mechanical signal; specifies shear rigidity. |
| **4** | **Electrical Resistivity** | **ρₑ** | Ω·m | Fluid-state proxy; separates saline brine from hydrocarbons. |
| **5** | **Magnetic Susceptibility** | **χ** | SI | Mineralogical fingerprint; identifies igneous/basement bodies. |
| **6** | **Thermal Conductivity** | **k** | W/m·K | Thermodynamic flux control; dictates heat flow and maturation. |
| **7** | **Pore Pressure** | **P** | Pa | **The Dynamic Driver.** Governs flow, effective stress, and rock failure. |
| **8** | **Temperature** | **T** | K | **The Metabolic Driver.** Governs reaction kinetics and phase state. |
| **9** | **Porosity** | **φ** | 0–1 | **The Void Basis.** Normalized volume for all fluid and storage logic. |

---

### CONSTITUTIONAL LOCK: DERIVED EXCLUSIONS

To prevent **LLM Drift** and maintain the thermodynamic integrity of the Large Earth Model, the following variables are strictly **EXCLUDED** from the Physics-9 State Vector. They must be treated as **Constitutive Responses** computed via governed kernels:

- **Permeability ($k_{perm}$)**: An emergent transport property.
- **Mechanical Moduli ($K, \mu, E, v$)**: Elastic responses derivable from ($\rho, V_p, V_s$).
- **Heat Capacity ($C_p$)**: A mineralogical/fluid property.

Inclusion of these in the base schema is a violation of **F2 (Truth)** and **F8 (Genius)**.

### 2. Physical Completeness

From these 9, any physics solver can compute:

- **Acoustic Impedance**: (Vp * ρ)
- **Poisson's Ratio**: f(Vp, Vs)
- **Fluid Saturation**: f(ρₑ, φ) via Archie/Simandoux
- **Effective Stress**: (σ - P)
- **Heat Flux**: (-k * ∇T)

### 3. AGI/LEM Foundation

For a Large Earth Model to achieve "Active Inference," it must understand **Cause and Effect**.

- **Cause**: Change in P or T.
- **Effect**: Changes in Vp, Vs, ρ, and ρₑ (D-fields).

The `PHYSICS_9` vector is the only basis that supports this causal chain natively.

---

## SEAL

DITEMPA BUKAN DIBERI. This is the official physics anchor for Physics9 v1.0.0.

999_SEAL.
