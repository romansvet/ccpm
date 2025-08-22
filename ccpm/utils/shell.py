"""Shell command execution utilities."""

import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


def run_pm_script(script_name: str, args: Optional[List[str]] = None, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Execute PM shell scripts.

    Args:
        script_name: Name of the script (without .sh extension)
        args: Optional arguments to pass to the script
        cwd: Working directory for script execution

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    if cwd is None:
        cwd = Path.cwd()

    script_path = cwd / ".claude" / "scripts" / "pm" / f"{script_name}.sh"

    if not script_path.exists():
        return 1, "", f"Script not found: {script_path}"

    cmd = ["bash", str(script_path)]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Script timed out: {script_name}"
    except Exception as e:
        return 1, "", f"Error running script: {e}"


def run_command(
    args: List[str], cwd: Optional[Path] = None, timeout: int = 60, check: bool = False
) -> Tuple[int, str, str]:
    """Run a shell command and return the result.

    Args:
        args: Command and arguments as list
        cwd: Working directory for command
        timeout: Command timeout in seconds
        check: Whether to raise exception on non-zero return

    Returns:
        Tuple of (return_code, stdout, stderr)

    Raises:
        subprocess.CalledProcessError: If check=True and command fails
    """
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=check
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout} seconds"
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return e.returncode, e.stdout, e.stderr
    except FileNotFoundError:
        return 1, "", f"Command not found: {args[0]}"
    except Exception as e:
        return 1, "", f"Error running command: {e}"
