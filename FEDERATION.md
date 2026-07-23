# FEDERATION.md — arifOS

```yaml
role: ROOT
organ: arifos
layer: L1
citizenship: warga-aaa
canon: ariffazil/ariffazil

depends_on:
  - repo: ariffazil/AAA
    reason: A2A gateway, state queries, cockpit triggers
  - repo: ariffazil/A-FORGE
    reason: Execution dispatch via forge_judge_proxy
  - repo: ariffazil/geox
    reason: Earth evidence routing
  - repo: ariffazil/wealth
    reason: Capital evidence routing
  - repo: ariffazil/well
    reason: Vitality evidence routing

mcp:
  port: 8088
  canonical_public_ingress: https://mcp.arif-fazil.com/mcp
  observatory_endpoint: https://arifos.arif-fazil.com/mcp
  tools_count: 8 public (48 internal)
  public_tools:
    - arif_init (000)
    - arif_observe (111)
    - arif_think (333)
    - arif_route (444)
    - arif_memory (555m)
    - arif_judge (888)
    - arif_forge (777)
    - arif_seal (999)

governance:
  judge: arifOS (self — constitutional kernel)
  seal: VAULT999 (append-only hash-chained ledger)
  floors: F1-F13 (enforced via GovernanceKernel.evaluate_floors)

stack_role: |
  arifOS is the constitutional kernel — L1 ROOT with AAA.
  It enforces 13 constitutional floors (F1-F13) over the 000→999 metabolic pipeline.
  It judges, routes, seals. It NEVER executes mutations directly.
  Execution is delegated to A-FORGE after SEAL verdict.
  Domain evidence is routed to GEOX/WEALTH/WELL.

entrypoints:
  - MCP: https://arifos.arif-fazil.com/mcp
  - Health: https://arifos.arif-fazil.com/health
  - Discovery: https://arifos.arif-fazil.com/llms.txt
  - Code: https://github.com/ariffazil/arifOS
```

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
**Part of the arifOS Federation. See `/root/AAA/docs/FEDERATION_MAP.md` for canonical topology.**
