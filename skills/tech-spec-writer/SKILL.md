---
name: apollo-tech-spec-writer
description: >
  Apollo-Lite 自动驾驶项目技术方案深度编写助手。覆盖 Apollo-lite 架构设计、Cyber RT 中间件选型、
  Bazel 构建系统、模块划分（perception/planning/control/prediction/localization/routing/canbus/guardian/monitor/dreamview）、
  传感器选型（hesai/livox/velodyne/continental）、算力平台（Orin/Thor/地平线）、
  数据闭环（cyber_recorder/标注/训练/OTA）。在以下场景触发使用：
  (1) Apollo-lite 新项目/新车型架构设计，(2) Cyber RT 中间件与模块划分方案，
  (3) 传感器与算力平台选型决策，(4) Bazel 构建系统与 CI/CD 设计，
  (5) 数据闭环流程设计（采集/标注/训练/部署），(6) Apollo 模块集成方案与接口设计。
---

# Apollo Tech Spec Writer

Apollo-Lite 项目技术方案深度编写助手。覆盖架构、模块、传感器、算力、数据闭环全链路。

## 快速启动

用户提供以下信息即可生成方案：
- 项目背景（车型、场景、法规）+ 约束条件（预算/时间/团队）
- 技术需求（功能定义、性能指标、安全等级）
- 对标信息（Apollo-lite 版本、竞品方案）
- 候选方案（已有初步想法，需要对比分析）

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| Apollo 架构 | Cyber RT 中间件、模块划分、DAG 拓扑 | `references/apollo-architecture.md` |
| 传感器选型 | Hesai/Livox/Velodyne/Continental 规格对比 | `references/sensor-selection.md` |
| 算力平台 | Orin/Thor/地平线/J5、GPU/CPU 需求估算 | `references/compute-platform.md` |
| Bazel 构建 | 构建系统、CI/CD、缓存策略 | `references/bazel-cicd.md` |
| 数据闭环 | cyber_recorder、标注、训练、OTA | `references/data-loop.md` |
| 模块集成 | 接口设计、DAG 配置、消息格式 | `references/module-integration.md` |

## Apollo-lite 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Apollo-Lite                           │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Camera  │  │  LiDAR   │  │  Radar   │  │  GNSS/   │   │
│  │  Driver  │  │  Driver  │  │  Driver  │  │  IMU     │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │          │
│       └─────────────┴─────────────┴─────────────┘          │
│                         │                                   │
│              ┌──────────┴──────────┐                        │
│              │   Cyber RT (DAG)   │                        │
│              │  ┌──────────────┐  │                        │
│              │  │  Perception  │  │                        │
│              │  │  (Camera/     │  │                        │
│              │  │  LiDAR/Radar) │  │                        │
│              │  └───────┬──────┘  │                        │
│              │          │          │                        │
│              │  ┌───────┴──────┐  │                        │
│              │  │  Prediction  │  │                        │
│              │  └───────┬──────┘  │                        │
│              │          │          │                        │
│              │  ┌───────┴──────┐  │                        │
│              │  │   Planning   │  │                        │
│              │  │  (EM/OpenSpace)│  │                        │
│              │  └───────┬──────┘  │                        │
│              │          │          │                        │
│              │  ┌───────┴──────┐  │                        │
│              │  │   Control    │  │                        │
│              │  │  (MPC/LQR)   │  │                        │
│              │  └───────┬──────┘  │                        │
│              └──────────┼──────────┘                        │
│                         │                                   │
│              ┌──────────┴──────────┐                        │
│              │       Canbus        │                        │
│              │   (Vehicle Control) │                        │
│              └─────────────────────┘                        │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │Localization│  │  Routing │  │ Dreamview│                  │
│  │  (RTK/SLAM)│  │  (A*)    │  │  (HMI)   │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                                              │
│  ┌──────────┐  ┌──────────┐                                │
│  │ Guardian │  │  Monitor │                                │
│  │ (Safety) │  │ (Health) │                                │
│  └──────────┘  └──────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

## 模块接口设计

| 模块 | 输入 Channel | 输出 Channel | 说明 |
|------|-------------|-------------|------|
| Perception | `/apollo/sensor/*` | `/apollo/perception/obstacles` | 障碍物/车道线/红绿灯 |
| Prediction | `/apollo/perception/obstacles` | `/apollo/prediction` | 轨迹预测 |
| Planning | `/apollo/prediction`, `/apollo/localization/pose` | `/apollo/planning/trajectory` | 规划轨迹 |
| Control | `/apollo/planning/trajectory` | `/apollo/control/chassis` | 控制命令 |
| Localization | `/apollo/sensor/gnss/*`, `/apollo/sensor/lidar/*` | `/apollo/localization/pose` | 位姿 |
| Guardian | `/apollo/monitor` | `/apollo/guardian` | 安全监控 |
| Monitor | 系统资源 | `/apollo/monitor` | 健康监控 |

## 传感器选型决策

| 场景 | Camera | LiDAR | Radar | 算力 | 成本 |
|------|--------|-------|-------|------|------|
| 高速 NOA | 5 | 1-2 | 5 | Orin N (40T) | $3K |
| 城市 NOA | 7-11 | 3-5 | 5+ | Orin X (254T) | $8K+ |
| Robotaxi | 11+ | 5+ | 5+ | Orin X × 2 | $15K+ |
| 低成本 ADAS | 1-3 | 0 | 1-3 | J3 (5T) | $500 |

## 输出规范

```markdown
# Apollo 技术方案

## 1. 项目背景与目标
## 2. 系统架构设计
## 3. 模块划分与接口
## 4. 传感器与算力选型
## 5. 构建系统与 CI/CD
## 6. 数据闭环设计
## 7. 实施计划
## 8. 风险评估与缓解
```

## 关键原则

- **Apollo 架构必须先定模块边界**：Cyber RT DAG 的 channel 接口一旦确定，变更成本极高
- **传感器选型必须匹配场景**：高速场景重视 Radar 远距离，城市场景重视 LiDAR 360° 覆盖
- **算力预留 30% 余量**：模型迭代、功能扩展、紧急修复需要 buffer
- **Bazel 缓存策略决定 CI 效率**：远程缓存（remote cache）可将构建时间从 2h 降至 10min
- **数据闭环必须覆盖全链路**：cyber_recorder → 标注 → 训练 → 验证 → OTA，缺一不可
