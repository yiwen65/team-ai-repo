#!/usr/bin/env python3
"""
trajectory_analyzer.py
解析规划轨迹（csv/rosbag），分析曲率/加速度/舒适性。

Usage:
  python trajectory_analyzer.py --csv trajectory.csv --output analysis.md

CSV format: t, x, y, heading, velocity, acceleration, curvature
"""

import pandas as pd
import numpy as np
import argparse


def analyze_trajectory(df):
    """Analyze trajectory quality."""
    results = {}
    
    # Basic stats
    results["duration"] = df["t"].iloc[-1] - df["t"].iloc[0]
    results["distance"] = np.sum(np.sqrt(np.diff(df["x"])**2 + np.diff(df["y"])**2))
    results["avg_speed"] = results["distance"] / results["duration"]
    
    # Curvature analysis
    if "curvature" in df.columns:
        k = df["curvature"].values
        results["max_curvature"] = np.max(np.abs(k))
        results["avg_curvature"] = np.mean(np.abs(k))
        results["curvature_jumps"] = np.sum(np.abs(np.diff(k)) > 0.01)
    
    # Acceleration
    if "acceleration" in df.columns:
        a = df["acceleration"].values
        results["max_acceleration"] = np.max(a)
        results["min_acceleration"] = np.min(a)
        results["acceleration_rms"] = np.sqrt(np.mean(a**2))
    
    # Jerk (3rd derivative)
    if "acceleration" in df.columns:
        dt = np.diff(df["t"]).mean()
        jerk = np.diff(df["acceleration"].values) / dt
        results["max_jerk"] = np.max(np.abs(jerk))
        results["avg_jerk"] = np.mean(np.abs(jerk))
        results["jerk_rms"] = np.sqrt(np.mean(jerk**2))
    
    # Comfort score (ISO 2631 inspired)
    comfort_penalty = 0
    if "max_jerk" in results:
        if results["max_jerk"] > 3.0:
            comfort_penalty += 2
        elif results["max_jerk"] > 2.5:
            comfort_penalty += 1
    
    if "max_acceleration" in results:
        if results["max_acceleration"] > 2.5:
            comfort_penalty += 2
        elif results["max_acceleration"] > 1.5:
            comfort_penalty += 1
    
    results["comfort_score"] = max(0, 10 - comfort_penalty)
    
    return results


def generate_report(results, output_path):
    lines = ["# 轨迹质量分析报告\n\n"]
    
    lines.append("## 基础信息\n")
    lines.append(f"- 轨迹时长: {results['duration']:.2f} s\n")
    lines.append(f"- 轨迹长度: {results['distance']:.2f} m\n")
    lines.append(f"- 平均速度: {results['avg_speed']:.2f} m/s ({results['avg_speed']*3.6:.1f} km/h)\n\n")
    
    lines.append("## 动力学指标\n")
    if "max_curvature" in results:
        lines.append(f"- 最大曲率: {results['max_curvature']:.4f} 1/m\n")
        lines.append(f"- 平均曲率: {results['avg_curvature']:.4f} 1/m\n")
        lines.append(f"- 曲率跳变次数: {results['curvature_jumps']}\n")
    
    if "max_acceleration" in results:
        lines.append(f"- 最大加速度: {results['max_acceleration']:.2f} m/s²\n")
        lines.append(f"- 最小加速度: {results['min_acceleration']:.2f} m/s²\n")
        lines.append(f"- 加速度 RMS: {results['acceleration_rms']:.2f} m/s²\n")
    
    if "max_jerk" in results:
        lines.append(f"- 最大 jerk: {results['max_jerk']:.2f} m/s³\n")
        lines.append(f"- 平均 jerk: {results['avg_jerk']:.2f} m/s³\n")
        lines.append(f"- Jerk RMS: {results['jerk_rms']:.2f} m/s³\n")
    
    lines.append("\n## 舒适性评分\n")
    score = results["comfort_score"]
    if score >= 8:
        rating = "✅ 优秀"
    elif score >= 6:
        rating = "⚠️ 合格"
    else:
        rating = "❌ 不合格"
    lines.append(f"评分: {score}/10 - {rating}\n\n")
    
    # Issues
    lines.append("## 问题诊断\n")
    issues = []
    
    if results.get("max_jerk", 0) > 2.5:
        issues.append("- jerk 超过舒适阈值 (2.5 m/s³)，乘客可能感到不适")
    if results.get("max_acceleration", 0) > 2.5:
        issues.append("- 加速度过大，建议降低规划激进程度")
    if results.get("curvature_jumps", 0) > 3:
        issues.append("- 曲率跳变较多，轨迹平滑性不足")
    
    if issues:
        lines.extend(issues)
    else:
        lines.append("- 未发现显著问题\n")
    
    report = "".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Trajectory CSV file")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    df = pd.read_csv(args.csv)
    results = analyze_trajectory(df)
    generate_report(results, args.output)


if __name__ == "__main__":
    main()
