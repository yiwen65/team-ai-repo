#!/usr/bin/env python3
"""
disengagement_analyzer.py
解析脱离记录，分类根因，统计趋势。

Usage:
  python disengagement_analyzer.py --csv disengagements.csv --output report.md

CSV format: timestamp, location, scenario, disengagement_type, root_cause, mileage
"""

import pandas as pd
import numpy as np
import argparse
from collections import Counter


def analyze_disengagements(df):
    """Analyze disengagement data."""
    results = {}
    
    # Basic stats
    total = len(df)
    total_mileage = df["mileage"].max() - df["mileage"].min()
    
    results["total_disengagements"] = total
    results["total_mileage_km"] = total_mileage
    results["disengagement_rate"] = total / total_mileage * 100 if total_mileage > 0 else 0
    
    # By type
    type_counts = Counter(df["disengagement_type"])
    results["by_type"] = dict(type_counts.most_common())
    
    # By root cause
    cause_counts = Counter(df["root_cause"])
    results["by_cause"] = dict(cause_counts.most_common())
    
    # By scenario
    scenario_counts = Counter(df["scenario"])
    results["by_scenario"] = dict(scenario_counts.most_common())
    
    # Trend over mileage (binned)
    bins = np.arange(0, total_mileage + 100, 100)
    df["mileage_bin"] = pd.cut(df["mileage"], bins=bins)
    trend = df.groupby("mileage_bin").size()
    results["trend"] = trend.to_dict()
    
    # MPK (miles per disengagement) equivalent
    if total > 0:
        results["km_per_disengagement"] = total_mileage / total
    
    return results


def generate_report(results, output_path):
    lines = ["# 脱离分析报告\n\n"]
    
    lines.append("## 总体统计\n")
    lines.append(f"- 总脱离次数: {results['total_disengagements']}\n")
    lines.append(f"- 测试总里程: {results['total_mileage_km']:.1f} km\n")
    lines.append(f"- 脱离率: {results['disengagement_rate']:.2f} 次/100km\n")
    if "km_per_disengagement" in results:
        lines.append(f"- 平均间隔: {results['km_per_disengagement']:.1f} km/次\n")
    lines.append("\n")
    
    lines.append("## 按脱离类型分布\n")
    for t, count in results["by_type"].items():
        pct = count / results["total_disengagements"] * 100
        lines.append(f"- {t}: {count} ({pct:.1f}%)\n")
    lines.append("\n")
    
    lines.append("## 按根因分布\n")
    for cause, count in results["by_cause"].items():
        pct = count / results["total_disengagements"] * 100
        lines.append(f"- {cause}: {count} ({pct:.1f}%)\n")
    lines.append("\n")
    
    lines.append("## 按场景分布\n")
    for scenario, count in results["by_scenario"].items():
        pct = count / results["total_disengagements"] * 100
        lines.append(f"- {scenario}: {count} ({pct:.1f}%)\n")
    lines.append("\n")
    
    # Recommendations
    lines.append("## 改进建议\n")
    top_cause = list(results["by_cause"].keys())[0] if results["by_cause"] else None
    if top_cause:
        lines.append(f"- 优先解决根因: **{top_cause}**（占比最高）\n")
    
    top_scenario = list(results["by_scenario"].keys())[0] if results["by_scenario"] else None
    if top_scenario:
        lines.append(f"- 重点加强场景: **{top_scenario}**\n")
    
    if results["disengagement_rate"] > 1.0:
        lines.append(f"- ⚠️ 脱离率 {results['disengagement_rate']:.2f} 次/100km 偏高，建议目标 < 0.5\n")
    
    report = "".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Disengagement CSV")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    df = pd.read_csv(args.csv)
    results = analyze_disengagements(df)
    generate_report(results, args.output)


if __name__ == "__main__":
    main()
