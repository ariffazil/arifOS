# WITNESS.md — how an outside human reproduces arifOS's governance claims

**You are the witness.** Not an agent, not a federation account, not a bot. A person with a
machine, Docker, and a public place to publish the result. You do not need access to Arif's VPS,
his database, his tokens, or his word.

**Time required: ~15 minutes.**

---

## Why this exists

arifOS claims that consequential agent actions are identity-bound, policy-authorized, executed
within scope, and refused when any of those fail. Today every receipt that supports that claim is
produced on a machine the claimant also administers. That is a record, not a proof.

This document exists so that one person outside the federation can check the claim and publish
what they found — including "it failed".

---

## What you are actually testing

Five negative tests. Each one tries to do something that should be refused, and checks that the
refusal happened **and that nothing was written**:

| # | Attack | Required result |
|---|--------|-----------------|
| N1 | call a mutating verb with no actor signature | explicit refusal; no silent binding to a session |
| N2 | address one agent with three different aliases | one canonical identity, not three |
| N3 | declare `verdict="SEAL"` over a judge packet saying HOLD | refusal; receipt records HOLD |
| N4 | force the gödel gate to time out during a seal | `HOLD`; no vault append |
| N5 | seal with a witness key identical to the actor key | refusal; witness recorded as absent |

A test that is missing is not a pass. A test that errors is not a pass. **The honest result of a
broken repo is "not ready", and that is a legitimate thing to publish.**

---

## Run it

```bash
git clone <REPO_URL> arifos-witness
cd arifos-witness
WITNESS_NAME="your name" ./witness.sh
```

`witness.sh` does everything: pinned commit, container, tests, result file. It writes
`witness-result.json` in the repo root.

If the repo is not ready to be witnessed, it says so and exits non-zero. Do not edit the script to
make it pass — the point is what it finds, not what it produces.

## Publish it

1. Copy `witness-result.json` into a repo **you** own (it does not have to be a fork).
2. Commit it, and say in your own words what you ran and what happened, including anything that
   looked wrong. Your sentence, not mine.
3. Optionally timestamp it so nobody — including Arif — can later claim this result was edited:
   ```bash
   pip install opentimestamps-client
   ots stamp witness-result.json          # produces witness-result.json.ots
   ots upgrade witness-result.json.ots    # re-run after a few hours to get the Bitcoin attestation
   ots verify witness-result.json.ots     # anyone can run this; no account, no trust in us
   ```
4. Send the link.

## What your result proves, and what it does not

**Proves:** that on your machine, at this commit, with a clean container, these five attempts were
refused (or were not).

**Does not prove:** that the rest of the system is trustworthy; that the tests are the right tests;
that a passing suite means the production instance behaves the same way. It proves one narrow,
falsifiable claim. That is the most any witness can honestly offer, and it is enough to start.

## If it fails

Publish the failure. A failing witness report is **more valuable** than a passing one, because it
names a defect the author could not see from inside. Do not soften it, and do not send it privately
first — publish, then tell him.

---

*DITEMPA BUKAN DIBERI — forged, not given.*
