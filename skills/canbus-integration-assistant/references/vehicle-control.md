# 车辆控制指令

一句话简介：VehicleController 是 Apollo-Lite 与车辆底盘的交互接口，负责将 Planning 输出的轨迹/速度转化为具体的油门、刹车、转向、档位等底盘控制指令。

## 核心概念/原理

控制指令体系：
- **Throttle**：油门开度百分比（0-100%）
- **Brake**：刹车压力/百分比（0-100%）
- **Steering**：目标方向盘角度（deg）或角速度（deg/s）
- **Gear**：档位指令（P/R/N/D）
- **Emergency Brake**：紧急制动（独立于正常制动链路）

控制策略：
- 纵向控制由 PID/MPC 计算油门/刹车
- 横向控制由 LQR/MPC 计算目标方向盘角度
- 控制周期通常为 10-20ms（100-50Hz）

## Apollo-Lite 中的实现位置

- 控制器基类：`modules/canbus/vehicle_controller.cc/.h`
- Lincoln 示例：`modules/canbus/vehicle/lincoln/lincoln_controller.cc/.h`
- Devkit 示例：`modules/canbus/vehicle/devkit/devkit_controller.cc/.h`

## 关键接口

```cpp
class VehicleController {
  virtual ErrorCode Start() = 0;           // 启动底盘（使能线控）
  virtual ErrorCode Stop() = 0;            // 停止底盘（禁用线控）
  virtual ErrorCode Throttle(double pct) = 0;   // 油门百分比
  virtual ErrorCode Brake(double pct) = 0;      // 刹车百分比
  virtual ErrorCode Steer(double angle) = 0;    // 转向角度
  virtual ErrorCode Gear(int position) = 0;     // 档位
  virtual Chassis chassis() = 0;           // 底盘状态反馈
};
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 油门不回零 | 指令未正确发送/底盘未响应 | 抓包确认 CAN 帧，检查底盘使能状态 |
| 转向超调 | 响应曲线非线性/滞后大 | 标定转向响应曲线，调整 MPC 预测 horizon |
| 刹车不响应 | 液压系统未预充/安全互锁 | 检查底盘 ready 状态和液压压力 |
| 档位切换失败 | 车速不满足条件 | 确认车速 < 阈值（如 5km/h）才能切换 P/R |

## 与其他模块的接口

- **control**：接收 `ControlCommand`，调用 Throttle/Brake/Steer/Gear
- **guardian**：Emergency Brake 直接绕过正常控制链路
- **monitor**：上报控制指令执行状态
