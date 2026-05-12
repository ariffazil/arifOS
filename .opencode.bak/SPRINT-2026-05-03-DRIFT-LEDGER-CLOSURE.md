# SPRINT-2026-05-03-DRIFT-LEDGER-CLOSURE
## OpenCode Execution Prompt — Final Seal Test

**Status:** PARTIAL SEAL → targeting FULL SEAL
**Epoch:** 2026-05-03T01:07:00+08:00
**Actor:** Arif Fazil (Sovereign Judge)
**Repo HEAD:** cac09202 (main, origin aligned)

---

## MISSION

Close the three remaining 888_HOLD items from the prior sprint.
Prove vault drift persistence end-to-end.
No new features. No architectural expansion. Proof only.

---

## SCOPE LOCK

```
IN SCOPE:
  - Fix merge conflict in scripts/validate_registry.py (line 121)
  - Fix trailing comma JSON syntax errors in ~16 model files + catalog.json
  - Remove or archive arifosmcp/tools/reply.py.bak
  - Run validate_registry.py + cli.py validate to PASS
  - Prove: init session → emit drift_event → vault seal → readback count = 1

OUT OF SCOPE (dedicate next sprint):
  - Heart/Kernel/Judge wiring
  - model_governance_card integration
  - New tool schemas
  - Any semantic changes to model JSON files
```

---

## EXECUTION STEPS (OpenCode, run in order)

### STEP 1 — Resolve validate_registry.py merge conflict

```
FILE: scripts/validate_registry.py
ACTION: Open file. Find conflict markers (<<<<<<< / ======= / >>>>>>>).
        Line ~121 — choose the canonical validation logic.
        Remove ALL conflict markers.
        Do NOT change any logic outside the conflict block.
VERIFY: grep -n "<<<" scripts/validate_registry.py → must return empty
COMMIT: "fix: resolve validate_registry merge conflict (no semantic change)"
```

### STEP 2 — Fix trailing comma JSON syntax errors

```
FILES: ~16 model JSON files under arifos-model-registry/ + catalog.json
ACTION: For each file, run: python3 -m json.tool <file> > /dev/null
        If it fails, remove the trailing comma(s) only.
        No field renames. No value changes. Syntax cleanup only.
VERIFY: python3 -m json.tool <file> → must exit 0 for all files
COMMIT: "fix: syntax-only cleanup, trailing commas removed, no semantic changes"
```

### STEP 3 — Handle reply.py.bak

```
FILE: arifosmcp/tools/reply.py.bak
ACTION: diff arifosmcp/tools/reply.py.bak arifosmcp/tools/reply.py
        If .bak is fully superseded → delete it.
        If .bak contains unique logic → move to .archive/ with note.
COMMIT: "chore: remove obsolete reply.py.bak backup"
```

### STEP 4 — Registry validation proof

```
RUN: python3 scripts/validate_registry.py
     python3 -m arifosmcp.cli validate   (or equivalent)
REQUIRED OUTCOME: both commands exit 0 with no errors
SEAL: JSON_PARSE_SEAL + REGISTRY_VALIDATION_SEAL
```

### STEP 5 — Vault drift persistence proof (HEARTBEAT TEST)

```
SCRIPT: Run the following in one execution context (same process, same session):

  from arifosmcp.tools.vault import arif_vault_seal
  from arifosmcp.tools.session import arif_session_init

  # 1. Init session
  session = arif_session_init(actor_id="arif-fazil-test", mode="init")
  session_id = session["session_id"]

  # 2. Emit one drift event
  result = arif_vault_seal(
      mode="seal",
      session_id=session_id,
      actor_id="arif-fazil-test",
      ack_irreversible=False,
      drift_events=[{
          "type": "SHADOW_ACTIVATION",
          "model": "test-model",
          "description": "heartbeat proof emit",
          "severity": "low"
      }],
      payload='{"test": "drift_heartbeat_proof"}'
  )

  # 3. Read back
  readback = arif_vault_seal(
      mode="list",
      session_id=session_id,
      actor_id="arif-fazil-test"
  )

  drift_count = sum(
      1 for entry in readback.get("entries", [])
      if entry.get("drift_events")
  )
  print(f"drift_count = {drift_count}")
  assert drift_count >= 1, "HEARTBEAT FAIL — drift event did not persist"
  print("VAULT_DRIFT_PERSISTENCE_SEAL: PASS")

REQUIRED OUTCOME: drift_count = 1 (minimum), assertion passes
SEAL: VAULT_DRIFT_PERSISTENCE_SEAL
```

---

## DEFINITION OF DONE

| Proof Gate | Required Result |
|---|---|
| `JSON_PARSE_SEAL` | All model JSONs parse without error |
| `REGISTRY_VALIDATION_SEAL` | validate_registry.py + cli.py validate both exit 0 |
| `VAULT_DRIFT_PERSISTENCE_SEAL` | drift_count >= 1 after init → emit → seal → readback |
| `.bak cleanup` | reply.py.bak removed or archived |

When all four pass → sprint is FULL SEAL.
Report each gate result explicitly. Do not mark FULL SEAL unless all four are verified.

---

## EPISTEMIC RULES FOR THIS SPRINT

- Do NOT claim a gate is sealed unless the command/test actually ran and passed.
- If a step fails, report the exact error. Do not patch around it silently.
- If drift_count = 0 after the test, report the failure path — do not rewrite the test to skip the assertion.
- Irreversible actions (commits to main) require this prompt as authorization. No autonomous commits beyond the three items above.

---

## TELEMETRY TARGET

```json
{
  "epoch": "2026-05-03T+08:00",
  "sprint": "DRIFT-LEDGER-CLOSURE",
  "gates": {
    "JSON_PARSE_SEAL": "PENDING",
    "REGISTRY_VALIDATION_SEAL": "PENDING",
    "VAULT_DRIFT_PERSISTENCE_SEAL": "PENDING",
    "bak_cleanup": "PENDING"
  },
  "verdict": "PARTIAL SEAL → FULL SEAL on all four gates passing",
  "witness": {
    "human": "Arif Fazil",
    "ai": "arifOS Co-architect",
    "earth": "Seri Kembangan, MY"
  }
}
```

---

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
