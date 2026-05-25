#!/usr/bin/env python3
"""分析 Cyber RT .record 录制文件信息。"""
import os
import sys
import struct

def analyze_record(record_path):
    if not os.path.exists(record_path):
        print(f"❌ 文件不存在: {record_path}")
        return
    
    file_size = os.path.getsize(record_path)
    print(f"\n📁 Record 文件分析: {record_path}")
    print("=" * 60)
    print(f"  文件大小: {file_size / 1024 / 1024:.2f} MB")
    
    # 读取头部信息（简化解析）
    with open(record_path, 'rb') as f:
        header = f.read(64)
        if len(header) < 16:
            print("  ⚠️ 文件过小，可能损坏")
            return
        
        # Record 文件头部 magic: 0x0001 0x0002 0x0003 0x0004
        magic = struct.unpack('<4I', header[:16])
        if magic == (1, 2, 3, 4):
            print("  ✅ 文件头部校验通过 (Apollo Record Format)")
        else:
            print(f"  ⚠️ 非标准 Record 文件 (magic={magic})")
    
    # 尝试用 cyber_recorder info 获取详细信息
    import subprocess
    try:
        result = subprocess.run(
            ["cyber_recorder", "info", record_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("\n  📊 cyber_recorder 信息:")
            for line in result.stdout.split('\n')[:30]:
                if line.strip():
                    print(f"    {line}")
        else:
            print(f"\n  ⚠️ cyber_recorder 解析失败: {result.stderr[:200]}")
    except FileNotFoundError:
        print("\n  ⚠️ cyber_recorder 命令未找到，请确认 Apollo 环境已 source")
    except Exception as e:
        print(f"\n  ⚠️ 解析异常: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python record_analyzer.py <record_file>")
        sys.exit(1)
    analyze_record(sys.argv[1])
