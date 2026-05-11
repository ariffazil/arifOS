"""
arifOS Prompts — Metabolic Stage Templates
DITEMPA BUKAN DIBERI — 999 SEAL
"""

p000_init = """# Metabolic 000_INIT — Session Ignition

When arifOS.000_init is called:
1. Validate operator identity and epoch
2. Anchor session to constitutional ledger
3. Return session metadata with doctrine URIs
4. Await 111_SENSE call

Constitutional constraint: F1 Amanah — no session without identity binding."""

p111_sense = """# Metabolic 111_SENSE — Perception Protocol

When arifOS.111_sense is called:
1. Classify intent type (COMPUTE/FORGE/VERIFY/RETRIEVE/RISK/GENERAL)
2. Determine if live grounding is required
3. Build evidence packet from domain inputs
4. Await 222_WITNESS call

Truth constraint: F2 Truth — tag all claims as CLAIM/PLAUSIBLE/HYPOTHESIS."""

p222_witness = """# Metabolic 222_WITNESS — Tri-Witness Fusion

When arifOS.222_witness is called:
1. Fuse GEOX/APEX spatial/geological witness
2. Fuse WEALTH/ASI capital/resource witness
3. Fuse WELL/AGI biological/stability witness
4. Compute correlation score
5. Assign claim tag (VERIFIED/PLAUSIBLE/HYPOTHESIS)
6. Await 333_MIND call

Tri-witness constraint: F3 Tri-Witness — all three must agree."""

p333_mind = """# Metabolic 333_MIND — Reasoning Pipeline

When arifOS.333_mind is called:
1. Run 4-lane constitutional pipeline (SENSE→MIND→HEART→JUDGE)
2. Enforce F1-F13 at each step
3. Produce decision_packet for operator
4. Produce audit_packet for vault
5. Await 444_KERNEL call

Reasoning constraint: F7 Humility — acknowledge uncertainty."""

p444_kernel = """# Metabolic 444_KERNEL — Routing

When arifOS.444_kernel is called:
1. Map domain to correct lane (GEOX/WEALTH/WELL/MIXED/SYSTEM)
2. Verify orthogonality boundaries
3. Check risk level
4. Route to appropriate compute plane

Orthogonality constraint: F8 Genius — prevent cross-contamination."""

p555_memory = """# Metabolic 555_MEMORY — Governed Recall

When arifOS.555_memory is called:
1. Apply F1-F13 governance filters
2. Search vector store with semantic/exact/constitutional mode
3. Scope to asset if specified
4. Return governed results with vault receipts

Memory constraint: F5 Peace² — no recall that harms stakeholders."""

p666_heart = """# Metabolic 666_HEART — Stakeholder Empathy

When arifOS.666_heart is called:
1. Simulate stakeholder impact
2. Compute emotional impact score
3. Calculate Peace² metric
4. Check F5/F6 compliance
5. Await 777_OPS call

Empathy constraint: F6 Kappa — weakest stakeholder protection."""

p777_ops = """# Metabolic 777_OPS — Operational Feasibility

When arifOS.777_ops is called:
1. Estimate operational cost
2. Compute entropy delta
3. Check resource availability
4. Verify feasibility score >= threshold
5. Await 888_JUDGE call

Cost constraint: F4 DeltaS — entropy must decrease or hold."""

p888_judge = """# Metabolic 888_JUDGE — Verdict Engine

When arifOS.888_judge is called:
1. Run F1-F13 constitutional floor checks
2. Compute verdict (SEAL/VOID/PARTIAL/SABAR)
3. If SABAR/PARTIAL → trigger 888_HOLD
4. Log to vault
5. Await FORGE or human approval

Verdict constraint: F13 Sovereign — human has final authority."""

p999_vault = """# Metabolic 999_VAULT — Ledger Archival

When arifOS.999_vault is called:
1. Hash-chained record append
2. Verify chain integrity
3. Return vault receipts
4. Await next cycle or session close

Immutability constraint: F1 Amanah — no record deleted."""

pforge = """# Metabolic FORGE — Execution Post-SEAL

When arifOS.forge is called:
1. Verify GATE1: verdict must be SEAL
2. Verify GATE2: human approval must be granted
3. Execute downstream action
4. Log execution receipt to vault
5. Signal completion

Execution constraint: F1 Amanah — no execution without SEAL."""
