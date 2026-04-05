#!/usr/bin/env python3
import sys, json, os
sys.path.insert(0, '/root/arifOS/geox')
from arifos.geox.lasi_interpreter import interpret_las
import lasio

las = lasio.read('/root/arifOS/sites/aaa-mcp-landing/geox/q15_dak_petro.las')
derived, report = interpret_las(las)

every = 5
sampled = {}
for name, arr in derived.items():
    vals = []
    for v in arr[::every]:
        if v is None:
            vals.append(None)
        else:
            try:
                vals.append(round(float(v), 6))
            except Exception:
                vals.append(None)
    sampled[name] = vals

zones_out = []
for z in report.zones:
    zones_out.append({
        'name': z.name,
        'md_min': z.md_min,
        'md_max': z.md_max,
        'phi_mean': z.phi_mean,
        'sw_mean': z.sw_mean,
        'pay_samples': z.pay_samples,
        'gas_samples': z.gas_samples,
        'wet': z.wet,
    })

meta = {
    'well': report.well_name,
    'field': report.field_name,
    'md_min': report.md_min,
    'md_max': report.md_max,
    'n_raw': report.n_points,
    'n_sampled': sampled['DEPT'].__len__(),
    'confidence': report.confidence,
    'epistemic': report.epistemic_level,
    'hold_triggers': report.hold_triggers,
    'zones': zones_out,
    'phi_cutoff': 0.10,
    'sw_cutoff': 0.60,
    'vsh_cutoff': 0.40,
    'matrix_density': 2.65,
    'rw': 0.02,
}

out_path = '/root/arifOS/sites/aaa-mcp-landing/geox/geox_data.json'
with open(out_path, 'w') as fh:
    json.dump({'meta': meta, 'data': sampled}, fh)

sz = os.path.getsize(out_path)
n_pt = sampled['DEPT'].__len__()
print(f'Written: {sz//1024} KB, {n_pt} depth points')
for z in zones_out:
    tag = 'WET' if z['wet'] else 'PAY'
    print(f"  {z['name']}: phi={z['phi_mean']:.3f} sw={z['sw_mean']:.3f} pay={z['pay_samples']} gas={z['gas_samples']} {tag}")
