#!/usr/bin/env python3
"""检查多传感器时间同步状态。"""
import sys
import json
from datetime import datetime

def check_sync(sensor_data):
    """
    sensor_data: dict of {sensor_name: [timestamps]}
    """
    print("\n⏱️  多传感器时间同步检查")
    print("=" * 60)
    
    # 找出每个传感器的最新时间戳
    latest = {}
    for name, ts_list in sensor_data.items():
        if ts_list:
            latest[name] = max(ts_list)
    
    if not latest:
        print("  ⚠️ 无传感器数据")
        return
    
    # 计算两两偏差
    sensors = list(latest.keys())
    base_ts = latest[sensors[0]]
    
    print(f"\n  基准传感器: {sensors[0]} (ts={base_ts})")
    print(f"  {'传感器':20s} {'时间戳':20s} {'偏差(ms)':12s} {'状态'}")
    print("  " + "-" * 60)
    
    for name in sensors:
        ts = latest[name]
        diff_ms = abs(ts - base_ts) / 1e6  # 假设时间戳为 ns
        status = "✅" if diff_ms < 5 else "⚠️" if diff_ms < 50 else "🔴"
        print(f"  {name:20s} {ts:20d} {diff_ms:10.2f}   {status}")
    
    max_diff = max(abs(latest[s] - base_ts) for s in sensors) / 1e6
    print(f"\n  最大时间偏差: {max_diff:.2f} ms")
    if max_diff > 50:
        print("  🔴 警告: 时间偏差 > 50ms，多传感器融合可能异常")
    elif max_diff > 5:
        print("  ⚠️ 提示: 时间偏差 > 5ms，建议优化同步配置")
    else:
        print("  ✅ 时间同步良好")

if __name__ == "__main__":
    # 示例用法
    example = {
        "lidar_front": [1620000000000000000, 1620000000100000000],
        "camera_front": [1620000000005000000, 1620000000105000000],
        "radar_front": [1620000000030000000, 1620000000130000000],
    }
    check_sync(example)
