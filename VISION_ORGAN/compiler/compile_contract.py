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

    # Physique Topography (5-stratum human mapping)
    if sc.get("physique_topography"):
        pt = sc["physique_topography"]
        topo_parts = []
        if pt.get("somatotype"):
            st = pt["somatotype"]
            bf = st.get("estimated_body_fat_pct")
            if bf:
                topo_parts.append(f"{bf}% body fat athletic definition")
            if st.get("vascularity_grade"):
                topo_parts.append(f"grade-{st['vascularity_grade']} vascularity")
            if st.get("muscular_striation_grade"):
                topo_parts.append(f"grade-{st['muscular_striation_grade']} striations")
        if pt.get("skeletal_framework"):
            sk = pt["skeletal_framework"]
            if sk.get("proportion_canon"):
                topo_parts.append(f"{sk['proportion_canon']} proportions")
            if sk.get("biacromial_to_biiliac_ratio"):
                topo_parts.append(f"{sk['biacromial_to_biiliac_ratio']} V-taper ratio")
        if pt.get("muscular_topography"):
            mt = pt["muscular_topography"]
            ant = mt.get("torso_anterior", {})
            if ant.get("pectoralis_major"):
                topo_parts.append(f"pectoralis {ant['pectoralis_major']}")
            if ant.get("rectus_abdominis_quadrants"):
                topo_parts.append(f"abdominals {ant['rectus_abdominis_quadrants']}")
            if ant.get("serratus_anterior_visibility"):
                topo_parts.append(f"serratus {ant['serratus_anterior_visibility']}")
        if pt.get("photometric_micro_topography"):
            pm = pt["photometric_micro_topography"]
            if pm.get("lighting_topography_angle_deg"):
                topo_parts.append(f"raking cross-lighting at {pm['lighting_topography_angle_deg']} deg")
            if pm.get("subsurface_scattering_strength"):
                topo_parts.append("natural dermal subsurface scattering")
        # Stratum S: Somatic State Layer & Reservoir Dynamics
        soma = pt.get("somatic_state") or pt.get("temporal_physiology", {})
        if soma:
            if soma.get("respiration_phase"):
                topo_parts.append(f"respiration {soma['respiration_phase']}")
            if soma.get("weight_distribution"):
                topo_parts.append(f"weight distribution {soma['weight_distribution']}")
            if soma.get("kinetic_tension"):
                topo_parts.append(f"kinetic tension {soma['kinetic_tension']}")
            if soma.get("fatigue_state"):
                topo_parts.append(f"metabolic state {soma['fatigue_state']}")
            if soma.get("emotional_embodiment"):
                topo_parts.append(f"embodied posture {soma['emotional_embodiment']}")
        if topo_parts:
            parts.append("physique topography: " + ", ".join(topo_parts))

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

    if sc.get("physique_topography"):
        prompt += "5. Physique Topography Integrity (skeletal canon, muscle insertions, no floating serratus/ribs, skin continuity) — PASS/FAIL/UNCERTAIN\n"
        prompt += "6. Photometric Lighting & Surface Normal congruence (raking cross-light relief, SSS, no plastic airbrushing) — PASS/FAIL/UNCERTAIN\n"
        prompt += "7. Somatic Embodiment & Reservoir Dynamics (SCAR-VIS-009: grounded center of gravity, kinetic load transfer, apparent respiration, anti-mannequin) — PASS/FAIL/UNCERTAIN\n"
    
    if sc.get("setting"):
        prompt += f"7. Setting: {sc['setting']} — PASS/FAIL/UNCERTAIN\n"
    
    if sc.get("camera"):
        prompt += f"8. Framing: {sc['camera']} — PASS/FAIL/UNCERTAIN\n"
    
    if sc.get("negative_constraints"):
        for constraint in sc["negative_constraints"]:
            prompt += f"9. No '{constraint}' — PASS/FAIL/UNCERTAIN\n"
    
    prompt += "\nReturn JSON: {check_name: 'PASS'|'FAIL'|'UNCERTAIN', overall: 'PASS'|'REJECT'|'HUMAN_REVIEW', confidence: 0.0-1.0, rejection_reasons: []}"
    
    return prompt
