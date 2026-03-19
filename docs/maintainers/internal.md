# Maintainer Guide

This section is for project maintainers. It covers internal processes like releasing new versions, managing the repository, and handling security issues.

## Release Process

We use [Commitizen](https://commitizen-tools.github.io/commitizen/) to handle versioning and changelogs automatically.

1.  **Create a Release**:
    Ensure you are on the `main` branch and have pulled the latest changes.

    > [!CAUTION]
    > **Strict Release Rules**:
    > - releases must **ONLY** be performed by designated maintainers.
    > - releases must **ONLY** be performed on the local `main` branch.
    > - **NEVER** run `cz bump` on a feature branch.

    Run the following command locally on the `main` branch:
    ```bash
    cz bump
    ```
    This will:
    - Update the version in `pyproject.toml` and `src/package_name/__init__.py`.
    - Update `CHANGELOG.md`.
    - Create a git tag.

2.  **Push Changes**:
    ```bash
    git push && git push --tags
    ```

3.  **Publish**:
    The GitHub Actions workflow will automatically build and publish the package to PyPI when a new tag is pushed.

## Reviewing Pull Requests

- Ensure all CI checks pass.
- Require at least one approval.
- Verify that `CHANGELOG.md` or release notes are not manually edited (handled by Commitizen/Release Drafter).
