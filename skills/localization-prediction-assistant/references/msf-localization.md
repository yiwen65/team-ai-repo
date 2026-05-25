# MSF 多传感器融合定位

一句话简介：MSF（Multi-Sensor Fusion）融合 LiDAR 点云、IMU 和 GNSS 数据，在 RTK 失锁或遮挡场景下提供连续可靠的定位输出，是 Apollo-Lite 高精度定位的核心。

## 核心概念/原理

MSF 融合框架：
- **预测阶段**：IMU 高频推算（100-200Hz）
- **量测阶段**：GNSS/RTK 提供全局约束，LiDAR 点云提供局部约束
- **地图匹配**：将点云与 HDMap 进行配准（NDT/ICP）
- **状态估计**：误差状态 EKF 或因子图优化

## Apollo-Lite 中的实现位置

- MSF 主模块：`modules/localization/msf/`
- 本地集成：`modules/localization/msf/local_integ/`
- 本地地图：`modules/localization/msf/local_map/`
- NDT 配准：`modules/localization/ndt/`
- 第三方库：`third_party/localization_msf/`

## 关键配置参数

```protobuf
msf_config {
  imu_rate: 100
  gnss_rate: 10
  lidar_rate: 10
  map_path: "/apollo/modules/map/data/"
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 融合发散 | IMU 零偏漂移/地图不匹配 | 检查 Allan 方差和地图版本 |
| 定位抖动 | LiDAR 配准不稳定 | 调整 NDT 分辨率，增加关键点 |
| RTK 失锁后漂移 | 纯 IMU 推算超限时 | 限制推算时间，触发降级策略 |

## 与其他模块的接口

- **map/hdmap**：依赖高精地图进行点云匹配
- **drivers/lidar**：LiDAR 点云输入
- **drivers/gnss**：GNSS/RTK 全局约束
- **localization/rtk**：RTK 作为 MSF 的观测输入
