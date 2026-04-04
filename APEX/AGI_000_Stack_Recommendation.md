# AGI 000 Recommended AI LLM Stack

> **Source:** arifOS Constitutional AGI Framework  
> **Date:** 2026-02-09  
> **Status:** Active Recommendation

---

## 1. LLM Layer (Best-in-Class, LLM-Agnostic)

| Model | Use Case |
|-------|----------|
| **OpenAI GPT-4o** | Reasoning, code, general tasks |
| **Claude 3** | Constitutional, ethical, multi-agent workflows |
| **Gemini Pro** | Google ecosystem, multi-modal tasks |
| **DeepSeek-R1** | Open-source, compositional reasoning |
| **Mixtral, Llama-3, Mistral** | Local, scalable, privacy-focused |
| **Ollama** | Easy local model management and switching |

---

## 2. Agentic Orchestration Framework

### Coagent
- Monolithic or distributed agentic workflows
- Multi-agent orchestration
- Function calling, ReAct agents
- A2A protocol support
- LLM-agnostic (OpenAI, Claude, DeepSeek, etc.)
- 🔗 https://github.com

### Flux0
- Real-time streaming
- Session management
- Modular by design
- LangGraph, PydanticAI, and custom logic support
- 🔗 https://github.com

### AgentMesh
- Multi-agent collaboration
- Task planning
- Autonomous decision-making
- 🔗 https://github.com

### AWS Multi-Agent Orchestrator (Agent Squad)
- Flexible, scalable
- Context management
- Streaming and classifier routing
- 🔗 https://github.com

---

## 3. Memory Engine (Agent-Native, Persistent, Semantic)

### Aegis Memory ⭐
- **Agent-native memory fabric** (not just vector DB)
- Semantic search
- Scope-aware access control
- ACE patterns for persistent learning
- 🔗 https://github.com

### FAISS
- Fast vector search
- Document retrieval
- Meta AI's library

---

## 4. Governance & Safety Layer

### arifOS ⭐
- **Constitutional floors** (F1-F13)
- Async validation
- Audit trails
- Real-time override capability
- Integrates with Agent Zero and agentic frameworks
- 🔗 https://github.com

---

## 5. Deployment & Integration

| Component | Purpose |
|-----------|---------|
| **Docker** | Containerized, secure, scalable |
| **API Gateway** | External integration, typed access control |
| **Project-specific memory** | Isolated, auditable workflows |

---

## Stack Summary Table

| Layer | Recommended Components |
|-------|----------------------|
| **LLM** | GPT-4o, Claude 3, Gemini Pro, DeepSeek, Mixtral, Llama-3, Ollama |
| **Orchestration** | Coagent, Flux0, AgentMesh, Agent Squad |
| **Memory** | Aegis Memory, FAISS |
| **Governance** | arifOS |
| **Deployment** | Docker, API Gateway |

---

## 🔒 Best Practices

1. **LLM-Agnostic Orchestration** - Future-proofing and easy upgrades
2. **Modular Agent Roles** - Compositional reasoning
3. **Agent-Native Memory** - Persistent learning and context
4. **Constitutional Governance** - Lawful, auditable, fail-safe operation
5. **Containerization** - Security, scalability, portability

---

## References

- Coagent: https://github.com
- Flux0: https://github.com
- AgentMesh: https://github.com
- Agent Squad (AWS): https://github.com
- Aegis Memory: https://github.com
- arifOS: https://github.com

---

**Next Steps:**
- [ ] Evaluate Coagent vs Flux0 for primary orchestration
- [ ] Set up Aegis Memory alongside Qdrant
- [ ] Integrate arifOS constitutional floors
- [ ] Containerize with Docker Compose
