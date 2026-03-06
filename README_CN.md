## RS-AC2-2DGS

[Introduction in English](README.md)

### 概述

RS-AC2-2DGS 是一个开源工具包，专为使用 Robosense Active Camera 2 (AC2) 进行高保真三维场景重建而设计。该工具包实现了从 rosbag 数据到 Gaussian Splatting 重建的完整流程。本仓库基于先进的 [2D Gaussian Splatting](https://github.com/hbb1/2d-gaussian-splatting.git) 方法构建，并提供从数据准备、模型训练到交互式场景可视化的流程。

### 前置依赖

本项目在以下环境中开发和测试：

| 组件 | 版本 |
|:---|:---|
| GPU | RTX3060 |
| Nvidia Driver | 575 |
| CUDA | 12.6 |
| Python | 3.10 |
| COLMAP | 3.7 |



### 安装

拉取本仓库代码：

```bash
git clone https://github.com/RoboSense-Robotics/robosense_ac2_2dgs.git
```


#### 方案一：Docker（推荐）

`docker/` 目录下提供了预配置的 Dockerfile，用于可复现的环境部署。

**构建 Docker 镜像：**

```bash
cd robosense_ac2_2dgs
docker build -f docker/Dockerfile -t robosense_ac2_2dgs:latest .
```

**创建并启动容器：**

```bash
docker run -it --gpus all \
    -v /path/to/your/data:/data \
    -m 900g --memory-swap -1 \
    --name ac2_2dgs \
    robosense_ac2_2dgs:latest bash
```

**容器内环境初始化：**

```bash
cd robosense_ac2_2dgs

# 安装预构建的 COLMAP 包
dpkg -i packages/colmap_3.7-2_amd64.deb

# 编译并安装 CUDA 扩展子模块
cd submodules/diff-surfel-rasterization && pip install -e .
cd ../simple-knn && pip install -e .
cd ../..

# 配置运行时库路径
export PYTHONPATH=$PWD/submodules/simple-knn:$PWD/submodules/diff-surfel-rasterization:$PYTHONPATH
export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/torch/lib:$LD_LIBRARY_PATH
```

#### 方案二：手动安装

```bash
cd robosense_ac2_2dgs

# 编译并安装 CUDA 扩展子模块
cd submodules/diff-surfel-rasterization && pip install -e .
cd ../simple-knn && pip install -e .
cd ../..

# 配置运行时库路径
export PYTHONPATH=$PWD/submodules/simple-knn:$PWD/submodules/diff-surfel-rasterization:$PYTHONPATH
export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/torch/lib:$LD_LIBRARY_PATH
```

其他依赖项安装请参考：
- [2D Gaussian Splatting README](https://github.com/hbb1/2d-gaussian-splatting/blob/main/README.md)
- [COLMAP 安装](https://colmap.github.io/install.html)

### 使用方法

#### 1. 数据预处理

从 ROS bag 文件中提取图像序列并生成 COLMAP 兼容数据：

```bash
# 从 rosbag 提取图像
python tools/rosbag_data_parser_2dgs.py {bag_path} --output-dir {data_path} --calib-file {calib_file}

# 运行 COLMAP 进行稀疏重建
bash tools/colmap_data_parse.sh {data_path}
```

**参数：**
- `{bag_path}`: 输入 ROS bag 文件路径
- `{data_path}`: 提取数据的输出目录
- `{calib_file}`: AC2 相机的标定文件

> **说明：** COLMAP 稀疏重建耗时约 1 小时，取决于输入图像数量、待重建目标场景的复杂程度及硬件配置。

#### 2. 模型训练

训练 2D Gaussian Splatting 模型：

```bash
python train.py -s {data_path} -m {model_path}
```

**参数：**
- `{data_path}`: 包含 COLMAP 输出的源数据目录
- `{model_path}`: 训练模型检查点的输出目录

> **说明：** 训练时长约为 20 分钟至 1 小时，取决于训练终端及待重建目标场景的复杂程度。

#### 3. Mesh 导出

已训练模型支持通过以下脚本进行 mesh 提取：

```bash
# 默认参数 (推荐)
bash tools/mesh_export.sh {model_path} {data_path}

# 带可选参数
bash tools/mesh_export.sh {model_path} {data_path} --unbounded --mesh_res 1024 
```

**参数：**
- `--unbounded`: 启用无界场景重建模式（可选）
- `--mesh_res <resolution>`: Mesh 分辨率（可选）
- `--voxel_size <size>`: mesh 生成时体素下采样大小（可选）

#### 4. 可视化

##### 交互式查看器

交互式可视化设置请参考 [SIBR Viewers 文档](https://github.com/graphdeco-inria/gaussian-splatting#interactive-viewers)。

##### 其他可视化工具

| 工具 | 类型 | 描述 |
|:---|:---|:---|
| [SuperSplat Editor](https://playcanvas.com/supersplat/editor/) | Web 端 | 基于浏览器的 Gaussian splat 编辑器 |
| [YouTube 教程](https://www.youtube.com/watch?v=xxQr61ifoqM) | 视频 | 视频录制和编辑指南 |

### 许可证

本项目基于 MIT 许可证发布，详情见 [LICENSE](LICENSE) 文件。

### 鸣谢

本项目基于以下开源项目：
- [3D Gaussian Splatting](https://github.com/graphdeco-inria/gaussian-splatting)
- [2D Gaussian Splatting](https://github.com/hbb1/2d-gaussian-splatting)
- [COLMAP](https://colmap.github.io/)

### 联系方式

如有问题报告或功能请求，请在 [GitHub Issues](https://github.com/RoboSense-Robotics/robosense_ac2_2dgs/issues) 页面提交。
