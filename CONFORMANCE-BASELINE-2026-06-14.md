# CONFORMANCE-BASELINE-2026-06-14

## Kernel State
```text
arifOS status:        ALIVE
version:              v2026.05.05-SSCT
session:              SEAL-bb05f170c0e24841
failed calls 5m:      0
active leases:        0
queued tasks:         0
verdict:              SEAL
```

## Passing Gates
| Gate | Status |
|------|--------|
| `arif_ping` | PASS |
| `arif_version_echo` | PASS |
| `arif_initialize_probe` | PASS |
| `arif_schema_echo` | PASS |
| `arif_transport_echo` | PASS |
| `arif_session_init(light)` | PASS |
| `arif_os_attest` | PASS |

## Known Residue
- **Diagnostic schema mismatch:** Tools accept varying levels of payload/envelope structures (some demand `{}`, others demand specific payloads).
- **Protocol version metadata drift:** Discrepancy between top-level and nested protocol versions.

## Current Verdict
Transport membrane is AMBER → GREEN-leaning. Kernel reachability, initialize lifecycle, schema echo, session init, vault readiness, and forge safety (dry-run only) all pass.
