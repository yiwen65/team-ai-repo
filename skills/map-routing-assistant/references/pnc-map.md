# PNC 地图接口

一句话简介：PncMap 是 Planning 和 Control 专用的地图抽象层，在 HDMap 基础上提供 s-t 坐标转换、路宽查询、限速查询、车道变更可行性分析等高级接口。

## 核心概念/原理

PncMap 核心功能：
- **s-t 坐标转换**：将全局 (x,y) 转换为车道局部 (s,l) 坐标
- **Reference Line**：车道的平滑中心线，是 Planning 的基础
- **LaneInfo**：包含车道宽度、类型、限速、相邻车道
- **RouteSegments**：Routing 结果的车道序列

关键算法：
- 点到车道最近匹配（投影到 Reference Line）
- 车道宽度插值（按 s 值查询）
- 车道变更可行性（检查相邻车道是否存在且无障碍）

## Apollo-Lite 中的实现位置

- PncMap 主接口：`modules/map/pnc_map/pnc_map.cc/.h`
- 路径表示：`modules/map/pnc_map/path.cc/.h`
- 路由段：`modules/map/pnc_map/route_segments.cc/.h`

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| s-t 坐标跳变 | Reference Line 曲率突变 | 检查地图平滑度 |
| 路宽查询为 0 | 地图数据缺失 | 核对地图 lane boundary 完整性 |
| 车道变更不可行 | 相邻车道不存在或被占用 | 检查 HDMap 定义和感知输出 |
| RouteSegment 为空 | Routing 失败或地图不匹配 | 检查 routing_response 和地图版本 |

## 与其他模块的接口

- **planning**：ReferenceLineProvider 使用 PncMap 生成参考线
- **routing**：提供 RouteSegments 作为 PncMap 的输入
- **map/hdmap**：底层数据来源
