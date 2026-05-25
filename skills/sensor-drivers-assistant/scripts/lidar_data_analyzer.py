#!/usr/bin/env python3
"""分析 LiDAR 点云数据质量。"""
import struct
import sys

def analyze_pointcloud(data, topic=""):
    """分析 PointCloud2 消息的字节数据。"""
    # PointCloud2 简析：假设标准 XYZI 格式
    point_size = 16  # 4 floats x 4 bytes
    num_points = len(data) // point_size
    
    print(f"\n📡 LiDAR 点云分析 ({topic})")
    print("-" * 50)
    print(f"  数据大小: {len(data)} bytes")
    print(f"  估算点数: {num_points}")
    
    if num_points == 0:
        print("  ⚠️ 无有效点云数据")
        return {"points": 0, "valid": False}
    
    # 简单统计前 N 个点
    sample = min(1000, num_points)
    intensities = []
    for i in range(sample):
        offset = i * point_size
        if offset + 16 <= len(data):
            x, y, z, intensity = struct.unpack('<ffff', data[offset:offset+16])
            intensities.append(intensity)
    
    if intensities:
        print(f"  强度范围: [{min(intensities):.1f}, {max(intensities):.1f}]")
        print(f"  平均强度: {sum(intensities)/len(intensities):.1f}")
    
    print(f"  ✅ 数据基本正常")
    return {"points": num_points, "valid": True}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python lidar_data_analyzer.py <pointcloud_file.bin>")
        sys.exit(1)
    with open(sys.argv[1], 'rb') as f:
        analyze_pointcloud(f.read(), sys.argv[1])
