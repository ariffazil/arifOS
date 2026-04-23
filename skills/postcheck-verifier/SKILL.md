---
name: postcheck-verifier
description: Proves actions worked in reality — not just exit code 0, not just logs — by validating actual observable outcomes in the system
user-invocable: true
type: flow
triggers:
  - after_action
  - after_deploy
  - after_change
  - claim_of_success
  - chain_step_complete
---

# postcheck-verifier

**P0 — Reality-Proven Outcome Verification**
**Seal:** DITEMPA BUKAN DIBERI · 2026-03-27

---

## Purpose

Every agent reports success too easily. `exit code 0` means the command ran, not that the goal was achieved. The `postcheck-verifier` exists because:

> **"The map is not the territory. The exit code is not the outcome."**

The opencode catastrophe is a textbook example: every git command returned success, every merge reported completion, and the final state was catastrophic destruction. Success was assumed from the command's return code, not from the system's actual state.

**Why this is P0:** Closing this gap adds an estimated +20% to AGI readiness (the single largest jump in the P0 set). `postcheck-verifier` is what separates a tool-using automaton from an AGI agent.

---

## The Verification Hierarchy

Not all verification is equal. Use the right level:

| Level | What It Proves | Example |
|-------|---------------|---------|
| **L0 — Exit Code** | Command ran | `grep` found something |
| **L1 — Output Check** | Output matches expectation | `docker ps` shows running container |
| **L2 — State Probe** | System state changed as intended | HTTP endpoint responds correctly |
| **L3 — Functional Test** | The feature actually works | User can log in, API returns correct data |
| **L4 — Reality Proof** | The change achieved the goal in the real world | The system does what Arif asked |

**Minimum standard for arifOS:** L2 for routine ops. L3 for code changes. L4 for sovereign decisions.

---

## Verification Protocol

### After Every Action — Run This

```bash
postcheck-verifier() {
  local action="$1"
  local expected="$2"
  local actual="$(eval "$action" 2>/dev/null)"
  local exit_code=$?

  # L0: Command ran
  if [ $exit_code -ne 0 ]; then
    echo "[L0 FAIL] Command exited with code $exit_code"
    echo "[ACTUAL] $actual"
    return 1
  fi
  echo "[L0 PASS] Command exited 0"

  # L1: Output matches expectation
  if [ -n "$expected" ] && ! echo "$actual" | grep -q "$expected"; then
    echo "[L1 FAIL] Output did not contain expected: $expected"
    echo "[ACTUAL] $actual"
    return 1
  fi
  echo "[L1 PASS] Output matches expected"

  # L2: State probe (when applicable)
  case "$action" in
    docker\ start*)
      container_name=$(echo "$action" | awk '{print $3}')
      state=$(docker inspect -f '{{.State.Running}}' "$container_name" 2>/dev/null)
      [ "$state" = "true" ] && echo "[L2 PASS] Container $container_name is running" || {
        echo "[L2 FAIL] Container $container_name not running"
        return 1
      }
      ;;
    curl\ -sf\ http://localhost:*)
      endpoint="${action#curl -sf }"
      curl -sf "$endpoint" > /dev/null 2>&1 && echo "[L2 PASS] $endpoint responds" || {
        echo "[L2 FAIL] $endpoint not reachable"
        return 1
      }
      ;;
    git\ push*)
      # Check remote actually has the commits
      git fetch origin 2>/dev/null
      local_sha=$(git rev-parse HEAD)
      remote_sha=$(git rev-parse origin/main 2>/dev/null)
      [ "$local_sha" = "$remote_sha" ] && echo "[L2 PASS] Commit on remote" || {
        echo "[L2 FAIL] Commit not on remote. Local=$local_sha Remote=$remote_sha"
        return 1
      }
      ;;
  esac

  echo "[VERIFIED] Action verified to L2. For L3/L4, manual verification recommended."
  return 0
}
```

### L3 — Functional Test Template

```bash
# For code changes — run actual functional proof
test_functional() {
  local feature="$1"
  case "$feature" in
    mcp_health)
      # Real probe: does the MCP actually process a request?
      response=$(curl -sf -X POST http://localhost:8080/mcp \
        -H "Content-Type: application/json" \
        -d '{"method":"tools/call","params":{"name":"health_probe"}}' 2>/dev/null)
      echo "$response" | grep -q "healthy" && echo "[L3 PASS] MCP functional" || {
        echo "[L3 FAIL] MCP responded but not healthy"
        return 1
      }
      ;;
    docker_compose)
      # Real probe: are all critical services reachable?
      for service in arifosmcp traefik postgres; do
        docker ps --filter "name=$service" --filter "status=running" | grep -q "$service" || {
          echo "[L3 FAIL] $service not running"
          return 1
        }
      done
      echo "[L3 PASS] All critical services running"
      ;;
    git_branch)
      # Real probe: does the branch have the expected files?
      required_files="core/governance_kernel.py core/judgment.py core/pipeline.py"
      for f in $required_files; do
        git ls-files | grep -q "^$f" || {
          echo "[L3 FAIL] Required file missing: $f"
          return 1
        }
      done
      echo "[L3 PASS] Required files present on branch"
      ;;
  esac
}
```

### L4 — Reality Proof (The Gold Standard)

```bash
# For sovereign decisions — prove the real-world outcome
prove_reality() {
  local goal="$1"
  echo "[L4] Proving reality: $goal"
  
  # The question to answer: "Did the system do what Arif asked?"
  case "$goal" in
    "main branch repaired")
      # The REAL proof: can pytest run? can the server start?
      cd /root/arifosmcp
      pytest --collect-only -q 2>/dev/null | tail -1 && echo "[L4 PASS] Tests collect" || echo "[L4 FAIL] Tests do not collect"
      curl -sf http://localhost:8080/health > /dev/null 2>&1 && echo "[L4 PASS] Server responds" || echo "[L4 FAIL] Server not responding"
      ;;
    "container running")
      # The REAL proof: can the service actually handle requests?
      docker exec arifosmcp python -c "import sys; sys.path.insert(0,'/root/arifosmcp'); from core.governance_kernel import GovernanceKernel; print('OK')" 2>/dev/null || echo "[L4 FAIL] Module cannot be imported inside container"
      ;;
    "config deployed")
      # The REAL proof: does the new config produce the expected behavior?
      curl -sf http://localhost:8080/health | grep -q "SOVEREIGN" && echo "[L4 PASS] Config loaded correctly" || echo "[L4 FAIL] Config not reflected"
      ;;
  esac
}
```

---

## Verification Matrix by Action Type

| Action Type | Minimum L | Required Check | Rollback If |
|------------|----------|----------------|-------------|
| `git push` / `git merge` | L2 | `git fetch && git log origin/main` shows commits | Yes |
| `docker start/restart` | L2 | `docker ps` shows running + health endpoint responds | Yes |
| `docker compose up -d` | L3 | All critical services respond to health probe | Yes |
| `pip install` / `uv add` | L2 | `python -c "import pkg"` succeeds | Yes |
| Code change | L3 | pytest passes (or equivalent functional test) | Yes |
| File edit / write | L1 | File exists + content check | Yes |
| Service restart | L2 | Service responds + logs show clean start | Yes |
| Production config change | L4 | Real-world behavior matches expectation | Yes |
| Irreversible (migration, delete) | L4 | Full reality proof + Arif veto | Always ask first |

---

## What "Verified" Means in arifOS

| Claim | Reality |
|-------|---------|
| "Git push succeeded" | ✅ Remote has the commits. Check with `git fetch && git log origin/main` |
| "Container is running" | ✅ `docker ps` shows it AND the health endpoint responds |
| "Server started" | ✅ `curl localhost:PORT/health` returns 200 |
| "Database migrated" | ✅ New schema query returns expected rows AND app queries work |
| "Config deployed" | ✅ Running process shows new config values, not old ones |
| "Test passed" | ✅ `pytest` exit 0 AND test count increased OR specific tests pass |

**What "verified" does NOT mean:**
- `exit code 0` alone
- `grep` found the string in a log
- A file was created
- A command printed "success"

---

## Anti-Patterns This Closes

1. **Exit code theater** — "it returned 0 so it worked" (the opencode disease)
2. **Log theater** — "the log says it started" but the service died 5 seconds later
3. **Creation verification** — a file existing doesn't mean its contents are correct
4. **Single-point verification** — checked only one indicator when the system has multiple dependencies
5. **No rollback plan** — verified success but had no way to undo if the verification was wrong

---

## Constitutional Alignment

| Floor | How Enforced |
|-------|--------------|
| F1 Amanah | Reversibility path checked before verification; rollback ready |
| F2 Truth ≥0.99 | L4 reality proof required for sovereign claims; no assumption |
| F4 ΔS ≤0 | Verification output is precise, no ambiguity in results |
| F7 Humility [0.03–0.05] | Uncertainty declared when verification is L2 only (not L4) |

---

*postcheck-verifier — Forged 2026-03-27 · DITEMPA BUKAN DIBERI · Reality Over Assumption 🔐*
