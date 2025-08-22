"""Console output utilities with cross-platform support."""

import sys


def get_emoji(emoji: str, fallback: str = "") -> str:
    """Get emoji or fallback for Windows console compatibility.
    
    Args:
        emoji: The emoji character to use
        fallback: ASCII fallback for Windows
        
    Returns:
        The emoji on Unix systems, fallback on Windows
    """
    if sys.platform == "win32":
        return fallback
    return emoji


def print_error(message: str) -> None:
    """Print an error message with platform-appropriate formatting.
    
    Args:
        message: The error message to print
    """
    error_prefix = get_emoji("❌", "[ERROR]")
    try:
        print(f"{error_prefix} {message}", file=sys.stderr)
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        safe_message = message.encode("ascii", "replace").decode("ascii")
        print(f"[ERROR] {safe_message}", file=sys.stderr)


def print_success(message: str) -> None:
    """Print a success message with platform-appropriate formatting.
    
    Args:
        message: The success message to print
    """
    success_prefix = get_emoji("✅", "[OK]")
    try:
        print(f"{success_prefix} {message}")
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        safe_message = message.encode("ascii", "replace").decode("ascii")
        print(f"[OK] {safe_message}")


def print_info(message: str) -> None:
    """Print an info message with platform-appropriate formatting.
    
    Args:
        message: The info message to print
    """
    info_prefix = get_emoji("🔍", "[INFO]")
    try:
        print(f"{info_prefix} {message}")
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        safe_message = message.encode("ascii", "replace").decode("ascii")
        print(f"[INFO] {safe_message}")


def print_warning(message: str) -> None:
    """Print a warning message with platform-appropriate formatting.
    
    Args:
        message: The warning message to print
    """
    warning_prefix = get_emoji("⚠️", "[WARN]")
    try:
        print(f"{warning_prefix} {message}")
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        safe_message = message.encode("ascii", "replace").decode("ascii")
        print(f"[WARN] {safe_message}")