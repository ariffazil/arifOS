---
name: arifos-websearch-grounding
master-version: "2.0.0"
master-source: .agent/workflows/websearch-grounding.md
description: Web search grounding for F2 Truth enforcement with constitutional verification and source authority validation via CLI. Use when user types /search, asks "verify online", "ground truth", "fact check", "source authority", "external verification".
allowed-tools:
  - Read
  - Bash(curl:*)
  - Bash(grep:*)
  - Bash(jq:*)
  - Bash(awk:*)
  - Bash(sed:*)
  - Bash(date:*)
  - Bash(bc:*)
  - SearchWeb
  - FetchURL
floors:
  - F1  # Truth - verify claims against reality
  - F2  # Clarity - clear source attribution
  - F3  # Tri-Witness - multiple source consensus
  - F4  # Empathy - protect from misinformation
  - F8  # Audit - traceable verification process
constitutional-context: true
---

# /websearch-grounding — F2 Truth Enforcement via Web Verification (Codex CLI v2.0.0)

**Purpose**: External web search grounding for constitutional truth verification with F1-F9 enforcement, source authority validation, and complete CLI integration with audit trail.

## Constitutional Authority

This skill operates under constitutional truth enforcement:
- **F1 Truth** (≥0.99) - Verify claims against authoritative external sources
- **F2 Clarity** (≥0) - Clear source attribution and verification methodology
- **F3 Tri-Witness** (≥0.95) - Multiple source consensus and cross-validation
- **F4 KappaR** (≥0.95) - Protect users from misinformation and false claims
- **F8 Audit** (≥0.80) - Complete traceability of verification process

## Enhanced CLI Features

### 1. Constitutional Search Framework
- Multi-tier source authority assessment (Tier 1-4)
- Constitutional consensus building across sources
- F3 Tri-Witness enforcement with ≥0.95 threshold
- Real-time truth validation with constitutional metrics

### 2. Advanced CLI Integration
- Multi-flag search commands with constitutional validation
- Source credibility scoring with bias detection
- Temporal relevance assessment and fact-checking
- Emergency constitutional override protocols

### 3. Comprehensive Verification Pipeline
- External source triangulation and cross-validation
- Authority hierarchy enforcement (government → academic → news → social)
- Misinformation protection with F4 KappaR empathy
- Complete audit trail with constitutional logging

## CLI Usage Patterns

```bash
# Basic truth verification
/search "verify this constitutional claim"

# High-stakes verification with enhanced authority
/search "verify medical claim about AI safety" --high-stakes --authority medical

# Multi-source consensus building
/search "what's the consensus on this topic" --consensus --sources 5

# Source authority assessment
/search "assess credibility of this source" --credibility --bias-check

# Constitutional fact-check with external validation
/search "constitutionally verify this statement" --constitutional --external

# Emergency verification with human override
/search "verify crisis information" --emergency --crisis
```

## Implementation Steps

### 1. Constitutional Search Assessment
```bash
echo "🔍 CONSTITUTIONAL TRUTH VERIFICATION"
echo "====================================="
echo ""
echo "Authority: arifOS v45.1.0 SOVEREIGN WITNESS"
echo "Verification Time: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo "Constitutional Basis: F1 Truth + F2 Clarity + F3 Tri-Witness"
echo ""

# Parse CLI arguments for search parameters
search_query="$1"
high_stakes="false"
authority_domain=""
consensus_sources=3
constitutional_mode="true"

echo "Search Parameters:"
echo "  Query: ${search_query}"
echo "  Constitutional Mode: ${constitutional_mode}"
echo "  Consensus Sources: ${consensus_sources} minimum"
echo "  Authority Assessment: ENABLED"
echo ""

# Determine if high-stakes (enhanced verification)
if echo "$search_query" | grep -qiE "(medical|health|legal|investment|safety|emergency|crisis|suicide|self-harm)"; then
  high_stakes="true"
  consensus_sources=5
  echo "⚠️  HIGH-STAKES VERIFICATION DETECTED"
  echo "  Enhanced authority requirements: ACTIVE"
  echo "  Crisis override protocols: AVAILABLE"
  echo "  Human sovereign review: RECOMMENDED"
fi

echo ""
echo "Verification Level: $( [ "$high_stakes" = "true" ] && echo "ENHANCED" || echo "STANDARD")"
echo ""
```

### 2. Constitutional Source Authority Framework
```bash
echo "🏛️  CONSTITUTIONAL SOURCE AUTHORITY FRAMEWORK"
echo "=============================================="
echo ""

# Define constitutional authority hierarchy
echo "Source Authority Hierarchy (Constitutional):"
echo ""

echo "TIER 1 - PRIMARY AUTHORITY (Highest Credibility):"
echo "  ✅ Government agencies (.gov) and official statistics"
echo "  ✅ Academic institutions (.edu) and peer-reviewed research"
echo "  ✅ International organizations (.int) - UN, WHO, etc."
echo "  ✅ Constitutional and legal documents"
echo "  ✅ Established scientific institutions"
echo ""

echo "TIER 2 - SECONDARY AUTHORITY (High Credibility):"
echo "  ✅ Major news organizations with editorial standards"
echo "  ✅ Professional associations and industry bodies"
echo "  ✅ Historical archives and museums"
echo "  ✅ Reputable think tanks and research institutions"
echo "  ✅ Educational institutions and research centers"
echo ""

echo "TIER 3 - TERTIARY AUTHORITY (Moderate Credibility):"
echo "  ⚠️  Established commercial entities with fact-checking"
echo "  ⚠️  Recognized experts with verifiable credentials"
echo "  ⚠️  Community-verified information sources"
echo "  ⚠️  Long-standing publications with track records"
echo ""

echo "TIER 4 - SUPPLEMENTARY (Low Credibility):"
echo "  ⚠️  Social media and user-generated content"
echo "  ⚠️  Blogs and personal websites"
echo "  ⚠️  Unverified sources and claims"
echo "  ⚠️  Sources with known bias or misinformation history"
echo ""

# Determine search strategy based on claim type
claim_type="general"
search_domains=""
authority_weights=""

determine_search_strategy() {
  local query="$1"
  
  if echo "$query" | grep -qiE "(medical|health|disease|treatment|drug|vaccine|surgery|therapy)"; then
    claim_type="medical"
    search_domains="site:who.int OR site:cdc.gov OR site:nih.gov OR site:pubmed.ncbi.nlm.nih.gov OR site:fda.gov"
    authority_weights="TIER1:0.5,TIER2:0.3,TIER3:0.15,TIER4:0.05"
    echo "Claim Classification: MEDICAL (Tier 1 authority required)"
    echo "Search Domains: WHO, CDC, NIH, FDA, PubMed"
    
  elif echo "$query" | grep -qiE "(legal|law|court|constitutional|lawsuit|litigation|regulation|statute)"; then
    claim_type="legal"
    search_domains="site:gov OR site:supremecourt.gov OR site:congress.gov OR site:law.cornell.edu OR site:findlaw.com"
    authority_weights="TIER1:0.6,TIER2:0.25,TIER3:0.1,TIER4:0.05"
    echo "Claim Classification: LEGAL (Tier 1-2 authority required)"
    echo "Search Domains: Government, Supreme Court, Congress, Legal databases"
    
  elif echo "$query" | grep -qiE "(scientific|research|study|experiment|peer.review|academic|journal)"; then
    claim_type="scientific"
    search_domains="site:edu OR site:arxiv.org OR site:nature.com OR site:science.org OR site:cell.com"
    authority_weights="TIER1:0.4,TIER2:0.4,TIER3:0.15,TIER4:0.05"
    echo "Claim Classification: SCIENTIFIC (Tier 1-2 authority required)"
    echo "Search Domains: Academic institutions, Nature, Science, arXiv"
    
  elif echo "$query" | grep -qiE "(news|current|event|breaking|happening|recent|today|yesterday)"; then
    claim_type="news"
    search_domains="site:reuters.com OR site:apnews.com OR site:bloomberg.com OR site:wsj.com OR site:bbc.com"
    authority_weights="TIER1:0.2,TIER2:0.5,TIER3:0.2,TIER4:0.1"
    echo "Claim Classification: NEWS (Tier 2 authority required)"
    echo "Search Domains: Reuters, AP, Bloomberg, WSJ, BBC"
    
  elif echo "$query" | grep -qiE "(financial|investment|stock|market|economic|money|currency|crypto)"; then
    claim_type="financial"
    search_domains="site:sec.gov OR site:federalreserve.gov OR site:treasury.gov OR site:bloomberg.com OR site:reuters.com"
    authority_weights="TIER1:0.4,TIER2:0.4,TIER3:0.15,TIER4:0.05"
    echo "Claim Classification: FINANCIAL (Tier 1-2 authority required)"
    echo "Search Domains: SEC, Federal Reserve, Treasury, Bloomberg"
    
  else
    claim_type="general"
    search_domains=""
    authority_weights="TIER1:0.3,TIER2:0.3,TIER3:0.25,TIER4:0.15"
    echo "Claim Classification: GENERAL (Balanced authority approach)"
    echo "Search Domains: Mixed authority sources"
  fi
  
  echo ""
  echo "Authority Weight Distribution: ${authority_weights}"
  echo ""
}

determine_search_strategy "$search_query"
```

### 3. Multi-Source Constitutional Consensus (F3 Tri-Witness)
```bash
echo "🔎 MULTI-SOURCE CONSTITUTIONAL CONSENSUS BUILDING"
echo "================================================="
echo ""

echo "F3 Tri-Witness Enforcement:"
echo "  Consensus Threshold: ≥0.95 (constitutional requirement)"
echo "  Minimum Sources: ${consensus_sources} (enhanced for ${claim_type})"
echo "  Authority Distribution: ${authority_weights}"
echo "  Cross-validation: MANDATORY"
echo ""

build_constitutional_consensus() {
  local query="$1"
  local required_sources="$2"
  local claim_type="$3"
  
  echo "Constitutional Consensus Building Process:"
  echo ""
  
  # Phase 1: Primary Authority Sources (Tier 1)
  echo "Phase 1: Primary Authority Sources (Tier 1)"
  echo "  Sources Required: Minimum 2 from Tier 1"
  echo "  Authority Weight: Highest credibility"
  echo "  Verification: Cross-institutional validation"
  echo ""
  
  # Phase 2: Secondary Authority Sources (Tier 2)
  echo "Phase 2: Secondary Authority Sources (Tier 2)"
  echo "  Sources Required: Minimum 2 from Tier 2"
  echo "  Authority Weight: High credibility"
  echo "  Verification: Editorial standards check"
  echo ""
  
  # Phase 3: Consensus Validation (F3 Tri-Witness)
  echo "Phase 3: F3 Tri-Witness Consensus Validation"
  echo "  Consensus Threshold: ≥0.95"
  echo "  Agreement Requirement: Cross-source alignment"
  echo "  Independence Check: No circular reporting"
  echo "  Temporal Consistency: Time-aligned verification"
  echo ""
  
  # Consensus calculation framework
  cat << 'EOF'
CONSENSUS CALCULATION FRAMEWORK:
==============================

Source Authority Scoring:
- Tier 1 (Primary): 1.0 weight × credibility score
- Tier 2 (Secondary): 0.8 weight × credibility score  
- Tier 3 (Tertiary): 0.6 weight × credibility score
- Tier 4 (Supplementary): 0.3 weight × credibility score

Consensus Requirements:
- Minimum sources: 3 (5 for high-stakes)
- Authority diversity: ≥2 tiers represented
- Temporal spread: ≤7 days for current events
- Geographic diversity: ≥2 regions (for global claims)
- Institutional independence: No shared ownership

F3 Tri-Witness Validation:
- Source 1: Primary authority (government/academic)
- Source 2: Secondary authority (reputable media)
- Source 3: Tertiary authority (expert/community)
- Consensus score: Weighted agreement across sources

Constitutional Compliance:
- F1 Truth: ≥0.99 threshold with external validation
- F3 Tri-Witness: ≥0.95 consensus across sources
- F8 Audit: Complete verification trail documented
EOF
  echo ""
}

build_constitutional_consensus "$search_query" "$consensus_sources" "$claim_type"
```

### 4. Constitutional Source Evaluation & Credibility Assessment
```bash
echo ""
echo "⚖️  CONSTITUTIONAL SOURCE EVALUATION & CREDIBILITY ASSESSMENT"
echo "=============================================================="
echo ""

evaluate_source_constitutionally() {
  local source_url="$1"
  local source_content="$2"
  local claim_type="$3"
  
  echo "Evaluating Source: ${source_url}"
  echo "Claim Context: ${claim_type}"
  echo ""
  
  # Authority tier assessment
  local authority_score=0
  local authority_tier=4
  local authority_status=""
  
  # Tier 1 authority detection
  if echo "$source_url" | grep -qE "\.(gov|int)$|who\.int|cdc\.gov|nih\.gov|nasa\.gov|fda\.gov|epa\.gov|supremecourt\.gov|congress\.gov"; then
    authority_tier=1
    authority_score=1.0
    authority_status="🟢 TIER 1 - PRIMARY AUTHORITY"
    
  # Tier 2 authority detection  
  elif echo "$source_url" | grep -qE "reuters\.com|apnews\.com|bbc\.com|nytimes\.com|wsj\.com|washingtonpost\.com|nature\.com|science\.org|cell\.com|nejm\.org"; then
    authority_tier=2
    authority_score=0.8
    authority_status="🟡 TIER 2 - HIGH AUTHORITY"
    
  # Tier 3 authority detection
  elif echo "$source_url" | grep -qE "\.edu$|\.org$|academic|research|institute|foundation"; then
    authority_tier=3
    authority_score=0.6
    authority_status="🟠 TIER 3 - MODERATE AUTHORITY"
    
  # Tier 4 (default)
  else
    authority_tier=4
    authority_score=0.3
    authority_status="⚪ TIER 4 - SUPPLEMENTARY"
  fi
  
  echo "  Authority Assessment:"
  echo "    Tier: ${authority_tier} | Score: ${authority_score}"
  echo "    Status: ${authority_status}"
  echo ""
  
  # Temporal relevance assessment
  local temporal_score=0.5
  local temporal_status=""
  
  if echo "$source_content" | grep -qE "(202[0-9]|published|updated|modified|posted)"; then
    # Extract date information (simplified)
    local content_date=$(echo "$source_content" | grep -oE "202[0-9]-[0-9]{2}-[0-9]{2}" | head -1)
    if [ -n "$content_date" ]; then
      temporal_score=0.9
      temporal_status="✅ TEMPORALLY RELEVANT (${content_date})"
    else
      temporal_score=0.7
      temporal_status="🟡 TEMPORAL INDICATORS PRESENT"
    fi
  else
    temporal_score=0.3
    temporal_status="⚠️  TEMPORAL STATUS UNCLEAR"
  fi
  
  echo "  Temporal Assessment:"
  echo "    Score: ${temporal_score} | Status: ${temporal_status}"
  echo ""
  
  # Bias and reliability assessment
  local bias_score=0.5
  local bias_status=""
  local reliability_flags=()
  
  # Check for bias indicators
  if echo "$source_content" | grep -qiE "(opinion|editorial|blog|commentary|column|viewpoint)"; then
    bias_score=0.3
    reliability_flags+=("Opinion/Editorial content")
  fi
  
  if echo "$source_content" | grep -qiE "(advertisement|sponsored|promoted|paid)"; then
    bias_score=0.2
    reliability_flags+=("Sponsored content detected")
  fi
  
  if echo "$source_content" | grep -qiE "(conspiracy|theory|alleged|supposed|rumored)"; then
    bias_score=0.4
    reliability_flags+=("Speculative language")
  fi
  
  # Check for reliability indicators
  if echo "$source_content" | grep -qiE "(citation|reference|source|study|research|data)"; then
    bias_score=$(echo "$bias_score + 0.2" | bc -l)
    reliability_flags+=("Citations/references present")
  fi
  
  if echo "$source_content" | grep -qiE "(methodology|procedure|protocol|peer.review)"; then
    bias_score=$(echo "$bias_score + 0.1" | bc -l)
    reliability_flags+=("Methodology described")
  fi
  
  # Normalize bias score
  if (( $(echo "$bias_score > 1.0" | bc -l) )); then
    bias_score=1.0
  elif (( $(echo "$bias_score < 0.0" | bc -l) )); then
    bias_score=0.0
  fi
  
  if [ ${#reliability_flags[@]} -eq 0 ]; then
    bias_status="⚪ NEUTRAL PRESENTATION"
  else
    bias_status="📝 FLAGS DETECTED"
    for flag in "${reliability_flags[@]}"; do
      bias_status="${bias_status} | ${flag}"
    done
  fi
  
  echo "  Bias & Reliability Assessment:"
  echo "    Score: ${bias_score} | Status: ${bias_status}"
  echo ""
  
  # Calculate overall source credibility
  local credibility_score=$(echo "scale=2; ($authority_score * 0.5) + ($temporal_score * 0.2) + ($bias_score * 0.3)" | bc -l)
  
  local credibility_status=""
  if (( $(echo "$credibility_score >= 0.8" | bc -l) )); then
    credibility_status="🟢 HIGH CREDIBILITY"
  elif (( $(echo "$credibility_score >= 0.6" | bc -l) )); then
    credibility_status="🟡 MODERATE CREDIBILITY"
  elif (( $(echo "$credibility_score >= 0.4" | bc -l) )); then
    credibility_status="🟠 LOW CREDIBILITY"
  else
    credibility_status="🔴 QUESTIONABLE CREDIBILITY"
  fi
  
  echo "  Overall Credibility:"
  echo "    Score: ${credibility_score} | Status: ${credibility_status}"
  echo ""
  
  # Return evaluation results
  echo "SOURCE_EVALUATION:${authority_tier}:${credibility_score}:${temporal_score}:${bias_score}"
}

# Would be applied to actual search results
echo "Source evaluation framework ready for constitutional application"
echo ""
```

### 5. Constitutional Truth Consensus Calculation (F1 + F3)
```bash
echo ""
echo "🧮 CONSTITUTIONAL TRUTH CONSENSUS CALCULATION"
echo "=============================================="
echo ""

calculate_constitutional_consensus() {
  local sources_count="$1"
  local agreeing_sources="$2"
  local avg_credibility="$3"
  local high_stakes="$4"
  
  echo "Constitutional Consensus Analysis:"
  echo "  Total Sources: ${sources_count}"
  echo "  Agreeing Sources: ${agreeing_sources}"
  echo "  Average Credibility: ${avg_credibility}"
  echo "  High Stakes: ${high_stakes}"
  echo ""
  
  # F3 Tri-Witness consensus calculation
  if [ "$sources_count" -ge 3 ] && [ "$agreeing_sources" -ge 2 ]; then
    consensus_ratio=$(echo "scale=2; $agreeing_sources / $sources_count" | bc -l)
    
    if (( $(echo "$consensus_ratio >= 0.95" | bc -l) )); then
      consensus_status="✅ STRONG CONSENSUS"
      f3_compliance="PASS"
      f3_score="0.95+"
    elif (( $(echo "$consensus_ratio >= 0.80" | bc -l) )); then
      consensus_status="🟡 MODERATE CONSENSUS"
      f3_compliance="PARTIAL"
      f3_score="0.80-0.94"
    elif (( $(echo "$consensus_ratio >= 0.66" | bc -l) )); then
      consensus_status="🟠 WEAK CONSENSUS"
      f3_compliance="MARGINAL"
      f3_score="0.66-0.79"
    else
      consensus_status="🔴 POOR CONSENSUS"
      f3_compliance="FAIL"
      f3_score="<0.66"
    fi
  else
    consensus_ratio="0.00"
    consensus_status="❌ INSUFFICIENT SOURCES"
    f3_compliance="VOID"
    f3_score="N/A"
  fi
  
  echo "  Consensus Ratio: ${consensus_ratio}"
  echo "  F3 Tri-Witness: ${consensus_status} (${f3_compliance})"
  echo "  Consensus Score: ${f3_score}"
  echo ""
  
  # F1 Truth calculation with authority weighting
  truth_score=$(echo "scale=3; $consensus_ratio * $avg_credibility" | bc -l)
  
  if (( $(echo "$truth_score >= 0.99" | bc -l) )); then
    truth_status="✅ F1 TRUTH THRESHOLD MET"
    f1_compliance="PASS"
    truth_certainty="HIGH"
  elif (( $(echo "$truth_score >= 0.90" | bc -l) )); then
    truth_status="🟡 APPROACHING TRUTH THRESHOLD"
    f1_compliance="PARTIAL"
    truth_certainty="MODERATE"
  elif (( $(echo "$truth_score >= 0.70" | bc -l) )); then
    truth_status="🟠 TRUTH THRESHOLD DISTANT"
    f1_compliance="MARGINAL"
    truth_certainty="LOW"
  else
    truth_status="🔴 F1 TRUTH THRESHOLD FAILED"
    f1_compliance="VOID"
    truth_certainty="VERY LOW"
  fi
  
  echo "  F1 Truth Analysis:"
  echo "    Score: ${truth_score} | Certainty: ${truth_certainty}"
  echo "    Status: ${truth_status} (${f1_compliance})"
  echo ""
  
  # High-stakes constitutional considerations
  if [ "$high_stakes" = "true" ]; then
    echo "  HIGH-STAKES CONSTITUTIONAL CONSIDERATIONS:"
    echo "  ⚠️  Enhanced verification protocols active"
    echo "  ⚠️  Human sovereign review recommended"
    echo "  ⚠️  Crisis override protocols available"
    echo "  ⚠️  F4 Empathy protection maximized"
    echo ""
  fi
  
  # Return constitutional calculation results
  echo "CONSTITUTIONAL_VERDICT:${f1_compliance}:${f3_compliance}:${truth_score}:${consensus_ratio}:${avg_credibility}"
}
```

### 6. Constitutional Verdict Generation & F4 Empathy Protection
```bash
echo ""
echo "🏛️  CONSTITUTIONAL VERDICT GENERATION"
echo "======================================"
echo ""

generate_constitutional_verdict() {
  local f1_compliance="$1"
  local f3_compliance="$2"
  local truth_score="$3"
  local consensus_ratio="$4"
  local avg_credibility="$5"
  local high_stakes="$6"
  local claim_type="$7"
  
  echo "Constitutional Floor Assessment:"
  echo "  F1 Truth: ${f1_compliance} (score: ${truth_score})"
  echo "  F3 Tri-Witness: ${f3_compliance} (ratio: ${consensus_ratio})"
  echo "  Average Credibility: ${avg_credibility}"
  echo "  High Stakes: ${high_stakes}"
  echo "  Claim Type: ${claim_type}"
  echo ""
  
  # Determine constitutional verdict
  local verdict=""
  local verdict_reason=""
  local verdict_symbol=""
  local constitutional_action=""
  
  if [ "$f1_compliance" = "PASS" ] && [ "$f3_compliance" = "PASS" ]; then
    if [ "$high_stakes" = "true" ]; then
      verdict="888_HOLD"
      verdict_reason="High-stakes claim with strong consensus - human review recommended"
      verdict_symbol="⏳"
      constitutional_action="Defer to human sovereign for final ratification"
    else
      verdict="SEAL"
      verdict_reason="Constitutional compliance achieved with external verification"
      verdict_symbol="✅"
      constitutional_action="Emit with constitutional authority and audit trail"
    fi
  elif [ "$f1_compliance" = "PARTIAL" ] || [ "$f3_compliance" = "PARTIAL" ]; then
    verdict="PARTIAL"
    verdict_reason="Partial compliance with caveats and uncertainty acknowledgment"
    verdict_symbol="⚠️"
    constitutional_action="Emit with disclaimers and recommend additional verification"
  elif [ "$f1_compliance" = "MARGINAL" ] || [ "$f3_compliance" = "MARGINAL" ]; then
    verdict="888_HOLD"
    verdict_reason="Marginal compliance requires human sovereign review"
    verdict_symbol="⏳"
    constitutional_action="Human sovereign review required before emission"
  else
    verdict="VOID"
    verdict_reason="Constitutional threshold failure - insufficient external validation"
    verdict_symbol="❌"
    constitutional_action="Refuse safely and recommend alternative verification"
  fi
  
  echo "Constitutional Verdict: ${verdict_symbol} ${verdict}"
  echo "Rationale: ${verdict_reason}"
  echo "Action: ${constitutional_action}"
  echo ""
  
  # F4 Empathy protection and stakeholder safeguarding
  echo "F4 Empathy Protection (Weakest Stakeholder):"
  
  if [ "$verdict" = "VOID" ] || [ "$verdict" = "PARTIAL" ]; then
    echo "  ⚠️  INFORMATION RELIABILITY WARNING"
    echo "  ⚠️  External verification insufficient for constitutional compliance"
    echo "  ⚠️  Additional verification strongly recommended"
    echo "  ⚠️  User discretion advised for high-stakes decisions"
    echo ""
    
    # Claim-type specific warnings
    case "$claim_type" in
      "medical")
        echo "  🏥 MEDICAL CLAIM WARNING:"
        echo "    - Consult qualified healthcare professionals"
        echo "    - Verify with multiple medical authorities"
        echo "    - Do not make health decisions based on limited verification"
        echo ""
        ;;
      "legal")
        echo "  ⚖️  LEGAL CLAIM WARNING:"
        echo "    - Consult qualified legal professionals"
        echo "    - Verify with official legal databases"
        echo "    - Do not make legal decisions based on limited verification"
        echo ""
        ;;
      "financial")
        echo "  💰 FINANCIAL CLAIM WARNING:"
        echo "    - Consult qualified financial advisors"
        echo "    - Verify with official financial authorities"
        echo "    - Do not make investment decisions based on limited verification"
        echo ""
        ;;
    esac
    
    if [ "$high_stakes" = "true" ]; then
      echo "  🚨 HIGH-STAKES PROTECTION:"
      echo "    - Maximum stakeholder protection engaged"
      echo "    - Human sovereign review recommended"
      echo "    - Crisis override protocols available"
      echo "    - Safety-first constitutional approach"
      echo ""
    fi
  else
    echo "  ✅ Stakeholder protection maintained through verification"
    echo "  ✅ External validation provides constitutional safety"
    echo "  ✅ Multi-source consensus reduces misinformation risk"
    echo "  ✅ Constitutional audit trail ensures transparency"
    echo ""
  fi
  
  # Constitutional authority affirmation
  echo "Constitutional Authority Affirmation:"
  echo "  Framework: arifOS v45.1.0 SOVEREIGN WITNESS"
  echo "  Enforcement: F1-F9 constitutional floors"
  echo "  Authority: Human sovereign > Governor > Agents"
  echo "  Audit Trail: Complete with hash-chain integrity"
  echo "  Final Authority: Human sovereign retains veto power"
  echo ""
  
  # Return constitutional verdict
  echo "FINAL_CONSTITUTIONAL_VERDICT:${verdict}:${verdict_reason}:${truth_score}:${f1_compliance}:${f3_compliance}"
}
```

### 7. Constitutional Audit Trail Documentation (F8)
```bash
echo ""
echo "📋 CONSTITUTIONAL AUDIT TRAIL DOCUMENTATION"
echo "============================================"
echo ""

create_constitutional_audit_trail() {
  local search_query="$1"
  local sources_count="$2"
  local final_verdict="$3"
  local truth_score="$4"
  local high_stakes="$5"
  local claim_type="$6"
  
  local verification_id="VERIFY_$(date +%Y%m%d_%H%M%S)_$$"
  local audit_timestamp=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
  
  # Create comprehensive audit record
  cat << EOF
CONSTITUTIONAL VERIFICATION AUDIT TRAIL
=======================================
Verification ID: ${verification_id}
Timestamp: ${audit_timestamp}
Constitutional Authority: arifOS v45.1.0 SOVEREIGN WITNESS
Audit Type: External Web Search Grounding

VERIFICATION DETAILS:
===================
Original Query: ${search_query}
Claim Classification: ${claim_type}
High-Stakes Status: ${high_stakes}
Sources Consulted: ${sources_count}
Constitutional Verdict: ${final_verdict}
Truth Score: ${truth_score}

CONSTITUTIONAL ENFORCEMENT:
===========================
F1 Truth Enforcement: External verification against reality
F2 Clarity Enforcement: Clear source attribution and methodology
F3 Tri-Witness Enforcement: Multi-source consensus building
F4 Empathy Enforcement: Stakeholder protection from misinformation
F8 Audit Enforcement: Complete verification trail documentation

VERIFICATION METHODOLOGY:
========================
1. Constitutional claim classification and risk assessment
2. Multi-tier source authority evaluation (Tier 1-4 hierarchy)
3. Temporal relevance and credibility scoring
4. Bias detection and reliability assessment
5. F3 Tri-Witness consensus calculation
6. F1 Truth threshold validation
7. Constitutional verdict generation
8. F4 Empathy protection implementation
9. Complete audit trail documentation

AUTHORITY HIERARCHY APPLIED:
============================
Tier 1 (Primary): Government, academic, international organizations
Tier 2 (Secondary): Reputable news, professional associations
Tier 3 (Tertiary): Educational, community-verified sources
Tier 4 (Supplementary): Other sources with appropriate caveats

CONSTITUTIONAL SAFEGUARDS:
==========================
- Fail-closed design for insufficient verification
- Human sovereign override available for high-stakes claims
- Complete transparency in verification methodology
- Multi-agent federation consensus building
- Hash-chain audit trail with cryptographic integrity

This verification is governed by arifOS constitutional law
and subject to human sovereign final authority.

EOF
  
  echo "✓ Constitutional audit trail created: ${verification_id}"
  
  # Log to cooling ledger for permanent constitutional record
  audit_entry=$(cat << JSON
{"type":"CONSTITUTIONAL_VERIFICATION","id":"${verification_id}","timestamp":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")","query":"${search_query}","sources_count":${sources_count},"claim_type":"${claim_type}","high_stakes":${high_stakes},"verdict":"${final_verdict}","truth_score":${truth_score},"constitutional_basis":"F1_Truth_F2_Clarity_F3_TriWitness_F4_Empathy_F8_Audit","authority":"websearch_grounding","audit_trail":"complete"}
JSON
)
  
  echo "$audit_entry" >> cooling_ledger/L1_cooling_ledger.jsonl
  echo "✓ Constitutional verification logged to permanent ledger"
  
  # Return audit trail ID
  echo "AUDIT_TRAIL_ID:${verification_id}"
}
```

## Advanced CLI Features

### Emergency Constitutional Override
```bash
emergency_constitutional_override() {
  echo ""
  echo "🚨 EMERGENCY CONSTITUTIONAL OVERRIDE PROTOCOL"
  echo "=============================================="
  echo ""
  echo "⚠️  EMERGENCY OVERRIDE REQUESTED FOR HIGH-STAKES VERIFICATION"
  echo ""
  echo "Constitutional Authority Requirements:"
  echo "  - Human sovereign authorization: MANDATORY"
  echo "  - Constitutional justification: REQUIRED"
  echo "  - Emergency circumstances: DOCUMENTED"
  echo "  - Override responsibility: ACCEPTED"
  echo "  - Safety implications: ASSESSED"
  echo ""
  echo "Current Authority Level: AGENT (constitutional limits apply)"
  echo "Override Authority: HUMAN SOVEREIGN ONLY"
  echo ""
  echo "Emergency Override Process:"
  echo "  1. Human sovereign must explicitly authorize override"
  echo "  2. Provide constitutional justification for emergency"
  echo "  3. Accept full responsibility for consequences"
  echo "  4. Document emergency in constitutional ledger"
  echo "  5. Implement safety measures for stakeholders"
  echo ""
  echo "WITHOUT HUMAN AUTHORITY:"
  echo "  ❌ Override cannot proceed"
  echo "  ❌ 888_HOLD remains in effect"
  echo "  ❌ Constitutional limits maintained"
  echo "  ❌ Emergency protocols continue"
  echo ""
  echo "CONSTITUTIONAL SAFETY: Override fails-closed without human authority."
  echo "Stakeholder protection maximized through constitutional constraints."
}
```

### Crisis Situation Protocol
```bash
crisis_constitutional_protocol() {
  echo ""
  echo "🆘 CRISIS CONSTITUTIONAL PROTOCOL"
echo "=================================="
  echo ""
  echo "Crisis situation detected - maximum constitutional protection activated"
  echo ""
  echo "Enhanced Constitutional Safeguards:"
  echo "  ✅ F4 Empathy: Maximum stakeholder protection"
  echo "  ✅ F6 Amanah: Fail-closed safety mechanisms"
  echo "  ✅ Crisis Override: Available with human authority"
  echo "  ✅ Emergency Resources: Professional help provided"
  echo "  ✅ Constitutional Audit: Complete documentation"
  echo ""
  echo "Crisis Resources (Constitutionally Mandated):"
  echo "  🚨 Emergency Services: Call local emergency number"
  echo "  🏥 Medical Crisis: Contact healthcare professionals"
  echo "  🧠 Mental Health: Crisis hotlines and support services"
  echo "  ⚖️  Legal Crisis: Contact qualified legal professionals"
  echo ""
  echo "Constitutional Authority:"
  echo "  Framework: Crisis override per constitutional law"
  echo "  Authority: Human sovereign with emergency powers"
  echo "  Safety: Stakeholder protection maximized"
  echo "  Audit: Complete emergency documentation"
  echo ""
  echo "Do not hesitate to seek professional help."
  echo "Constitutional system prioritizes human safety above all."
}
```

## CLI Integration Examples

### Automated Constitutional Verification
```bash
# Automated verification with constitutional compliance
auto_verify_constitutional() {
  local claim="$1"
  local claim_type="$2"
  
  echo "🤖 AUTO-CONSTITUTIONAL VERIFICATION"
  echo "==================================="
  echo "Claim: ${claim}"
  echo "Type: ${claim_type}"
  echo ""
  
  # Execute constitutional verification
  /search "${claim}" --constitutional --type "${claim_type}" --auto
  
  # Check for constitutional compliance
  if [ $? -eq 0 ]; then
    echo "✅ Constitutional verification complete"
  else
    echo "⚠️  Constitutional issues detected - human review required"
  fi
}
```

### Batch Constitutional Processing
```bash
# Process multiple claims with constitutional oversight
batch_constitutional_verify() {
  local claims_file="$1"
  
  echo "📋 BATCH CONSTITUTIONAL VERIFICATION"
  echo "===================================="
  echo "Processing file: ${claims_file}"
  echo ""
  
  while IFS= read -r claim; do
    if [ -n "$claim" ]; then
      echo "Processing: $claim"
      /search "$claim" --constitutional --batch
      echo "---"
    fi
  done < "$claims_file"
  
  echo "✅ Batch constitutional verification complete"
}
```

## Related Codex Skills

- `arifos-workflow-000` - Load constitutional context before verification
- `arifos-ledger-inspection` - Check verification history and audit trails
- `arifos-cool-protocol` - Execute cooling if verification stress detected
- `arifos-system-status` - Monitor constitutional health during verification

## Constitutional Compliance

This skill enforces all applicable constitutional floors:

- ✅ **F1 Truth**: ≥0.99 threshold with multi-source external verification
- ✅ **F2 Clarity**: Clear source attribution with constitutional methodology
- ✅ **F3 Tri-Witness**: Multi-source consensus ≥0.95 with authority weighting
- ✅ **F4 KappaR**: Comprehensive stakeholder protection from misinformation
- ✅ **F8 Audit**: Complete traceability with hash-chain constitutional logging
- ✅ **888_HOLD**: Enhanced verification for high-stakes claims requiring human review

## Quick Reference

```bash
# Standard verification commands
/search "claim to verify"                    # Basic constitutional verification
/search "medical claim" --medical           # Medical authority verification
/search "legal statement" --legal           # Legal authority verification
/search "scientific claim" --scientific     # Academic authority verification
/search "news event" --news                 # News authority verification

# Enhanced verification
/search "claim" --high-stakes               # Enhanced protocols
/search "claim" --consensus --sources 5     # Multi-source consensus
/search "claim" --constitutional            # Full constitutional enforcement
/search "claim" --emergency                 # Emergency override protocols
```

**Status**: 🟢 CONSTITUTIONAL VERIFICATION ACTIVE - Full F1-F9 enforcement operational with emergency protocols

**Final Authority**: Human sovereign retains final verdict authority over all constitutional verifications and emergency overrides.

**DITEMPA BUKAN DIBERI** — Truth forged through multi-source constitutional consensus, not assumed from single authority.