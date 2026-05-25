# Camera 驱动开发指南

一句话简介：Apollo-Lite Camera 驱动负责图像采集、ISP 处理和帧同步，通过 V4L2/GMSL 接口接入相机，输出标准化 `Image` 消息供感知模块使用。

## 核心概念/原理

Camera 驱动核心链路：
- **图像采集**：通过 V4L2（USB/GMSL）或厂商 SDK 获取 RAW/YUV 图像
- **ISP 处理**：去噪、白平衡、Gamma 校正（部分在硬件 ISP 完成）
- **时间戳标记**：采集时刻打上 Cyber RT Header 时间戳
- **发布**：通过 Cyber RT Channel 发布 `Image` 消息

关键要求：
- 帧率稳定（通常 10/15/30Hz）
- 时间戳精度 < 1ms（用于多传感器同步）
- 图像分辨率与感知模型输入匹配

## Apollo-Lite 中的实现位置

- Camera 驱动：`modules/drivers/camera/`
- HAL 抽象：`modules/drivers/hal/`
- 图像 Protobuf：`modules/common_msgs/sensor_msgs/image.proto`

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 图像花屏/绿屏 | GMSL 线束接触不良/速率不匹配 | 检查线束和 SERDES 速率配置 |
| 帧率不稳 | ISP 负载过高/曝光时间波动 | 固定曝光时间和增益 |
| 图像延迟高 | 缓冲区堆积 | 减少 buffer 数量，增加消费线程 |
| 时间戳偏差 | 软触发 vs 硬触发 | 启用硬件 trigger 或 PTP 同步 |

## 与其他模块的接口

- **perception/camera**：接收 `Image` 进行 2D/3D 检测
- **calibration**：相机内参和畸变参数用于图像去畸变
- **drivers/gnss**：硬件同步时需要 GNSS PPS 信号
