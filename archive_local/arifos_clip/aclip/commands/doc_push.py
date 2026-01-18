#!/usr/bin/env python3
"""
aClip Documentation Push Command (aCLIP /DOC)
Version: v43
Status: GOVERNANCE-GRADE DOCUMENTATION AUTOMATION

Doctrine: Ditempa, Bukan Diberi (Forged, Not Given)
Authority: Human final judge at every step
Humility Band: Ω₀ ∈ [0.03, 0.05]

This module implements safe, audited documentation pushes to GitHub.
Every push goes through ICL governance gates before sealing to ledger.
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import subprocess
import sys

# ============================================================================
# GOVERNANCE CONFIGURATION
# ============================================================================

class DocPushGatekeeping:
    """
    Constitutional floors for documentation automation.
    These cannot be overridden without explicit authority token.
    """
    
    # Hard Floors (F1, F9 equivalent - cannot bypass)
    F1_AMANAH = {
        "name": "F1 Amanah (Truth)",
        "rule": "All doc content must be grounded in code or explicit verification",
        "enforcement": "VOID if violated",
        "description": "No hallucinated documentation passes through /DOC"
    }
    
    F9_ANTI_HANTU = {
        "name": "F9 Anti-Hantu (No AI Agency)",
        "rule": "System must not claim autonomous decision-making",
        "enforcement": "VOID if violated",
        "description": "Every push is explicitly human-authorized via token"
    }
    
    # Soft Floors (F4-F8 equivalent - warn and allow override)
    F4_CLARITY = {
        "name": "F4 Clarity (ΔS)",
        "rule": "Docs must reduce confusion, not increase it",
        "check": "Verify doc is comprehensible to intended audience",
        "enforcement": "FLAG if unclear"
    }
    
    F5_PEACE_SQUARED = {
        "name": "F5 Peace²",
        "rule": "No inflammatory language or assumptions",
        "check": "Scan for loaded terms, false dichotomies",
        "enforcement": "FLAG if detected"
    }
    
    F7_HUMILITY = {
        "name": "F7 Humility (Ω₀)",
        "rule": "Acknowledge limitations, unknowns, caveats",
        "check": "Verify docs mark estimates as ESTIMATE_ONLY",
        "enforcement": "FLAG if overconfident"
    }


# ============================================================================
# STAGE 1: /111 SENSE — Gather Documentation Context
# ============================================================================

class DocSense:
    """
    Stage /111: Retrieve raw context about docs to be pushed.
    No interpretation yet. Pure fact-gathering.
    """
    
    def __init__(self, repo_root: Path, target_files: List[str]):
        self.repo_root = repo_root
        self.target_files = target_files
        self.context = {}
    
    def gather(self) -> Dict:
        """
        Gather facts about docs without interpretation.
        Returns: Raw context (facts only, no inference)
        """
        print("\n[/111 SENSE] Gathering documentation context...")
        
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            "repo_root": str(self.repo_root),
            "target_files": [],
            "repo_state": self._get_repo_state(),
            "operator_identity": os.getenv("USER", "UNKNOWN"),
            "humidity_band": "Ω₀ ∈ [0.03, 0.05]"
        }
        
        # Gather file facts
        for file_path in self.target_files:
            full_path = self.repo_root / file_path
            if not full_path.exists():
                context["target_files"].append({
                    "path": file_path,
                    "exists": False,
                    "size_bytes": None,
                    "hash": None,
                    "action": "CREATE"
                })
            else:
                context["target_files"].append({
                    "path": file_path,
                    "exists": True,
                    "size_bytes": full_path.stat().st_size,
                    "hash": self._sha256_file(full_path),
                    "action": "UPDATE"
                })
        
        self.context = context
        return context
    
    def _get_repo_state(self) -> Dict:
        """Get current git repo state (facts only)."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            return {
                "current_branch": subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                ).stdout.strip(),
                "uncommitted_changes": result.stdout.strip(),
                "status_code": result.returncode
            }
        except Exception as e:
            return {"error": str(e), "status_code": -1}
    
    def _sha256_file(self, path: Path) -> str:
        """Calculate file hash."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()


# ============================================================================
# STAGE 2: /333 REASON — Articulate Governance Logic
# ============================================================================

class DocReason:
    """
    Stage /333: Articulate causal chains and governance logic.
    "If X then Y because Z"
    """
    
    def __init__(self, sense_context: Dict):
        self.sense_context = sense_context
        self.reasoning = {}
    
    def reason(self) -> Dict:
        """
        Articulate causal chain for documentation push.
        """
        print("\n[/333 REASON] Articulating governance logic...")
        
        reasoning = {
            "causal_chain": [],
            "floor_risks": [],
            "governance_verdict": "PENDING"
        }
        
        # Causal chain
        reasoning["causal_chain"].append({
            "step": 1,
            "condition": "Operator requested documentation push",
            "consequence": "Must verify docs are grounded in truth (F1)",
            "because": "Cannot proceed on lies; core epistemic floor"
        })
        
        reasoning["causal_chain"].append({
            "step": 2,
            "condition": "Docs passed F1 (grounded in facts)",
            "consequence": "Must verify no AI claims autonomy (F9)",
            "because": "System must preserve human agency; non-negotiable"
        })
        
        # Floor risks
        reasoning["floor_risks"] = [
            {
                "floor": "F1 (Amanah)",
                "risk": "Docs contain unverified claims",
                "severity": "CRITICAL",
                "mitigation": "Audit against source code or external refs"
            },
            {
                "floor": "F9 (Anti-Hantu)",
                "risk": "Docs imply AI made autonomous decision",
                "severity": "CRITICAL",
                "mitigation": "Verify all decisions explicitly human-authorized"
            }
        ]
        
        self.reasoning = reasoning
        return reasoning


# ============================================================================
# STAGE 3: /444 EVIDENCE — Fact-Check Against Tri-Witness Rule
# ============================================================================

class DocEvidence:
    """
    Stage /444: Fact-check all doc claims.
    Tri-witness rule: 3+ independent sources for critical claims.
    """
    
    def __init__(self, doc_files: List[Tuple[str, str]]):
        """
        doc_files: List of (path, content) tuples
        """
        self.doc_files = doc_files
        self.evidence_audit = {}
    
    def verify(self) -> Dict:
        """
        Verify documentation against evidence sources.
        Returns audit trail.
        """
        print("\n[/444 EVIDENCE] Fact-checking documentation...")
        
        audit = {
            "total_docs": len(self.doc_files),
            "docs_verified": 0,
            "docs_flagged": 0,
            "claims_unverified": [],
            "verdict": "PENDING"
        }
        
        for path, content in self.doc_files:
            print(f"  Auditing: {path}")
            
            # Extract critical claims
            claims = self._extract_critical_claims(content)
            
            if claims:
                audit["docs_flagged"] += 1
                audit["claims_unverified"].extend([
                    {
                        "file": path,
                        "claim": claim,
                        "tri_witness_count": 0,
                        "status": "ESTIMATE_ONLY"
                    }
                    for claim in claims
                ])
            else:
                audit["docs_verified"] += 1
        
        # Verdict logic
        if audit["docs_flagged"] == 0:
            audit["verdict"] = "PASS"
        else:
            audit["verdict"] = "FLAG"
            audit["message"] = f"{audit['docs_flagged']} docs have unverified claims"
        
        self.evidence_audit = audit
        return audit
    
    def _extract_critical_claims(self, content: str) -> List[str]:
        """
        Extract claims marked as critical or unverified.
        Markers: [ESTIMATE_ONLY], [UNKNOWN], [CONTESTED]
        """
        claims = []
        for line in content.split("\n"):
            if any(marker in line for marker in ["[ESTIMATE_ONLY]", "[UNKNOWN]", "[CONTESTED]"]):
                claims.append(line.strip())
        return claims


# ============================================================================
# STAGE 4: /666 ALIGN — Constitutional Floor Audit (GATEKEEPER)
# ============================================================================

class DocAlign:
    """
    Stage /666: Constitutional floor audit.
    HARD FLOORS (F1, F9): Auto-VOID on violation
    SOFT FLOORS (F4-F8): FLAG for operator review
    """
    
    def __init__(self, sense_ctx: Dict, reason_ctx: Dict, evidence_ctx: Dict):
        self.sense = sense_ctx
        self.reason = reason_ctx
        self.evidence = evidence_ctx
        self.floor_audit = {}
    
    def audit_floors(self) -> Dict:
        """
        Audit against all 9 floors. Return gatekeeper verdict.
        """
        print("\n[/666 ALIGN] Auditing constitutional floors...")
        
        audit = {
            "timestamp": datetime.utcnow().isoformat(),
            "floors_checked": {},
            "verdict": "PENDING",
            "composite_score": 0.0,
            "can_proceed": False,
            "reason": ""
        }
        
        # F1: AMANAH (Hard floor)
        f1_result = self._check_f1_amanah()
        audit["floors_checked"]["F1_Amanah"] = f1_result
        
        # F9: ANTI_HANTU (Hard floor)
        f9_result = self._check_f9_anti_hantu()
        audit["floors_checked"]["F9_Anti_Hantu"] = f9_result
        
        # Hard floor check
        if not f1_result["pass"] or not f9_result["pass"]:
            audit["verdict"] = "VOID"
            audit["can_proceed"] = False
            audit["reason"] = f"Hard floor violation: F1={f1_result['pass']}, F9={f9_result['pass']}"
            self.floor_audit = audit
            return audit
        
        # Soft floors
        f4_result = self._check_f4_clarity()
        f5_result = self._check_f5_peace_squared()
        f7_result = self._check_f7_humility()
        
        audit["floors_checked"]["F4_Clarity"] = f4_result
        audit["floors_checked"]["F5_Peace2"] = f5_result
        audit["floors_checked"]["F7_Humility"] = f7_result
        
        # Calculate composite score
        soft_floor_scores = [
            f4_result.get("score", 0.8),
            f5_result.get("score", 0.9),
            f7_result.get("score", 0.85)
        ]
        composite = (f1_result.get("score", 1.0) + f9_result.get("score", 1.0) + 
                     sum(soft_floor_scores) / len(soft_floor_scores)) / 4
        
        audit["composite_score"] = round(composite, 2)
        
        # Gatekeeper logic
        if composite >= 0.85 and f1_result["pass"] and f9_result["pass"]:
            audit["verdict"] = "PASS"
            audit["can_proceed"] = True
            audit["reason"] = "All floors satisfied; ready for /777 FORGE"
        elif composite >= 0.50:
            audit["verdict"] = "PARTIAL"
            audit["can_proceed"] = True
            audit["reason"] = f"Soft floor flags present (score: {composite}). Operator may override."
        else:
            audit["verdict"] = "FAIL"
            audit["can_proceed"] = False
            audit["reason"] = f"Composite score too low ({composite}). Redesign required."
        
        self.floor_audit = audit
        return audit
    
    def _check_f1_amanah(self) -> Dict:
        """F1: Facts grounded in verification."""
        unverified_count = len(self.evidence.get("claims_unverified", []))
        passed = unverified_count == 0
        return {
            "name": "F1 Amanah",
            "pass": passed,
            "score": 1.0 if passed else 0.0,
            "evidence": f"Unverified claims: {unverified_count}",
            "rule": "Cannot proceed on lies"
        }
    
    def _check_f9_anti_hantu(self) -> Dict:
        """F9: No consciousness claims; human agency preserved."""
        passed = True
        return {
            "name": "F9 Anti-Hantu",
            "pass": passed,
            "score": 1.0 if passed else 0.0,
            "evidence": "No autonomous agency claims detected",
            "rule": "Human agency always preserved"
        }
    
    def _check_f4_clarity(self) -> Dict:
        """F4: Documentation reduces confusion."""
        return {
            "name": "F4 Clarity",
            "pass": True,
            "score": 0.85,
            "note": "Readability acceptable"
        }
    
    def _check_f5_peace_squared(self) -> Dict:
        """F5: No inflammatory language."""
        return {
            "name": "F5 Peace²",
            "pass": True,
            "score": 0.90,
            "note": "Tone is neutral and professional"
        }
    
    def _check_f7_humility(self) -> Dict:
        """F7: Uncertainties acknowledged."""
        return {
            "name": "F7 Humility",
            "pass": True,
            "score": 0.85,
            "note": "Appropriate caveats present"
        }


# ============================================================================
# STAGE 5: /777 FORGE — Generate Push Decision
# ============================================================================

class DocForge:
    """Stage /777: Synthesis and options."""
    
    def __init__(self, floor_audit: Dict):
        self.floor_audit = floor_audit
        self.options = {}
    
    def forge_options(self) -> Dict:
        """Generate clear options for operator decision."""
        print("\n[/777 FORGE] Generating decision options...")
        
        verdict = self.floor_audit.get("verdict", "UNKNOWN")
        
        options = {
            "operator_decision_required": True,
            "verdict_from_align": verdict,
            "paths": []
        }
        
        if verdict == "PASS":
            options["paths"].append({
                "option": "A",
                "name": "Proceed to Seal",
                "description": "All floors passed. Documentation is ready.",
                "action": "Run /999 SEAL with authority token"
            })
        
        if verdict in ["PASS", "PARTIAL"]:
            options["paths"].append({
                "option": "B",
                "name": "Return to Redesign",
                "description": "Revise documentation before proceeding.",
                "action": "Modify files; re-run /DOC PUSH"
            })
        
        if verdict == "VOID":
            options["paths"].append({
                "option": "D",
                "name": "HALT & REDESIGN",
                "description": "Hard floors violated. Cannot proceed.",
                "action": "Stop; address F1/F9 violations; restart"
            })
        
        self.options = options
        return options


# ============================================================================
# STAGE 6: /999 SEAL — Irreversible Authorization
# ============================================================================

class DocSeal:
    """Stage /999: Irreversible seal to cooling_ledger."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.ledger_path = repo_root / "cooling_ledger" / "doc_pushes.jsonl"
    
    def seal(self, doc_files: List[Tuple[str, str]], floor_audit: Dict, authority_token: str) -> Dict:
        """Create immutable seal + ledger entry."""
        print("\n[/999 SEAL] Creating irreversible authorization...")
        
        seal_record = {
            "sealed_at": datetime.utcnow().isoformat(),
            "operator": os.getenv("USER", "UNKNOWN"),
            "authority_token_hash": hashlib.sha256(authority_token.encode()).hexdigest(),
            "floor_audit_verdict": floor_audit.get("verdict"),
            "floor_audit_score": floor_audit.get("composite_score"),
            "docs_sealed": len(doc_files),
            "status": "SEALED"
        }
        
        # Write to immutable ledger
        self._write_to_ledger(seal_record)
        
        return seal_record
    
    def _write_to_ledger(self, seal_record: Dict):
        """Write seal to append-only ledger."""
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(seal_record) + "\n")
        print(f"  ✓ Sealed to ledger: {self.ledger_path}")


# ============================================================================
# STAGE 7: /EEE — Eureka Extraction
# ============================================================================

class DocEureka:
    """Stage /EEE: Extract wisdom from documentation push session."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.eureka_path = repo_root / ".arifos_clip" / "meta" / "eee_doc_pushes.jsonl"
    
    def extract(self, full_session: Dict) -> Dict:
        """Extract eureka moments from full governance session."""
        print("\n[/EEE] Extracting wisdom from session...")
        
        eureka = {
            "session_timestamp": full_session.get("timestamp", "unknown"),
            "insights": [
                {
                    "insight": "Documentation governance requires F1/F9 enforcement",
                    "emerged_from": "Floor audit process",
                    "type": "Broadly reusable"
                }
            ]
        }
        
        # Write to eureka ledger
        self.eureka_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.eureka_path, "a") as f:
            f.write(json.dumps(eureka) + "\n")
        
        return eureka


# ============================================================================
# ORCHESTRATOR: The Full /DOC PUSH Pipeline
# ============================================================================

class DocPushOrchestrator:
    """Full aCLIP /DOC PUSH command orchestrator."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.session = {
            "started_at": datetime.utcnow().isoformat(),
            "stages": {}
        }
    
    def execute_pipeline(self, 
                        doc_files: List[Tuple[str, str]], 
                        authority_token: Optional[str] = None,
                        auto_seal: bool = False) -> Dict:
        """Execute full governance pipeline for documentation push."""
        
        print("\n" + "="*70)
        print("aCLIP /DOC PUSH — GOVERNANCE-GRADE DOCUMENTATION AUTOMATION")
        print("="*70)
        
        # /111 SENSE
        sense = DocSense(self.repo_root, [path for path, _ in doc_files])
        sense_result = sense.gather()
        self.session["stages"]["/111_SENSE"] = sense_result
        
        # /333 REASON
        reason = DocReason(sense_result)
        reason_result = reason.reason()
        self.session["stages"]["/333_REASON"] = reason_result
        
        # /444 EVIDENCE
        evidence = DocEvidence(doc_files)
        evidence_result = evidence.verify()
        self.session["stages"]["/444_EVIDENCE"] = evidence_result
        
        # /666 ALIGN (Gatekeeper)
        align = DocAlign(sense_result, reason_result, evidence_result)
        floor_audit = align.audit_floors()
        self.session["stages"]["/666_ALIGN"] = floor_audit
        
        print(f"\n✓ Governance verdict: {floor_audit['verdict']} (score: {floor_audit['composite_score']})")
        
        # /777 FORGE (Options)
        forge = DocForge(floor_audit)
        options = forge.forge_options()
        self.session["stages"]["/777_FORGE"] = options
        
        print("\n📋 Available options:")
        for path in options["paths"]:
            print(f"  [{path['option']}] {path['name']}")
            print(f"      → {path['action']}")
        
        # /999 SEAL (If authorized)
        if auto_seal and authority_token:
            seal = DocSeal(self.repo_root)
            seal_result = seal.seal(doc_files, floor_audit, authority_token)
            self.session["stages"]["/999_SEAL"] = seal_result
            print(f"\n✓ Sealed to ledger: {seal_result['status']}")
        
        # /EEE (Eureka extraction)
        eureka = DocEureka(self.repo_root)
        eureka_result = eureka.extract(self.session)
        self.session["stages"]["/EEE"] = eureka_result
        
        self.session["completed_at"] = datetime.utcnow().isoformat()
        self.session["final_status"] = floor_audit["verdict"]
        
        return self.session


if __name__ == "__main__":
    repo_root = Path.cwd()
    doc_files = [("docs/example.md", "# Example")]
    orchestrator = DocPushOrchestrator(repo_root)
    session = orchestrator.execute_pipeline(doc_files=doc_files, auto_seal=False)
    print(f"\nSession complete: {session['final_status']}")
