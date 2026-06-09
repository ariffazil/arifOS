# arifOS Bubblewrap Integration — Agent Containment on Linux

> **FORGED:** 2026-06-09 by Ω (Omega)
> **Source:** MXC bubblewrap backend analysis (`mxc-research/src/backends/bubblewrap/`)
> **Status:** SPEC — implementation queued for next session
> **DITEMPA BUKAN DIBERI**

---

## 0. WHAT MXC TAUGHT US

Microsoft MXC uses bubblewrap (`bwrap`) as its DEFAULT Linux containment backend. The code at `mxc-research/src/backends/bubblewrap/common/src/bwrap_runner.rs` translates SandboxPolicy JSON into `bwrap` CLI arguments:

```
SandboxPolicy (JSON) → bwrap_runner.rs → bwrap CLI args → Linux user namespace
```

This is NOT Docker. This is NOT a VM. This is Linux kernel namespaces — the same technology Flatpak uses. Zero overhead. No daemon. No image layers. Just kernel-enforced isolation.

arifOS agents can use the SAME mechanism for OS-level containment without adding Docker or any Microsoft dependency.

---

## 1. BUBBLEWRAP — WHAT IT IS

`bwrap` (bubblewrap) is a setuid-less, unprivileged sandbox tool. It uses Linux user namespaces to create isolated environments:

```bash
# Install (already on most distros)
apt install bubblewrap

# Check
bwrap --version
```

Key capabilities:
- `--ro-bind SRC DST` — read-only bind mount (agent CAN'T write)
- `--bind SRC DST` — read-write bind mount
- `--tmpfs /tmp` — isolated /tmp (cleaned on exit)
- `--unshare-net` — NO network access
- `--unshare-pid` — isolated PID namespace
- `--die-with-parent` — kill sandbox when parent dies
- `--proc /proc` — mount procfs
- `--dev /dev` — mount minimal /dev

---

## 2. arifOS INTEGRATION PLAN

### Phase 1: Development Sandbox (this session)
```bash
#!/bin/bash
# arifos-bwrap.sh — Development sandbox for agent testing
exec bwrap \
  --ro-bind / / \
  --ro-bind /root/arifOS /workspace/arifOS \
  --bind /tmp /tmp \
  --bind /root/arifOS/output /workspace/output \
  --tmpfs /root/.ssh \
  --tmpfs /root/.aws \
  --tmpfs /root/.secrets \
  --unshare-net \
  --unshare-pid \
  --die-with-parent \
  --proc /proc \
  --dev /dev \
  python3 /workspace/arifOS/arifosmcp/server.py
```

### Phase 2: AgentPolicy → bwrap Args (next session)
```python
def policy_to_bwrap_args(policy: AgentPolicy) -> list[str]:
    """Translate AgentPolicy to bubblewrap CLI arguments."""
    args = ["bwrap"]

    # Filesystem
    if policy.filesystem_posture == FilesystemPosture.READ_ONLY:
        for path in policy.readonly_paths:
            args.extend(["--ro-bind", path, path])
    elif policy.filesystem_posture == FilesystemPosture.WORKSPACE:
        for path in policy.readwrite_paths:
            args.extend(["--bind", path, path])

    # Always deny sensitive paths
    for denied in policy.denied_paths:
        args.extend(["--tmpfs", denied])

    # Network
    if policy.network_posture == NetworkPosture.NONE:
        args.append("--unshare-net")

    # PID isolation
    args.append("--unshare-pid")

    # Die with parent
    args.append("--die-with-parent")

    return args
```

### Phase 3: Production Integration (multi-session)
- arifosd spawns MCP process inside bubblewrap
- AgentPolicy from AAA determines bwrap arguments
- VAULT999 records sandbox creation + destruction
- If MCP process crashes, bubblewrap cleans up

---

## 3. MXC vs arifOS BUBBLEWRAP — COMPARISON

| Feature | MXC | arifOS bwrap | Notes |
|---------|-----|-------------|-------|
| **Config format** | JSON (0.6.0-alpha schema) | AgentPolicy (Pydantic) | Different format, same concept |
| **Backend** | Rust → bwrap CLI | Python → bwrap CLI | Same underlying tool |
| **SDK** | TypeScript (@microsoft/mxc-sdk) | Python (agent_policy.py) | Language-native wrapper |
| **Lifecycle** | provision→deprovision | AgentLifecycle in AAA | Same state machine pattern |
| **Cross-platform** | Windows/Linux/macOS | Linux only | arifOS only needs Linux |
| **Maturity** | Early preview (alpha) | Spec (today) | Both pre-production |
| **License** | MIT | Proprietary (Arif) | Different licensing |

---

## 4. VERIFICATION

After Phase 1 implementation:

```bash
# Test 1: Can agent read a file outside the sandbox?
bwrap --ro-bind /usr /usr --tmpfs /root -- bash -c "cat /root/.ssh/id_rsa"
# Expected: cat: /root/.ssh/id_rsa: No such file or directory ✅

# Test 2: Can agent write to read-only mount?
bwrap --ro-bind /root/arifOS /root/arifOS -- bash -c "echo 'hacked' >> /root/arifOS/core/laws.py"
# Expected: Permission denied ✅

# Test 3: Can agent access network?
bwrap --unshare-net -- bash -c "curl -s http://example.com"
# Expected: curl: Could not resolve host ✅

# Test 4: Does sandbox clean up on exit?
bwrap --tmpfs /tmp -- bash -c "touch /tmp/test" && ls /tmp/test
# Expected: ls: cannot access '/tmp/test': No such file or directory ✅
```

---

## 5. GOTCHAS (from MXC source code)

1. **bwrap must be on PATH** — MXC checks `bwrap --version` before execution. Same pattern.
2. **Network filtering needs root** — `--unshare-net` (no network at all) works unprivileged. Per-domain filtering via iptables requires `CAP_NET_ADMIN`. MXC uses a cooperative proxy for unprivileged filtering.
3. **User namespace max** — Some distros limit user namespaces. Check: `cat /proc/sys/user/max_user_namespaces`
4. **No GPU access** — bubblewrap isolates the GPU by default. For VLM/vision agents, need `--dev-bind /dev/dri /dev/dri`

---

*DITEMPA BUKAN DIBERI — Even the sandbox is forged, not given.*
*999 SPEC | arifOS Federation | 2026-06-09*
