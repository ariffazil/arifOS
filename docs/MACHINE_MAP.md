# MACHINE MAP — CANONICAL SOT POINTER

> **The canonical Source of Truth for the arifOS federation physical topology lives in:**
> **[`/root/AAA/docs/MACHINE_MAP.md`](file:///root/AAA/docs/MACHINE_MAP.md)**

## Architecture Rationale: Why AAA Owns the Machine Map

1. **Separation of Eternal Kernel from Temporal Hardware:**
   `arifOS` is the **Constitutional Kernel & Court** (`:8088`). Its laws (F1–F13) and invariant logic must remain portable, eternal, and independent of specific machine IPs, cloud providers, or hardware upgrades.
2. **AAA as Federation Cockpit & Cartography:**
   `AAA` is the operational interface and cartographer of the federation. It houses the organ manifests (`AAA/federation/organs.yaml`), agent instructions (`AAA/instructions/`), and the authoritative multi-node infrastructure ledger.
3. **Single Pen Discipline:**
   Maintaining a single canonical document in `AAA/docs/MACHINE_MAP.md` eliminates split-brain drift and contradictory network maps across repositories.

Refer to `/root/AAA/docs/MACHINE_MAP.md` for the live 3-node topology (KVM8 truth, KVM4 workshop, KVM2 witness) and verification ledger.
