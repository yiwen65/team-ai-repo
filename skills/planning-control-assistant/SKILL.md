---
name: apollo-planning-control-assistant
description: >
  Apollo-Lite 规划控制（PNC）模块深度助手。基于 Cyber RT 中间件，覆盖 ReferenceLineProvider、
  EM Planner、Lattice Planner、OpenSpace Planner、Learning-Based Planner、MPC Controller、
  LQR Controller、差速驱动控制器。涉及场景管理器（ScenarioManager）、任务调度（TaskFactory）、
  Deciders（Path/Speed/ST Bounds）、Optimizers（PiecewiseJerk、DP/Quadratic Programming）、
  交通规则（TrafficRules）、参数调优（Tuning）、安全验证（RSS）。
  在以下场景触发使用：
  (1) Apollo planning/control 模块编译/启动/运行问题，(2) ReferenceLine 生成与平滑问题，
  (3) Scenario/Stage/Task 配置与调试，(4) PiecewiseJerkPath/Speed Optimizer 参数调优，
  (5) MPC Controller 参数调优与跟踪误差分析，(6) OpenSpace 泊车轨迹生成问题，
  (7) 规划控制联合性能瓶颈分析（延迟/内存）。
---

# Apollo Planning-Control Assistant

Apollo-Lite 规划控制深度助手。覆盖 Planning + Control 全链路分析与优化。

## 快速启动

用户提供以下信息即可触发分析：
- Apollo-lite 路径 + 模块（planning/control）
- 场景描述（城市道路/高速/泊车/路口）+ 地图信息
- Cyber RT DAG/日志 + 配置文件（.dag/.pb.txt）
- 问题描述（轨迹碰撞/控制超调/规划无解/性能差）

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| ReferenceLine | 地图参考线生成、平滑、拼接 | `references/reference-line.md` |
| Scenario | 场景管理器、Stage、Task 流水线 | `references/scenario-manager.md` |
| Path Optimizer | PiecewiseJerkPath、DP Path、Path Bounds | `references/path-optimizer.md` |
| Speed Optimizer | PiecewiseJerkSpeed、DP ST、Speed Bounds | `references/speed-optimizer.md` |
| MPC Control | 横向/纵向 MPC、OSQP、参数调优 | `references/mpc-control.md` |
| OpenSpace | Hybrid A*、ROI、泊车轨迹生成 | `references/open-space.md` |
| Learning-Based | 基于学习的规划器（深度学习模型） | `references/learning-based-planning.md` |
| Traffic Rules | 交通规则处理（红绿灯/停止线/让行） | `references/traffic-rules.md` |

## Apollo-lite Planning 模块结构

```
modules/planning/
├── reference_line/           # 参考线生成与平滑
│   ├── reference_line_provider.cc
│   ├── qp_spline_reference_line_smoother.cc
│   └── discrete_points_reference_line_smoother.cc
├── scenarios/                # 场景管理
│   ├── lane_follow/          # 车道保持
│   ├── intersection/         # 路口
│   ├── park/                 # 泊车
│   ├── emergency/            # 紧急
│   ├── cruise/               # 巡航
│   ├── maneuver/             # 机动场景
│   └── learning_model/       # 机器学习模型场景
├── tasks/                    # 任务（Deciders + Optimizers）
│   ├── deciders/             # 决策器
│   │   ├── path_bounds_decider.cc
│   │   ├── speed_bounds_decider.cc
│   │   ├── st_bounds_decider.cc
│   │   └── rss_decider.cc
│   └── optimizers/           # 优化器
│       ├── piecewise_jerk_path_optimizer.cc
│       ├── piecewise_jerk_speed_optimizer.cc
│       └── path_time_heuristic_optimizer.cc
├── lattice/                  # Lattice Planner
├── open_space/               # OpenSpace Planner
│   ├── parking/              # 泊车
│   └── trajectory_smoother/  # 轨迹平滑
├── learning_based/           # 基于学习的规划
├── navi/                     # 导航模式
├── traffic_rules/            # 交通规则处理
├── constraint_checker/     # 约束检查
└── tuning/                   # 参数调优
```

## Planning 流水线

```
ReferenceLineProvider (地图 → 参考线)
  → ScenarioManager (场景识别)
    → Stage (阶段)
      → Task 1: PathBoundsDecider (路径边界)
      → Task 2: PiecewiseJerkPathOptimizer (路径优化)
      → Task 3: SpeedBoundsDecider (速度边界)
      → Task 4: PiecewiseJerkSpeedOptimizer (速度优化)
    → Output: Trajectory
```

## Apollo-lite Control 模块结构

```
modules/control/
├── controller/               # 控制器实现
│   ├── mpc_controller.cc     # MPC 控制器
│   ├── lat_controller.cc     # 横向控制器 (LQR-like)
│   ├── diff_drive_lat_controller.cc  # 差速驱动横向控制器
│   ├── lon_controller.cc     # 纵向控制器
│   └── lon_speed_controller.cc  # 纵向速度控制器
├── common/                   # 公共工具
│   ├── interpolation_1d.cc
│   ├── interpolation_2d.cc
│   └── trajectory_analyzer.cc
└── conf/                     # 配置文件
    └── control_conf.pb.txt
```

## 问题诊断流程

1. **确认场景与地图** → 地图版本、ReferenceLine 质量
2. **Planning 层排查** → Scenario 识别、Stage 执行、Task 输出
3. **Trajectory 层排查** → 曲率、加速度、碰撞检测
4. **Control 层排查** → MPC 求解、跟踪误差、延迟
5. **联合分析** → Planning-Control 频率匹配、消息延迟

## 关键配置参数

### Planning 配置

```protobuf
// modules/planning/conf/planning_config.pb.txt
standard_planning_config {
  planner_type: EM
  
  // 参考线平滑
  reference_line_config {
    smoother_type: QP_SPLINE
    max_constraint_interval: 5.0
  }
  
  // 场景配置
  scenario_config {
    scenario_type: LANE_FOLLOW
    stage_type: LANE_FOLLOW_DEFAULT_STAGE
  }
}
```

### Control 配置

```protobuf
// modules/control/conf/control_conf.pb.txt
control_period: 0.01           # 100Hz
lat_controller_conf {
  ts: 0.01                     # 采样时间
  cf: 155494.663               # 前轴侧偏刚度
  cr: 155494.663               # 后轴侧偏刚度
  mass_fl: 520                 # 左前轮负荷
  mass_fr: 520                 # 右前轮负荷
  mass_rl: 520                 # 左后轮负荷
  mass_rr: 520                 # 右后轮负荷
  matrix_q: 0.05               # 横向误差权重
  matrix_q: 0.0                # 横向误差率权重
  matrix_q: 1.0                # 航向误差权重
  matrix_q: 0.0               # 航向误差率权重
  max_iteration: 150          # MPC 最大迭代次数
  max_lateral_acceleration: 5.0 # 最大横向加速度
}
```

## 输出规范

```markdown
# Apollo 规划控制问题分析报告

## 1. 场景与地图信息
## 2. Planning 输出分析
## 3. Trajectory 质量评估
## 4. Control 跟踪性能
## 5. 根因定位
## 6. 参数调优建议
## 7. 验证方法
```

## 关键原则

- **Apollo Planning 问题先看 ReferenceLine**：参考线不平滑（曲率突变）会导致规划无解
- **Scenario 识别错误会连锁反应**：ScenarioManager 误判场景 → 错误的 Stage → 错误的 Task 序列
- **MPC 求解失败先查约束**：PiecewiseJerk 优化器中约束冲突（路径边界 + 障碍物）会导致 OSQP 无解
- **Control 超调先看延迟**：从 Planning 输出到车辆执行的全链路延迟 > 200ms 时，MPC 预测 horizon 必须补偿
- **OpenSpace 无解先查 ROI**：泊车场景 ROI（感兴趣区域）生成错误会导致 Hybrid A* 搜索空间异常
- **差速驱动车辆使用 diff_drive_lat_controller**：非阿克曼转向车辆（如 diff-drive robots）需使用专用的差速驱动控制器
- **Learning-Based Planner 需检查模型加载**：`learning_based/` 依赖深度学习模型，模型路径错误或版本不匹配会导致规划失败
- **Traffic Rules 直接影响 Decider 输出**：交通规则配置错误（如停止线位置）会导致 SpeedBoundsDecider 产生异常约束
