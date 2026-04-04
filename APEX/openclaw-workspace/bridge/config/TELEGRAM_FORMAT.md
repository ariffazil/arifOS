# TELEGRAM_FORMAT.md — Reply Template for Telegram

*Standardized output format for AGI agents communicating via Telegram*

**Authority:** Muhammad Arif bin Fazil (888 Judge)
**Format:** MarkdownV2 (Telegram-native)
**Status:** SEALED

---

## Why MarkdownV2?

- Native to Telegram — no conversion needed
- Coder-friendly — works in terminals and logs
- Less escaping pain than HTML
- OpenClaw already supports it

---

## Standard Reply Template

Use this structure for most replies:

```markdown
**Snapshot**
<one sentence answer with context>

**Key Points**
• <main point 1>
• <main point 2>
• <main point 3 if needed>

**Options**
A: <label> — <brief trade-off>
B: <label> — <brief trade-off>

**Next Step**
<what Arif can do now, or "Awaiting your call">
```

---

## Minimal Template (Fast Chat)

For quick mobile replies:

```markdown
**Snapshot**
<1 sentence answer>

• <reason 1>
• <reason 2>

Options: A (<label>) or B (<label>)
```

---

## When to Show Governance

**Default:** Hide all internal metrics (Ω₀, floors, Δ·Ω·Ψ scores)

**Show only when:**
1. Arif explicitly asks ("show me the metrics")
2. High-risk decision requiring audit trail
3. Constitutional violation detected

When shown, use human labels:
- "Confidence: moderate" instead of "Ω₀ = 0.05"
- "Reversible via git" instead of "F1 Amanah: PASS"
- "Estimate only" instead of "F2 Truth < 0.95"

---

## Formatting Rules

| Element | MarkdownV2 Syntax |
|---------|-------------------|
| Bold header | `**Header**` |
| Bullet point | `•` or `-` |
| Code/command | `` `code` `` |
| Link | `[text](url)` |
| Italic | `_italic_` |

**Escape these characters:** `_`, `*`, `[`, `]`, `(`, `)`, `~`, `` ` ``, `>`, `#`, `+`, `-`, `=`, `|`, `{`, `}`, `.`, `!`

---

## OpenClaw Configuration

OpenClaw handles Telegram formatting automatically. No code changes needed.

Current setup:
- Channel: Telegram (@AGI_ASI_bot)
- Parse mode: MarkdownV2 (default)
- Block streaming: enabled for Telegram

---

## Examples

### Technical Task

```
**Snapshot**
Database backup completed successfully.

**Key Points**
• 47 tables exported to `/backup/2026-02-07.sql`
• Compressed size: 12MB
• Verified with checksum

**Next Step**
Backup is ready. Want me to schedule this daily?
```

### Decision Support

```
**Snapshot**
Two viable options for the API migration.

**Options**
A: Gradual rollout — lower risk, takes 2 weeks
B: Full cutover — faster, but needs weekend downtime

**Trade-off**
A is safer but slower. B matches your "fast for reversible" preference since we can rollback within 4 hours.

**Next Step**
Your call. Say "A" or "B" and I'll execute.
```

### Uncertainty Case

```
**Snapshot**
I can give you a rough estimate, but data is limited.

**Key Points**
• Based on 3 similar projects, cost range is RM 15-25K
• Confidence is moderate — no direct quotes yet

**Next Step**
Want me to get actual quotes, or is the range enough for now?
```

---

## Governance Audit

| Floor | Compliance |
|-------|------------|
| F2 Truth | ✅ Uncertainty stated plainly |
| F4 Clarity | ✅ Structured, scannable format |
| F7 Humility | ✅ No fake precision |
| F9 Anti-Hantu | ✅ No jargon unless requested |

---

*Ditempa Bukan Diberi.* 🔥

**Last Updated:** 2026-02-07
