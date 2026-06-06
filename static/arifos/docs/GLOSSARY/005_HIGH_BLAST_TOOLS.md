# 005 — Security boundary for high-blast tools (Wajib #10)

> Concrete naming: shell, filesystem, database, email, browser, deploy,
> ledger write. "0 ungated high-risk tools."

## High-blast tool inventory (audit target)

| Tool / capability          | Blast radius                       | Current gating          | Target gating                    |
| -------------------------- | ---------------------------------- | ----------------------- | -------------------------------- |
| arif_forge_execute         | deploy / build                     | F1+F11+F13 (good)       | + reversibility score in payload |
| arif_vault_seal            | ledger write                       | F1+F11+F13              | + envelope upgrade (LEGACY_WRAP) |
| shell_* (if any)           | arbitrary code exec                 | NOT EXPOSED              | KEEP NOT EXPOSED                 |
| fs_write_* (if any)        | filesystem mutation                 | NOT EXPOSED              | KEEP NOT EXPOSED                 |
| db_write_* (if any)        | data corruption                     | NOT EXPOSED              | KEEP NOT EXPOSED                 |
| email_send_* (if any)      | external comms                      | NOT EXPOSED              | KEEP NOT EXPOSED                 |
| browser_* (if any)         | exfiltration                        | NOT EXPOSED              | sandboxed read-only              |
| deploy_* (A-FORGE)         | production state                    | 4-layer gate             | + post-deploy attestation        |
| claims_seal (GEOX)         | canonical promotion                | LEGACY_WRAP bug         | FederationEnvelope upgrade       |
| Geox export tools          | data exfiltration                   | path-bound               | + DLP-style redaction            |

## Target: 0 ungated high-risk tools.

## Per-MCP-server threat model (template)

```
MCP server: <organ>
Tools: <list>
Attack surface:
  - prompt injection: <handled by F12>
  - data exfiltration: <handled by evidence_contract>
  - mutation: <handled by reversibility score>
  - rollback: <handled by L01>
  - impersonation: <handled by F11 AUDIT>
Threat model last updated: 2026-06-06
Tool attestation: 100%
Red-team coverage: <target 95%>
```
