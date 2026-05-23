#!/usr/bin/env python3
"""
control_tracking_analyzer.py
对比规划轨迹与实际控制输出，计算跟踪误差。

Usage:
  python control_tracking_analyzer.py \
    --planned planned.csv --actual actual.csv --output tracking.md
"""

import pandas as pd
import numpy as np
import argparse


def compute_tracking_error(planned, actual):
    """Compute tracking error between planned and actual trajectories."""
    # Interpolate actual to planned time points
    actual_interp = {
        "x": np.interp(planned["t"], actual["t"], actual["x"]),
        "y": np.interp(planned["t"], actual["t"], actual["y"]),
        "v": np.interp(planned["t"], actual["t"], actual["velocity"]),
    }
    
    # Lateral error (perpendicular distance to planned path)
    dx = np.diff(planned["x"])
    dy = np.diff(planned["y"])
    path_heading = np.arctan2(dy, dx)
    
    # Simplified: use heading at each point
    lateral_errors = []
    for i in range(len(planned)):
        if i < len(path_heading):
            heading = path_heading[min(i, len(path_heading)-1)]
            perp_x = -np.sin(heading)
            perp_y = np.cos(heading)
            
            error_x = actual_interp["x"][i] - planned["x"].iloc[i]
            error_y = actual_interp["y"][i] - planned["y"].iloc[i]
            
            lateral_error = error_x * perp_x + error_y * perp_y
            lateral_errors.append(abs(lateral_error))
    
    longitudinal_errors = np.abs(actual_interp["v"] - planned["velocity"])
    
    return {
        "lateral_errors": np.array(lateral_errors),
        "longitudinal_errors": longitudinal_errors.values if hasattr(longitudinal_errors, 'values') else longitudinal_errors,
        "max_lateral": np.max(lateral_errors),
        "rms_lateral": np.sqrt(np.mean(np.array(lateral_errors)**2)),
        "max_longitudinal": np.max(longitudinal_errors),
        "rms_longitudinal": np.sqrt(np.mean(longitudinal_errors**2))
    }


def generate_report(errors, output_path):
    lines = ["# 控制跟踪误差分析报告\n\n"]
    
    lines.append("## 横向误差\n")
    lines.append(f"- 最大横向误差: {errors['max_lateral']:.3f} m\n")
    lines.append(f"- RMS 横向误差: {errors['rms_lateral']:.3f} m\n")
    
    # Grade
    if errors['rms_lateral'] < 0.1:
        grade_lat = "✅ 优秀"
    elif errors['rms_lateral'] < 0.2:
        grade_lat = "⚠️ 合格"
    else:
        grade_lat = "❌ 不合格"
    lines.append(f"- 评级: {grade_lat}\n\n")
    
    lines.append("## 纵向误差\n")
    lines.append(f"- 最大纵向速度误差: {errors['max_longitudinal']:.2f} m/s\n")
    lines.append(f"- RMS 纵向速度误差: {errors['rms_longitudinal']:.2f} m/s\n")
    
    if errors['rms_longitudinal'] < 0.5:
        grade_long = "✅ 优秀"
    elif errors['rms_longitudinal'] < 1.0:
        grade_long = "⚠️ 合格"
    else:
        grade_long = "❌ 不合格"
    lines.append(f"- 评级: {grade_long}\n\n")
    
    # Analysis
    lines.append("## 诊断建议\n")
    if errors['max_lateral'] > 0.5:
        lines.append("- 横向误差过大，检查：\n")
        lines.append("  - MPC 预测 horizon 是否足够\n")
        lines.append("  - 舵角到轮胎响应的延迟补偿\n")
        lines.append("  - 参考线曲率是否突变\n")
    
    if errors['max_longitudinal'] > 2.0:
        lines.append("- 纵向速度跟踪差，检查：\n")
        lines.append("  - 油门/刹车标定曲线\n")
        lines.append("  - 纵向 MPC 参数（N, dt, Q, R）\n")
        lines.append("  - 执行器响应延迟\n")
    
    report = "".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--planned", required=True, help="Planned trajectory CSV")
    parser.add_argument("--actual", required=True, help="Actual trajectory CSV")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    planned = pd.read_csv(args.planned)
    actual = pd.read_csv(args.actual)
    
    errors = compute_tracking_error(planned, actual)
    generate_report(errors, args.output)


if __name__ == "__main__":
    main()
