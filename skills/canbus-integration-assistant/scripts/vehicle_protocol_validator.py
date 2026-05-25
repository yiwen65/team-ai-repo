#!/usr/bin/env python3
"""验证车辆协议配置（DBC 一致性检查）。"""
import sys
import re

def validate_dbc_consistency(dbc_path, protocol_dir):
    """
    检查 DBC 文件与 Apollo 协议代码的一致性。
    """
    print(f"\n🔧 车辆协议验证: {dbc_path}")
    print("=" * 60)
    
    # 读取 DBC 信号
    dbc_signals = {}
    try:
        with open(dbc_path, 'r') as f:
            for line in f:
                # 简单解析 BO_ 和 SG_ 行
                bo_match = re.search(r'BO_\s+(\d+)\s+([^:]+):', line)
                if bo_match:
                    can_id = bo_match.group(1)
                    msg_name = bo_match.group(2)
                    dbc_signals[msg_name] = {"can_id": can_id, "signals": []}
                sg_match = re.search(r'SG_\s+(\w+)', line)
                if sg_match:
                    sig_name = sg_match.group(1)
                    if dbc_signals:
                        list(dbc_signals.values())[-1]["signals"].append(sig_name)
    except FileNotFoundError:
        print(f"  ❌ DBC 文件不存在: {dbc_path}")
        return False
    
    print(f"  DBC 消息数量: {len(dbc_signals)}")
    for msg, info in dbc_signals.items():
        print(f"    {msg} (ID={info['can_id']}): {len(info['signals'])} 个信号")
    
    # 检查 Apollo 协议代码是否覆盖
    import os
    if os.path.isdir(protocol_dir):
        code_files = [f for f in os.listdir(protocol_dir) if f.endswith('.cc') or f.endswith('.h')]
        print(f"\n  Apollo 协议代码文件: {len(code_files)} 个")
        
        # 简单检查：代码中是否引用了 DBC 消息名
        uncovered = []
        for msg in dbc_signals:
            found = False
            for cf in code_files:
                with open(os.path.join(protocol_dir, cf), 'r') as f:
                    content = f.read()
                    if msg.lower() in content.lower() or msg.upper() in content.upper():
                        found = True
                        break
            if not found:
                uncovered.append(msg)
        
        if uncovered:
            print(f"\n  ⚠️ 以下 DBC 消息可能未在代码中实现:")
            for msg in uncovered[:10]:
                print(f"    - {msg}")
        else:
            print(f"\n  ✅ DBC 与代码覆盖基本一致")
    else:
        print(f"\n  ⚠️ 协议代码目录不存在: {protocol_dir}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python vehicle_protocol_validator.py <dbc_file> <protocol_dir>")
        sys.exit(1)
    validate_dbc_consistency(sys.argv[1], sys.argv[2])
