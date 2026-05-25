#!/usr/bin/env python3
"""检查底盘信号完整性。"""
import sys

def check_chassis_signals(chassis_data):
    """
    chassis_data: dict with keys like speed, steering, throttle, brake, gear, error_code
    """
    print("\n🚗 底盘信号完整性检查")
    print("=" * 60)
    
    required_fields = ["speed", "steering", "throttle", "brake", "gear", "error_code"]
    missing = [f for f in required_fields if f not in chassis_data]
    
    if missing:
        print(f"  🔴 缺失关键信号: {', '.join(missing)}")
        return False
    
    print(f"  ✅ 所有关键信号存在")
    
    # 范围检查
    checks = [
        ("speed", -1, 60, "m/s"),
        ("steering", -720, 720, "deg"),
        ("throttle", 0, 100, "%"),
        ("brake", 0, 100, "%"),
    ]
    
    issues = []
    for field, min_v, max_v, unit in checks:
        val = chassis_data[field]
        if val < min_v or val > max_v:
            issues.append(f"  ⚠️ {field}={val}{unit} 超出范围 [{min_v}, {max_v}]")
    
    # 故障码检查
    if chassis_data.get("error_code", 0) != 0:
        issues.append(f"  🔴 error_code={chassis_data['error_code']}，底盘存在故障")
    
    # 档位合理性
    gear = chassis_data.get("gear")
    speed = chassis_data.get("speed", 0)
    if gear == "P" and speed > 0.5:
        issues.append("  🔴 档位为 P 但车速 > 0.5m/s，逻辑异常")
    
    if issues:
        print("\n  问题汇总:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("\n  ✅ 底盘信号正常")
        return True

if __name__ == "__main__":
    example = {
        "speed": 12.5,
        "steering": 5.0,
        "throttle": 20.0,
        "brake": 0.0,
        "gear": "D",
        "error_code": 0,
    }
    check_chassis_signals(example)
