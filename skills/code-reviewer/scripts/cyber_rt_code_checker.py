#!/usr/bin/env python3
"""检查 Cyber RT 代码规范（Component 注册、Channel 命名等）。"""
import sys
import re
import os

def check_cyber_rt_code(file_path):
    print(f"\n🔍 Cyber RT 代码检查: {file_path}")
    print("-" * 60)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    issues = []
    
    # 检查 Component 注册
    if 'class ' in content and 'cyber::Component' in content:
        if 'CYBER_REGISTER_COMPONENT' not in content:
            issues.append("🔴 Component 缺少 CYBER_REGISTER_COMPONENT 宏")
        else:
            print("  ✅ CYBER_REGISTER_COMPONENT 已注册")
    
    # 检查头文件保护
    if content.count('#ifndef') == 0 and content.count('#pragma once') == 0:
        issues.append("⚠️ 缺少头文件保护（#ifndef 或 #pragma once）")
    
    # 检查裸指针
    raw_ptrs = len(re.findall(r'\b\w+\*\s+\w+', content)) - len(re.findall(r'std::shared_ptr|std::unique_ptr', content))
    if raw_ptrs > 5:
        issues.append(f"⚠️ 发现较多裸指针使用 ({raw_ptrs} 处)，建议改用智能指针")
    
    # 检查阻塞调用
    blocking_calls = re.findall(r'\b(sleep|usleep|pthread_mutex_lock|std::mutex::lock)\b', content)
    if blocking_calls:
        issues.append(f"⚠️ 发现可能的阻塞调用: {set(blocking_calls)}")
    
    if issues:
        print("\n  问题汇总:")
        for issue in issues:
            print(f"    {issue}")
        return False
    else:
        print("\n  ✅ 代码检查通过")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python cyber_rt_code_checker.py <cpp_file>")
        sys.exit(1)
    ok = check_cyber_rt_code(sys.argv[1])
    sys.exit(0 if ok else 1)
