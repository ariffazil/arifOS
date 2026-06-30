# arifOS Kernel Primitives

This document outlines the canonical agentic primitives implemented in the arifOS kernel. These primitives provide the foundational substrate for governed, multi-agent execution.

## 1. Pattern Registry (`core/kernel/pattern_registry.py`)
Catalog for reusable agentic patterns (e.g., ReAct, Reflection, Chain-of-Thought).
- **Purpose:** Enables explicit, auditable selection of agentic execution patterns.
- **Key Interface:**
    - `register_pattern(name, description, schema)`
    - `get_pattern(name)`
    - `list_patterns()`

## 2. Pattern Selection Engine (`core/kernel/pattern_selector.py`)
Dynamically selects the most appropriate agentic pattern based on task context.
- **Purpose:** Ensures the right agentic pattern is applied per task, supporting safe and optimal execution.
- **Key Interface:**
    - `select(context)` -> Returns optimal pattern name.
    - `apply(pattern_name, state)` -> Instantiates a pattern with the given state.

## 3. Planner Object / Task Graph (`core/kernel/planner.py`)
Manages multi-step plans and task graphs for complex workflows.
- **Purpose:** Enables explicit, inspectable planning and task decomposition.
- **Key Interface:**
    - `create_plan(goal, context)`
    - `add_task(plan_id, description, dependencies)`
    - `get_current_tasks(plan_id)` -> Returns tasks ready for execution.

## 4. Tool Contract Registry (`core/kernel/tool_registry.py`)
Central registry for tool schemas and validation logic.
- **Purpose:** Ensures tools are discoverable, schema-validated, and safely callable.
- **Key Interface:**
    - `register_tool(name, description, schema)`
    - `validate_call(name, params)` -> Validates call against registered schema.

## 5. Agent Role Registry / Handoff Protocol (`core/kernel/role_registry.py`)
Formalizes agent roles and multi-agent handoff protocols.
- **Purpose:** Enables auditable agent role assignment and safe transfer of authority.
- **Key Interface:**
    - `register_role(name, description, permissions)`
    - `assign_role(agent_id, role_name, session_id)`
    - `handoff(from_agent, to_agent, reason)`

## 6. Evaluation Harness (`tests/evaluation_harness/`)
Comprehensive test suite for kernel compliance and regression testing.
- **Purpose:** Ensures constitutional invariants are preserved across substrate updates.
- **Key Interface:**
    - `TestKernelPrimitives` (unittest-based scenarios).
