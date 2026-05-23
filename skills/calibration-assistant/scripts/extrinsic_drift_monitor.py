#!/usr/bin/env python3
"""
extrinsic_drift_monitor.py
基于场景特征（车道线、灯杆）检测外参漂移。

Usage:
  python extrinsic_drift_monitor.py \
    --calib calib.yaml \
    --rosbag driving.bag \
    --topic /camera/front/image \
    --output drift_report.md
"""

import cv2
import numpy as np
import yaml
import argparse
from collections import deque


class DriftMonitor:
    """Monitor extrinsic drift using scene features."""
    
    def __init__(self, calib, window_size=100):
        self.calib = calib
        self.window_size = window_size
        self.lane_angles = deque(maxlen=window_size)
        self.pole_angles = deque(maxlen=window_size)
    
    def detect_lane_lines(self, image):
        """Detect lane lines and compute angle."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Hough transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=100, maxLineGap=10)
        
        if lines is None:
            return None
        
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            # Filter near-vertical lines (lane lines)
            if abs(abs(angle) - 90) < 20:
                angles.append(angle)
        
        return np.median(angles) if angles else None
    
    def detect_poles(self, image):
        """Detect vertical poles and compute angle."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Simple vertical edge detection
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Threshold and find vertical lines
        _, thresh = cv2.threshold(np.abs(sobel_y), 100, 255, cv2.THRESH_BINARY)
        
        # Morphological operations to get vertical lines
        kernel = np.ones((20, 1), np.uint8)
        vertical = cv2.morphologyEx(thresh.astype(np.uint8), cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        angles = []
        for cnt in contours:
            if cv2.contourArea(cnt) < 100:
                continue
            rect = cv2.minAreaRect(cnt)
            angle = rect[2]
            if abs(angle) < 15 or abs(angle - 90) < 15:
                angles.append(angle)
        
        return np.median(angles) if angles else None
    
    def process_frame(self, image):
        """Process a single frame and update statistics."""
        lane_angle = self.detect_lane_lines(image)
        pole_angle = self.detect_poles(image)
        
        if lane_angle is not None:
            self.lane_angles.append(lane_angle)
        if pole_angle is not None:
            self.pole_angles.append(pole_angle)
    
    def get_drift_stats(self):
        """Compute drift statistics."""
        stats = {}
        
        if len(self.lane_angles) > 10:
            stats["lane_mean"] = np.mean(self.lane_angles)
            stats["lane_std"] = np.std(self.lane_angles)
            stats["lane_max_dev"] = max(abs(a - stats["lane_mean"]) for a in self.lane_angles)
        
        if len(self.pole_angles) > 10:
            stats["pole_mean"] = np.mean(self.pole_angles)
            stats["pole_std"] = np.std(self.pole_angles)
            stats["pole_max_dev"] = max(abs(a - stats["pole_mean"]) for a in self.pole_angles)
        
        return stats
    
    def check_drift(self):
        """Check if drift exceeds thresholds."""
        stats = self.get_drift_stats()
        alerts = []
        
        if "lane_max_dev" in stats and stats["lane_max_dev"] > 1.0:
            alerts.append(f"车道线角度漂移 {stats['lane_max_dev']:.2f}° > 1.0° 阈值")
        
        if "pole_max_dev" in stats and stats["pole_max_dev"] > 2.0:
            alerts.append(f"灯杆垂直度漂移 {stats['pole_max_dev']:.2f}° > 2.0° 阈值")
        
        return alerts, stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calib", help="Calibration YAML (for reference angles)")
    parser.add_argument("--video", help="Video file path")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    monitor = DriftMonitor(None)
    
    if args.video:
        cap = cv2.VideoCapture(args.video)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            monitor.process_frame(frame)
        cap.release()
    
    alerts, stats = monitor.check_drift()
    
    lines = ["# 外参漂移监控报告\n"]
    lines.append(f"- 分析帧数: {len(monitor.lane_angles)}\n")
    
    if stats:
        lines.append("## 统计结果\n")
        for k, v in stats.items():
            lines.append(f"- {k}: {v:.3f}\n")
    
    if alerts:
        lines.append("\n## ⚠️ 漂移告警\n")
        for alert in alerts:
            lines.append(f"- {alert}\n")
    else:
        lines.append("\n✅ 未检测到显著漂移\n")
    
    report = "".join(lines)
    print(report)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)


if __name__ == "__main__":
    main()
