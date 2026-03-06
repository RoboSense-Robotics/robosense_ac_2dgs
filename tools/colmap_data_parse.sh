#!/bin/bash

# colmap_to_3dgs.sh
# Usage: ./colmap_to_3dgs.sh /path/to/your/project_root
# Requirement: project_root must contain a subfolder named "images"
export QT_QPA_PLATFORM=offscreen
set -e  # Exit on error

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <project_root_directory>"
    echo "  The <project_root_directory> must contain an 'images' subfolder with JPG/PNG files."
    exit 1
fi

PROJECT_ROOT=$(realpath "$1")

if [ ! -d "$PROJECT_ROOT/images" ]; then
    echo "Error: Directory '$PROJECT_ROOT' does not contain an 'images' subfolder."
    exit 1
fi

echo "Processing project root: $PROJECT_ROOT"

# Define paths
IMAGE_DIR="$PROJECT_ROOT/images"
DB_PATH="$PROJECT_ROOT/database.db"
SPARSE_DIR="$PROJECT_ROOT/sparse"

# Clean previous runs (optional)
rm -f "$DB_PATH"
rm -rf "$SPARSE_DIR"

# Step 1: Feature extraction
echo "Step 1: Feature extraction..."
colmap feature_extractor \
    --database_path "$DB_PATH" \
    --image_path "$IMAGE_DIR" \
    --ImageReader.camera_model PINHOLE \
    --ImageReader.single_camera 1 \
    --SiftExtraction.use_gpu 0

# Step 2: Feature matching
echo "Step 2: Feature matching..."
colmap exhaustive_matcher \
    --database_path "$DB_PATH" \
    --SiftMatching.use_gpu 0


# Step 3: Sparse reconstruction
echo "Step 3: Sparse reconstruction..."
mkdir -p "$SPARSE_DIR"
colmap mapper \
    --database_path "$DB_PATH" \
    --image_path "$IMAGE_DIR" \
    --output_path "$SPARSE_DIR" \
    # --Mapper.ba_use_gpu 1 \
    # --Mapper.ba_local_num_images 16 \
    # --Mapper.ba_global_frames_freq 100 \
    --Mapper.filter_max_reproj_error 4

# Optional: Convert to TXT for inspection (comment out if not needed)
# echo "Converting model to TXT..."
# colmap model_converter \
#     --input_path "$SPARSE_DIR/0" \
#     --output_path "$SPARSE_DIR/0" \
#     --output_type TXT

echo "✅ Done! 3DGS-ready sparse reconstruction saved to: $SPARSE_DIR/0"
echo "You can now use this folder with 3D Gaussian Splatting training."