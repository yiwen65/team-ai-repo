---
name: apollo-localization-prediction-assistant
description: >
  Apollo-Lite 定位与预测模块深度助手。覆盖 Localization（RTK/MSF/NDT）和 Prediction（Evaluator/
  Predictor/Network/Scenario）全链路开发与调试。涉及 RTK 差分定位、MSF 多传感器融合（LiDAR+IMU+GNSS）、
  NDT 点云配准、预测容器（Container）、意图评估（Evaluator）、轨迹预测（Predictor）、
  深度学习预测网络（Network）、场景分类（Scenario）、子模块调度（Submodules）。
  在以下场景触发使用：
  (1) 定位漂移/跳变/失锁问题排查，(2) MSF/NDT 配准失败或收敛问题，
  (3) Prediction 输出异常（轨迹不合理/预测延迟/场景误判），(4) Evaluator 意图评估精度问题，
  (5) Predictor 自由运动/车道序列/交互式预测问题，(6) 预测网络模型加载与推理问题，
  (7) Localization-Prediction-Planning 联合时序对齐问题。
---

# Apollo Localization-Prediction Assistant

Apollo-Lite 定位与预测模块深度助手。覆盖 Localization（RTK/MSF/NDT）+ Prediction（Evaluator/Predictor/Network）全链路。

## 快速启动

用户提供以下信息即可触发分析：
- 模块（localization/prediction）+ 子系统（rtk/msf/ndt/evaluator/predictor/network）
- Apollo-lite 路径 + 模块日志
- 地图版本 + 传感器配置（GNSS/IMU/LiDAR）
- 问题描述（定位漂移/预测轨迹异常/场景误判）+ 日志

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| RTK 定位 | 实时差分 GNSS、坐标系转换 | `references/rtk-localization.md` |
| MSF 融合 | 多传感器融合（LiDAR + IMU + GNSS） | `references/msf-localization.md` |
| NDT 配准 | 正态分布变换点云配准 | `references/ndt-localization.md` |
| 预测容器 | Container 管理障碍物历史轨迹 | `references/prediction-container.md` |
| Evaluator | 意图评估（lane_sequence/free_move/junction） | `references/prediction-evaluator.md` |
| Predictor | 轨迹预测生成器 | `references/prediction-predictor.md` |
| Network | 深度学习预测模型 | `references/prediction-network.md` |
| Scenario | 预测场景分类（on_lane/junction/parking） | `references/prediction-scenario.md` |

## Localization 模块结构

```
modules/localization/
├── rtk/                       # RTK 差分定位
│   └── rtk_localization.cc/.h
├── msf/                       # 多传感器融合（MSF）
│   ├── common/                # 公共工具
│   ├── local_integ/           # 本地集成
│   ├── local_map/             # 本地地图
│   └── ...
├── ndt/                       # NDT 点云配准
│   └── ndt_localization.cc/.h
├── common/                    # 公共工具
├── conf/                      # 配置文件
├── dag/                       # DAG 配置
├── launch/                    # Launch 配置
├── proto/                     # Protobuf 定义
└── testdata/                  # 测试数据
```

## Prediction 模块结构

```
modules/prediction/
├── prediction_component.cc/.h     # 预测 Component 入口
├── container/                 # 障碍物容器
│   └── ...                    # 管理障碍物历史轨迹和特征
├── evaluator/                 # 意图评估器
│   └── ...                    # lane_sequence / free_move / junction 评估
├── predictor/                 # 轨迹预测器
│   └── ...                    # 生成预测轨迹
├── network/                   # 深度学习网络
│   └── ...                    # 预测模型推理
├── scenario/                  # 场景分类
│   └── ...                    # on_lane / junction / parking
├── submodules/                # 子模块
│   └── ...                    # 异步子任务调度
├── pipeline/                  # 流水线配置
├── common/                    # 公共工具
├── conf/                      # 配置文件
├── dag/                       # DAG 配置
├── launch/                    # Launch 配置
├── proto/                     # Protobuf 定义
├── testdata/                  # 测试数据
└── tools/                     # 离线工具
```

## 预测流水线

```
Container（障碍物历史轨迹）
  → Scenario（场景识别: on_lane / junction / parking）
    → Evaluator（意图评估: lane_sequence / free_move / junction）
      → Predictor（轨迹预测生成）
    → Output: PredictionObstacles
```

## Cyber RT Channel 规范

| Channel | 类型 | 发布者 | 订阅者 |
|---------|------|--------|--------|
| `/apollo/localization/pose` | `LocalizationEstimate` | localization | planning/prediction/control |
| `/apollo/localization/msf_status` | `LocalizationStatus` | localization/msf | monitor |
| `/apollo/prediction` | `PredictionObstacles` | prediction | planning |
| `/apollo/perception/obstacles` | `PerceptionObstacles` | perception | prediction |

## 问题诊断流程

### Localization
1. **确认 GNSS 信号** → RTK 固定解/浮点解状态、卫星数量
2. **检查 IMU 数据** → 角速度/加速度合理性、温度漂移
3. **验证 LiDAR 点云** → MSF/NDT 依赖点云质量，点云稀疏会导致配准失败
4. **排查地图匹配** → MSF/NDT 依赖高精地图，地图版本不匹配会导致定位偏移
5. **分析坐标系转换** → ENU/UTM/车辆坐标系转换参数

### Prediction
1. **确认输入数据** → PerceptionObstacles 完整性、时间戳对齐
2. **检查 Container** → 障碍物历史轨迹是否足够（通常需 10 帧以上）
3. **分析 Scenario** → 场景分类错误会导致错误的 Evaluator 选择
4. **验证 Evaluator** → 意图评估置信度、lane_sequence 合理性
5. **排查 Predictor** → 轨迹曲率/加速度是否满足车辆动力学约束
6. **检查 Network** → 深度学习模型加载、推理延迟、输入特征归一化

## 输出规范

```markdown
# Apollo 定位/预测问题分析报告

## 1. 模块状态与配置
## 2. 输入数据质量
## 3. Localization 层分析（RTK/MSF/NDT）
## 4. Prediction 层分析（Scenario/Evaluator/Predictor/Network）
## 5. 时序对齐验证
## 6. 根因定位
## 7. 修复方案
## 8. 验证方法
```

## 关键原则

- **Localization 漂移先看地图版本**：MSF/NDT 依赖高精地图，地图更新后必须重新验证
- **RTK 失锁时 MSF 退化**：GNSS 信号遮挡时 MSF 会退化为纯 IMU 推算，漂移会快速累积
- **NDT 配准失败先查点云密度**：点云稀疏场景（开阔地带）NDT 容易配准失败
- **Prediction 问题先看 Container**：障碍物历史轨迹不足会导致 Evaluator 输出不稳定
- **Scenario 误判是连锁故障**：Scenario 分类错误 → Evaluator 错误 → Predictor 输出异常轨迹
- **预测网络输入特征必须归一化**：Network 的输入特征（速度/位置/朝向）未归一化会导致推理异常
- **Prediction 延迟必须 < Planning 周期**：预测输出延迟 > Planning 周期会导致规划使用过期预测结果
- **Localization-Prediction-Planning 必须时序对齐**：三个模块的时间戳偏移 > 50ms 会导致系统性偏差
