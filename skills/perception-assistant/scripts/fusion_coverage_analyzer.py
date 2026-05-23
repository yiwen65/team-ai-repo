#!/usr/bin/env python3
"""
fusion_coverage_analyzer.py
分析多传感器 FOV 覆盖，识别盲区。

Usage:
  python fusion_coverage_analyzer.py --config sensors.yaml --output coverage.html

Input config example (YAML):
  sensors:
    - name: front_camera
      type: camera
      fov_h: 120
      fov_v: 60
      range: 150
      mount: [0.0, 0.0, 1.2, 0.0, 0.0, 0.0]  # x,y,z,roll,pitch,yaw
    - name: top_lidar
      type: lidar
      fov_h: 360
      fov_v: 30
      range: 200
      mount: [0.0, 0.0, 2.0, 0.0, 0.0, 0.0]
"""

import yaml
import numpy as np
import argparse
from dataclasses import dataclass


@dataclass
class Sensor:
    name: str
    sensor_type: str
    fov_h: float
    fov_v: float
    range_m: float
    mount: list  # [x, y, z, roll, pitch, yaw]


def load_config(path):
    with open(path) as f:
        data = yaml.safe_load(f)
    sensors = []
    for s in data["sensors"]:
        sensors.append(Sensor(
            name=s["name"],
            sensor_type=s["type"],
            fov_h=s["fov_h"],
            fov_v=s["fov_v"],
            range_m=s["range"],
            mount=s["mount"]
        ))
    return sensors


def generate_coverage_grid(sensors, grid_res=1.0, radius=100.0):
    """Generate bird's-eye view coverage grid."""
    n = int(2 * radius / grid_res)
    grid = np.zeros((n, n), dtype=bool)
    coverage_map = {s.name: np.zeros((n, n), dtype=bool) for s in sensors}
    
    for i in range(n):
        for j in range(n):
            x = (i - n/2) * grid_res
            y = (j - n/2) * grid_res
            
            for s in sensors:
                # Transform to sensor frame
                mx, my, mz, roll, pitch, yaw = s.mount
                dx, dy = x - mx, y - my
                dist = np.sqrt(dx**2 + dy**2)
                
                if dist > s.range_m:
                    continue
                
                angle = np.arctan2(dy, dx) - yaw
                angle = (angle + np.pi) % (2 * np.pi) - np.pi
                
                half_h = np.radians(s.fov_h / 2)
                half_v = np.radians(s.fov_v / 2)  # simplified: assume flat ground
                
                if abs(angle) <= half_h and dist <= s.range_m:
                    grid[i, j] = True
                    coverage_map[s.name][i, j] = True
    
    return grid, coverage_map, n, grid_res


def analyze_blindspots(grid, sensors, n, grid_res):
    """Identify blind spots and weak coverage zones."""
    total_cells = grid.size
    covered = np.sum(grid)
    
    print("=" * 60)
    print("Sensor Coverage Analysis")
    print("=" * 60)
    print(f"Grid size: {n}x{n}, Resolution: {grid_res}m")
    print(f"Total area: {total_cells * grid_res**2:.0f} m²")
    print(f"Covered: {covered} cells ({covered/total_cells*100:.1f}%)")
    print(f"Blind spots: {total_cells - covered} cells ({(total_cells-covered)/total_cells*100:.1f}%)")
    
    # Identify blind spot clusters
    from scipy import ndimage
    blind = ~grid
    labeled, num_features = ndimage.label(blind)
    
    print(f"\nBlind spot clusters: {num_features}")
    for i in range(1, min(num_features + 1, 6)):
        cluster = labeled == i
        size = np.sum(cluster) * grid_res**2
        if size > 10:
            center = ndimage.center_of_mass(cluster)
            cx = (center[0] - n/2) * grid_res
            cy = (center[1] - n/2) * grid_res
            print(f"  Cluster {i}: ~{size:.0f} m² around ({cx:.1f}, {cy:.1f})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Sensor config YAML")
    parser.add_argument("--output", default="coverage_report.txt", help="Output file")
    parser.add_argument("--grid-res", type=float, default=1.0, help="Grid resolution (m)")
    parser.add_argument("--radius", type=float, default=100.0, help="Analysis radius (m)")
    args = parser.parse_args()
    
    sensors = load_config(args.config)
    grid, cov_map, n, res = generate_coverage_grid(sensors, args.grid_res, args.radius)
    analyze_blindspots(grid, sensors, n, res)


if __name__ == "__main__":
    main()
