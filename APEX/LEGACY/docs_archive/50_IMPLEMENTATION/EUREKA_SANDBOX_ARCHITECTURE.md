# EUREKA Sandbox Runner Architecture
**Version:** v62.6-STEEL  
**Component:** 777_EUREKA_FORGE Hardening  
**Floors:** F1, F5, F7, F12

---

## Executive Summary

**Problem:** EUREKA FORGE executes shell commands directly in the MCP container, risking VPS compromise if malicious commands slip through.

**Solution:** Route all execution through **disposable sandbox containers** with restricted capabilities.

```
EUREKA FORGE (MCP Server)
    ↓
Docker API: spawn runner container
    ↓
Sandbox Container (isolated)
    ↓
Limited filesystem access only
```

---

## Constitutional Alignment

| Floor | Sandbox Protection |
|-------|-------------------|
| **F1 Amanah** | Irreversible ops contained to sandbox |
| **F5 Peace²** | Safe defaults, minimal privileges |
| **F7 Humility** | Limited power (cap-drop=ALL) |
| **F12 Defense** | Hardened execution boundary |

---

## Architecture

### Before (Vulnerable)

```
MCP Container
    ↓
subprocess.run("rm -rf /", shell=True)  # 😱 HOST DEATH
```

### After (Sandboxed)

```
MCP Container (orchestrator)
    ↓
docker run --rm \
  --network=none \
  --cap-drop=ALL \
  --read-only \
  --memory=256m \
  --cpus=0.5 \
  -v /workspace:/workspace:rw \
  alpine:3.19 \
  sh -c "rm -rf /workspace/temp"  # ✅ Only sandbox dies
```

---

## Security Restrictions

| Restriction | Flag | Purpose |
|-------------|------|---------|
| No network | `--network=none` | Prevents data exfiltration |
| No privileges | `--cap-drop=ALL` | Prevents container escape |
| Read-only root | `--read-only` | Immutable base filesystem |
| Memory limit | `--memory=256m` | Prevents OOM attacks |
| CPU limit | `--cpus=0.5` | Prevents CPU exhaustion |
| PID limit | `--pids-limit=64` | Prevents fork bombs |
| No new privileges | `--security-opt=no-new-privileges` | Blocks privilege escalation |

---

## Implementation

### Runner Module

```python
# aaa_mcp/services/sandbox_runner.py
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple

class SandboxRunner:
    """
    F1 Amanah: Execute commands in disposable sandbox containers.
    
    All filesystem mutations are contained. Even CRITICAL commands
    can only damage the sandbox, not the host VPS.
    """
    
    def __init__(
        self,
        image: str = "alpine:3.19",
        memory_limit: str = "256m",
        cpu_limit: str = "0.5",
        timeout: int = 60,
    ):
        self.image = image
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.timeout = timeout
    
    async def execute(
        self,
        command: str,
        workspace: Path,
        env_vars: dict | None = None,
    ) -> Tuple[int, str, str]:
        """
        Execute command in sandbox.
        
        Returns: (exit_code, stdout, stderr)
        """
        # Build docker run command
        docker_cmd = [
            "docker", "run", "--rm",
            "--network=none",
            "--cap-drop=ALL",
            "--read-only",
            f"--memory={self.memory_limit}",
            f"--cpus={self.cpu_limit}",
            "--pids-limit=64",
            "--security-opt=no-new-privileges:true",
            "-v", f"{workspace}:/workspace:rw",
            "-w", "/workspace",
            self.image,
            "sh", "-c", command,
        ]
        
        # Execute with timeout
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        
        return (
            result.returncode,
            result.stdout,
            result.stderr,
        )
```

### Integration with eureka_forge

```python
# In eureka_forge implementation
from aaa_mcp.services.sandbox_runner import SandboxRunner

# Initialize sandbox runner (singleton)
_sandbox_runner = SandboxRunner()

async def eureka_forge(
    session_id: str,
    command: str,
    working_dir: str | None = None,
    use_sandbox: bool = True,  # ✅ Default to sandbox
    ...
) -> dict[str, Any]:
    """777 EUREKA FORGE with sandbox execution."""
    
    # ... risk classification ...
    
    if use_sandbox:
        # F1 Amanah: Execute in sandbox
        exit_code, stdout, stderr = await _sandbox_runner.execute(
            command=command,
            workspace=Path(working_dir),
        )
    else:
        # Fallback: direct execution (requires explicit override)
        # This path should rarely be used
        ...
    
    # ... build response ...
```

---

## Filesystem Allowlist

Restrict which directories can be mounted:

```python
ALLOWED_WORKSPACES = [
    "/usr/src/app/docs",
    "/usr/src/app/scripts", 
    "/usr/src/app/experiments",
    "/usr/src/app/data",
]

def validate_workspace(path: Path) -> bool:
    """F12 Defense: Only allowlisted paths."""
    resolved = path.resolve()
    return any(
        str(resolved).startswith(str(Path(allowed).resolve()))
        for allowed in ALLOWED_WORKSPACES
    )
```

---

## Docker Compose Updates

### 1. MCP Server Needs Docker Socket

```yaml
services:
  arifosmcp_server:
    # ... existing config ...
    volumes:
      # ... existing volumes ...
      - /var/run/docker.sock:/var/run/docker.sock:ro  # ✅ Spawn sandboxes
    environment:
      # ... existing env ...
      EUREKA_USE_SANDBOX: "true"
      EUREKA_SANDBOX_IMAGE: "alpine:3.19"
```

### 2. Dedicated Runner Network (Optional Hardening)

```yaml
networks:
  arifos_trinity:
    driver: bridge
  # Isolated network for sandboxes (no external access)
  sandbox_net:
    driver: bridge
    internal: true  # No internet access
```

---

## Risk Comparison

| Attack Vector | Direct Execution | Sandbox Execution |
|--------------|------------------|-------------------|
| `rm -rf /` | ☠️ HOST DEATH | ✅ Sandbox only |
| Fork bomb | ☠️ HOST OOM | ✅ PID limited |
| Network exfil | ☠️ Data stolen | ✅ No network |
| Container escape | ☠️ Root on host | ✅ Cap-drop=ALL |
| Crypto miner | ☠️ CPU stolen | ✅ CPU limited |

---

## Migration Path

### Phase 1: Workspace Boundary (Immediate)
- ✅ Implemented: `DEFAULT_WORKDIR` env var
- ✅ Implemented: Path validation in `eureka_forge`

### Phase 2: Sandbox Runner (Next)
1. Create `aaa_mcp/services/sandbox_runner.py`
2. Update `eureka_forge` to use sandbox by default
3. Add Docker socket mount to compose
4. Test with benign commands
5. Gradually migrate all execution

### Phase 3: Filesystem Allowlist (Future)
- Restrict to specific subdirectories
- Implement read-only mounts for sensitive areas

---

## Testing Sandbox

```bash
# Test 1: Benign command
docker run --rm --network=none --cap-drop=ALL \
  -v /srv/arifOS/docs:/workspace \
  alpine:3.19 sh -c "echo 'hello' > /workspace/test.txt"

# Test 2: Destructive command (contained)
docker run --rm --network=none --cap-drop=ALL \
  -v /srv/arifOS/temp:/workspace \
  alpine:3.19 sh -c "rm -rf /workspace/*"
# ✅ Only temp directory affected

# Test 3: Escape attempt (blocked)
docker run --rm --network=none --cap-drop=ALL \
  -v /srv/arifOS:/workspace \
  alpine:3.19 sh -c "cat /etc/shadow"
# ✅ File not found (read-only root, no host mount)
```

---

## Constitutional Verdict

```
┌─────────────────────────────────────────────────────────────┐
│ APEX JUDGE VERDICT: SEAL with F12 Hardening                 │
│                                                             │
│ EUREKA Sandbox Architecture                                 │
│                                                             │
│ F1 Amanah:    Irreversible ops contained ✅                 │
│ F5 Peace²:    Minimal privileges ✅                        │
│ F7 Humility:  Bounded power ✅                             │
│ F12 Defense:  Hardened boundary ✅                         │
│                                                             │
│ Status: Architecturally sound, implement Phase 2            │
└─────────────────────────────────────────────────────────────┘
```

---

## References

- Docker Security: https://docs.docker.com/engine/security/
- Container Runtime Security: https://github.com/opencontainers/runtime-spec/blob/main/config.md#linux-process
- arifOS F1 Amanah: `000_THEORY/000_LAW.md`
- arifOS F12 Defense: `000_THEORY/000_LAW.md`

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given  
**Ψ Psi Lane | Stage 777**
