#!/usr/bin/env python3
"""
Ω-Wiki View Generator

Generates auto-indexed views from page frontmatter.
No folders — just queries against YAML metadata.

Usage:
    python wiki/scripts/generate_views.py

Output:
    wiki/view/start-here.md
    wiki/view/tier/{00_INDEX,10_FOUNDATIONS,...}.md
    wiki/view/strand/{architecture,constitutional,...}.md
    wiki/view/audience/{engineers,researchers,operators,all}.md
    wiki/view/path/to/{page}.md (prerequisite chains)
    wiki/view/gaps.md (orphan detection)
"""

import os
import re
import yaml
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Set, Optional, Any

# Configuration
WIKI_ROOT = Path(__file__).parent.parent
PAGES_DIR = WIKI_ROOT / "pages"
VIEW_DIR = WIKI_ROOT / "view"

# Tier ordering
TIER_ORDER = [
    "00_INDEX",
    "10_FOUNDATIONS", 
    "20_RUNTIME",
    "30_GOVERNANCE",
    "40_HORIZONS",
    "50_AUDITS",
    "90_ENTITIES"
]

# Strand definitions
STRANDS = [
    "architecture",
    "constitutional",
    "integration",
    "operations",
    "roadmap",
    "paradox",
    "tools",
    "philosophy"
]

# Audience definitions
AUDIENCES = [
    "engineers",
    "researchers",
    "operators",
    "all"
]


def parse_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None
    
    try:
        # Find end of frontmatter
        end_match = re.search(r"\n---\s*\n", content[3:])
        if not end_match:
            return None
        
        frontmatter_text = content[3:3+end_match.start()]
        return yaml.safe_load(frontmatter_text)
    except Exception as e:
        print(f"Warning: Failed to parse frontmatter: {e}")
        return None


def load_pages() -> List[Dict[str, Any]]:
    """Load all pages with their frontmatter."""
    pages = []
    
    for md_file in PAGES_DIR.glob("*.md"):
        content = md_file.read_text()
        frontmatter = parse_frontmatter(content)
        
        if frontmatter:
            pages.append({
                "filename": md_file.stem,
                "title": md_file.stem.replace("-", " ").replace("_", " "),
                **frontmatter
            })
        else:
            print(f"Warning: No frontmatter in {md_file.name}")
    
    return pages


def compute_depended_by(pages: List[Dict]) -> None:
    """Compute reverse dependencies (depended_by) for each page."""
    # Build lookup
    page_map = {p["filename"]: p for p in pages}
    
    # Initialize depended_by
    for page in pages:
        page["depended_by"] = []
    
    # Populate
    for page in pages:
        prereqs = page.get("prerequisites", [])
        for prereq in prereqs:
            # Handle both [[Page_Name]] and Page_Name formats
            clean_prereq = prereq.strip("[]").replace(" ", "-")
            if clean_prereq in page_map:
                page_map[clean_prereq]["depended_by"].append(page["filename"])


def generate_start_here(pages: List[Dict]) -> str:
    """Generate the 5-page (or more) beginner journey."""
    # Find root pages (no prerequisites)
    roots = [p for p in pages if not p.get("prerequisites")]
    
    # Sort by tier order
    tier_rank = {t: i for i, t in enumerate(TIER_ORDER)}
    roots.sort(key=lambda p: tier_rank.get(p.get("tier", ""), 999))
    
    # Build content
    lines = [
        "---",
        "type: Meta",
        "auto_generated: true",
        f"generated_at: {datetime.now().isoformat()}",
        "generation_source: prerequisites_graph",
        "---",
        "",
        "# Start Here — The Guided Journey",
        "",
        "> **Auto-generated** from page prerequisites and tier ordering.",
        f"> **Total Entry Points**: {len(roots)}",
        "",
        "This path takes you from zero knowledge to system fluency.",
        "",
    ]
    
    current_tier = None
    page_num = 1
    
    for page in roots:
        tier = page.get("tier", "UNKNOWN")
        
        # New tier header
        if tier != current_tier:
            tier_name = tier.replace("_", " ").title() if tier != "00_INDEX" else "Orientation"
            lines.append(f"## Phase {page_num}: {tier_name}")
            lines.append("")
            current_tier = tier
        
        # Page entry
        difficulty = page.get("difficulty", "unknown")
        reading_time = "5 min" if difficulty == "beginner" else "10 min" if difficulty == "intermediate" else "15 min"
        
        lines.append(f"{page_num}. **[[{page['filename']}|{page['title']}]]** — {reading_time}")
        lines.append(f"   - *{page.get('strand', ['unknown'])[0]}* — {get_description(page)}")
        lines.append("")
        page_num += 1
    
    # Add branch points
    lines.append("---")
    lines.append("")
    lines.append("## Choose Your Path")
    lines.append("")
    lines.append("After the foundation journey, explore by interest:")
    lines.append("")
    lines.append("### 🔧 Engineering (strand: integration)")
    lines.append("→ [[MCP_Tools]] → [[Integration_Patterns]] → [[Agent_Roles]]")
    lines.append("")
    lines.append("### ⚖️ Governance (strand: constitutional)")
    lines.append("→ [[Philosophy_Registry]] → [[Floor_Tensions]] → [[Governance_Enforcer]]")
    lines.append("")
    lines.append("### 🚀 Future (strand: roadmap)")
    lines.append("→ [[Horizon_2_Swarm]] → [[Horizon_3_Universal_Body]]")
    lines.append("")
    lines.append("### 🔍 Operations (strand: operations)")
    lines.append("→ [[Drift_Checks]] → [[Surface_Fragmentation]]")
    lines.append("")
    
    return "\n".join(lines)


def get_description(page: Dict) -> str:
    """Extract short description from page content or frontmatter."""
    # Try to get from first paragraph after frontmatter
    filename = page["filename"]
    filepath = PAGES_DIR / f"{filename}.md"
    
    if filepath.exists():
        content = filepath.read_text()
        # Remove frontmatter
        if content.startswith("---"):
            end = content.find("\n---", 3)
            if end != -1:
                content = content[end+4:]
        
        # Get first non-empty line that's not a header
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("["):
                # Clean up markdown
                line = line.replace("**", "").replace("*", "")
                if len(line) > 100:
                    line = line[:97] + "..."
                return line
    
    return "See page for details."


def generate_tier_view(pages: List[Dict], tier: str) -> str:
    """Generate view for a specific tier."""
    tier_pages = [p for p in pages if p.get("tier") == tier]
    tier_pages.sort(key=lambda p: p.get("title", ""))
    
    tier_name = tier.replace("_", " ").title()
    
    lines = [
        "---",
        "type: Meta",
        "auto_generated: true",
        f"generated_at: {datetime.now().isoformat()}",
        f"filter: tier={tier}",
        "---",
        "",
        f"# View: {tier_name}",
        "",
        f"> **Auto-generated** from `tier: {tier}` filter.",
        f"> **Total Pages**: {len(tier_pages)}",
        "",
    ]
    
    if not tier_pages:
        lines.append("*No pages found for this tier.*")
        return "\n".join(lines)
    
    # Table header
    lines.append("| Page | Strand | Difficulty | Prerequisites |")
    lines.append("|------|--------|------------|---------------|")
    
    for page in tier_pages:
        title = page.get("title", page["filename"])
        strand = ", ".join(page.get("strand", ["-"]))
        difficulty = page.get("difficulty", "-")
        prereqs = ", ".join(page.get("prerequisites", ["-"]))
        lines.append(f"| [[{page['filename']}|{title}]] | {strand} | {difficulty} | {prereqs} |")
    
    lines.append("")
    lines.append("## Description")
    lines.append("")
    lines.append(f"Pages at the **{tier_name}** depth level.")
    lines.append("")
    
    return "\n".join(lines)


def generate_strand_view(pages: List[Dict], strand: str) -> str:
    """Generate view for a specific strand."""
    strand_pages = [p for p in pages if strand in p.get("strand", [])]
    
    # Sort by tier, then by title
    tier_rank = {t: i for i, t in enumerate(TIER_ORDER)}
    strand_pages.sort(key=lambda p: (tier_rank.get(p.get("tier", ""), 999), p.get("title", "")))
    
    lines = [
        "---",
        "type: Meta",
        "auto_generated: true",
        f"generated_at: {datetime.now().isoformat()}",
        f"filter: strand={strand}",
        "---",
        "",
        f"# Strand: {strand.title()}",
        "",
        f"> **Auto-generated** from `strand: {strand}` filter.",
        f"> **Total Pages**: {len(strand_pages)}",
        "",
    ]
    
    if not strand_pages:
        lines.append("*No pages found for this strand.*")
        return "\n".join(lines)
    
    # Group by tier
    by_tier = defaultdict(list)
    for page in strand_pages:
        by_tier[page.get("tier", "UNKNOWN")].append(page)
    
    for tier in TIER_ORDER:
        if tier in by_tier:
            tier_name = tier.replace("_", " ").title()
            lines.append(f"## {tier_name}")
            lines.append("")
            
            for page in by_tier[tier]:
                title = page.get("title", page["filename"])
                difficulty = page.get("difficulty", "")
                diff_badge = f"[{difficulty}]" if difficulty else ""
                lines.append(f"- [[{page['filename']}|{title}]] {diff_badge}")
            
            lines.append("")
    
    return "\n".join(lines)


def generate_audience_view(pages: List[Dict], audience: str) -> str:
    """Generate view for a specific audience."""
    if audience == "all":
        audience_pages = pages  # All pages
    else:
        audience_pages = [p for p in pages if audience in p.get("audience", []) or "all" in p.get("audience", [])]
    
    # Sort by tier, then by difficulty
    tier_rank = {t: i for i, t in enumerate(TIER_ORDER)}
    diff_rank = {"beginner": 0, "intermediate": 1, "advanced": 2}
    audience_pages.sort(key=lambda p: (
        tier_rank.get(p.get("tier", ""), 999),
        diff_rank.get(p.get("difficulty", ""), 99)
    ))
    
    audience_name = audience.title()
    
    lines = [
        "---",
        "type: Meta",
        "auto_generated: true",
        f"generated_at: {datetime.now().isoformat()}",
        f"filter: audience={audience}",
        "---",
        "",
        f"# Audience: {audience_name}",
        "",
        f"> **Auto-generated** for `{audience}` audience.",
        f"> **Total Pages**: {len(audience_pages)}",
        "",
        f"Pages relevant to **{audience_name}**.",
        "",
    ]
    
    if not audience_pages:
        lines.append("*No pages found for this audience.*")
        return "\n".join(lines)
    
    # Table
    lines.append("| Page | Tier | Difficulty | Strand |")
    lines.append("|------|------|------------|--------|")
    
    for page in audience_pages:
        title = page.get("title", page["filename"])
        tier = page.get("tier", "-").replace("_", " ")
        difficulty = page.get("difficulty", "-")
        strand = ", ".join(page.get("strand", ["-"]))
        lines.append(f"| [[{page['filename']}|{title}]] | {tier} | {difficulty} | {strand} |")
    
    lines.append("")
    
    return "\n".join(lines)


def generate_gaps_view(pages: List[Dict]) -> str:
    """Generate view showing orphans and gaps."""
    # Find orphans (no depended_by)
    orphans = [p for p in pages if not p.get("depended_by") and p.get("tier") != "90_ENTITIES"]
    
    # Find missing prerequisites
    all_filenames = {p["filename"] for p in pages}
    missing_prereqs = defaultdict(list)
    
    for page in pages:
        for prereq in page.get("prerequisites", []):
            clean = prereq.strip("[]").replace(" ", "-")
            if clean and clean not in all_filenames:
                missing_prereqs[clean].append(page["filename"])
    
    lines = [
        "---",
        "type: Meta",
        "auto_generated: true",
        f"generated_at: {datetime.now().isoformat()}",
        "filter: gaps_analysis",
        "---",
        "",
        "# Wiki Gaps & Orphans",
        "",
        "> **Auto-generated** analysis of wiki topology.",
        "",
        "## Orphan Pages (No Incoming Links)",
        "",
        f"Pages with no `depended_by` references (excluding 90_ENTITIES): {len(orphans)}",
        "",
    ]
    
    if orphans:
        for page in orphans:
            lines.append(f"- [[{page['filename']}|{page['title']}]] ({page.get('tier', '-')})")
    else:
        lines.append("*No orphans found.*")
    
    lines.append("")
    lines.append("## Missing Prerequisite Pages")
    lines.append("")
    lines.append(f"Referenced but not created: {len(missing_prereqs)}")
    lines.append("")
    
    if missing_prereqs:
        for prereq, referrers in sorted(missing_prereqs.items()):
            lines.append(f"- `[[{prereq}]]` — referenced by: {', '.join(referrers)}")
    else:
        lines.append("*All prerequisites resolved.*")
    
    lines.append("")
    lines.append("## Frontmatter Completeness")
    lines.append("")
    
    incomplete = []
    for page in pages:
        missing = []
        if not page.get("tier"):
            missing.append("tier")
        if not page.get("strand"):
            missing.append("strand")
        if not page.get("audience"):
            missing.append("audience")
        if not page.get("difficulty"):
            missing.append("difficulty")
        if missing:
            incomplete.append((page["filename"], missing))
    
    if incomplete:
        lines.append(f"Pages with incomplete frontmatter: {len(incomplete)}")
        lines.append("")
        for filename, missing in incomplete:
            lines.append(f"- [[{filename}]] — missing: {', '.join(missing)}")
    else:
        lines.append("*All pages have complete frontmatter.* ✅")
    
    lines.append("")
    
    return "\n".join(lines)


def generate_path_to_page(pages: List[Dict], target: Dict) -> str:
    """Generate prerequisite path to reach a specific page."""
    # BFS to find all paths
    page_map = {p["filename"]: p for p in pages}
    
    def get_prereq_chain(page_name: str, visited: Set[str] = None) -> List[List[str]]:
        if visited is None:
            visited = set()
        
        if page_name in visited:
            return [[]]  # Cycle detected
        
        visited = visited | {page_name}
        page = page_map.get(page_name)
        
        if not page or not page.get("prerequisites"):
            return [[page_name]]
        
        all_paths = []
        for prereq in page.get("prerequisites", []):
            clean = prereq.strip("[]").replace(" ", "-")
            sub_paths = get_prereq_chain(clean, visited)
            for sub_path in sub_paths:
                all_paths.append(sub_path + [page_name])
        
        return all_paths
    
    chains = get_prereq_chain(target["filename"])
    
    title = target.get("title", target["filename"])
    
    lines = [
        "---",
        "type: Meta",
        "auto_generated: true",
        f"generated_at: {datetime.now().isoformat()}",
        f"target: {target['filename']}",
        "---",
        "",
        f"# Path to: {title}",
        "",
        f"> **Auto-generated** prerequisite chains to reach [[{target['filename']}]].",
        f"> **Difficulty**: {target.get('difficulty', 'unknown')}",
        f"> **Tier**: {target.get('tier', 'unknown')}",
        "",
        "## Prerequisite Chains",
        "",
    ]
    
    if not chains or (len(chains) == 1 and not chains[0]):
        lines.append("*No prerequisites — this is a root page.*")
    else:
        for i, chain in enumerate(chains[:5], 1):  # Limit to 5 paths
            lines.append(f"### Path {i}")
            lines.append("")
            for j, page_name in enumerate(chain):
                page = page_map.get(page_name, {})
                display = page.get("title", page_name)
                indent = "  " * j
                marker = "→" if j < len(chain) - 1 else "🎯"
                lines.append(f"{indent}{marker} [[{page_name}|{display}]]")
            lines.append("")
    
    # Add related pages (same strand)
    strands = target.get("strand", [])
    if strands:
        lines.append("## Related Pages (Same Strand)")
        lines.append("")
        
        related = [p for p in pages if any(s in p.get("strand", []) for s in strands) and p["filename"] != target["filename"]]
        related.sort(key=lambda p: p.get("title", ""))
        
        for page in related[:10]:  # Limit to 10
            title = page.get("title", page["filename"])
            lines.append(f"- [[{page['filename']}|{title}]]")
        
        lines.append("")
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    print("🔧 Ω-Wiki View Generator")
    print("=" * 50)
    
    # Ensure view directory exists
    VIEW_DIR.mkdir(exist_ok=True)
    
    # Load pages
    print("\n📚 Loading pages...")
    pages = load_pages()
    print(f"   Found {len(pages)} pages")
    
    # Compute dependencies
    print("\n🔗 Computing dependencies...")
    compute_depended_by(pages)
    
    # Generate views
    views_generated = 0
    
    # 1. Start Here
    print("\n🎯 Generating Start Here...")
    content = generate_start_here(pages)
    (VIEW_DIR / "start-here.md").write_text(content)
    views_generated += 1
    
    # 2. Tier views
    print("\n📊 Generating tier views...")
    tier_dir = VIEW_DIR / "tier"
    tier_dir.mkdir(exist_ok=True)
    
    for tier in TIER_ORDER:
        content = generate_tier_view(pages, tier)
        (tier_dir / f"{tier.lower()}.md").write_text(content)
        views_generated += 1
    
    # 3. Strand views
    print("\n🧬 Generating strand views...")
    strand_dir = VIEW_DIR / "strand"
    strand_dir.mkdir(exist_ok=True)
    
    for strand in STRANDS:
        content = generate_strand_view(pages, strand)
        (strand_dir / f"{strand}.md").write_text(content)
        views_generated += 1
    
    # 4. Audience views
    print("\n👥 Generating audience views...")
    audience_dir = VIEW_DIR / "audience"
    audience_dir.mkdir(exist_ok=True)
    
    for audience in AUDIENCES:
        content = generate_audience_view(pages, audience)
        (audience_dir / f"{audience}.md").write_text(content)
        views_generated += 1
    
    # 5. Gaps view
    print("\n🔍 Generating gaps view...")
    content = generate_gaps_view(pages)
    (VIEW_DIR / "gaps.md").write_text(content)
    views_generated += 1
    
    # 6. Path views (for key pages only, to avoid explosion)
    print("\n🛤️  Generating path views...")
    path_dir = VIEW_DIR / "path" / "to"
    path_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate paths for advanced pages (most useful)
    key_pages = [p for p in pages if p.get("difficulty") == "advanced"]
    for page in key_pages[:10]:  # Limit to first 10 advanced pages
        content = generate_path_to_page(pages, page)
        safe_name = page["filename"].lower().replace(" ", "-")
        (path_dir / f"{safe_name}.md").write_text(content)
        views_generated += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"✅ Generated {views_generated} views")
    print(f"📁 Output: {VIEW_DIR}")
    print("\nKey views:")
    print(f"  - {VIEW_DIR / 'start-here.md'}")
    print(f"  - {VIEW_DIR / 'gaps.md'}")
    print(f"  - {VIEW_DIR / 'tier' / '10_foundations.md'}")
    print(f"  - {VIEW_DIR / 'strand' / 'constitutional.md'}")
    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
