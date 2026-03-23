"""
CLI entry point for the UQ Feature pipeline.

This module provides command-line interface commands for running the UQ
feature pipeline with Hydra configuration management.
"""

from __future__ import annotations

import sys
from pathlib import Path

import hydra
import loguru
import typer

from uq_feature.pipeline.runner import run_pipeline

logger = loguru.logger

# -----------------------------------------------------------------------------
# CLI setup
# -----------------------------------------------------------------------------
app = typer.Typer(help="UQ Feature CLI")
run_app = typer.Typer(help="Run pipeline components")

app.add_typer(run_app, name="run")


# -----------------------------------------------------------------------------
# Hydra entry
# -----------------------------------------------------------------------------
def hydra_entry():
    """
    Create and return a Hydra-decorated main function.

    Returns
    -------
    callable
        A Hydra-decorated function that serves as the entry point for
        the pipeline execution with configuration management.
    """

    @hydra.main(
        config_path=None,
        config_name=None,
        version_base=None,
    )
    def _main(cfg):
        logger.info(f"[Hydra] Original cwd: {hydra.utils.get_original_cwd()}")

        cfg.WORK_DIR = str(Path.cwd())

        logger.info(f"[Hydra] WORK_DIR set to: {cfg.WORK_DIR}")

        run_pipeline(cfg)

    return _main


# -----------------------------------------------------------------------------
# CLI command
# -----------------------------------------------------------------------------
@run_app.command(
    "pipeline",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run_pipeline_command(
    ctx: typer.Context,
    config: Path = typer.Option(..., "--config", "-c"),
    steps: str | None = typer.Option(None, "--steps"),
):
    """
    Run the UQ feature pipeline with Hydra configuration.

    Parameters
    ----------
    ctx : typer.Context
        Typer context containing command-line arguments.
    config : Path
        Path to the Hydra configuration file.
    steps : str | None
        Optional comma-separated list of pipeline steps to run.
    """
    from hydra.core.global_hydra import GlobalHydra

    # Reset Hydra (important for repeated runs / multirun)
    if GlobalHydra.instance().is_initialized():
        GlobalHydra.instance().clear()

    # Capture all Hydra args (including -m and overrides)
    hydra_args = list(ctx.args)

    # Optional: override pipeline steps
    if steps:
        hydra_args.append(f"pipeline.steps=[{steps}]")

    # Pass arguments to Hydra
    sys.argv = [
        sys.argv[0],
        f"--config-path={config.parent}",
        f"--config-name={config.stem}",
        *hydra_args,
    ]
    # Run Hydra
    entry = hydra_entry()
    entry()


def main():
    """Execute the main entry point."""
    app()


if __name__ == "__main__":
    main()
