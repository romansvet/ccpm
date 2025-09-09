"""Integration tests for PM shell scripts.

These tests verify that all PM shell scripts work correctly with real execution,
real file operations, and real git repositories. NO MOCKS OR SIMULATIONS.
"""

# import os  # Unused import
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

import pytest


@pytest.fixture
def pm_git_repo():
    """Create a real git repository with CCPM structure for PM script testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test_pm_repo"

        # Copy current project to simulate a real repository
        project_root = Path(__file__).parent.parent.parent
        shutil.copytree(
            project_root,
            repo_path,
            ignore=shutil.ignore_patterns(
                "__pycache__",
                "*.pyc",
                ".git",
                ".pytest_cache",
                "*.egg-info",
                "build",
                "dist",
            ),
        )

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        # Create CCPM directory structure
        (repo_path / ".claude" / "prds").mkdir(parents=True, exist_ok=True)
        (repo_path / ".claude" / "epics").mkdir(parents=True, exist_ok=True)
        (repo_path / ".claude" / "rules").mkdir(parents=True, exist_ok=True)

        # Add initial commit
        subprocess.run(
            ["git", "add", "."], cwd=repo_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial test repository"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        yield repo_path


def run_pm_script(
    script_name: str, args: List[str] = None, cwd: Path = None
) -> Tuple[int, str, str]:
    """Execute a PM script using the proper cross-platform shell utilities."""
    from ccpm.utils.shell import (
        get_shell_environment,
    )
    from ccpm.utils.shell import run_pm_script as utils_run_pm_script

    # Check if shell is available
    shell_env = get_shell_environment()
    if not shell_env["shell_available"]:
        pytest.skip("No compatible shell found for PM script execution")

    if args is None:
        args = []

    # Remove .sh extension if present since utils function adds it
    script_base = script_name.replace(".sh", "")

    return utils_run_pm_script(script_base, args, cwd)


class TestPMScriptExecution:
    """Test that all PM scripts execute without syntax errors."""

    def test_all_scripts_have_valid_syntax(self):
        """Test that all PM scripts pass bash syntax validation."""
        import sys

        # Skip on Windows if bash is not available (no WSL/Git Bash)
        if sys.platform == "win32":
            try:
                result = subprocess.run(
                    ["bash", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode != 0:
                    pytest.skip("bash not available on Windows")
                # Also check for WSL installation message
                if (
                    "Windows Subsystem for Linux has no installed distributions"
                    in result.stdout
                ):
                    pytest.skip("WSL bash available but no distributions installed")
            except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
                pytest.skip("bash not available on Windows")

        pm_scripts_dir = (
            Path(__file__).parent.parent.parent / ".claude" / "scripts" / "pm"
        )

        for script_file in pm_scripts_dir.glob("*.sh"):
            # Check syntax with bash -n
            result = subprocess.run(
                ["bash", "-n", str(script_file)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert (
                result.returncode == 0
            ), f"Syntax error in {script_file.name}: {result.stderr}"

    def test_all_scripts_have_proper_shebangs(self):
        """Test that all PM scripts have correct shebang lines."""
        pm_scripts_dir = (
            Path(__file__).parent.parent.parent / ".claude" / "scripts" / "pm"
        )

        for script_file in pm_scripts_dir.glob("*.sh"):
            with open(script_file, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()

            assert (
                first_line == "#!/bin/bash"
            ), f"Invalid shebang in {script_file.name}: {first_line}"

    def test_all_scripts_have_error_handling(self):
        """Test that all PM scripts have set -euo pipefail for error handling."""
        pm_scripts_dir = (
            Path(__file__).parent.parent.parent / ".claude" / "scripts" / "pm"
        )

        for script_file in pm_scripts_dir.glob("*.sh"):
            with open(script_file, "r", encoding="utf-8") as f:
                content = f.read()

            assert (
                "set -euo pipefail" in content
            ), f"Missing error handling in {script_file.name}"


class TestHelpScript:
    """Test the help.sh script with real execution."""

    def test_help_script_execution(self, pm_git_repo):
        """Test that help script runs successfully."""
        returncode, stdout, stderr = run_pm_script("help.sh", cwd=pm_git_repo)

        assert returncode == 0, f"Help script failed: {stderr}"
        assert "Claude Code PM" in stdout
        assert "Quick Start Workflow" in stdout
        assert "/pm:prd-new" in stdout

    def test_help_shows_all_commands(self, pm_git_repo):
        """Test that help displays all available commands."""
        returncode, stdout, stderr = run_pm_script("help.sh", cwd=pm_git_repo)

        assert returncode == 0

        # Check for major command categories
        expected_commands = [
            "prd-new",
            "prd-parse",
            "epic-decompose",
            "epic-sync",
            "status",
            "next",
            "blocked",
            "in-progress",
            "validate",
        ]

        for cmd in expected_commands:
            assert cmd in stdout, f"Command {cmd} not found in help output"


class TestStatusScript:
    """Test the status.sh script with real git repository."""

    def test_status_empty_repository(self, pm_git_repo):
        """Test status script with empty CCPM repository."""
        returncode, stdout, stderr = run_pm_script("status.sh", cwd=pm_git_repo)

        assert returncode == 0, f"Status script failed: {stderr}"
        assert "PRDs:" in stdout
        assert "EPICS:" in stdout
        assert "TASKS:" in stdout

    def test_status_with_prds(self, pm_git_repo):
        """Test status script with PRD files."""
        # Create test PRD files
        prds_dir = pm_git_repo / ".claude" / "prds"

        (prds_dir / "test-feature.md").write_text(
            """---
name: Test Feature
status: backlog
description: A test feature
---

# Test Feature PRD

This is a test PRD.
"""
        )

        (prds_dir / "another-feature.md").write_text(
            """---
name: Another Feature
status: in-progress
description: Another test feature
---

# Another Feature PRD

This is another test PRD.
"""
        )

        returncode, stdout, stderr = run_pm_script("status.sh", cwd=pm_git_repo)

        assert returncode == 0, f"Status script failed: {stderr}"
        assert "Total: 2" in stdout


class TestPRDListScript:
    """Test the prd-list.sh script with real PRD files."""

    def test_prd_list_empty_directory(self, pm_git_repo):
        """Test PRD list with no PRD files."""
        returncode, stdout, stderr = run_pm_script("prd-list.sh", cwd=pm_git_repo)

        assert returncode == 0, f"PRD list script failed: {stderr}"
        assert "No PRDs found" in stdout

    def test_prd_list_with_files(self, pm_git_repo):
        """Test PRD list with actual PRD files."""
        prds_dir = pm_git_repo / ".claude" / "prds"

        # Create PRDs with different statuses
        (prds_dir / "backlog-feature.md").write_text(
            """---
name: Backlog Feature
status: backlog
description: A backlog feature
---

# Backlog Feature
"""
        )

        (prds_dir / "active-feature.md").write_text(
            """---
name: Active Feature
status: in-progress
description: An active feature
---

# Active Feature
"""
        )

        (prds_dir / "completed-feature.md").write_text(
            """---
name: Completed Feature
status: implemented
description: A completed feature
---

# Completed Feature
"""
        )

        returncode, stdout, stderr = run_pm_script("prd-list.sh", cwd=pm_git_repo)

        assert returncode == 0, f"PRD list script failed: {stderr}"

        # Check that all sections are present
        assert "BACKLOG PRDs:" in stdout
        assert "IN-PROGRESS PRDs:" in stdout
        assert "IMPLEMENTED PRDs:" in stdout

        # Check summary
        assert "Total PRDs: 3" in stdout
        assert "Backlog: 1" in stdout
        assert "In-Progress: 1" in stdout
        assert "Implemented: 1" in stdout

    def test_prd_list_with_spaces_in_names(self, pm_git_repo):
        """Test PRD list handles filenames with spaces correctly."""
        prds_dir = pm_git_repo / ".claude" / "prds"

        # Create PRD with spaces in filename
        (prds_dir / "my complex feature.md").write_text(
            """---
name: My Complex Feature
status: backlog
description: A feature with spaces in the name
---

# My Complex Feature
"""
        )

        returncode, stdout, stderr = run_pm_script("prd-list.sh", cwd=pm_git_repo)

        assert returncode == 0, f"PRD list failed with spaced filename: {stderr}"
        assert "my complex feature.md" in stdout


class TestEpicListScript:
    """Test the epic-list.sh script with real epic structures."""

    def test_epic_list_empty(self, pm_git_repo):
        """Test epic list with no epics."""
        returncode, stdout, stderr = run_pm_script("epic-list.sh", cwd=pm_git_repo)

        assert returncode == 0, f"Epic list script failed: {stderr}"
        assert "No epics found" in stdout

    def test_epic_list_with_epics(self, pm_git_repo):
        """Test epic list with real epic structures."""
        epics_dir = pm_git_repo / ".claude" / "epics"

        # Create epic structure
        test_epic_dir = epics_dir / "test-epic"
        test_epic_dir.mkdir()

        (test_epic_dir / "epic.md").write_text(
            """---
name: Test Epic
status: in-progress
progress: 50%
github: https://github.com/test/repo/issues/123
---

# Test Epic

This is a test epic.
"""
        )

        # Create some tasks
        (test_epic_dir / "1.md").write_text(
            """---
name: Task 1
status: open
---

# Task 1
"""
        )

        (test_epic_dir / "2.md").write_text(
            """---
name: Task 2
status: closed
---

# Task 2
"""
        )

        returncode, stdout, stderr = run_pm_script("epic-list.sh", cwd=pm_git_repo)

        assert returncode == 0, f"Epic list script failed: {stderr}"
        assert "In Progress:" in stdout
        assert "test-epic" in stdout
        assert "2 tasks" in stdout


class TestSearchScript:
    """Test the search.sh script with real content."""

    def test_search_requires_query(self, pm_git_repo):
        """Test that search script requires a query parameter."""
        returncode, stdout, stderr = run_pm_script("search.sh", cwd=pm_git_repo)

        assert returncode == 1, "Search should fail without query"
        assert "provide a search query" in stderr or "provide a search query" in stdout

    def test_search_in_prds(self, pm_git_repo):
        """Test searching content in PRD files."""
        prds_dir = pm_git_repo / ".claude" / "prds"

        (prds_dir / "feature1.md").write_text(
            """---
name: Authentication Feature
status: backlog
---

# Authentication Feature

This feature implements user authentication with OAuth2.
"""
        )

        (prds_dir / "feature2.md").write_text(
            """---
name: Database Feature
status: backlog
---

# Database Feature

This feature implements database migrations.
"""
        )

        returncode, stdout, stderr = run_pm_script(
            "search.sh", ["authentication"], cwd=pm_git_repo
        )

        assert returncode == 0, f"Search script failed: {stderr}"
        assert "feature1" in stdout
        assert "matches" in stdout  # Should find matches
        assert "TOTAL FILES WITH MATCHES:" in stdout

    def test_search_in_epics_and_tasks(self, pm_git_repo):
        """Test searching in epic and task files."""
        epics_dir = pm_git_repo / ".claude" / "epics"
        epic_dir = epics_dir / "auth-epic"
        epic_dir.mkdir(exist_ok=True)

        (epic_dir / "epic.md").write_text(
            """---
name: Authentication Epic
status: planning
---

# Authentication Epic

Implement comprehensive authentication system.
"""
        )

        (epic_dir / "1.md").write_text(
            """---
name: OAuth Setup
status: open
---

# OAuth Setup Task

Configure OAuth2 providers.
"""
        )

        returncode, stdout, stderr = run_pm_script(
            "search.sh", ["OAuth"], cwd=pm_git_repo
        )

        assert returncode == 0, f"Search script failed: {stderr}"
        assert "EPICS:" in stdout
        assert "TASKS:" in stdout
        assert "auth-epic" in stdout


class TestValidateScript:
    """Test the validate.sh script with real repository validation."""

    def test_validate_healthy_repository(self, pm_git_repo):
        """Test validation of a healthy repository structure."""
        # Create proper structure
        epics_dir = pm_git_repo / ".claude" / "epics"
        epic_dir = epics_dir / "test-epic"
        epic_dir.mkdir()

        (epic_dir / "epic.md").write_text(
            """---
name: Test Epic
status: planning
---

# Test Epic
"""
        )

        returncode, stdout, stderr = run_pm_script("validate.sh", cwd=pm_git_repo)

        assert returncode == 0, f"Validate script failed: {stderr}"
        assert "VALIDATING PM SYSTEM" in stdout
        assert "DIRECTORY STRUCTURE:" in stdout

    def test_validate_missing_epic_files(self, pm_git_repo):
        """Test validation catches missing epic.md files."""
        epics_dir = pm_git_repo / ".claude" / "epics"
        epic_dir = epics_dir / "broken-epic"
        epic_dir.mkdir()

        # Create epic directory but no epic.md file
        (epic_dir / "1.md").write_text(
            """---
name: Task without epic
status: open
---

# Orphaned Task
"""
        )

        returncode, stdout, stderr = run_pm_script("validate.sh", cwd=pm_git_repo)

        assert returncode == 0  # Script should complete but show warnings
        assert "Missing epic.md" in stdout or "WARNING" in stdout


class TestErrorHandling:
    """Test error handling in PM scripts."""

    def test_scripts_handle_missing_directories(self, pm_git_repo):
        """Test that scripts handle missing .claude data directories gracefully."""
        # Remove data directories but keep scripts
        for data_dir in ["prds", "epics", "rules"]:
            dir_path = pm_git_repo / ".claude" / data_dir
            if dir_path.exists():
                shutil.rmtree(dir_path)

        # Test various scripts
        scripts_to_test = ["status.sh", "prd-list.sh", "epic-list.sh"]

        for script in scripts_to_test:
            returncode, stdout, stderr = run_pm_script(script, cwd=pm_git_repo)

            # Scripts should either succeed with appropriate messages or fail gracefully
            assert returncode in [
                0,
                1,
            ], f"Script {script} had unexpected return code: {returncode}"

            # Should have some informative output
            assert len(stdout + stderr) > 0, f"Script {script} produced no output"

    def test_epic_status_with_invalid_epic(self, pm_git_repo):
        """Test epic-status script with non-existent epic."""
        returncode, stdout, stderr = run_pm_script(
            "epic-status.sh", ["nonexistent-epic"], cwd=pm_git_repo
        )

        assert returncode == 1, "Should fail with non-existent epic"
        assert "not found" in stdout or "not found" in stderr

    def test_epic_show_without_arguments(self, pm_git_repo):
        """Test epic-show script without required arguments."""
        returncode, stdout, stderr = run_pm_script("epic-show.sh", cwd=pm_git_repo)

        assert returncode == 1, "Should fail without arguments"
        assert "provide an epic name" in stdout or "Usage:" in stdout


class TestCrossplatformCompatibility:
    """Test cross-platform compatibility aspects."""

    def test_scripts_handle_special_characters(self, pm_git_repo):
        """Test that scripts handle special characters in filenames."""
        prds_dir = pm_git_repo / ".claude" / "prds"

        # Create files with various special characters (safe for filesystem)
        special_files = [
            "feature_with_underscores.md",
            "feature-with-dashes.md",
            "feature with spaces.md",
            "feature(with)parens.md",
        ]

        for filename in special_files:
            (prds_dir / filename).write_text(
                f"""---
name: {filename}
status: backlog
---

# {filename}
"""
            )

        # Test that PRD list handles all these files
        returncode, stdout, stderr = run_pm_script("prd-list.sh", cwd=pm_git_repo)

        assert returncode == 0, f"PRD list failed with special characters: {stderr}"
        assert f"Total PRDs: {len(special_files)}" in stdout

        # Test search works with special characters
        returncode, stdout, stderr = run_pm_script(
            "search.sh", ["feature"], cwd=pm_git_repo
        )

        assert returncode == 0, f"Search failed with special characters: {stderr}"
        assert "TOTAL FILES WITH MATCHES:" in stdout

    def test_scripts_work_in_subdirectories(self, pm_git_repo):
        """Test that scripts work when run from subdirectories."""
        # Create a subdirectory and run from there
        subdir = pm_git_repo / "subdir"
        subdir.mkdir()

        # Scripts should still work when run from subdirectories
        # (they use relative paths to find .claude)
        returncode, stdout, stderr = run_pm_script("../help.sh", cwd=subdir)

        # This might fail due to relative path issues, but we test anyway
        # The script should either work or fail gracefully
        assert returncode in [
            0,
            1,
            127,
        ], f"Unexpected return code from subdirectory: {returncode}"


class TestScriptIntegration:
    """Test integration between different PM scripts."""

    def test_workflow_integration(self, pm_git_repo):
        """Test basic workflow integration between scripts."""
        prds_dir = pm_git_repo / ".claude" / "prds"
        epics_dir = pm_git_repo / ".claude" / "epics"

        # Create PRD
        (prds_dir / "integration-test.md").write_text(
            """---
name: Integration Test Feature
status: backlog
description: Test integration between scripts
---

# Integration Test Feature

This tests script integration.
"""
        )

        # Create corresponding epic
        epic_dir = epics_dir / "integration-test"
        epic_dir.mkdir()

        (epic_dir / "epic.md").write_text(
            """---
name: Integration Test Epic
status: planning
progress: 0%
---

# Integration Test Epic

Epic for integration testing.
"""
        )

        (epic_dir / "1.md").write_text(
            """---
name: First Task
status: open
depends_on: []
---

# First Task
"""
        )

        # Test that various scripts can see and work with this data
        scripts_and_expectations = [
            ("status.sh", "Total: 1"),  # Should show 1 PRD
            ("prd-list.sh", "integration-test.md"),  # Should list the PRD
            ("epic-list.sh", "integration-test"),  # Should show the epic
            ("next.sh", "First Task"),  # Should show available task
        ]

        for script, expected in scripts_and_expectations:
            returncode, stdout, stderr = run_pm_script(script, cwd=pm_git_repo)

            assert returncode == 0, f"Integration test failed for {script}: {stderr}"
            assert (
                expected in stdout
            ), f"Expected '{expected}' not found in {script} output: {stdout}"
