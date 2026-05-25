#!/usr/bin/env python3
"""传感器选型决策辅助工具。"""
import sys

def sensor_selection_advisor(scenario, budget_tier):
    """
    scenario: 'highway' | 'urban' | 'robotaxi' | 'lowcost'
    budget_tier: 'low' | 'medium' | 'high'
    """
    print(f"\n📡 传感器选型建议 ({scenario}, {budget_tier})")
    print("=" * 60)
    
    recommendations = {
        'highway': {
            'low': {'camera': 3, 'lidar': 1, 'radar': 3, 'compute': 'J3 (5T)', 'cost': '$500-1K'},
            'medium': {'camera': 5, 'lidar': 1, 'radar': 5, 'compute': 'Orin N (40T)', 'cost': '$3-5K'},
            'high': {'camera': 5, 'lidar': 2, 'radar': 5, 'compute': 'Orin X (254T)', 'cost': '$5-8K'},
        },
        'urban': {
            'low': {'camera': 5, 'lidar': 1, 'radar': 3, 'compute': 'Orin N (40T)', 'cost': '$3-5K'},
            'medium': {'camera': 7, 'lidar': 3, 'radar': 5, 'compute': 'Orin X (254T)', 'cost': '$6-10K'},
            'high': {'camera': 11, 'lidar': 5, 'radar': 5, 'compute': 'Orin X x2', 'cost': '$12-18K'},
        },
        'robotaxi': {
            'medium': {'camera': 11, 'lidar': 5, 'radar': 5, 'compute': 'Orin X x2', 'cost': '$12-18K'},
            'high': {'camera': 13, 'lidar': 6, 'radar': 6, 'compute': 'Orin X x2 + Thor', 'cost': '$18-25K'},
        },
    }
    
    if scenario not in recommendations:
        print(f"  ⚠️ 未知场景: {scenario}")
        return
    
    if budget_tier not in recommendations[scenario]:
        print(f"  ⚠️ 该场景下无 '{budget_tier}' 档位建议")
        return
    
    rec = recommendations[scenario][budget_tier]
    print(f"  推荐配置:")
    print(f"    Camera: {rec['camera']} 个")
    print(f"    LiDAR:  {rec['lidar']} 个")
    print(f"    Radar:  {rec['radar']} 个")
    print(f"    算力:   {rec['compute']}")
    print(f"    估算成本: {rec['cost']}")
    
    # Apollo-Lite 兼容性提示
    print(f"\n  Apollo-Lite 兼容性:")
    print(f"    - LiDAR: 支持 Hesai/Livox/Velodyne/Robosense/Vanjee/Seyond/lslidar")
    print(f"    - Radar: 支持 Continental/Racobit/NanoRadar/Ultrasonic")
    print(f"    - 算力: 需确认 CUDA 版本与 Apollo Docker 兼容")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python sensor_selection_tool.py <scenario> <budget_tier>")
        print("  scenario: highway | urban | robotaxi")
        print("  budget_tier: low | medium | high")
        sys.exit(1)
    sensor_selection_advisor(sys.argv[1], sys.argv[2])
