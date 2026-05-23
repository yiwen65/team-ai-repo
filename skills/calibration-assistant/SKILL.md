---
name: apollo-calibration-assistant
description: >
  Apollo-Lite 自动驾驶标定系统深度助手。基于 Cyber RT 中间件，覆盖相机内参/外参标定、
  LiDAR-Camera 联合标定、Radar 标定、IMU-GNSS 标定、在线标定、外参漂移检测。
  涉及标定工具链（camera_lidar_calibrator, online_calibrator）、标定数据验证、
  重投影误差分析、多传感器时空同步。在以下场景触发使用：
  (1) Apollo calibration 模块编译/运行问题，(2) 相机内参/外参标定与验证，
  (3) LiDAR-Camera 联合标定（Pandar/Livox/Velodyne + 相机），(4) 在线标定与漂移检测，
  (5) 标定参数版本管理与加载，(6) 多传感器时间同步验证。
---

# Apollo Calibration Assistant

Apollo-Lite 标定系统深度助手。覆盖 camera/lidar/radar/imu 全传感器标定与验证。

## 快速启动

用户提供以下信息即可触发分析：
- 标定类型（内参/外参/联合/在线）+ 传感器型号
- Apollo-lite 路径 + 标定模块日志
- 标定数据（图像/点云/轨迹）+ 标定结果文件
- 问题描述（重投影误差大/融合错位/外参漂移）

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| 相机标定 | 针孔/鱼眼模型、棋盘格/AprilGrid、内参+畸变 | `references/camera-calibration.md` |
| LiDAR 标定 | 多线雷达内参、LiDAR-Camera 联合外参 | `references/lidar-calibration.md` |
| 在线标定 | 场景特征提取、外参漂移检测、自动补偿 | `references/online-calibration.md` |
| 时间同步 | 多传感器时间戳对齐、gPTP/PTP、硬件同步 | `references/time-sync.md` |
| 标定验证 | 重投影误差、多距离验证、动态场景测试 | `references/calibration-validation.md` |

## Apollo-lite 标定模块结构

```
modules/calibration/
├── camera_lidar_calibrator/    # LiDAR-Camera 联合标定
├── online_calibrator/          # 在线标定
├── extrinsic_file_process/     # 外参文件处理
└── ...

modules/perception/camera/lib/calibrator/   # 相机标定相关
├── laneline/                   # 车道线辅助标定
└── online_calibration/         # 在线标定服务
```

## 标定问题诊断流程

1. **确认标定类型** → 内参/外参/联合/在线
2. **检查标定数据** → 图像质量、点云密度、姿态多样性
3. **验证标定结果** → 重投影误差、边缘对齐、融合效果
4. **排查时间同步** → 各传感器 timestamp 单调性、偏移量
5. **在线监控** → 场景特征稳定性、漂移趋势、触发阈值

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
## 2. 标定数据质量评估
## 3. 标定结果验证（多距离）
## 4. 时间同步状态
## 5. 根因定位
## 6. 重标定方案
## 7. 在线监控建议
```

## 关键原则

- **Apollo 标定板角点精度决定一切**：Apollo 使用高反射率标定板，角点在点云中需清晰可见
- **LiDAR-Camera 联合标定先查时间戳**：Cyber RT Header 中的 timestamp_sec 必须对齐，偏移 > 50ms 导致标定失败
- **在线标定依赖车道线/灯杆**：Apollo online_calibrator 利用车道线平行度和灯杆垂直度作为约束
- **外参文件格式**：Apollo 使用 YAML/Proto 格式，需确认加载路径和版本
- **温度漂移量化**：-20°C 到 +60°C 范围内，外参变化应 < 0.1°（旋转）和 < 2cm（平移）
