---
name: apollo-perception-assistant
description: >
  Apollo-Lite 自动驾驶感知模块深度助手。基于 Cyber RT 中间件，覆盖 camera/lidar/radar/multi-sensor-fusion
  全链路开发与调试。涉及 YOLOv4/DarkSCNN/DenseLine 等检测器、在线标定、BEV 检测（camera）、PointPillars、
  时序跟踪（OMT/OMT2 BEV Tracker）、数据融合、TensorRT 部署优化。在以下场景触发使用：
  (1) Apollo perception 模块编译/启动/运行问题排查，(2) Camera 检测器（YOLOv4/DarkSCNN）调优与精度分析，
  (3) LiDAR 点云处理（hesai/livox/velodyne/robosense/vanjee/inno 驱动）与融合，(4) 多传感器融合配置与同步问题，
  (5) Cyber RT DAG/Component 配置与 channel 通信问题，(6) 感知模型 TensorRT 部署与精度验证，
  (7) 数据闭环：采集、标注、训练、验证流程。
---

# Apollo Perception Assistant

Apollo-Lite 感知模块深度助手。基于 Cyber RT 中间件，覆盖 camera/lidar/radar/fusion/pipeline/onboard 全链路。

## 快速启动

用户提供以下信息即可触发分析：
- Apollo-lite 路径 + 模块名称（perception/camera/lidar/radar/fusion/pipeline/onboard）
- Cyber RT DAG 配置文件（.dag）或日志
- 传感器型号（hesai/livox/velodyne/robosense/vanjee/inno + 相机型号）
- 问题描述（启动失败/检测异常/融合错位/部署问题）+ 日志

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| Camera 感知 | YOLOv4 障碍物检测、DarkSCNN/DenseLine 车道线、红绿灯检测、BEV 检测 | `references/camera-perception.md` |
| LiDAR 感知 | PointPillars 点云检测、多线雷达驱动（6 家厂商） | `references/lidar-perception.md` |
| Radar 感知 | 毫米波雷达目标检测 | `references/radar-perception.md` |
| 多传感器融合 | Camera-LiDAR-Radar 数据关联、时空同步 | `references/multi-sensor-fusion.md` |
| Pipeline | 感知流水线配置（stage 编排） | `references/perception-pipeline.md` |
| Onboard | Cyber RT Component 封装、DAG 配置 | `references/perception-onboard.md` |
| 部署优化 | TensorRT/ONNX、Bazel 构建、模型管理 | `references/perception-deployment.md` |

## Apollo-lite 感知模块实际结构

```
modules/perception/
├── camera/                    # 相机感知
│   ├── app/                   # 应用入口（障碍物/车道线/红绿灯）
│   ├── common/                # 公共工具（数据 provider、坐标转换、undistortion）
│   ├── lib/                   # 算法库
│   │   ├── obstacle/
│   │   │   ├── detector/yolov4/          # YOLOv4 障碍物检测器
│   │   │   ├── detector/bev_detection/   # Camera BEV 障碍物检测
│   │   │   ├── transformer/              # 2D→3D 转换
│   │   │   ├── tracker/omt/              # OMT 多目标跟踪
│   │   │   ├── tracker/omt2/             # OMT2 BEV 跟踪器
│   │   │   ├── preprocessor/             # 预处理
│   │   │   └── postprocessor/            # 后处理
│   │   ├── lane/
│   │   │   ├── detector/darkSCNN/        # DarkSCNN 车道线检测
│   │   │   ├── detector/denseline/       # DenseLine 车道线检测
│   │   │   ├── postprocessor/darkSCNN/   # DarkSCNN 车道线后处理
│   │   │   ├── postprocessor/denseline/  # DenseLine 车道线后处理
│   │   │   └── common/                   # 车道线公共工具
│   │   ├── traffic_light/
│   │   │   ├── detector/detection/yolo_single_stage_dector/  # 红绿灯 YOLO 检测
│   │   │   └── tracker/                  # 红绿灯跟踪
│   │   ├── calibration_service/
│   │   │   └── online_calibration_service/  # 在线标定服务
│   │   ├── calibrator/
│   │   │   └── laneline/                 # 车道线辅助标定
│   │   ├── feature_extractor/            # 特征提取
│   │   ├── interface/                    # 接口定义
│   │   ├── motion/                       # 运动估计
│   │   ├── motion_service/               # 运动估计服务
│   │   └── dummy/                        # dummy 占位实现
│   └── tools/               # 离线工具与可视化
│
├── lidar/                     # 激光雷达感知
│   ├── app/                   # 点云检测应用
│   ├── common/                # 点云公共工具
│   ├── lib/                   # 点云算法库
│   │   └── detector/point_pillars_detection/  # PointPillars 检测器
│   └── tools/                 # 离线工具
│
├── radar/                     # 毫米波雷达感知
│   ├── app/                   # 雷达检测应用
│   ├── common/                # 雷达公共工具
│   └── lib/                   # 雷达算法库
│
├── fusion/                    # 多传感器融合
│   ├── app/                   # 融合应用入口
│   ├── base/                  # 融合基础框架
│   ├── common/                # 融合公共工具
│   └── lib/                   # 融合算法库
│
├── onboard/                   # Cyber RT Component 封装
│   └── component/
│       ├── camera_bev_detection_component.cc/.h
│       └── ...                # 其他感知 Component
│
├── pipeline/                  # 感知流水线配置
│   ├── config/                # 流水线配置文件（*.pb.txt）
│   └── proto/                 # 流水线 Protobuf 定义
│
├── production/                # 生产部署配置
│   ├── dag/                   # 生产环境 DAG 文件
│   └── conf/                  # 生产环境参数配置
│
├── base/                      # 感知基础数据结构
├── common/                    # 感知公共库
└── lib/                       # 感知底层框架
```

## ⚠️ 重要纠正

| Skill 旧描述 | 实际情况 |
|-------------|---------|
| **ByteTrack** | ❌ 不存在于代码库。跟踪器为 **OMT** / **OMT2**（OMT2 是 BEV Tracker） |
| **CenterPoint** | ❌ 不存在于代码库。LiDAR 检测器为 **PointPillars** |
| **BEVFusion** | ❌ 命名错误。Camera BEV 检测为 `bev_detection`（camera only），非 BEVFusion |
| **YOLO** | 实际为 **YOLOv4**（`modules/perception/camera/lib/obstacle/detector/yolov4/`） |

## 问题诊断流程

1. **确认 Cyber RT 环境** → `cyber_monitor` 查看 channel 状态
2. **检查 Pipeline 配置** → `modules/perception/pipeline/config/` 的 stage 编排
3. **检查 DAG 配置** → `modules/perception/production/dag/` 的 readers/writers channel 匹配
4. **排查传感器驱动** → drivers 模块日志、点云/图像数据正常
5. **分析感知算法** → 检测器输出、跟踪结果、融合关联
6. **验证部署产物** → Bazel 编译产物、so 库加载、TensorRT 引擎

## 工具脚本

| 脚本 | 用途 |
|---|---|
| `scripts/cyber_channel_checker.py` | 检查 Cyber RT channel 发布/订阅状态 |
| `scripts/dag_config_validator.py` | 验证 DAG 文件配置完整性 |
| `scripts/perception_latency_analyzer.py` | 分析感知链路各阶段延迟 |
| `scripts/sensor_sync_checker.py` | 检查多传感器时间戳同步状态 |
| `scripts/fusion_coverage_analyzer.py` | 分析多传感器融合覆盖范围 |

## Cyber RT Channel 规范

| Channel | 类型 | 发布者 | 订阅者 |
|---------|------|--------|--------|
| `/apollo/sensor/camera/front_6mm/image` | `Image` | drivers/camera | perception/camera |
| `/apollo/sensor/lidar128/compensator/PointCloud2` | `PointCloud` | drivers/lidar | perception/lidar |
| `/apollo/sensor/radar/front` | `ContiRadar` | drivers/radar | perception/radar |
| `/apollo/perception/obstacles` | `PerceptionObstacles` | perception/fusion | planning/prediction |
| `/apollo/perception/traffic_light` | `TrafficLightDetection` | perception/camera | planning |

## 输出规范

```markdown
# Apollo 感知问题分析报告

## 1. 现象与影响
## 2. Cyber RT 环境状态
## 3. Pipeline/DAG/Channel 配置检查
## 4. 传感器数据质量
## 5. 感知算法分析（检测/跟踪/融合）
## 6. 根因定位
## 7. 修复方案
## 8. 验证方法
```

## 关键原则

- **Pipeline 是感知入口**：`modules/perception/pipeline/config/` 定义了 stage 执行顺序，配置错误会导致整个链路失败
- **Production DAG 是生产部署关键**：`modules/perception/production/dag/` 与开发 DAG 可能不同，部署问题先看 production 配置
- **Cyber RT 问题先看 channel**: `cyber_channel echo /apollo/sensor/...` 确认数据流
- **DAG 配置 readers/writers 必须匹配**: channel 名称拼写错误是常见启动失败原因
- **相机检测先看 data_provider**: 图像格式、分辨率、畸变参数错误会导致检测器崩溃
- **LiDAR 融合时检查时间戳**: Cyber RT Header 中的 timestamp 用于时序对齐，偏移 > 100ms 导致融合错位
- **Bazel 编译产物路径**: 产物在 `bazel-bin/` 下，DAG 中 `module_library` 必须指向正确的 `.so` 路径
- **OMT2 是 BEV Tracker**：OMT2 在 BEV 空间进行跟踪，与 OMT（图像空间）不同
- **PointPillars 是唯一的 LiDAR 检测器**：代码库中无 CenterPoint 实现
