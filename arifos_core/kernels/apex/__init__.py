"""
arifOS APEX Kernel — Psi Engine (F6, F8-F12)

v47 Stage 888_compass per L1_THEORY/canon/888_compass/801_APEX_PSI_JUDGE_v46.md

Floors:
- F6: Amanah floor (per L1/888_compass/830_AMANAH_F6_v46.md)
- F8: Tri-Witness floor (per L1/888_compass/840_TRI_WITNESS_F8_v46.md)
- F9: Anti-Hantu floor (per L1/888_compass/850_ANTI_HANTU_F9_v46.md)
- F10: Symbolic Guard (per L1/888_compass/860_SYMBOLIC_GUARD_F10_v46.md)
- F11: Command Auth (per L1/888_compass/870_COMMAND_AUTH_F11_v46.md)
- F12: Injection Defense (per L1/888_compass/880_INJECTION_DEFENSE_F12_v46.md)

Psi (Ψ) responsibility:
  Final verdict authority. Audit and judge all decisions.
  Guard against injection, manipulation, false consciousness.
  Issue SEAL, PARTIAL, VOID, or 888_HOLD verdicts.

DITEMPA BUKAN DIBERI
"""

from .amanah_floor import check_amanah_f6, F6AmanahResult
from .witness_floor import check_tri_witness_f8, F8TriWitnessResult
from .anti_hantu_floor import check_anti_hantu_f9, F9AntiHantuResult
from .symbolic_guard import check_symbolic_guard_f10, F10SymbolicGuardResult
from .command_auth import check_command_auth_f11, F11CommandAuthResult
from .injection_defense import check_injection_defense_f12, F12InjectionDefenseResult

__all__ = [
    "check_amanah_f6",
    "F6AmanahResult",
    "check_tri_witness_f8",
    "F8TriWitnessResult",
    "check_anti_hantu_f9",
    "F9AntiHantuResult",
    "check_symbolic_guard_f10",
    "F10SymbolicGuardResult",
    "check_command_auth_f11",
    "F11CommandAuthResult",
    "check_injection_defense_f12",
    "F12InjectionDefenseResult",
]
