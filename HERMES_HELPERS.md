# HERMES_HELPERS.md — Hermes Agent Helper Specs

> **Forged:** 2026-06-14
> **Status:** Blueprint — ready for OpenCode forge
> **DITEMPA BUKAN DIBERI**

This document specifies 4 helper agents that Hermes can call directly.
These are NOT federation organs — they are **Hermes sub-agents**:
small, focused, single-purpose agents that Hermes spawns for specific tasks.

---

## Helper 1: Memory Steward

### Purpose
Manage Hermes's long-term context. When Hermes's context window is full
or a session is getting long, Memory Steward compacts without losing
critical facts.

### Trigger
- Context utilisation > 70%
- Hermes explicitly calls `memory_steward.compact(session_id)`

### Behaviour
1. Read current session transcript (last N messages)
2. Extract: decisions made, files forged, state changes, pending items
3. Compress into structured summary: ~500 chars max
4. Store compressed summary in L3 session memory with `compacted: true` flag
5. Return compacted context to Hermes

### Input
```json
{
  "session_id": "string",
  "last_n_messages": 50,
  "max_compact_length": 500,
  "preserve_topics": ["string"]
}
```

### Output
```json
{
  "status": "OK",
  "compacted": true,
  "original_length_chars": 15000,
  "compacted_length_chars": 480,
  "preserved": ["decision: forge ROOTKEY v53", "file: /root/arifOS/..."],
  "summary": "Ringkasan pendek..."
}
```

---

## Helper 2: Fact Checker

### Purpose
Verify a CLAIM against available evidence before Hermes asserts it.
Cross-references VAULT999, memory, and optionally external sources.

### Trigger
- Hermes makes a CLAIM at NAMPAK or RASA confidence level
- Hermes explicitly calls `fact_checker.verify(claim)`

### Behaviour
1. Receive claim + evidence_context
2. Search VAULT999 for matching entries
3. Search memory for contradictions
4. If mode="full": query external (Perplexity/Google) for corroboration
5. Return confidence score + gaps

### Input
```json
{
  "claim": "string",
  "evidence_context": "string (optional)",
  "mode": "quick | vault | full"
}
```

### Output
```json
{
  "status": "OK",
  "confidence_score": 0.85,
  "confidence_label": "TAHU",
  "evidence_found": [
    {"source": "VAULT999/SEAL-xxx.json", "match": 0.9}
  ],
  "gaps": ["No source attribution in claim"],
  "contradictions_found": []
}
```

---

## Helper 3: Plan Reviewer

### Purpose
Review an execution plan before Hermes submits it to OpenCode or
the kernel. Checks for missing steps, risk gaps, and E7 ceiling
violations.

### Trigger
- Hermes plans 3+ step action sequence
- Hermes explicitly calls `plan_reviewer.review(plan)`

### Behaviour
1. Receive plan as structured step list
2. For each step, check: risk level, reversibility, E7 autonomy band
3. Identify: missing preconditions, circular dependencies, resource gaps
4. Return: risk assessment + recommended changes

### Input
```json
{
  "plan_name": "string",
  "goal": "string",
  "steps": [
    {"step": 1, "action": "read file X", "risk": "low", "tool": "read_file"},
    {"step": 2, "action": "forge file Y", "risk": "medium", "tool": "forge_execute"}
  ],
  "organ_context": "string (optional)"
}
```

### Output
```json
{
  "status": "OK",
  "overall_risk": "medium",
  "step_reviews": [
    {"step": 1, "risk": "low", "recommendation": "auto"},
    {"step": 2, "risk": "medium", "recommendation": "propose"}
  ],
  "gaps": ["No verify step after forge"],
  "e7_check": "PASS — all steps within autonomy ceiling",
  "recommended_changes": ["Add step 3: verify"]
}
```

---

## Helper 4: Ecosystem Watcher

### Purpose
Monitor external feeds and alert Hermes when something relevant
appears. This is the "eyes on the outside" agent.

### Trigger
- Cron job (daily)
- Hermes explicitly calls `ecosystem_watcher.check()`

### Behaviour
1. Check MCP ecosystem news (GitHub releases, blog posts)
2. Check NATS/Temporal/Graphiti ecosystem
3. Check arifOS-related GitHub discussions
4. Summarise: "3 items relevant to arifOS this week"
5. Return structured alerts

### Output
```json
{
  "status": "OK",
  "alerts": [
    {
      "source": "FastMCP",
      "type": "new_release",
      "version": "3.3.0",
      "relevance": "Contains new task API — could improve forge pipeline",
      "url": "https://github.com/jlowin/fastmcp/releases/..."
    }
  ],
  "last_checked": "2026-06-14T04:00:00Z"
}
```

---

## Implementation Notes

### How Hermes Calls Helpers
Helpers are NOT MCP servers. They are:
1. **Python functions** in `arifosmcp/tools/hermes_helpers/` — each helper is a module with a single entry point
2. Called via `delegate_task()` with the helper's goal + context
3. Each helper runs in isolated subagent context

### Priority Order for Forging
1. Fact Checker (P0 — reduces epistemic risk immediately)
2. Memory Steward (P1 — extends context window)
3. Plan Reviewer (P1 — reduces E7 violations)
4. Ecosystem Watcher (P2 — nice-to-have)

### Constraints
- Helpers have NO access to MCP tools
- Helpers have NO ability to execute or forge
- Helpers return structured data only — no side effects
- Helpers are stateless — state lives in Hermes context
