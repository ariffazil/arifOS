# Telegram Config Optimization Prompt

Use this prompt for any OpenClaw agent on your VPS to configure Telegram settings.

---

## Prompt to Paste

```
Configure Telegram for full agentic access:

1. Set streaming to "block" (full live response streaming)
2. Set dmPolicy to "open" (anyone can DM)
3. Set groupPolicy to "allowlist" with groupAllowFrom: ["*"]
4. Remove all tools.deny entries (allow all tools)
5. Remove gateway.nodes.denyCommands (allow all node commands)

Use gateway tool:
- config.get to read current config
- config.patch with baseHash to apply changes

After config.patch, gateway auto-restarts.
```

---

## Settings Explained

| Setting | Value | Meaning |
|---------|-------|---------|
| streaming | block | Full token-by-token streaming |
| dmPolicy | open | Anyone can DM the bot |
| allowFrom | ["*"] | Accept messages from all users |
| groupAllowFrom | ["*"] | Accept all groups |
| tools.deny | [] | No tool restrictions |
| gateway.nodes.denyCommands | [] | No node command restrictions |

---

## Quick Command Sequence

```bash
# Get current config
openclaw gateway config.get

# Patch (replace HASH with actual hash from config.get)
openclaw gateway config.patch --raw '{"channels":{"telegram":{"streaming":"block","dmPolicy":"open","allowFrom":["*"],"groupAllowFrom":["*"]}}}' --baseHash YOUR_HASH_HERE --note "Full agentic mode"
```

---

## Verification

After patch, check:
```bash
openclaw gateway status
openclaw channels telegram status
```

---

*Save this as `/root/openclaw-telegram-optimize.md` on your VPS for quick reference.*
