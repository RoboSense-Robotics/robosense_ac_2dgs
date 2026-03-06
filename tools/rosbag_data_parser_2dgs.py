#!/usr/bin/env python3
"""
ROS Bag Parser for Stereo Images (rosbags version)
从rosbag中读取左相机图像并解包到指定文件夹内
无需安装 ROS，仅依赖 rosbags 纯Python库

Dependencies:
    pip install rosbags opencv-python numpy pyyaml
"""

import cv2
import os
import argparse
from pathlib import Path
import yaml
import numpy as np
from rosbags.rosbag1 import Reader
from rosbags.typesys import get_typestore, Stores


def imgmsg_to_cv2(msg):
    """
    将 rosbags 图像消息转换为 OpenCV BGR 图像

    Args:
        msg: rosbags 反序列化的图像消息

    Returns:
        numpy.ndarray: BGR 格式图像
    """
    encoding = msg.encoding
    height = msg.height
    width = msg.width
    raw_data = np.frombuffer(msg.data, dtype=np.uint8)

    if encoding == 'rgb8':
        img = raw_data.reshape((height, width, 3))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif encoding == 'bgr8':
        img = raw_data.reshape((height, width, 3))
    elif encoding == 'mono8':
        img = raw_data.reshape((height, width))
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif encoding in ('bayer_rggb8', 'bayer_bggr8', 'bayer_gbrg8', 'bayer_grbg8'):
        img = raw_data.reshape((height, width))
        bayer_map = {
            'bayer_rggb8': cv2.COLOR_BayerRG2BGR,
            'bayer_bggr8': cv2.COLOR_BayerBG2BGR,
            'bayer_gbrg8': cv2.COLOR_BayerGB2BGR,
            'bayer_grbg8': cv2.COLOR_BayerGR2BGR,
        }
        img = cv2.cvtColor(img, bayer_map[encoding])
    else:
        raise ValueError(f"不支持的图像编码格式: {encoding}")

    return img


class StereoBagMonoParser:
    def __init__(self, bag_path, left_topic, output_dir, calib_file=None):
        """
        初始化双目图像解析器

        Args:
            bag_path: rosbag文件路径
            left_topic: 左相机topic名称
            output_dir: 输出目录路径
            calib_file: 标定文件路径（可选）
        """
        self.bag_path = bag_path
        self.left_topic = left_topic
        self.output_dir = Path(output_dir)
        self.typestore = get_typestore(Stores.ROS1_NOETIC)

        # 创建输出目录
        self.left_dir = self.output_dir / "images"
        self.left_dir.mkdir(parents=True, exist_ok=True)

        # 加载相机标定参数
        self.left_undistort_map = None
        self.right_undistort_map = None
        if calib_file:
            self._load_calibration(calib_file)

        print(f"输出目录: {self.output_dir}")
        print(f"左图像目录: {self.left_dir}")
        if calib_file:
            print(f"标定文件: {calib_file}")
            print(f"去畸变: {'启用' if self.left_undistort_map is not None else '未启用'}")

    def _load_calibration(self, calib_file):
        """加载相机标定参数"""
        try:
            with open(calib_file, 'r') as f:
                calib_data = yaml.safe_load(f)

            # 左相机(Camera)
            cam_left = calib_data['Sensor']['Camera']
            left_K = np.array(cam_left['intrinsic']['int_matrix']).reshape(3, 3)
            left_D = np.array(cam_left['intrinsic']['dist_coeff'])
            left_img_size = tuple(cam_left['intrinsic']['image_size'])  # (width, height)

            # 右相机(Camera_R)
            cam_right = calib_data['Sensor']['Camera_R']
            right_K = np.array(cam_right['intrinsic']['int_matrix']).reshape(3, 3)
            right_D = np.array(cam_right['intrinsic']['dist_coeff'])
            right_img_size = tuple(cam_right['intrinsic']['image_size'])

            # 计算去畸变映射
            self.left_undistort_map = cv2.initUndistortRectifyMap(
                left_K, left_D, None, left_K, left_img_size, cv2.CV_32FC1
            )
            self.right_undistort_map = cv2.initUndistortRectifyMap(
                right_K, right_D, None, right_K, right_img_size, cv2.CV_32FC1
            )

            print(f"\n成功加载标定参数:")
            print(f"  左相机内参:\n{left_K}")
            print(f"  左相机畸变系数: {left_D}")

        except Exception as e:
            print(f"\n警告: 加载标定文件失败: {e}")
            print("将不进行去畸变处理")
            self.left_undistort_map = None
            self.right_undistort_map = None

    def _undistort_image(self, image, undistort_map):
        """去畸变处理"""
        if undistort_map is None:
            return image
        return cv2.remap(image, undistort_map[0], undistort_map[1], cv2.INTER_LINEAR)

    def parse(self):
        """解析rosbag并保存图像"""
        if not os.path.exists(self.bag_path):
            print(f"错误: bag文件不存在: {self.bag_path}")
            return

        print(f"开始解析bag文件: {self.bag_path}")

        left_count = 0

        with Reader(self.bag_path) as reader:
            # 检查topic是否存在
            available_topics = [conn.topic for conn in reader.connections]
            if self.left_topic not in available_topics:
                print(f"\n警告: 左相机topic '{self.left_topic}' 不存在")
                print(f"可用topics: {available_topics}")
                return

            # 筛选目标topic的connections
            connections = [c for c in reader.connections if c.topic == self.left_topic]

            print(f"\n开始提取图像...")

            for connection, timestamp, rawdata in reader.messages(connections=connections):
                msg = self.typestore.deserialize_ros1(rawdata, connection.msgtype)

                # 将消息转换为OpenCV图像
                cv_image = imgmsg_to_cv2(msg)

                # 使用消息header中的时间戳（纳秒）
                ts_nsec = msg.header.stamp.sec * 10**9 + msg.header.stamp.nanosec

                # 左相机去畸变
                if self.left_undistort_map is not None:
                    cv_image = self._undistort_image(cv_image, self.left_undistort_map)

                filename = f"{ts_nsec}.png"
                filepath = self.left_dir / filename
                cv2.imwrite(str(filepath), cv_image)
                left_count += 1

                if left_count % 10 == 0:
                    print(f"已保存 {left_count} 张左图像...", end='\r')

        print(f"\n\n解析完成!")
        print(f"左图像: {left_count} 张 -> {self.left_dir}")


def main():
    parser = argparse.ArgumentParser(description='从rosbag中提取左相机图像 (无需ROS环境)')
    parser.add_argument('bag_path', type=str, help='rosbag文件路径')
    parser.add_argument('--left-topic', type=str, default='/rs_camera/left/color/image_raw', help='左相机topic名称')
    parser.add_argument('--output-dir', type=str, default='./stereo_images', help='输出目录路径')
    parser.add_argument('--calib-file', type=str, default=None, help='相机标定文件路径(YAML格式)')

    args = parser.parse_args()

    stereo_parser = StereoBagMonoParser(
        bag_path=args.bag_path,
        left_topic=args.left_topic,
        output_dir=args.output_dir,
        calib_file=args.calib_file
    )

    stereo_parser.parse()


if __name__ == '__main__':
    main()
