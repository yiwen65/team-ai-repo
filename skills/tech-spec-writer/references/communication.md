# 通信架构参考

## 车载网络对比

| 技术 | 带宽 | 延迟 | 可靠性 | 用途 |
|------|------|------|--------|------|
| CAN 2.0 | 500 Kbps | ~1ms | 高 | 底盘控制、传统信号 |
| CAN-FD | 8 Mbps | ~0.5ms | 高 | 新一代底盘 |
| Ethernet 100BASE-T1 | 100 Mbps | ~0.1ms | 中 | 诊断、OTA |
| Ethernet 1000BASE-T1 | 1 Gbps | ~0.05ms | 中 | ADAS 传感器 |
| 10GBASE-T1 | 10 Gbps | ~0.01ms | 中 | 激光雷达 |
| TSN (IEEE 802.1) | 1-10 Gbps | 确定性 | 高 | 实时控制 |
| DDS (ROS2) | 1-10 Gbps | ~0.1ms | 可配置 | 智驾系统内部 |

## 智驾系统典型网络拓扑

```
[传感器域]
  ├── 相机 × N → GMSL2 / FPD-Link III → 1000BASE-T1
  ├── 激光雷达 × M → Ethernet 10G
  ├── 毫米波 × K → CAN-FD
  └── IMU/GNSS → CAN-FD / 100BASE-T1
        │
        ▼
[计算域 - 智驾域控制器]
  ├── 主芯片 (Orin/J5) ← 传感器数据
  ├── 冗余芯片 (Orin/J5) ← 备份数据
  └── MCU ← 底盘控制指令
        │
        ▼
[执行域]
  ├── 转向 EPS ← CAN-FD / TSN
  ├── 制动 IPB ← CAN-FD / TSN
  └── 驱动 VCU ← CAN-FD
```

## DDS QoS 配置

```xml
<!-- 传感器数据：高吞吐，允许丢帧 -->
<qos_profile name="sensor_profile">
    <reliability kind="BEST_EFFORT"/>
    <durability kind="VOLATILE"/>
    <history kind="KEEP_LAST" depth="1"/>
    <deadline period="100ms"/>
</qos_profile>

<!-- 控制指令：必须送达，持久化 -->
<qos_profile name="control_profile">
    <reliability kind="RELIABLE"/>
    <durability kind="TRANSIENT_LOCAL"/>
    <history kind="KEEP_LAST" depth="5"/>
    <deadline period="50ms"/>
</qos_profile>
```

## 时间同步

**gPTP (IEEE 802.1AS)**：
- 精度：< 1μs
- 主时钟：GNSS 授时或域控制器
- 从时钟：所有传感器节点

**PTP (IEEE 1588)**：
- 精度：< 100μs
- 适用于 Ethernet 网络

**硬件时间戳**：
- 传感器：硬件时间戳 + gPTP 同步
- 软件时间戳：精度差（受系统调度影响），仅用于诊断
