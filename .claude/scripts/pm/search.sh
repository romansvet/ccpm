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
echo "PRDs:"
if [ -d ".claude/prds" ]; then
  # Simple approach: use grep directly on all files
  if grep -l -F -i -- "$query" .claude/prds/*.md 2>/dev/null; then
    # If grep found files, process them
    grep -l -F -i -- "$query" .claude/prds/*.md 2>/dev/null | while read -r file; do
      name=$(basename "$file" .md)
      matches=$(grep -c -F -i -- "$query" "$file" 2>/dev/null || echo "0")
      echo "  * $name ($matches matches)"
    done
  else
    echo "  No matches"
  fi
else
  echo "  No matches"
fi
echo ""

# Search in Epics
echo "EPICS:"
if [ -d ".claude/epics" ]; then
  # Simple approach: use grep directly
  if grep -l -F -i -- "$query" .claude/epics/*/epic.md 2>/dev/null; then
    # If grep found files, process them
    grep -l -F -i -- "$query" .claude/epics/*/epic.md 2>/dev/null | while read -r file; do
      epic_name=$(basename "$(dirname "$file")")
      matches=$(grep -c -F -i -- "$query" "$file" 2>/dev/null || echo "0")
      echo "  * $epic_name ($matches matches)"
    done
  else
    echo "  No matches"
  fi
else
  echo "  No matches"
fi
echo ""

# Search in Tasks
echo "TASKS:"
if [ -d ".claude/epics" ]; then
  # Simple approach: use grep directly
  if grep -l -F -i -- "$query" .claude/epics/*/[0-9]*.md 2>/dev/null; then
    # If grep found files, process them (limit to first 10)
    grep -l -F -i -- "$query" .claude/epics/*/[0-9]*.md 2>/dev/null | head -10 | while read -r file; do
      epic_name=$(basename "$(dirname "$file")")
      task_num=$(basename "$file" .md)
      echo "  * Task #$task_num in $epic_name"
    done
  else
    echo "  No matches"
  fi
else
  echo "  No matches"
fi

# Summary - count total matches
echo ""
if [ -d ".claude" ]; then
  total=$(grep -l -F -i -- "$query" .claude/prds/*.md .claude/epics/*/epic.md .claude/epics/*/[0-9]*.md 2>/dev/null | wc -l || echo "0")
else
  total=0
fi
echo "TOTAL FILES WITH MATCHES: $total"

exit 0