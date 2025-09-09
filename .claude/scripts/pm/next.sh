#!/bin/bash
set -euo pipefail
echo "Getting status..."
echo ""
echo ""

echo "TASK Next Available Tasks"
echo "======================="
echo ""

# Find tasks that are open and have no dependencies or whose dependencies are closed
found=0

for epic_dir in .claude/epics/*/; do
  [ -d "$epic_dir" ] || continue
  epic_name=$(basename "$epic_dir")

  for task_file in "$epic_dir"[0-9]*.md; do
    [ -f "$task_file" ] || continue

    # Check if task is open
    status=$(grep "^status:" "$task_file" | head -1 | sed 's/^status: *//' || true)
    [ "$status" != "open" ] && [ -n "$status" ] && continue

    # Check dependencies
    deps=$(grep "^depends_on:" "$task_file" | head -1 | sed 's/^depends_on: *\[//' | sed 's/\]//' || true)

    # If no dependencies or empty, task is available
    if [ -z "$deps" ] || [ "$deps" = "depends_on:" ]; then
      task_name=$(grep "^name:" "$task_file" | head -1 | sed 's/^name: *//' || true)
      task_num=$(basename "$task_file" .md)
      parallel=$(grep "^parallel:" "$task_file" | head -1 | sed 's/^parallel: *//' || true)

      echo "OK Ready: #$task_num - $task_name"
      echo "   Epic: $epic_name"
      [ "$parallel" = "true" ] && echo "   IN-PROGRESS Can run in parallel"
      echo ""
      found=$((found + 1))
    fi
  done
done

if [ $found -eq 0 ]; then
  echo "No available tasks found."
  echo ""
  echo "TIP Suggestions:"
  echo "  * Check blocked tasks: /pm:blocked"
  echo "  * View all tasks: /pm:epic-list"
fi

echo ""
echo "STATUS Summary: $found tasks ready to start"

exit 0
