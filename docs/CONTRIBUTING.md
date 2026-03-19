# Developer Guide

Welcome! This guide covers everything you need to know to set up your development environment and contribute to the project.

## Table of Contents

- [Environment Setup](#environment-setup)
  - [Local Development](#local-development)
  - [HPC Clusters](#hpc-clusters)
- [Development Workflow](#development-workflow)
  - [Git Process](#git-process)
  - [Running Quality Checks](#running-quality-checks)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)

---

## Environment Setup

We recommend using **uv** for package management due to its speed (10-100x faster than pip).

### Local Development

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/skethirajan/uq_feature.git
cd uq_feature

# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package with development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### HPC Clusters

On HPC systems (e.g., NERSC, Kestrel), home directories have limited space. Install packages in your scratch directory.

#### One-Time Setup

```bash
# Install uv in your $HOME directory
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=$HOME/.local/bin sh

# Add to your .bashrc or .bash_profile (if not in the $PATH already)
export PATH="$HOME/.local/bin:$PATH"

# Recommended: Store uv cache in scratch to avoid hitting quota limits
export UV_CACHE_DIR="${SCRATCH}/uv-cache"
```

#### Per-Project Setup

```bash
# Clone the repository
cd $SCRATCH/projects  # or your preferred scratch location
git clone https://github.com/skethirajan/uq_feature.git
cd uq_feature

# Create virtual environment in scratch
uv venv $SCRATCH/venvs/uq_feature

# Activate and install
source $SCRATCH/venvs/uq_feature/bin/activate
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

> [!TIP]
> On NERSC, your scratch directory is at `$PSCRATCH` or `/pscratch/sd/<first-letter>/<skethirajan>/`.

---

## Development Workflow

### Git Process

1.  **Fork and Clone**:
    Fork the repository to your account and clone it locally.

2.  **Create a Branch**:
    ```bash
    git checkout -b feature/your-feature-name
    ```

3.  **Make Changes**:
    Ensure your code passes all checks before committing.

4.  **Commit**:
    We use [Conventional Commits](https://www.conventionalcommits.org/).

    > [!TIP]
    > **Interactive Commit**:
    > Run `cz commit` to launch an interactive wizard that helps you build a valid commit message.
    >
    > If pre-commit hooks fail (e.g. formatting fixes), stage the changes (`git add .`) and run `cz commit --retry` to retry with your last message.

    - `feat:` — New feature
    - `fix:` — Bug fix
    - `docs:` — Documentation changes
    - `refactor:` — Code refactoring
    - `test:` — Adding/updating tests

5.  **Push and PR**:
    Push to your fork and open a Pull Request against the `main` branch.

    > [!IMPORTANT]
    > **Do NOT push tags or run `cz bump` on feature branches.**
    > Versioning and releases are handled exclusively by maintainers on the `main` branch. Pushing tags from a feature branch can mess up the release history.

### Running Quality Checks

You should run these checks locally before submitting a PR.

```bash
# Lint code
ruff check .

# Lint and auto-fix
ruff check --fix .

# Format code
ruff format .

# Type check
pyrefly check

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## Code Style Guidelines

### General Principles

1. **Use `pathlib` for all file paths** — never use string concatenation for paths
   ```python
   # Good
   from pathlib import Path
   config_path = Path(__file__).parent / "config" / "settings.yaml"

   # Bad
   config_path = os.path.dirname(__file__) + "/config/settings.yaml"
   ```

2. **Use future annotations** — all modules should start with:
   ```python
   from __future__ import annotations
   ```

3. **Type hints** — add type hints to all public functions and methods.

4. **Docstrings** — use NumPy-style docstrings for all public APIs.

### Example Function

```python
from __future__ import annotations

from pathlib import Path


def load_data(file_path: Path, *, normalize: bool = True) -> dict[str, float]:
    """
    Load data from a file.

    Parameters
    ----------
    file_path
        Path to the data file.
    normalize
        Whether to normalize the values, by default True.

    Returns
    -------
    dict[str, float]
        Dictionary mapping names to values.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.

    Examples
    --------
    >>> data = load_data(Path("data.json"))
    >>> data["temperature"]
    298.15
    """
    ...
```

---

## Testing

All changes should have associated unit tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=uq_feature --cov-report=html

# Run specific test file
pytest tests/test_module.py

# Run tests matching a pattern
pytest -k "test_load"
```

### Writing Tests

- Place tests in the `tests/` directory.
- Mirror the source structure (e.g., `src/uq_feature/utils.py` → `tests/test_utils.py`).
- Use descriptive test names: `test_load_data_raises_on_missing_file`.

---

## Documentation

The documentation is built using [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

### Installing Dependencies

```bash
uv pip install -e ".[docs]"
```

### Building Locally

To build and serve the documentation locally (auto-reloads on changes):

```bash
mkdocs serve
```

Then open http://localhost:8000 in your browser.

### API Documentation

API documentation is auto-generated from docstrings using `mkdocstrings`. Write good docstrings and the API docs will update automatically.
