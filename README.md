# py-scaffold

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/package_name.svg)](https://pypi.org/project/package_name/)
[![codecov](https://codecov.io/gh/skethirajan/py-scaffold/graph/badge.svg?token=dl0U9dYIj6)](https://codecov.io/gh/skethirajan/py-scaffold)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pyrefly](https://img.shields.io/badge/pyrefly-checked-blueviolet)](https://github.com/NoneGG/pyrefly)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![MkDocs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://www.mkdocs.org/)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-green.svg)](LICENSE)

A minimal scaffold for building modern, reproducible scientific Python packages.

## Create your own python package with this template

Use this template to create your own repo, ```new_project```. Then clone your ```new_project``` repo and follow along the instructions given in the [Developer Guide on Environment Setup](docs/CONTRIBUTING.md#environment-setup) to set up your environment.

Now, run the initialization script (will interactively prompt you for some details) to automatically rename all the placeholders from the template.

```bash
# Run the init script (ensure you're at the project root level)
uv run python scripts/init_project.py
```

Before you push your changes (initialized with your project details), remember to configure GitHub Pages to host your docs. Also, you need to setup ```ADMIN_TOKEN``` (used in [settings.yml](.github/workflows/settings.yml)) and ```CODECOV_TOKEN``` (used in [ci.yml](.github/workflows/ci.yml)). Now, manually run the Repository Settings workflow (you need to do it just once) from the Actions tab of your repo.

Now, you can push your changes to GitHub and the CI/CD pipeline will take care of the rest.

```bash
git add .
git commit -m "chore(main): initialize project"
git push origin main
```

## 📦 Features

- Quick project initialization with modern tools & best practices
- Easy to extend this template to your needs

## 🚀 Getting Started

| Resource        | Link                                                                                   |
|-----------------|----------------------------------------------------------------------------------------|
| 👉 Installation Guide | [Installation Guide](docs/getting-started/installation.md) |
| 🧑‍💻 Developer Guide | [Developer Guide](docs/CONTRIBUTING.md) |

---
