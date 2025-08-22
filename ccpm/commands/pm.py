"""PM workflow commands."""

from pathlib import Path
from typing import Optional

from ..utils.shell import run_pm_script


def init_command() -> None:
    """Initialize PM system (shortcut for /pm:init)."""
    returncode, stdout, stderr = run_pm_script("init")
    
    if stdout:
        print(stdout)
    if stderr and returncode != 0:
        print(f"❌ Error: {stderr}")
    
    if returncode != 0:
        raise RuntimeError("Init command failed")


def list_command() -> None:
    """List all PRDs (shortcut for /pm:prd-list)."""
    # First check if .claude directory exists
    cwd = Path.cwd()
    if not (cwd / ".claude").exists():
        print("❌ No CCPM installation found. Run 'ccpm setup .' first.")
        raise RuntimeError("CCPM not installed")
    
    # Check for PRDs directory
    prds_dir = cwd / ".claude" / "prds"
    if not prds_dir.exists():
        print("📄 No PRDs found")
        return
    
    # List PRD files
    prd_files = list(prds_dir.glob("*.md"))
    
    if not prd_files:
        print("📄 No PRDs found")
        return
    
    print("📄 Product Requirements Documents:")
    print("=" * 40)
    
    for prd_file in sorted(prd_files):
        name = prd_file.stem
        # Try to read the first line as title
        try:
            with open(prd_file, "r") as f:
                first_line = f.readline().strip()
                if first_line.startswith("#"):
                    title = first_line.lstrip("#").strip()
                else:
                    title = name
        except Exception:
            title = name
        
        print(f"  • {name}: {title}")
    
    print(f"\nTotal: {len(prd_files)} PRD(s)")


def status_command() -> None:
    """Show project status (shortcut for /pm:prd-status)."""
    returncode, stdout, stderr = run_pm_script("status")
    
    if stdout:
        print(stdout)
    if stderr and returncode != 0:
        print(f"❌ Error: {stderr}")
    
    if returncode != 0 and "Script not found" in stderr:
        # Fallback to basic status
        print("📊 Project Status")
        print("=" * 40)
        
        cwd = Path.cwd()
        
        # Check PRDs
        prds_dir = cwd / ".claude" / "prds"
        prd_count = len(list(prds_dir.glob("*.md"))) if prds_dir.exists() else 0
        print(f"📄 PRDs: {prd_count}")
        
        # Check Epics
        epics_dir = cwd / ".claude" / "epics"
        epic_count = len([d for d in epics_dir.iterdir() if d.is_dir()]) if epics_dir.exists() else 0
        print(f"📚 Epics: {epic_count}")
        
        print("\nRun 'ccpm list' to see all PRDs")
        print("Run 'ccpm help' for available commands")


def sync_command() -> None:
    """Sync with GitHub (shortcut for /pm:sync)."""
    returncode, stdout, stderr = run_pm_script("sync")
    
    if stdout:
        print(stdout)
    if stderr and returncode != 0:
        print(f"❌ Error: {stderr}")
    
    if returncode != 0:
        if "Script not found" in stderr:
            print("⚠️ Sync script not found. This command requires a GitHub repository.")
            print("Make sure you have:")
            print("  1. Initialized a git repository")
            print("  2. Set up a GitHub remote")
            print("  3. Authenticated with GitHub (gh auth login)")
        raise RuntimeError("Sync command failed")


def import_command(issue_number: Optional[int] = None) -> None:
    """Import GitHub issues (shortcut for /pm:import).
    
    Args:
        issue_number: Optional specific issue to import
    """
    if issue_number:
        print(f"📥 Importing issue #{issue_number}...")
        # TODO: Implement specific issue import
        print("⚠️ Specific issue import not yet implemented")
    else:
        print("📥 Importing all open issues...")
        # TODO: Implement bulk import
        print("⚠️ Bulk issue import not yet implemented")
    
    print("\nThis feature will be available in a future update.")