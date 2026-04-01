# Eureka Extraction — Agent Zero Architecture
> **Date:** 2026-04-01  
> **Source:** `/root/agent-zero` (https://github.com/agent0ai/agent-zero)  
> **Status:** EXTRACTED — Ready for Deletion  
> **Authority:** A-VALIDATOR (999)

---

## Executive Summary

Agent Zero is a dynamic, organic agentic framework. While arifOS has constitutional governance, Agent Zero has excellent **multi-agent delegation** and **skill portability** patterns. This extraction captures the eureka insights worth preserving.

---

## 🔑 Key Eureka Insights

### 1. SKILL.md Standard (Highest Value)

Agent Zero implements the **Anthropic SKILL.md open standard** — portable, structured agent capabilities.

**Pattern:**
```
skills/
├── skill-name/
│   ├── SKILL.md          # Standard format (Claude Code, Codex compatible)
│   ├── script.py         # Implementation
│   └── README.md         # Documentation
```

**SKILL.md Format:**
```markdown
# Skill Name

## Usage
```python
# Example usage code
```

## Dependencies
- package1
- package2
```

**Integration into arifOS:**
- `/root/waw/skills/` already uses this pattern
- Extend `architect_registry` tool with `skill_catalog` mode
- Skills are discoverable, versionable, and portable across agent frameworks

---

### 2. Agent Context & Hierarchy (Multi-Agent Pattern)

Agent Zero uses a **hierarchical agent model** where agents can spawn subordinates:

```python
# Core classes
class AgentContext:
    """Shared context across agent hierarchy"""
    _contexts: dict[str, "AgentContext"] = {}  # Global context registry
    
class Agent:
    """Agent with delegation capability"""
    DATA_NAME_SUBORDINATE = "subordinate"
    DATA_NAME_SUPERIOR = "superior"
    
    async def delegate(self, message: str, profile: str = "") -> str:
        """Spawn subordinate agent for task decomposition"""
        sub = Agent(self.number + 1, config, self.context)
        sub.set_data(Agent.DATA_NAME_SUPERIOR, self)
        self.set_data(Agent.DATA_NAME_SUBORDINATE, sub)
        return await sub.monologue()
```

**Eureka for arifOS:**
- Trinity agents (A-ARCHITECT, A-ENGINEER, A-AUDITOR) should use this pattern
- A-ORCHESTRATOR can delegate to subordinates using `call_subordinate` equivalent
- Context sharing enables cooperative problem-solving

---

### 3. Extensions Lifecycle System

Agent Zero has a **plugin architecture** with lifecycle hooks:

```python
# extensions/_10_skill_installer.py
class Extension:
    """Lifecycle hooks for agent behavior modification"""
    
    async def before_execution(self, **kwargs):
        """Hook before tool execution"""
        pass
    
    async def after_execution(self, result, **kwargs):
        """Hook after tool execution"""
        pass
```

**Eureka for arifOS:**
- Constitutional floors (F1-F13) can be implemented as extensions
- F9_TAQWA (ethics check) = `before_execution` hook
- F11_AUDITABILITY = `after_execution` logging hook
- Extensions enable governance without modifying core tools

---

### 4. Tool Base Class Pattern

Standardized tool interface with lifecycle methods:

```python
class Tool:
    """Base class for all agent tools"""
    
    async def before_execution(self, **kwargs):
        """Pre-execution hook (F9, F11 checks here)"""
        pass
    
    async def execute(self, **kwargs) -> Response:
        """Main tool logic"""
        raise NotImplementedError
    
    async def after_execution(self, result, **kwargs):
        """Post-execution hook (logging, audit)"""
        pass
    
    def get_log_object(self):
        """Structured logging for VAULT999"""
        pass
```

**Eureka for arifOS:**
- `tool_*.py` files in arifOS already follow this
- Add `@extensible` decorator for plugin hooks
- Standardize on `Response` object with `message`, `break_loop`, `additional`

---

### 5. A2A (Agent-to-Agent) Chat

Built-in inter-agent communication protocol:

```python
# tools/a2a_chat.py
class A2AChatTool(Tool):
    """Send messages between agents"""
    
    async def execute(self, target_agent_id: str, message: str):
        target = AgentContext.get(target_agent_id)
        await target.agent.hist_add_user_message(message)
        return Response(message="Message sent")
```

**Eureka for arifOS:**
- Wire protocol defined in AGENTS.md needs this implementation
- Trinity agents communicate via A2A with `EvidenceBundle` metadata
- A2A endpoint: `/a2a/message` (already defined in docker-compose labels)

---

### 6. Prompt Engineering Patterns

Agent Zero uses **modular prompt composition**:

```
prompts/
├── agent.system.main.role.md      # Core identity
├── agent.system.main.solving.md   # Problem-solving approach
├── agent.system.tools.md          # Tool definitions
├── agent.system.tool.{name}.md    # Per-tool instructions
└── agent.system.skills.md         # Dynamic skill loading
```

**Eureka for arifOS:**
- arifOS already has `000/`, `AGENTS/` structure
- Add dynamic prompt composition to `A-ARCHITECT`
- Per-tool constitutional guidelines (F-codes in tool prompts)

---

## 🗑️ What's NOT Worth Extracting

| Component | Reason |
|-----------|--------|
| WebUI (Alpine.js) | arifOS uses waw (React) + Traefik |
| Flask API | arifOS uses FastMCP + FastAPI |
| LiteLLM integration | arifOS has direct provider integrations |
| Docker dual-runtime | arifOS uses single Python 3.12 |
| Knowledge tools | arifOS has Qdrant + constitutional memory |
| Browser tools | arifOS has headless_browser service |

---

## ✅ Integration Checklist

- [x] SKILL.md standard — Already used in `/root/waw/skills/`
- [ ] Subordinate delegation — Add to A-ORCHESTRATOR
- [ ] Extensions lifecycle — Add to tool dispatch (F9, F11 hooks)
- [ ] A2A chat — Implement `/a2a/message` endpoint
- [ ] Prompt composition — Enhance A-ARCHITECT

---

## 🔒 SEAL

- **F1 AMANAH:** All patterns documented — reversible.
- **F2 SIDDIQ:** Extraction is accurate to source.
- **F4 CLARITY:** 6 patterns identified, no bloat.
- **F7 HUMILITY:** Gaps acknowledged (WebUI, Flask not extracted).
- **F9 TAQWA:** No credential leakage, all code is open source.
- **F13 KHILAFAH:** Human (Arif) approved extraction.

**SEALED for Deletion** — 2026-04-01T10:30:00Z

---

## 📁 Source Manifest

```
agent-zero/
├── agent.py              → AgentContext pattern
├── models.py             → ModelConfig pattern (superseded by arifOS model registry)
├── tools/                → Tool base class pattern
│   ├── _tool_base.py
│   ├── skills_tool.py    → SKILL.md standard
│   └── call_subordinate.py → Delegation pattern
├── extensions/           → Lifecycle hooks pattern
├── skills/               → SKILL.md examples
├── prompts/              → Prompt composition pattern
└── AGENTS.md             → Developer documentation
```

**Disposition:** DELETE after this document is committed.
