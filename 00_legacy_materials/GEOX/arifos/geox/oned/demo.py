"""
GEOX 1D Demo — Joint inversion toy example.
DITEMPA BUKAN DIBERI
"""

"""
GEOX 1D Demo — Joint inversion toy example.
Run: cd /root/GEOX && python -m arifos.geox.oned.demo
DITEMPA BUKAN DIBERI
"""

import numpy as np
from arifos.geox.oned.canon9_profile import Canon9Profile, DepthSample
from arifos.geox.oned.synthetic import SyntheticSeismic, Wavelet
from arifos.geox.oned.inversion import JointInversion1D


def create_synthetic_well(
    n_samples: int = 100,
    dz: float = 1.0,
    gas_sand_depth: tuple[float, float] = (30, 50),
) -> Canon9Profile:
    """
    Create a synthetic well with:
    - Shale above
    - Gas sand in middle
    - Shale below
    """
    samples = []

    for i in range(n_samples):
        depth = i * dz

        # Lithology boundaries
        if gas_sand_depth[0] <= depth <= gas_sand_depth[1]:
            # Gas sand
            phi = 0.25
            sw = 0.2  # High gas saturation
            vp = 3200
            vs = 1800
            rho = 2200
        else:
            # Shale
            phi = 0.15
            sw = 1.0  # Fully wet
            vp = 2800
            vs = 1200
            rho = 2400

        sample = DepthSample(
            depth=depth,
            density=rho,
            vp=vp,
            vs=vs,
            resistivity=10.0 if sw > 0.5 else 100.0,  # High resistivity in gas
            magnetic_suscept=0.0,
            thermal_conduct=2.5,
            pressure=depth * 1e4,  # Hydrostatic
            temperature=300 + depth * 0.03,  # Geothermal gradient
            porosity=phi,
            sw=sw,
            salinity=35000,
            sources={"synthetic": "demo well"},
        )
        samples.append(sample)

    return Canon9Profile(well_id="DEMO-001", samples=samples)


def main():
    print("=" * 60)
    print("GEOX 1D Joint Inversion Demo")
    print("DITEMPA BUKAN DIBERI")
    print("=" * 60)

    # 1. Create synthetic true model
    print("\n[1] Creating synthetic true model...")
    true_profile = create_synthetic_well()
    print(f"    Well: {true_profile.well_id}")
    print(f"    Depths: {true_profile.samples[0].depth} to {true_profile.samples[-1].depth} m")
    print(f"    Telemetry: {true_profile.to_telemetry()}")

    # 2. Generate synthetic seismic
    print("\n[2] Generating synthetic seismic...")
    wavelet = Wavelet.ricker(fdom=30, dt=0.004)
    synthetic_gen = SyntheticSeismic(wavelet=wavelet)
    synthetic_cmp = synthetic_gen.generate(true_profile)
    print(f"    Wavelet: Ricker {wavelet.fdom} Hz")
    print(f"    Angles: {synthetic_cmp.angles}")
    print(f"    Time range: {synthetic_cmp.time[0]:.3f} to {synthetic_cmp.time[-1]:.3f} s")

    # 3. Extract observed logs
    print("\n[3] Extracting observed logs...")
    obs_logs = {
        "vp": true_profile.get_property("vp"),
        "vs": true_profile.get_property("vs"),
        "density": true_profile.get_property("density"),
        "resistivity": true_profile.get_property("resistivity"),
    }
    print(f"    Vp range: {obs_logs['vp'].min():.0f} to {obs_logs['vp'].max():.0f} m/s")
    print(
        f"    Density range: {obs_logs['density'].min():.0f} to {obs_logs['density'].max():.0f} kg/m³"
    )

    # 4. Create prior (wrong guess)
    print("\n[4] Creating prior model (initial guess)...")
    prior_samples = []
    for s in true_profile.samples:
        # Start with wrong assumptions
        prior_samples.append(
            DepthSample(
                depth=s.depth,
                density=2300,  # Constant
                vp=3000,  # Constant
                vs=1500,  # Constant
                resistivity=20.0,  # Constant
                magnetic_suscept=0.0,
                thermal_conduct=2.5,
                pressure=s.pressure,
                temperature=s.temperature,
                porosity=0.20,  # Wrong average
                sw=0.8,  # Assume mostly water
                salinity=35000,
                sources={"prior": "uniform guess"},
            )
        )

    prior_profile = Canon9Profile(
        well_id="DEMO-001-PRIOR",
        samples=prior_samples,
        tdr_depths=true_profile.tdr_depths[:],
        tdr_times=true_profile.tdr_times[:],
    )
    print(f"    Prior φ: {prior_profile.get_property('porosity').mean():.3f}")
    print(f"    Prior Sw: {prior_profile.get_property('sw').mean():.3f}")

    # 5. Run joint inversion
    print("\n[5] Running joint inversion...")
    inverter = JointInversion1D(method="gradient")
    result = inverter.invert(
        prior_profile=prior_profile,
        obs_seismic=synthetic_cmp,
        obs_logs=obs_logs,
        max_iter=50,
        step_size=0.05,
    )

    print(f"    Converged: {result.converged}")
    print(f"    Iterations: {result.iterations}")
    print(f"    Final misfit: {result.misfit_history[-1]:.4f}")

    # 6. Compare results
    print("\n[6] Results comparison...")
    true_phi = true_profile.get_property("porosity")
    inv_phi = result.profile.get_property("porosity")
    phi_error = np.abs(true_phi - inv_phi).mean()

    true_sw = true_profile.get_property("sw")
    inv_sw = result.profile.get_property("sw")
    sw_error = np.abs(true_sw - inv_sw).mean()

    print(f"    Porosity MAE: {phi_error:.4f}")
    print(f"    Saturation MAE: {sw_error:.4f}")

    # 7. Identify gas sand
    print("\n[7] Gas sand identification...")
    gas_zone = (result.profile.depths >= 30) & (result.profile.depths <= 50)
    avg_sw_gas = inv_sw[gas_zone].mean()
    print(f"    Average Sw in gas zone: {avg_sw_gas:.3f}")
    print(f"    Gas detected: {avg_sw_gas < 0.5}")

    print("\n" + "=" * 60)
    print("Demo complete. 1D joint inversion works.")
    print("DITEMPA BUKAN DIBERI — 999 SEAL ALIVE")
    print("=" * 60)


if __name__ == "__main__":
    main()
