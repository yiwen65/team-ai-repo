# VehicleFactory 使用指南

一句话简介：VehicleFactory 是 Apollo-Lite Canbus 模块的车型动态加载机制，通过工厂模式在运行时根据配置创建对应车型的 VehicleController 和 MessageManager 实例。

## 核心概念/原理

工厂模式设计：
- **AbstractVehicleFactory**：抽象工厂接口
- **VehicleFactory**：具体工厂，维护车型名称 → 创建函数的映射表
- **注册机制**：每种车型在编译时通过宏或显式代码注册到工厂
- **动态创建**：运行时根据 `vehicle_type` 配置创建对应实例

## Apollo-Lite 中的实现位置

- 抽象工厂：`modules/canbus/abstract_vehicle_factory.cc/.h`
- 车辆工厂：`modules/canbus/vehicle_factory.cc/.h`
- 注册示例：各车型的 `vehicle_factory.cc` 注册代码

## 注册示例

```cpp
// 在 vehicle_factory.cc 中注册新车型
void VehicleFactory::RegisterVehicle() {
  Register("Lincoln", []() -> AbstractVehicleFactory* {
    return new LincolnVehicleFactory();
  });
  Register("Devkit", []() -> AbstractVehicleFactory* {
    return new DevkitVehicleFactory();
  });
  // ... 其他车型
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 车型未找到 | 名称拼写不一致 | 核对配置 `vehicle_type` 和注册名称 |
| so 加载失败 | 编译产物路径错误 | 检查 DAG 中 `module_library` 路径 |
| 多车型冲突 | 不同车型使用了相同符号 | 使用命名空间隔离各车型实现 |

## 与其他模块的接口

- **canbus_component**：启动时调用 Factory 创建车型实例
- **config**：`vehicle_type` 配置决定加载哪种车型
