---
name: apollo-map-routing-assistant
description: >
  Apollo-Lite 地图与路由模块深度助手。覆盖高精地图（HDMap）、PNC 地图（PncMap）、
  路由引擎（Routing）、相对地图（RelativeMap/WorldModel）全链路开发与调试。
  涉及地图解析（hdmap/）、PNC 专用地图接口（pnc_map/）、A* 寻路、混合搜索策略、
  路由拓扑创建（topo_creator）、地图数据管理、RelativeMap 生成。
  在以下场景触发使用：
  (1) 高精地图加载/解析失败问题，(2) PNC 地图接口异常（lane 找不到/s 值越界/路宽异常），
  (3) Routing 寻路失败或路径不合理，(4) 地图版本不匹配导致定位/规划异常，
  (5) 相对地图（RelativeMap）生成与更新问题，(6) 新道路/地图更新后的集成验证，
  (7) 地图数据格式转换（OpenDRIVE → Apollo 格式）。
---

# Apollo Map-Routing Assistant

Apollo-Lite 地图与路由深度助手。覆盖 HDMap/PNCMap/Routing/RelativeMap/WorldModel 全链路。

## 快速启动

用户提供以下信息即可触发分析：
- 模块（map/routing/world_model）+ 子系统（hdmap/pnc_map/core/graph/relative_map）
- Apollo-lite 路径 + 地图版本 + 模块日志
- 问题描述（地图加载失败/路由无解/lane 异常/relative map 不更新）
- 地图数据文件路径或示例

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| HDMap | 高精地图解析（lane/road/junction/signal） | `references/hdmap.md` |
| PncMap | PNC 专用地图接口（s-t 坐标、路宽、限速） | `references/pnc-map.md` |
| Routing | A* 寻路、混合搜索策略、路由结果 | `references/routing-engine.md` |
| TopoCreator | 路由拓扑图生成 | `references/topo-creator.md` |
| RelativeMap | 相对地图生成（感知/定位融合） | `references/relative-map.md` |
| WorldModel | 世界模型（relative_map + 感知融合） | `references/world-model.md` |

## Map 模块结构

```
modules/map/
├── hdmap/                     # 高精地图解析
│   ├── hdmap.cc/.h            # HDMap 主接口
│   ├── hdmap_common.h         # 公共数据结构
│   └── ...
├── pnc_map/                   # PNC 专用地图
│   ├── pnc_map.cc/.h          # PncMap 接口
│   ├── path.cc/.h             # 路径表示
│   └── route_segments.cc/.h  # 路由段
├── data/                      # 地图数据文件
│   └── ...                    # .bin / .xml 格式
├── tools/                     # 地图工具
└── testdata/                  # 测试数据
```

## Routing 模块结构

```
modules/routing/
├── core/                      # 路由核心算法
│   └── ...                    # A* / 混合搜索
├── graph/                     # 路由图
│   └── ...                    # 拓扑图表示
├── strategy/                  # 搜索策略
│   └── ...                    # 不同 routing 策略
├── topo_creator/             # 拓扑图生成
│   └── ...
├── routing.cc/.h             # Routing 主接口
├── routing_component.cc/.h   # Cyber RT Component
├── common/                    # 公共工具
├── conf/                      # 配置文件
├── dag/                       # DAG 配置
├── launch/                    # Launch 配置
├── proto/                     # Protobuf 定义
├── tools/                     # 工具
└── testdata/                  # 测试数据
```

## WorldModel 模块结构

```
modules/world_model/
└── relative_map/              # 相对地图
    └── ...                    # 基于感知和定位生成的局部地图
```

## 路由引擎流水线

```
TopoCreator（地图数据 → 拓扑图）
  → Routing Core（A* / 混合搜索）
    → Strategy（策略选择：最短/最快/最安全）
      → Output: RoutingResponse
```

## Cyber RT Channel 规范

| Channel | 类型 | 发布者 | 订阅者 |
|---------|------|--------|--------|
| `/apollo/routing_request` | `RoutingRequest` | planning/dreamview | routing |
| `/apollo/routing_response` | `RoutingResponse` | routing | planning |
| `/apollo/relative_map` | `MapMsg` | world_model | planning |

## 问题诊断流程

### Map
1. **确认地图文件存在** → `modules/map/data/` 下的 `.bin` 文件
2. **验证地图版本** → 地图版本与代码版本兼容性
3. **检查 HDMap 解析** → lane/road/junction 解析是否正常
4. **排查 PncMap 接口** → s-t 坐标转换、路宽查询、限速查询

### Routing
1. **确认起点/终点有效性** → 必须在车道上，不能在路口或人行道上
2. **检查拓扑图** → TopoCreator 生成的图是否完整
3. **分析搜索策略** → A* 是否陷入局部最优、策略权重设置
4. **验证路由结果** → 路径连续性、lane 变更次数、总长度

### RelativeMap
1. **确认定位输入** → LocalizationEstimate 质量
2. **检查感知输入** → 车道线检测结果
3. **验证地图生成** → RelativeMap 覆盖范围、精度

## 输出规范

```markdown
# Apollo 地图/路由问题分析报告

## 1. 地图版本与数据完整性
## 2. HDMap/PNCMap 解析状态
## 3. 路由请求与响应分析
## 4. 拓扑图状态
## 5. RelativeMap 生成状态
## 6. 根因定位
## 7. 修复方案
## 8. 验证方法
```

## 关键原则

- **地图版本必须与代码版本匹配**：地图格式变更后需同步更新解析代码
- **Routing 失败先看起点/终点**：不在车道上的点会导致 routing 直接失败
- **PncMap s-t 坐标必须单调**：s 值计算错误会导致规划异常
- **TopoCreator 是路由基础**：拓扑图生成失败（如地图数据损坏）会导致所有 routing 失败
- **RelativeMap 依赖定位质量**：定位漂移会导致 relative map 生成的车道位置错误
- **Lane 变更次数影响舒适性**：routing 结果中 lane 变更次数过多需要优化策略权重
- **地图数据格式为 Apollo 私有格式**：OpenDRIVE 需通过转换工具转为 Apollo 格式
