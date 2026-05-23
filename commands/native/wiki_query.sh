#!/bin/bash
# arifos-wiki — Query TREE777 and federation wikis from shell
# Usage: arifos-wiki <topic|skill|concept> [repo]

WIKI_ROOT="/root/AAA/wiki"
ARIFOS_WIKI="/root/arifOS/wiki"
WEALTH_WIKI="/root/WEALTH/wiki"
QUERY="${1,,}"  # lowercase
REPO="${2:-all}"

search_wiki() {
    local dir="$1"
    local label="$2"
    
    # Search titles
    find "$dir" -name "*.md" -not -path "*/_runtime/*" -not -path "*/raw/*" | while read -r file; do
        local basename=$(basename "$file" .md | tr '_' ' ' | tr '-' ' ')
        if echo "$basename" | grep -qi "$QUERY"; then
            local status=$(grep -m1 "^status:" "$file" 2>/dev/null | cut -d: -f2 | xargs)
            local risk=$(grep -m1 "^risk_band:" "$file" 2>/dev/null | cut -d: -f2 | xargs)
            printf "  %-12s %-30s status=%-10s risk=%s\n" "$label" "$(basename "$file")" "${status:-unknown}" "${risk:-unknown}"
        fi
    done
    
    # Search content (first match only)
    grep -rli "$QUERY" "$dir" --include="*.md" 2>/dev/null | grep -v "_runtime" | grep -v "/raw/" | head -5 | while read -r file; do
        local basename=$(basename "$file" .md)
        local excerpt=$(grep -i "$QUERY" "$file" 2>/dev/null | head -1 | cut -c1-80)
        printf "  %-12s %-30s excerpt: %s...\n" "$label" "$basename" "$excerpt"
    done
}

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     ARIFOS WIKI QUERY — $QUERY"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

if [ "$REPO" = "all" ] || [ "$REPO" = "aaa" ]; then
    echo "[TREE777 / AAA]"
    search_wiki "$WIKI_ROOT" "TREE777"
    echo ""
fi

if [ "$REPO" = "all" ] || [ "$REPO" = "arifos" ]; then
    echo "[arifOS Ω-Wiki]"
    search_wiki "$ARIFOS_WIKI" "arifOS"
    echo ""
fi

if [ "$REPO" = "all" ] || [ "$REPO" = "wealth" ]; then
    echo "[WEALTH Wiki]"
    search_wiki "$WEALTH_WIKI" "WEALTH"
    echo ""
fi

# Also search skills directories
echo "[SKILLS]"
for skill_dir in /root/AAA/wiki/skills /root/arifOS/skills /root/geox/skills /root/.agents/skills /root/.claude/skills; do
    if [ -d "$skill_dir" ]; then
        local repo_name=$(basename $(dirname "$skill_dir"))
        find "$skill_dir" -name "SKILL.md" -o -name "*.md" 2>/dev/null | while read -r file; do
            local basename=$(basename "$file" .md | tr '_' ' ' | tr '-' ' ')
            if echo "$basename" | grep -qi "$QUERY"; then
                printf "  %-12s %-30s %s\n" "SKILL" "$(basename $(dirname "$file"))" "$repo_name"
            fi
        done
    fi
done

echo ""
