---
tier: 3
parent: AGENTS.md
purpose: Security guardrails + escalation triggers
load_when: shell_commands, file_system, credentials, production, 888_HOLD
version: v36.2 PHOENIX
---

# SECURITY.md - arifOS Guardrails (Tier 3)

**Enforcement layer.** Never bypass without human (888 Judge).

## 1. DENY PATTERNS (VOID immediately)

**NEVER execute without explicit human confirmation:**

```yaml
shell_deny:
  - rm -rf
  - DROP TABLE
  - TRUNCATE
  - shutil.rmtree
  - curl | bash
  - wget | sh
  - eval(input)
  - chmod 777
  - sudo rm
  - > /dev/sda

path_deny:
  - .env
  - .env.*
  - secrets/**
  - credentials/**
  - **/*.pem
  - **/*.key
  - **/*id_rsa*
  - **/.ssh/**
  - **/config/prod*
```

## 2. 888_HOLD TRIGGERS

Escalate to human when ANY of these occur:

| Category | Trigger | Action |
|----------|---------|--------|
| Scope | >10 files modified | HOLD |
| Scope | >500 lines changed | HOLD |
| Data | DB migrations | HOLD |
| Infra | Production deploy | HOLD |
| Auth | Credentials touched | HOLD |
| Git | Force push to main | HOLD |
| Config | CI/CD pipeline changes | HOLD |

**Response format:**
```
[888_HOLD] This action requires human (888 Judge) confirmation.
Category: {category}
Trigger: {trigger}
Risk: {low|medium|high}

Awaiting explicit approval: "proceed" or "abort"
```

## 3. REVERSIBILITY PRINCIPLE

| Operation | Reversibility | Approach |
|-----------|---------------|----------|
| Read | Always | Proceed |
| Create | Easy | Proceed with note |
| Modify | Medium | Commit first |
| Delete | Hard | 888_HOLD |
| Truncate | Impossible | 888_HOLD + backup |

## 4. FILE OPERATION SAFETY

**Before ANY file edit:**
1. Check file exists: `ls -la {path}`
2. Check git status: `git status`
3. Preview change: describe before executing
4. Prefer small, reversible edits

**Before ANY shell command:**
1. Explain what it does
2. Show expected output
3. Identify side effects
4. Require confirmation for destructive ops

## 5. CREDENTIAL HANDLING

**NEVER:**
- Echo credentials to stdout
- Store secrets in code
- Commit API keys
- Log sensitive data

**ALWAYS:**
- Use environment variables
- Reference secret managers
- Mask in output: `sk-...XXXX`

## 6. INCIDENT RESPONSE

If agent causes unintended effect:
1. STOP immediately (F1 Amanah)
2. Document what happened
3. Identify rollback path
4. Execute rollback with human
5. Add to deny patterns if needed

---

**Security is a floor, not a feature.**
