# Radar 驱动开发指南

一句话简介：Apollo-Lite 支持 Continental、Racobit、NanoRadar、超声波等多种 Radar 驱动，将雷达原始目标数据解析为 Apollo `ContiRadar` 格式，供感知融合模块使用。

## 核心概念/原理

Radar 驱动主要处理两类数据：
- **目标级数据**：雷达已完成的聚类目标（位置、速度、RCS）
- **原始回波数据**：原始 ADC 采样（部分高端雷达支持）

Apollo-Lite 主要使用目标级数据：
1. 通过 CAN/以太网接收雷达目标列表
2. 按 DBC/厂商协议解析目标属性
3. 转换为统一的 `ContiRadar` Protobuf 消息
4. 通过 Cyber RT Channel 发布

## Apollo-Lite 中的实现位置

- Continental：`modules/drivers/radar/conti_radar/`
- Racobit：`modules/drivers/radar/racobit_radar/`
- NanoRadar：`modules/drivers/radar/nano_radar/`
- 超声波雷达：`modules/drivers/radar/ultrasonic_radar/`、`udas_ultrasonic_radar/`
- YG Radar：`modules/drivers/radar/yg_radar/`
- Protobuf：`modules/drivers/radar/proto/`

## 关键配置参数

```protobuf
// conti_radar 配置
can_channel: "can0"
radar_conf {
  radar_id: 0
  obstacle_conf {
    range_threshold: 0.5    # 距离门限 (m)
  }
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 目标数量异常多 | RCS 门限过低 | 调整 `range_threshold` 和 RCS 滤波 |
| 目标频繁跳变 | 聚类算法不稳定 | 启用跟踪器平滑或调整聚类参数 |
| 速度异常 | 径向速度分解错误 | 检查雷达安装角度和车辆速度输入 |
| 假阳性多 | 多径反射/地面杂波 | 调整俯仰角门限，过滤地面回波 |

## 与其他模块的接口

- **perception/radar**：接收 `ContiRadar` 进行目标级处理
- **perception/fusion**：Radar 目标与 Camera/LiDAR 目标融合
- **canbus**：Radar 数据通常通过 CAN 总线接入，与底盘 CAN 共用或独立
