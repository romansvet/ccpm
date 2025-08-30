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

# Search in PRDs
if [ -d ".claude/prds" ]; then
  echo "PRDs:"
  found_matches=false
  
  # Use a simple approach that works across platforms
  if [ "$(find .claude/prds -name "*.md" 2>/dev/null | wc -l)" -gt 0 ]; then
    for file in .claude/prds/*.md; do
      # Check if file actually exists (glob didn't match)
      if [ -f "$file" ]; then
        # Use fixed-string matching and option terminator for security
        if grep -q -F -i -- "$query" "$file" 2>/dev/null; then
          name=$(basename "$file" .md)
          matches=$(grep -c -F -i -- "$query" "$file" 2>/dev/null || echo "0")
          echo "  * $name ($matches matches)"
          found_matches=true
        fi
      fi
    done
  fi
  
  if [ "$found_matches" = false ]; then
    echo "  No matches"
  fi
  echo ""
fi

# Search in Epics
if [ -d ".claude/epics" ]; then
  echo "EPICS:"
  found_matches=false
  
  # Find all epic.md files
  if [ "$(find .claude/epics -name "epic.md" 2>/dev/null | wc -l)" -gt 0 ]; then
    find .claude/epics -name "epic.md" 2>/dev/null > /tmp/epic_files_$$ || true
    while IFS= read -r file; do
      if [ -f "$file" ]; then
        # Use fixed-string matching and option terminator for security
        if grep -q -F -i -- "$query" "$file" 2>/dev/null; then
          epic_name=$(basename "$(dirname "$file")")
          matches=$(grep -c -F -i -- "$query" "$file" 2>/dev/null || echo "0")
          echo "  * $epic_name ($matches matches)"
          found_matches=true
        fi
      fi
    done < /tmp/epic_files_$$
    rm -f /tmp/epic_files_$$
  fi
  
  if [ "$found_matches" = false ]; then
    echo "  No matches"
  fi
  echo ""
fi

# Search in Tasks
if [ -d ".claude/epics" ]; then
  echo "TASKS:"
  found_matches=false
  
  # Find all task .md files
  if [ "$(find .claude/epics -name "[0-9]*.md" 2>/dev/null | wc -l)" -gt 0 ]; then
    find .claude/epics -name "[0-9]*.md" 2>/dev/null | sort | head -10 > /tmp/task_files_$$ || true
    while IFS= read -r file; do
      if [ -f "$file" ]; then
        # Use fixed-string matching and option terminator for security
        if grep -q -F -i -- "$query" "$file" 2>/dev/null; then
          epic_name=$(basename "$(dirname "$file")")
          task_num=$(basename "$file" .md)
          echo "  * Task #$task_num in $epic_name"
          found_matches=true
        fi
      fi
    done < /tmp/task_files_$$
    rm -f /tmp/task_files_$$
  fi
  
  if [ "$found_matches" = false ]; then
    echo "  No matches"
  fi
fi

# Summary
if [ -d ".claude" ]; then
  total=0
  # Count all .md files with matches
  if [ "$(find .claude -name "*.md" 2>/dev/null | wc -l)" -gt 0 ]; then
    find .claude -name "*.md" 2>/dev/null > /tmp/all_files_$$ || true
    while IFS= read -r file; do
      if [ -f "$file" ]; then
        # Use fixed-string matching and option terminator for security
        if grep -q -F -i -- "$query" "$file" 2>/dev/null; then
          total=$((total + 1))
        fi
      fi
    done < /tmp/all_files_$$
    rm -f /tmp/all_files_$$
  fi
else
  total=0
fi
echo ""
echo "TOTAL FILES WITH MATCHES: $total"

exit 0