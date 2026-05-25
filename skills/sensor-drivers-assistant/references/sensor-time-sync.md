# 多传感器时间同步

一句话简介：Apollo-Lite 通过 gPTP/PTP 协议和硬件 Trigger 实现 Camera、LiDAR、Radar、IMU、GNSS 的亚毫秒级时间同步，是传感器融合精度的基础保障。

## 核心概念/原理

时间同步架构：
- **主时钟源**：通常为 GNSS 接收机（PPS + NMEA）或 gPTP Grandmaster
- **从节点**：各传感器（LiDAR/Camera/Radar/IMU）作为 PTP 从时钟
- **同步方式**：
  - **硬件同步**：PPS 触发 + 编码时间戳（最精确，< 1ms）
  - **软件同步**：gPTP/PTP 协议同步网络时钟（< 5ms）
  - **后处理同步**：Cyber RT Header 时间戳对齐（> 10ms，用于离线）

## Apollo-Lite 中的实现位置

- Cyber RT 时间：`cyber/time/time.h`
- 时间转换：`cyber/common/time_conversion.h`
- GNSS PPS：`modules/drivers/gnss/`
- Velodyne 在线标定（含时间补偿）：`modules/drivers/lidar/velodyne/parser/online_calibration.h`

## 关键配置

```bash
# 主机 gPTP 配置（Linux ptp4l）
ptp4l -i eth0 -m -H  # 硬件时间戳

# LiDAR PTP 配置（厂商网页/配置工具）
ptp_domain: 0
ptp_transport: L2
time_sync_source: PTP
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 多传感器时间偏差 > 10ms | PTP 未同步/时钟源漂移 | `cyber_channel echo` 对比各传感器 Header timestamp |
| LiDAR-Camera 同步失效 | 硬件触发线断开 | 检查 Trigger 线缆和电平匹配 |
| 时间戳单调性异常 | NTP 跳变/系统时间回拨 | 禁用 NTP，使用 PTP 或单调时钟 |
| PTP 同步不稳定 | 网络抖动大 | 使用专用同步交换机，启用硬件时间戳 |

## 与其他模块的接口

- **perception/fusion**：依赖时间对齐后的多传感器数据进行目标融合
- **localization/msf**：IMU-LiDAR 时间对齐是融合精度关键
- **planning**：Planning 输入（感知+定位）时间戳对齐影响轨迹质量
