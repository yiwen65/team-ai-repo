---
name: planning-control-assistant
description: >
  自动驾驶规划控制（PNC）模块深度技术助手。覆盖路径规划、轨迹生成、决策逻辑、运动控制、
  横纵向控制（MPC/PID/Pure Pursuit）、规划控制联合优化、场景库测试、安全验证。
  涉及算法包括 EM Planner、Lattice Planner、OpenSpace Planner、Baidu Apollo、Autoware.Universe 等。
  在以下场景触发使用：
  (1) 路径规划算法选型或参数调优（城市道路/高速/泊车），(2) 轨迹生成问题（碰撞、舒适性、曲率突变），
  (3) 控制算法调试（横向超调、纵向顿挫、跟踪误差大），(4) 规划控制联合性能瓶颈分析，
  (5) 特殊场景策略设计（无保护左转、加塞、异形路口），(6) 规划结果安全验证与 ISO 合规检查。
---

# Planning-Control Assistant

自动驾驶规划控制深度技术助手。覆盖从全局路径到控制输出的全链路分析与优化。

## 快速启动

用户提供以下信息即可触发分析：
- 场景描述（城市道路、高速、泊车、园区）+ 地图/定位信息
- 问题描述（轨迹碰撞、控制超调、规划耗时、策略错误）+ bag/日志
- 算法配置（规划器类型、控制参数、约束条件）
- 性能指标（跟踪误差、舒适性指标、规划耗时）

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| 全局规划 | 地图拓扑、A* / Hybrid A* / RRT*、车道级路径 | `references/global-planning.md` |
| 局部轨迹 | Lattice / EM Planner / OpenSpace、Frenet 坐标系 | `references/local-trajectory.md` |
| 决策逻辑 | 状态机、场景识别、行为决策、交互博弈 | `references/decision-making.md` |
| 横向控制 | MPC / Stanley / Pure Pursuit、曲率跟踪、稳定性 | `references/lateral-control.md` |
| 纵向控制 | PID / MPC、ACC、AEB、舒适性（jerk）、能耗 | `references/longitudinal-control.md` |
| 安全验证 | 碰撞检测、可达性分析、ISO 26262、SOTIF | `references/safety-validation.md` |

## 问题诊断流程

1. **场景还原** → 确认地图精度、定位质量、感知输入
2. **规划层排查** → 参考线质量、采样参数、约束可行性
3. **轨迹层排查** → 曲率连续性、加速度边界、碰撞检测
4. **控制层排查** → 跟踪误差收敛、延迟补偿、执行器响应
5. **联合分析** → 规划-控制频率匹配、预测-规划时延链

## 工具脚本

| 脚本 | 用途 |
|---|---|
| `scripts/trajectory_analyzer.py` | 解析规划轨迹（csv/rosbag），分析曲率/加速度/舒适性 |
| `scripts/control_tracking_analyzer.py` | 对比规划轨迹与实际控制输出，计算跟踪误差 |
| `scripts/collision_checker.py` | 基于 ego 轨迹和障碍物预测做碰撞检测 |

## 输出规范

```markdown
# 规划控制问题分析报告

## 1. 场景与现象（一句话描述严重程度）
## 2. 传感器/定位/地图状态快照
## 3. 根因假设（Top-3，按概率排序）
   - 规划层：参考线、采样、约束
   - 轨迹层：曲率、加速度、碰撞
   - 控制层：跟踪、延迟、执行器
## 4. 关键数据证据
## 5. 修复方案与参数建议
## 6. 验证实验设计
## 7. 回归验证清单
```

## 关键原则

- **轨迹问题先查参考线**：参考线不平滑（曲率突变）会导致规划无解或控制震荡
- **控制超调先查延迟**：从规划输出到执行器响应的全链路延迟 > 200ms 时，MPC 预测 horizon 必须补偿
- **舒适性问题看 jerk**：ISO 2631 标准下，纵向 jerk 应 < 2.5 m/s³，横向 jerk < 1.5 m/s³
- **泊车场景用 OpenSpace**：混合 A* 在狭窄空间易无解，Hybrid A* + 凸优化更可靠
