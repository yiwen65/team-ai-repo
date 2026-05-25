#!/usr/bin/env python3
"""检查 Bazel BUILD 文件依赖完整性。"""
import sys
import re
import os

def check_bazel_build(build_path):
    print(f"\n📦 Bazel 依赖检查: {build_path}")
    print("-" * 60)
    
    with open(build_path, 'r') as f:
        content = f.read()
    
    issues = []
    
    # 检查 cc_library 是否有 deps
    lib_blocks = re.findall(r'cc_library\([^)]+\)', content, re.DOTALL)
    for block in lib_blocks:
        if 'deps' not in block:
            name_match = re.search(r'name\s*=\s*"([^"]+)"', block)
            name = name_match.group(1) if name_match else "unknown"
            issues.append(f"⚠️ cc_library '{name}' 缺少 deps 声明")
    
    # 检查是否有循环依赖提示（简化）
    if content.count('//modules/') > 20:
        issues.append("⚠️ 模块内依赖较多，建议检查是否存在循环依赖风险")
    
    # 检查 apollo_package() 和 cpplint()
    if 'apollo_package()' not in content:
        issues.append("⚠️ 缺少 apollo_package()")
    if 'cpplint()' not in content:
        issues.append("⚠️ 缺少 cpplint()")
    
    if issues:
        print("\n  问题汇总:")
        for issue in issues:
            print(f"    {issue}")
        return False
    else:
        print("\n  ✅ BUILD 文件基本完整")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python bazel_dep_checker.py <BUILD_file>")
        sys.exit(1)
    ok = check_bazel_build(sys.argv[1])
    sys.exit(0 if ok else 1)
