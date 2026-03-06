ARG UBUNTU_VERSION=22.04
ARG NVIDIA_CUDA_VERSION=12.6.1

#
# Docker builder stage.
#
FROM nvcr.io/nvidia/cuda:${NVIDIA_CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION} as builder

# Use Tsinghua mirror for NVIDIA apt repository to avoid network issues
RUN sed -i 's|https://developer.download.nvidia.com|https://mirrors.tuna.tsinghua.edu.cn/nvidia|g' /etc/apt/sources.list.d/*.list || true

# Disable NVIDIA repo if network issues persist (CUDA already in base image)
RUN mv /etc/apt/sources.list.d/cuda*.list /tmp/ || true

ARG COLMAP_GIT_COMMIT=main
ARG CUDA_ARCHITECTURES=native
ENV QT_XCB_GL_INTEGRATION=xcb_egl

# Prevent stop building ubuntu at time zone selection.
ENV DEBIAN_FRONTEND=noninteractive


RUN rm /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/ubuntu/ jammy main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/ubuntu/ jammy-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.ustc.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse" >> /etc/apt/sources.list && \
    apt-get update

# Prepare and empty machine for building.
RUN apt-get update && \
    apt-get install -y --no-install-recommends --no-install-suggests \
        git \
        cmake \
        ninja-build \
        build-essential \
        libboost-all-dev \
        libeigen3-dev \
        libflann-dev \
        libfreeimage-dev \
        libmetis-dev \
        libgoogle-glog-dev \
        libgtest-dev \
        libgmock-dev \
        libsqlite3-dev \
        libglew-dev \
        qtbase5-dev \
        libqt5opengl5-dev \
        libcgal-dev \
        libceres-dev \
        libilmbase-dev \
        libopenexr-dev \
        libpng-dev \
        libjpeg-dev \
        libtiff-dev \
        libwebp-dev \
        libraw-dev \
        libopenjp2-7-dev

# Build and install Imath from source (Ubuntu 20.04 package too old).


# Install Python 3.10 and pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends --no-install-suggests \
        python3 \
        python3-dev \
        python3-pip && \
    pip install --upgrade pip setuptools wheel


# Set CUDA environment variables
ENV PATH=/usr/local/cuda/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

RUN pip install  \
        ffmpeg-python  \
        Pillow==10.2.0  \
        typing_extensions>=4.10.0  

RUN pip  install  \
        open3d==0.19.0  \
        mediapy==1.1.2  \
        lpips==0.1.4  \
        scikit-image==0.21.0  \
        tqdm==4.66.2  \
        trimesh==4.3.2 \
        plyfile \
        opencv-python \
        gnupg

RUN pip install torch==2.6.0+cu126 torchvision==0.21.0+cu126 \
    --index-url https://download.pytorch.org/whl/cu126 && \
    pip install  torchaudio==2.6.0  rosbags