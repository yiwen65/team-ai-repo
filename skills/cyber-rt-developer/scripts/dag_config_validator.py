#!/usr/bin/env python3
"""验证 Cyber RT DAG 文件配置完整性。"""
import os
import re
import sys
from pathlib import Path

def validate_dag(dag_path):
    print(f"\n验证 DAG: {dag_path}")
    print("-" * 60)
    
    with open(dag_path, 'r') as f:
        content = f.read()
    
    issues = []
    
    # 检查 module_library
    lib_match = re.search(r'module_library:\s*"([^"]+)"', content)
    if not lib_match:
        issues.append("❌ 缺少 module_library")
    else:
        lib_path = lib_match.group(1)
        # 去掉 bazel-bin 前缀检查
        real_path = lib_path.replace("bazel-bin/", "")
        if not os.path.exists(real_path):
            issues.append(f"⚠️ module_library 路径不存在: {lib_path}")
        else:
            print(f"  ✅ module_library: {lib_path}")
    
    # 检查 class_name
    class_names = re.findall(r'class_name:\s*"([^"]+)"', content)
    if not class_names:
        issues.append("❌ 缺少 class_name")
    else:
        for cn in class_names:
            print(f"  ✅ class_name: {cn}")
    
    # 检查 readers channel
    readers = re.findall(r'readers\s*\{\s*channel:\s*"([^"]+)"', content)
    for r in readers:
        print(f"  📥 reader channel: {r}")
    
    # 检查 writers channel
    writers = re.findall(r'writers\s*\{\s*channel:\s*"([^"]+)"', content)
    for w in writers:
        print(f"  📤 writer channel: {w}")
    
    if issues:
        print("\n  问题汇总:")
        for issue in issues:
            print(f"    {issue}")
    else:
        print("\n  ✅ DAG 配置基本完整")
    
    return len(issues) == 0

def main():
    if len(sys.argv) < 2:
        print("用法: python dag_config_validator.py <dag_file_or_dir>")
        sys.exit(1)
    
    path = sys.argv[1]
    if os.path.isdir(path):
        dag_files = list(Path(path).glob("**/*.dag"))
        print(f"发现 {len(dag_files)} 个 DAG 文件")
        all_ok = all(validate_dag(str(f)) for f in dag_files)
    else:
        all_ok = validate_dag(path)
    
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
