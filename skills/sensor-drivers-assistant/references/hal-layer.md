# 硬件抽象层（HAL）

一句话简介：Apollo-Lite HAL（Hardware Abstraction Layer）位于 `modules/drivers/hal/`，统一封装不同传感器硬件的差异，为上层驱动提供标准化的设备管理、配置和诊断接口。

## 核心概念/原理

HAL 设计目标：
- **设备统一抽象**：屏蔽不同厂商硬件接口差异（USB/CAN/以太网/串口）
- **热插拔支持**：设备动态发现和重新连接
- **配置管理**：统一加载和验证硬件配置
- **诊断接口**：标准化设备健康状态查询

## Apollo-Lite 中的实现位置

- HAL 层：`modules/drivers/hal/`
- 设备管理：`modules/drivers/hal/device_manager/`
- 配置解析：`modules/drivers/hal/config_parser/`

## 关键接口

```cpp
// HAL 设备接口示例
class HalDevice {
 public:
  virtual bool Init(const std::string& config_path) = 0;
  virtual bool Start() = 0;
  virtual bool Stop() = 0;
  virtual DeviceStatus GetStatus() = 0;
};
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 设备初始化失败 | 配置不匹配/驱动缺失 | 检查 HAL 配置文件和硬件 ID |
| 热插拔后无数据 | 重新枚举失败 | 重启对应 HAL 设备管理器 |
| 多设备冲突 | 资源（端口/中断）冲突 | 检查设备树和 IRQ 分配 |

## 与其他模块的接口

- **drivers/所有传感器**：各传感器驱动通过 HAL 访问底层硬件
- **monitor**：HAL 上报设备状态到系统监控
