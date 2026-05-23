#!/usr/bin/env python3
"""
log_analyzer.py
解析 ROS2/系统日志，定位错误根因。

Usage:
  python log_analyzer.py --log ros2_log.txt --output analysis.md
"""

import re
import argparse
from collections import Counter, defaultdict


def parse_ros2_log(log_path):
    """Parse ROS2 log file."""
    errors = []
    warnings = []
    node_stats = defaultdict(lambda: {"errors": 0, "warnings": 0})
    
    patterns = {
        "error": re.compile(r"\[ERROR\].*\[(\w+)\].*:(.*)"),
        "warning": re.compile(r"\[WARN\].*\[(\w+)\].*:(.*)"),
        "fatal": re.compile(r"\[FATAL\].*\[(\w+)\].*:(.*)"),
    }
    
    with open(log_path) as f:
        for line in f:
            for level, pattern in patterns.items():
                match = pattern.search(line)
                if match:
                    node = match.group(1)
                    message = match.group(2).strip()
                    
                    if level in ["error", "fatal"]:
                        errors.append({"node": node, "message": message})
                        node_stats[node]["errors"] += 1
                    else:
                        warnings.append({"node": node, "message": message})
                        node_stats[node]["warnings"] += 1
    
    return errors, warnings, node_stats


def analyze_errors(errors):
    """Analyze error patterns."""
    # Group by message pattern
    message_patterns = Counter()
    for err in errors:
        # Simplify message for grouping
        msg = err["message"]
        # Extract key part (first few words)
        key = " ".join(msg.split()[:5])
        message_patterns[key] += 1
    
    return message_patterns


def generate_report(errors, warnings, node_stats, output_path):
    lines = ["# 日志分析报告\n\n"]
    
    lines.append("## 统计\n")
    lines.append(f"- 错误数: {len(errors)}\n")
    lines.append(f"- 警告数: {len(warnings)}\n")
    lines.append(f"- 涉及节点: {len(node_stats)}\n\n")
    
    # Node breakdown
    lines.append("## 节点统计\n")
    lines.append("| 节点 | 错误 | 警告 |\n")
    lines.append("|------|------|------|\n")
    for node, stats in sorted(node_stats.items(), key=lambda x: -x[1]["errors"]):
        lines.append(f"| {node} | {stats['errors']} | {stats['warnings']} |\n")
    lines.append("\n")
    
    # Error patterns
    if errors:
        patterns = analyze_errors(errors)
        lines.append("## 常见错误模式\n")
        for pattern, count in patterns.most_common(10):
            lines.append(f"- `{pattern}`: {count} 次\n")
        lines.append("\n")
    
    # Recent errors
    if errors:
        lines.append("## 最新错误\n")
        for err in errors[-5:]:
            lines.append(f"- `[{err['node']}]` {err['message']}\n")
        lines.append("\n")
    
    # Recommendations
    lines.append("## 诊断建议\n")
    
    if any("timeout" in e["message"].lower() for e in errors):
        lines.append("- 发现超时错误，检查：\n")
        lines.append("  - 节点计算负载（CPU/GPU）\n")
        lines.append("  - 话题队列大小和消息频率\n")
        lines.append("  - 网络延迟（多机通信）\n")
    
    if any("memory" in e["message"].lower() for e in errors):
        lines.append("- 发现内存相关错误，检查：\n")
        lines.append("  - 内存泄漏（valgrind/ASan）\n")
        lines.append("  - 大对象拷贝（点云/图像）\n")
        lines.append("  - 内存限制（ulimit/cgroup）\n")
    
    if any("cuda" in e["message"].lower() or "gpu" in e["message"].lower() for e in errors):
        lines.append("- 发现 GPU/CUDA 错误，检查：\n")
        lines.append("  - CUDA 版本兼容性\n")
        lines.append("  - 显存不足（nvidia-smi）\n")
        lines.append("  - TensorRT 引擎兼容性\n")
    
    report = "".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True, help="Log file path")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    errors, warnings, node_stats = parse_ros2_log(args.log)
    generate_report(errors, warnings, node_stats, args.output)


if __name__ == "__main__":
    main()
