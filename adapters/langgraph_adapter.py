"""
LangGraph Adapter for arifOS Constitutional Kernel

This adapter acts as a middleware node for LangGraph workflows.
It forces high-risk actions to pause for constitutional judgment (F1-F13)
via arifOS, before the execution node is allowed to run.
"""
from typing import Dict, Any, Callable
from arifosmcp.tools.judge import arif_judge_deliberate

def create_arifos_judgment_node(
    intent_extractor: Callable[[Dict[str, Any]], str],
    risk_classifier: Callable[[Dict[str, Any]], str] = lambda x: "high",
    reversible_checker: Callable[[Dict[str, Any]], bool] = lambda x: False
):
    """
    Creates a LangGraph node that performs arifOS judgment.
    
    Args:
        intent_extractor: Function to extract the intent/action description from the state.
        risk_classifier: Function to classify risk based on state.
        reversible_checker: Function to determine if action is reversible.
        
    Returns:
        A LangGraph-compatible node function.
    """
    
    async def arifos_judgment_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        The actual node that intercepts the workflow.
        """
        intent = intent_extractor(state)
        risk = risk_classifier(state)
        reversible = reversible_checker(state)
        
        # If low risk and reversible, we might fast-path, but we still pass through judge
        # with different parameters.
        
        # Call the arifOS judge
        judge_output = await arif_judge_deliberate(
            proposed_action=intent,
            session_id=state.get("session_id", "langgraph_session"),
            reversible=reversible,
            actor_id="langgraph_agent",
            evidence=state.get("evidence", []),
            trace_root=state.get("trace_id", "unknown_trace")
        )
        
        verdict = judge_output.verdict
        
        # Update state with the verdict
        new_state = state.copy()
        new_state["arifos_verdict"] = verdict
        new_state["arifos_advisory"] = judge_output.advisory
        new_state["arifos_failed_floors"] = judge_output.failed_floors
        
        if verdict in ["HOLD", "VOID", "SABAR"]:
            new_state["workflow_status"] = "BLOCKED"
        else:
            new_state["workflow_status"] = "APPROVED"
            
        return new_state
        
    return arifos_judgment_node

def arifos_routing_edge(state: Dict[str, Any]) -> str:
    """
    A LangGraph conditional edge that routes based on the arifOS verdict.
    Must be attached after the arifos_judgment_node.
    """
    status = state.get("workflow_status", "UNKNOWN")
    verdict = state.get("arifos_verdict", "UNKNOWN")
    
    if status == "APPROVED" and verdict == "SEAL":
        return "execute_action"
    elif verdict == "SABAR":
        return "replan"
    elif verdict == "HOLD":
        return "human_review"
    else:
        return "end"
