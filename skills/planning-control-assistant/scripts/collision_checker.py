#!/usr/bin/env python3
"""
collision_checker.py
基于 ego 轨迹和障碍物预测做碰撞检测。

Usage:
  python collision_checker.py \
    --ego ego_trajectory.csv \
    --obstacles obstacles.json \
    --output collision_report.md
"""

import json
import pandas as pd
import numpy as np
import argparse


def load_obstacles(path):
    with open(path) as f:
        return json.load(f)


def predict_obstacle_trajectory(obstacle, t_start, t_end, dt=0.1):
    """Simple constant velocity prediction."""
    times = np.arange(t_start, t_end + dt, dt)
    traj = []
    for t in times:
        x = obstacle["x"] + obstacle["vx"] * (t - t_start)
        y = obstacle["y"] + obstacle["vy"] * (t - t_start)
        traj.append({"t": t, "x": x, "y": y, "heading": obstacle["heading"]})
    return pd.DataFrame(traj)


def get_vehicle_corners(x, y, heading, length=4.5, width=1.8):
    """Get vehicle corner points."""
    cos_h = np.cos(heading)
    sin_h = np.sin(heading)
    
    # Vehicle center to corners
    corners_local = [
        (length/2, width/2),
        (length/2, -width/2),
        (-length/2, -width/2),
        (-length/2, width/2)
    ]
    
    corners = []
    for cx, cy in corners_local:
        corners.append({
            "x": x + cx * cos_h - cy * sin_h,
            "y": y + cx * sin_h + cy * cos_h
        })
    
    return corners


def check_collision(ego_corners, obs_corners):
    """Check if two polygons intersect using SAT."""
    def project_polygon(axis, corners):
        dots = [c["x"] * axis["x"] + c["y"] * axis["y"] for c in corners]
        return min(dots), max(dots)
    
    def get_axes(corners):
        axes = []
        for i in range(len(corners)):
            j = (i + 1) % len(corners)
            edge = {
                "x": corners[j]["x"] - corners[i]["x"],
                "y": corners[j]["y"] - corners[i]["y"]
            }
            # Perpendicular
            axes.append({"x": -edge["y"], "y": edge["x"]})
        return axes
    
    axes = get_axes(ego_corners) + get_axes(obs_corners)
    
    for axis in axes:
        # Normalize
        mag = np.sqrt(axis["x"]**2 + axis["y"]**2)
        if mag < 1e-6:
            continue
        axis = {"x": axis["x"]/mag, "y": axis["y"]/mag}
        
        min1, max1 = project_polygon(axis, ego_corners)
        min2, max2 = project_polygon(axis, obs_corners)
        
        if max1 < min2 or max2 < min1:
            return False
    
    return True


def analyze_collisions(ego_df, obstacles, safety_margin=0.5):
    """Check collisions along trajectory."""
    collisions = []
    
    for idx, ego_state in ego_df.iterrows():
        t = ego_state["t"]
        ego_corners = get_vehicle_corners(
            ego_state["x"], ego_state["y"], ego_state["heading"]
        )
        
        for obs in obstacles:
            # Predict obstacle at time t
            obs_t = t
            obs_x = obs["x"] + obs.get("vx", 0) * obs_t
            obs_y = obs["y"] + obs.get("vy", 0) * obs_t
            
            obs_corners = get_vehicle_corners(
                obs_x, obs_y, obs["heading"],
                obs.get("length", 4.5), obs.get("width", 1.8)
            )
            
            # Apply safety margin by expanding ego
            # (Simplified: just check raw collision)
            if check_collision(ego_corners, obs_corners):
                collisions.append({
                    "time": t,
                    "ego_x": ego_state["x"],
                    "ego_y": ego_state["y"],
                    "obstacle_id": obs.get("id", "unknown"),
                    "obstacle_x": obs_x,
                    "obstacle_y": obs_y,
                    "severity": "COLLISION"
                })
    
    return collisions


def generate_report(collisions, output_path):
    lines = ["# 碰撞检测报告\n\n"]
    
    if not collisions:
        lines.append("✅ 未检测到碰撞\n")
    else:
        lines.append(f"❌ 检测到 {len(collisions)} 个碰撞时刻\n\n")
        lines.append("| 时间 (s) | Ego X | Ego Y | 障碍物 ID | 障碍物 X | 障碍物 Y |\n")
        lines.append("|---------|-------|-------|----------|---------|---------|\n")
        
        for c in collisions:
            lines.append(
                f"| {c['time']:.2f} | {c['ego_x']:.2f} | {c['ego_y']:.2f} | "
                f"{c['obstacle_id']} | {c['obstacle_x']:.2f} | {c['obstacle_y']:.2f} |\n"
            )
        
        lines.append("\n## 建议\n")
        lines.append("- 检查规划轨迹是否与障碍物预测轨迹冲突\n")
        lines.append("- 确认障碍物预测模型（匀速假设可能不准确）\n")
        lines.append("- 增加安全余量或调整规划策略\n")
    
    report = "".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ego", required=True, help="Ego trajectory CSV")
    parser.add_argument("--obstacles", required=True, help="Obstacles JSON")
    parser.add_argument("--margin", type=float, default=0.5, help="Safety margin (m)")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    ego = pd.read_csv(args.ego)
    obstacles = load_obstacles(args.obstacles)
    
    collisions = analyze_collisions(ego, obstacles, args.margin)
    generate_report(collisions, args.output)


if __name__ == "__main__":
    main()
