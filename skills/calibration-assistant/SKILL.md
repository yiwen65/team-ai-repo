---
name: apollo-calibration-assistant
description: >
  Apollo-Lite 自动驾驶标定系统深度助手。基于 Cyber RT 中间件，覆盖相机内参/外参标定、
  LiDAR-Camera 联合标定、Radar 标定、IMU-GNSS 标定、在线标定、外参漂移检测。
  涉及标定服务（online_calibration_service）、车道线辅助标定（laneline calibrator）、
  LiDAR 在线标定（velodyne online_calibration）、标定数据验证、重投影误差分析。
  在以下场景触发使用：
  (1) 相机内参/外参标定与验证，(2) LiDAR-Camera 联合标定（Hesai/Livox/Velodyne + 相机），
  (3) 在线标定与漂移检测，(4) 标定参数版本管理与加载，(5) 多传感器时间同步验证。
  ⚠️ 注意：Apollo-Lite 的 `modules/calibration/` 目录目前仅含构建文件，标定功能实际分布在
  `perception/camera/` 和 `drivers/lidar/` 模块中。
---

# Apollo Calibration Assistant

Apollo-Lite 标定系统深度助手。覆盖 camera/lidar/radar/imu 全传感器标定与验证。

## ⚠️ 重要说明

Apollo-Lite 的标定功能**并非集中**在 `modules/calibration/` 目录下（该目录目前仅有 `BUILD` 和 `calibration.BUILD` 构建文件，无业务代码）。标定相关实现实际分布在以下模块：

- **`modules/perception/camera/lib/calibrator/`** — 车道线辅助标定
- **`modules/perception/camera/lib/calibration_service/online_calibration_service/`** — 在线标定服务
- **`modules/perception/camera/lib/calibration_service/`** — 标定数据服务
- **`modules/drivers/lidar/velodyne/parser/online_calibration.h`** — Velodyne LiDAR 在线标定

## 快速启动

用户提供以下信息即可触发分析：
- 标定类型（内参/外参/联合/在线）+ 传感器型号
- Apollo-lite 路径 + 相关模块日志（perception camera / drivers lidar）
- 标定数据（图像/点云/轨迹）+ 标定结果文件
- 问题描述（重投影误差大/融合错位/外参漂移）

## 核心能力域

| 域 | 说明 | 实际代码位置 |
|---|---|-------------|
| 相机标定 | 针孔/鱼眼模型、棋盘格/AprilGrid、内参+畸变 | `perception/camera/lib/calibrator/` |
| LiDAR 在线标定 | Velodyne 点云在线标定补偿 | `drivers/lidar/velodyne/parser/online_calibration.h` |
| 在线标定服务 | 场景特征提取、外参漂移检测、自动补偿 | `perception/camera/lib/calibration_service/online_calibration_service/` |
| 车道线辅助标定 | 利用车道线平行度约束进行外参校验 | `perception/camera/lib/calibrator/laneline/` |
| 时间同步 | 多传感器时间戳对齐、gPTP/PTP、硬件同步 | Cyber RT Header timestamp |
| 标定验证 | 重投影误差、多距离验证、动态场景测试 | 离线脚本 + `cyber_recorder` 回放 |

## Apollo-lite 标定相关代码结构

```
modules/
├── perception/
│   └── camera/
│       └── lib/
│           ├── calibration_service/
│           │   └── online_calibration_service/   # 在线标定服务核心
│           │       ├── online_calibration_service.h
│           │       └── online_calibration_service.cc
│           └── calibrator/
│               └── laneline/                    # 车道线辅助标定
│                   └── lane_calibrator.cc/.h
│
├── drivers/
│   └── lidar/
│       └── velodyne/
│           └── parser/
│               ├── online_calibration.h         # Velodyne 在线标定
│               └── online_calibration.cc
│
└── calibration/                                 # ⚠️ 仅有构建文件，无业务代码
    ├── BUILD
    └── calibration.BUILD
```

## 标定问题诊断流程

1. **确认标定类型** → 内参/外参/联合/在线
2. **定位实际模块** →
   - 相机在线标定 → `perception/camera/lib/calibration_service/`
   - 车道线辅助校验 → `perception/camera/lib/calibrator/laneline/`
   - Velodyne LiDAR 标定 → `drivers/lidar/velodyne/parser/online_calibration.*`
3. **检查标定数据** → 图像质量、点云密度、姿态多样性
4. **验证标定结果** → 重投影误差、边缘对齐、融合效果
5. **排查时间同步** → Cyber RT Header timestamp_sec 单调性、偏移量
6. **在线监控** → 场景特征稳定性、漂移趋势、触发阈值

## 关键标定参数

| 标定类型 | 精度要求 | 验证方法 | 漂移检测周期 |
|---------|---------|---------|-------------|
| 相机内参 | 重投影误差 < 0.3px | 棋盘格角点 | 每季度 |
| 相机-相机 | 重叠区误差 < 2px | 场景特征匹配 | 每月 |
| 相机-LiDAR | 重投影 < 5px @ 10m | 标定板/自然特征 | 每周 |
| LiDAR-IMU | 时间偏移 < 5ms | 运动场景验证 | 每次启动 |
| Radar-相机 | 角度误差 < 0.5° | 目标关联验证 | 每月 |

## 输出规范

```markdown
# Apollo 标定问题分析报告

## 1. 标定类型与传感器配置
## 2. 标定代码实际位置定位
## 3. 标定数据质量评估
## 4. 标定结果验证（多距离）
## 5. 时间同步状态
## 6. 根因定位
## 7. 重标定方案
## 8. 在线监控建议
```

## 关键原则

- **Apollo-Lite 标定代码分散在感知和驱动模块**：不要到 `modules/calibration/` 找业务代码
- **在线标定服务在 camera perception 内**：`online_calibration_service` 是相机外参漂移检测的核心
- **车道线辅助标定利用平行度约束**：`laneline` calibrator 通过车道线平行度和灯杆垂直度校验外参
- **LiDAR-Camera 联合标定先查时间戳**：Cyber RT Header 中的 timestamp_sec 必须对齐，偏移 > 50ms 导致标定失败
- **外参文件格式**：Apollo 使用 YAML/Proto 格式，需确认加载路径和版本
- **温度漂移量化**：-20°C 到 +60°C 范围内，外参变化应 < 0.1°（旋转）和 < 2cm（平移）
