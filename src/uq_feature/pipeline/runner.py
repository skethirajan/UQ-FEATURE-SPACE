"""
Pipeline runner for executing UQ feature extraction steps.

This module provides functionality to run the UQ feature pipeline with a
specified configuration object.
"""

from __future__ import annotations

import importlib

STEP_REGISTRY: dict[str, str] = {
    "ace": "uq_feature.descriptors.ace.core:main",
    # future:
    # "cluster": "uq_feature.clustering.kmeans:run_kmeans",
    # "uq": "uq_feature.uq.compute:run_uq",
}


def run_pipeline(cfg):
    """
    Execute the UQ feature extraction pipeline.

    Parameters
    ----------
    cfg : object
        Configuration object containing pipeline steps and settings.

    Raises
    ------
    ValueError
        If no pipeline steps are specified or step is invalid.
    """
    steps = cfg.pipeline.steps

    if isinstance(steps, str):
        steps = [steps]

    for step in steps:
        if step not in STEP_REGISTRY:
            raise ValueError(f"Unknown pipeline step: {step}")

        entrypoint = STEP_REGISTRY[step]
        module_path, func_name = entrypoint.split(":")

        try:
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
        except (ModuleNotFoundError, AttributeError) as exc:
            raise ValueError(
                f"Failed to load pipeline step '{step}' from entrypoint '{entrypoint}': {exc}"
            ) from exc

        func(cfg)
