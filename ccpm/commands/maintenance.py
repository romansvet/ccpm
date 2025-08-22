"""Maintenance and utility commands."""

from pathlib import Path

from ..utils.console import get_emoji, print_error, print_info, print_success, print_warning
from ..utils.shell import run_pm_script


def validate_command() -> None:
    """Validate system integrity (shortcut for /pm:validate)."""
    returncode, stdout, stderr = run_pm_script("validate")

    if stdout:
        print(stdout)
    if stderr and returncode != 0:
        print_error(f"Error: {stderr}")

    if returncode != 0:
        if "Script not found" in stderr:
            # Fallback validation
            print_info("Validating CCPM installation...")

            cwd = Path.cwd()
            issues = []

            # Check .claude directory
            if not (cwd / ".claude").exists():
                issues.append("Missing .claude directory")
            else:
                # Check required subdirectories
                required_dirs = ["scripts/pm", "commands/pm", "agents"]
                for dir_path in required_dirs:
                    if not (cwd / ".claude" / dir_path).exists():
                        issues.append(f"Missing {dir_path}")

            # Check git
            if not (cwd / ".git").exists():
                issues.append("Not a git repository")

            if issues:
                print_warning("\nIssues found:")
                for issue in issues:
                    print(f"  • {issue}")
                print("\nRun 'ccpm setup .' to fix issues")
            else:
                print_success("CCPM installation is valid")
        else:
            raise RuntimeError("Validate command failed")


def clean_command() -> None:
    """Archive completed work (shortcut for /pm:clean)."""
    returncode, stdout, stderr = run_pm_script("clean")

    if stdout:
        print(stdout)
    if stderr and returncode != 0:
        print_error(f"Error: {stderr}")

    if returncode != 0:
        if "Script not found" in stderr:
            print(f"{get_emoji('🧹', '>>>')} Cleaning completed work...")
            print_warning("Clean script not available. Manual cleanup required.")
            print("\nTo clean manually:")
            print("  1. Archive completed epics in .claude/epics/")
            print("  2. Close completed GitHub issues")
            print("  3. Remove old backup files")
        else:
            raise RuntimeError("Clean command failed")


def search_command(query: str) -> None:
    """Search across all content (shortcut for /pm:search).

    Args:
        query: Search term
    """
    returncode, stdout, stderr = run_pm_script("search", [query])

    if stdout:
        print(stdout)
    if stderr and returncode != 0:
        print_error(f"Error: {stderr}")

    if returncode != 0:
        if "Script not found" in stderr:
            # Fallback search using grep
            print_info(f"Searching for: {query}")
            print("=" * 40)

            cwd = Path.cwd()
            claude_dir = cwd / ".claude"

            if not claude_dir.exists():
                print_error("No CCPM installation found")
                return

            import subprocess

            # Search in PRDs
            prds_dir = claude_dir / "prds"
            if prds_dir.exists():
                result = subprocess.run(
                    ["grep", "-r", "-i", query, str(prds_dir)],
                    capture_output=True,
                    text=True,
                )
                if result.stdout:
                    print(f"\n{get_emoji('📄', '>>>')} Found in PRDs:")
                    for line in result.stdout.splitlines()[:10]:
                        print(f"  {line}")

            # Search in epics
            epics_dir = claude_dir / "epics"
            if epics_dir.exists():
                result = subprocess.run(
                    ["grep", "-r", "-i", query, str(epics_dir)],
                    capture_output=True,
                    text=True,
                )
                if result.stdout:
                    print(f"\n{get_emoji('📚', '>>>')} Found in Epics:")
                    for line in result.stdout.splitlines()[:10]:
                        print(f"  {line}")
        else:
            raise RuntimeError("Search command failed")


def help_command() -> None:
    """Display CCPM help and command summary."""
    returncode, stdout, stderr = run_pm_script("help")

    if stdout:
        print(stdout)
    elif returncode != 0 or "Script not found" in stderr:
        # Fallback help text
        print(
            """
📚 CCPM - Claude Code Project Management CLI
=============================================

🎯 Quick Start
  ccpm setup <path>    Set up CCPM in a repository
  ccpm init           Initialize PM system
  ccpm help           Show this help message

📄 PRD Commands
  ccpm list           List all PRDs
  ccpm status         Show project status

🔄 Workflow Commands  
  ccpm sync           Sync with GitHub
  ccpm import         Import GitHub issues

🔧 Maintenance
  ccpm update         Update CCPM to latest version
  ccpm validate       Check system integrity
  ccpm clean          Archive completed work
  ccpm search <term>  Search across all content
  ccpm uninstall      Remove CCPM (preserves existing content)

💡 Tips
  • Use Claude Code commands for full functionality:
    /pm:prd-new <name>    Create new PRD
    /pm:epic-start <name> Start epic execution
    /pm:next             Get next priority task
  
  • View README.md for complete documentation
        """
        )

    if stderr and returncode != 0 and "Script not found" not in stderr:
        print_warning(f"\nWarning: {stderr}")
