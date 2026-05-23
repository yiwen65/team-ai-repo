#!/usr/bin/env python3
"""
docker_size_analyzer.py
分析 Docker 镜像层大小，定位膨胀原因。

Usage:
  python docker_size_analyzer.py --image autoware:latest --output report.md
"""

import subprocess
import json
import argparse


def get_image_history(image):
    """Get Docker image layer history."""
    result = subprocess.run(
        ["docker", "history", "--no-trunc", "--format", "{{.Size}}|{{.CreatedBy}}", image],
        capture_output=True, text=True
    )
    
    layers = []
    for line in result.stdout.strip().split("\n"):
        if "|" in line:
            size, cmd = line.split("|", 1)
            layers.append({"size": size.strip(), "command": cmd.strip()})
    
    return layers


def parse_size(size_str):
    """Parse Docker size string to bytes."""
    size_str = size_str.strip()
    if not size_str or size_str == "0B":
        return 0
    
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
    
    for unit, multiplier in sorted(units.items(), key=lambda x: -x[1]):
        if unit in size_str:
            num = size_str.replace(unit, "").strip()
            try:
                return float(num) * multiplier
            except ValueError:
                return 0
    
    return 0


def analyze_layers(layers):
    """Analyze layer sizes."""
    total = 0
    large_layers = []
    
    for layer in layers:
        size_bytes = parse_size(layer["size"])
        total += size_bytes
        
        if size_bytes > 50 * 1024**2:  # > 50MB
            large_layers.append({
                "size": layer["size"],
                "size_bytes": size_bytes,
                "command": layer["command"]
            })
    
    return total, large_layers


def generate_report(image, total, large_layers, output_path):
    lines = [f"# Docker 镜像大小分析报告: {image}\n\n"]
    lines.append(f"- 总大小: {total / 1024**3:.2f} GB\n")
    lines.append(f"- 层数: {len(large_layers)} 个大层 (>50MB)\n\n")
    
    if large_layers:
        lines.append("## 大层分析\n\n")
        lines.append("| 大小 | 命令 |\n")
        lines.append("|------|------|\n")
        
        for layer in sorted(large_layers, key=lambda x: -x["size_bytes"]):
            cmd = layer["command"][:80] + "..." if len(layer["command"]) > 80 else layer["command"]
            lines.append(f"| {layer['size']} | `{cmd}` |\n")
        
        lines.append("\n## 优化建议\n")
        
        # Check for common issues
        has_apt = any("apt-get" in l["command"] for l in large_layers)
        has_pip = any("pip" in l["command"] for l in large_layers)
        has_copy = any("COPY" in l["command"] for l in large_layers)
        
        if has_apt:
            lines.append("- `apt-get` 层较大，建议合并 RUN 并清理缓存: `rm -rf /var/lib/apt/lists/*`\n")
        if has_pip:
            lines.append("- `pip install` 层较大，建议使用多阶段构建，runtime 阶段不保留编译依赖\n")
        if has_copy:
            lines.append("- `COPY` 大文件，建议检查 `.dockerignore` 是否排除了不必要的文件\n")
        
        lines.append("- 考虑使用 `docker-squash` 或 BuildKit 的 `--squash` 减少层数\n")
    
    report = "".join(lines)
    print(report)
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(report)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Docker image name")
    parser.add_argument("--output", help="Output report path")
    args = parser.parse_args()
    
    layers = get_image_history(args.image)
    total, large_layers = analyze_layers(layers)
    generate_report(args.image, total, large_layers, args.output)


if __name__ == "__main__":
    main()
