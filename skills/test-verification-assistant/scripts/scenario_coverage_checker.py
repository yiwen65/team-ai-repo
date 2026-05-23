#!/usr/bin/env python3
"""
scenario_coverage_checker.py
检查场景库覆盖度，识别盲区。

Usage:
  python scenario_coverage_checker.py --library scenarios.json --output coverage.md
"""

import json
import argparse
from collections import defaultdict


def load_scenarios(path):
    with open(path) as f:
        return json.load(f)


def check_coverage(scenarios):
    """Check scenario library coverage."""
    coverage = defaultdict(lambda: defaultdict(int))
    
    required_categories = {
        "basic_driving": ["straight", "curve", "lane_change", "overtake"],
        "intersection": ["straight", "left_turn", "right_turn", "unprotected_left"],
        "parking": ["perpendicular", "parallel", "diagonal"],
        "vru": ["pedestrian_crossing", "cyclist", "child", "wheelchair"],
        "weather": ["clear", "light_rain", "heavy_rain", "fog", "snow"],
        "lighting": ["day", "dusk", "night", "tunnel"],
        "special": ["construction", "accident", "police", "school_zone"]
    }
    
    # Count existing scenarios
    for s in scenarios:
        cat = s.get("category", "unknown")
        sub = s.get("subcategory", "unknown")
        coverage[cat][sub] += 1
    
    # Check gaps
    gaps = []
    for cat, subs in required_categories.items():
        for sub in subs:
            if coverage[cat][sub] == 0:
                gaps.append(f"{cat}/{sub}")
    
    return coverage, gaps, required_categories


def generate_report(coverage, gaps, required, output_path):
    lines = ["# 场景库覆盖度报告\n\n"]
    
    lines.append("## 覆盖统计\n")
    for cat, subs in required.items():
        covered = sum(1 for s in subs if coverage[cat][s] > 0)
        total = len(subs)
        pct = covered / total * 100
        lines.append(f"- {cat}: {covered}/{total} ({pct:.0f}%)\n")
    lines.append("\n")
    
    lines.append("## 详细分布\n")
    for cat, subs in required.items():
        lines.append(f"\n### {cat}\n")
        for sub in subs:
            count = coverage[cat][sub]
            status = "✅" if count > 0 else "❌"
            lines.append(f"- {status} {sub}: {count} 个场景\n")
    lines.append("\n")
    
    if gaps:
        lines.append("## ⚠️ 覆盖盲区\n")
        for gap in gaps:
            lines.append(f"- ❌ {gap}\n")
        lines.append(f"\n共 {len(gaps)} 个盲区，建议优先补充\n")
    else:
        lines.append("\n✅ 无覆盖盲区\n")
    
    report = "".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True, help="Scenario library JSON")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    scenarios = load_scenarios(args.library)
    coverage, gaps, required = check_coverage(scenarios)
    generate_report(coverage, gaps, required, args.output)


if __name__ == "__main__":
    main()
