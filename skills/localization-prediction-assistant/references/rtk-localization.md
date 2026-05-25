# RTK 定位

一句话简介：RTK（Real-Time Kinematic）通过差分 GNSS 技术实现厘米级定位，是 Apollo-Lite 定位系统的基础层，输出 `LocalizationEstimate` 供 Planning 和 Control 使用。

## 核心概念/原理

RTK 工作流程：
1. 流动站（车辆）接收卫星信号
2. 基站发送差分改正数（通过电台/4G/网络）
3. 流动站解算固定解（Fix），精度可达 2cm + 1ppm
4. 若信号遮挡则退化为浮点解（Float），精度 ~0.5m

## Apollo-Lite 中的实现位置

- RTK 定位：`modules/localization/rtk/`
- GNSS 驱动：`modules/drivers/gnss/`
- Protobuf：`modules/common_msgs/localization_msgs/localization.proto`

## 关键配置参数

```protobuf
rtk_config {
  use_gnss_heading: true
  gps_imu_offset: 0.0   # GNSS-IMU 杆臂偏移 (m)
  enable_ins: true      # 启用组合导航
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 无法固定解 | 卫星数不足/基线过长/电离层活跃 | 检查 CNR > 40、基线 < 20km |
| 定位跳变 | 多径效应/周跳 | 对比基准站数据，检查周跳统计 |
| 坐标系偏差 | 基准站坐标不准 | 核对基准站 ECEF 坐标 |

## 与其他模块的接口

- **planning**：`LocalizationEstimate` 用于 ReferenceLine 匹配
- **control**：车辆位姿用于 MPC 状态反馈
- **drivers/gnss**：RTK 输入依赖 GNSS 驱动数据质量
