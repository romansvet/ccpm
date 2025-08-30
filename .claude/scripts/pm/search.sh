#!/bin/bash
set -euo pipefail

query="${1:-}"

if [ -z "$query" ]; then
  echo "[ERROR] Please provide a search query"
  echo "Usage: /pm:search <query>"
  exit 1
fi

echo "Searching for '$query'..."
echo ""
echo ""

echo "SEARCH RESULTS FOR: '$query'"
echo "================================"
echo ""

# Helper function to search in a directory
search_directory() {
    local dir="$1"
    local pattern="$2"
    local section="$3"
    
    echo "$section:"
    local found=false
    
    if [ -d "$dir" ]; then
        # Create a temporary file list
        local temp_file="/tmp/search_files_$$"
        find "$dir" -name "$pattern" 2>/dev/null > "$temp_file" || true
        
        if [ -s "$temp_file" ]; then  # File exists and is not empty
            while IFS= read -r file; do
                if [ -f "$file" ] && grep -q -F -i -- "$query" "$file" 2>/dev/null; then
                    if [ "$section" = "PRDs" ]; then
                        name=$(basename "$file" .md)
                        matches=$(grep -c -F -i -- "$query" "$file" 2>/dev/null || echo "0")
                        echo "  * $name ($matches matches)"
                    elif [ "$section" = "EPICS" ]; then
                        epic_name=$(basename "$(dirname "$file")")
                        matches=$(grep -c -F -i -- "$query" "$file" 2>/dev/null || echo "0")
                        echo "  * $epic_name ($matches matches)"
                    elif [ "$section" = "TASKS" ]; then
                        epic_name=$(basename "$(dirname "$file")")
                        task_num=$(basename "$file" .md)
                        echo "  * Task #$task_num in $epic_name"
                    fi
                    found=true
                fi
            done < "$temp_file"
        fi
        rm -f "$temp_file"
    fi
    
    if [ "$found" = false ]; then
        echo "  No matches"
    fi
    echo ""
}

# Search in PRDs
search_directory ".claude/prds" "*.md" "PRDs"

# Search in Epics  
search_directory ".claude/epics" "epic.md" "EPICS"

# Search in Tasks
echo "TASKS:"
found=false
if [ -d ".claude/epics" ]; then
    temp_file="/tmp/search_tasks_$$"
    find ".claude/epics" -name "[0-9]*.md" 2>/dev/null | head -10 > "$temp_file" || true
    
    if [ -s "$temp_file" ]; then
        while IFS= read -r file; do
            if [ -f "$file" ] && grep -q -F -i -- "$query" "$file" 2>/dev/null; then
                epic_name=$(basename "$(dirname "$file")")
                task_num=$(basename "$file" .md)
                echo "  * Task #$task_num in $epic_name"
                found=true
            fi
        done < "$temp_file"
    fi
    rm -f "$temp_file"
fi

if [ "$found" = false ]; then
    echo "  No matches"
fi

# Summary
echo ""
total=0
if [ -d ".claude" ]; then
    # Count matches in all directories
    temp_summary="/tmp/search_summary_$$"
    
    # Find all markdown files
    find ".claude" -name "*.md" 2>/dev/null > "$temp_summary" || true
    
    if [ -s "$temp_summary" ]; then
        while IFS= read -r file; do
            if [ -f "$file" ] && grep -q -F -i -- "$query" "$file" 2>/dev/null; then
                total=$((total + 1))
            fi
        done < "$temp_summary"
    fi
    rm -f "$temp_summary"
fi

echo "TOTAL FILES WITH MATCHES: $total"

exit 0