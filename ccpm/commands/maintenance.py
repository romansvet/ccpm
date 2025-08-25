"""Maintenance and utility commands."""

import subprocess
from pathlib import Path

from ..utils.claude import find_claude_cli
from ..utils.console import (
    get_emoji,
    print_error,
    print_info,
    print_warning,
    safe_print,
)
from ..utils.shell import run_pm_script


def invoke_claude_command(command: str, description: str = "") -> None:
    """Invoke a Claude Code command directly with progress indication.

    Args:
        command: The command to pass to Claude (e.g., "/pm:validate")
        description: Optional description to show while executing
    """
    # Check if Claude CLI is available
    claude_cli = find_claude_cli()

    if not claude_cli:
        print_error("Claude Code CLI not found. Please install Claude Code first.")
        print_info("Visit: https://claude.ai/code")
        raise RuntimeError("Claude Code not installed")

    # Check if .claude directory exists
    if not Path(".claude").exists():
        print_error("No CCPM installation found. Run 'ccpm setup .' first.")
        raise RuntimeError("CCPM not installed")

    # Show progress indication
    if description:
        safe_print(f"{get_emoji('⚙️', '[Working...]')} {description}")
    else:
        safe_print(f"{get_emoji('⚙️', '[Working...]')} Executing Claude Code command: {command}")
    
    safe_print("=" * 60)

    # Invoke Claude with the command
    try:
        # Use -p flag to get direct output without interactive session
        result = subprocess.run(
            [claude_cli, "-p", command],
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minute timeout
            cwd=Path.cwd(),
        )

        if result.stdout:
            safe_print(result.stdout)
        if result.stderr:
            print_error(f"Claude stderr: {result.stderr}")

        if result.returncode != 0:
            print_error(f"Command completed with exit code {result.returncode}")
            raise RuntimeError(f"Claude command failed: {command}")
        else:
            safe_print("=" * 60)
            safe_print(f"{get_emoji('✅', '[Done!]')} Command completed successfully")

    except subprocess.TimeoutExpired:
        print_error(f"Command timed out: {command}")
        print_info("Consider breaking large operations into smaller steps")
        raise RuntimeError("Command timeout")
    except Exception as e:
        print_error(f"Failed to execute Claude command: {e}")
        raise


def validate_command() -> None:
    """Validate system integrity (shortcut for /pm:validate)."""
    # Check if Claude is available first
    from ..utils.claude import claude_available

    if not claude_available():
        import os

        if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
            print_warning("Claude Code not available in CI - skipping validate command")
            return
        print_error("Claude Code CLI not found. Please install Claude Code first.")
        print_info("Visit: https://claude.ai/code")
        raise RuntimeError("Claude Code not installed")
    invoke_claude_command("/pm:validate", "Validating system integrity and checking for issues")


def clean_command() -> None:
    """Archive completed work (shortcut for /pm:clean)."""
    # Check if Claude is available first
    from ..utils.claude import claude_available

    if not claude_available():
        import os

        if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
            print_warning("Claude Code not available in CI - skipping clean command")
            return
        print_error("Claude Code CLI not found. Please install Claude Code first.")
        print_info("Visit: https://claude.ai/code")
        raise RuntimeError("Claude Code not installed")
    invoke_claude_command("/pm:clean", "Archiving completed work and cleaning up old files")


def search_command(query: str) -> None:
    """Search across all content (shortcut for /pm:search).

    Args:
        query: Search term
    """
    if not query or not query.strip():
        print_error("Search query is required")
        raise RuntimeError("Empty search query")

    # Check if Claude is available first
    from ..utils.claude import claude_available

    if not claude_available():
        import os

        if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
            print_warning("Claude Code not available in CI - skipping search command")
            return
        print_error("Claude Code CLI not found. Please install Claude Code first.")
        print_info("Visit: https://claude.ai/code")
        raise RuntimeError("Claude Code not installed")

    invoke_claude_command(f"/pm:search {query}", f"Searching for '{query}' across all PRDs, epics, and tasks")


def help_command() -> None:
    """Display CCPM CLI help and command summary."""
    # Always show CLI-focused help instead of PM script help
    safe_print(f"""
{get_emoji('📚', '[CCPM]')} CCPM - Claude Code Project Management CLI
=============================================

{get_emoji('🎯', '[Start]')} Quick Start
  ccpm setup <path>    Set up CCPM in a repository
  ccpm init            Initialize PM system  
  ccpm help            Show this help message

{get_emoji('📄', '[PM]')} Project Management
  ccpm list            List all PRDs
  ccpm status          Show project status and dashboard

{get_emoji('🔄', '[Sync]')} GitHub Integration
  ccpm sync            Sync with GitHub issues
  ccpm import [num]    Import GitHub issues (all or specific)

{get_emoji('🔧', '[Tools]')} Maintenance & Tools
  ccpm update          Update CCPM to latest version
  ccpm validate        Check system integrity
  ccpm clean           Archive completed work
  ccpm search <term>   Search across all content
  ccpm uninstall       Remove CCPM (preserves existing content)

{get_emoji('💡', '[Advanced]')} Advanced Usage with Claude Code
  Once CCPM is set up, use these commands inside Claude Code for full functionality:
  
  /pm:prd-new <name>        Create new product requirements
  /pm:prd-parse <name>      Convert PRD to technical epic
  /pm:epic-decompose <name> Break epic into parallel tasks
  /pm:epic-sync <name>      Push epic and tasks to GitHub
  /pm:epic-start <name>     Launch parallel AI agent execution
  /pm:next                  Get next priority task with context

{get_emoji('📄', '[Docs]')} Documentation
  • View README.md for complete setup and workflow documentation
  • Visit https://github.com/jeremymanning/ccpm for examples and updates
""")
