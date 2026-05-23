#!/usr/bin/env python3
"""
reprojection_analyzer.py
计算多距离重投影误差，生成可视化报告。

Usage:
  python reprojection_analyzer.py \
    --calib calib.yaml \
    --data test_data/ \
    --distances 5 20 50 100 \
    --output report.md
"""

import yaml
import numpy as np
import cv2
import argparse
from pathlib import Path
import glob


def load_calib(path):
    with open(path) as f:
        return yaml.safe_load(f)


def project_points(points_3d, K, D, R, t):
    """Project 3D points to image plane."""
    rvec, _ = cv2.Rodrigues(R)
    projected, _ = cv2.projectPoints(points_3d, rvec, t, K, D)
    return projected.reshape(-1, 2)


def analyze_distance(data_dir, calib, distance, camera_name="front_camera"):
    """Analyze reprojection error at specific distance."""
    cam = calib["cameras"][camera_name]
    K = np.array(cam["K"])
    D = np.array(cam["D"])
    
    # Load extrinsic (lidar to camera)
    lidar_to_cam = np.array(calib["extrinsics"]["lidar_to_camera"])
    R = lidar_to_cam[:3, :3]
    t = lidar_to_cam[:3, 3]
    
    # Find test data for this distance
    pattern = f"{data_dir}/{distance}m_*.npz"
    files = glob.glob(pattern)
    
    if not files:
        return None
    
    errors = []
    for f in files:
        data = np.load(f)
        points_3d = data["points_3d"]  # Nx3 in lidar frame
        points_2d_gt = data["points_2d"]  # Nx2 in image
        
        projected = project_points(points_3d, K, D, R, t)
        error = np.linalg.norm(projected - points_2d_gt, axis=1)
        errors.extend(error)
    
    errors = np.array(errors)
    return {
        "distance": distance,
        "count": len(errors),
        "mean": np.mean(errors),
        "rms": np.sqrt(np.mean(errors**2)),
        "max": np.max(errors),
        "std": np.std(errors),
        "percentile_95": np.percentile(errors, 95),
        "percentile_99": np.percentile(errors, 99)
    }


def generate_report(results, output_path):
    lines = ["# 重投影误差分析报告\n"]
    lines.append("| 距离 (m) | 样本数 | 均值 (px) | RMS (px) | Max (px) | P95 (px) | P99 (px) | 评级 |")
    lines.append("|---------|--------|----------|---------|---------|---------|---------|------|")
    
    for r in results:
        if r["rms"] < 3:
            grade = "✅ 优秀"
        elif r["rms"] < 5:
            grade = "⚠️ 合格"
        else:
            grade = "❌ 不合格"
        
        lines.append(
            f"| {r['distance']} | {r['count']} | {r['mean']:.2f} | {r['rms']:.2f} | "
            f"{r['max']:.2f} | {r['percentile_95']:.2f} | {r['percentile_99']:.2f} | {grade} |"
        )
    
    # Flag issues
    lines.append("\n## 问题分析\n")
    for r in results:
        if r["max"] > 10:
            lines.append(f"- ❌ {r['distance']}m 处最大误差 {r['max']:.1f}px，可能存在标定板角点误提取或外参错误")
        elif r["rms"] > 5:
            lines.append(f"- ⚠️ {r['distance']}m 处 RMS {r['rms']:.1f}px，建议检查畸变模型或重新采集数据")
    
    report = "\n".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calib", required=True, help="Calibration YAML")
    parser.add_argument("--data", required=True, help="Test data directory")
    parser.add_argument("--distances", nargs="+", type=float, default=[5, 20, 50, 100])
    parser.add_argument("--camera", default="front_camera")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    calib = load_calib(args.calib)
    results = []
    
    for d in args.distances:
        result = analyze_distance(args.data, calib, d, args.camera)
        if result:
            results.append(result)
    
    generate_report(results, args.output)


if __name__ == "__main__":
    main()
