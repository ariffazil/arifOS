# START HERE — arifOS Documentation

**One question, four paths.**

## What are you trying to do?

### "I want to understand what arifOS is"
Read the [README](../README.md) — it covers the problem, solution, architecture, and what is/isn't proven in one page.

### "I want to evaluate arifOS for my team"
1. Read the [README](../README.md) for architecture overview
2. Read [SECURITY.md](../SECURITY.md) for threat model and known gaps
3. Run `pip install arifos && arifos demo --guided` for a five-minute governed action
4. Check the [live health endpoint](https://arifos.arif-fazil.com/health) for current status

### "I want to build with arifOS"
1. Read the [README](../README.md) Quick Start section
2. Read the MCP interface documentation in the README
3. Connect to the kernel at `http://localhost:8088/mcp`
4. See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines

### "I want to review arifOS as a security evaluator"
1. Read [SECURITY.md](../SECURITY.md) — threat model, known gaps, disclosure policy
2. Read the [README](../README.md) "What Is Proven" and "What Is Not Yet Proven" sections
3. Check the [live health endpoint](https://arifos.arif-fazil.com/health)
4. The kernel source is in `arifosmcp/` — constitutional floors are in `arifosmcp/constitution/`

---

## Documentation Map

| Document | Purpose |
|----------|---------|
| [README](../README.md) | What arifOS is, how it works, what's proven |
| [SECURITY.md](../SECURITY.md) | Threat model, known gaps, disclosure policy |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | How to contribute |
| [LICENSE](../LICENSE) | AGPL-3.0 license terms |

### Architecture
| Document | Purpose |
|----------|---------|
| [FEDERATION_CARD.md](./FEDERATION_CARD.md) | Organ topology and relationships |
| [README-FULL.md](./README-FULL.md) | Complete feature documentation |
| [CONSTITUTION.md](./CONSTITUTION.md) | Constitutional floors and doctrine |
| [ZEN.md](./ZEN.md) | Governance philosophy |

### Reference
| Document | Purpose |
|----------|---------|
| [VAULT999_README.md](./VAULT999_README.md) | Audit ledger implementation |
| [VERDICT_SEMANTICS.md](./VERDICT_SEMANTICS.md) | What SEAL/HOLD/SABAR/VOID mean |
| [QUICKSTART.md](./QUICKSTART.md) | Getting started guide |

---

## Evidence Hierarchy

Every claim in this documentation is classified:

- **OBS** — Externally observable (GitHub, PyPI, live endpoints)
- **DER** — Derived from observed evidence (architecture analysis, code inspection)
- **INT** — Interpretive (assessment, positioning, recommendations)
- **SPEC** — Specification (design intent, not yet proven in production)

When you see a claim, check which class it belongs to. OBS claims can be independently verified. INT claims are the author's assessment. SPEC claims are design goals.

---

**Last updated:** September 2026
**Maintainer:** Muhammad Arif bin Fazil
