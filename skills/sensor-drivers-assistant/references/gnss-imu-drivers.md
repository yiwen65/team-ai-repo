# GNSS/IMU 驱动开发指南

一句话简介：Apollo-Lite GNSS/IMU 驱动支持 RTK 差分定位和惯性导航，输出 `GnssBestPose` 和 `Imu` 消息，为 Localization、Planning 和 Sensor Fusion 提供位姿基准。

## 核心概念/原理

GNSS/IMU 驱动通常以组合导航形式工作：
- **GNSS 接收机**：接收卫星信号，输出原始观测值或 RTK 解算结果
- **IMU**：输出高频（100-200Hz）角速度和加速度
- **组合导航引擎**：在 GNSS 接收机内部或外部进行 Kalman 滤波融合
- **时间同步**：GNSS 秒脉冲（PPS）用于各传感器统一时间基准

## Apollo-Lite 中的实现位置

- GNSS/IMU 驱动：`modules/drivers/gnss/`
- RTK 定位：`modules/localization/rtk/`
- MSF 融合：`modules/localization/msf/`
- Protobuf：`modules/common_msgs/localization_msgs/`

## 关键配置参数

```protobuf
// gnss 配置
gnss_conf {
  frame_id: "gnss"
  tf_child_frame_id: "imu"
  enable_ins: true
  imu_rate: 100   # Hz
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| RTK 无法固定解 | 基站距离远/遮挡多/电离层活跃 | 检查基线距离、卫星数量、PDOP |
| IMU 数据漂移 | 温度漂移/零偏未标定 | 静止时采集零偏，做温度补偿 |
| 组合导航发散 | GNSS 失锁时间过长 | 限制纯 IMU 推算时间 < 30s |
| 时间戳跳秒 | GNSS 闰秒/接收机跳变 | 监控 `GnssStatus` 中的时间状态 |

## 与其他模块的接口

- **localization/rtk**：直接使用 `GnssBestPose`
- **localization/msf**：GNSS + IMU + LiDAR 融合
- **drivers/lidar**：PPS 信号用于 LiDAR 时间同步
- **planning**：车辆速度/航向用于 ReferenceLine 匹配
