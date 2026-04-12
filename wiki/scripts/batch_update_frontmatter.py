#!/usr/bin/env python3
"""
Ω-Wiki Batch Frontmatter Updater

Updates all wiki pages with proper tier/strand/difficulty per PAGE_REGISTRY.md

Usage:
    python wiki/scripts/batch_update_frontmatter.py
"""

import re
from pathlib import Path
from datetime import datetime

# Configuration
WIKI_ROOT = Path(__file__).parent.parent
PAGES_DIR = WIKI_ROOT / "pages"

# Page registry mapping: filename -> (tier, strand, audience, difficulty, prerequisites)
REGISTRY = {
    # 00_INDEX
    "quickstart": ("00_INDEX", "[onboarding]", "all", "beginner", "[]"),
    "Prerequisite_Map": ("00_INDEX", "[onboarding]", "all", "beginner", "[]"),
    
    # 10_FOUNDATIONS
    "What-is-arifOS": ("10_FOUNDATIONS", "[philosophy]", "all", "beginner", "[]"),
    "Floors": ("10_FOUNDATIONS", "[constitutional]", "all", "beginner", "[What-is-arifOS]"),
    "Trinity_Architecture": ("10_FOUNDATIONS", "[architecture]", "all", "beginner", "[What-is-arifOS]"),
    
    # 20_RUNTIME
    "Metabolic_Loop": ("20_RUNTIME", "[architecture]", "engineers", "intermediate", "[Trinity_Architecture]"),
    "MCP_Tools": ("20_RUNTIME", "[tools]", "engineers", "intermediate", "[Metabolic_Loop]"),
    "Tool_Surface_Architecture": ("20_RUNTIME", "[architecture]", "engineers", "intermediate", "[MCP_Tools]"),
    "Concept_Architecture": ("20_RUNTIME", "[architecture]", "engineers", "intermediate", "[Trinity_Architecture]"),
    "Concept_Deployment_Architecture": ("20_RUNTIME", "[integration]", "engineers", "intermediate", "[Concept_Architecture]"),
    "Concept_Vault999_Architecture": ("20_RUNTIME", "[architecture]", "engineers", "advanced", "[Concept_Architecture]"),
    "Concept_Metabolic_Pipeline": ("20_RUNTIME", "[architecture]", "engineers", "advanced", "[Metabolic_Loop]"),
    "agent-roles": ("20_RUNTIME", "[architecture]", "engineers", "intermediate", "[Trinity_Architecture]"),
    "integration-patterns": ("20_RUNTIME", "[integration]", "engineers", "intermediate", "[MCP_Tools, Metabolic_Loop]"),
    "arifos_forge": ("20_RUNTIME", "[tools]", "engineers", "intermediate", "[MCP_Tools]"),
    "arifos_health": ("20_RUNTIME", "[tools]", "engineers", "intermediate", "[MCP_Tools]"),
    "Concept_Decision_Velocity": ("20_RUNTIME", "[paradox]", "researchers", "advanced", "[Concept_Metabolic_Pipeline]"),
    
    # 30_GOVERNANCE
    "Philosophy_Registry": ("30_GOVERNANCE", "[philosophy]", "researchers", "intermediate", "[Floors]"),
    "Concept_Governance_Enforcer": ("30_GOVERNANCE", "[constitutional]", "researchers", "advanced", "[Floors, Philosophy_Registry]"),
    "Concept_Godellock": ("30_GOVERNANCE", "[paradox]", "researchers", "advanced", "[Floors]"),
    "Concept_Floor_Tensions": ("30_GOVERNANCE", "[paradox]", "researchers", "advanced", "[Floors, Trinity_Architecture]"),
    "Concept_Epistemic_Circuit_Breakers": ("30_GOVERNANCE", "[paradox]", "researchers", "advanced", "[Floors, Concept_Godellock]"),
    "Agents-and-AAA-Architecture": ("30_GOVERNANCE", "[architecture]", "engineers", "intermediate", "[Trinity_Architecture]"),
    
    # 40_HORIZONS
    "Roadmap": ("40_HORIZONS", "[roadmap]", "all", "beginner", "[What-is-arifOS]"),
    "Horizon_2_Swarm": ("40_HORIZONS", "[roadmap]", "researchers", "advanced", "[Agent_Roles, Concept_Metabolic_Pipeline]"),
    "Horizon_3_Universal_Body": ("40_HORIZONS", "[roadmap]", "researchers", "advanced", "[Horizon_2_Swarm]"),
    "Eigent_Backend": ("40_HORIZONS", "[integration]", "engineers", "intermediate", "[Integration_Patterns]"),
    
    # 50_AUDITS
    "Drift_Checks": ("50_AUDITS", "[operations]", "engineers", "intermediate", "[Tool_Surface_Architecture]"),
    "Audit_Surface_Fragmentation": ("50_AUDITS", "[operations]", "engineers", "intermediate", "[Tool_Surface_Architecture]"),
    "Audit_Repo_Chaos_Reduction": ("50_AUDITS", "[operations]", "operators", "intermediate", "[Concept_Architecture]"),
    "Audit_MCP_Tools_vs_Wiki": ("50_AUDITS", "[operations]", "engineers", "intermediate", "[MCP_Tools]"),
    "Changelog": ("50_AUDITS", "[operations]", "operators", "beginner", "[What-is-arifOS]"),
    
    # 90_ENTITIES
    "GEOX": ("90_ENTITIES", "[architecture]", "all", "beginner", "[]"),
    "Entity_Andrej_Karpathy": ("90_ENTITIES", "[philosophy]", "all", "beginner", "[]"),
    "Source_Karpathy_LLM_Wiki": ("90_ENTITIES", "[philosophy]", "researchers", "beginner", "[]"),
    "Source_NotebookLM_HighLevel_Overview": ("90_ENTITIES", "[philosophy]", "researchers", "beginner", "[]"),
    
    # Tool Specifications
    "ToolSpec_arifos_judge": ("20_RUNTIME", "[tools]", "engineers", "advanced", "[MCP_Tools, Concept_Governance_Enforcer]"),
    
    # Synthesis
    "Synthesis_OpenQuestions": ("30_GOVERNANCE", "[roadmap]", "researchers", "intermediate", "[Roadmap, Floors]"),
}


def parse_existing_frontmatter(content: str) -> dict:
    """Parse existing frontmatter to preserve non-registry fields."""
    if not content.startswith("---"):
        return {}
    
    end_match = re.search(r"\n---\s*\n", content[3:])
    if not end_match:
        return {}
    
    frontmatter_text = content[3:3+end_match.start()]
    
    # Parse key-value pairs
    fields = {}
    for line in frontmatter_text.strip().split("\n"):
        if ":" in line and not line.strip().startswith("#"):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    
    return fields


def update_page(filepath: Path, tier: str, strand: str, audience: str, difficulty: str, prerequisites: str) -> bool:
    """Update a single page with new frontmatter."""
    content = filepath.read_text()
    
    # Parse existing frontmatter
    existing = parse_existing_frontmatter(content)
    
    # Preserve certain fields from existing
    type_val = existing.get("type", "Concept")
    tags = existing.get("tags", "[]")
    sources = existing.get("sources", "[]")
    confidence = existing.get("confidence", "0.95")
    
    # Build new frontmatter
    new_frontmatter = f"""---
type: {type_val}
tier: {tier}
strand: {strand}
audience: [{audience}]
difficulty: {difficulty}
prerequisites: {prerequisites}
tags: {tags}
sources: {sources}
last_sync: {datetime.now().strftime('%Y-%m-%d')}
confidence: {confidence}
---
"""
    
    # Replace old frontmatter or add new one
    if content.startswith("---"):
        end_match = re.search(r"\n---\s*\n", content[3:])
        if end_match:
            new_content = new_frontmatter + content[3+end_match.end():]
        else:
            new_content = new_frontmatter + "\n\n" + content
    else:
        new_content = new_frontmatter + "\n\n" + content
    
    filepath.write_text(new_content)
    return True


def main():
    """Main entry point."""
    print("🔧 Ω-Wiki Batch Frontmatter Updater")
    print("=" * 50)
    
    updated = 0
    skipped = 0
    errors = 0
    
    for filename, (tier, strand, audience, difficulty, prerequisites) in REGISTRY.items():
        filepath = PAGES_DIR / f"{filename}.md"
        
        if not filepath.exists():
            print(f"⚠️  Skip: {filename}.md (not found)")
            skipped += 1
            continue
        
        try:
            if update_page(filepath, tier, strand, audience, difficulty, prerequisites):
                print(f"✅ Updated: {filename}.md ({tier}, {difficulty})")
                updated += 1
        except Exception as e:
            print(f"❌ Error: {filename}.md — {e}")
            errors += 1
    
    print("\n" + "=" * 50)
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print("\n🎉 Done! Run view generator next:")
    print("   python wiki/scripts/generate_views.py")


if __name__ == "__main__":
    main()
