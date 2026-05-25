#!/usr/bin/env python3
"""检查地图版本兼容性。"""
import os
import sys

def check_map_version(map_dir, expected_version=None):
    print(f"\n🗺️  地图版本检查: {map_dir}")
    print("=" * 60)
    
    if not os.path.exists(map_dir):
        print(f"  🔴 地图目录不存在: {map_dir}")
        return False
    
    # 查找地图文件
    bin_files = [f for f in os.listdir(map_dir) if f.endswith('.bin') or f.endswith('.xml')]
    print(f"  地图文件数量: {len(bin_files)}")
    for f in bin_files[:5]:
        size = os.path.getsize(os.path.join(map_dir, f))
        print(f"    {f}: {size/1024/1024:.1f} MB")
    
    # 查找版本信息（假设存在 version.txt 或从文件名提取）
    version = None
    version_file = os.path.join(map_dir, "version.txt")
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            version = f.read().strip()
    else:
        # 从文件名猜测
        for f in bin_files:
            if "v" in f.lower():
                version = f
                break
    
    if version:
        print(f"\n  检测到的版本: {version}")
    else:
        print(f"\n  ⚠️ 未检测到版本信息")
    
    if expected_version:
        if version == expected_version:
            print(f"  ✅ 版本匹配 (期望: {expected_version})")
        else:
            print(f"  🔴 版本不匹配! 期望: {expected_version}, 实际: {version}")
            return False
    
    # 检查目录结构完整性
    expected_files = ["base_map.bin", "routing_map.bin", "sim_map.bin"]
    missing = [f for f in expected_files if not os.path.exists(os.path.join(map_dir, f))]
    if missing:
        print(f"\n  ⚠️ 缺失标准文件: {', '.join(missing)}")
    else:
        print(f"\n  ✅ 标准地图文件完整")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python map_version_checker.py <map_dir> [expected_version]")
        sys.exit(1)
    check_map_version(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
