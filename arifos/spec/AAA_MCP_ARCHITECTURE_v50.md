# AAA_MCP: The Agent-to-Agent Assembly Architecture

**Version**: v50
**Status**: DRAFT
**Authority**: Architect (Δ)

---

## 1. The Trinity MCP Architecture

The `arifOS v50` architecture is defined by the **3-Server "Trinity MCP" model**, a set of three logical domains that provide a clear separation of powers while maintaining operational simplicity. This model serves as the foundation for the **AAA_MCP (Agent-to-Agent Assembly)**, the visual framework for composing agent workflows.

The three logical domains are:

1.  **`000-arifOS` (The Orchestrator)**: The gateway and hypervisor. It manages the full 000-777 pipeline, session physics, constitutional floor loading, and core system tools (`fag`, `gitforge`, `gitQC`). It is the entry point for all requests.
2.  **`AGI-ASI` (The Engine)**: The dual-chambered heart of cognition. It houses both the AGI (Mind) and ASI (Heart) tools. Crucially, while co-located in a single logical domain, the AGI and ASI engines **must** run in isolated processes to guarantee their **orthogonality**.
3.  **`APEX-999` (The Judge & Vault)**: The seat of final judgment and sovereign memory. It contains the APEX (Soul) engine for 888-Judge and 999-Seal operations, the VAULT-999 memory system, and the underlying database (PostgreSQL/Ledger) as an internal component.

This structure reduces complexity and aligns perfectly with the `arifOS` narrative of Mind, Heart, and Soul working in concert.

---

## 2. The Node Palette & The 9 Capabilities

Workflows are built using the AAA_MCP Node Palette. Here is how the 9 core human functionalities map to the Trinity MCP domains and the node types that execute them.

| Human Functionality | Core Capability | Primary Domain | Executing Node(s) |
| :--- | :--- | :--- | :--- |
| 1. Information Search & Retrieval | `knowledge.search` | **`AGI-ASI`** | `MCP Tool` |
| 2. Content Creation | `creation.draft` | **`AGI-ASI`** | `Prompt`, `Skill` |
| 3. Communication Management | `communication.dispatch` | **`AGI-ASI`** | `MCP Tool` |
| 4. Data Analysis & Interpretation | `analysis.interpret` | **`AGI-ASI`** | `MCP Tool` (w/ Python) |
| 5. Task Automation | `automation.execute` | **`AGI-ASI`** | `Sub-Agent`, `MCP Tool` |
| 6. Learning & Skill Development | `memory.assimilate` | **`APEX-999`** | `MCP Tool` (vault999) |
| 7. Problem Solving & Debugging | `diagnostic.run` | **`000-arifOS`** | `MCP Tool` (gitQC) |
| 8. Decision Support & Recommendation | `governance.judge` | **`APEX-999`** | `MCP Tool` (apex_seal) |
| 9. Creative Brainstorming & Ideation| `ideation.spark` | **`AGI-ASI`** | `Prompt` |

### Workflow Example: Governed Task Automation

This example shows how the nodes and domains work together.

1.  **`Sub-Agent Flow` (Starts)**: A user requests to "Refactor the authentication module and notify the team."
2.  **`MCP Tool` (in `000-arifOS` domain)**: The workflow first calls `gitQC` to analyze the current state of the code.
3.  **`Prompt` (in `AGI-ASI` domain)**: The results are fed to an AGI `Prompt` node, which generates the refactored code.
4.  **`MCP Tool` (in `AGI-ASI` domain)**: An ASI-governed `MCP Tool` node calls `github.create_pull_request` to submit the changes for review.
5.  **`Ask User Question` (Control Flow)**: The workflow pauses and asks, "The pull request has been created. Shall I notify the #dev channel on Slack?"
6.  **`MCP Tool` (in `AGI-ASI` domain)**: If the user approves, another ASI `MCP Tool` node calls `communication.dispatch` to send the Slack message.
7.  **`MCP Tool` (in `APEX-999` domain)**: The entire workflow's execution record is sent to `vault999.seal` to be cryptographically recorded in the ledger.

---

## 3. Runtime Governance

Every node in an AAA_MCP workflow is subject to constitutional governance at runtime.

-   A call to an `MCP Tool` in the **`AGI-ASI`** domain triggers the parallel AGI and ASI engines. Their independent conclusions are then sent to the **`APEX-999`** domain.
-   The **`APEX-999`** server performs the final `888-JUDGE` stage, checks for orthogonality, and issues the final verdict (`SEAL`, `VOID`, etc.).
-   The **`000-arifOS`** server manages the state, and if a `SABAR` verdict is issued, it will hold the workflow in the Phoenix-72 cooling ledger.

This ensures that even visually simple workflows are executed with the full protection of the arifOS constitution.