# 世界模型（WorldModel）

一句话简介：WorldModel 是 Apollo-Lite 中对周围环境综合建模的模块，当前主要包含 RelativeMap 子系统，融合感知、定位和路由信息，为 Planning 提供统一的局部环境表示。

## 核心概念/原理

WorldModel 组成：
- **RelativeMap**：局部车道线地图
- **静态障碍物**：从感知获取的静止障碍物（如 parked cars）
- **动态障碍物**：`PredictionObstacles` 提供的未来轨迹
- **导航路径**：Routing 提供的全局路径约束

数据融合：
- 以车辆当前位置为原点建立局部坐标系
- 将各模块输出统一到同一坐标系和时间戳

## Apollo-Lite 中的实现位置

- WorldModel：`modules/world_model/`
- RelativeMap：`modules/world_model/relative_map/`

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 世界模型不完整 | 感知/定位/路由任一模块故障 | 逐一排查各输入模块 |
| 坐标系不一致 | 各模块使用不同坐标原点 | 确认所有数据都转换到 ego 坐标系 |
| 时间戳不同步 | 各模块发布频率不同 | 使用最近时间戳或插值对齐 |

## 与其他模块的接口

- **perception**：障碍物和车道线输入
- **localization**：车辆位姿
- **routing**：全局导航路径
- **planning**：WorldModel 是 Planning 决策的环境上下文
