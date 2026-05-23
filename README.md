# 自动驾驶团队 AI 应用提效建设

> 团队级 AI 工具链与知识资产库。8 个深度 skill，覆盖自动驾驶全栈技术域。

## 📁 目录结构

```
team-ai-repo/
├── skills/                    # AI skill（按模块划分）
│   ├── perception-assistant/      # 感知模块（传感器融合/BEV/部署/数据质量）
│   ├── calibration-assistant/     # 传感器标定（联合标定/在线标定/漂移检测）
│   ├── planning-control-assistant/ # 规划控制（EM Planner/MPC/安全验证）
│   ├── test-verification-assistant/ # 测试验证（场景库/ISO/SIL-HIL/回归）
│   ├── code-reviewer/             # 代码审查（实时性/ROS2/CUDA/功能安全）
│   ├── tech-spec-writer/          # 技术方案（传感器/算法/算力/安全/数据闭环）
│   ├── deployment-checker/        # 部署运维（ROS2/Docker/TensorRT/OTA/CI-CD）
│   └── report-writer/             # 汇报材料（进度/方案/复盘/评审/跨团队）
├── prompts/                 # Prompt 模板（待补充）
├── tools/                   # 脚本与自动化工具（待补充）
├── docs/                    # 团队文档与使用指南
└── resources/               # 资源清单（API keys、账号、配置）
```

## 🚀 快速开始

### 在 Claude Code 中使用

```bash
# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 加载团队 skill
/skill load ./skills/perception-assistant
/skill load ./skills/calibration-assistant
# ... 其他 skill
```

### 使用配套脚本

每个 skill 的 `scripts/` 目录包含可直接运行的工具脚本：

| Skill | 脚本 | 用途 |
|-------|------|------|
| perception | `sensor_sync_checker.py` | 检查多传感器时间同步 |
| perception | `fusion_coverage_analyzer.py` | 分析传感器 FOV 盲区 |
| perception | `detection_drift_detector.py` | 对比模型版本精度漂移 |
| calibration | `reprojection_analyzer.py` | 多距离重投影误差分析 |
| calibration | `extrinsic_drift_monitor.py` | 场景特征外参漂移检测 |
| calibration | `calib_validator.py` | 标定结果完整验证 |
| planning-control | `trajectory_analyzer.py` | 轨迹曲率/加速度/舒适性分析 |
| planning-control | `control_tracking_analyzer.py` | 规划轨迹 vs 实际控制误差 |
| planning-control | `collision_checker.py` | 轨迹-障碍物碰撞检测 |
| test-verification | `disengagement_analyzer.py` | 脱离记录分类与趋势分析 |
| test-verification | `scenario_coverage_checker.py` | 场景库覆盖度检查 |
| test-verification | `regression_test_selector.py` | 基于代码变更选最小回归集 |
| deployment | `ros2_health_check.sh` | ROS2 环境全面健康检查 |
| deployment | `docker_size_analyzer.py` | Docker 镜像层大小分析 |
| deployment | `ota_verifier.py` | OTA 包完整性/签名验证 |
| deployment | `log_analyzer.py` | ROS2/系统日志根因分析 |

## 📋 Skill 总览

| Skill | 核心域 | 技术深度 | 状态 |
|-------|--------|---------|------|
| **perception-assistant** | 多传感器融合、BEV、时序对齐、TensorRT 部署 | 算法选型/参数调优/故障排查 | ✅ |
| **calibration-assistant** | 相机/激光雷达/毫米波/IMU 联合标定 | 在线标定/漂移检测/温度补偿 | ✅ |
| **planning-control-assistant** | EM Planner、Lattice、MPC、Stanley | 轨迹质量/控制跟踪/安全验证 | ✅ |
| **test-verification-assistant** | 场景库、SIL/HIL、NCAP、回归测试 | ISO 26262/SOTIF/数据分析 | ✅ |
| **code-reviewer** | C++ ROS2、Python、CUDA、功能安全 | 实时性/内存安全/多线程/ASIL | ✅ |
| **tech-spec-writer** | 传感器/算法/算力/通信/安全/数据闭环 | 选型决策/架构设计/风险评估 | ✅ |
| **deployment-checker** | ROS2、Docker、TensorRT、OTA、CI/CD | 环境检查/模型部署/现场诊断 | ✅ |
| **report-writer** | 进度/方案/复盘/成果/评审/跨团队 | 层级适配/数据驱动/Q&A 预判 | ✅ |

## 🎯 AI 应用领域

- ✅ AI 辅助感知算法选型与调优
- ✅ AI 辅助传感器标定问题诊断
- ✅ AI 辅助规划控制参数优化
- ✅ AI 辅助测试场景设计与数据分析
- ✅ AI 辅助代码审查（安全/实时/性能）
- ✅ AI 辅助技术方案编写与评审
- ✅ AI 辅助部署问题排查与运维
- ✅ AI 辅助汇报材料编写

---

> 维护者：Vincent
> 最后更新：2026-05-23
> GitHub：https://github.com/yiwen65/team-ai-repo
