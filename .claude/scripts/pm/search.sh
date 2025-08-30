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
  results=""
  # Find all .md files and search each one
  if md_files=$(find .claude/prds -name "*.md" 2>/dev/null); then
    for file in $md_files; do
      # Use fixed-string matching and option terminator for security
      if grep -l -F -i -- "$query" "$file" >/dev/null 2>&1; then
        results="$results$file\n"
      fi
    done
  fi
  
  if [ -n "$results" ]; then
    echo "$results" | while IFS= read -r file; do
      if [ -n "$file" ]; then
        name=$(basename "$file" .md)
        matches=$(grep -c -F -i -- "$query" "$file" 2>/dev/null || echo "0")
        echo "  * $name ($matches matches)"
      fi
    done
  else
    echo "  No matches"
  fi
  echo ""
fi

# Search in Epics
if [ -d ".claude/epics" ]; then
  echo "EPICS:"
  results=""
  # Find all epic.md files and search each one
  if epic_files=$(find .claude/epics -name "epic.md" 2>/dev/null); then
    for file in $epic_files; do
      # Use fixed-string matching and option terminator for security
      if grep -l -F -i -- "$query" "$file" >/dev/null 2>&1; then
        results="$results$file\n"
      fi
    done
  fi
  
  if [ -n "$results" ]; then
    echo "$results" | while IFS= read -r file; do
      if [ -n "$file" ]; then
        epic_name=$(basename "$(dirname "$file")")
        matches=$(grep -c -F -i -- "$query" "$file" 2>/dev/null || echo "0")
        echo "  * $epic_name ($matches matches)"
      fi
    done
  else
    echo "  No matches"
  fi
  echo ""
fi

# Search in Tasks
if [ -d ".claude/epics" ]; then
  echo "TASKS:"
  results=""
  # Find all task .md files and search each one
  if task_files=$(find .claude/epics -name "[0-9]*.md" 2>/dev/null | sort | head -10); then
    for file in $task_files; do
      # Use fixed-string matching and option terminator for security
      if grep -l -F -i -- "$query" "$file" >/dev/null 2>&1; then
        results="$results$file\n"
      fi
    done
  fi
  
  if [ -n "$results" ]; then
    echo "$results" | while IFS= read -r file; do
      if [ -n "$file" ]; then
        epic_name=$(basename "$(dirname "$file")")
        task_num=$(basename "$file" .md)
        echo "  * Task #$task_num in $epic_name"
      fi
    done
  else
    echo "  No matches"
  fi
fi

# Summary
if [ -d ".claude" ]; then
  total=0
  # Count all .md files with matches
  if all_files=$(find .claude -name "*.md" 2>/dev/null); then
    for file in $all_files; do
      # Use fixed-string matching and option terminator for security
      if grep -l -F -i -- "$query" "$file" >/dev/null 2>&1; then
        total=$((total + 1))
      fi
    done
  fi
else
  total=0
fi
echo ""
echo "TOTAL FILES WITH MATCHES: $total"

exit 0
