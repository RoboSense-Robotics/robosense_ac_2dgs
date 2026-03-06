## RS-AC2-2DGS

[中文介绍](README_CN.md)
### Overview

RS-AC2-2DGS is an open-source toolkit designed for high-fidelity 3D scene reconstruction using Robosense Active Camera 2 (AC2). It enables the complete workflow from rosbag data to Gaussian Splatting reconstruction. Built upon the state-of-the-art [2D Gaussian Splatting](https://github.com/hbb1/2d-gaussian-splatting.git) method, this repository offers a pipeline from data preparation and model training to interactive scene visualization.

### Prerequisites

This project has been developed and tested in the following environment:

| Component | Version | 
|:---|:---| 
| GPU | RTX3060 | 
| Nvidia Driver | 575|
| CUDA | 12.6 | 
| Python | 3.10 | 
| COLMAP | 3.7 | 




### Installation

Clone the repository:

```bash
git clone https://github.com/RoboSense-Robotics/robosense_ac_2dgs.git
```


#### Option 1: Docker (Recommended)

A pre-configured Dockerfile is provided under `docker/` for reproducible environment setup.

**Build the Docker image:**

```bash
cd robosense_ac2_2dgs
docker build -f docker/Dockerfile -t robosense_ac2_2dgs:latest .
```

**Create and start the container:**

```bash
docker run -it --gpus all \
    -v /path/to/your/data:/data \
    -m 900g --memory-swap -1 \
    --name ac2_2dgs \
    robosense_ac2_2dgs:latest bash
```

**Initialize the environment inside the container:**

```bash
cd robosense_ac2_2dgs

# Install COLMAP from the pre-built package
dpkg -i packages/colmap_3.7-2_amd64.deb

# Install submodules
cd submodules/diff-surfel-rasterization && pip install -e .
cd ../simple-knn && pip install -e .
cd ../..

# Set runtime paths
export PYTHONPATH=$PWD/submodules/simple-knn:$PWD/submodules/diff-surfel-rasterization:$PYTHONPATH
export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/torch/lib:$LD_LIBRARY_PATH
```

#### Option 2: Manual Installation

```bash
cd robosense_ac2_2dgs

# Install submodules
cd submodules/diff-surfel-rasterization && pip install -e .
cd ../simple-knn && pip install -e .
cd ../..

# Set runtime paths
export PYTHONPATH=$PWD/submodules/simple-knn:$PWD/submodules/diff-surfel-rasterization:$PYTHONPATH
export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/torch/lib:$LD_LIBRARY_PATH
```

For additional dependency installation, refer to：
- [2D Gaussian Splatting README](https://github.com/hbb1/2d-gaussian-splatting/blob/main/README.md)
- [COLMAP Installation](https://colmap.github.io/install.html)

### Usage

#### 1. Data Preprocessing

Extract image sequences from ROS bag files and generate COLMAP-compatible data:

```bash
# Extract images from rosbag
python tools/rosbag_data_parser_2dgs.py {bag_path} --output-dir {data_path} --calib-file {calib_file}

# Run COLMAP for sparse reconstruction
bash tools/colmap_data_parse.sh {data_path}
```

**Arguments:**
- `{bag_path}`: Input ROS bag file path
- `{data_path}`: Output directory for extracted data
- `{calib_file}`: Calibration file for AC2 camera

> **Note:** COLMAP sparse reconstruction typically takes approximately 1 hour, depending on the number of input images, the complexity of the target scene, and hardware configuration.

#### 2. Model Training

Train the 2D Gaussian Splatting model:

```bash
python train.py -s {data_path} -m {model_path}
```

**Arguments:**
- `{model_path}`: Path to the trained model output directory
- `{data_path}`: Path to the source data directory

> **Note:** Training time ranges from approximately 20 minutes to 1 hour, depending on hardware configuration and the complexity of the target scene.

#### 3. Mesh Export

The trained model supports mesh extraction via the following script:

```bash
# Default parameters （recommand）
bash tools/mesh_export.sh {model_path} {data_path}

# With optional parameters
bash tools/mesh_export.sh {model_path} {data_path} --unbounded --mesh_res 1024 
```

**Arguments:**

- `--unbounded`: Enable unbounded scene reconstruction mode (optional)
- `--mesh_res <resolution>`: Mesh resolution (optional)
- `--voxel_size <size>`: Voxel size for volumetric downsampling during mesh generation (optional)

#### 4. Visualization

##### Interactive Viewer

For interactive visualization setup, refer to the [SIBR Viewers documentation](https://github.com/graphdeco-inria/gaussian-splatting#interactive-viewers).


##### Additional Visualization Tools

| Tool | Type | Description |
|:---|:---|:---|
| [SuperSplat Editor](https://playcanvas.com/supersplat/editor/) | Web-based | Browser-based Gaussian splat editor |
| [YouTube Tutorial](https://www.youtube.com/watch?v=xxQr61ifoqM) | Video | Video recording and editing guide |

### License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

### Acknowledgments

This work builds upon the following open-source projects:
- [3D Gaussian Splatting](https://github.com/graphdeco-inria/gaussian-splatting)
- [2D Gaussian Splatting](https://github.com/hbb1/2d-gaussian-splatting)
- [COLMAP](https://colmap.github.io/)

### Contact

For bug reports and feature requests, please open an issue on [GitHub Issues](https://github.com/RoboSense-Robotics/robosense_ac_2dgs/issues).
