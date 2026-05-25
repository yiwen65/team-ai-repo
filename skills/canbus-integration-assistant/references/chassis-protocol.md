# 底盘协议解析

一句话简介：底盘协议解析负责将 Apollo 控制指令编码为 CAN/以太网帧，以及将底盘状态帧解码为 Apollo Protobuf 消息，是 Canbus 模块的核心数据转换层。

## 核心概念/原理

协议解析架构：
- **MessageManager**：管理所有 CAN 消息的收发
- **Protocol 类**：每个 CAN ID 对应一个 Protocol 类，负责编解码
- **Parse 流程**：CAN 原始字节 → 按 DBC 信号定义提取 → 转换为物理量
- **Encode 流程**：Apollo 控制值 → 按 DBC 信号定义打包 → CAN 字节

## Apollo-Lite 中的实现位置

- MessageManager：`modules/canbus/vehicle/<name>/<name>_message_manager.cc/.h`
- Protocol 定义：`modules/canbus/vehicle/<name>/protocol/`
- DBC 工具：`modules/tools/whl-can/`

## 关键编码规则

| 属性 | 说明 | 示例 |
|------|------|------|
| CAN ID | 标准帧 11bit / 扩展帧 29bit | 0x0C0 |
| Start Bit | 信号起始位（Intel/Motorola） | 0 |
| Length | 信号长度（bit） | 16 |
| Factor | 物理值 = raw × factor + offset | 0.01 |
| Offset | 偏移量 | 0 |
| Byte Order | Intel（Little Endian）/ Motorola（Big Endian）| Intel |

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 数值跳变 | 符号位处理错误（有符号/无符号） | 核对 DBC 的 Value Type |
| 精度丢失 | factor 过小，整数精度不足 | 检查 DBC 的 factor 和 length |
| 多帧解析混乱 | 周期不一致导致状态不同步 | 按 CAN ID 分队列处理 |

## 与其他模块的接口

- **VehicleController**：调用 MessageManager 发送控制帧
- **drivers/canbus**：底层 CAN 收发
- **monitor**：解析异常上报到系统监控
