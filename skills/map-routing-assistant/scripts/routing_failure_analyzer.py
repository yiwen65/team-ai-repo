#!/usr/bin/env python3
"""分析路由失败原因。"""
import sys

def analyze_routing_failure(request, response=None, map_data=None):
    """
    request: dict with start {x,y} and end {x,y}
    response: optional routing response dict
    map_data: optional map info dict
    """
    print("\n🗺️  路由失败分析")
    print("=" * 60)
    
    sx, sy = request.get("start", {}).get("x", 0), request.get("start", {}).get("y", 0)
    ex, ey = request.get("end", {}).get("x", 0), request.get("end", {}).get("y", 0)
    
    print(f"  起点: ({sx:.2f}, {sy:.2f})")
    print(f"  终点: ({ex:.2f}, {ey:.2f})")
    
    issues = []
    
    # 检查起点/终点是否在地图范围内
    if map_data:
        bounds = map_data.get("bounds", {})
        min_x = bounds.get("min_x", -1e9)
        max_x = bounds.get("max_x", 1e9)
        min_y = bounds.get("min_y", -1e9)
        max_y = bounds.get("max_y", 1e9)
        
        if not (min_x <= sx <= max_x and min_y <= sy <= max_y):
            issues.append("🔴 起点超出地图范围")
        if not (min_x <= ex <= max_x and min_y <= ey <= max_y):
            issues.append("🔴 终点超出地图范围")
    
    # 检查距离
    dist = ((ex-sx)**2 + (ey-sy)**2)**0.5
    if dist < 1.0:
        issues.append("⚠️ 起点和终点距离 < 1m，可能为同一位置")
    if dist > 100000:
        issues.append("⚠️ 起点和终点距离 > 100km，可能坐标有误")
    
    # 检查响应
    if response is None:
        issues.append("🔴 无路由响应（请求未到达 Routing 模块或模块异常）")
    elif response.get("status") != "OK":
        issues.append(f"🔴 路由状态异常: {response.get('status')}")
    elif not response.get("road", []):
        issues.append("🔴 路由结果为空道路序列")
    
    if issues:
        print("\n  可能原因:")
        for issue in issues:
            print(f"    {issue}")
    else:
        print("\n  ✅ 请求参数无明显异常，可能为拓扑图或地图数据问题")
    
    print("\n  排查建议:")
    print("    1. 确认起点/终点投影到最近车道成功")
    print("    2. 检查 TopoCreator 生成的拓扑图完整性")
    print("    3. 检查 HDMap junction 连接关系")
    print("    4. 查看 routing 模块日志中的 A* 搜索状态")

if __name__ == "__main__":
    req = {"start": {"x": 100.0, "y": 200.0}, "end": {"x": 500.0, "y": 600.0}}
    analyze_routing_failure(req)
