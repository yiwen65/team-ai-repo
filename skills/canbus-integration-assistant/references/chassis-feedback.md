# 底盘状态反馈

一句话简介：底盘状态反馈通过 CAN/以太网持续上报车辆实际状态（车速、轮速、方向盘角度、油门/刹车位置、故障码），是 Control 闭环控制和安全监控的基础输入。

## 核心概念/原理

反馈信号分类：
- **运动状态**：车速、轮速、纵向加速度、横摆角速度
- **转向状态**：方向盘角度、方向盘角速度
- **踏板状态**：实际油门位置、实际刹车压力
- **档位状态**：当前档位、档位切换状态
- **故障状态**：EPS 故障、ABS 故障、VCU 故障等

## Apollo-Lite 中的实现位置

- 底盘消息：`modules/common_msgs/chassis_msgs/chassis.proto`
- Lincoln 解析：`modules/canbus/vehicle/lincoln/protocol/`
- Devkit 解析：`modules/canbus/vehicle/devkit/protocol/`

## 关键信号

```protobuf
// Chassis 消息核心字段
speed_mps: 12.5           # 车速 (m/s)
steering_percentage: 15.0 # 方向盘百分比
throttle_percentage: 20.0 # 油门百分比
brake_percentage: 0.0   # 刹车百分比
driving_mode: COMPLETE_AUTO_DRIVE  # 驾驶模式
error_code: NO_ERROR      # 故障码
gear_location: GEAR_DRIVE # 当前档位
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 车速为 0 但车在动 | 轮速信号未接入/协议错误 | 检查轮速 CAN ID 和 factor |
| 方向盘角度反向 | 方向定义与 Apollo 不一致 | 核对 DBC 中角度的正负定义 |
| 故障码频繁上报 | 底盘系统异常 | 根据故障码查底盘维修手册 |
| 反馈延迟高 | CAN 总线负载高 | 检查总线波特率和帧周期 |

## 与其他模块的接口

- **control**：用于 MPC 状态反馈，计算跟踪误差
- **guardian**：故障码触发安全降级
- **monitor**：底盘健康状态监控
