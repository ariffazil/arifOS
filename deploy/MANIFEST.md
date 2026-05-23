# arifOS Machine Kernel — Stage D Deploy Manifest
# SEAL: seal-20260523T125400-DITEMPA-BUKAN-DIBERI-999-SEAL
| arifosd.py | 1222 | f57217632e56af929ed4d2056821cb9d |
| contract_schemas.py | 600 | b43d9c44c239854a30675666e0266b56 |
| adapters.py | 284 | 6799b90d9b10cd647ec80e56cdc78756 |
| arifOS_emulator.py | 222 | 73a9f15bedcc55978f7e8c4e99927afb |
| arifos.service | 50 | 6d66e1f165f428adcec5d45f7c9bc743 |
| arifos.socket | 16 | 16ecf96e6474e6c5a9a075169b3f5a21 |
| arifosd.yaml | 222 | 87de03ed24a14efae24943c8e540393a |
| arif_run.py | 238 | dddcc2a52b2b8582dea368df32650bd2 |
| arif_exec.py | 140 | c4789061ae0b99302a5c8c844b7af4b4 |
| arif_sudo.py | 138 | 034e07f71cb6d94ff01cb30dddc2bf1e |
| arif-systemctl.py | 183 | 3bc0fd459c9cf2f8276b634ecb55a82a |
| arifos_install.sh | 534 | 077c80c7c2bba8c29d0a20d40743065c |

---

## Consolidation Note (2026-05-23)

**scripts/ → commands/:** Under 444 ROUT, the `scripts/` directory (41 files) 
was consolidated into `commands/` as the canonical entrypoint layer.

Command reference update:
- `arif_run.py` → `/workspace/arifOS/commands/arif_run.py`
- `arif_exec.py` → `/workspace/arifOS/commands/arif_exec.py`
- `arif_sudo.py` → `/workspace/arifOS/commands/arif_sudo.py`
- `arif-systemctl.py` → `/workspace/arifOS/commands/arif-systemctl.py`
- All other scripts → `commands/scripts_deploy/` or `commands/scripts_archive/`

deploy/MANIFEST.md SEAL remains valid.
