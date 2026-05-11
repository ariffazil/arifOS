#!/bin/bash
# scan-carry-forward.sh — Find all carry-forward items across memory files
# Usage: bash scripts/scan-carry-forward.sh [memory_dir]
# Output: Structured list of carry-forward items with status

MEMORY_DIR="${1:-$HOME/.openclaw/workspace/memory}"

echo "# Carry-Forward Audit — $(TZ='Asia/Kuala_Lumpur' date '+%Y-%m-%d %H:%M MYT')"
echo ""
echo "| Item | First Seen | Last Seen | Status |"
echo "|------|-----------|-----------|--------|"

# Extract carry-forward sections from all dated memory files
for f in $(ls "$MEMORY_DIR"/2*.md 2>/dev/null | sort); do
    date=$(basename "$f" .md)
    in_section=false
    while IFS= read -r line; do
        if echo "$line" | grep -qi "^## Carry Forward"; then
            in_section=true
            continue
        fi
        if echo "$line" | grep -q "^## " && [ "$in_section" = true ]; then
            in_section=false
        fi
        if [ "$in_section" = true ] && echo "$line" | grep -q "^- "; then
            item=$(echo "$line" | sed 's/^- //')
            echo "| $item | $date | — | ⚠️ OPEN |"
        fi
    done < "$f"
done

echo ""
echo "---"
echo "Files scanned: $(ls "$MEMORY_DIR"/2*.md 2>/dev/null | wc -l)"
