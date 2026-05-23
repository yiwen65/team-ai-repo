---
name: apollo-report-writer
description: >
  Apollo-Lite 自动驾驶项目技术汇报深度助手。覆盖 Apollo-lite 特有的汇报场景：
  Cyber RT 模块状态汇报、DAG 拓扑变更汇报、Bazel 构建结果汇报、传感器标定报告、
  规划控制性能汇报（ReferenceLine/Trajectory/Control Tracking）、感知精度汇报（mAP/延迟）、
  测试验证报告（scenario 通过率/cyber_recorder 回放结果）、Guardian/Monitor 安全监控报告。
  支持不同层级（工程师→TL→总监→VP→CTO）和多种形式（Markdown/PPT 大纲/邮件/文档）。
  在以下场景触发使用：
  (1) Apollo 模块开发进度汇报（Cyber RT DAG/Component/Channel 状态），
  (2) 感知/规划/控制算法性能汇报（精度/延迟/跟踪误差），
  (3) 测试验证汇报（scenario 通过率/回归测试结果），
  (4) 安全监控汇报（Guardian/Monitor 告警与处理），
  (5) 传感器标定与验证汇报，(6) 技术方案评审与答辩。
---

# Apollo Report Writer

Apollo-Lite 项目技术汇报深度助手。覆盖 Apollo 特有的模块状态、性能指标、安全监控汇报。

## 快速启动

用户提供以下信息即可生成汇报：
- 汇报对象层级（工程师/TL/总监/VP/CTO）
- 汇报场景（模块状态/算法性能/测试结果/安全监控/标定验证）
- Apollo-lite 路径 + 相关日志/数据/配置文件
- 时间限制（5min / 15min / 30min）

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| 模块状态 | Cyber RT DAG/Component/Channel 状态汇报 | `references/module-status-report.md` |
| 算法性能 | 感知/规划/控制精度、延迟、跟踪误差 | `references/algorithm-performance-report.md` |
| 测试验证 | Scenario 通过率、回归测试、回放分析 | `references/test-verification-report.md` |
| 安全监控 | Guardian/Monitor 告警、异常处理、降级 | `references/safety-monitor-report.md` |
| 标定验证 | 传感器标定结果、重投影误差、漂移检测 | `references/calibration-report.md` |
| 技术评审 | 方案对比、风险评估、Q&A 预判 | `references/tech-review-report.md` |

## Apollo 特有汇报指标

### Cyber RT 模块状态

| 指标 | 说明 | 正常范围 |
|------|------|---------|
| DAG 加载率 | 成功加载的 DAG / 总 DAG | 100% |
| Component 启动率 | 成功启动的 Component / 总 Component | 100% |
| Channel 数据率 | 有数据的 Channel / 总 Channel | > 95% |
| 消息延迟 | Header 时间戳差 | < 100ms |
| 消息丢帧率 | 期望频率 vs 实际频率 | < 5% |

### 感知性能指标

| 指标 | 说明 | 目标 |
|------|------|------|
| mAP (Camera) | 平均精度均值 | > 70% |
| mAP (LiDAR) | 点云检测精度 | > 65% |
| 端到端延迟 | 图像输入 → 感知输出 | < 150ms |
| 跟踪准确率 | ID 保持率 | > 95% |
| 融合精度 | 多传感器融合位置误差 | < 0.3m |

### 规划控制性能指标

| 指标 | 说明 | 目标 |
|------|------|------|
| 规划成功率 | 成功生成轨迹 / 总请求 | > 99% |
| 规划延迟 | 请求 → 轨迹输出 | < 100ms |
| 横向跟踪误差 | 实际位置 vs 规划位置 (RMS) | < 0.2m |
| 纵向跟踪误差 | 实际速度 vs 规划速度 (RMS) | < 0.5m/s |
| 横向加速度 | 最大 | < 2.0 m/s² |
| 纵向 jerk | 最大 | < 2.5 m/s³ |

### 安全监控指标

| 指标 | 说明 | 目标 |
|------|------|------|
| Guardian 触发率 | 安全干预次数 / 总运行时间 | < 0.1/h |
| Monitor 告警率 | 告警次数 / 总运行时间 | < 1/h |
| 模块心跳丢失 | 模块无响应次数 | 0 |
| 系统资源使用率 | CPU/内存/磁盘 | < 80% |

## 汇报模板

### 模块状态日报

```markdown
# Apollo 模块状态日报 (YYYY-MM-DD)

## Cyber RT 系统状态
- DAG 加载: 12/12 ✅
- Component 运行: 28/28 ✅
- Channel 活跃: 45/48 ⚠️ (3 个 channel 无数据)

## 各模块状态
| 模块 | 状态 | CPU | 内存 | 延迟 | 说明 |
|------|------|-----|------|------|------|
| Perception | 🟢 | 45% | 2.1G | 120ms | 正常 |
| Planning | 🟢 | 30% | 1.5G | 80ms | 正常 |
| Control | 🟢 | 15% | 0.8G | 10ms | 正常 |
| Localization | 🟡 | 60% | 1.2G | 50ms | CPU 偏高 |

## 异常与处理
1. **Localization CPU 60%** → 正在排查 IMU 数据处理逻辑
2. **3 个 Channel 无数据** → Radar 驱动未启动，已重启

## 明日计划
- 修复 Localization CPU 问题
- 完成 Radar 驱动稳定性测试
```

### 算法性能周报

```markdown
# 感知算法性能周报 (YYYY-MM-DD)

## 本周进展
1. ✅ YOLO-3D 模型优化: mAP 71.0% → 74.2% (+3.2%)
2. ✅ TensorRT FP16 部署: 延迟 150ms → 85ms (-43%)
3. 🔄 车道线 DarkSCNN: 测试中

## 关键指标对比
| 指标 | 上周 | 本周 | 目标 | 趋势 |
|------|------|------|------|------|
| Camera mAP | 71.0% | 74.2% | 75.0% | ↗ |
| LiDAR mAP | 63.5% | 65.1% | 68.0% | ↗ |
| 端到端延迟 | 150ms | 85ms | 100ms | ↘ ✅ |
| 跟踪准确率 | 94.2% | 95.5% | 95.0% | ↗ ✅ |

## 问题与风险
| 问题 | 等级 | 影响 | 缓解 |
|------|------|------|------|
| DarkSCNN 隧道场景断裂 | 🟡 | 夜间可用性 | 增加隧道数据训练 |

## 下周计划
- DarkSCNN 隧道场景优化
- 多传感器融合精度提升 (目标 < 0.25m)
```

### 安全监控月报

```markdown
# 安全监控月报 (YYYY-MM)

## Guardian 统计
- 总触发: 3 次 (目标 < 5 次 ✅)
- 触发原因:
  - Planning 超时 1 次 → 已优化 Task 调度
  - Control 延迟 1 次 → 已增加 MPC 预测 horizon
  - Perception 丢帧 1 次 → 已修复 Camera 驱动

## Monitor 告警
- CPU 告警: 12 次 (目标 < 20 次 ✅)
- 内存告警: 2 次 (目标 < 5 次 ✅)
- 磁盘告警: 0 次 ✅

## 异常处理
| 异常 | 次数 | 处理 | 状态 |
|------|------|------|------|
| Planning 无解 | 5 | 优化 ReferenceLine | 已解决 |
| Control 饱和 | 3 | 调整 MPC 约束 | 已解决 |

## 下月目标
- Guardian 触发 < 2 次
- 零模块心跳丢失
- 系统资源使用率 < 70%
```

## 输出规范

所有汇报材料默认结构：

```markdown
# [汇报标题]

## 1. 一句话结论（TL;DR）
## 2. Apollo 系统/模块状态快照
## 3. 关键指标（量化对比）
## 4. 异常与风险
## 5. 处理措施与进展
## 6. 下一步/资源需求
## 7. Q&A 预判（评审场景）
```

## 关键原则

- **Apollo 汇报先看系统状态**：Cyber RT 模块健康度是一切的基础
- **指标必须对标 Apollo 目标**：mAP、延迟、跟踪误差有明确的内部目标值
- **异常必须带处理闭环**：不仅是发现问题，要有处理措施和验证结果
- **Guardian/Monitor 告警不可忽视**：安全相关的任何异常都必须立即响应
- **不同层级不同深度**：工程师看 channel 级指标，VP 看系统级趋势
- **数据说话**：每个结论必须有 cyber_monitor/cyber_recorder 的数据支撑
