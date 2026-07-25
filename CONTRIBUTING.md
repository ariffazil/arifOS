# Contributing to arifOS

> **SOT:** 2026-07-25 | **DITEMPA BUKAN DIBERI**

arifOS is the constitutional governance kernel of the arifOS Federation. Contributions are welcome from anyone who respects the 13 constitutional floors (F1–F13).

## Before You Start

1. Read the [README](README.md) — understand the 8 canonical tools and 13 floors
2. Read [AGENTS.md](AGENTS.md) — agent boot sequence and autonomy tiers
3. Run `make health` — ensure the kernel is running

## Setup

```bash
git clone git@github.com:ariffazil/arifos.git && cd arifOS
uv sync --all-extras
python -m arifosmcp.runtime.server           # starts on :8088
curl http://127.0.0.1:8088/health
```

## Making Changes

1. **Fork → Branch → Edit → Test → PR**
2. Run `pytest tests/ -q --tb=short` before pushing
3. Run `ruff check . && ruff format .` for linting
4. Never skip the constitutional chain: `arif_init → arif_judge → arif_forge → arif_seal`

## Commit Format

```
[ORIGIN] description — TASK-ID
```

Where ORIGIN is one of: `FORGE`, `SEAL`, `HOLD`, `AUDIT`, `TEST`, `ZEN`, `REPAIR`, `COLLAPSE`

## Boundaries

- arifOS judges — never executes (A-FORGE does that)
- arifOS seals — never mutates without SEAL
- No self-authorization
- No floor bypass

## Federation

arifOS is one of 7 organs in the arifOS Federation. See [ariffazil/ariffazil](https://github.com/ariffazil/ariffazil) for the federation map.

---

*Maintained under F13 SOVEREIGN by Muhammad Arif bin Fazil.*
