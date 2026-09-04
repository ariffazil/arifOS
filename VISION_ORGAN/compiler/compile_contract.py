"""
Scene Contract Compiler — converts declarative scene contracts into generation prompts
"""

def compile_prompt(contract):
    """Compile a scene contract into an optimized generation prompt."""
    sc = contract.get("scene_contract", {})
    parts = []

    # Subject
    if sc.get("subject"):
        count = sc.get("subject_count", 1)
        if count > 0:
            parts.append(f"{count} {sc['subject']}")
        else:
            parts.append(sc["subject"])

    # Action
    if sc.get("action"):
        action = sc["action"]
        verb = action.get("verb", "")
        tool = action.get("tool", "")
        target = action.get("target", "")
        
        action_parts = []
        if verb:
            action_parts.append(verb)
        if tool:
            action_parts.append(f"using {tool}")
        if target:
            action_parts.append(f"{target}")
        
        parts.append(" ".join(action_parts))
        
        if action.get("required_relation"):
            parts.append(action["required_relation"])

    # Required objects
    if sc.get("required_objects"):
        parts.append(f"with {', '.join(sc['required_objects'])} clearly visible")

    # Setting
    if sc.get("setting"):
        parts.append(f"setting: {sc['setting']}")

    # Camera
    if sc.get("camera"):
        parts.append(f"camera: {sc['camera']}")

    # Negative constraints
    if sc.get("negative_constraints"):
        parts.append(f"NO {', '.join(sc['negative_constraints'])}")

    return ". ".join(parts) + "."


def compile_analysis_prompt(contract):
    """Compile a scene contract into an atomic quality gate prompt."""
    sc = contract.get("scene_contract", {})
    
    prompt = "Inspect this image strictly against the scene contract. Return JSON only.\n\n"
    
    if sc.get("subject"):
        prompt += f"1. Subject: {sc.get('subject_count', 1)} {sc['subject']} — PASS/FAIL/UNCERTAIN\n"
    
    if sc.get("required_objects"):
        for obj in sc["required_objects"]:
            prompt += f"2. Object '{obj}' visible — PASS/FAIL/UNCERTAIN\n"
    
    if sc.get("action"):
        action = sc["action"]
        prompt += f"3. Action '{action.get('verb')}' with '{action.get('tool')}' on '{action.get('target')}' — PASS/FAIL/UNCERTAIN\n"
        if action.get("required_relation"):
            prompt += f"4. Relation: {action['required_relation']} — PASS/FAIL/UNCERTAIN\n"
    
    if sc.get("setting"):
        prompt += f"5. Setting: {sc['setting']} — PASS/FAIL/UNCERTAIN\n"
    
    if sc.get("camera"):
        prompt += f"6. Framing: {sc['camera']} — PASS/FAIL/UNCERTAIN\n"
    
    if sc.get("negative_constraints"):
        for constraint in sc["negative_constraints"]:
            prompt += f"7. No '{constraint}' — PASS/FAIL/UNCERTAIN\n"
    
    prompt += "\nReturn JSON: {check_name: 'PASS'|'FAIL'|'UNCERTAIN', overall: 'PASS'|'REJECT'|'HUMAN_REVIEW', confidence: 0.0-1.0, rejection_reasons: []}"
    
    return prompt
