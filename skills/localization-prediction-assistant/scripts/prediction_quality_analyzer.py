#!/usr/bin/env python3
"""分析预测输出质量。"""
import sys

def analyze_predictions(predictions, ground_truth=None):
    """
    predictions: list of dicts {id, timestamps, positions: [(x,y)]}
    ground_truth: optional, same format for comparison
    """
    print("\n🔮 预测质量分析")
    print("=" * 60)
    
    if not predictions:
        print("  ⚠️ 无预测数据")
        return
    
    print(f"  障碍物数量: {len(predictions)}")
    
    for pred in predictions:
        pid = pred.get("id", "unknown")
        positions = pred.get("positions", [])
        
        if len(positions) < 2:
            print(f"  ⚠️ 障碍物 {pid}: 轨迹点不足")
            continue
        
        # 计算轨迹曲率和加速度
        dx = positions[-1][0] - positions[0][0]
        dy = positions[-1][1] - positions[0][1]
        length = (dx**2 + dy**2)**0.5
        
        # 简单曲率估计（折线近似）
        curvature = 0
        for i in range(1, len(positions)-1):
            a = (positions[i][0] - positions[i-1][0], positions[i][1] - positions[i-1][1])
            b = (positions[i+1][0] - positions[i][0], positions[i+1][1] - positions[i][1])
            cross = abs(a[0]*b[1] - a[1]*b[0])
            if cross > 0:
                curvature += cross
        
        status = "✅"
        issues = []
        if length > 200:
            issues.append("轨迹过长")
        if curvature > 10:
            issues.append("曲率过大")
        
        if issues:
            status = "⚠️"
            issue_str = ", ".join(issues)
        else:
            issue_str = "正常"
        
        print(f"  {status} 障碍物 {pid}: 长度={length:.1f}m, 曲率={curvature:.2f} ({issue_str})")
    
    # 如果有真值，计算 ADE/FDE
    if ground_truth:
        print("\n  📊 与真值对比:")
        # 简化：只计算第一个障碍物的终点误差
        if predictions and ground_truth:
            pred_end = predictions[0]["positions"][-1]
            gt_end = ground_truth[0]["positions"][-1]
            fde = ((pred_end[0]-gt_end[0])**2 + (pred_end[1]-gt_end[1])**2)**0.5
            print(f"    终点位移误差 (FDE): {fde:.2f}m")

if __name__ == "__main__":
    preds = [
        {"id": "veh_1", "positions": [(0,0), (1,0), (2,0.1), (3,0)]},
        {"id": "ped_1", "positions": [(10,10), (10.2,10.1), (10.5,10.3)]},
    ]
    analyze_predictions(preds)
