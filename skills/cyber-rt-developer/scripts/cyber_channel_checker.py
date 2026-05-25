#!/usr/bin/env python3
"""检查 Cyber RT Channel 发布/订阅状态。"""
import subprocess
import sys
import re

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

def check_channels():
    print("=" * 60)
    print("Cyber RT Channel 状态检查")
    print("=" * 60)
    
    # 列出所有 channel
    output = run_cmd("cyber_channel list")
    channels = [line.strip() for line in output.split('\n') if line.strip().startswith('/')]
    
    print(f"\n发现 {len(channels)} 个 Channel:\n")
    for ch in channels[:50]:  # 最多显示50个
        info = run_cmd(f"cyber_channel info {ch}")
        writers = len(re.findall(r'writer:', info))
        readers = len(re.findall(r'reader:', info))
        freq_match = re.search(r'freq\s*=\s*([\d.]+)', info)
        freq = freq_match.group(1) if freq_match else "N/A"
        status = "🟢" if writers > 0 and readers > 0 else "🔴"
        print(f"  {status} {ch:60s} writers={writers} readers={readers} freq={freq}Hz")
    
    print("\n" + "=" * 60)
    print("检查完成。🔴 表示无发布者或无订阅者。")

if __name__ == "__main__":
    check_channels()
