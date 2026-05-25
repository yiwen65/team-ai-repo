# 自动驾驶团队 AI 应用提效建设

> 团队级 AI 工具链与知识资产库。13 个深度 skill，基于 Apollo-Lite 实际代码库（wheelos/apollo-lite），覆盖自动驾驶全栈技术域。

**代码库映射**: 本仓库所有 skill 均基于 `wheelos/apollo-lite` main 分支实际代码结构编写，所有目录树、模块名称、类名均与代码库一致。

## 📁 目录结构

```
team-ai-repo/
├── skills/                    # AI skill（按模块划分，共 13 个）
│   ├── cyber-rt-developer/        # Cyber RT 中间件开发（Component/DAG/Channel/调度/录制）
│   ├── sensor-drivers-assistant/  # 传感器驱动（LiDAR 8 家/Radar/Camera/GNSS/IMU）
│   ├── perception-assistant/      # 感知模块（YOLOv4/DarkSCNN/PointPillars/OMT/融合）
│   ├── calibration-assistant/     # 传感器标定（在线标定/车道线辅助/重投影分析）
│   ├── localization-prediction-assistant/  # 定位与预测（RTK/MSF/NDT + Evaluator/Predictor）
│   ├── map-routing-assistant/     # 地图与路由（HDMap/PNCMap/Routing/RelativeMap）
│   ├── planning-control-assistant/ # 规划控制（EM/Lattice/OpenSpace/MPC/差速驱动）
│   ├── canbus-integration-assistant/ # 底盘集成（13+ 车型/DBC/车辆控制/功能安全）
│   ├── test-verification-assistant/ # 测试验证（场景库/cyber_recorder/Guardian/Monitor）
│   ├── code-reviewer/             # 代码审查（Cyber RT/Bazel/Protobuf/实时性/ASIL）
│   ├── tech-spec-writer/          # 技术方案（架构/传感器/算力/数据闭环）
│   ├── deployment-checker/        # 部署运维（whl/Docker/Bazel/TensorRT/OTA）
│   └── report-writer/             # 汇报材料（模块状态/性能/安全/评审）
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

# 加载团队 skill（按 Apollo-Lite 模块分层）
/skill load ./skills/cyber-rt-developer
/skill load ./skills/sensor-drivers-assistant
/skill load ./skills/perception-assistant
/skill load ./skills/calibration-assistant
/skill load ./skills/localization-prediction-assistant
/skill load ./skills/map-routing-assistant
/skill load ./skills/planning-control-assistant
/skill load ./skills/canbus-integration-assistant
/skill load ./skills/test-verification-assistant
/skill load ./skills/code-reviewer
/skill load ./skills/tech-spec-writer
/skill load ./skills/deployment-checker
/skill load ./skills/report-writer
```

### 使用配套脚本

每个 skill 的 `scripts/` 目录包含可直接运行的工具脚本：

| Skill | 脚本 | 用途 |
|-------|------|------|
| cyber-rt | `cyber_channel_checker.py` | 检查 Cyber RT channel 发布/订阅状态 |
| cyber-rt | `dag_config_validator.py` | 验证 DAG 文件配置完整性 |
| sensor-drivers | `sensor_sync_checker.py` | 检查多传感器时间同步 |
| sensor-drivers | `lidar_data_analyzer.py` | LiDAR 点云数据质量分析 |
| perception | `fusion_coverage_analyzer.py` | 分析传感器 FOV 盲区 |
| perception | `detection_drift_detector.py` | 对比模型版本精度漂移 |
| calibration | `reprojection_analyzer.py` | 多距离重投影误差分析 |
| calibration | `extrinsic_drift_monitor.py` | 场景特征外参漂移检测 |
| calibration | `calib_validator.py` | 标定结果完整验证 |
| localization-prediction | `prediction_latency_analyzer.py` | 预测链路延迟分析 |
| map-routing | `routing_failure_analyzer.py` | 路由失败根因分析 |
| planning-control | `trajectory_analyzer.py` | 轨迹曲率/加速度/舒适性分析 |
| planning-control | `control_tracking_analyzer.py` | 规划轨迹 vs 实际控制误差 |
| planning-control | `collision_checker.py` | 轨迹-障碍物碰撞检测 |
| canbus | `chassis_signal_checker.py` | 底盘信号完整性检查 |
| test-verification | `disengagement_analyzer.py` | 脱离记录分类与趋势分析 |
| test-verification | `scenario_coverage_checker.py` | 场景库覆盖度检查 |
| test-verification | `regression_test_selector.py` | 基于代码变更选最小回归集 |
| deployment | `docker_size_analyzer.py` | Docker 镜像层大小分析 |
| deployment | `ota_verifier.py` | OTA 包完整性/签名验证 |
| deployment | `log_analyzer.py` | Cyber RT/系统日志根因分析 |

## 📋 Skill 总览

| Skill | 核心域 | 代码覆盖 | 技术深度 | 状态 |
|-------|--------|---------|---------|------|
| **cyber-rt-developer** | Cyber RT 中间件、Component、DAG、Channel、调度、录制 | `cyber/` (~57K 行) | Component 开发/调度优化/性能调优 | ✅ |
| **sensor-drivers-assistant** | LiDAR/Radar/Camera/GNSS/IMU 驱动 | `drivers/` (~46K 行) | 8 家 LiDAR/6 家 Radar/驱动适配 | ✅ |
| **perception-assistant** | Camera/LiDAR/Radar/Fusion/Onboard/Pipeline | `perception/` (~158K 行) | YOLOv4/DarkSCNN/PointPillars/OMT2 | ✅ |
| **calibration-assistant** | 相机/激光雷达/在线标定/漂移检测 | `perception/camera/calibration_service/` | 在线标定/重投影/温度漂移 | ✅ |
| **localization-prediction-assistant** | RTK/MSF/NDT + Evaluator/Predictor/Network | `localization/` (~37K) + `prediction/` (~30K) | 多传感器融合/意图评估/轨迹预测 | ✅ |
| **map-routing-assistant** | HDMap/PNCMap/Routing/RelativeMap | `map/` (~19K) + `routing/` (~6K) | 地图解析/A* 寻路/拓扑生成 | ✅ |
| **planning-control-assistant** | EM/Lattice/OpenSpace/Learning-Based + MPC/LQR | `planning/` (~122K) + `control/` (~12K) | 场景管理/优化器/差速驱动控制 | ✅ |
| **canbus-integration-assistant** | 13+ 车型底盘适配/DBC/车辆控制 | `canbus/` (~95K 行) | 协议解析/控制响应/功能安全 | ✅ |
| **test-verification-assistant** | 场景库/cyber_recorder/Guardian/Monitor | `guardian/` + `monitor/` + 集成测试 | 数据回放/安全监控/回归测试 | ✅ |
| **code-reviewer** | C++ Cyber RT/Bazel/Protobuf/功能安全 | 全模块通用 | 实时性/内存安全/接口兼容/ASIL | ✅ |
| **tech-spec-writer** | 架构/传感器/算力/安全/数据闭环 | 系统级 | 选型决策/Bazel CI/CD/OTA 流程 | ✅ |
| **deployment-checker** | whl/Docker/Bazel/TensorRT/OTA/CI-CD | 系统级 | 容器化/模型部署/远程缓存 | ✅ |
| **report-writer** | 模块状态/算法性能/安全监控/评审 | 系统级 | 量化指标/分层汇报/Q&A 预判 | ✅ |

## 🎯 AI 应用领域

- ✅ AI 辅助 Cyber RT 中间件开发与调试
- ✅ AI 辅助传感器驱动适配与故障排查（LiDAR/Radar/Camera/GNSS）
- ✅ AI 辅助感知算法选型与调优（YOLOv4/DarkSCNN/PointPillars/OMT2）
- ✅ AI 辅助传感器标定问题诊断（在线标定/重投影/漂移）
- ✅ AI 辅助定位与预测问题排查（RTK/MSF/NDT + Evaluator/Predictor）
- ✅ AI 辅助地图与路由问题分析（HDMap/PNCMap/Routing/RelativeMap）
- ✅ AI 辅助规划控制参数优化（EM/Lattice/OpenSpace/MPC/差速驱动）
- ✅ AI 辅助底盘集成与车型适配（DBC/车辆控制/功能安全）
- ✅ AI 辅助测试场景设计与数据分析（cyber_recorder/Guardian/Monitor）
- ✅ AI 辅助代码审查（Cyber RT/Bazel/Protobuf/实时性/ASIL）
- ✅ AI 辅助技术方案编写与评审
- ✅ AI 辅助部署问题排查与运维（whl/Docker/Bazel/TensorRT/OTA）
- ✅ AI 辅助汇报材料编写

---

> 维护者：Vincent
> 最后更新：2026-05-25（重构完成：13 skill，基于 apollo-lite 实际代码库）
> GitHub：https://github.com/yiwen65/team-ai-repo
