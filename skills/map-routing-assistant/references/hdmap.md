# 高精地图解析（HDMap）

一句话简介：HDMap 是 Apollo-Lite 高精地图模块，解析 OpenDRIVE/Apollo 私有格式的地图数据，提供车道、路口、交通标志、路面标线等结构化几何信息，是 Planning、Localization 和 Perception 的基础输入。

## 核心概念/原理

HDMap 数据结构：
- **Road**：道路段，包含多个 LaneSection
- **LaneSection**：横截面，包含多条 Lane（左/中/右）
- **Lane**：车道线，用中心线 Reference Line + 边界表示
- **Junction**：路口，包含连接关系（Connection）
- **Signal/StopSign**：交通信号和停止线
- **Crosswalk**：人行横道
- **SpeedBump**：减速带

地图坐标系：
- 全局坐标：ENU（东北天）或 UTM
- 车道局部坐标：沿 Reference Line 的 s-t 坐标系

## Apollo-Lite 中的实现位置

- HDMap 主接口：`modules/map/hdmap/hdmap.cc/.h`
- 公共结构：`modules/map/hdmap/hdmap_common.h`
- 地图数据：`modules/map/data/`（.bin / .xml）
- 地图工具：`modules/map/tools/`

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 地图加载失败 | 文件路径错误/格式不兼容 | 检查 `map_path` 和文件存在性 |
| lane 找不到 | 坐标超出地图范围 | 确认车辆位置在地图覆盖范围内 |
| s-t 坐标异常 | Reference Line 不连续 | 检查地图接缝处的连接关系 |
| 路口拓扑错误 | junction 定义不完整 | 用 `modules/map/tools/` 可视化检查 |

## 与其他模块的接口

- **planning**：提供 ReferenceLine、SpeedLimit、边界约束
- **localization/msf**：提供点云配准参考地图
- **perception**：提供车道线先验用于相机检测校验
- **routing**：提供拓扑图节点和边权重
