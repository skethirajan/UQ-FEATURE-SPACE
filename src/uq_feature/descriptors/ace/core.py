"""
Core module for ACE (Atomic Cluster Expansion) descriptor computation.

This module provides the main entry point for launching Julia-based ACE
descriptor calculations with configurable parameters.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import loguru
from omegaconf import DictConfig, OmegaConf

logger = loguru.logger


def main(cfg: DictConfig) -> None:
    """
    Launch Julia-based ACE descriptor computation.

    Parameters
    ----------
    cfg : DictConfig
        Configuration object containing ACE settings and paths, including
        body_order, rcut, totaldegree, dataset path, julia executable path,
        and julia project path.

    Raises
    ------
    ValueError
        If the dataset path is not provided in the configuration.
    subprocess.CalledProcessError
        If the Julia subprocess exits with a non-zero status code.
    """
    # Config
    pkg_default_config_file = Path(__file__).parents[2] / "config/ace.yaml"
    ace_default_cfg = OmegaConf.load(pkg_default_config_file)

    ace_user_cfg = OmegaConf.select(cfg, "ace") or {}
    ace_cfg = OmegaConf.merge(ace_default_cfg, ace_user_cfg)
    ace_cfg = OmegaConf.create(ace_cfg)

    body_order = int(OmegaConf.select(ace_cfg, "body_order"))
    rcut = float(OmegaConf.select(ace_cfg, "rcut"))
    totaldegree = int(OmegaConf.select(ace_cfg, "totaldegree"))

    dataset = OmegaConf.select(ace_cfg, "paths.dataset")
    julia_exe = OmegaConf.select(ace_cfg, "paths.julia_exe")
    julia_project = OmegaConf.select(ace_cfg, "paths.julia_project")

    julia_script = Path(__file__).parent / "ace.jl"

    if dataset is None:
        raise ValueError("Missing dataset path")

    dataset_path = Path(dataset)

    # Hydra-provided WORK_DIR
    work_dir = OmegaConf.select(cfg, "WORK_DIR")
    if work_dir is None:
        raise ValueError("WORK_DIR not set in config")

    save_dir = (
        work_dir / f"ACE/{dataset_path.stem}/B-{body_order}_D-{totaldegree}_Rcut-{rcut}"
    )
    save_dir.mkdir(parents=True, exist_ok=True)

    # Call Julia script
    logger.info("[Python] Launching Julia ACE computation...")

    cmd = [
        str(julia_exe),
        str(julia_script),
        str(julia_project),
        str(dataset_path),
        str(save_dir),
        str(body_order),
        str(totaldegree),
        str(rcut),
    ]

    logger.debug("Command:")
    logger.debug(" ".join(cmd))

    subprocess.run(cmd, check=True)

    logger.info("ACE descriptor computation complete.")
