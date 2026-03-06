#!/bin/bash

# mesh_export.sh
# Usage: ./mesh_export.sh <model_path> <data_path> [--unbounded] [--mesh_res <resolution>] [--voxel_size <size>]
# Example: ./mesh_export.sh /path/to/output/model /path/to/data --unbounded --mesh_res 1024 --voxel_size 0.01

set -e  # Exit on error

# Default values
UNBOUNDED=""
MESH_RES=1024
VOXEL_SIZE=""

# Function to display usage
usage() {
    echo "Usage: $0 <model_path> <data_path> [OPTIONS]"
    echo ""
    echo "Required arguments:"
    echo "  <model_path>      Path to the trained Gaussian Splatting model output directory"
    echo "  <data_path>       Path to the source data directory"
    echo ""
    echo "Optional arguments:"
    echo "  --unbounded           Enable unbounded scene mode"
    echo "  --mesh_res <res>      Mesh resolution (default: 1024)"
    echo "  --voxel_size <size>   Voxel size for mesh generation"
    echo ""
    echo "Example:"
    echo "  $0 /path/to/output/model /path/to/data --unbounded --mesh_res 1024 --voxel_size 0.01"
    exit 1
}

# Check if at least 2 arguments are provided
if [ "$#" -lt 2 ]; then
    echo "Error: Missing required arguments."
    usage
fi

# Parse required arguments
MODEL_PATH=$(realpath "$1")
DATA_PATH=$(realpath "$2")
shift 2

# Parse optional arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --unbounded)
            UNBOUNDED="--unbounded"
            shift
            ;;
        --mesh_res)
            if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
                MESH_RES=$2
                shift 2
            else
                echo "Error: --mesh_res requires a numeric argument."
                usage
            fi
            ;;
        --voxel_size)
            if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
                VOXEL_SIZE="--voxel_size $2"
                shift 2
            else
                echo "Error: --voxel_size requires a numeric argument."
                usage
            fi
            ;;
        *)
            echo "Error: Unknown option: $1"
            usage
            ;;
    esac
done

# Validate paths
if [ ! -d "$MODEL_PATH" ]; then
    echo "Error: Model path '$MODEL_PATH' does not exist."
    exit 1
fi

if [ ! -d "$DATA_PATH" ]; then
    echo "Error: Data path '$DATA_PATH' does not exist."
    exit 1
fi

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Display configuration
echo "========================================"
echo "Mesh Export Configuration"
echo "========================================"
echo "Model path:      $MODEL_PATH"
echo "Data path:       $DATA_PATH"
echo "Unbounded:       ${UNBOUNDED:-No}"
echo "Mesh resolution: $MESH_RES"
echo "Voxel size:      ${VOXEL_SIZE#--voxel_size }"
[ -z "$VOXEL_SIZE" ] && echo "Voxel size:      (default)"
echo "========================================"
echo ""

# Run render.py
echo "Starting mesh export..."
cd "$PROJECT_ROOT"

python3 render.py \
    -m "$MODEL_PATH" \
    -s "$DATA_PATH" \
    $UNBOUNDED \
    --mesh_res "$MESH_RES" \
    $VOXEL_SIZE

echo ""
echo "✅ Mesh export completed successfully!"
echo "Output saved to: $MODEL_PATH"
