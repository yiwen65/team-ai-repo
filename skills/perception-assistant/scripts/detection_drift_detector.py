#!/usr/bin/env python3
"""
detection_drift_detector.py
对比两版模型的检测结果，定位精度漂移的类别和场景。

Usage:
  python detection_drift_detector.py \
    --baseline baseline_results.json \
    --new new_results.json \
    --output drift_report.md

Input JSON format (per image/frame):
  {
    "frame_id": "0001",
    "detections": [
      {"class": "car", "x": 100, "y": 200, "w": 50, "h": 30, "score": 0.95}
    ]
  }
"""

import json
import argparse
from collections import defaultdict
import numpy as np


def load_results(path):
    with open(path) as f:
        return json.load(f)


def compute_iou(box1, box2):
    x1, y1, w1, h1 = box1["x"], box1["y"], box1["w"], box1["h"]
    x2, y2, w2, h2 = box2["x"], box2["y"], box2["w"], box2["h"]
    
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)
    
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - inter_area
    
    return inter_area / union_area if union_area > 0 else 0


def match_detections(baseline_dets, new_dets, iou_thresh=0.5):
    """Match detections between two versions."""
    matched = []
    unmatched_baseline = []
    unmatched_new = list(new_dets)
    
    for bdet in baseline_dets:
        best_iou = 0
        best_idx = -1
        for i, ndet in enumerate(unmatched_new):
            if bdet["class"] != ndet["class"]:
                continue
            iou = compute_iou(bdet, ndet)
            if iou > best_iou:
                best_iou = iou
                best_idx = i
        
        if best_iou >= iou_thresh:
            matched.append((bdet, unmatched_new[best_idx], best_iou))
            unmatched_new.pop(best_idx)
        else:
            unmatched_baseline.append(bdet)
    
    return matched, unmatched_baseline, unmatched_new


def analyze_drift(baseline, new_results, iou_thresh=0.5):
    """Analyze detection drift across all frames."""
    class_stats = defaultdict(lambda: {
        "matched": 0, "baseline_count": 0, "new_count": 0,
        "score_drops": [], "iou_list": [], "lost": 0, "gained": 0
    })
    
    baseline_frames = {r["frame_id"]: r for r in baseline}
    new_frames = {r["frame_id"]: r for r in new_results}
    
    all_frames = set(baseline_frames.keys()) | set(new_frames.keys())
    
    for frame_id in sorted(all_frames):
        b_dets = baseline_frames.get(frame_id, {}).get("detections", [])
        n_dets = new_frames.get(frame_id, {}).get("detections", [])
        
        # Count per class
        for d in b_dets:
            class_stats[d["class"]]["baseline_count"] += 1
        for d in n_dets:
            class_stats[d["class"]]["new_count"] += 1
        
        matched, lost, gained = match_detections(b_dets, n_dets, iou_thresh)
        
        for bdet, ndet, iou in matched:
            c = bdet["class"]
            class_stats[c]["matched"] += 1
            class_stats[c]["iou_list"].append(iou)
            class_stats[c]["score_drops"].append(bdet["score"] - ndet["score"])
        
        for d in lost:
            class_stats[d["class"]]["lost"] += 1
        for d in gained:
            class_stats[d["class"]]["gained"] += 1
    
    return class_stats


def print_report(stats, output_path):
    lines = []
    lines.append("# 检测模型漂移分析报告\n")
    lines.append("| 类别 | 基线数量 | 新版数量 | 匹配 | 丢失 | 新增 | 平均IoU | 得分变化 | 召回率变化 |")
    lines.append("|------|---------|---------|------|------|------|---------|----------|-----------|")
    
    for cls, s in sorted(stats.items()):
        baseline = s["baseline_count"]
        new = s["new_count"]
        matched = s["matched"]
        lost = s["lost"]
        gained = s["gained"]
        avg_iou = np.mean(s["iou_list"]) if s["iou_list"] else 0
        avg_score_change = np.mean(s["score_drops"]) if s["score_drops"] else 0
        recall_old = matched / baseline if baseline > 0 else 0
        recall_new = matched / new if new > 0 else 0
        recall_delta = (recall_new - recall_old) * 100
        
        lines.append(
            f"| {cls} | {baseline} | {new} | {matched} | {lost} | {gained} | "
            f"{avg_iou:.3f} | {avg_score_change:+.3f} | {recall_delta:+.1f}% |"
        )
        
        # Flag critical issues
        if lost > baseline * 0.1:
            lines.append(f"\n⚠️ **{cls}**: 丢失率 > 10% ({lost}/{baseline})，建议重点排查")
        if avg_score_change < -0.1:
            lines.append(f"\n⚠️ **{cls}**: 平均置信度下降 {abs(avg_score_change):.3f}，可能阈值过滤受影响")
    
    report = "\n".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)
        print(f"\nReport saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True, help="Baseline results JSON")
    parser.add_argument("--new", required=True, help="New model results JSON")
    parser.add_argument("--output", help="Output report path")
    parser.add_argument("--iou-thresh", type=float, default=0.5, help="Matching IoU threshold")
    args = parser.parse_args()
    
    baseline = load_results(args.baseline)
    new_results = load_results(args.new)
    
    stats = analyze_drift(baseline, new_results, args.iou_thresh)
    print_report(stats, args.output)


if __name__ == "__main__":
    main()
