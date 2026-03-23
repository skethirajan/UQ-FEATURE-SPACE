#!/usr/bin/env julia

import Pkg

# ---------------------------------------
# Parse CLI arguments
# ---------------------------------------
function parse_args()
    if length(ARGS) < 6
        println("""
Usage:
julia compute_ace.jl <julia_project> <xyz_file> <out_dir> <order> <totaldegree> <rcut>

Example:
julia compute_ace.jl /path/to/env dataset.xyz out_dir 3 6 6.0
""")
        exit(1)
    end

    return (
        julia_project = ARGS[1],
        xyz_file      = ARGS[2],
        out_dir       = ARGS[3],
        order         = parse(Int, ARGS[4]),
        totaldegree   = parse(Int, ARGS[5]),
        rcut          = parse(Float64, ARGS[6]),
    )
end

args = parse_args()

# ---------------------------------------
# Activate Julia environment
# ---------------------------------------
println("[Julia] Activating project: ", args.julia_project)
Pkg.activate(args.julia_project)

using ACEpotentials
using ExtXYZ
using NPZ
using Base.Threads

println("[Julia] Threads: ", Threads.nthreads())
println("[Julia] Dataset: ", args.xyz_file)
println("[Julia] Output: ", args.out_dir)

# ---------------------------------------
# Load dataset
# ---------------------------------------
frames = ExtXYZ.load(args.xyz_file)

if length(frames) == 0
    error("No frames found in dataset")
end

println("[Julia] Total frames: ", length(frames))

# ---------------------------------------
# Detect species
# ---------------------------------------
species = unique(vcat([
    frame.atom_data.atomic_symbol for frame in frames
]...))

println("[Julia] Detected species: ", species)

# ---------------------------------------
# Build ACE model
# ---------------------------------------
model = ACEpotentials.ace1_model(
    species = species,
    order = args.order,
    totaldegree = args.totaldegree,
    rcut = args.rcut
)

println("[Julia] Basis size: ", length_basis(model))

# ---------------------------------------
# Descriptor computation helper
# ---------------------------------------
function descriptors_matrix(frame, model)
    feats = ACEpotentials.site_descriptors(frame, model)
    return reduce(hcat, feats)'   # (N_atoms, n_features)
end

# ---------------------------------------
# Save features (streaming)
# ---------------------------------------
function save_features(frames, model, out_dir)
    mkpath(out_dir)

    Threads.@threads for i in eachindex(frames)
        file = joinpath(out_dir, "frame_$(lpad(i-1, 6, '0')).npz")

        X = descriptors_matrix(frames[i], model)

        npzwrite(file, Dict(
            "features" => X,
            # "n_atoms"  => size(X, 1),
            # "n_feat"   => size(X, 2)
        ))

        if i % 50 == 0
            println("[Julia] Processed frame $i")
        end
    end
end

# ---------------------------------------
# Run
# ---------------------------------------
println("[Julia] Starting ACE descriptor computation...")

save_features(frames, model, args.out_dir)

println("[Julia] Done.")
