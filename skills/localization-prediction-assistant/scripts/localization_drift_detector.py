#!/usr/bin/env python3
"""检测定位漂移。"""
import sys

def detect_drift(localization_samples):
    """
    localization_samples: list of dicts with keys: timestamp, x, y, z
    """
    print("\n🧭 定位漂移检测")
    print("=" * 60)
    
    if len(localization_samples) < 2:
        print("  ⚠️ 数据不足")
        return
    
    # 计算相邻帧位移和速度
    drifts = []
    for i in range(1, len(localization_samples)):
        prev = localization_samples[i-1]
        curr = localization_samples[i]
        dt = (curr["timestamp"] - prev["timestamp"]) / 1e9  # s
        if dt <= 0:
            continue
        dx = curr["x"] - prev["x"]
        dy = curr["y"] - prev["y"]
        dist = (dx**2 + dy**2)**0.5
        speed = dist / dt
        drifts.append({"dt": dt, "dist": dist, "speed": speed, "idx": i})
    
    if not drifts:
        print("  ⚠️ 无法计算有效位移")
        return
    
    # 统计
    speeds = [d["speed"] for d in drifts]
    avg_speed = sum(speeds) / len(speeds)
    max_speed = max(speeds)
    
    print(f"  样本数: {len(drifts)}")
    print(f"  平均速度: {avg_speed:.2f} m/s")
    print(f"  最大速度: {max_speed:.2f} m/s")
    
    # 检测跳变（> 5m 的瞬时位移视为跳变）
    jumps = [d for d in drifts if d["dist"] > 5.0]
    if jumps:
        print(f"\n  🔴 发现 {len(jumps)} 次定位跳变 (> 5m)")
        for j in jumps[:5]:
            print(f"    帧 {j['idx']}: 位移 {j['dist']:.2f}m @ {j['speed']:.2f}m/s")
    else:
        print(f"\n  ✅ 无明显定位跳变")
    
    # 检测停滞（> 3s 无变化视为可能失锁）
    if avg_speed < 0.1 and max_speed > 1.0:
        print("  ⚠️ 速度分布异常（平均极低但存在峰值），可能为定位失锁后重收敛")

if __name__ == "__main__":
    # 示例
    samples = [
        {"timestamp": 0, "x": 0, "y": 0, "z": 0},
        {"timestamp": 1e9, "x": 1.0, "y": 0, "z": 0},
        {"timestamp": 2e9, "x": 2.0, "y": 0.1, "z": 0},
        {"timestamp": 3e9, "x": 15.0, "y": 0, "z": 0},  # 跳变
        {"timestamp": 4e9, "x": 15.2, "y": 0, "z": 0},
    ]
    detect_drift(samples)
