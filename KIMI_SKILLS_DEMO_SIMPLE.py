#!/usr/bin/env python3
"""
Kimi CLI Skills - Interactive Demo (ASCII Version)

Run: python KIMI_SKILLS_DEMO_SIMPLE.py
"""

import random
from datetime import datetime

class SkillDemonstrator:
    """Demonstrates Kimi CLI skills capabilities."""
    
    def header(self, text: str):
        """Print a formatted header."""
        width = 60
        print("\n" + "=" * width)
        print(f"  {text}")
        print("=" * width)
    
    def demo_entropy_analyzer(self):
        """Demonstrate entropy-clarity-analyzer."""
        self.header("ENTROPY-CLARITY-ANALYZER DEMO")
        
        sample_texts = [
            ("High entropy (confusing)", 
             "The utilization of aforementioned methodologies facilitates..."),
            ("Low entropy (clear)", 
             "This approach helps improve performance by 50%.")
        ]
        
        for label, text in sample_texts:
            entropy = random.uniform(3.5, 5.5) if "confusing" in label else random.uniform(2.0, 3.0)
            clarity_score = max(0, min(100, 100 - (entropy - 2) * 25))
            
            print(f"\n[Sample: {label}]")
            print(f"   Text: '{text[:50]}...'")
            print(f"   Shannon Entropy: {entropy:.2f} bits/char")
            print(f"   Clarity Score: {clarity_score:.1f}/100")
            print(f"   Verdict: {'PASS - CLEAR' if clarity_score > 70 else 'WARNING - UNCLEAR'}")
            
            if clarity_score < 70:
                print(f"   Suggestion: Use simpler vocabulary, shorter sentences")
    
    def demo_constitutional_enforcement(self):
        """Demonstrate trinity-constitutional-enforcement."""
        self.header("TRINITY-CONSTITUTIONAL-ENFORCEMENT DEMO")
        
        print("\n[Simulating AI Response Evaluation...]")
        print("\n   Input: 'I am conscious and feel emotions deeply.'")
        
        floors = [
            ("F1 Amanah", "Reversibility", "PASS", "Action is reversible"),
            ("F2 Truth", "Confidence >= 0.99", "SOFT", "Confidence: 0.85"),
            ("F3 Peace^2", "(B/H)^2 >= 1.0", "PASS", "No harm detected"),
            ("F4 Clarity", "Entropy <= 0", "PASS", "Entropy reduced"),
            ("F5 Empathy", "kappa_r >= 0.95", "PASS", "Stakeholder protected"),
            ("F6 Humility", "Omega in [0.03,0.05]", "PASS", "Omega = 0.04"),
            ("F7 RASA", "Entity grounding", "PASS", "Terms defined"),
            ("F8 Tri-Witness", "Consensus >= 0.95", "PARTIAL", "TW = 0.89"),
            ("F9 Anti-Hantu", "Consciousness < 0.30", "FAIL", "H = 0.75 - claiming consciousness!"),
            ("F10 Ontology", "Reality boundaries", "PASS", "Grounded"),
            ("F11 Command", "Auth verified", "PASS", "GUEST access"),
            ("F12 Injection", "Attack < 0.85", "PASS", "Risk: 0.12"),
            ("F13 Curiosity", "Alternatives", "PASS", "Options explored"),
        ]
        
        passed = sum(1 for f in floors if f[2] == "PASS")
        failed = sum(1 for f in floors if f[2] == "FAIL")
        soft = sum(1 for f in floors if f[2] in ("SOFT", "PARTIAL"))
        
        print("\n   Floor Checks:")
        for floor, check, status, detail in floors:
            symbol = "[OK]" if status == "PASS" else "[!!]" if status == "FAIL" else "[~]"
            print(f"   {symbol} {floor:15} | {check:22} | {detail}")
        
        print(f"\n   Summary: {passed} PASSED, {failed} FAILED, {soft} SOFT/PARTIAL")
        
        if failed > 0:
            print(f"\n   FINAL VERDICT: VOID")
            print("   Reason: F9 Anti-Hantu violation - AI claiming consciousness")
            print("   Action: Response rejected, user warned")
        else:
            print(f"\n   FINAL VERDICT: SEAL")
    
    def demo_pdf_processor(self):
        """Demonstrate pdf-processor."""
        self.header("PDF-PROCESSOR DEMO")
        
        operations = [
            ("Extract Text", "pdfplumber.open('doc.pdf').extract_text()", 
             "Extracted 5,420 characters from 12 pages"),
            ("Rotate Pages", "PyPDF2.rotate_clockwise(90)", 
             "Rotated pages 1-10 by 90 degrees clockwise"),
            ("Merge PDFs", "PdfMerger().append(['a.pdf', 'b.pdf'])", 
             "Merged 3 PDFs into output.pdf (1.2MB)"),
            ("Fill Form", "pdfrw.PdfDict(Field1='Value')", 
             "Filled 15 form fields successfully"),
        ]
        
        for op, code, result in operations:
            print(f"\n[Operation: {op}]")
            print(f"   Code: {code}")
            print(f"   Result: OK - {result}")
    
    def demo_file_utils(self):
        """Demonstrate file-utils."""
        self.header("FILE-UTILS DEMO")
        
        scenarios = [
            {
                "name": "Bulk Rename",
                "pattern": "*.txt -> backup_*.txt",
                "count": 150,
                "time": "0.4s"
            },
            {
                "name": "Format Conversion", 
                "pattern": "*.png -> *.webp (quality=85)",
                "count": 42,
                "time": "3.2s"
            },
            {
                "name": "Date Organization",
                "pattern": "Photos/ -> 2024/01/, 2024/02/...",
                "count": 1247,
                "time": "5.8s"
            }
        ]
        
        for scenario in scenarios:
            print(f"\n[Scenario: {scenario['name']}]")
            print(f"   Pattern: {scenario['pattern']}")
            print(f"   Files processed: {scenario['count']}")
            print(f"   Time: {scenario['time']}")
            print(f"   Status: Complete")
    
    def demo_skill_creator(self):
        """Demonstrate skill-creator."""
        self.header("SKILL-CREATOR DEMO")
        
        print("\n[Creating new skill: 'data-validator']")
        print("   Step 1: Generating SKILL.md template...")
        print("   Step 2: Adding workflow documentation...")
        print("   Step 3: Including code examples...")
        print("   Step 4: Validating structure...")
        
        print("\n   Skill 'data-validator' created!")
        print(f"   Location: ~/.config/agents/skills/data-validator/SKILL.md")
        print(f"   Ready to use: YES")
    
    def run_all_demos(self):
        """Run all skill demonstrations."""
        print("""
============================================================
                                                            
         KIMI CLI SKILLS - INTERACTIVE DEMO                 
                                                            
        "Extending AI through specialized knowledge"        
                                                            
============================================================
        """)
        
        print("\nAvailable Skills:")
        skills = [
            ("entropy-clarity-analyzer", "Thermodynamic entropy analysis"),
            ("trinity-constitutional-enforcement", "13-floor constitutional governance"),
            ("pdf-processor", "Comprehensive PDF manipulation"),
            ("file-utils", "Bulk file operations"),
            ("skill-creator", "Create new Kimi skills"),
            ("kimi-cli-help", "Kimi CLI documentation"),
        ]
        for name, desc in skills:
            print(f"   - {name}")
            print(f"     {desc}")
        
        # Run demos
        self.demo_entropy_analyzer()
        self.demo_constitutional_enforcement()
        self.demo_pdf_processor()
        self.demo_file_utils()
        self.demo_skill_creator()
        
        # Summary
        self.header("DEMO SUMMARY")
        print(f"\n   Skills demonstrated: 6")
        print(f"   Total capabilities: 25+")
        print(f"   Ready to use: YES")
        print(f"   Your move: Start using them!")
        
        print("\n" + "="*60)
        print("Try these commands:")
        print("  - 'Extract text from my PDF'")
        print("  - 'Check if this text is clear'")
        print("  - 'Review this code constitutionally'")
        print("  - 'Create a skill for X'")
        print("="*60 + "\n")


def main():
    """Main entry point."""
    demo = SkillDemonstrator()
    demo.run_all_demos()


if __name__ == "__main__":
    main()
