# 功能安全方案参考

## ASIL 分解策略

**独立性要求**：
- 冗余通道必须电气隔离、软件隔离、物理隔离
- 共因失效分析（CCA）：识别共同根因

**典型分解**：
```
ASIL D → ASIL B(D) + ASIL B(D)

例：AEB 系统
  ├── 主通道：相机 + 算法 + 控制 → ASIL B(D)
  └── 冗余通道：毫米波 + 简化算法 + 独立制动 → ASIL B(D)
  
  独立性验证：
  - 传感器：不同物理原理（视觉 vs 雷达）
  - 算法：不同实现团队/不同架构
  - 执行：独立 CAN 通道 + 独立制动回路
```

## 冗余架构

| 层级 | 冗余方案 | 切换时间 | 适用 |
|------|---------|---------|------|
| 传感器 | 异构冗余（相机+雷达） | 实时 | 感知 |
| 计算 | 双 Orin 热备 | < 50ms | 主控 |
| 通信 | 双以太网 + CAN | < 10ms | 网络 |
| 执行 | 双制动回路 | < 100ms | 底盘 |

## 降级策略

| 故障 | 检测方法 | 降级级别 | 动作 |
|------|---------|---------|------|
| 主相机失效 | 帧超时/图像异常 | L2 → L1 | 切换环视相机，限速 |
| 激光雷达失效 | 点云超时 | L2 → L1 | 纯视觉，限速 |
| 主 Orin 失效 | 心跳超时 | L2 → L0 | 切换备 Orin，继续运行 |
| 双 Orin 失效 | 双心跳超时 | L2 → 人工 | 安全停车，请求接管 |
| 制动失效 | 指令反馈异常 | L2 → 人工 | 缓速滑行，双闪 |

## 安全机制

```cpp
// 看门狗 + 安全监控
class SafetyMonitor {
public:
    void checkHeartbeat() {
        if (now() - last_heartbeat_ > timeout_) {
            // 触发降级
            enterDegradedMode();
            // 记录 DTC
            setDTC(DTC_HEARTBEAT_LOST);
        }
    }
    
    void checkOutputPlausibility() {
        // 输出合理性检查
        if (abs(steering_cmd_) > MAX_STEERING) {
            steering_cmd_ = sign(steering_cmd_) * MAX_STEERING;
            setDTC(DTC_STEERING_SATURATED);
        }
    }
    
private:
    void enterDegradedMode() {
        // 降级策略
        switch (current_level_) {
            case L2: current_level_ = L1; break;
            case L1: current_level_ = L0; break;
            case L0: requestTakeover(); break;
        }
    }
};
```
