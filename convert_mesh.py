#!/usr/bin/env python3
"""
PLY格式mesh文件转换脚本
将PLY格式的mesh文件转换为OBJ和STL格式，用于3D打印
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import trimesh
except ImportError:
    print("错误: 需要安装trimesh库")
    print("请运行: pip install trimesh")
    sys.exit(1)


def convert_ply_to_obj_stl(input_ply_path, output_dir=None, output_name=None):
    """
    将PLY文件转换为OBJ和STL格式
    
    参数:
        input_ply_path: 输入的PLY文件路径
        output_dir: 输出目录，默认为输入文件所在目录
        output_name: 输出文件名（不含扩展名），默认使用输入文件名
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_ply_path):
        print(f"错误: 输入文件不存在: {input_ply_path}")
        return False
    
    # 加载PLY文件
    print(f"正在加载PLY文件: {input_ply_path}")
    try:
        mesh = trimesh.load(input_ply_path)
    except Exception as e:
        print(f"错误: 无法加载PLY文件: {e}")
        return False
    
    # 检查是否成功加载为mesh
    if not isinstance(mesh, trimesh.Trimesh):
        print(f"错误: 文件不是有效的mesh数据")
        return False
    
    print(f"成功加载mesh - 顶点数: {len(mesh.vertices)}, 面数: {len(mesh.faces)}")
    
    # 确定输出目录和文件名
    input_path = Path(input_ply_path)
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    if output_name is None:
        output_name = input_path.stem
    
    # 输出文件路径
    obj_path = output_dir / f"{output_name}.obj"
    stl_path = output_dir / f"{output_name}.stl"
    
    # 转换为OBJ格式（不包含颜色信息）
    print(f"\n正在导出OBJ文件: {obj_path}")
    try:
        # 移除顶点颜色信息
        mesh_no_color = mesh.copy()
        mesh_no_color.visual = trimesh.visual.ColorVisuals()
        mesh_no_color.export(str(obj_path), include_color=False)
        print(f"✓ OBJ文件导出成功（无颜色信息）")
    except Exception as e:
        print(f"✗ OBJ导出失败: {e}")
        return False
    
    # 转换为STL格式
    print(f"\n正在导出STL文件: {stl_path}")
    try:
        mesh.export(str(stl_path))
        print(f"✓ STL文件导出成功")
    except Exception as e:
        print(f"✗ STL导出失败: {e}")
        return False
    
    # 显示mesh信息
    print("\n=== Mesh信息 ===")
    print(f"顶点数量: {len(mesh.vertices)}")
    print(f"面数量: {len(mesh.faces)}")
    print(f"是否闭合: {mesh.is_watertight}")
    print(f"表面积: {mesh.area:.2f}")
    print(f"体积: {mesh.volume:.2f}")
    print(f"边界框: {mesh.bounds}")
    
    print("\n转换完成！")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="将PLY格式的mesh文件转换为OBJ和STL格式，用于3D打印",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python convert_mesh.py input.ply
  python convert_mesh.py input.ply -o output_dir
  python convert_mesh.py input.ply -o output_dir -n my_model
        """
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="输入的PLY文件路径"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=None,
        help="输出目录（默认为输入文件所在目录）"
    )
    
    parser.add_argument(
        "-n", "--name",
        type=str,
        default=None,
        help="输出文件名（不含扩展名，默认使用输入文件名）"
    )
    
    args = parser.parse_args()
    
    # 执行转换
    success = convert_ply_to_obj_stl(
        args.input,
        args.output_dir,
        args.name
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
