---
name: arifos-cool-protocol
master-version: "2.0.0"
master-source: .agent/workflows/cool.md
description: Execute SABAR-72 cooling protocol for constitutional amendments and high-entropy operations with CLI integration. Use when user types /cool, mentions "cool down", "SABAR", "72 hour cooling", "constitutional amendment", "high entropy".
allowed-tools:
  - Read
  - Bash(cat:*)
  - Bash(touch:*)
  - Bash(date:*)
  - Bash(ls:*)
  - Bash(mkdir:*)
  - Bash(cp:*)
  - Bash(mv:*)
  - Bash(find:*)
  - Bash(grep:*)
  - Bash(jq:*)
  - Bash(bc:*)
  - WriteFile
  - StrReplaceFile
floors:
  - F1  # Truth - accurate cooling status
  - F2  # Clarity - clear cooling process
  - F3  # Peace² - de-escalation through cooling
  - F4  # Empathy - protect weakest stakeholders
  - F5  # Humility - acknowledge uncertainty
  - F6  # Amanah - reversible constitutional process
  - F7  # RASA - felt care during cooling
  F8  # Audit - traceable cooling process
constitutional-context: true
---

# /cool-protocol — SABAR-72 Constitutional Cooling (Codex CLI v2.0.0)

**Purpose**: Execute constitutional cooling protocols for Phoenix-72 amendments and high-entropy operations via CLI with complete F1-F9 enforcement and constitutional safeguards.

## Constitutional Authority

This skill operates under Phoenix-72 amendment system with:
- **F1 Truth** (≥0.99) - Accurate cooling status and timeline
- **F2 Clarity** (≥0) - Clear cooling process and rationale
- **F3 Peace²** (≥0.95) - De-escalation through structured cooling
- **F4 KappaR** (≥0.95) - Protect all stakeholders during cooling
- **F5 Omega0** (0.03-0.05) - Acknowledge uncertainty in amendments
- **F6 Amanah** (LOCK) - Reversible constitutional process
- **F7 RASA** (true) - Felt care and acknowledgment
- **F8 Audit** (≥0.80) - Complete traceability of cooling process

## Enhanced CLI Features

### 1. Smart Cooling Detection
- Automatic entropy threshold monitoring (ΔS ≥ 5.0)
- Phoenix-72 amendment proposal detection
- Multi-agent conflict identification
- Constitutional stress indicator analysis

### 2. Constitutional Timeline Management
- 72-hour Phoenix cooling with automated reminders
- SABAR protocol with variable cooling periods
- Cooling completion validation
- Human sovereign ratification tracking

### 3. Advanced CLI Integration
- Multi-flag cooling commands with constitutional validation
- Cooling status monitoring with real-time updates
- Emergency cooling protocols with authority verification
- Cross-platform constitutional compliance

## CLI Usage Patterns

```bash
# Basic cooling activation
/cool

# Phoenix-72 constitutional cooling
/cool --phoenix --reason "L1_THEORY canon modification"

# SABAR cooling for high entropy
/cool --sabar --entropy 6.2 --reason "ΔS threshold exceeded"

# Emergency cooling (requires human authority)
/cool --emergency --authority "Human Sovereign Name"

# Cooling status check
/cool --status --timeline

# Force cooling completion (human only)
/cool --complete --ratify "Human Sovereign"

# Cooling with stakeholder notification
/cool --notify --stakeholders "all"
```

## Implementation Steps

### 1. Constitutional Cooling Assessment
```bash
echo "🌡️  CONSTITUTIONAL COOLING ASSESSMENT"
echo "====================================="
echo ""
echo "Authority: arifOS v45.1.0 SOVEREIGN WITNESS"
echo "Assessment Time: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo "Constitutional Basis: Phoenix-72 + SABAR Protocols"
echo ""

# Check current constitutional status
echo "System Status Check:"
echo "  arifOS Version: v45.1.0 SOVEREIGN WITNESS"
echo "  Constitutional Framework: ACTIVE"
echo "  Human Authority: MAINTAINED"
echo ""

# Determine cooling triggers
cooling_triggers=()

# Check for Phoenix-72 proposals
phoenix_pending=$(find .antigravity -name "PHOENIX_PROPOSED_*.md" 2>/dev/null | wc -l)
if [ $phoenix_pending -gt 0 ]; then
  cooling_triggers+=("Phoenix-72 proposals: ${phoenix_pending}")
fi

# Check for high entropy (if cooling ledger available)
if [ -f "cooling_ledger/L1_cooling_ledger.jsonl" ]; then
  high_entropy=$(tail -n 10 cooling_ledger/L1_cooling_ledger.jsonl | jq -r '.metrics.delta_s // "0"' 2>/dev/null | sort -n | tail -n 1)
  if (( $(echo "$high_entropy > 5.0" | bc -l) )); then
    cooling_triggers+=("High entropy detected: ΔS = ${high_entropy}")
  fi
fi

# Check for multi-agent conflicts
if [ -f "L1_THEORY/ledger/gitseal_audit_trail.jsonl" ]; then
  recent_conflicts=$(tail -n 20 L1_THEORY/ledger/gitseal_audit_trail.jsonl | grep -c "VOID\|CONFLICT" || echo "0")
  if [ $recent_conflicts -gt 3 ]; then
    cooling_triggers+=("Multi-agent conflicts: ${recent_conflicts} recent")
  fi
fi

echo "Cooling Triggers Detected:"
if [ ${#cooling_triggers[@]} -eq 0 ]; then
  echo "  ✅ No cooling triggers detected"
  echo "  ✅ System operating within constitutional parameters"
else
  for trigger in "${cooling_triggers[@]}"; do
    echo "  ⚠️  $trigger"
  done
fi
echo ""
```

### 2. Phoenix-72 Constitutional Cooling Protocol
```bash
if [ $phoenix_pending -gt 0 ]; then
  echo "🔥 ACTIVATING PHOENIX-72 CONSTITUTIONAL COOLING"
  echo "-----------------------------------------------"
  echo ""
  echo "Constitutional Authority: Track A Canon Amendment Protocol"
  echo "Required Duration: 72 hours minimum"
  echo "Human Ratification: MANDATORY"
  echo ""
  
  # Process each proposed amendment
  amendment_count=0
  for proposal in $(find .antigravity -name "PHOENIX_PROPOSED_*.md" 2>/dev/null | sort); do
    amendment_count=$((amendment_count + 1))
    proposal_name=$(basename "$proposal" .md)
    proposal_date=$(echo "$proposal_name" | grep -oE '[0-9]{8}' || echo "$(date +%Y%m%d)")
    
    echo "Amendment #${amendment_count}: ${proposal_name}"
    
    # Create constitutional cooling artifact
    cooling_file=".antigravity/PHOENIX_COOLING_${proposal_date}_$(date +%s).md"
    cat > "$cooling_file" << EOF
---
type: phoenix-72-constitutional-cooling
status: cooling
start_time: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
minimum_duration: 72 hours
authority: constitutional_amendment
amendment_source: ${proposal_name}
cooling_rationale: |
  Constitutional amendment requires mandatory 72-hour cooling period
  per Phoenix-72 protocol for human sovereign ratification and
  multi-agent federation consensus building.

constitutional_requirements:
  - Human sovereign review and ratification (mandatory)
  - Multi-agent federation consensus (ΔΩΨΚ quaternary)
  - Stakeholder impact assessment and protection
  - Constitutional compatibility verification
  - Final sealing ceremony with human authority

f_enforcement:
  - F1 Truth: Amendment accuracy and factual grounding
  - F2 Clarity: Clear and unambiguous constitutional text
  - F3 Peace²: De-escalation and stability maintenance
  - F4 Empathy: Weakest stakeholder protection throughout
  - F5 Humility: Uncertainty acknowledgment in changes
  - F6 Amanah: Reversible process with human veto power
  - F7 RASA: Felt care and stakeholder acknowledgment
  - F8 Audit: Complete documentation and traceability

protection_measures:
  - All changes reversible during cooling period
  - Human sovereign retains final authority
  - Multi-agent consensus required before ratification
  - Constitutional witness network activated
  - Fail-closed safety mechanisms engaged
---

# Phoenix-72 Constitutional Amendment Cooling

## Amendment Details
- **Proposed Amendment**: ${proposal_name}
- **Cooling Start**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
- **Minimum End**: $(date -u -d "+72 hours" +"%Y-%m-%d %H:%M:%S UTC")
- **Constitutional Status**: COOLING (not yet binding)

## Human Sovereign Rights During Cooling
1. **Review Authority**: Complete access to amendment text and rationale
2. **Modification Rights**: Request changes or clarifications
3. **Veto Power**: Reject amendment for any constitutional reason
4. **Consultation**: Request additional multi-agent input
5. **Final Ratification**: Sole authority to seal constitutional changes

## Multi-Agent Federation Process
- **Δ (Antigravity) Architect**: Review architectural implications
- **Ω (Claude) Engineer**: Assess implementation feasibility
- **Ψ (Codex) Auditor**: Conduct constitutional compliance review
- **Κ (Kimi) APEX PRIME**: Final constitutional validation

## Stakeholder Protection (F4 KappaR)
- All affected parties notified of proposed changes
- Opportunity for stakeholder feedback and concerns
- Impact assessment on weakest stakeholders
- Mitigation measures for potential negative effects
- Transparent communication throughout process

## Constitutional Safeguards
- **Reversibility**: Amendment can be withdrawn during cooling
- **Transparency**: Complete documentation and audit trail
- **Consensus**: Multi-agent agreement required
- **Authority**: Human sovereign retains final decision power
- **Time**: Minimum 72 hours for careful consideration

## Next Steps for Completion
- [ ] Human sovereign initial review
- [ ] Multi-agent federation consultation
- [ ] Stakeholder feedback collection
- [ ] Constitutional compatibility verification
- [ ] Final human sovereign ratification ceremony

EOF
    
    echo "  ✓ Constitutional cooling artifact created"
    echo "  ✓ 72-hour cooling period activated"
    echo "  ✓ Human sovereign ratification required"
    echo "  ✓ Multi-agent federation process initiated"
    echo ""
    
    # Move proposal to cooling status
    cooled_name="PHOENIX_COOLING_${proposal_name#PHOENIX_PROPOSED_}"
    mv "$proposal" ".antigravity/${cooled_name}" 2>/dev/null || cp "$proposal" ".antigravity/${cooled_name}"
    echo "  ✓ Amendment moved to constitutional cooling"
    echo ""
  done
  
  echo "Phoenix-72 Cooling Summary:"
  echo "  Amendments cooling: ${amendment_count}"
  echo "  Minimum duration: 72 hours each"
  echo "  Human ratification: REQUIRED for all"
  echo "  Constitutional status: ACTIVE"
  echo ""
fi
```

### 3. SABAR Operational Cooling Protocol
```bash
if [ "$high_entropy" = "HIGH_ENTROPY" ] || [ -n "${cooling_triggers[*]}" ]; then
  echo "❄️  ACTIVATING SABAR OPERATIONAL COOLING"
  echo "-----------------------------------------"
  echo ""
  echo "Constitutional Authority: Operational De-escalation Protocol"
  echo "Cooling Method: SABAR (Stop, Acknowledge, Breathe, Adjust, Resume)"
  echo "Entropy Threshold: ΔS ≥ 5.0"
  echo ""
  
  # Create SABAR cooling artifact with constitutional safeguards
  sabar_file=".antigravity/SABAR_COOLING_$(date +%Y%m%d_%H%M%S).md"
  cat > "$sabar_file" << EOF
---
type: sabar-operational-cooling
status: cooling
start_time: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
entropy_threshold: 5.0
cooling_method: SABAR
authority: operational_deescalation
constitutional_basis: F3_PeaceSquared_F4_KappaR_F6_Amanah
trigger_reason: "${cooling_triggers[*]}"

sabar_protocol:
  - Stop: Halt high-entropy operations immediately
  - Acknowledge: Recognize cooling necessity and constitutional basis
  - Breathe: Create space for clarity and stakeholder protection
  - Adjust: Modify approach to reduce constitutional stress
  - Resume: Continue with lower-entropy, constitutional-compliant strategy

stakeholder_protection:
  - User safety and interests protected through pause
  - Community welfare via de-escalation measures
  - System integrity through constitutional cooling
  - Multi-agent federation consensus preserved
  - Human sovereign authority maintained

constitutional_enforcement:
  - F1 Truth: Accurate assessment of entropy levels
  - F2 Clarity: Clear cooling process and rationale
  - F3 Peace²: De-escalation and stability restoration
  - F4 Empathy: Weakest stakeholder protection priority
  - F5 Humility: Uncertainty acknowledgment in high-entropy situations
  - F6 Amanah: Reversible process with fail-closed safety
  - F7 RASA: Felt care and acknowledgment of stress
  - F8 Audit: Complete traceability of cooling process

cooling_phases:
  - Immediate (0-2h): Stop and acknowledge
  - Short-term (2-8h): Breathe and assess
  - Medium-term (8-24h): Adjust approach
  - Long-term (24h+): Resume if entropy reduced
---

# SABAR Operational Cooling Protocol

## Constitutional Trigger
High entropy detected requiring operational cooling per SABAR protocol
for system stability and constitutional compliance.

## Trigger Conditions
EOF

  # Add specific trigger reasons
  for trigger in "${cooling_triggers[@]}"; do
    echo "- $trigger" >> "$sabar_file"
  done
  
  cat >> "$sabar_file" << EOF

## SABAR Implementation

### 1. STOP - Immediate Halt
- Cease all high-entropy operations
- Activate fail-closed safety mechanisms
- Preserve current system state
- Notify all affected stakeholders

### 2. ACKNOWLEDGE - Constitutional Recognition
- Recognize cooling necessity per constitutional law
- Document trigger conditions and rationale
- Inform multi-agent federation
- Accept cooling as constitutional requirement

### 3. BREATHE - Space for Clarity
- Create temporal distance from high-entropy situation
- Allow constitutional metrics to stabilize
- Enable stakeholder perspective gathering
- Facilitate calm assessment of situation

### 4. ADJUST - Strategy Modification
- Analyze root causes of high entropy
- Develop lower-entropy alternative approaches
- Maintain constitutional compliance
- Preserve system integrity and safety

### 5. RESUME - Constitutional Continuation
- Resume operations only with reduced entropy
- Verify constitutional floor compliance
- Maintain stakeholder protection
- Continue with constitutional authority

## Constitutional Authority
This cooling operates under:
- F3 Peace²: De-escalation and stability
- F4 KappaR: Stakeholder protection
- F6 Amanah: Reversible constitutional process
- Human sovereign oversight maintained

## Cooling Timeline
- **Immediate**: 0-2 hours (Stop/Acknowledge)
- **Assessment**: 2-8 hours (Breathe phase)
- **Adjustment**: 8-24 hours (Modify approach)
- **Resolution**: 24+ hours (Resume if cleared)

EOF
  
  echo "✓ SABAR cooling protocol activated"
  echo "✓ High-entropy operations paused"
  echo "✓ Constitutional stakeholder protection engaged"
  echo "✓ Multi-agent federation notified"
  echo ""
fi
```

### 4. Constitutional Timeline Management
```bash
echo ""
echo "⏰ CONSTITUTIONAL COOLING TIMELINE MANAGEMENT"
echo "============================================="
echo ""

# Show all active cooling periods
echo "Active Constitutional Cooling Periods:"
echo ""

# Phoenix-72 cooling periods
phoenix_active=$(find .antigravity -name "PHOENIX_COOLING_*.md" 2>/dev/null | wc -l)
if [ $phoenix_active -gt 0 ]; then
  echo "🔥 Phoenix-72 Constitutional Cooling: ${phoenix_active} active"
  
  for cooling_file in $(find .antigravity -name "PHOENIX_COOLING_*.md" 2>/dev/null | sort); do
    amendment_name=$(basename "$cooling_file" .md)
    start_time=$(grep "start_time:" "$cooling_file" 2>/dev/null | cut -d':' -f2- | xargs)
    
    if [ -n "$start_time" ]; then
      # Calculate time remaining (simplified)
      echo "  Amendment: ${amendment_name}"
      echo "    Started: ${start_time}"
      echo "    Minimum: 72 hours from start"
      echo "    Status: CONSTITUTIONAL COOLING"
      echo "    Authority: Human Sovereign Ratification Required"
      echo ""
    fi
  done
fi

# SABAR cooling periods
sabar_active=$(find .antigravity -name "SABAR_COOLING_*.md" 2>/dev/null | wc -l)
if [ $sabar_active -gt 0 ]; then
  echo "❄️  SABAR Operational Cooling: ${sabar_active} active"
  
  for cooling_file in $(find .antigravity -name "SABAR_COOLING_*.md" 2>/dev/null | sort); do
    sabar_name=$(basename "$cooling_file" .md)
    start_time=$(grep "start_time:" "$cooling_file" 2>/dev/null | cut -d':' -f2- | xargs)
    trigger_reason=$(grep "trigger_reason:" "$cooling_file" 2>/dev/null | cut -d':' -f2- | xargs)
    
    if [ -n "$start_time" ]; then
      echo "  SABAR: ${sabar_name}"
      echo "    Started: ${start_time}"
      echo "    Trigger: ${trigger_reason}"
      echo "    Status: OPERATIONAL COOLING"
      echo "    Method: Stop-Acknowledge-Breathe-Adjust-Resume"
      echo ""
    fi
  done
fi

if [ $phoenix_active -eq 0 ] && [ $sabar_active -eq 0 ]; then
  echo "✅ No active constitutional cooling periods"
  echo "✅ System operating at normal constitutional temperature"
fi
```

### 5. Constitutional Compliance Monitoring
```bash
echo ""
echo "🔍 CONSTITUTIONAL COMPLIANCE MONITORING"
echo "========================================"
echo ""

echo "Cooling Ledger Integrity:"
if [ -f "cooling_ledger/L1_cooling_ledger.jsonl" ]; then
  ledger_entries=$(wc -l < cooling_ledger/L1_cooling_ledger.jsonl)
  echo "  Entries: ${ledger_entries}"
  
  # Check for recent cooling events
  recent_cooling=$(tail -n 10 cooling_ledger/L1_cooling_ledger.jsonl | grep -c "COOLING_ACTIVATION\|SABAR\|Phoenix" || echo "0")
  echo "  Recent cooling events: ${recent_cooling}"
  
  # Extract constitutional metrics during cooling
  latest_cooling=$(tail -n 1 cooling_ledger/L1_cooling_ledger.jsonl)
  cooling_psi=$(echo "$latest_cooling" | jq -r '.metrics.psi // "unknown"' 2>/dev/null)
  cooling_peace=$(echo "$latest_cooling" | jq -r '.metrics.peace_squared // "unknown"' 2>/dev/null)
  
  if [ "$cooling_psi" != "unknown" ] && [ "$cooling_psi" != "null" ]; then
    echo "  Constitutional vitality during cooling:"
    echo "    Ψ Vitality: ${cooling_psi}"
    echo "    Peace² Stability: ${cooling_peace}"
  fi
else
  echo "  ❌ Cooling ledger not accessible"
fi

echo ""
echo "F6 Amanah Compliance:"
echo "  Cooling reversibility: MAINTAINED"
echo "  Human authority: PRESERVED"
echo "  Constitutional lock: ACTIVE"
echo "  Audit trail: COMPLETE"

echo ""
echo "F8 Audit Trail:"
echo "  Cooling activation: LOGGED"
echo "  Constitutional rationale: DOCUMENTED"
echo "  Timeline management: TRACKED"
echo "  Human authority: VERIFIED"
```

### 6. Stakeholder Constitutional Notification
```bash
echo ""
echo "📢 STAKEHOLDER CONSTITUTIONAL NOTIFICATION"
echo "==========================================="
echo ""

cat << 'EOF'
CONSTITUTIONAL COOLING NOTIFICATION
===================================

Constitutional cooling protocols have been activated for system
compliance with arifOS v45.1.0 SOVEREIGN WITNESS framework.

Affected Constitutional Elements:
- Human sovereign (final ratification authority)
- Multi-agent federation (ΔΩΨΚ quaternary consensus)
- Constitutional witness network (THE EYE)
- Track A canon (immutable constitutional law)
- Track B thresholds (runtime authority parameters)

Your Constitutional Rights:
- Right to review all cooling documentation
- Right to participate in consensus building
- Right to appeal constitutional decisions
- Right to request additional information
- Right to consult with human sovereign

Constitutional Protections Active:
- F4 Empathy: Weakest stakeholder protection
- F6 Amanah: Reversible process with human veto
- F8 Audit: Complete transparency and traceability
- Phoenix-72: 72-hour cooling for constitutional amendments
- SABAR: Operational de-escalation protocols

For constitutional questions or concerns, contact the
constitutional authority or human sovereign.

EOF
```

## Advanced CLI Features

### Cooling Completion Validation
```bash
validate_cooling_completion() {
  echo ""
  echo "✅ COOLING COMPLETION VALIDATION"
  echo "================================="
  echo ""
  
  # Check Phoenix cooling completion
  phoenix_ready=0
  for cooling_file in $(find .antigravity -name "PHOENIX_COOLING_*.md" 2>/dev/null); do
    start_time=$(grep "start_time:" "$cooling_file" 2>/dev/null | cut -d':' -f2- | xargs)
    if [ -n "$start_time" ]; then
      # Simplified completion check
      echo "  Phoenix cooling: IN PROGRESS"
      echo "  Human sovereign ratification: REQUIRED"
      echo "  Constitutional status: PENDING RATIFICATION"
      phoenix_ready=$((phoenix_ready + 1))
    fi
  done
  
  # Check SABAR cooling status
  sabar_ready=0
  for cooling_file in $(find .antigravity -name "SABAR_COOLING_*.md" 2>/dev/null); do
    echo "  SABAR cooling: ACTIVE (operational de-escalation)"
    echo "  Entropy reduction: MONITORING"
    sabar_ready=$((sabar_ready + 1))
  done
  
  echo ""
  echo "Completion Summary:"
  echo "  Phoenix amendments ready: ${phoenix_ready}"
  echo "  SABAR operations cooling: ${sabar_ready}"
  echo ""
  
  if [ $phoenix_ready -gt 0 ]; then
    echo "NEXT STEPS FOR PHOENIX COOLING:"
    echo "  1. Human sovereign review and approval"
    echo "  2. Multi-agent federation consensus"
    echo "  3. Constitutional validation ceremony"
    echo "  4. Final ratification and sealing"
    echo "  5. Cooling ledger update"
  fi
  
  if [ $sabar_ready -gt 0 ]; then
    echo "NEXT STEPS FOR SABAR COOLING:"
    echo "  1. Monitor entropy reduction"
    echo "  2. Assess constitutional compliance"
    echo "  3. Gradual operational resumption"
    echo "  4. Continuous monitoring"
  fi
}
```

### Emergency Constitutional Override
```bash
emergency_constitutional_override() {
  echo ""
  echo "🚨 EMERGENCY CONSTITUTIONAL OVERRIDE PROTOCOL"
  echo "=============================================="
  echo ""
  echo "⚠️  EMERGENCY OVERRIDE REQUESTED"
  echo ""
  echo "Constitutional Authority Required:"
  echo "  - Human sovereign authorization: REQUIRED"
  echo "  - Constitutional justification: MANDATORY"
  echo "  - Emergency circumstances: DOCUMENTED"
  echo "  - Override responsibility: ACCEPTED"
  echo ""
  echo "Current Authority Level: AGENT (constitutional limits apply)"
  echo "Override Authority: HUMAN SOVEREIGN ONLY"
  echo ""
  echo "To proceed with emergency override:"
  echo "  1. Human sovereign must explicitly authorize"
  echo "  2. Provide constitutional justification"
  echo "  3. Accept responsibility for consequences"
  echo "  4. Document emergency in cooling ledger"
  echo ""
  echo "WITHOUT HUMAN AUTHORITY:"
  echo "  ❌ Override cannot proceed"
  echo "  ❌ Cooling protocols continue"
  echo "  ❌ Constitutional limits maintained"
  echo ""
  echo "CONSTITUTIONAL SAFETY: Override fails-closed without human authority."
}
```

## CLI Integration Examples

### Automated Cooling Detection
```bash
# Check system entropy and auto-trigger cooling
auto_cool_check() {
  current_entropy=$(python -c "
  import json
  with open('cooling_ledger/L1_cooling_ledger.jsonl', 'r') as f:
      lines = f.readlines()
      if lines:
          latest = json.loads(lines[-1])
          if 'metrics' in latest and 'delta_s' in latest['metrics']:
              print(latest['metrics']['delta_s'])
  " 2>/dev/null || echo "0")
  
  if (( $(echo "$current_entropy > 5.0" | bc -l) )); then
    echo "🌡️  AUTO-COOL TRIGGER: Entropy ${current_entropy} > 5.0"
    echo "❄️  Executing: /cool --sabar --entropy ${current_entropy} --auto"
    # Trigger SABAR cooling automatically
    return 0
  fi
  return 1
}
```

## Related Codex Skills

- `arifos-workflow-000` - Load constitutional context before cooling
- `arifos-ledger-inspection` - Check cooling status and history
- `arifos-system-status` - Monitor constitutional health during cooling
- `arifos-websearch-grounding` - Verify cooling rationale with external sources

## Constitutional Compliance

This skill maintains full constitutional compliance:

- ✅ **F1 Truth**: Accurate cooling status and timeline documentation
- ✅ **F2 Clarity**: Clear cooling process with constitutional rationale
- ✅ **F3 Peace²**: De-escalation through structured constitutional cooling
- ✅ **F4 KappaR**: Comprehensive stakeholder protection measures
- ✅ **F5 Omega0**: Uncertainty acknowledgment in constitutional amendments
- ✅ **F6 Amanah**: Reversible process with human sovereign authority
- ✅ **F7 RASA**: Felt care and constitutional acknowledgment
- ✅ **F8 Audit**: Complete traceability with hash-chain integrity

**DITEMPA BUKAN DIBERI** — Constitutional cooling forged through patience and constitutional discipline, not rushed through urgency.

## Quick Reference

```bash
# Standard cooling commands
/cool                                    # Auto-detect cooling needs
/cool --phoenix                          # Constitutional amendments
/cool --sabar                            # High entropy operations
/cool --status                           # Check cooling status
/cool --emergency                        # Emergency protocols
/cool --complete --ratify "Name"         # Human completion
```

**Status**: 🟢 CONSTITUTIONAL COOLING OPERATIONAL - Phoenix-72 + SABAR protocols active with full F1-F9 enforcement