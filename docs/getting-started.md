# Apollo-Lite 团队 AI Skill 使用指南

> 本文档面向 Apollo-Lite 自动驾驶开发团队，介绍如何高效使用 team-ai-repo 的 13 个 AI Skill。

## 📋 快速导航

| 开发阶段 | 推荐 Skill | 代码覆盖 |
|----------|-----------|---------|
| **中间件开发** | `cyber-rt-developer` | `cyber/` (~57K 行) |
| **传感器集成** | `sensor-drivers-assistant` | `drivers/` (~46K 行) |
| **感知算法** | `perception-assistant` | `perception/` (~158K 行) |
| **标定验证** | `calibration-assistant` | `perception/camera/calibration_service/` |
| **定位预测** | `localization-prediction-assistant` | `localization/` + `prediction/` (~67K 行) |
| **地图路由** | `map-routing-assistant` | `map/` + `routing/` (~25K 行) |
| **规划控制** | `planning-control-assistant` | `planning/` + `control/` (~134K 行) |
| **底盘集成** | `canbus-integration-assistant` | `canbus/` (~95K 行) |
| **测试验证** | `test-verification-assistant` | `guardian/` + `monitor/` + 集成测试 |
| **代码审查** | `code-reviewer` | 全模块通用 |
| **技术方案** | `tech-spec-writer` | 系统级 |
| **部署运维** | `deployment-checker` | 系统级 |
| **汇报材料** | `report-writer` | 系统级 |

## 🚀 在 Claude Code 中使用

```bash
# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 进入项目目录
cd /path/to/apollo-lite

# 加载需要的 skill（按需加载）
/skill load /path/to/team-ai-repo/skills/cyber-rt-developer
/skill load /path/to/team-ai-repo/skills/planning-control-assistant
```

## 🎯 典型工作流

### 场景 1：感知模块调试
```
用户: "Apollo 感知启动失败，camera 无输出"
→ 加载 perception-assistant
→ 提供: DAG 配置 + 日志 + 相机型号
→ AI 输出: 根因定位 + 修复方案
```

### 场景 2：新车型底盘适配
```
用户: "新车型 Devkit2 的刹车控制无响应"
→ 加载 canbus-integration-assistant
→ 提供: DBC 文件 + VehicleController 代码 + CAN 抓包
→ AI 输出: 信号映射分析 + 协议修正建议
```

### 场景 3：定位漂移排查
```
用户: "MSF 定位在隧道场景漂移严重"
→ 加载 localization-prediction-assistant
→ 提供: localization 日志 + 地图版本 + IMU 数据
→ AI 输出: RTK/IMU/NDT 层分析 + 参数调优
```

### 场景 4：Cyber RT 性能调优
```
用户: "Planning 延迟不稳定，偶发 > 200ms"
→ 加载 cyber-rt-developer
→ 提供: cyber_monitor 截图 + DAG 配置 + 调度器配置
→ AI 输出: 调度策略优化 + Channel QoS 调整
```

## 📁 目录结构

```
team-ai-repo/
├── skills/           # 13 个 AI Skill
│   ├── cyber-rt-developer/
│   ├── sensor-drivers-assistant/
│   ├── perception-assistant/
│   ├── calibration-assistant/
│   ├── localization-prediction-assistant/
│   ├── map-routing-assistant/
│   ├── planning-control-assistant/
│   ├── canbus-integration-assistant/
│   ├── test-verification-assistant/
│   ├── code-reviewer/
│   ├── tech-spec-writer/
│   ├── deployment-checker/
│   └── report-writer/
├── prompts/          # 标准 Prompt 模板
├── scripts/          # 各 Skill 配套脚本
└── docs/             # 使用文档
```

## ⚠️ 重要提示

1. **所有 Skill 基于 apollo-lite 实际代码库**：目录树、类名、算法名称均与 `wheelos/apollo-lite` main 分支一致
2. **Skill 之间可组合使用**：复杂问题可加载多个 Skill 协同分析
3. **脚本工具需 Apollo 环境**：部分 Python 脚本依赖 `cyber_recorder`、`cyber_channel` 等 CLI 工具
4. **持续同步**：apollo-lite 代码更新后，定期同步 team-ai-repo 的 Skill 内容

## 🔗 相关资源

- Apollo-Lite 仓库: https://github.com/wheelos/apollo-lite
- Cyber RT 文档: `cyber/README.md`
- 模块设计文档: 见各模块 `README.md` / `README_cn.md`

---

> 维护者：Vincent
> 最后更新：2026-05-25（重构完成：13 Skill，基于 apollo-lite 实际代码库）
