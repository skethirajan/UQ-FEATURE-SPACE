#!/usr/bin/env python3
"""
Initialize a new project from the py-scaffold template.

This script renames all occurrences of 'package_name' to your chosen name
and updates author/project metadata.

Usage:
    python scripts/init_project.py

Or make executable and run:
    chmod +x scripts/init_project.py
    ./scripts/init_project.py
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default value."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def replace_in_file(file_path: Path, replacements: dict[str, str]) -> None:
    """Replace all occurrences of keys with values in a file."""
    if not file_path.exists():
        return

    content = file_path.read_text()
    for old, new in replacements.items():
        content = content.replace(old, new)
    file_path.write_text(content)


def rename_directory(old_path: Path, new_path: Path) -> None:
    """Rename a directory."""
    if old_path.exists():
        shutil.move(str(old_path), str(new_path))


def validate_package_name(name: str) -> bool:
    """Validate Python package name."""
    pattern = r"^[a-z][a-z0-9_]*$"
    if not re.match(pattern, name):
        print(f"Error: '{name}' is not a valid Python package name.")
        print("Package names must:")
        print("  - Start with a lowercase letter")
        print("  - Contain only lowercase letters, numbers, and underscores")
        return False
    return True


def main() -> int:
    """Run the project initialization."""
    print("=" * 60)
    print("  py-scaffold Project Initializer")
    print("=" * 60)
    print()

    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Check if already initialized
    if not (project_root / "src" / "package_name").exists():
        print("Error: This project appears to already be initialized.")
        print("The 'src/package_name' directory does not exist.")
        return 1

    # Gather information
    print("Please provide the following information:\n")

    package_name = ""
    while not package_name:
        package_name = get_input("Package name (e.g., my_package)")
        if not validate_package_name(package_name):
            package_name = ""

    description = get_input(
        "Short description", "A Python package for scientific computing"
    )

    author_name = get_input("Author name", "Your Name")
    author_email = get_input("Author email", "you@example.com")
    github_username = get_input("GitHub username", "username")

    # Confirm
    print()
    print("-" * 60)
    print("Summary:")
    print(f"  Package name:    {package_name}")
    print(f"  Description:     {description}")
    print(f"  Author:          {author_name} <{author_email}>")
    print(f"  GitHub:          https://github.com/{github_username}/{package_name}")
    print("-" * 60)
    print()

    confirm = get_input("Proceed with these settings? (y/n)", "y")
    if confirm.lower() != "y":
        print("Aborted.")
        return 0

    print()
    print("Initializing project...")

    # Define replacements
    replacements = {
        "package_name": package_name,
        "Short package description.": description,
        "Your Name": author_name,
        "you@example.com": author_email,
        "username": github_username,
        "[COPYRIGHT HOLDER]": author_name,
        "[YEAR]": str(__import__("datetime").date.today().year),
    }

    # Files to update
    files_to_update = [
        "pyproject.toml",
        "mkdocs.yml",
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "LICENSE",
        ".pre-commit-config.yaml",
        ".github/workflows/ci.yml",
        ".github/workflows/docs.yml",
        ".github/workflows/publish.yml",
        "docs/index.md",
        "docs/about/changelog.md",
        "docs/about/contributors.md",
        "docs/CONTRIBUTING.md",
        "docs/getting-started/installation.md",
        "docs/getting-started/quickstart.md",
        "src/package_name/__init__.py",
        "src/package_name/__init__.py",
        "tests/test_package.py",
        ".github/CODEOWNERS",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/ISSUE_TEMPLATE/config.yaml",
        ".github/ISSUE_TEMPLATE/bug.yaml",
        ".github/ISSUE_TEMPLATE/docs.yaml",
        ".github/ISSUE_TEMPLATE/idea.yaml",
        ".github/ISSUE_TEMPLATE/misc.yaml",
    ]

    # Perform replacements
    for file_path_str in files_to_update:
        if file_path_str == "ruff.toml":
            continue  # Skipped if removed
        fpath = project_root / file_path_str
        if not fpath.exists():
            continue

        content = fpath.read_text("utf-8")

        # Replace package name in all files
        content = content.replace("package_name", package_name)
        content = content.replace("username", github_username)
        content = content.replace("Your Name", author_name)
        content = content.replace("you@example.com", author_email)
        content = content.replace(
            "src/package_name", f"src/{package_name}"
        )  # For hatch/commitizen configs
        content = content.replace(
            "[COPYRIGHT HOLDER]", replacements["[COPYRIGHT HOLDER]"]
        )
        content = content.replace("[YEAR]", replacements["[YEAR]"])
        # Handle hardcoded template values so new projects get fresh placeholders
        content = content.replace(
            "skethirajan/py-scaffold", f"{github_username}/{package_name}"
        )
        content = content.replace(
            "skethirajan", github_username
        )  # catch-all for remaining hardcoded username
        content = content.replace(
            "py-scaffold", package_name
        )  # catch-all for remaining hardcoded repo name
        # Remove hardcoded Codecov token query parameter for new projects
        content = re.sub(r"\?token=[a-zA-Z0-9]+", "", content)

        fpath.write_text(content, "utf-8")
        print(f"  Updated: {file_path_str}")

    # Rename source directory
    old_src = project_root / "src" / "package_name"
    new_src = project_root / "src" / package_name
    if old_src.exists():
        rename_directory(old_src, new_src)
        print(f"  Renamed: src/package_name -> src/{package_name}")

    # Remove this script and scripts directory if empty
    script_path = Path(__file__)
    script_path.unlink()
    print("  Removed: scripts/init_project.py")

    scripts_dir = project_root / "scripts"
    if scripts_dir.exists() and not any(scripts_dir.iterdir()):
        scripts_dir.rmdir()
        print("  Removed: scripts/ (empty)")

    print()
    print("=" * 60)
    print("  Project initialized successfully!")
    print("=" * 60)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
