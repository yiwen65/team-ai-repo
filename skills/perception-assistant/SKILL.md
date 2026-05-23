---
name: perception-assistant
description: >
  自动驾驶感知模块的深度技术助手。覆盖相机、激光雷达、毫米波雷达、超声波的多传感器融合感知全流程，
  包括传感器选型与配置、数据预处理、2D/3D/BEV 目标检测、时序融合、跟踪（MOT）、语义分割、Occupancy 预测、
  数据集构建与质量评估、模型部署优化（TensorRT/ONNX）、在线监控与故障诊断。
  在以下场景触发使用：
  (1) 多传感器标定验证与融合参数调优，(2) 感知模型选型（BEVDet/BEVFusion/PointPillars/CenterPoint/YOLO-Pose等）
  或性能瓶颈分析，(3) 时序对齐、数据关联、跟踪丢失问题排查，(4) 数据集标注质量检查与分布分析，
  (5) 模型量化/剪枝/TensorRT部署问题，(6) 传感器异常（鬼影、漏检、类别错分）根因定位。
---

# Perception Assistant

自动驾驶感知模块深度技术助手。提供从传感器配置到模型部署的全链路分析能力。

## 快速启动

用户提供以下信息之一即可触发分析：
- 传感器配置清单（型号、分辨率、FOV、安装位姿）
- 问题描述 + 日志/数据片段（rosbag、检测结果、可视化截图）
- 模型选型需求（算力约束、精度要求、延迟目标）
- 数据集样本或标注统计

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| 传感器与标定 | 多传感器时空标定验证、外参漂移检测 | `references/sensor-calibration.md` |
| 融合策略 | 前融合/后融合/中间融合（BEVFusion/TransFusion）选型与调优 | `references/fusion-strategies.md` |
| 检测算法 | 2D/3D/BEV/Occupancy 模型选型与性能分析 | `references/detection-algorithms.md` |
| 跟踪与时序 | MOT（ByteTrack/StrongSORT）、时序对齐、航迹关联 | `references/tracking.md` |
| 部署优化 | TensorRT/ONNX 量化、算子适配、延迟 profiling | `references/deployment.md` |
| 数据质量 | 数据集分布分析、标注质量检查、长尾问题诊断 | `references/data-quality.md` |

## 分析流程

1. **信息收集** → 确认传感器拓扑、问题现象、约束条件
2. **根因定位** → 按传感器层 → 数据层 → 算法层 → 部署层逐层排查
3. **方案输出** → 给出可执行的调参建议、配置修改、验证方法

## 工具脚本

| 脚本 | 用途 |
|---|---|
| `scripts/sensor_sync_checker.py` | 检查多传感器时间同步偏移，输出 topic 时差统计 |
| `scripts/fusion_coverage_analyzer.py` | 分析各传感器 FOV 覆盖盲区，生成可视化报告 |
| `scripts/detection_drift_detector.py` | 对比两版模型检测结果，定位精度漂移类别和场景 |

> 使用脚本前读取脚本头部的依赖说明和参数定义。

## 输出规范

所有分析报告的默认结构：

```markdown
# 感知问题分析报告

## 1. 现象与影响（一句话描述严重程度）
## 2. 传感器配置快照
## 3. 根因假设（Top-3，按概率排序）
## 4. 逐层排查证据
   - 传感器层：原始数据质量、标定精度
   - 数据层：预处理、时间同步、坐标转换
   - 算法层：模型输入、参数配置、后处理阈值
   - 部署层：量化损失、算子精度、推理框架版本
## 5. 验证实验设计
## 6. 修复方案与参数建议
## 7. 回归验证清单
```

## 关键原则

- **多传感器问题先查时间同步**：ROS2 的 `message_filters::Synchronizer` 或 ` ApproximateTime` policy 常是跟踪丢失的根因
- **BEV 模型精度问题先查标定**：相机-激光雷达外参漂移 0.5° 可导致 BEVFusion 近距目标偏移 > 1m
- **量化掉点优先查敏感算子**：SoftNMS、DeformConv、注意力模块在 INT8 下易崩，优先保留 FP16
- **鬼影/误检优先查数据分布**：训练集缺少的施工锥桶、异形车辆、低光照场景，直接补数据比调阈值更有效
