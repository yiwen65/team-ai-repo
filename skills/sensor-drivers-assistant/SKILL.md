---
name: apollo-sensor-drivers-assistant
description: >
  Apollo-Lite 传感器驱动深度助手。覆盖 LiDAR（Hesai/Livox/Velodyne/Robosense/Vanjee/Seyond/Inno/lslidar
  等 8 家厂商）、Radar（Conti/Racobit/nano/ultrasonic/yg/udas）、Camera、GNSS、IMU、Video、Microphone
  全链路驱动开发与调试。涉及驱动框架（lidar_driver_component）、点云补偿（compensator）、
  多传感器融合驱动（fusion）、硬件抽象层（HAL）、协议解析、数据质量验证。
  在以下场景触发使用：
  (1) 传感器驱动编译/启动/运行问题，(2) LiDAR 点云数据异常（丢点/畸变/时间戳跳变），
  (3) Radar 目标数据异常（假阳性/漏检/ID 跳变），(4) Camera 图像数据异常（花屏/帧率不稳/同步问题），
  (5) GNSS/IMU 定位数据异常（RTK 失锁/漂移/时间戳不齐），(6) 多传感器硬件同步配置（gPTP/PTP/trigger），
  (7) 新传感器型号适配与集成。
---

# Apollo Sensor Drivers Assistant

Apollo-Lite 传感器驱动深度助手。覆盖 LiDAR/Radar/Camera/GNSS/IMU/Video/Microphone 全链路。

## 快速启动

用户提供以下信息即可触发分析：
- 传感器类型（lidar/radar/camera/gnss/imu/video/microphone）+ 厂商型号
- Apollo-lite 路径 + 驱动模块日志（`modules/drivers/`）
- 硬件配置（接口类型/CAN/以太网/串口/触发方式）
- 问题描述（无数据/数据异常/时间戳不对/帧率不稳）+ 日志

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| LiDAR 驱动 | 8 家厂商点云驱动、parser、compensator | `references/lidar-drivers.md` |
| Radar 驱动 | 毫米波/超声波雷达驱动、目标解析 | `references/radar-drivers.md` |
| Camera 驱动 | 图像采集、ISP、帧同步 | `references/camera-drivers.md` |
| GNSS/IMU 驱动 | RTK、INS、组合导航驱动 | `references/gnss-imu-drivers.md` |
| HAL 层 | 硬件抽象层、设备管理 | `references/hal-layer.md` |
| 时间同步 | gPTP/PTP、硬件 trigger、软同步 | `references/sensor-time-sync.md` |
| 数据质量 | 点云/图像/目标数据质量验证 | `references/sensor-data-quality.md` |

## Apollo-lite 驱动模块结构

```
modules/drivers/
├── lidar/                     # 激光雷达驱动（15K+ 行，最大驱动子系统）
│   ├── lidar_driver_component.cc/.h    # 通用 LiDAR Component
│   ├── common/                # 公共工具
│   ├── compensator/           # 点云运动补偿
│   ├── fusion/                # 多 LiDAR 融合
│   ├── hesai/                 # Hesai 禾赛
│   ├── livox/                 # Livox 览沃
│   ├── lslidar/               # Leishen 镭神
│   ├── rslidar/               # Robosense 速腾
│   ├── seyond/                # Seyond
│   ├── vanjeelidar/           # Vanjee 万集
│   ├── velodyne/              # Velodyne
│   │   └── parser/
│   │       ├── online_calibration.h    # Velodyne 在线标定
│   │       └── online_calibration.cc
│   ├── proto/                 # LiDAR Protobuf
│   └── conf/                  # 配置文件
│
├── radar/                     # 雷达驱动
│   ├── conti_radar/           # Continental 大陆雷达
│   ├── nano_radar/            # NanoRadar 纳雷
│   ├── racobit_radar/         # Racobit
│   ├── ultrasonic_radar/      # 超声波雷达
│   ├── udas_ultrasonic_radar/ # UDAS 超声波
│   └── yg_radar/              # YG
│
├── camera/                    # 相机驱动
│   └── ...                    # 图像采集、ISP
│
├── gnss/                      # GNSS/INS 驱动
│   └── ...                    # RTK、组合导航
│
├── hal/                       # 硬件抽象层（4.5K 行）
│   └── ...
│
├── video/                     # 视频驱动
├── microphone/                # 麦克风驱动
└── canbus/                    # CAN 总线驱动（3.4K 行）
    └── ...
```

## LiDAR 厂商兼容性矩阵

| 厂商 | 代码目录 | 典型型号 | 接口 | 状态 |
|------|---------|---------|------|------|
| Hesai | `drivers/lidar/hesai/` | Pandar128/QT/PXT | 以太网 | ✅ 主力 |
| Livox | `drivers/lidar/livox/` | Mid-360/HAP/Tele | 以太网 | ✅ 主力 |
| Velodyne | `drivers/lidar/velodyne/` | VLP-16/VLP-32 | 以太网 | ✅ 兼容 |
| Robosense | `drivers/lidar/rslidar/` | M1/Helios/E1 | 以太网 | ✅ 兼容 |
| Vanjee | `drivers/lidar/vanjeelidar/` | WLR-720/760 | 以太网 | ✅ 兼容 |
| Seyond | `drivers/lidar/seyond/` | Seyond SDK | 以太网 | ✅ 兼容 |
| lslidar | `drivers/lidar/lslidar/` | 镭神系列 | 以太网 | ✅ 兼容 |
| Inno | `drivers/lidar/inno/` | Inno SDK | 以太网 | ⚠️ 检查版本 |

## 问题诊断流程

1. **确认硬件连接** → 以太网/CAN/串口连通性、IP 配置、波特率
2. **检查驱动启动** → `cyber_launch start drivers/.../launch/*.launch`
3. **验证数据输出** → `cyber_channel echo /apollo/sensor/...` 查看原始数据
4. **分析时间戳** → Cyber RT Header timestamp_sec 单调性、传感器间同步误差
5. **排查补偿器** → `compensator/` 运动补偿参数（IMU 频率/车辆速度）
6. **检查融合层** → 多 LiDAR 融合时检查坐标系转换和时间对齐

## Cyber RT Channel 规范（传感器层）

| Channel | 类型 | 发布者 | 说明 |
|---------|------|--------|------|
| `/apollo/sensor/lidar128/PointCloud2` | `PointCloud` | drivers/lidar | 原始点云 |
| `/apollo/sensor/lidar128/compensator/PointCloud2` | `PointCloud` | compensator | 补偿后点云 |
| `/apollo/sensor/radar/front` | `ContiRadar` | drivers/radar | 雷达目标 |
| `/apollo/sensor/camera/front_6mm/image` | `Image` | drivers/camera | 相机图像 |
| `/apollo/sensor/gnss/best_pose` | `GnssBestPose` | drivers/gnss | GNSS 定位 |
| `/apollo/sensor/gnss/imu` | `Imu` | drivers/gnss | IMU 数据 |

## 输出规范

```markdown
# Apollo 传感器驱动问题分析报告

## 1. 传感器配置与硬件连接
## 2. 驱动启动状态
## 3. 原始数据质量评估
## 4. 时间同步状态
## 5. 补偿器与融合层分析
## 6. 根因定位
## 7. 修复方案
## 8. 验证方法
```

## 关键原则

- **LiDAR 驱动问题先看 parser**：各家厂商的点云协议格式不同，parser 是最常见的故障点
- **时间同步是传感器融合的前提**：LiDAR-Camera 时间偏移 > 50ms 会导致融合结果不可用
- **compensator 依赖 IMU 频率**：IMU 数据丢帧会导致点云运动补偿不准确
- **Camera 帧率不稳先看 ISP**：ISP 处理耗时过长会导致帧率下降
- **Radar 假阳性先看 RCS 门限**：雷达反射截面积（RCS）门限设置过低会导致大量虚假目标
- **新传感器适配从 proto 开始**：新增传感器型号需先定义 Protobuf 消息格式，再实现 parser
- **HAL 层屏蔽硬件差异**：通过 HAL 抽象层统一接口，上层代码不直接依赖具体硬件
