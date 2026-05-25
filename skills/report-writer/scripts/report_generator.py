#!/usr/bin/env python3
"""自动生成 Apollo 模块状态日报/周报框架。"""
import sys
from datetime import datetime

def generate_daily_report(module_status):
    """
    module_status: dict of {module_name: {status, cpu, memory, latency, notes}}
    """
    date = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""# Apollo 模块状态日报 ({date})

## Cyber RT 系统状态
- DAG 加载: 检查中
- Component 运行: 检查中
- Channel 活跃: 检查中

## 各模块状态

| 模块 | 状态 | CPU | 内存 | 延迟 | 说明 |
|------|------|-----|------|------|------|
"""
    
    for name, info in module_status.items():
        status = info.get("status", "🟢")
        cpu = info.get("cpu", "N/A")
        mem = info.get("memory", "N/A")
        lat = info.get("latency", "N/A")
        notes = info.get("notes", "")
        report += f"| {name} | {status} | {cpu} | {mem} | {lat} | {notes} |\n"
    
    report += """
## 异常与处理
1. （待补充）

## 明日计划
- （待补充）
"""
    
    print(report)
    return report

if __name__ == "__main__":
    example = {
        "Perception": {"status": "🟢", "cpu": "45%", "memory": "2.1G", "latency": "120ms", "notes": "正常"},
        "Planning": {"status": "🟢", "cpu": "30%", "memory": "1.5G", "latency": "80ms", "notes": "正常"},
        "Localization": {"status": "🟡", "cpu": "60%", "memory": "1.2G", "latency": "50ms", "notes": "CPU 偏高"},
    }
    generate_daily_report(example)
