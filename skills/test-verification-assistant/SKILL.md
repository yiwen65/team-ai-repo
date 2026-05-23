---
name: apollo-test-verification-assistant
description: >
  Apollo-Lite 自动驾驶测试验证深度助手。基于 Cyber RT 中间件，覆盖 cyber_recorder 数据回放、
  场景库测试、集成测试、SIL/HIL 测试、性能测试、安全验证。
  涉及 Apollo 测试框架（integration_tests、scenario_manager）、dreamview 可视化验证、
  guardian 安全监控、monitor 系统监控。在以下场景触发使用：
  (1) Apollo 模块集成测试与问题排查，(2) cyber_recorder 数据录制/回放/分析，
  (3) 场景库设计（lane_follow/intersection/park/emergency），(4) dreamview 可视化验证与问题，
  (5) guardian 安全监控与异常处理，(6) monitor 系统健康检查与告警。
---

# Apollo Test-Verification Assistant

Apollo-Lite 测试验证深度助手。覆盖数据回放、场景测试、集成验证、安全监控全链路。

## 快速启动

用户提供以下信息即可触发分析：
- Apollo-lite 路径 + 测试模块（integration_tests/dreamview/guardian/monitor）
- cyber_recorder 记录文件（.record）+ 回放问题
- 测试场景（lane_follow/intersection/park）+ 测试结果
- 安全监控日志（guardian/monitor）+ 异常描述

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| 数据回放 | cyber_recorder 录制/回放/分析 | `references/cyber-recorder.md` |
| 集成测试 | Bazel 测试、模块集成验证 | `references/integration-test.md` |
| 场景测试 | ScenarioManager 场景库验证 | `references/scenario-test.md` |
| Dreamview | 可视化验证、HMI 交互 | `references/dreamview-test.md` |
| Guardian | 安全监控、异常处理、降级 | `references/guardian-test.md` |
| Monitor | 系统健康、资源监控、告警 | `references/monitor-test.md` |

## Apollo-lite 测试模块结构

```
modules/
├── planning/integration_tests/     # Planning 集成测试
├── control/integration_tests/      # Control 集成测试
├── dreamview/                      # 可视化与 HMI
│   ├── backend/                    # 后端数据服务
│   └── frontend/                   # 前端界面
├── guardian/                       # 安全监控模块
│   ├── guardian_component.cc       # 主组件
│   └── guardian_monitor.cc         # 监控逻辑
└── monitor/                        # 系统监控
    ├── monitor_component.cc        # 监控组件
    ├── hardware/                     # 硬件监控
    └── software/                     # 软件监控
```

## 测试问题诊断流程

1. **确认测试环境** → Docker 容器、Bazel 编译、cyber 启动
2. **数据回放检查** → cyber_recorder 录制完整性、channel 数据流
3. **模块集成验证** → 各模块 DAG 启动、channel 连通性
4. **场景执行分析** → ScenarioManager 场景识别、Stage 执行、Task 输出
5. **安全监控检查** → Guardian 状态、异常检测、降级策略
6. **系统监控验证** → Monitor 资源使用、硬件状态、告警规则

## Cyber Recorder 工具

```bash
# 录制所有 channel
cyber_recorder record -a

# 录制指定 channel
cyber_recorder record -c /apollo/perception/obstacles \
                       -c /apollo/planning/trajectory \
                       -c /apollo/control/chassis

# 回放数据
cyber_recorder play -f 20260524.record

# 回放指定 channel
cyber_recorder play -f 20260524.record -c /apollo/perception/obstacles

# 查看记录信息
cyber_recorder info 20260524.record
```

## Guardian 安全监控

```protobuf
// modules/guardian/conf/guardian_conf.pb.txt
guardian_config {
  enable: true
  
  // 监控的模块
  monitored_modules: "planning"
  monitored_modules: "control"
  monitored_modules: "perception"
  
  // 超时阈值
  timeout_threshold_ms: 500
  
  // 异常处理
  action: EMERGENCY_STOP   # 或 SOFT_STOP / WARN_ONLY
}
```

## Monitor 系统监控

```protobuf
// modules/monitor/conf/monitor_conf.pb.txt
monitor_config {
  // CPU 监控
  cpu_monitor {
    enable: true
    alarm_threshold: 90.0    # CPU 使用率告警阈值
  }
  
  // 内存监控
  memory_monitor {
    enable: true
    alarm_threshold: 90.0    # 内存使用率告警阈值
  }
  
  // 磁盘监控
  disk_monitor {
    enable: true
    alarm_threshold: 90.0    # 磁盘使用率告警阈值
  }
  
  // 模块心跳监控
  module_monitor {
    enable: true
    timeout_threshold: 1000   # ms
  }
}
```

## Dreamview 可视化

```bash
# 启动 Dreamview
/apollo/bazel-bin/modules/dreamview/dreamview

# Dreamview 默认端口
http://localhost:8888

# 主要功能
- 地图显示与轨迹可视化
- 障碍物与感知结果渲染
- 规划轨迹与控制命令显示
- 模块状态监控面板
- HMI 交互（启动/停止/模式切换）
```

## 输出规范

```markdown
# Apollo 测试验证分析报告

## 1. 测试环境与配置
## 2. 数据回放状态
## 3. 模块集成验证
## 4. 场景执行结果
## 5. 安全监控状态
## 6. 系统监控告警
## 7. 问题根因
## 8. 修复与验证
```

## 关键原则

- **Apollo 测试问题先看 cyber_recorder 完整性**：录制文件损坏或 channel 缺失会导致回放异常
- **Guardian 异常会触发全系统降级**：监控模块超时或异常 → Guardian 触发 EMERGENCY_STOP → 车辆安全停车
- **Dreamview 不更新先查 WebSocket**：前端与后端通过 WebSocket 通信，backend 数据服务异常会导致界面冻结
- **Monitor 告警要分级处理**：CPU/内存/磁盘告警 → 资源优化；模块超时告警 → 模块重启或排查
- **集成测试必须覆盖所有 Scenarios**：lane_follow、intersection、park、emergency 等场景必须逐一验证
