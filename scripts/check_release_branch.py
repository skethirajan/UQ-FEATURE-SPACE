"""Pre-bump hook to ensure cz bump is only run on the main branch and by
authorized maintainers/owners."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path


def get_current_branch() -> str:
    """Get the current active git branch."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Could not determine current git branch.")
        sys.exit(1)


def get_git_user_email() -> str:
    """Get the current git user email."""
    try:
        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Could not determine git user.email.")
        sys.exit(1)


def get_maintainer_emails() -> set[str]:
    """Parse maintainer emails from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found.")
        sys.exit(1)

    try:
        # Load pyproject.toml safely using Path
        data = tomllib.loads(pyproject_path.read_text())
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
        sys.exit(1)

    maintainers = data.get("project", {}).get("maintainers", [])
    return {m.get("email") for m in maintainers if "email" in m}


def main() -> int:
    """Check branch and user permissions."""
    # 1. Check Branch
    branch = get_current_branch()
    if branch != "main":
        print("Error: 'cz bump' execution is restricted to the 'main' branch.")
        print(f"Current branch: '{branch}'")
        print("Please switch to 'main' before releasing a new version.")
        return 1

    # 2. Check Maintainer
    user_email = get_git_user_email()
    maintainer_emails = get_maintainer_emails()

    # Identify using the email set in git config
    if user_email not in maintainer_emails:
        print(f"Error: Unauthorized user '{user_email}'.")
        print("Only listed maintainers in pyproject.toml can execute a release.")
        print(f"Allowed emails: {', '.join(maintainer_emails)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
