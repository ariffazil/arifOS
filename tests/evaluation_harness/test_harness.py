"""
tests/evaluation_harness/test_harness.py — Evaluation Harness for arifOS Kernel Primitives.

Comprehensive test harness for constitutional compliance, regression,
and scenario-based evaluation of new kernel primitives.
"""

import unittest
from core.kernel.pattern_registry import PatternRegistry
from core.kernel.pattern_selector import PatternSelector
from core.kernel.planner import Planner
from core.kernel.tool_registry import ToolContractRegistry
from core.kernel.role_registry import AgentRoleRegistry

class TestKernelPrimitives(unittest.TestCase):
    """Scenario-based evaluation of the arifOS kernel primitives."""

    def setUp(self):
        """Initialize all registries for testing."""
        self.pattern_registry = PatternRegistry()
        self.pattern_selector = PatternSelector(self.pattern_registry)
        self.planner = Planner()
        self.tool_registry = ToolContractRegistry()
        self.role_registry = AgentRoleRegistry()

    def test_pattern_registry_and_selection(self):
        """Test registration and selection of agentic patterns."""
        # Check defaults
        self.assertIn("ReAct", self.pattern_registry.list_patterns())
        self.assertIn("Reflection", self.pattern_registry.list_patterns())

        # Test selection
        context = {"available_tools": ["search"], "query": "Find the capital of France."}
        selected = self.pattern_selector.select(context)
        self.assertEqual(selected, "ReAct")

        context = {"query": "Check this answer for errors.", "requires_verification": True}
        selected = self.pattern_selector.select(context)
        self.assertEqual(selected, "Reflection")

        context = {"query": "Hello world."}
        selected = self.pattern_selector.select(context)
        self.assertEqual(selected, "Chain-of-Thought")

    def test_planner_tasks_and_dependencies(self):
        """Test planning and task dependency tracking."""
        plan = self.planner.create_plan(goal="Deploy service")
        
        t1 = self.planner.add_task(plan.id, "Build image")
        t2 = self.planner.add_task(plan.id, "Push image", dependencies=[t1])
        t3 = self.planner.add_task(plan.id, "Run container", dependencies=[t2])

        # Initially, only t1 should be ready
        ready_tasks = self.planner.get_current_tasks(plan.id)
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].id, t1)

        # Complete t1, now t2 should be ready
        self.planner.update_task_status(plan.id, t1, "COMPLETED")
        ready_tasks = self.planner.get_current_tasks(plan.id)
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].id, t2)

    def test_tool_contract_validation(self):
        """Test tool registration and call validation."""
        schema = {
            "name": "calculate",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"},
                    "precision": {"type": "integer"}
                },
                "required": ["expression"]
            }
        }
        self.tool_registry.register_tool("calculate", "Evaluate math expression", schema)

        # Valid call
        is_valid = self.tool_registry.validate_call("calculate", {"expression": "2+2"})
        self.assertTrue(is_valid)

        # Invalid call (missing required field)
        is_valid = self.tool_registry.validate_call("calculate", {"precision": 2})
        self.assertFalse(is_valid)

    def test_agent_role_assignment(self):
        """Test agent role registry and AAA role assignment."""
        self.role_registry.assign_role("agent_123", "Engineer", "session_abc")
        role = self.role_registry.get_role("agent_123")
        self.assertIsNotNone(role)
        self.assertEqual(role.name, "Engineer")
        self.assertIn("write", role.permissions)

if __name__ == "__main__":
    unittest.main()
