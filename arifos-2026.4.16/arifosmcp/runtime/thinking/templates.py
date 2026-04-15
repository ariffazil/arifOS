"""
Thinking Templates for arifOS Sequential Thinking

Constitutional frameworks for structured reasoning.
Each template maps to specific constitutional floors.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ThinkingTemplate:
    """A constitutional thinking framework"""
    name: str
    description: str
    steps: List[str]  # Step prompts
    step_types: List[str]  # Corresponding step types
    constitutional_floor: str  # Primary floor this enforces
    use_cases: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL THINKING TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

THINKING_TEMPLATES: Dict[str, ThinkingTemplate] = {
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Scientific Method - F2 TRUTH focused
    # ═══════════════════════════════════════════════════════════════════════════
    "scientific-method": ThinkingTemplate(
        name="Scientific Method",
        description="Hypothesis → Experimentation → Verification → Conclusion",
        steps=[
            "Define the research question clearly and precisely",
            "Gather background information and existing evidence",
            "Formulate falsifiable hypothesis based on evidence",
            "Design verification approach (experiment or analysis)",
            "Execute verification step and collect data",
            "Analyze results and compare against hypothesis",
            "Draw conclusion: accept, reject, or revise hypothesis"
        ],
        step_types=["analysis", "analysis", "hypothesis", "verification", "verification", "verification", "conclusion"],
        constitutional_floor="F2_TRUTH",
        use_cases=["research", "debugging", "root_cause_analysis", "fact_verification"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Five Whys - F5 PEACE focused (systemic safety)
    # ═══════════════════════════════════════════════════════════════════════════
    "five-whys": ThinkingTemplate(
        name="Five Whys Analysis",
        description="Drill down to root cause by asking 'why' repeatedly",
        steps=[
            "State the problem or defect clearly",
            "Ask: Why does this happen? (Why #1) - Identify immediate cause",
            "Ask: Why does that happen? (Why #2) - Dig deeper",
            "Ask: Why does that happen? (Why #3) - Find contributing factors",
            "Ask: Why does that happen? (Why #4) - Uncover systemic issues",
            "Ask: Why does that happen? (Why #5) - Reach root cause",
            "Identify the weakest stakeholder affected and protect them"
        ],
        step_types=["analysis", "hypothesis", "hypothesis", "hypothesis", "hypothesis", "hypothesis", "conclusion"],
        constitutional_floor="F5_PEACE",
        use_cases=["incident_analysis", "defect_prevention", "safety_analysis", "quality_improvement"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # First Principles - F2 TRUTH focused
    # ═══════════════════════════════════════════════════════════════════════════
    "first-principles": ThinkingTemplate(
        name="First Principles Thinking",
        description="Break down to fundamental truths and rebuild",
        steps=[
            "Identify the current assumption, analogy, or inherited belief",
            "Break the problem down to fundamental, irreducible truths",
            "Verify each fundamental component is actually true",
            "Strip away inherited assumptions and historical analogies",
            "Rebuild solution from verified fundamentals only",
            "Test rebuilt solution against edge cases and constraints"
        ],
        step_types=["analysis", "analysis", "verification", "analysis", "hypothesis", "verification"],
        constitutional_floor="F2_TRUTH",
        use_cases=["innovation", "paradigm_shift", "complex_problem_solving", "breakthrough_design"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Decision Matrix - F3 TRI-WITNESS focused
    # ═══════════════════════════════════════════════════════════════════════════
    "decision-matrix": ThinkingTemplate(
        name="Decision Matrix",
        description="Weight criteria and score options systematically",
        steps=[
            "Define the decision to be made and its constraints",
            "Identify evaluation criteria (what matters for this decision)",
            "Assign weights to each criterion (sum to 1.0)",
            "List all viable options to evaluate",
            "Score each option against each criterion",
            "Calculate weighted scores for each option",
            "Synthesize decision with sensitivity analysis"
        ],
        step_types=["analysis", "analysis", "verification", "hypothesis", "verification", "verification", "conclusion"],
        constitutional_floor="F3_TRI_WITNESS",
        use_cases=["vendor_selection", "architecture_decisions", "prioritization", "tradeoff_analysis"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SWOT Analysis - F3 TRI-WITNESS focused (multi-perspective)
    # ═══════════════════════════════════════════════════════════════════════════
    "swot-analysis": ThinkingTemplate(
        name="SWOT Analysis",
        description="Analyze Strengths, Weaknesses, Opportunities, Threats",
        steps=[
            "Identify internal strengths (what we do well)",
            "Identify internal weaknesses (where we struggle)",
            "Identify external opportunities (market, timing, technology)",
            "Identify external threats (competition, risks, constraints)",
            "Cross-analyze: How can strengths capture opportunities?",
            "Cross-analyze: How can we mitigate weaknesses against threats?",
            "Synthesize strategic insights and priorities"
        ],
        step_types=["analysis", "analysis", "analysis", "analysis", "hypothesis", "hypothesis", "conclusion"],
        constitutional_floor="F3_TRI_WITNESS",
        use_cases=["strategic_planning", "project_evaluation", "personal_development", "competitive_analysis"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Root Cause Analysis (Fishbone) - F5 PEACE focused
    # ═══════════════════════════════════════════════════════════════════════════
    "root-cause-analysis": ThinkingTemplate(
        name="Root Cause Analysis",
        description="Fishbone/Ishikawa analysis for systemic causes",
        steps=[
            "Define the effect/problem (the 'head' of the fishbone)",
            "Identify major cause categories (People, Process, Technology, Environment)",
            "Brainstorm potential causes within each category",
            "Apply 5-Why analysis to each significant potential cause",
            "Identify true root causes vs symptoms",
            "Assess impact on weakest stakeholders",
            "Recommend systemic fixes with prevention focus"
        ],
        step_types=["analysis", "analysis", "hypothesis", "verification", "verification", "analysis", "conclusion"],
        constitutional_floor="F5_PEACE",
        use_cases=["incident_postmortem", "quality_assurance", "safety_investigation", "process_improvement"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Pros and Cons - F3 TRI-WITNESS focused
    # ═══════════════════════════════════════════════════════════════════════════
    "pros-cons": ThinkingTemplate(
        name="Pros and Cons Analysis",
        description="Balance weighing for binary decisions",
        steps=[
            "State the binary decision clearly",
            "List all advantages and positive factors (Pros)",
            "List all disadvantages and risks (Cons)",
            "Assign weights to each factor by importance",
            "Calculate weighted balance for both sides",
            "Consider F1: Which choice is more reversible?",
            "Make recommendation with confidence level"
        ],
        step_types=["analysis", "analysis", "analysis", "verification", "verification", "analysis", "conclusion"],
        constitutional_floor="F3_TRI_WITNESS",
        use_cases=["go_no_go", "build_vs_buy", "hire_decisions", "feature_flags"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Pareto Analysis - F8 GENIUS focused (efficiency)
    # ═══════════════════════════════════════════════════════════════════════════
    "pareto-analysis": ThinkingTemplate(
        name="Pareto Analysis",
        description="80/20 rule - identify vital few from trivial many",
        steps=[
            "List all problems, causes, or items to analyze",
            "Measure frequency, impact, or cost of each",
            "Rank by measured metric (highest first)",
            "Calculate cumulative percentage",
            "Identify the vital few (typically top 20%)",
            "Verify F8: Focus on high-impact, low-effort interventions",
            "Plan intervention for vital few with maximum leverage"
        ],
        step_types=["analysis", "verification", "verification", "verification", "analysis", "verification", "conclusion"],
        constitutional_floor="F8_GENIUS",
        use_cases=["prioritization", "resource_allocation", "bug_triage", "optimization"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Fishbone Diagram - F5 PEACE focused
    # ═══════════════════════════════════════════════════════════════════════════
    "fishbone": ThinkingTemplate(
        name="Fishbone Diagram (Ishikawa)",
        description="Visual root cause categorization",
        steps=[
            "State the problem (effect) at the 'head'",
            "Define the 6M categories: Man, Machine, Material, Method, Measurement, Environment",
            "Brainstorm causes per category (the 'bones')",
            "Identify potential root causes through evidence",
            "Verify root causes with data",
            "Assess safety impact of each root cause",
            "Recommend fixes with F1 reversibility check"
        ],
        step_types=["analysis", "analysis", "hypothesis", "verification", "verification", "analysis", "conclusion"],
        constitutional_floor="F5_PEACE",
        use_cases=["manufacturing_quality", "process_analysis", "systemic_failure", "design_review"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Ethical Analysis - F4 + F5 + F6 focused
    # ═══════════════════════════════════════════════════════════════════════════
    "ethical-analysis": ThinkingTemplate(
        name="Ethical Analysis Framework",
        description="Stakeholder-centered ethical decision making",
        steps=[
            "Define the decision and its direct/indirect effects",
            "Identify all stakeholders (especially weakest)",
            "Analyze impact on each stakeholder (benefits and harms)",
            "Apply reversibility test (F1): Can this be undone?",
            "Apply universality test: What if everyone did this?",
            "Assess F5: Does this protect the most vulnerable?",
            "Render verdict with ethical justification"
        ],
        step_types=["analysis", "analysis", "verification", "verification", "verification", "verification", "conclusion"],
        constitutional_floor="F5_PEACE",
        use_cases=["policy_decisions", "ai_ethics", "business_ethics", "medical_ethics"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Algorithm Design - F2 + F8 focused
    # ═══════════════════════════════════════════════════════════════════════════
    "algorithm-design": ThinkingTemplate(
        name="Algorithm Design",
        description="Systematic algorithm development with complexity analysis",
        steps=[
            "Define the problem and constraints clearly",
            "Identify the algorithm paradigm (greedy, divide-conquer, DP, etc.)",
            "Design the core algorithm logic",
            "Prove correctness (or provide strong argument)",
            "Analyze time complexity (best, average, worst)",
            "Analyze space complexity",
            "Identify edge cases and test scenarios"
        ],
        step_types=["analysis", "analysis", "hypothesis", "verification", "verification", "verification", "verification"],
        constitutional_floor="F2_TRUTH",
        use_cases=["coding_interviews", "system_design", "optimization", "research"]
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # Risk Assessment - F1 + F5 + F7 focused
    # ═══════════════════════════════════════════════════════════════════════════
    "risk-assessment": ThinkingTemplate(
        name="Risk Assessment",
        description="Systematic risk identification and mitigation",
        steps=[
            "Define the activity, system, or decision to assess",
            "Identify potential risks (technical, operational, human)",
            "Assess probability and impact of each risk",
            "Identify weakest stakeholders most at risk",
            "Design mitigations for high-priority risks",
            "Create rollback plan (F1 reversibility)",
            "Define go/no-go criteria with F7 uncertainty bounds"
        ],
        step_types=["analysis", "analysis", "verification", "analysis", "hypothesis", "analysis", "conclusion"],
        constitutional_floor="F1_AMANAH",
        use_cases=["deployment_planning", "architecture_review", "safety_analysis", "compliance"]
    ),
}


def get_template(name: str) -> ThinkingTemplate:
    """Get a thinking template by name"""
    if name not in THINKING_TEMPLATES:
        raise ValueError(f"Unknown template: {name}. Available: {list(THINKING_TEMPLATES.keys())}")
    return THINKING_TEMPLATES[name]


def list_templates(floor: str = None, use_case: str = None) -> List[str]:
    """List available templates with optional filtering"""
    templates = list(THINKING_TEMPLATES.items())
    
    if floor:
        templates = [(n, t) for n, t in templates if t.constitutional_floor == floor]
    
    if use_case:
        templates = [(n, t) for n, t in templates if use_case in t.use_cases]
    
    return [n for n, t in templates]


def auto_select_template(problem: str) -> str:
    """Auto-select template based on problem keywords"""
    problem_lower = problem.lower()
    
    # Algorithm/design problems
    if any(kw in problem_lower for kw in ["algorithm", "design", "complexity", "performance"]):
        return "algorithm-design"
    
    # Root cause / debugging
    if any(kw in problem_lower for kw in ["why", "cause", "defect", "bug", "incident", "error"]):
        return "five-whys"
    
    # Decision making
    if any(kw in problem_lower for kw in ["choose", "decide", "select", "vs", "between", "which"]):
        return "decision-matrix"
    
    # Ethical concerns
    if any(kw in problem_lower for kw in ["ethics", "should we", "morally", "fair", "bias"]):
        return "ethical-analysis"
    
    # Risk/safety
    if any(kw in problem_lower for kw in ["risk", "safety", "downtime", "failure", "migration"]):
        return "risk-assessment"
    
    # Strategy/planning
    if any(kw in problem_lower for kw in ["strategy", "plan", "roadmap", "future"]):
        return "swot-analysis"
    
    # Default to scientific method
    return "scientific-method"
