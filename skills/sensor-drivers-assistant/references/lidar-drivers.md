# LiDAR 驱动开发指南

一句话简介：Apollo-Lite 支持 8 家 LiDAR 厂商（Hesai/Livox/Velodyne/Robosense/Vanjee/Seyond/lslidar），通过统一的 `lidar_driver_component` 框架接入，实现点云采集、解析、补偿与发布。

## 核心概念/原理

LiDAR 驱动采用分层架构：
- **硬件接口层**：UDP/TCP 接收原始数据包
- **Parser 层**：按厂商协议解析为点云（XYZI/XYZIT）
- **Compensator 层**：基于 IMU/车速数据对点云进行运动补偿
- **Fusion 层**：多 LiDAR 点云融合（可选）

关键流程：
1. 驱动 Component 以固定频率接收 UDP 数据包
2. Parser 按厂商协议提取点坐标、强度、时间戳
3. Compensator 根据车辆运动状态修正点云位置
4. 通过 Cyber RT Channel 发布 `PointCloud` 消息

## Apollo-Lite 中的实现位置

- 通用驱动 Component：`modules/drivers/lidar/lidar_driver_component.cc/.h`
- Hesai：`modules/drivers/lidar/hesai/`
- Livox：`modules/drivers/lidar/livox/`
- Velodyne：`modules/drivers/lidar/velodyne/`
  - 在线标定：`modules/drivers/lidar/velodyne/parser/online_calibration.h`
- Robosense：`modules/drivers/lidar/rslidar/`
- Vanjee：`modules/drivers/lidar/vanjeelidar/`
- Seyond：`modules/drivers/lidar/seyond/`
- lslidar：`modules/drivers/lidar/lslidar/`
- 补偿器：`modules/drivers/lidar/compensator/`
- 融合：`modules/drivers/lidar/fusion/`
- Protobuf：`modules/drivers/lidar/proto/`

## 关键配置参数

```protobuf
// lidar 驱动配置示例
model: "Pandar128"
frame_id: "lidar128"
scan_channel: "/apollo/sensor/lidar128/PointCloud2"
 compensator_channel: "/apollo/sensor/lidar128/compensator/PointCloud2"
frequency: 10
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 无点云输出 | 网络不通/IP 配置错误 | `ping` LiDAR IP，检查防火墙 |
| 点云稀疏 | 激光器故障/扫描频率降低 | 对比厂商官方工具输出 |
| 点云畸变 | 补偿器参数错误/IMU 数据异常 | 检查 `compensator` 的 IMU 输入频率 |
| 时间戳跳变 | LiDAR 内部时钟漂移 | 启用硬件同步（PTP/gPTP） |
| 多 LiDAR 融合错位 | 外参不准/时间不同步 | 检查标定文件和各 LiDAR 时间戳偏差 |

## 与其他模块的接口

- **perception/lidar**：接收补偿后的 `PointCloud` 进行目标检测
- **drivers/gnss**：为 compensator 提供车辆位姿
- **calibration**：外参用于多 LiDAR 融合和 LiDAR-Camera 联合标定
- **localization/msf**：LiDAR 点云用于 MSF 定位
