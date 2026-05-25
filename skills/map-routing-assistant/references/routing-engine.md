# 路由引擎（Routing Engine）

一句话简介：Routing 模块基于 A* 算法和混合搜索策略，在高精地图拓扑图上计算从起点到终点的最优路径，输出 `RoutingResponse` 供 Planning 模块跟随。

## 核心概念/原理

Routing 算法：
- **A* 搜索**：以预估代价（距离+启发函数）引导搜索方向
- **混合搜索**：结合交通规则、道路等级、历史经验权重
- **Lane 级 Routing**：输出具体的车道序列，而非仅道路级路径
- **Rerouting**：当前路径不可行时（如封路）重新计算

搜索空间：
- 节点：车道（Lane）
- 边：车道连接关系（Successor/Left/Right/U-turn）
- 代价：距离 + 时间 + 转弯惩罚 + 车道变更惩罚

## Apollo-Lite 中的实现位置

- Routing 核心：`modules/routing/core/`
- 路由图：`modules/routing/graph/`
- 搜索策略：`modules/routing/strategy/`
- 拓扑生成：`modules/routing/topo_creator/`
- 主接口：`modules/routing/routing.cc/.h`
- Component：`modules/routing/routing_component.cc/.h`

## 关键配置参数

```protobuf
routing_conf {
  search_strategy: "A_STAR"
  base_speed: 10.0          # 基础速度用于时间估计 (m/s)
  left_turn_penalty: 5.0    # 左转弯惩罚 (s)
  right_turn_penalty: 2.0   # 右转弯惩罚 (s)
  uturn_penalty: 30.0       # 掉头惩罚 (s)
  change_lane_penalty: 3.0  # 变道惩罚 (s)
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 路由失败 | 起点/终点不在车道上 | 将请求点投影到最近车道 |
| 路径绕远 | 搜索权重设置不当 | 调整转弯/变道惩罚参数 |
| 路径不可通行 | 地图未更新（新封路） | 检查地图数据时效性 |
| 频繁 Rerouting | 定位漂移导致偏离路径 | 检查 localization 精度 |

## 与其他模块的接口

- **planning**：`RoutingResponse` 是 Planning 的主要输入之一
- **map/hdmap**：拓扑图基于 HDMap 构建
- **dreamview**：可视化显示 routing 路径
