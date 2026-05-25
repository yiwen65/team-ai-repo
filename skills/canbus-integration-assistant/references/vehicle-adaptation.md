# 车型适配指南

一句话简介：Apollo-Lite Canbus 支持 13+ 款车型平台，每款车型需实现完整的 VehicleController + MessageManager + DBC 协议解析，是自动驾驶系统量产落地的核心工程工作。

## 核心概念/原理

车型适配本质是协议翻译工作：
1. **控制指令翻译**：Apollo Protobuf → 车型底盘 CAN/以太网帧
2. **状态反馈翻译**：底盘 CAN/以太网帧 → Apollo Protobuf
3. **安全机制对接**：底盘故障码 → Guardian 安全策略

适配内容：
- 油门响应曲线（百分比 → 扭矩/转速）
- 刹车压力映射（百分比 → 液压压力）
- 转向角度协议（目标角度 → CAN 信号）
- 档位控制（P/R/N/D → 底盘信号）
- 底盘状态反馈（车速、轮速、方向盘角度、故障码）

## Apollo-Lite 中的实现位置

- 抽象工厂：`modules/canbus/abstract_vehicle_factory.cc/.h`
- 车辆工厂：`modules/canbus/vehicle_factory.cc/.h`
- 控制器基类：`modules/canbus/vehicle_controller.cc/.h`
- 各车型目录：`modules/canbus/vehicle/<name>/`

## 新增车型流程

```
1. 获取底盘协议文档（DBC/协议手册）
2. 创建车型目录：modules/canbus/vehicle/new_vehicle/
3. 继承 VehicleController，实现控制接口
4. 继承 MessageManager，实现 CAN 帧解析/编码
5. 在 vehicle_factory.cc 中注册新车型
6. 编写单元测试（模拟 CAN 信号）
7. 实车标定（throttle/brake/steering 响应曲线）
8. 安全验证（故障注入、降级策略）
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 控制指令无效 | CAN ID 错误/信号长度不匹配 | 用 CANoe/PCAN 抓包对比 DBC |
| 底盘反馈异常 | 字节序错误（Big/Little Endian） | 核对 DBC 中的 Byte Order |
| 车型未识别 | factory 未注册/名称拼写错误 | 检查 `vehicle_factory.cc` 注册列表 |

## 与其他模块的接口

- **control**：接收 `ControlCommand`，转换为底盘协议
- **guardian**：上报底盘故障，触发安全降级
- **monitor**：上报底盘状态到系统监控
