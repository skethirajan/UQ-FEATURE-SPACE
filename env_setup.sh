#!/usr/bin/env bash

# ./env_setup.sh > setup.log 

set -euo pipefail

CONDA_ENV_NAME="uq_feature"
IPYTHON_KERNEL_DISPLAY_NAME="uq_feature"
PYTHON_VERSION="3.12"

WORKSPACE_ROOT="/usr/workspace/$USER"  # HPC-specific setting
SOFTWARE_ROOT="$WORKSPACE_ROOT/softwares"
CONDA_INSTALL_ROOT="$SOFTWARE_ROOT/miniconda"
JULIA_INSTALL_ROOT="$SOFTWARE_ROOT/juliaup"

# UV Cache in scratch
export UV_CACHE_DIR="/p/lustre5/${USER}/uv-cache/${CONDA_ENV_NAME}"  # HPC-specific setting (add to ~/.bashrc)  
mkdir -p "$UV_CACHE_DIR"

DEBUG_QUEUE="pdebug"
DEBUG_TIME="30"   # minutes
ROCM_MODULE_VERSION="rocm/6.3.0"

cleanup() {
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        echo
        echo "Project environment configured successfully!"
        echo "Exiting allocation shell and releasing compute allocation."
    else
        echo
        echo "Environment setup failed with exit code: $exit_code"
        echo "Exiting allocation shell and releasing compute allocation."
    fi
    exit "$exit_code"
}

trap cleanup EXIT

# ------------------------------------------------------------------
# Re-run inside a debug allocation if not already there
# ------------------------------------------------------------------
if [[ "${1:-}" != "--inside-allocation" ]]; then
    echo "Requesting a $DEBUG_QUEUE node for $DEBUG_TIME minutes..."
    exec salloc -p "$DEBUG_QUEUE" -N 1 -n 1 -t "$DEBUG_TIME" bash "$0" --inside-allocation
fi

echo "Running inside allocated compute node: $(hostname)"

# ------------------------------------------------------------------
# Detect GPU vendor
# ------------------------------------------------------------------
GPU_INFO="$(lspci | grep -i -E 'processing accelerators|vga|display|3d|nvidia|amd/ati|amd' || true)"

HAS_NVIDIA_GPU=0
HAS_AMD_GPU=0

if echo "$GPU_INFO" | grep -qi "NVIDIA"; then
    HAS_NVIDIA_GPU=1
fi

if echo "$GPU_INFO" | grep -qiE "AMD/ATI|AMD Instinct|Advanced Micro Devices"; then
    HAS_AMD_GPU=1
fi

echo "Detected GPU info:"
echo "$GPU_INFO"

# ------------------------------------------------------------------
# Load ROCm only if:
#   1) GPU is AMD (and not NVIDIA)
#   2) rocminfo does not already work
# ------------------------------------------------------------------
if [[ "$HAS_NVIDIA_GPU" -eq 0 && "$HAS_AMD_GPU" -eq 1 ]]; then
    if ! command -v rocminfo >/dev/null 2>&1 || ! rocminfo >/dev/null 2>&1; then
        echo "AMD GPU detected and rocminfo is not available; loading $ROCM_MODULE_VERSION ..."
        module load "$ROCM_MODULE_VERSION"
    else
        echo "AMD GPU detected and rocminfo already works; not loading ROCm module."
    fi
else
    echo "No AMD-only GPU condition met; skipping ROCm module load."
fi

# ------------------------------------------------------------------
# Report backend state
# ------------------------------------------------------------------
if command -v rocminfo >/dev/null 2>&1; then
    echo "rocminfo found at: $(which rocminfo)"
    rocminfo >/dev/null 2>&1 && echo "rocminfo works" || echo "rocminfo exists but does not run cleanly"
else
    echo "rocminfo not found"
fi

if command -v hipconfig >/dev/null 2>&1; then
    echo "hipconfig found at: $(which hipconfig)"
    hipconfig --version || true
fi

# ------------------------------------------------------------------
# Initialize conda for this shell
# ------------------------------------------------------------------
eval "$($CONDA_INSTALL_ROOT/bin/conda shell.bash hook)"

# ------------------------------------------------------------------
# Clean installation
# ------------------------------------------------------------------
conda deactivate || true
conda env remove -n "$CONDA_ENV_NAME" -y || true
rm -rf "$HOME/.local/share/jupyter/kernels/$CONDA_ENV_NAME"

# Optional: remove Julia installation entirely if necessary
rm -rf "$JULIA_INSTALL_ROOT" "$HOME/.julia" "$WORKSPACE_ROOT/.home.julia"

# ------------------------------------------------------------------
# Install Julia outside conda if not already installed at target path
# ------------------------------------------------------------------
bash -c "
set -euo pipefail
if [ ! -x '$JULIA_INSTALL_ROOT/bin/julia' ]; then
    curl -fsSL https://install.julialang.org | sh -s -- -y --path '$JULIA_INSTALL_ROOT'
    if [ -d \"\$HOME/.julia\" ] && [ ! -L \"\$HOME/.julia\" ]; then
        mv \"\$HOME/.julia\" '$WORKSPACE_ROOT/.home.julia'
        ln -s '$WORKSPACE_ROOT/.home.julia' \"\$HOME/.julia\"
    fi
fi
"

export PATH="$JULIA_INSTALL_ROOT/bin:$PATH"

# ------------------------------------------------------------------
# Create conda environment
# ------------------------------------------------------------------
conda create -n "$CONDA_ENV_NAME" python="$PYTHON_VERSION" -c conda-forge -y
conda activate "$CONDA_ENV_NAME"

# ------------------------------------------------------------------
# Install uv
# ------------------------------------------------------------------
UV_INSTALL_ROOT="$CONDA_PREFIX"
UV_BIN_DIR="$UV_INSTALL_ROOT/bin"

if [ ! -x "$UV_BIN_DIR/uv" ]; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | \
        env UV_INSTALL_DIR="$UV_BIN_DIR" sh
fi

echo "uv path: $(which uv || echo 'NOT FOUND')"

# ------------------------------------------------------------------
# Install PyTorch (UV version — controlled)
# ------------------------------------------------------------------
uv pip uninstall -y torch torchvision torchaudio || true

if [[ "$HAS_NVIDIA_GPU" -eq 1 ]]; then
    echo "Installing NVIDIA CUDA PyTorch via uv..."
    uv pip install torch torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/cu128 
elif command -v rocminfo >/dev/null 2>&1 && rocminfo >/dev/null 2>&1; then
    echo "Installing AMD ROCm PyTorch via uv..."
    uv pip install torch torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/rocm6.3 
else
    echo "Installing CPU PyTorch via uv..."
    uv pip install torch torchvision torchaudio
fi

python - <<'PY'
import torch
print("torch version:", torch.__version__)
print("torch.version.cuda:", torch.version.cuda)
print("torch.version.hip:", getattr(torch.version, "hip", None))
print("torch.cuda.is_available():", torch.cuda.is_available())
if torch.cuda.is_available():
    try:
        print("device count:", torch.cuda.device_count())
        print("device 0:", torch.cuda.get_device_name(0))
    except Exception as e:
        print("GPU detected, but could not query device name:", e)
PY

# ------------------------------------------------------------------
# Install minimal Python deps (ONLY infrastructure ones)
# ------------------------------------------------------------------
uv pip install juliacall ipykernel

# ------------------------------------------------------------------
# Configure JuliaCall / PythonCall environment
# ------------------------------------------------------------------
JULIACALL_PROJECT_ENV_PATH="$CONDA_PREFIX/julia_envs/$CONDA_ENV_NAME"

mkdir -p "$JULIACALL_PROJECT_ENV_PATH"

export JULIACALL_PROJECT_ENV_PATH
export PYTHON_JULIACALL_PROJECT="$JULIACALL_PROJECT_ENV_PATH"
export JULIA_CONDAPKG_BACKEND=Null
export PYTHON_JULIACALL_EXE="$JULIA_INSTALL_ROOT/bin/julia"
export JULIA_PYTHONCALL_EXE="$CONDA_PREFIX/bin/python"

# ------------------------------------------------------------------
# Install Julia packages into the JuliaCall project
# ------------------------------------------------------------------
julia -e 'import Pkg; Pkg.activate(ENV["JULIACALL_PROJECT_ENV_PATH"]); Pkg.add(["PythonCall", "ACEpotentials", "AtomsBase", "Unitful"])'

# ------------------------------------------------------------------
# Check ACE installation
# ------------------------------------------------------------------
python -c "from juliacall import Main as jl; jl.seval('using PythonCall, ACEpotentials; println(\"ACE loaded\")')"

# ------------------------------------------------------------------
# Install Jupyter kernel
# ------------------------------------------------------------------
python -m ipykernel install --user --name "$CONDA_ENV_NAME" --display-name "$IPYTHON_KERNEL_DISPLAY_NAME"

echo "uv version: $(uv --version)"
