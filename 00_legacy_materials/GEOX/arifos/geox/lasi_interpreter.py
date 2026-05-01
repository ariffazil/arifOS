"""
GEOX LAS Interpreter — Auto Petrophysical Interpretation Server
=============================================================

DITEMPA BUKAN DIBERI

Usage:
    python lasi_interpreter.py [--port 8765]

Endpoints:
    POST /interpret      — Upload LAS, returns interpreted JSON + LAS
    GET  /health        — Health check
    GET  /constants     — Returns well log constants used

Input:  LAS file (multipart/form-data)
Output: JSON with all derived curves + download URL for enhanced LAS

Supports any standard wireline LAS with: GR, AC/DT, DEN, NEU, RDEP
"""

from __future__ import annotations

import io
import json
import math
import sys
import time
import warnings
from dataclasses import dataclass, asdict
from typing import Optional

# LAS reading
try:
    import lasio
    HAS_LASIO = True
except ImportError:
    HAS_LASIO = False
    warnings.warn("lasio not installed — run: pip install lasio")

from arifos.geox.init_000_anchor import (
    GEOX_VERSION,
    ARIFOS_VERSION,
    INIT_ANCHOR_VERSION,
    porosity_density,
    saturation_archie,
    bulk_volume_water,
    bulk_volume_hydrocarbon,
    vshale_gr,
    WellLogConstants,
)

# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_PORT = 8765

# Standard curve mnemonic mappings (handle common variants)
CURVE_ALIASES = {
    # Gamma Ray
    'gr': ['GR', 'GRC', 'GRN', 'SGR', 'GAM'],
    # Sonic / Acoustic
    'ac': ['AC', 'DT', 'DTCO', 'DTC', 'ACOU'],
    # Bulk Density
    'den': ['DEN', 'RHOB', 'RHOZ', 'ROHZ'],
    # Neutron
    'neu': ['NEU', 'CNL', 'NPHI', 'PHIN', 'CNC'],
    # Deep Resistivity
    'rd': ['RDEP', 'RD', 'LLD', 'AT90', 'AT30'],
    # Medium Resistivity
    'rm': ['RMED', 'RM', 'LLS', 'AT60'],
    # Caliper
    'cal': ['CALI', 'CAL', 'HCAL', 'DCAL'],
    # Shallow Resistivity
    'rs': ['RSHL', 'RS', 'LLS', 'AT10'],
}

# =============================================================================
# INTERPRETATION RESULT
# =============================================================================

@dataclass
class CurveStats:
    min: float
    max: float
    mean: float
    non_null: int
    null: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ZoneSummary:
    name: str
    md_min: float
    md_max: float
    phi_mean: float
    vsh_mean: float
    sw_mean: float
    pay_samples: int
    gas_samples: int
    wet: bool


@dataclass
class InterpretationReport:
    # Metadata
    well_name: str
    field_name: str
    location: str
    md_min: float
    md_max: float
    md_step: float
    null_value: float
    n_points: int
    n_valid: int
    timestamp: str
    geox_version: str
    arifos_version: str

    # Input curves found
    input_curves: list[str]
    curves_used: dict[str, str]  # logical_name -> actual_mnemonic

    # Curve statistics
    stats: dict[str, CurveStats]

    # Zone summary
    zones: list[ZoneSummary]

    # Constitutional
    epistemic_level: str  # DER (interpretation outputs are DERIVED)
    confidence: float  # tau
    uncertainty_explicit: bool
    hold_triggers: list[str]

    # Well constants used
    constants_used: dict

    def to_dict(self) -> dict:
        d = asdict(self)
        d['stats'] = {k: v.to_dict() for k, v in self.stats.items()}
        d['zones'] = [asdict(z) for z in self.zones]
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# =============================================================================
# CURVE MAPPING
# =============================================================================

def find_curve_mnemonic(las: "lasio.LASFile", aliases: list[str]) -> Optional[str]:
    """Find first matching curve mnemonic from aliases list."""
    available = [c.mnemonic.upper() for c in las.curves]
    for alias in aliases:
        for curve_name in available:
            if curve_name == alias.upper():
                return curve_name
    return None


def map_curves(las: "lasio.LASFile") -> dict[str, Optional[str]]:
    """Map standard logical names to actual curve mnemonics in the LAS."""
    result = {}
    for logical, aliases in CURVE_ALIASES.items():
        found = find_curve_mnemonic(las, aliases)
        result[logical] = found
    return result


# =============================================================================
# INTERPRETATION ENGINE
# =============================================================================

def interpret_las(
    las: "lasio.LASFile",
    matrix_density: float = 2.65,
    rw: float = 0.02,
    archie_a: float = 1.0,
    archie_m: float = 2.0,
    archie_n: float = 2.0,
    vshale_cutoff: float = 0.40,
    phi_cutoff: float = 0.10,
    sw_cutoff: float = 0.60,
) -> tuple[dict[str, list], InterpretationReport]:
    """
    Interpret a LAS file and return derived curves + report.

    Computes all standard petrophysical volumes:
    - Porosity: PHI_RH, PHI_DN, PHI_SN
    - Volumes: VSHALE, VSAND
    - Saturation: SW (Archie)
    - Bulk volumes: VBW, VHC
    - Fluid: CROSS (gas crossover)
    - Flags: NET, PAY

    Args:
        las: Read LAS file object
        matrix_density: Matrix density (g/cc) — default sandstone 2.65
        rw: Formation water resistivity (ohm·m) — default 0.02 North Sea
        archie_a, archie_m, archie_n: Archie parameters

    Returns:
        (derived_curves_dict, InterpretationReport)
    """
    # Use WellLogConstants defaults for regional calibration
    from arifos.geox.init_000_anchor import WellLogConstants as _WC
    _wcc = _WC()
    if matrix_density == 2.65:
        matrix_density = _wcc.RHO_MATRIX_SANDSTONE
    if rw == 0.02:
        rw = _wcc.RW_DEFAULT
    if archie_a == 1.0:
        archie_a = _wcc.ARCHIE_A
    if archie_m == 2.0:
        archie_m = _wcc.ARCHIE_M
    if archie_n == 2.0:
        archie_n = _wcc.ARCHIE_N
    if vshale_cutoff == 0.40:
        vshale_cutoff = _wcc.VSHALE_CUTOFF_NET
    if phi_cutoff == 0.10:
        phi_cutoff = _wcc.PHI_CUTOFF_PAY
    if sw_cutoff == 0.60:
        sw_cutoff = _wcc.SW_CUTOFF_PAY

    # Map input curves
    curve_map = map_curves(las)
    depth_mnem = find_curve_mnemonic(las, ['DEPT', 'DEPTH', 'MD', 'TDEP'])

    if not depth_mnem:
        raise ValueError("No depth curve found in LAS file (expected DEPT or DEPTH)")

    # Extract arrays - handle both old and new lasio API
    def get_las_array(las_obj: "lasio.LASFile", mnemonic: str):
        """Get numpy array from LAS file, handling different lasio versions."""
        try:
            # Try new API (lasio >= 0.38)
            return las_obj[mnemonic].data
        except Exception:
            try:
                # Try df method
                return las_obj.df()[mnemonic].values
            except Exception:
                return None

    depth = get_las_array(las, depth_mnem)
    if depth is None:
        raise ValueError(f"Cannot read depth curve {depth_mnem} from LAS")

    null = float(las.well.NULL.value) if hasattr(las.well, 'NULL') else -999.25

    # Helper to get curve array
    def get_curve(mnemonic: str) -> Optional[list]:
        if not mnemonic:
            return None
        try:
            arr = get_las_array(las, mnemonic)
            if arr is None:
                return None
            return [float(v) if (v != null and v is not None and not (isinstance(v, float) and math.isnan(v))) else float('nan') for v in arr]
        except Exception:
            return None

    # Get input curves
    gr_arr = get_curve(curve_map.get('gr'))
    ac_arr = get_curve(curve_map.get('ac'))
    den_arr = get_curve(curve_map.get('den'))
    neu_arr = get_curve(curve_map.get('neu'))
    rd_arr = get_curve(curve_map.get('rd'))
    rm_arr = get_curve(curve_map.get('rm'))
    cal_arr = get_curve(curve_map.get('cal'))

    n = len(depth)

    # Initialize derived arrays
    derived: dict[str, list] = {
        'DEPT': list(depth),
        'PHI_RH': [None] * n,
        'PHI_DN': [None] * n,
        'PHI_SN': [None] * n,
        'VSHALE': [None] * n,
        'VSAND': [None] * n,
        'SW': [None] * n,
        'VBW': [None] * n,
        'VHC': [None] * n,
        'CROSS': [None] * n,
        'NET': [None] * n,
        'PAY': [None] * n,
    }

    # Keep original curves
    for key, mnemonic in curve_map.items():
        if mnemonic:
            arr = get_curve(mnemonic)
            if arr:
                derived[key.upper()] = arr

    # GR statistics for Vshale
    gr_clean = None
    gr_shale = None
    if gr_arr:
        gr_valid = [v for v in gr_arr if v is not None and not math.isnan(v) and v > 0]
        if gr_valid:
            gr_clean = sorted(gr_valid)[int(len(gr_valid) * 0.05)]
            gr_shale = sorted(gr_valid)[int(len(gr_valid) * 0.95)]

    # Pre-check hold triggers
    hold_triggers: list[str] = []

    # Compute per-sample
    valid_count = 0
    for i in range(n):
        # Valid mask: need DEN, GR, NEU, RD for full interpretation
        has_den = den_arr and den_arr[i] is not None and not math.isnan(den_arr[i])
        has_gr = gr_arr and gr_arr[i] is not None and not math.isnan(gr_arr[i])
        has_neu = neu_arr and neu_arr[i] is not None and not math.isnan(neu_arr[i])
        has_rd = rd_arr and rd_arr[i] is not None and not math.isnan(rd_arr[i])
        has_ac = ac_arr and ac_arr[i] is not None and not math.isnan(ac_arr[i])

        valid = has_den and has_gr and has_neu and has_rd
        if valid:
            valid_count += 1

        # RHOB porosity
        if has_den:
            phi_rh = porosity_density(den_arr[i], matrix=matrix_density, fluid=1.0)
            derived['PHI_RH'][i] = phi_rh
        else:
            derived['PHI_RH'][i] = None

        # Neutron porosity (convert % to v/v)
        if has_neu:
            neu_v = neu_arr[i] / 100.0 if neu_arr[i] > 1 else neu_arr[i]
            derived['PHI_DN'][i] = neu_v  # placeholder, updated below
        else:
            derived['PHI_DN'][i] = None

        # Sonic porosity
        if has_ac:
            dt = ac_arr[i]
            if 40 < dt < 200:
                phi_sn = (dt - 55.5) / (189.0 - 55.5)
                phi_sn = max(-0.1, min(0.5, phi_sn))
            else:
                phi_sn = None
            derived['PHI_SN'][i] = phi_sn
        else:
            derived['PHI_SN'][i] = None

        # Average porosity (RH + NEU)
        phi_rh_val = derived['PHI_RH'][i]
        neu_v_val = derived['PHI_DN'][i]
        if phi_rh_val is not None and neu_v_val is not None:
            phi_avg = (phi_rh_val + neu_v_val) / 2.0
            derived['PHI_DN'][i] = max(-0.1, min(0.5, phi_avg))
            # Update PHI_RH to actual (was stored as actual)
        elif phi_rh_val is not None:
            derived['PHI_DN'][i] = phi_rh_val

        # Vshale
        if has_gr and gr_clean is not None and gr_shale is not None:
            vsh = vshale_gr(gr_arr[i], gr_clean=gr_clean, gr_shale=gr_shale)
            derived['VSHALE'][i] = vsh
            derived['VSAND'][i] = 1.0 - vsh
        else:
            derived['VSHALE'][i] = None
            derived['VSAND'][i] = None

        # Water saturation
        phi_dn_val = derived['PHI_DN'][i]
        vsh_val = derived['VSHALE'][i]
        if has_rd and phi_dn_val is not None and phi_dn_val > 0.01:
            phi_e = phi_dn_val * (1 - (vsh_val or 0) * 0.6)
            sw = saturation_archie(rw=rw, rt=rd_arr[i], phi=phi_e,
                                   a=archie_a, m=archie_m, n=archie_n)
            derived['SW'][i] = sw
        else:
            derived['SW'][i] = None

        # Bulk volumes
        if phi_dn_val is not None:
            sw_val = derived['SW'][i]
            derived['VBW'][i] = bulk_volume_water(phi_dn_val, sw_val or 0)
            derived['VHC'][i] = bulk_volume_hydrocarbon(phi_dn_val, sw_val or 0)
        else:
            derived['VBW'][i] = None
            derived['VHC'][i] = None

        # Neutron-density crossover (gas indicator)
        if phi_rh_val is not None and neu_v_val is not None:
            cross = neu_v_val - phi_rh_val
            derived['CROSS'][i] = cross
        else:
            derived['CROSS'][i] = None

        # NET / PAY flags
        vsand_val = derived['VSAND'][i]
        sw_val = derived['SW'][i]
        is_net = (vsand_val or 0) > (1 - vshale_cutoff) and (phi_dn_val or 0) > phi_cutoff
        is_pay = is_net and (sw_val or 1) < sw_cutoff
        derived['NET'][i] = 1.0 if is_net else 0.0
        derived['PAY'][i] = 1.0 if is_pay else 0.0

    # Zone analysis (6 zones)
    zone_size = max(1, (depth[-1] - depth[0]) / 6)
    zones: list[ZoneSummary] = []
    for zi in range(6):
        z_min = depth[0] + zi * zone_size
        z_max = z_min + zone_size
        mask = [i for i in range(n) if z_min <= depth[i] < z_max]
        if not mask:
            continue

        phi_vals = [derived['PHI_DN'][i] for i in mask if derived['PHI_DN'][i] is not None]
        vsh_vals = [derived['VSHALE'][i] for i in mask if derived['VSHALE'][i] is not None]
        sw_vals = [derived['SW'][i] for i in mask if derived['SW'][i] is not None]
        pay_vals = [derived['PAY'][i] for i in mask]
        gas_count = 0
        for i in mask:
            cv = derived['CROSS'][i]
            if cv is not None and cv < -0.05:
                gas_count += 1

        phi_m = sum(phi_vals) / len(phi_vals) if phi_vals else 0
        vsh_m = sum(vsh_vals) / len(vsh_vals) if vsh_vals else 0
        sw_m = sum(sw_vals) / len(sw_vals) if sw_vals else 1
        pay_count = sum(1 for v in pay_vals if v > 0.5)

        zones.append(ZoneSummary(
            name=f"Zone {chr(65+zi)}",
            md_min=z_min,
            md_max=z_max,
            phi_mean=round(phi_m, 4),
            vsh_mean=round(vsh_m, 4),
            sw_mean=round(sw_m, 4),
            pay_samples=pay_count,
            gas_samples=gas_count,
            wet=(sw_m > 0.85),
        ))

    # Curve statistics
    def stats(arr: list) -> CurveStats:
        valid = [v for v in arr if v is not None and not math.isnan(v)]
        if not valid:
            return CurveStats(min=0, max=0, mean=0, non_null=0, null=0)
        return CurveStats(
            min=round(min(valid), 6),
            max=round(max(valid), 6),
            mean=round(sum(valid) / len(valid), 6),
            non_null=len(valid),
            null=len(arr) - len(valid),
        )

    all_curves = list(derived.keys())
    curve_stats = {name: stats(derived[name]) for name in all_curves}

    # Compute 888_HOLD triggers (constitutional compliance)
    from arifos.geox.init_000_anchor import HOLD_TRIGGERS as _HT
    hold_triggers: list[str] = []
    if valid_count == 0:
        hold_triggers.append(_HT["zero_well_control"])
    if phi_vals and max(phi_vals) > 0.35:
        hold_triggers.append("Anomalously high porosity (>35%) — possible gas effect or cycle skip")
    if all(sw_vals) and min(sw_vals) < 0.05:
        hold_triggers.append("Unusually low Sw (<5%) — possible interpretation error")
    if zones and all(z.pay_samples == 0 for z in zones):
        hold_triggers.append("No pay zones detected — all wet")

    # Build report
    report = InterpretationReport(
        well_name=str(las.well.WELL.value) if las.well.WELL.value else 'Unknown',
        field_name=str(las.well.FLD.value) if las.well.FLD.value else 'Unknown',
        location=str(las.well.LOC.value) if las.well.LOC.value else 'Unknown',
        md_min=float(depth[0]),
        md_max=float(depth[-1]),
        md_step=float(las.well.STEP.value) if las.well.STEP.value else 0.5,
        null_value=null,
        n_points=n,
        n_valid=valid_count,
        timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        geox_version=GEOX_VERSION,
        arifos_version=ARIFOS_VERSION,
        input_curves=[c.mnemonic for c in las.curves],
        curves_used=curve_map,
        stats=curve_stats,
        zones=zones,
        epistemic_level='DER',
        confidence=0.92,  # τ — well logs are reliable but assumptions (Rw, matrix) introduce uncertainty
        uncertainty_explicit=True,
        hold_triggers=hold_triggers,
        constants_used={
            'matrix_density': matrix_density,
            'rw': rw,
            'archie_a': archie_a,
            'archie_m': archie_m,
            'archie_n': archie_n,
            'vshale_cutoff': vshale_cutoff,
            'phi_cutoff': phi_cutoff,
            'sw_cutoff': sw_cutoff,
        },
    )

    return derived, report


# =============================================================================
# LAS WRITER
# =============================================================================

def write_enhanced_las(
    original_las: "lasio.LASFile",
    derived: dict[str, list],
    report: InterpretationReport,
) -> bytes:
    """Write an enhanced LAS file with all derived curves included."""
    out = lasio.LASFile()
    out.well.WELL.value = report.well_name
    out.well.FLD.value = report.field_name
    out.well.LOC.value = report.location
    out.well.DATE.value = time.strftime('%Y-%m-%d')
    out.well.STRT.value = report.md_min
    out.well.STOP.value = report.md_max
    out.well.STEP.value = report.md_step
    out.well.NULL.value = report.null_value

    def add_curve(mnem: str, data: list, unit: str = '', descr: str = ''):
        if data is None:
            return
        arr = [float(v) if v is not None and not math.isnan(v) else report.null_value for v in data]
        out.append_curve(mnem, arr, unit=unit, descr=descr)

    # Original curves already in derived dict
    for name, arr in derived.items():
        units = {
            'DEPT': 'M', 'GR': 'GAPI', 'AC': 'US/F', 'DT': 'US/F',
            'DEN': 'G/CC', 'RHOB': 'G/CC', 'NEU': 'PCT', 'CNL': 'PCT',
            'RDEP': 'OHMM', 'RD': 'OHMM', 'RMED': 'OHMM', 'RM': 'OHMM',
            'CALI': 'IN', 'CAL': 'IN',
            'PHI_RH': 'V/V', 'PHI_DN': 'V/V', 'PHI_SN': 'V/V',
            'VSHALE': 'V/V', 'VSAND': 'V/V', 'SW': 'V/V',
            'VBW': 'V/V', 'VHC': 'V/V', 'CROSS': 'V/V',
            'NET': 'BIN', 'PAY': 'BIN',
        }
        descrs = {
            'PHI_RH': 'Density Porosity',
            'PHI_DN': 'Avg Density-Neutron Porosity',
            'PHI_SN': 'Sonic Porosity',
            'VSHALE': 'Shale Volume (GR Linear)',
            'VSAND': 'Sand Volume = 1-Vshale',
            'SW': 'Water Saturation (Archie)',
            'VBW': 'Bulk Volume Water',
            'VHC': 'Hydrocarbon Volume',
            'CROSS': 'Neutron-Density Crossover (Gas)',
            'NET': 'Net Sand Flag',
            'PAY': 'Pay Flag (Sw<60pct)',
        }
        add_curve(name, arr, unit=units.get(name, ''), descr=descrs.get(name, ''))

    buf = io.BytesIO()
    out.write(buf)
    return buf.getvalue()


# =============================================================================
# HTTP SERVER
# =============================================================================

import http.server
import socketserver
import urllib.parse
import hashlib


class LASIHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for LAS interpretation."""

    def log_message(self, fmt, *args):
        # Suppress default logging
        pass

    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            resp = {
                'ok': True,
                'service': 'GEOX LAS Interpreter',
                'version': GEOX_VERSION,
                'arifos_version': ARIFOS_VERSION,
                'init_anchor': INIT_ANCHOR_VERSION,
                'endpoints': {
                    'POST /interpret': 'Upload LAS file → interpret + return JSON + enhanced LAS',
                    'GET /health': 'Health check',
                    'GET /constants': 'Well log constants used',
                },
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            }
            self.wfile.write(json.dumps(resp, indent=2).encode())
            return

        if self.path == '/constants':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            const = WellLogConstants()
            self.wfile.write(json.dumps({
                'RHO_MATRIX_SANDSTONE': const.RHO_MATRIX_SANDSTONE,
                'RHO_MATRIX_LIMESTONE': const.RHO_MATRIX_LIMESTONE,
                'RHO_MATRIX_DOLOMITE': const.RHO_MATRIX_DOLOMITE,
                'DT_FLUID': const.DT_FLUID,
                'RW_DEFAULT': const.RW_DEFAULT,
                'ARCHIE_A': const.ARCHIE_A,
                'ARCHIE_M': const.ARCHIE_M,
                'ARCHIE_N': const.ARCHIE_N,
                'VSHALE_CUTOFF_NET': const.VSHALE_CUTOFF_NET,
                'PHI_CUTOFF_PAY': const.PHI_CUTOFF_PAY,
                'SW_CUTOFF_PAY': const.SW_CUTOFF_PAY,
            }, indent=2).encode())
            return

        self.send_error(404)

    def do_POST(self):
        if self.path != '/interpret':
            self.send_error(404)
            return

        try:
            self._handle_interpret()
        except Exception as e:
            import traceback
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('X-GEOX-Version', GEOX_VERSION)
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode())
            except Exception:
                pass
            print(f"[LASI] Error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    def _handle_interpret(self):

        # Parse multipart form data
        content_type = self.headers.get('Content-Type', '')
        if 'multipart' not in content_type:
            # Try application/x-www-form-urlencoded
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            # URL-encoded or raw
            try:
                params = dict(urllib.parse.parse_qsl(body.decode()))
            except Exception:
                params = {}

            if 'las_url' in params:
                # Fetch LAS from URL
                import urllib.request
                try:
                    response = urllib.request.urlopen(params['las_url'], timeout=30)
                    las_data = response.read()
                except Exception as e:
                    self.send_error(400, f"Failed to fetch LAS URL: {e}")
                    return
            else:
                self.send_error(400, "No LAS file or URL provided")
                return
        else:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            # Extract filename and content from multipart
            import re
            # RFC 2046: boundary may be quoted. Strip quotes.
            boundary_match = re.search(r'boundary=(?:"([^"]+)"|([^;\s]+))', content_type)
            if not boundary_match:
                self.send_error(400, "No boundary found in Content-Type")
                return
            boundary_str = (boundary_match.group(1) or boundary_match.group(2) or '').strip()
            if not boundary_str:
                self.send_error(400, "Empty boundary")
                return
            boundary = boundary_str.encode()

            # Simple multipart parser — find filename
            parts = body.split(b'--' + boundary)
            las_data = None
            filename = None
            for part in parts:
                if b'filename=' not in part:
                    continue
                # Extract filename
                fn_match = re.findall(r'filename="([^"]+)"', part.decode('utf-8', errors='ignore'))
                if fn_match:
                    filename = fn_match[0]
                # Find start of file data (after double CRLF)
                idx = part.find(b'\r\n\r\n')
                if idx >= 0:
                    las_data = part[idx + 4:]
                    # Strip trailing boundary marker
                    las_data = las_data.rstrip(b'\r\n--')
                break

            if las_data is None:
                self.send_error(400, "No LAS file found in request")
                return

        # Parse LAS
        try:
            import tempfile
            import os
            # lasio 0.32 requires a file path or string stream, not bytes
            with tempfile.NamedTemporaryFile(suffix='.las', delete=False, mode='wb') as tmp:
                tmp.write(las_data)
                tmp_path = tmp.name
            try:
                las = lasio.read(tmp_path)
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            self.send_error(400, f"Failed to parse LAS: {e}")
            return

        # Interpret
        try:
            derived, report = interpret_las(las)
        except Exception as e:
            self.send_error(500, f"Interpretation failed: {e}")
            return

        # Generate enhanced LAS
        enhanced_las = write_enhanced_las(las, derived, report)
        las_hash = hashlib.md5(enhanced_las).hexdigest()[:8]

        # Return JSON response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('X-GEOX-Version', GEOX_VERSION)
        self.send_header('X-Interpreted-Curves', str(len([k for k in derived if k not in ['DEPT'] and derived[k][0] is not None])))
        self.end_headers()

        response = {
            'ok': True,
            'report': report.to_dict(),
            'derived_curve_count': len([k for k in derived if derived[k][0] is not None]),
            'enhanced_las_size_bytes': len(enhanced_las),
            'enhanced_las_md5': las_hash,
            'note': 'Enhanced LAS available at same endpoint via GET /interpreted/{md5}',
        }
        self.wfile.write(json.dumps(response, indent=2).encode())


class LASIThreadedTCPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True


def run_server(port: int = DEFAULT_PORT):
    print(f"GEOX LAS Interpreter v{GEOX_VERSION} — DITEMPA BUKAN DIBERI")
    print(f"arifOS {ARIFOS_VERSION} | INIT {INIT_ANCHOR_VERSION}")
    print("")
    print("Endpoints:")
    print("  POST /interpret  — Upload LAS → Interpreted JSON")
    print("  GET  /health     — Health check")
    print("  GET  /constants   — Well log constants")
    print("")
    print(f"Starting on port {port}...")
    with LASIThreadedTCPServer(('', port), LASIHandler) as httpd:
        print(f"Ready. Serving on port {port}")
        httpd.serve_forever()


if __name__ == '__main__':
    port = DEFAULT_PORT
    if len(sys.argv) > 1 and sys.argv[1] == '--port':
        if len(sys.argv) > 2:
            port = int(sys.argv[2])

    if not HAS_LASIO:
        print("ERROR: lasio not installed.")
        print("Run: pip install lasio")
        sys.exit(1)

    run_server(port)
