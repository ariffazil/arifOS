# Case 2 — 238,000 receipts that cannot be joined to the objective that produced them

## 1. What happened

The doctrine at `/root/AAA/instructions/state-transition-discipline.md:3` states that the
rule "every consequential receipt carries a trace_id" was codified from the two-KVM
coherence experiment, specifically "52,043 receipts with trace_id=NULL". The same figure
appears at `/root/AAA/instructions/proxy-reality-paradox.md:188`. I tried to reproduce it
and could not.

```
$ grep -rn "52,043" /root/arifOS
(no output)
$ grep -rn "52,043" /root/AAA/instructions/
state-transition-discipline.md:3:  … 52,043 receipts with trace_id=NULL; …
proxy-reality-paradox.md:188:- 52,043 receipts with trace_id=NULL (2026-09) — …
```

Two hits, both prose, in the same governance directory. `evidence not located` for any
measurement receipt, ledger, or probe that produced the number: I searched `/root/arifOS`
including `docs/`, `VAULT999/`, `scripts/`, and `tests/` (zero hits), plus
`/root/AAA/instructions/`, `/root/AAA/canon/`, `/root/AAA/reports/`, and `/root/work/`
(two prose hits). The claimed figure is unverified.

What can be counted is the current state of the receipt stores. This measurement was taken
at `2026-09-20T19:17:09Z`; the ledgers are live and append while you read them.

```
$ cd /root/arifOS/VAULT999 && python3 -c "…count records with no key matching 'trace'…"
MEASURED_AT=2026-09-20T19:17:09Z
files=23
records=238860
records_with_no_trace_field=238148
records_with_trace_id_key=5
records_with_trace_id_null=0
```

Read carefully. 238,148 of 238,860 records in the Vault999 JSONL ledgers carry no trace
field of any kind. Only 5 records carry a `trace_id` key, and none of those is null. So
the literal claim — records with the field present and set to NULL — is not reproducible
at all in this store, and the wider defect it points at is roughly 4.6x larger than the
doctrine's number.

The same defect is still being produced, at small scale, by the control that is supposed
to prevent it. The Hermes gate receipt trail:

```
$ python3 -c "…count trace_id is None in hermes_hook_receipts.jsonl…"
hermes_hook_receipts.jsonl records=29139 trace_id_null=18 sample_lines=[1, 2, 3, 4, 5, 6]
```

18 records with `trace_id: null`, all at the head of the trail — the records written before
a fallback mint was added. They are permanent, because the trail is append-only and
nothing backfills them.

## 2. The systemic cause

The write path was open-loop: a receipt writer earns its keep by recording that an event
occurred, so the causal key was optional at write time and no downstream consumer
complained. The gate hook's own writer still carries that shape —
`write_receipt(tool_name, classification, decision, reason="", trace_id="unknown", …)`.
A sentinel string is as unjoinable as a null: you cannot group by `"unknown"` and recover
which objective the record belonged to.

The cost is specific and testable. Given a receipt, you can answer "something happened at
this time". You cannot answer "which objective did this mutation come from", "what is this
witness attesting", or "which loop does this closure close". An append-only ledger with
238,000 unjoinable rows is an event pile, not a causal ledger, and the volume actively
misleads: receipt counts rise while traceability stays flat.

## 3. The control that now exists

- `/root/arifOS/arifosmcp/runtime/trace_enforcer.py::validate_trace` — returns
  `missing_trace_field:<key>` for each absent required trace field, and
  `invalid_trace_id_format` when a supplied id does not match the expected pattern;
  `enforce_trace` converts any violation into `status="HOLD"`.
- `/root/arifOS/arifosmcp/runtime/receipt_store.py` — declares `trace_id: str` as a
  required field of a `Receipt` and exposes `by_trace_id(trace_id)`, the join operation
  the earlier ledgers could not support.
- `/root/arifOS/arifosmcp/arifos_observability/trace_context.py` — mints the root
  `trace_id` at trusted ingress and propagates it to nested calls.

Proof:

```
$ cd /root/arifOS && .venv/bin/python -m pytest tests/runtime/test_receipt_store.py -q
16 passed, 3 warnings in 2.00s

$ .venv/bin/python -m pytest tests/test_trace_propagation.py -q
8 passed, 3 warnings in 2.47s
```

`test_trace_propagation.py` asserts the properties that make a receipt joinable: the root
span mints UUIDs with a null `parent_span_id`, a nested call inherits its parent's
`trace_id` and links the parent's `span_id`, siblings share a trace with distinct ids, and
context resets on exit. Both suites require the repository virtualenv; the system
`python3` cannot import the package (`ModuleNotFoundError: No module named 'blake3'`).

## 4. What is still missing

- No retraction. The "52,043" figure has never been marked `RETRACTED` or `SUPERSEDED`
  with a pointer to a corrected number, in either file that carries it — the exact
  stale-claim-propagation failure the same doctrine defines a metric for.
- No backfill and no annotation on the 238,148 historical records. They remain in the
  append-only ledger indistinguishable from joinable records.
- The gate hook's default `trace_id="unknown"` was not changed; the fallback mint in
  `main()` covers the normal path, which is why the nulls are historical, but the writer's
  contract still permits an unjoinable value.
- `evidence not located` for any published metric of joinability. The live health surface
  reports floors, tool counts, and drift; it does not report the fraction of receipts that
  carry a causal key.
- Whether 52,043 was ever accurate cannot be reconstructed; no historical probe or ledger
  snapshot carrying that count was located.

## 5. The lesson

A receipt count measures logging; only a shared causal key measures memory — so publish
the joinability rate, because an event pile and a causal ledger look identical in a line
count.
