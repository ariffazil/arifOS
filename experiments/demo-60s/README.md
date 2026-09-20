# arifOS — 60-second governance demo

Offline, ~5 s, against this repo's kernel. No mock.

## Proves (`TRANSCRIPT.txt`)

1. An action outside the acting authority envelope is submitted.
2. The pipe returns **HOLD** at `GATE_7_ENVELOPE` ("Delegation expired or missing
   expiry"); the executor is never invoked; the artefact's bytes and sha256 are
   unchanged (separate witness process).
3. The same call, actor and target with a valid envelope returns **PASS**.
4. The executor appends one line inside `./sandbox/`, and an append-only receipt
   binds pre-state `input_hash`, post-state `result_hash` and the envelope's
   `trace_id`. The ledger verifies gap-free; rewriting a field in a copy is caught
   (`HASH_MISMATCH`).

## Does NOT prove

* **Target containment**: the pipe permitted a call targeting
  `/root/arifOS/README.md` (CONTROL B) — containment is the executor's duty, not
  the kernel's. Complete mediation is not shown.
* Anything about the live kernel `:8088` or production VAULT999; the vault-liveness
  gate is off (probes live `:5001`).
* Receipt authenticity — unsigned (no HMAC key).
* Stable hashes: ids, PIDs, hashes change per run; verdicts and the 22 checks do not.

## Reproduce

    cd experiments/demo-60s && ./run.sh 2>&1 | tee TRANSCRIPT.txt

Any interpreter that can `import arifosmcp` (`$ARIFOS_PYTHON`,
`../../.venv/bin/python`, `python3`). Non-zero exit if a check fails.
