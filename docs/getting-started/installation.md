# Installation

## Requirements

- Python 3.12 or higher

## Install from PyPI

```bash
pip install package_name
```

## Install from Source

```bash
git clone https://github.com/username/package_name.git
cd package_name
pip install -e .
```

## Install with Development Dependencies

```bash
pip install -e ".[dev]"
```

This will install all development dependencies including:

- Testing: `pytest`, `pytest-cov`
- Linting: `ruff`, `docformatter`, `pre-commit`
- Type checking: `pyrefly`
- Documentation: `mkdocs-material`, `mkdocstrings`
