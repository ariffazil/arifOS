# AGENT_LAYOUT_CONTRACT - arifOS Federation

Status: SOVEREIGN LAW
Target: AI agents and automation working inside federation repos
Authority: Arif is final judge. Agents execute, audit, and propose.

## Purpose

This contract defines the structural grammar for arifOS federation repositories. Its job is to prevent stochastic repo entropy: random root files, duplicate configs, generated artifacts in source paths, and behavior-changing "cleanup" disguised as housekeeping.

## Root Rule

The repository root is a low-entropy navigation layer. It should help a human or agent understand the repo in under one minute.

Allowed root items:

- `README.md`
- `AGENTS.md` and existing agent SOT files such as `.AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `ARIF.md`
- `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODEOWNERS`
- `.gitignore`, `.gitattributes`, `.editorconfig`, `.env.example`
- dependency manifests and lockfiles: `package.json`, `package-lock.json`, `pyproject.toml`, `uv.lock`, `requirements.txt`
- root orchestration files: `Makefile`, `Dockerfile`, `docker-compose.yml`
- `.github/`
- canonical source directories: `src/`, repo package directories, `core/`, `arifosmcp/`, `host/`, `mcp/`
- verification directories: `tests/` or `test/`
- governance and memory directories: `docs/`, `specs/`, `contracts/`, `schemas/`
- operation directories: `scripts/`, `config/`, `deploy/`, `examples/`, `archive/`
- small fixture directories: `data/`, `fixtures/`

Anything else at root must have a reason documented in `README.md`, `AGENTS.md`, or this contract. New root items require explicit approval unless they are clearly generated ignored files.

## Directory Grammar

| Path | Purpose | Rule |
| --- | --- | --- |
| `src/` or package dir | Production code | Runtime behavior lives here. |
| `tests/` or `test/` | Proof | Preserve each repo's established test directory name. |
| `docs/` | Human and agent memory | Docs belong here, not scattered at root. |
| `specs/`, `contracts/`, `schemas/` | Law and interfaces | Public contracts must not be renamed silently. |
| `scripts/` | Automation | One-off tools go here, not at root. |
| `config/` | Non-secret templates | Secrets and live `.env` files are forbidden. |
| `data/`, `fixtures/` | Small test data only | Large runtime data belongs outside Git. |
| `deploy/` | Deployment source | Deployment edits require extra verification. |
| `archive/` | History | Archive instead of deleting when history matters. |

## Classification

Wajib:

- README, agent contract, license, dependency manifest, lockfile, source, tests, docs, CI, safe env template.

Sunat:

- contributing guide, security policy, code owners, architecture docs, ADRs, doctor/audit scripts, archive manifest.

Harus:

- Docker files, local compose, config templates, small fixtures, examples, benchmarks.

Makruh:

- many markdown files at root, temp/scratch folders, duplicate configs, generated reports, build outputs, big binaries.

Haram:

- secrets, live credentials, unapproved deletes, casual license edits, package-manager drift, deploy edits without verification, public API or contract renames without migration.

## Execution Rules

1. Audit before patch. Identify runtime, package manager, build/test commands, dirty files, and root anomalies.
2. Move before dump. New scripts go to `scripts/`; new docs go to `docs/`.
3. Archive before delete. Do not remove historical material without approval and a manifest.
4. Preserve behavior. Housekeeping must not change imports, public APIs, deployment behavior, or lockfiles unless explicitly approved.
5. Keep generated artifacts out of source. Logs, sessions, caches, build outputs, reports, and local databases must be ignored or externalized.
6. Resolve paths from the repo root or environment variables. Brittle relative paths are prohibited.
7. Summarize moves as `old_path -> new_path` with reason, risk, and verification command.

## Repo-Specific Notes

- `arifOS`: strictest root control. It is the constitutional kernel. Do not casually alter tool registry, floor logic, vault behavior, or deploy source of truth.
- `AAA`: control plane, cockpit, A2A gateway, and agent identity workspace. `agents/*` identity files may be source; `agents/*/runtime/` is runtime and must stay ignored.
- `A-FORGE`: TypeScript execution runtime. Keep `src/` canonical and preserve `test/` singular unless a deliberate migration is approved.
- `WEALTH`: dual Python/Node repo with legal sensitivity. Do not auto-fix license mismatch or collapse Python/Node structure without approval.
- `GEOX`: geoscience/domain runtime. Preserve compatibility aliases and manifests; keep large operational data outside Git.

## Verification

Before pushing housekeeping:

```bash
git status --short --branch
git diff --check
```

Then run the repo's established build/test commands from `AGENTS.md`, `README.md`, `Makefile`, package manifests, or CI.

## HOLD Items

Stop and ask Arif before:

- deleting files with history
- force pushing, rebasing shared branches, or rewriting history
- changing license fields
- changing package manager or lockfile without dependency intent
- changing deployment config
- moving code across module boundaries
- renaming public tools, schemas, endpoints, or contracts
- committing secrets or live runtime state

Ditempa Bukan Diberi. Root is navigation. Source is execution. Tests are proof. Docs are memory. Specs are law. Scripts are tools. Archive is history.
